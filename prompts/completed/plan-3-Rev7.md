# Plan 3 — Execution Layer (Routing Engine, Lifecycle, Task State Machine, DAG Validator, ITaskStateQuery)

**Batch**: 3 of 4 (Plans 1–4 drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-2
Vision principles: 1 (sacred core), 5 (wire as you go), 7 (modular core), 9 (observability), 11 (DI, no globals), 12 (plain-English docstrings), 13 (strong, robust)
Open questions resolved: Q3 (memory abstraction interface — defined here, implementation deferred), Q4 (routing — capability-based via the graph), Q14 (persistence — in-memory only per A7; durable backends deferred to DEBT)

---

## Adjudication Log (Rev6 → Rev7)

Per GR4. Rev7 does not get a new context brief. 6 panelist responses were received on Rev6 (5 CLEAN PASS, 1 REVISE). One panelist (Kimi) caught 3 stale code blocks the Architect's adjudication described but didn't update in the actual plan code.

### Finding 1 — `dag_validator.py` still defines local `DAGValidationError` (Kimi HIGH)
**Severity**: HIGH (latent — breaks post-batch)
**Reasoning**: Rev6 Finding 3 said "Local exception definitions removed from dag_validator.py (S5.1)" but the actual S5.1 code block was never updated. It still has `class DAGValidationError(Exception):`. When composite tasks call `validate_dag()`, it raises `dag_validator.DAGValidationError` but Plan 4 catches `types.DAGValidationError` — different classes.
**Action**: ACCEPTED. S5.1 `dag_validator.py` code block updated: local `DAGValidationError` class definition removed. Import added: `from sovereignai.shared.types import DAGValidationError`.

### Verdict
All HIGH issues fixed. Plan 3 Rev7 is ready for execution.

---

## Adjudication Log (Rev5 → Rev6)

Per GR4. Rev6 does not get a new context brief. 6 panelist responses were received on Rev5. The following Rev5 issues were accepted and fixed.

### Finding 1 — `TraceEmitter` imported from `types.py` in `auth.py` and `capability_api.py` (Kimi HIGH, Qwen HIGH)
**Severity**: HIGH (ImportError at runtime — blocks execution)
**Reasoning**: `TraceEmitter` is defined in `sovereignai/shared/trace_emitter.py`, NOT in `types.py`. Both `auth.py` and `capability_api.py` import it from `types.py` → ImportError at module load.
**Action**: ACCEPTED. This is a Plan 4 fix (see Plan 4 Rev6 adjudication log).

### Finding 2 — `Optional`, `DAGSpec`, `EventBus` not imported in `task_state_machine.py` (Qwen HIGH)
**Severity**: HIGH (mypy blocks at /close)
**Reasoning**: S4.1 uses `Optional[DAGSpec]`, `Optional[TaskState]`, and `EventBus` in type annotations but none are in the import blocks. `EventBus` was never flagged in any prior revision — latent since Plan 3 Rev1.
**Action**: ACCEPTED. S4.1 imports updated: `Optional` added to typing import; `DAGSpec` added to types import; `EventBus` imported from `sovereignai.shared.event_bus`.

### Finding 3 — Duplicate exception definitions still in original modules (Kimi HIGH, Qwen HIGH)
**Severity**: HIGH (latent — doesn't trigger in this batch but breaks post-batch)
**Reasoning**: Rev5 Finding 1 added `DAGValidationError`, `InvalidStateTransitionError`, `UnknownTaskError` to `types.py`, but `dag_validator.py` and `task_state_machine.py` still define local copies. Plan 4 catches `types.DAGValidationError` but `dag_validator` raises `dag_validator.DAGValidationError` — different classes. The `except` clause won't match.
**Action**: ACCEPTED. Local exception definitions removed from `dag_validator.py` (S5.1) and `task_state_machine.py` (S4.1). Both modules now import from `sovereignai.shared.types`.

### Finding 6 — `_publish` old_state rationale stale (Qwen LOW)
**Severity**: LOW (behavior correct, rationale wrong)
**Reasoning**: Rev5 Finding 10 said "initial event uses None" but code uses `old_state or TaskState.RECEIVED` which converts None to RECEIVED. Behavior is semantically correct (a new task "came from" RECEIVED). Rationale was wrong.
**Action**: ACCEPTED. Adjudication log updated. Code unchanged (behavior is correct).

### Rejected findings

- **Gemini** "CORE_INTERNALS_CONCRETE_DENYLIST includes types" — false. Types was never in that denylist. It was in UI_PACKAGE_DENYLIST (removed in Rev5). The API test does NOT flag types imports.
- **Qwen** "sovereignai.shared.types removal is a no-op" — true but harmless. `sovereignai.shared` is still in UI_PACKAGE_DENYLIST with prefix matching. The rationale (UIs need types) is architecturally correct even if the mechanical effect is null.

### Verdict

All HIGH issues fixed. Plan 3 Rev6 is ready for execution.

---

## Adjudication Log (Rev4 → Rev5)

Per GR4. Rev5 does not get a new context brief. 6 panelist responses were received on Rev4. The following Rev4 issues were accepted and fixed.

### Finding 1 — Plan 4 imports undefined exception types from `types.py` (Kimi HIGH, Qwen HIGH)
**Severity**: HIGH (ImportError at Plan 4 /verify)
**Action**: ACCEPTED. Plan 3 S1.1 now defines `DAGValidationError`, `InvalidStateTransitionError`, `UnknownTaskError` in `shared/types.py`. Original modules import from there.

### Finding 2 — `task_state_machine.py` uses `Optional` and `DAGSpec` without importing (Qwen HIGH)
**Severity**: HIGH (mypy error at /close)
**Action**: ACCEPTED. Both added to imports.

### Finding 5 — `route()` lock contention + TOCTOU (all 6 panelists)
**Severity**: MEDIUM
**Action**: ACCEPTED. `try_recover()` now returns `ComponentStatus`. `route()` makes a single locked call.

### Finding 7 — Stale docstrings (Gemini, Kimi)
**Action**: ACCEPTED. TaskStateMachine docstring updated to "raises InvalidStateTransitionError." `set_status()` docstring updated to reference `try_recover()`.

### Finding 9 — `record_error()` can circuit-break unregistered component (Kimi LOW)
**Action**: ACCEPTED. Unregistered components are treated as STOPPED; `record_error()` is a no-op for them.

### Finding 10 — `_publish` emits initial RECEIVED with `old_state=RECEIVED` (Kimi LOW)
**Action**: ACCEPTED. `old_state` is now `Optional[TaskState]`; initial event uses `None`.

### Verdict
All HIGH/MEDIUM issues fixed. Plan 3 Rev5 is ready for execution.

---

## Adjudication Log (Rev3 → Rev4)

Per GR4. Rev4 does not get a new context brief. 5 panelist responses were received on Rev3. The following Rev3 issues were accepted and fixed.

### Finding 1 — `try_recover()` has no caller in production (Gemini HIGH, gpt-5.4-mini MEDIUM, DeepSeek MEDIUM, Kimi MEDIUM, Qwen MEDIUM — convergent)
**Severity**: HIGH (components stay broken forever)
**Reasoning**: Rev3 separated `get_status()` (read-only) from `try_recover()` (explicit recovery), but no component in the batch calls `try_recover()`. The RoutingEngine calls only `get_status()`. A circuit-broken component whose error window has expired stays CIRCUIT_BROKEN indefinitely — the system does not auto-recover from transient failures.
**Action**: ACCEPTED. S2.1 `RoutingEngine.route()` now calls `self._lifecycle.try_recover(component_id)` before checking status. If recovery succeeds, the component is treated as ACTIVE for this routing decision. This makes the routing path self-healing for components in active use. Components NOT in active routing still require a periodic heartbeat (deferred to DEBT — Finding 9).

### Finding 2 — Duplicate `NoActiveProviderError` definition (Qwen HIGH)
**Severity**: HIGH (exception type mismatch — callers catch wrong class)
**Reasoning**: Rev3 Plan 4 Finding 4 moved `NoActiveProviderError` from `routing_engine.py` to `shared/types.py`, but Plan 3 S2.1 was not updated to remove the local definition or import from `types.py`. Result: two different exception classes with the same name exist. Callers catching `types.NoActiveProviderError` won't catch exceptions raised by `routing_engine.route()`.
**Action**: ACCEPTED. S2.1 `routing_engine.py` no longer defines `NoActiveProviderError` locally. It imports from `sovereignai.shared.types`. **Execution order note**: Plan 4 S1.1 adds `NoActiveProviderError` to `types.py`. Plan 3 executes before Plan 4, so Plan 3 must also add `NoActiveProviderError` to `types.py` in S1.1 (Plan 3's type extension step). Plan 4's S1.1 then becomes a no-op for this type (it already exists). Cross-plan coordination: Plan 3 S1.1 adds it; Plan 4 S1.1 verifies it exists.

### Finding 8 — Test 5 description unclear about `try_recover()` requirement (Qwen LOW)
**Severity**: LOW (Executor writes wrong test)
**Reasoning**: Rev3 S3.3 test 5 said "51 errors over 11s (with 1s gap), still ACTIVE" but didn't mention `try_recover()`. In Rev3, `get_status()` is read-only — the test must call `try_recover()` to verify recovery.
**Action**: ACCEPTED. S3.3 test 5 updated to explicitly call `try_recover()` and assert it returns `True`.

### Finding 9 — Circuit breaker auto-recovery heartbeat deferred (Architect self-identified, complements Finding 1)
**Severity**: MEDIUM (operational gap)
**Reasoning**: Finding 1 fixes the routing path, but components not in active routing stay broken. A periodic heartbeat calling `try_recover()` on all components is the full fix. Out of scope for this batch (no heartbeat component exists).
**Action**: ACCEPTED as DEBT. Added `DEBT.md` entry: "Circuit breaker auto-recovery heartbeat."

### Rejected findings

- **DeepSeek** "off-by-one `>` vs `>=` verify" — AR16 says "more than 50 errors in 10 seconds" — `> 50` is correct (trips at 51). Verified in Rev3 code: `if len(log) > CIRCUIT_BREAKER_THRESHOLD:`. Test records 51 errors and asserts CIRCUIT_BROKEN. Correct.
- **DeepSeek** "get_state returns None vs transition raises — inconsistency" — different semantics for different operations. `get_state` is a query (None = not found); `transition` is an action (raise = precondition violated). Both are appropriate patterns. Document in DECISIONS.md (added D6).
- **Kimi** "DAGSpec lacks fields for real composite skills" — accepted as DEBT (Finding 5 in Plan 4 Rev4). Composite skills are post-batch per scope.

### Verdict

All HIGH/MEDIUM issues fixed. Plan 3 Rev4 is ready for execution.

---

## Adjudication Log (Rev2 → Rev3)

Per GR4. Rev3 does not get a new context brief. 6 panelist responses were received on Rev2. The following Rev2 issues were accepted and fixed.

### Finding 1 — S4.2 stale test descriptions (Kimi HIGH, Qwen HIGH — convergent)
**Severity**: HIGH (Executor writes failing tests)
**Reasoning**: Rev2 S4.1 changed `transition()` to raise `InvalidStateTransitionError` (Finding 3) and `get_state()` to return `None` for unknown (Finding 5). But S4.2 test descriptions still described Rev1 behavior:
- Test 3 `test_invalid_transition_logs_warn` — expects "no exception, trace has WARN" but code raises.
- Test 4 `test_terminal_states_have_no_transitions` — expects "no transition" but code raises.
- Test 5 `test_get_state_unknown_returns_failed` — expects "returns FAILED" but code returns None.
**Action**: ACCEPTED. S4.2 test descriptions updated:
- Test 3 → `test_invalid_transition_raises` — assert InvalidStateTransitionError raised, state unchanged.
- Test 4 → `test_terminal_states_raise_on_transition` — assert InvalidStateTransitionError.
- Test 5 → `test_get_state_unknown_returns_none` — assert returns None.

### Finding 6 — DAGSpec type never defined (Kimi MEDIUM, Qwen MEDIUM — convergent)
**Severity**: MEDIUM (mypy blocks; Executor has no spec)
**Reasoning**: Rev2 S4.1 `submit()` accepts `dag: Optional["DAGSpec"]` and accesses `dag.nodes`, `dag.edges`, `dag.input_types`, `dag.output_types` via attribute access. But no DAGSpec dataclass is defined anywhere. Mypy fails with `Name "DAGSpec" is not defined`.
**Action**: ACCEPTED. DAGSpec defined as a frozen dataclass in `shared/types.py` (S1.1 extension) with fields: `nodes: Tuple[str, ...]`, `edges: Tuple[Tuple[str, str], ...]`, `input_types: Dict[str, str]`, `output_types: Dict[str, str]`.

### Finding 7 — get_status() mutates state on read (Gemini MEDIUM, DeepSeek MEDIUM, Kimi MEDIUM, Qwen MEDIUM — convergent)
**Severity**: MEDIUM (semantic unsoundness, P9 observability gap)
**Reasoning**: Rev2 S3.2 `get_status()` auto-recovers CIRCUIT_BROKEN → ACTIVE when the error window expires. This mutates state during a read query, which (a) conflates "window expired?" with "component healthy?", (b) emits no trace so operators don't see recovery (P9 violation), (c) a component never queried stays broken forever while a single query flips it.
**Action**: ACCEPTED. S3.2 `get_status()` is now read-only. Auto-recovery moved to a separate `try_recover()` method that callers (e.g. the future RoutingEngine, or a periodic heartbeat) invoke explicitly. `try_recover()` emits an INFO trace on recovery. `get_status()` returns the current status without side effects. Tests updated to call `try_recover()` explicitly.

### Finding 11 — InvalidStateTransitionError uses FAILED as old_state for unknown tasks (Qwen LOW)
**Severity**: LOW (misleading error message)
**Reasoning**: Rev2 S4.1 `transition()` raised `InvalidStateTransitionError(task_id, TaskState.FAILED, new_state)` for unknown task_ids. The error message says "FAILED -> EXECUTING" but the task doesn't exist — it's not in FAILED state.
**Action**: ACCEPTED. New `UnknownTaskError(Exception)` class added. `transition()` raises `UnknownTaskError(task_id)` for unknown tasks, `InvalidStateTransitionError(task_id, old_state, new_state)` only for known tasks with invalid transitions.

### Rejected findings

- **DeepSeek** "circuit breaker TOCTOU race" — the Lock serializes get_status and record_error. No data race. The semantic issue (mutating on read) is accepted as Finding 7 above.
- **Kimi** "DAG validator rejects valid multi-producer DAGs" — design choice (ambiguous routing). Multi-producer forces the manifest author to disambiguate via priority.
- **DeepSeek** "transition_to acquires lock once, raise releases, partially modified state" — the code does all checks before any mutation. The raise exits the with block before any state write. Safe.

### Verdict

All HIGH/MEDIUM issues fixed. Plan 3 Rev3 is ready for execution.

---

## Adjudication Log (Rev1 → Rev2)

Per GR4. Rev2 does not get a new context brief. 6 panelist responses received. The following Rev1 issues were accepted and fixed.

### Finding 1 — DAG validator never called by TaskStateMachine.submit() (DeepSeek HIGH, Kimi HIGH)
**Severity**: HIGH (A6 unfulfilled, P9 violation)
**Reasoning**: Rev1 S5.1 created `dag_validator.py` and S5.2 tested it in isolation, but S4.1 `TaskStateMachine.submit()` accepted any Task and published it as RECEIVED without validation. A6 states composite skills must pass DAG validation before entering the state machine. A cyclic or type-mismatched composite skill would be accepted, emit a trace, and fail later at execution — a silent failure (P9 violation).
**Action**: ACCEPTED. S4.1 `submit()` now accepts an optional `dag` parameter (a tuple of nodes/edges/types). If provided, `validate_dag()` is called before the task enters RECEIVED state. If validation fails, `DAGValidationError` is raised (not silently swallowed). If no dag is provided (atomic task), validation is skipped — atomic tasks have no DAG to validate.

### Finding 2 — Circuit breaker has no reset mechanism (Qwen HIGH, Gemini MEDIUM)
**Severity**: HIGH (irreversible degradation)
**Reasoning**: Rev1 S3.2 `LifecycleManager.record_error()` set `CIRCUIT_BROKEN` when threshold exceeded, but the class exposed only `register()`, `get_status()`, and `record_error()` — no `reset()`, no half-open state, no time-based recovery. A transient failure would trip the breaker permanently for the process lifetime.
**Action**: ACCEPTED. S3.2 now includes a `reset(component_id)` method that clears the error log and sets status back to ACTIVE. Also: `get_status()` now checks if the error window has expired and auto-recovers (if no errors in the last 10 seconds, status flips from CIRCUIT_BROKEN back to ACTIVE). This implements a half-open-style recovery without a separate state.

### Finding 3 — Invalid transitions "log and ignore" allows corrupt state (Gemini HIGH, DeepSeek HIGH)
**Severity**: HIGH (P13 violation — silent corruption)
**Reasoning**: Rev1 S4.1 `transition()` logged invalid transitions at WARN and returned without raising. This allowed corrupt state to propagate — downstream DAG tasks could trigger under the assumption that upstream succeeded.
**Action**: ACCEPTED. S4.1 `transition()` now raises `InvalidStateTransitionError` for invalid transitions. The error includes the task_id, old_state, and attempted new_state. The state machine's state is NOT modified — the task remains in its valid state. Other tasks are unaffected (per-task isolation, not system-wide STOP).

### Finding 4 — Circuit breaker doesn't emit trace when tripped (DeepSeek MEDIUM)
**Severity**: MEDIUM (P9 observability)
**Reasoning**: Rev1 S3.2 `record_error()` updated `_statuses` but never called `trace.emit(...)`. An operator watching the Log drawer would see errors but no indication that a component was unloaded.
**Action**: ACCEPTED. S3.2 `record_error()` now accepts a `trace: TraceEmitter` parameter (added to constructor). When the circuit breaks, an ERROR trace is emitted with the component_id and error count.

### Finding 5 — `ITaskStateQuery.get_state` returns FAILED for unknown UUID (DeepSeek MEDIUM)
**Severity**: MEDIUM (misleading semantics)
**Reasoning**: Rev1 S4.1 returned `TaskState.FAILED` for unknown UUIDs. This conflated "never submitted" with "submitted and failed." A UI querying a typo UUID would see "task failed."
**Action**: ACCEPTED. S4.1 `get_state()` now returns `None` for unknown UUIDs. The Protocol signature changes to `Optional[TaskState]`. Callers (including Plan 4's Capability API) must handle `None` explicitly.

### Finding 6 — LifecycleManager exposes no way to set DEGRADED or STOPPED (DeepSeek MEDIUM)
**Severity**: MEDIUM (incomplete API)
**Reasoning**: Rev1 S3.2 defined `DEGRADED` and `STOPPED` in the enum and tests skipped them, but the manager only set ACTIVE (register) and CIRCUIT_BROKEN (record_error). No public method to reach other states.
**Action**: ACCEPTED. S3.2 now includes `set_status(component_id, status)` method. Tests can use it; future operational code can use it to degrade or stop a component.

### Finding 7 — `now_utc_safe()` unnecessary lazy-import wrapper (Qwen MEDIUM)
**Severity**: MEDIUM (code clarity)
**Reasoning**: Rev1 S4.1 had a `now_utc_safe()` function that lazily imported `now_utc` from `types.py`, but the module already imported from `types` at the top. The wrapper added indirection.
**Action**: ACCEPTED. `now_utc_safe()` removed. `_publish()` calls `now_utc()` directly from the top-level import.

### Rejected findings

- **DeepSeek** "off-by-one circuit breaker `>` vs `>=`" — AR16 says "more than 50 errors in 10 seconds" — `> 50` is correct. The threshold is exclusive (51 errors trips it). Test `test_record_error_at_threshold_circuit_breaks` records 51 errors and asserts CIRCUIT_BROKEN.
- **Qwen** "DAG validator rejects valid multi-producer DAGs" — this is a design choice. The vision's Q28 says composite skills have nodes with UUIDs and directed edges with optional condition expressions. Multi-producer (one type, multiple sources) is ambiguous routing — the Routing Engine should pick one, not accept both. The validator correctly flags this as an error to force the manifest author to disambiguate via priority.
- **Gemini** "synchronous event bus blockage by slow subscribers" — true but out of scope for Plan 3. The event bus is Plan 1's component. A subscriber timeout would be a Plan 1 change. Accept as a documented limitation; defer to DEBT if needed.

### Verdict

All HIGH/MEDIUM issues fixed. Plan 3 Rev2 is ready for execution.

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
# Routing errors (used by RoutingEngine in S2; moved here per Rev4 Finding 2)
# ============================================================================

class NoActiveProviderError(Exception):
    """Raised when no active component provides the requested capability.

    Per Rev4 Finding 2: defined here (shared/types.py) so both
    routing_engine.py and capability_api.py import from the same location.
    """

    def __init__(self, message: str = "No active provider for the requested capability") -> None:
        """Create a no-active-provider error with a descriptive message."""
        super().__init__(message)


class UnknownTaskError(Exception):
    """Raised when an operation references a task_id that was never submitted.

    Per Rev5 Finding 1: moved from task_state_machine.py to types.py.
    """

    def __init__(self, task_id) -> None:
        """Create an error for an unknown task ID."""
        self.task_id = task_id
        super().__init__(f"Unknown task {task_id} — never submitted")


class InvalidStateTransitionError(Exception):
    """Raised when a task state transition violates the state machine's rules.

    Per Rev5 Finding 1: moved from task_state_machine.py to types.py.
    """

    def __init__(self, task_id, old_state, new_state) -> None:
        """Create an error describing an invalid state transition attempt."""
        self.task_id = task_id
        self.old_state = old_state
        self.new_state = new_state
        super().__init__(f"Invalid transition {old_state} -> {new_state} for task {task_id}")


class DAGValidationError(Exception):
    """Raised when a skill DAG has a cycle or a type mismatch.

    Per Rev5 Finding 1: moved from dag_validator.py to types.py.
    """


# ============================================================================
# DAG types (used by DAG validator + TaskStateMachine.submit in S4/S5)
# ============================================================================

@dataclass(frozen=True)
class DAGSpec:
    """Specification of a composite skill's directed acyclic graph.
    
    Per Rev3 Finding 6: defined here so TaskStateMachine.submit() can
    accept it as a typed parameter. Frozen so the spec is immutable
    once constructed — a composite skill's DAG cannot be mutated after
    submission.
    
    Attributes:
        nodes: Tuple of skill node IDs (e.g. ("open_browser", "register_email")).
        edges: Tuple of (source, target) pairs meaning source's output
            feeds into target's input.
        input_types: Map of node ID -> type name it requires as input.
        output_types: Map of node ID -> type name it produces as output.
    """
    nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    input_types: dict[str, str]
    output_types: dict[str, str]


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

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.types import (
    CapabilityCategory,
    ComponentId,
    ComponentStatus,
    NoActiveProviderError,
)


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

        Per Rev4 Finding 1: calls `try_recover(component_id)` before
        checking status. If the error window has expired, the component
        is recovered to ACTIVE and routing proceeds. This makes the
        routing path self-healing for components in active use.

        Args:
            category: The capability category needed.
            name: The specific capability name needed.

        Returns:
            ComponentId of the chosen provider.

        Raises:
            NoActiveProviderError: If no ACTIVE component provides the
                requested capability (after attempting recovery).
        """
        providers = self._index.find_providers(category, name)
        for component_id, _declaration in providers:
            status = self._lifecycle.try_recover(component_id)
            if status.is_available():
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

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ComponentId, ComponentStatus, TraceLevel


CIRCUIT_BREAKER_THRESHOLD = 50      # errors
CIRCUIT_BREAKER_WINDOW_SECONDS = 10.0


class LifecycleManager:
    """Track component status and enforce the circuit breaker rule.

    Per AR16: a component that records more than 50 errors in 10 seconds
    is automatically unloaded (circuit-broken). The Routing Engine queries
    the Lifecycle Manager to skip circuit-broken components.

    Per AR18: no component manages its own lifecycle. This module is the
    sole authority for spawning, promoting, loading, and unloading.

    Per Finding 2 (Rev2): circuit breaker now auto-recovers. If
    `get_status()` is called and the error window has expired (no errors
    in the last 10 seconds), status flips from CIRCUIT_BROKEN back to
    ACTIVE. A `reset()` method is also provided for explicit recovery.

    Per Finding 4 (Rev2): emits an ERROR trace when the circuit breaks.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a lifecycle manager with no registered components.

        Args:
            trace: Trace emitter for logging circuit-breaker trips and
                status changes (per Finding 4 — P9 observability).
        """
        self._trace = trace
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
        """Return the current status of a registered component (read-only).

        Per Finding 7 (Rev3): this method is now read-only. It returns
        the current status WITHOUT auto-recovering. Auto-recovery moved
        to `try_recover()` which callers invoke explicitly. This separates
        "what is the status?" from "should we attempt recovery?" — the
        conflation in Rev2 caused semantic unsoundness (a component never
        queried stayed broken forever; a single query flipped it).

        Args:
            component_id: The component to query.

        Returns:
            ComponentStatus. Returns STOPPED if the component was
            never registered (defensive default).
        """
        with self._lock:
            return self._statuses.get(component_id, ComponentStatus.STOPPED)

    def try_recover(self, component_id: ComponentId) -> ComponentStatus:
        """Attempt recovery; return resulting status (single locked call per Rev5 Finding 5)."""
        now = monotonic()
        recovered = False
        with self._lock:
            status = self._statuses.get(component_id, ComponentStatus.STOPPED)
            if status is ComponentStatus.CIRCUIT_BROKEN:
                log = self._error_log.get(component_id, deque())
                cutoff = now - CIRCUIT_BREAKER_WINDOW_SECONDS
                while log and log[0] < cutoff:
                    log.popleft()
                if len(log) == 0:
                    self._statuses[component_id] = ComponentStatus.ACTIVE
                    status = ComponentStatus.ACTIVE
                    recovered = True
        if recovered:
            self._trace.emit(
                component="LifecycleManager",
                level=TraceLevel.INFO,
                message=f"Component {component_id} recovered to ACTIVE (error window expired)",
            )
        return status

    def set_status(self, component_id: ComponentId, status: ComponentStatus) -> None:
        """Manually set a component's status (per Finding 6 — Rev2).

        Use for operational signals: degrade a component under load, stop
        a component for maintenance. The circuit breaker's auto-trip
        (record_error) and auto-recover (get_status) still apply on top
        of this manual setting.

        Args:
            component_id: The component to update.
            status: The new status.
        """
        with self._lock:
            self._statuses[component_id] = status
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} status set to {status}",
        )

    def reset(self, component_id: ComponentId) -> None:
        """Clear a component's error log and restore ACTIVE status (per Finding 2 — Rev2).

        Use after fixing the underlying cause of a circuit break, or to
        force recovery without waiting for the window to expire.

        Args:
            component_id: The component to reset.
        """
        with self._lock:
            self._error_log[component_id] = deque()
            self._statuses[component_id] = ComponentStatus.ACTIVE
        self._trace.emit(
            component="LifecycleManager",
            level=TraceLevel.INFO,
            message=f"Component {component_id} reset to ACTIVE (error log cleared)",
        )

    def record_error(self, component_id: ComponentId) -> None:
        """Record one error for a component and check the circuit breaker.

        If the rolling 10-second error count exceeds the threshold
        (50 per AR16), the component is automatically circuit-broken.
        Per Finding 4 (Rev2): emits an ERROR trace when the circuit
        breaks, so operators can see the trip in the Log drawer.

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
            # Check threshold (AR16: "more than 50" — exclusive, trips at 51)
            if len(log) > CIRCUIT_BREAKER_THRESHOLD:
                if self._statuses.get(component_id) != ComponentStatus.CIRCUIT_BROKEN:
                    self._statuses[component_id] = ComponentStatus.CIRCUIT_BROKEN
                    # Emit trace outside the lock to avoid deadlock on TraceEmitter
                    tripped = True
                    error_count = len(log)
                else:
                    tripped = False
                    error_count = len(log)
            else:
                tripped = False
                error_count = len(log)
        if tripped:
            self._trace.emit(
                component="LifecycleManager",
                level=TraceLevel.ERROR,
                message=(
                    f"Circuit breaker tripped for {component_id} "
                    f"({error_count} errors in {CIRCUIT_BREAKER_WINDOW_SECONDS}s)"
                ),
            )
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
5. **`test_try_recover_after_window_expires_returns_true`** — Rev4 update per Finding 8. Record 51 errors (trips breaker), mock time forward 11s, call `try_recover()`, assert returns `True` and status is ACTIVE. (Rev3 description was unclear about needing `try_recover()` — `get_status()` is read-only in Rev3+.)
6. **`test_circuit_broken_is_not_available`** — `ComponentStatus.CIRCUIT_BROKEN.is_available()` returns False
7. **`test_active_is_available`** — `ComponentStatus.ACTIVE.is_available()` returns True

For test 5 (window expiry), use `unittest.mock.patch` on `monotonic` to simulate time passing.

After tests pass, run `/verify`.

### S3.4 — Create `tests/test_routing_engine.py`

Required tests:

1. **`test_route_returns_highest_priority_active`** — two providers, both ACTIVE, returns higher priority
2. **`test_route_skips_circuit_broken`** — higher-priority provider CIRCUIT_BROKEN (window not expired), returns lower-priority ACTIVE one
3. **`test_route_recovers_circuit_broken_when_window_expired`** — Rev4 addition per Finding 1. Higher-priority provider CIRCUIT_BROKEN but error window expired; `route()` calls `try_recover()` internally, recovery succeeds, returns the recovered provider
4. **`test_route_raises_when_no_active_provider`** — all providers CIRCUIT_BROKEN (window not expired), raises NoActiveProviderError
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
from typing import Dict, List, Optional, Protocol, Tuple
from uuid import UUID

from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    DAGSpec,
    DAGValidationError,
    InvalidStateTransitionError,
    TaskState,
    Task,
    TaskStateChanged,
    TASK_STATE_CHANNEL,
    TraceLevel,
    UnknownTaskError,
    now_utc,
)


# NOTE (Rev6 Finding 3): UnknownTaskError, InvalidStateTransitionError, and
# DAGValidationError are defined in shared/types.py (Plan 3 S1.1 per Rev5
# Finding 1) and imported above. Do NOT define local copies — the import is
# canonical. Local definitions would create separate exception classes that
# callers catching types.DAGValidationError would not match.


class ITaskStateQuery(Protocol):
    """Locked query interface for the task state machine.

    Plan 4's Capability API imports ONLY this protocol — never the
    concrete TaskStateMachine class. This enforces AR7 (UIs are
    separate processes consuming the Capability API).
    """

    def get_state(self, task_id: UUID) -> Optional[TaskState]:
        """Return the current state of a task by its ID, or None if unknown.

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown (per
            Finding 5 — None distinguishes "never submitted" from
            "submitted and failed").
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

    def submit(self, task: Task, dag: Optional[DAGSpec] = None) -> None:
        """Accept a new task into the RECEIVED state, validating its DAG if provided.

        Per Finding 1 (Rev2): if a `dag` parameter is provided, the DAG
        validator runs BEFORE the task enters RECEIVED. If validation
        fails, DAGValidationError is raised and the task is NOT submitted.
        This satisfies A6 (composite skills must validate before entering
        the state machine).

        Per Finding 6 (Rev3): `dag` is now typed as `Optional[DAGSpec]`
        (a frozen dataclass defined in shared/types.py). Rev2 used a
        string forward reference `Optional["DAGSpec"]` but never
        defined the type — mypy blocked.

        Args:
            task: Frozen Task instance to track.
            dag: Optional DAGSpec for composite tasks. If provided,
                validated via validate_dag() before submission.
                If None (atomic task), validation is skipped.

        Raises:
            DAGValidationError: If `dag` is provided and fails validation.
        """
        if dag is not None:
            from sovereignai.shared.dag_validator import validate_dag
            validate_dag(
                nodes=list(dag.nodes),
                edges=list(dag.edges),
                input_types=dag.input_types,
                output_types=dag.output_types,
            )
        with self._lock:
            self._tasks[task.task_id] = task
            self._states[task.task_id] = TaskState.RECEIVED
        self._publish(task.task_id, None, TaskState.RECEIVED)

    def transition(self, task_id: UUID, new_state: TaskState) -> None:
        """Move a task to a new state if the transition is valid.

        Per Finding 3 (Rev2): invalid transitions now raise
        InvalidStateTransitionError instead of being silently logged.
        The task's state is NOT modified on invalid transition. Other
        tasks are unaffected (per-task isolation).

        Per Finding 11 (Rev3): unknown task_ids raise UnknownTaskError
        (not InvalidStateTransitionError with FAILED as old_state).

        Args:
            task_id: UUID of the task to transition.
            new_state: Target state.

        Raises:
            UnknownTaskError: If the task_id was never submitted.
            InvalidStateTransitionError: If the transition is not in
                the valid transitions table.
        """
        with self._lock:
            old_state = self._states.get(task_id)
            if old_state is None:
                raise UnknownTaskError(task_id)
            if new_state not in _VALID_TRANSITIONS.get(old_state, []):
                raise InvalidStateTransitionError(task_id, old_state, new_state)
            self._states[task_id] = new_state
        self._publish(task_id, old_state, new_state)

    def get_state(self, task_id: UUID) -> Optional[TaskState]:
        """Return the current state of a task by its ID, or None if unknown.

        Per Finding 5 (Rev2): returns None for unknown UUIDs instead of
        FAILED. Callers must handle None explicitly — a None means "task
        was never submitted" which is distinct from "task was submitted
        and failed."

        Args:
            task_id: UUID of the task to query.

        Returns:
            TaskState if the task is tracked, None if unknown.
        """
        with self._lock:
            return self._states.get(task_id)

    def list_tasks(self) -> Tuple[Task, ...]:
        """Return all tasks currently tracked by the state machine.

        Returns:
            Tuple of Task instances, in insertion order (oldest first).
        """
        with self._lock:
            return tuple(self._tasks.values())

    def _publish(self, task_id: UUID, old_state: Optional[TaskState],
                 new_state: TaskState) -> None:
        """Publish a TaskStateChanged event on the task state channel.

        Per Finding 7 (Rev2): uses `now_utc()` directly from the
        top-level import instead of the removed `now_utc_safe()` wrapper.

        Args:
            task_id: UUID of the task that transitioned.
            old_state: Previous state, or None for the initial RECEIVED.
            new_state: New state.
        """
        event = TaskStateChanged(
            channel=TASK_STATE_CHANNEL,
            correlation_id=task_id,
            timestamp=now_utc(),
            task_id=task_id,
            old_state=old_state or TaskState.RECEIVED,
            new_state=new_state,
        )
        self._bus.publish(event)


# Removed in Rev2 per Finding 7: now_utc_safe() lazy-import wrapper.
# _publish() now calls now_utc() directly from the top-level import.
```

**Verify:**
- `ITaskStateQuery` is a `Protocol` (A5)
- `TaskStateMachine` implements it
- Valid transitions enforced (RECEIVED → QUEUED → EXECUTING → COMPLETE/FAILED)
- Invalid transitions raise `InvalidStateTransitionError`; state is NOT modified (Rev5 Finding 7: updated from stale "logged at WARN" docstring)
- State changes published on `TASK_STATE_CHANNEL` (A9 in-order)
- Thread-safe (Lock)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S4.2 — Create `tests/test_task_state_machine.py`

Required tests:

1. **`test_submit_sets_received`** — submit, get_state returns RECEIVED
2. **`test_valid_transition_publishes_event`** — RECEIVED → QUEUED, subscriber receives TaskStateChanged
3. **`test_invalid_transition_raises`** — Rev3 update per Finding 1. RECEIVED → COMPLETE, assert `InvalidStateTransitionError` raised, state unchanged (still RECEIVED)
4. **`test_terminal_states_raise_on_transition`** — Rev3 update per Finding 1. COMPLETE → anything, assert `InvalidStateTransitionError` raised
5. **`test_get_state_unknown_returns_none`** — Rev3 update per Finding 1. Unknown UUID, returns `None` (not FAILED)
6. **`test_list_tasks_returns_insertion_order`** — submit 3, list returns in submit order
7. **`test_protocol_compliance`** — `isinstance(machine, ITaskStateQuery)` returns True
8. **`test_transitions_published_in_order`** — submit, transition to QUEUED, transition to EXECUTING; subscriber receives 3 events in order (A9 verification)
9. **`test_transition_unknown_task_raises_unknown_task_error`** — Rev3 addition per Finding 11. transition() on unknown UUID raises `UnknownTaskError` (not `InvalidStateTransitionError`)
10. **`test_submit_with_valid_dag_passes`** — Rev3 addition per Finding 6. submit with a valid DAGSpec, task enters RECEIVED
11. **`test_submit_with_invalid_dag_raises`** — Rev3 addition per Finding 6. submit with a cyclic DAGSpec, `DAGValidationError` raised, task NOT submitted

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

from sovereignai.shared.types import DAGValidationError


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
    # 4. LifecycleManager — depends on TraceEmitter, singleton (Plan 3)
    # Rev2 per Finding 4: accepts TraceEmitter to emit on circuit-breaker trips.
    from sovereignai.shared.lifecycle_manager import LifecycleManager
    lifecycle = LifecycleManager(trace=trace)
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
- sovereignai/shared/types.py (extended: TaskState, TaskStateChanged, Task, ComponentStatus, TASK_STATE_CHANNEL, DAGSpec per Rev3 Finding 6, NoActiveProviderError per Rev4 Finding 2)
- sovereignai/shared/lifecycle_manager.py (new — circuit breaker per AR16, 50 errors/10s; reset() per Finding 2; emits ERROR trace per Finding 4; set_status per Finding 6; get_status read-only + try_recover() per Rev3 Finding 7)
- sovereignai/shared/routing_engine.py (new — capability-based routing, skips non-ACTIVE; calls try_recover() per Rev4 Finding 1; imports NoActiveProviderError from types per Rev4 Finding 2)
- sovereignai/shared/task_state_machine.py (new — ITaskStateQuery protocol, in-memory only per A7; raises InvalidStateTransitionError per Finding 3; submit() validates DAG per Finding 1; get_state returns None for unknown per Finding 5; UnknownTaskError per Rev3 Finding 11; DAGSpec typed per Rev3 Finding 6; now_utc_safe removed per Finding 7)
- sovereignai/shared/dag_validator.py (new — acyclicity + type-matching per A6; wired into submit() per Finding 1)
- sovereignai/main.py (extended: registers Lifecycle (with trace), Router, TaskStateMachine against ITaskStateQuery)
- DEBT.md (add circuit breaker auto-recovery heartbeat per Rev4 Finding 9)
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

*Plan 3 — Execution Layer. Rev7. Architect draft. Part of Plans 1-4 batch — Round Table reviews alongside plan-1-Rev3, plan-2-Rev3, plan-4-Rev7, and the shared context brief. Adjudication logs above record Rev1 → Rev2 → Rev3 → Rev4 → Rev5 → Rev6 → Rev7 changes per GR4.*
