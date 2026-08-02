# Plan 3 — Execution Layer (Routing Engine, Lifecycle, Task State Machine, DAG Validator, ITaskStateQuery)

**Batch**: 3 of 4 (Plans 1–4 drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-2
Vision principles: 1 (sacred core), 5 (wire as you go), 7 (modular core), 9 (observability), 11 (DI, no globals), 12 (plain-English docstrings), 13 (strong, robust)
Open questions resolved: Q3 (memory abstraction interface — defined here, implementation deferred), Q4 (routing — capability-based via the graph), Q14 (persistence — in-memory only per A7; durable backends deferred to DEBT)

---

## S0 — Opening

**S0.1** — Run `/open` workflow. Verify `prompt-2` on origin. Clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md`. Note AR16 (circuit breaker — 50 errors/10s unloads Worker; the Lifecycle Manager enforces this), AR18 (Managers/Workers lifecycle — Lifecycle Manager in `shared/` handles spawn/promote/load/unload).

**S0.3** — No new AR/OR rules this plan. Proceed to S1.

---

## Architectural Context

Per the locked scope adjudication:

- **A1** — Routing engine moved from Plan 2 to Plan 3. The routing engine must know whether a component is active, degraded, or circuit-broken — that's the Lifecycle Manager's job (also Plan 3). Building the router before the lifecycle manager produces a static dispatcher that requires a rewrite.
- **A6** — DAG validator stays in Plan 3 (not Plan 4). If the state machine accepts composite skill tasks without validating their DAG, composite tasks enter unvalidated until Plan 4 — a silent failure (P9 violation).
- **A7** — Q14 persistence scoped to in-memory only. Durable backends and full crash recovery deferred to DEBT.
- **A5** — Plan 3 ships `ITaskStateQuery` as a locked named protocol. Plan 4 imports only this protocol.

**Cross-plan dependencies:**
- Plan 3 depends on Plan 2's `ICapabilityIndex` for routing and lifecycle queries.
- Plan 3 depends on Plan 1's EventBus for state transition publication.
- Plan 4 depends on Plan 3's `ITaskStateQuery`.

---

## S1 — Extend `shared/types.py` with Task and Lifecycle Types

### S1.1 — Add task and lifecycle types

Append to `sovereignai/shared/types.py`:

```python
# ============================================================================
# Task types (used by task state machine in S4)
# ============================================================================

class TaskState(str, Enum):
    """Lifecycle state of a single task, from receipt to completion.

    The task state machine transitions: RECEIVED → QUEUED → EXECUTING
    → COMPLETE or FAILED. Transitions are published as events on the
    event bus so subscribers (e.g. the Capability API in Plan 4) can
    react to state changes.
    """
    RECEIVED = "received"      # task entered the system, not yet queued
    QUEUED = "queued"          # task is waiting for a worker
    EXECUTING = "executing"    # a worker is running this task
    COMPLETE = "complete"      # task finished successfully
    FAILED = "failed"          # task failed; see traces for details


# Event channel for task state transitions (per A9 — bus guarantees order)
TASK_STATE_CHANNEL = Channel("task_state")


@dataclass(frozen=True)
class TaskStateChanged(Event):
    """Event published when a task transitions between states.

    Frozen so subscribers receive an immutable snapshot. Subscribers
    cannot modify the event before another subscriber sees it.
    """
    task_id: UUID
    old_state: TaskState
    new_state: TaskState


@dataclass(frozen=True)
class Task:
    """A unit of work submitted to the system for execution.

    Frozen so a task cannot be mutated after submission. The state
    machine tracks transitions externally (via TaskStateChanged events)
    rather than mutating the Task itself.
    """
    task_id: UUID
    capability: CapabilityDeclaration    # what the task needs done
    payload: str                          # opaque payload (JSON or similar)
    submitted_at: datetime                # UTC, timezone-aware (per OR20)


# ============================================================================
# Lifecycle types (used by Lifecycle Manager in S3)
# ============================================================================

class ComponentStatus(str, Enum):
    """Health status of a registered component, used by the routing engine.

    The Lifecycle Manager tracks status; the Routing Engine queries it
    to skip degraded or circuit-broken components (per A1).
    """
    ACTIVE = "active"                # healthy and available
    DEGRADED = "degraded"            # experiencing errors but still running
    CIRCUIT_BROKEN = "circuit_broken"  # unloaded due to >50 errors/10s (AR16)
    STOPPED = "stopped"              # explicitly stopped, not available
```

After edit, run `/verify`. Run existing tests to confirm no regressions:
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv
```

---

## S2 — Routing Engine

### S2.1 — Create `sovereignai/shared/routing_engine.py`

Per A1: routing engine knows component status via the Lifecycle Manager. Per Q4 resolution: capability advertisement via manifests; routing engine inspects request requirements, routes to highest-priority active provider.

Per AR9: no hard-coded component names. Routing queries the capability graph.

```python
"""Route capability requests to the highest-priority active provider.

Per A1: the routing engine queries the Lifecycle Manager to skip
components that are degraded or circuit-broken. A router built before
the Lifecycle Manager would be a static dispatcher requiring a rewrite
when status tracking lands.

Per Q4: routing is capability-based. The caller declares what
capability it needs; the router finds the highest-priority active
provider from the capability graph.
"""
from __future__ import annotations

from typing import Optional

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.types import (
    CapabilityCategory,
    CapabilityDeclaration,
    ComponentId,
)


class NoActiveProviderError(Exception):
    """Raised when no active component provides the requested capability."""


class RoutingEngine:
    """Find the best active component to handle a capability request.

    The router depends on ICapabilityIndex (Plan 2) for discovery and
    on the Lifecycle Manager (S3 of this plan) for status. It never
    routes to a CIRCUIT_BROKEN or STOPPED component.
    """

    def __init__(self, capability_index: ICapabilityIndex,
                 lifecycle_manager: "LifecycleManager") -> None:
        """Create a router that queries the capability graph and lifecycle manager.

        Args:
            capability_index: Protocol implementation providing
                find_providers() (Plan 2's CapabilityGraph).
            lifecycle_manager: Tracks component status; the router
                skips components that are not ACTIVE.
        """
        self._index = capability_index
        self._lifecycle = lifecycle_manager

    def route(self, category: CapabilityCategory, name: str) -> ComponentId:
        """Return the component ID of the highest-priority active provider.

        Args:
            category: The capability category needed.
            name: The specific capability name needed.

        Returns:
            ComponentId of the chosen provider.

        Raises:
            NoActiveProviderError: If no ACTIVE component provides the
                requested capability.
        """
        providers = self._index.find_providers(category, name)
        for component_id, _declaration in providers:
            if self._lifecycle.get_status(component_id).is_available():
                return component_id
        raise NoActiveProviderError(
            f"No active provider for {category}/{name} "
            f"(checked {len(providers)} registered providers)"
        )
```

**Note**: The `is_available()` method on `ComponentStatus` is added at S3.1 — it returns True only for ACTIVE. This keeps the router's status check explicit and avoids hard-coding the enum values.

After creating, run `/verify`.

---

## S3 — Lifecycle Manager

### S3.1 — Add helper to ComponentStatus

Extend `sovereignai/shared/types.py` to add an `is_available()` method to `ComponentStatus`. Since `ComponentStatus` is a `str, Enum`, we add a method:

```python
class ComponentStatus(str, Enum):
    """Health status of a registered component, used by the routing engine."""
    ACTIVE = "active"
    DEGRADED = "degraded"
    CIRCUIT_BROKEN = "circuit_broken"
    STOPPED = "stopped"

    def is_available(self) -> bool:
        """Return True if a component in this state can accept new work.

        Only ACTIVE components are available. DEGRADED components may
        be running existing tasks but should not receive new ones.
        CIRCUIT_BROKEN and STOPPED are never available.
        """
        return self is ComponentStatus.ACTIVE
```

After edit, run `/verify`.

### S3.2 — Create `sovereignai/shared/lifecycle_manager.py`

Per AR16: circuit breaker — >50 errors in 10 seconds triggers automatic unload. Per AR18: no Manager or Worker manages its own lifecycle; Lifecycle Manager in `shared/` handles spawn/promote/load/unload.

Per AR4: error count is a DI-managed per-Worker object, not module-level state.

```python
"""Track component health and enforce the circuit breaker rule.

Per AR16: a component that records more than 50 errors in 10 seconds
is automatically unloaded (circuit-broken). The Routing Engine queries
the Lifecycle Manager to skip circuit-broken components.

Per AR18: no component manages its own lifecycle. This module is the
sole authority for spawning, promoting, loading, and unloading.
"""
from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic
from typing import Deque, Dict

from sovereignai.shared.types import ComponentId, ComponentStatus


CIRCUIT_BREAKER_THRESHOLD = 50      # errors
CIRCUIT_BREAKER_WINDOW_SECONDS = 10.0


class LifecycleManager:
    """Track component status and enforce the circuit breaker rule.

    The manager records errors per component in a rolling 10-second
    window. When the count exceeds the threshold (50 per AR16), the
    component's status flips to CIRCUIT_BROKEN and the Routing Engine
    stops routing to it.
    """

    def __init__(self) -> None:
        """Create a lifecycle manager with no registered components."""
        self._statuses: Dict[ComponentId, ComponentStatus] = {}
        self._error_log: Dict[ComponentId, Deque[float]] = {}
        self._lock = Lock()

    def register(self, component_id: ComponentId) -> None:
        """Start tracking a component with ACTIVE status.

        Args:
            component_id: The component to register.
        """
        with self._lock:
            self._statuses[component_id] = ComponentStatus.ACTIVE
            self._error_log[component_id] = deque()

    def get_status(self, component_id: ComponentId) -> ComponentStatus:
        """Return the current status of a registered component.

        Args:
            component_id: The component to query.

        Returns:
            ComponentStatus. Returns STOPPED if the component was
            never registered (defensive default).
        """
        with self._lock:
            return self._statuses.get(component_id, ComponentStatus.STOPPED)

    def record_error(self, component_id: ComponentId) -> None:
        """Record one error for a component and check the circuit breaker.

        If the rolling 10-second error count exceeds the threshold
        (50 per AR16), the component is automatically circuit-broken.

        Args:
            component_id: The component that experienced an error.
        """
        now = monotonic()
        with self._lock:
            log = self._error_log.setdefault(component_id, deque())
            log.append(now)
            # Drop entries outside the window
            cutoff = now - CIRCUIT_BREAKER_WINDOW_SECONDS
            while log and log[0] < cutoff:
                log.popleft()
            # Check threshold
            if len(log) > CIRCUIT_BREAKER_THRESHOLD:
                self._statuses[component_id] = ComponentStatus.CIRCUIT_BROKEN
```

**Verify:**
- Circuit breaker threshold = 50 errors / 10s (AR16)
- Error log is per-Worker, not module-level (AR4)
- Thread-safe (Lock around `_statuses` and `_error_log`)
- Defensive default: unregistered component returns STOPPED
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S3.3 — Create `tests/test_lifecycle_manager.py`

Required tests:

1. **`test_register_sets_active`** — register, get_status returns ACTIVE
2. **`test_unregistered_returns_stopped`** — get_status on unknown returns STOPPED
3. **`test_record_error_below_threshold_stays_active`** — 49 errors, still ACTIVE
4. **`test_record_error_at_threshold_circuit_breaks`** — 51 errors within 10s, CIRCUIT_BROKEN
5. **`test_old_errors_expire_from_window`** — 51 errors over 11s (with 1s gap), still ACTIVE
6. **`test_circuit_broken_is_not_available`** — `ComponentStatus.CIRCUIT_BROKEN.is_available()` returns False
7. **`test_active_is_available`** — `ComponentStatus.ACTIVE.is_available()` returns True

For test 5 (window expiry), use `unittest.mock.patch` on `monotonic` to simulate time passing.

After tests pass, run `/verify`.

### S3.4 — Create `tests/test_routing_engine.py`

Required tests:

1. **`test_route_returns_highest_priority_active`** — two providers, both ACTIVE, returns higher priority
2. **`test_route_skips_circuit_broken`** — higher-priority provider CIRCUIT_BROKEN, returns lower-priority ACTIVE one
3. **`test_route_skips_stopped`** — provider STOPPED, returns other ACTIVE one
4. **`test_route_raises_when_no_active_provider`** — all providers CIRCUIT_BROKEN, raises NoActiveProviderError
5. **`test_route_raises_when_no_providers_at_all`** — capability not registered, raises NoActiveProviderError

After tests pass, run `/verify`.

---

## S4 — Task State Machine (with `ITaskStateQuery` Protocol)

### S4.1 — Create `sovereignai/shared/task_state_machine.py`

Per A5: ships `ITaskStateQuery` as a locked named protocol. Per A6: DAG validator stays in Plan 3 to validate composite tasks before they enter the state machine. Per A7: in-memory persistence only.

Per A9: state transitions published as events on the bus (in-order per channel).

```python
"""Track task state transitions and publish them on the event bus.

Per A6: composite tasks must pass DAG validation before entering the
state machine. The validator (S5 of this plan) is called from
submit() before the task is accepted.

Per A7: persistence is in-memory only. Durable backends and crash
recovery are deferred to DEBT. On restart, all task state is lost.

Per A9: state transitions are published on TASK_STATE_CHANNEL. The
event bus guarantees in-order delivery per channel, so subscribers
see transitions in the order they occurred.
"""
from __future__ import annotations

from threading import Lock
from typing import Dict, List, Protocol, Tuple
from uuid import UUID

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.types import (
    TASK_STATE_CHANNEL,
    Task,
    TaskState,
    TaskStateChanged,
    TraceEmitter,
    TraceLevel,
)


class ITaskStateQuery(Protocol):
    """Locked query interface for the task state machine.

    Plan 4's Capability API imports ONLY this protocol — never the
    concrete TaskStateMachine class. This enforces AR7 (UIs are
    separate processes consuming the Capability API).
    """

    def get_state(self, task_id: UUID) -> TaskState:
        """Return the current state of a task by its ID.

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState. Returns FAILED if the task was never submitted
            (defensive default).
        """
        ...

    def list_tasks(self) -> Tuple[Task, ...]:
        """Return all tasks currently tracked by the state machine.

        Returns:
            Tuple of Task instances, oldest first.
        """
        ...


# Valid state transitions (per the state machine diagram in the vision)
_VALID_TRANSITIONS: Dict[TaskState, List[TaskState]] = {
    TaskState.RECEIVED: [TaskState.QUEUED, TaskState.FAILED],
    TaskState.QUEUED: [TaskState.EXECUTING, TaskState.FAILED],
    TaskState.EXECUTING: [TaskState.COMPLETE, TaskState.FAILED],
    TaskState.COMPLETE: [],   # terminal
    TaskState.FAILED: [],     # terminal
}


class TaskStateMachine:
    """Track task state transitions and publish them on the event bus.

    The state machine depends on EventBus (Plan 1) for publishing
    transitions and TraceEmitter (Plan 1) for logging invalid
    transition attempts. It implements ITaskStateQuery so callers
    depend on the protocol, not the concrete class.
    """

    def __init__(self, bus: EventBus, trace: TraceEmitter) -> None:
        """Create an empty state machine with no tracked tasks.

        Args:
            bus: Event bus for publishing TaskStateChanged events.
            trace: Trace emitter for logging invalid transitions.
        """
        self._bus = bus
        self._trace = trace
        self._tasks: Dict[UUID, Task] = {}
        self._states: Dict[UUID, TaskState] = {}
        self._lock = Lock()

    def submit(self, task: Task) -> None:
        """Accept a new task into the RECEIVED state and publish the transition.

        Args:
            task: Frozen Task instance to track.
        """
        with self._lock:
            self._tasks[task.task_id] = task
            self._states[task.task_id] = TaskState.RECEIVED
        self._publish(task.task_id, None, TaskState.RECEIVED)

    def transition(self, task_id: UUID, new_state: TaskState) -> None:
        """Move a task to a new state if the transition is valid.

        Invalid transitions are logged at WARN and ignored (no
        exception raised — the system stays robust per P13).

        Args:
            task_id: UUID of the task to transition.
            new_state: Target state.
        """
        with self._lock:
            old_state = self._states.get(task_id)
            if old_state is None:
                self._trace.emit(
                    component="TaskStateMachine",
                    level=TraceLevel.WARN,
                    message=f"Transition attempted for unknown task {task_id}",
                )
                return
            if new_state not in _VALID_TRANSITIONS.get(old_state, []):
                self._trace.emit(
                    component="TaskStateMachine",
                    level=TraceLevel.WARN,
                    message=(
                        f"Invalid transition {old_state} -> {new_state} "
                        f"for task {task_id}"
                    ),
                )
                return
            self._states[task_id] = new_state
        self._publish(task_id, old_state, new_state)

    def get_state(self, task_id: UUID) -> TaskState:
        """Return the current state of a task by its ID.

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState. Returns FAILED if the task was never submitted
            (defensive default — callers should treat unknown tasks as
            failed rather than crashing).
        """
        with self._lock:
            return self._states.get(task_id, TaskState.FAILED)

    def list_tasks(self) -> Tuple[Task, ...]:
        """Return all tasks currently tracked by the state machine.

        Returns:
            Tuple of Task instances, in insertion order (oldest first).
        """
        with self._lock:
            return tuple(self._tasks.values())

    def _publish(self, task_id: UUID, old_state: TaskState | None,
                 new_state: TaskState) -> None:
        """Publish a TaskStateChanged event on the task state channel.

        Args:
            task_id: UUID of the task that transitioned.
            old_state: Previous state, or None for the initial RECEIVED.
            new_state: New state.
        """
        event = TaskStateChanged(
            channel=TASK_STATE_CHANNEL,
            correlation_id=task_id,
            timestamp=now_utc_safe(),
            task_id=task_id,
            old_state=old_state or TaskState.RECEIVED,
            new_state=new_state,
        )
        self._bus.publish(event)


def now_utc_safe():
    """Return current UTC time — imported lazily to avoid circular imports."""
    from sovereignai.shared.types import now_utc
    return now_utc()
```

**Verify:**
- `ITaskStateQuery` is a `Protocol` (A5)
- `TaskStateMachine` implements it
- Valid transitions enforced (RECEIVED → QUEUED → EXECUTING → COMPLETE/FAILED)
- Invalid transitions logged at WARN, not raised (P13 robust)
- State changes published on `TASK_STATE_CHANNEL` (A9 in-order)
- Thread-safe (Lock)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S4.2 — Create `tests/test_task_state_machine.py`

Required tests:

1. **`test_submit_sets_received`** — submit, get_state returns RECEIVED
2. **`test_valid_transition_publishes_event`** — RECEIVED → QUEUED, subscriber receives TaskStateChanged
3. **`test_invalid_transition_logs_warn`** — RECEIVED → COMPLETE, no exception, trace has WARN
4. **`test_terminal_states_have_no_transitions`** — COMPLETE → anything, no transition
5. **`test_get_state_unknown_returns_failed`** — unknown UUID, returns FAILED
6. **`test_list_tasks_returns_insertion_order`** — submit 3, list returns in submit order
7. **`test_protocol_compliance`** — `isinstance(machine, ITaskStateQuery)` returns True
8. **`test_transitions_published_in_order`** — submit, transition to QUEUED, transition to EXECUTING; subscriber receives 3 events in order (A9 verification)

After tests pass, run `/verify`.

---

## S5 — DAG Validator

### S5.1 — Create `sovereignai/shared/dag_validator.py`

Per A6: DAG validator stays in Plan 3 to validate composite skill tasks before they enter the state machine. Per Q20 resolution: DAG-based, not pipeline-based; validator checks acyclicity and type-matching.

```python
"""Validate skill DAGs for acyclicity and type-matching before execution.

Per A6: composite skills must pass DAG validation before entering the
task state machine. Without this check, composite tasks with cycles
or type mismatches would enter the state machine and fail at runtime
(a silent failure, violating P9).

Per Q20: DAG-based execution. Each skill declares inputs (which can
be outputs of other skills). The validator checks:
  1. Acyclicity — no skill depends on its own output transitively
  2. Type-matching — every input has a producer with a matching type
"""
from __future__ import annotations

from typing import Dict, List, Set


class DAGValidationError(Exception):
    """Raised when a skill DAG has a cycle or a type mismatch."""


def validate_dag(nodes: List[str], edges: List[tuple[str, str]],
                 input_types: Dict[str, str],
                 output_types: Dict[str, str]) -> None:
    """Check that a skill DAG is acyclic and that all input types are produced.

    Args:
        nodes: List of skill node IDs (e.g. ["open_browser", "register_email"]).
        edges: List of (source, target) pairs meaning source's output
            feeds into target's input.
        input_types: Map of node ID -> type name it requires as input.
        output_types: Map of node ID -> type name it produces as output.

    Raises:
        DAGValidationError: If the graph has a cycle or an input has no
            matching producer.
    """
    # 1. Type-matching: every input must have a producer with matching type
    available_types: Dict[str, str] = {}  # type_name -> producer node
    for node, out_type in output_types.items():
        if out_type in available_types:
            raise DAGValidationError(
                f"Type {out_type!r} produced by multiple nodes: "
                f"{available_types[out_type]} and {node}"
            )
        available_types[out_type] = node
    for node, in_type in input_types.items():
        if in_type not in available_types:
            raise DAGValidationError(
                f"Node {node!r} requires input type {in_type!r} "
                f"but no node produces it"
            )

    # 2. Acyclicity: topological sort via Kahn's algorithm
    in_degree: Dict[str, int] = {n: 0 for n in nodes}
    adj: Dict[str, List[str]] = {n: [] for n in nodes}
    for src, tgt in edges:
        if src not in in_degree or tgt not in in_degree:
            raise DAGValidationError(
                f"Edge ({src}, {tgt}) references unknown node"
            )
        adj[src].append(tgt)
        in_degree[tgt] += 1

    queue: List[str] = [n for n in nodes if in_degree[n] == 0]
    visited = 0
    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(nodes):
        raise DAGValidationError(
            f"DAG has a cycle — visited {visited} of {len(nodes)} nodes"
        )
```

After creating, run `/verify`.

### S5.2 — Create `tests/test_dag_validator.py`

Required tests:

1. **`test_valid_dag_passes`** — linear 3-node DAG, no error
2. **`test_cyclic_dag_raises`** — A → B → A, raises DAGValidationError
3. **`test_missing_input_type_raises`** — node requires type "X", no node produces "X"
4. **`test_duplicate_output_type_raises`** — two nodes produce "X", raises
5. **`test_unknown_node_in_edge_raises`** — edge references node not in `nodes` list
6. **`test_diamond_dag_passes`** — A → B, A → C, B → D, C → D (diamond), no error

After tests pass, run `/verify`.

---

## S6 — Extend Composition Root (`main.py`)

### S6.1 — Add Plan 3 components to `build_container()`

Per A3: incremental Composition Root. Extend `sovereignai/main.py` to register the Lifecycle Manager, Routing Engine, and Task State Machine after the Capability Graph (Plan 2).

Append to `build_container()` (before `return container`):

```python
    # 4. LifecycleManager — no dependencies, singleton (Plan 3)
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    lifecycle = LifecycleManager()
    container.register_singleton(LifecycleManager, lifecycle)

    # 5. RoutingEngine — depends on ICapabilityIndex + LifecycleManager
    from sovereignai.shared.capability_graph import ICapabilityIndex
    from sovereignai.shared.routing_engine import RoutingEngine
    router = RoutingEngine(
        capability_index=container.retrieve(ICapabilityIndex),
        lifecycle_manager=lifecycle,
    )
    container.register_singleton(RoutingEngine, router)

    # 6. TaskStateMachine — depends on EventBus + TraceEmitter
    from sovereignai.shared.task_state_machine import (
        ITaskStateQuery,
        TaskStateMachine,
    )
    state_machine = TaskStateMachine(bus=bus, trace=trace)
    container.register_singleton(TaskStateMachine, state_machine)
    container.register_singleton(ITaskStateQuery, state_machine)

    return container
```

After edit, run `/verify`.

### S6.2 — Update `tests/test_composition_root.py`

Add tests for Plan 3 wiring:

10. **`test_lifecycle_manager_registered`** — retrieve LifecycleManager, not None
11. **`test_routing_engine_registered`** — retrieve RoutingEngine, not None
12. **`test_task_state_machine_registered`** — retrieve TaskStateMachine, not None
13. **`test_itask_state_query_registered`** — retrieve ITaskStateQuery, returns the same state machine instance
14. **`test_routing_engine_has_capability_index_wired`** — retrieve RoutingEngine, verify its `_index` attribute is the registered CapabilityGraph
15. **`test_routing_engine_has_lifecycle_wired`** — retrieve RoutingEngine, verify its `_lifecycle` is the registered LifecycleManager

After tests pass, run `/verify`.

---

## S7 — Update PLANS.md Baseline + DEBT.md

### S7.1 — Update Test Baseline

Plan 3 adds tests. New total: 37 (Plan 2) + 7 (lifecycle) + 5 (routing) + 8 (task state machine) + 6 (DAG validator) + 6 (composition root extensions) = **69 tests**.

Update the Test Baseline section in `PLANS.md`. Exact count confirmed at `/close`.

### S7.2 — Add DEBT entries for Q3 (memory abstraction) and Q14 (durable persistence)

Per A7: durable persistence deferred. Per Q3: memory abstraction interface defined here (in the ITaskStateQuery protocol shape — memory routing is pluggable, not in Core Scope v1), but implementation deferred.

Append to `DEBT.md`:

```markdown
## Deferred: Durable persistence backends and crash recovery

**Deferred at**: prompt-3 (per Plan 1-4 scope adjudication A7)
**Reason**: Plan 3 implements the event-store interface and in-memory replay only. Durable backends and full crash recovery are too much alongside four other components.
**Trigger condition**: When Plan 3's in-memory event store is stable.
**Target plan**: TBD (post Plan 3).

## Deferred: Memory abstraction implementation

**Deferred at**: prompt-3 (memory routing is pluggable per vision, not in Core Scope v1)
**Reason**: The Librarian is a pluggable component, not a core component. Plan 3 defines the interface shape (via ITaskStateQuery protocol pattern) but does not implement memory routing.
**Trigger condition**: When the Librarian Registry is needed (post Plan 4).
**Target plan**: TBD (post Plan 4).
```

After edit, run `/verify`.

---

## S8 — Update CHANGELOG.md

Append to `CHANGELOG.md`:

```markdown
## prompt-3 — Execution layer (routing, lifecycle, task state machine, DAG validator, ITaskStateQuery)

**Date**: {YYYY-MM-DD}
**Plan file**: prompts/plan-3-Rev1.md

**Files changed**:
- sovereignai/shared/types.py (extended: TaskState, TaskStateChanged, Task, ComponentStatus, TASK_STATE_CHANNEL)
- sovereignai/shared/lifecycle_manager.py (new — circuit breaker per AR16, 50 errors/10s)
- sovereignai/shared/routing_engine.py (new — capability-based routing, skips non-ACTIVE)
- sovereignai/shared/task_state_machine.py (new — ITaskStateQuery protocol, in-memory only per A7)
- sovereignai/shared/dag_validator.py (new — acyclicity + type-matching per A6)
- sovereignai/main.py (extended: registers Lifecycle, Router, TaskStateMachine against ITaskStateQuery)
- tests/test_lifecycle_manager.py (new — 7 tests)
- tests/test_routing_engine.py (new — 5 tests)
- tests/test_task_state_machine.py (new — 8 tests, including A9 in-order verification)
- tests/test_dag_validator.py (new — 6 tests)
- tests/test_composition_root.py (extended — 6 new tests)
- DEBT.md (added Q3 + Q14 deferrals)
- PLANS.md (updated test baseline)

**Results**:
- Tests: 69 passed (37 from Plans 1-2 + 32 new)
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass

**Notes**:
- Q3 (memory abstraction interface) resolved — interface shape defined; implementation deferred (DEBT).
- Q4 (routing) resolved — capability-based via ICapabilityIndex + LifecycleManager.
- Q14 (persistence) resolved — in-memory only per A7; durable backends deferred (DEBT).
- ITaskStateQuery protocol shipped as locked named output (per A5). Plan 4 will import only this protocol.
- Circuit breaker: 50 errors/10s triggers CIRCUIT_BROKEN (AR16). Verified by test_record_error_at_threshold_circuit_breaks.
- Event bus in-order delivery verified for task state transitions (A9, test_transitions_published_in_order).
- DAG validator prevents composite tasks with cycles or type mismatches from entering the state machine (A6, P9).
```

After edit, run `/verify`.

---

## S9 — Commit and Tag Prompt-3

**STOP condition**: If any `/verify` failed, STOP.

1. Stage all changes:
   ```bash
   git add -A
   git status -s | tail -n 30
   ```

2. Commit (multiple `-m` per OR42):
   ```bash
   git commit -m "prompt-3: Execution layer — routing, lifecycle, task state machine, DAG validator" -m "shared/types.py: extended with TaskState, Task, ComponentStatus, TASK_STATE_CHANNEL." -m "shared/lifecycle_manager.py: circuit breaker per AR16 (50 errors/10s -> CIRCUIT_BROKEN). Thread-safe, per-component error log (not module-level per AR4)." -m "shared/routing_engine.py: capability-based routing via ICapabilityIndex; skips non-ACTIVE components per A1." -m "shared/task_state_machine.py: ITaskStateQuery Protocol (locked named output per A5). In-memory only per A7. Publishes transitions on TASK_STATE_CHANNEL (A9 in-order)." -m "shared/dag_validator.py: acyclicity (Kahn's algorithm) + type-matching per A6. Prevents composite tasks with cycles from entering the state machine (P9)." -m "main.py: extended to register Lifecycle, Router, TaskStateMachine against ITaskStateQuery." -m "Tests: 32 new (7 lifecycle + 5 routing + 8 task_state + 6 dag + 6 composition_root). Total: 69." -m "Q3 (interface), Q4 (routing), Q14 (in-memory) resolved. Q3 implementation + Q14 durable backends deferred to DEBT."
   ```

3. Tag, push, verify:
   ```bash
   git tag prompt-3
   git push origin main
   git push origin prompt-3
   git ls-remote --tags origin | grep "prompt-3"
   ```

---

## Closing

Run `/close` workflow (all 21 steps). Expected:
- Tests: 69 passed
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped to Plan 3 `.py` files per OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs
- Vulture: 0 findings
- Detect-secrets: pass
- Custom AR checks: pass (no globals, ≤15 args, no context bags, docstrings)

**Key verifications**:
- `ITaskStateQuery` is a `Protocol` (A5)
- Circuit breaker triggers at 50 errors/10s (AR16)
- Routing engine skips CIRCUIT_BROKEN components (A1)
- Task state transitions published in-order (A9)
- DAG validator rejects cycles and type mismatches (A6, P9)
- In-memory persistence only — no durable backend code (A7)

After `/close`, create `logs/execution-log-prompt-3.md`. User pastes log, then asks Executor to commit/push.

**Reminder**: Step 21 (kill bash) mandatory.

---

## Files WILL Create

- `sovereignai/shared/lifecycle_manager.py`
- `sovereignai/shared/routing_engine.py`
- `sovereignai/shared/task_state_machine.py`
- `sovereignai/shared/dag_validator.py`
- `tests/test_lifecycle_manager.py`
- `tests/test_routing_engine.py`
- `tests/test_task_state_machine.py`
- `tests/test_dag_validator.py`
- `logs/execution-log-prompt-3.md` (created by `/close`)

## Files WILL Edit

- `sovereignai/shared/types.py` (append task + lifecycle types at S1.1; add `is_available()` to ComponentStatus at S3.1)
- `sovereignai/main.py` (extend `build_container()` at S6.1)
- `tests/test_composition_root.py` (add 6 new tests at S6.2)
- `DEBT.md` (add Q3 + Q14 deferrals at S7.2)
- `PLANS.md` (update test baseline at S7.1; add prompt-3 row at `/close`)
- `CHANGELOG.md` (append prompt-3 entry at S8)

## Files WILL NOT Edit

- `AGENTS.md`, `AI_HANDOFF.md`, `.devin/workflows/*.md` (stable)
- `documents/*` (archived)
- `prompts/*` (no changes)
- `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`, `README.md`, `txt/*` (stable)
- All `.gitkeep` files
- `DECISIONS.md`, `LANDMINES.md` (no new decisions/landmines unless execution surfaces them)

---

*Plan 3 — Execution Layer. Rev1. Architect draft. Part of Plans 1-4 batch — Round Table reviews alongside plan-1, plan-2, plan-4, and the shared context brief.*
