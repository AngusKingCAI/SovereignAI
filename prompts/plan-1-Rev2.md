# Plan 1 — Core Scaffold (Event Bus, TraceEmitter, DI Container, Types, Composition Root)

**Batch**: 1 of 4 (Plans 1–4 are drafted together; shared context brief at `plan-1-4-batch-Rev1-context-brief.md`)

Depends on: prompt-0.4
Vision principles: 1 (sacred core), 5 (wire as you go — implementations AND contracts), 7 (modular core), 9 (observability by default — TraceEmitter), 11 (DI, no globals, no context bags), 12 (plain-English docstrings), 13 (strong, robust)
Open questions resolved: Q9 (test strategy — conformance + contract + property-based, established here), Q32 (DEBT.md scaffold — already done in prompt-0)

---

## Adjudication Log (Rev1 → Rev2)

Per GR4. Rev2 does not get a new context brief — the Round Table reviews this revised file directly. 6 panelist responses were received (gpt-5.4-mini, llama4, Gemini-3.5-Flash, DeepSeek, Kimi, Qwen). The following Rev1 issues were accepted and fixed.

### Finding 1 — EventBus imports TraceEmitter from wrong file (Kimi HIGH)
**Severity**: HIGH (blocks execution)
**Reasoning**: Rev1 S2.1 imported `TraceEmitter` from `sovereignai.shared.types`, but S3.1 defines `TraceEmitter` in `sovereignai/shared/trace_emitter.py`. The import would fail with `ImportError: cannot import name 'TraceEmitter' from 'sovereignai.shared.types'`.
**Action**: ACCEPTED. S2.1 import list corrected to import `TraceEmitter` from `sovereignai.shared.trace_emitter`. Note: this creates a forward reference (S2.1 imports from S3.1's file), but Python resolves imports at module load time, so as long as both files exist when `event_bus.py` is imported, this works. The plan's step order (S2 before S3) is preserved because the import is resolved at runtime, not at edit time.

### Finding 2 — main.py smoke test passes `level="info"` string (Kimi MEDIUM, upgraded to HIGH)
**Severity**: HIGH (smoke test is the wiring verification)
**Reasoning**: Rev1 S5.1 `__main__` block called `trace.emit(..., level="info", ...)`. The `emit()` signature expects `level: TraceLevel`. While `TraceLevel(str, Enum)` allows the string at runtime, `event.level.value` in the print statement would raise `AttributeError` on a plain `str`. The smoke test is the only verification that the composition root is wired correctly — if it fails, the wiring is unverified.
**Action**: ACCEPTED. S5.1 `__main__` block changed to `level=TraceLevel.INFO` with the proper import.

### Finding 3 — DIContainer docstring claims thread-safety but has no Lock (Kimi MEDIUM, Qwen MEDIUM)
**Severity**: MEDIUM
**Reasoning**: Rev1 S4.1 docstring said "Thread-safe: registration and retrieval may happen concurrently from different components." The implementation had no `Lock`. Once Plan 2–4 components register concurrently, dict mutation races could produce lost registrations.
**Action**: ACCEPTED. S4.1 implementation now includes a `threading.Lock` around `_instances` and `_factories`. Docstring claim is now accurate.

### Finding 4 — TraceEmitter.emit `correlation_id` parameter lacks type annotation (Kimi LOW)
**Severity**: LOW (would block mypy strict)
**Reasoning**: Rev1 S3.1 had `correlation_id=None` with no type annotation. Strict mypy flags this.
**Action**: ACCEPTED. S3.1 signature now reads `correlation_id: UUID | None = None`.

### Finding 5 — dependency-injector added to requirements but never used (Qwen MEDIUM — partially accepted)
**Severity**: MEDIUM (governance tension)
**Reasoning**: Qwen flagged that `dependency-injector>=1.2` is added to `txt/requirements.txt` per OR39 but the S4.1 DIContainer is hand-rolled using plain dicts — no import of `dependency_injector` anywhere. This is correct: A8 mandates a passive registry (no `@inject`, no auto-wiring), which the hand-rolled container satisfies. But AR4 names `dependency-injector` as the DI library. There's a tension between AR4 (names the library) and A8 (passive registry, no auto-wiring magic).
**Action**: PARTIALLY ACCEPTED. The hand-rolled passive container is correct per A8. AR4's reference to `dependency-injector` is stale — it predates A8's clarification. Plan 1 Rev2 keeps the hand-rolled container, removes `dependency-injector>=1.2` from `txt/requirements.txt` (no runtime dep needed), and adds a DEBT entry noting that AR4 should be amended to remove the `dependency-injector` reference (Architect will propose the AR4 amendment in a future plan's S0.3).

### Rejected findings

- **Llama4** "shared/types.py might not be sufficient" — speculative, no concrete failure scenario. The incremental approach is sound (verified by Q-A engagement).
- **Qwen** "Channel uses NewType but downstream may need typed channels" — speculative future concern. Accept for MVP; DEBT entry added if needed in Plan 2+.

### Verdict

All HIGH issues fixed. Plan 1 Rev2 is ready for execution.

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify previous tag (`prompt-0.4`) exists on origin. Confirm working copy is clean and on `main`. Activate venv per step 4 (OR45).

**S0.2** — Read `AGENTS.md` in full. Note the always-on subset (OR5, OR6, OR15, OR16, OR34, AR5, AR16, AR21) applies to every edit. Note OR39 (runtime deps go in `txt/requirements.txt` — first runtime dep lands in this plan), OR46 (absolute venv paths), OR47 (mypy on `.py` files only).

**S0.3** — No new AR/OR rules this plan. The existing rules (AR4–AR6, AR21, OR39, OR46, OR47) are sufficient. Proceed to S1.

---

## Architectural Context (read before S1)

This plan establishes the foundational layer that Plans 2–4 build on. Per the locked scope adjudication (A1–A9 in `documents/plan-1-4-scope-adjudication.md`):

- **A2** — `shared/types.py` is the canonical type module. All downstream plans import from here only. Types are frozen dataclasses.
- **A3** — Composition Root is incremental. `main.py` wires only Plan 1 components. Plans 2–4 extend it. Q26 confirmed at Plan 4 `/close`, not here.
- **A8** — DI container is a passive typed registry. No `@inject` decorators, no auto-wiring magic. `main.py` does all explicit instantiation in topological order.
- **A9** — Event bus guarantees in-order delivery per typed channel. This must be verified by this plan's test suite (Plan 3's task state machine depends on it).

**Key constraints from AGENTS.md:**
- AR4: `shared/container.py` is the DI container. No global mutable state. `shared/` holds contracts, interfaces, and the DI container only — no runtime state outside the container.
- AR5: ≤15 constructor args per class. `main.py` (Composition Root) is exempt.
- AR6: No context bags. TraceEmitter is permitted as a typed single-responsibility argument, not a vehicle for bypassing explicit-argument discipline.
- AR21: Every `def`/`async def` has a docstring. First line: verb-first, ≥10 words, plain English, no jargon.

**Per OR39**: this plan introduces the first runtime dependency (`dependency-injector` per AR4). Append `dependency-injector>=1.2` to `txt/requirements.txt`, then run `.venv/Scripts/pip.exe install -e .[dev]` and `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt`.

---

## S1 — `shared/types.py` (Core Domain Types)

### S1.1 — Create `sovereignai/shared/__init__.py`

Empty file (or minimal docstring). Marks `shared/` as a Python package.

### S1.2 — Create `sovereignai/shared/types.py`

Define core domain types as **frozen dataclasses** (per A2). These are the canonical types all downstream plans import. Do NOT add speculative types — only types this plan or Plan 2–4 will use (per P5 wire-as-you-go).

Required types (Plan 1 needs these; Plan 2–4 will extend):

```python
"""Core domain types shared across all SovereignAI components.

This module is the single source of truth for domain types. All other
modules import from here — never define duplicate types elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import NewType, Sequence
from uuid import UUID, uuid4


# ============================================================================
# Trace types (used by TraceEmitter in S3)
# ============================================================================

class TraceLevel(str, Enum):
    """Severity level for trace events, ordered from least to most severe."""
    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class TraceEvent:
    """Single observability event emitted by a component via TraceEmitter.

    Immutable so events can be safely shared across threads and stored in
    trace memory without risk of mutation.
    """
    component: str          # e.g. "EventBus", "TraceEmitter", "main"
    level: TraceLevel
    message: str            # plain-English description of what happened
    timestamp: datetime     # UTC, timezone-aware (per OR20)
    correlation_id: UUID    # groups events from the same task or request


# ============================================================================
# Event bus types (used by EventBus in S2)
# ============================================================================

# Typed channel identifier — NewType prevents passing a raw string where a
# Channel is expected. Channels are per-type: each event type has its own
# channel, and the bus guarantees in-order delivery per channel (per A9).
Channel = NewType("Channel", str)


@dataclass(frozen=True)
class Event:
    """Base type for all events published on the event bus.

    Subclasses (defined in Plans 2-4) add payload fields. The base type
    carries only routing metadata. Frozen so events are immutable once
    published — a subscriber cannot modify an event before another
    subscriber sees it.
    """
    channel: Channel
    correlation_id: UUID
    timestamp: datetime     # UTC, timezone-aware (per OR20)


# ============================================================================
# Component identity (used by DI container in S4, capability graph in Plan 2)
# ============================================================================

ComponentId = NewType("ComponentId", str)  # e.g. "EventBus", "TraceEmitter"


# ============================================================================
# Helper functions
# ============================================================================

def now_utc() -> datetime:
    """Return the current time in UTC with timezone awareness.
    
    Use this instead of datetime.now() or datetime.utcnow() — both are
    forbidden per OR20 (naive/aware datetime mixing caused L6).
    """
    return datetime.now(timezone.utc)


def new_correlation_id() -> UUID:
    """Generate a fresh UUID4 for correlating events across components."""
    return uuid4()
```

**Verify:**
- All types are `frozen=True` dataclasses (immutability per A2)
- `datetime` fields use timezone-aware values (helper `now_utc()` enforces OR20)
- No speculative types — only what Plan 1 + Plans 2–4 will use
- Module docstring + every `def` has a docstring (AR21 — verb-first, ≥10 words, plain English)

After creating, run `/verify` (TOML/Python syntax check + ruff).

### S1.3 — No runtime dependency added this plan (Rev2 change)

**Rev1 → Rev2 change**: Rev1 added `dependency-injector>=1.2` to `txt/requirements.txt` per OR39. The S4.1 DIContainer is hand-rolled using plain dicts (correct per A8 — passive registry, no auto-wiring). The `dependency-injector` library is never imported. AR4's reference to `dependency-injector` is stale (predates A8's clarification).

**Rev2 action**: Do NOT add `dependency-injector>=1.2` to `txt/requirements.txt`. The hand-rolled passive container is correct per A8. Add a DEBT entry noting that AR4 should be amended to remove the `dependency-injector` reference (Architect will propose the AR4 amendment in a future plan's S0.3).

**Append to `DEBT.md`** (use Edit tool):

```markdown
## Deferred: AR4 amendment — remove dependency-injector reference

**Deferred at**: prompt-1 (per Plan 1-4 batch Round Table Rev2 adjudication, Finding 5)
**Reason**: AR4 names `dependency-injector` as the DI library, but A8 mandates a passive registry (no `@inject`, no auto-wiring). The hand-rolled DIContainer in `shared/container.py` satisfies A8 without using the `dependency-injector` library. AR4's reference is stale.
**Trigger condition**: When the Architect next drafts a plan's S0.3 (next batch, Plan 5+).
**Target plan**: Plan 5 (Scan) or first plan in next batch.
```

No `pip install` or `pip-audit` step needed this plan — `txt/requirements.txt` remains empty.

After creating the DEBT entry, run `/verify`.

---

## S2 — Event Bus (In-Order Per Channel)

### S2.1 — Create `sovereignai/shared/event_bus.py`

Per A9: the event bus guarantees in-order delivery per typed channel. Subscribers receive events in the order they were published, per channel. Cross-channel ordering is NOT guaranteed.

Per P10 (no silent failures): if a subscriber raises, the bus catches, logs at ERROR via TraceEmitter, and continues — does NOT silently swallow.

Per AR4: the bus receives its TraceEmitter via constructor injection, never instantiates it.

Per AR6: the bus does NOT accept a context bag — TraceEmitter is the only permitted non-business argument.

```python
"""Typed event bus with in-order delivery per channel.

The bus is transparent infrastructure (per Q6 resolution): it routes
events, it does not orchestrate. Subscribers register for a channel;
publishers send events to a channel. The bus guarantees that events on
the same channel arrive at each subscriber in publish order.
"""
from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import Callable, Dict, List

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    Channel,
    Event,
    TraceLevel,
)


Subscriber = Callable[[Event], None]


class EventBus:
    """Route events from publishers to subscribers, preserving per-channel order.

    Each channel has its own subscriber list and its own ordering guarantee.
    A subscriber registered for channel A will receive channel A's events in
    publish order, but may receive channel B's events in any order relative
    to channel A's.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create an empty event bus with no subscribers yet.

        Args:
            trace: The trace emitter for logging subscriber failures. The
                bus never silently swallows errors (per P10) — if a
                subscriber raises, the bus logs at ERROR and continues.
        """
        self._trace = trace
        self._subscribers: Dict[Channel, List[Subscriber]] = defaultdict(list)
        self._lock = Lock()

    def subscribe(self, channel: Channel, subscriber: Subscriber) -> None:
        """Register a subscriber to receive events sent to a specific channel.

        Multiple subscribers may register for the same channel; each
        receives every event published to that channel. Subscribers are
        called in registration order for each event.

        Args:
            channel: The typed channel identifier to listen on.
            subscriber: A callable that accepts an Event. It will be
                called synchronously on the publishing thread.
        """
        with self._lock:
            self._subscribers[channel].append(subscriber)
        self._trace.emit(
            component="EventBus",
            level=TraceLevel.DEBUG,
            message=f"Subscriber registered for channel {channel}",
        )

    def publish(self, event: Event) -> None:
        """Send an event to all subscribers registered on its channel.

        Subscribers are called synchronously in registration order. If a
        subscriber raises an exception, the bus catches it, logs at ERROR
        with full context, and continues to the next subscriber. The bus
        never silently swallows failures (per P10, criterion 28).

        Args:
            event: The event to publish. Must already carry its channel,
                correlation ID, and timestamp.
        """
        with self._lock:
            subscribers = list(self._subscribers.get(event.channel, []))
        for subscriber in subscribers:
            try:
                subscriber(event)
            except Exception as exc:
                self._trace.emit(
                    component="EventBus",
                    level=TraceLevel.ERROR,
                    message=(
                        f"Subscriber {subscriber!r} raised {type(exc).__name__} "
                        f"on channel {event.channel}: {exc}"
                    ),
                )
```

**Verify:**
- In-order delivery per channel (subscribers called in registration order)
- No silent failures (subscriber exceptions caught + logged at ERROR)
- TraceEmitter received via constructor (AR4, AR6)
- No global mutable state (`_subscribers` is instance state, not module-level)
- Every `def` has a docstring (AR21)
- ≤15 constructor args (1 arg — well under cap)

After creating, run `/verify`.

### S2.2 — Create `tests/test_event_bus.py`

Per Q9 resolution (conformance + contract + property-based). Establish the test strategy here. Required tests:

1. **`test_subscribe_and_publish_delivers_event`** — single subscriber receives the event
2. **`test_multiple_subscribers_receive_in_registration_order`** — verifies A9 in-order delivery
3. **`test_subscriber_exception_does_not_silently_swallow`** — verifies P10 criterion 28 (subscriber raises → bus logs at ERROR → next subscriber still receives)
4. **`test_unrelated_channels_are_isolated`** — subscriber on channel A does not receive channel B's events
5. **`test_publish_to_empty_channel_is_noop`** — no subscribers, no error
6. **`test_trace_emitter_called_on_subscriber_failure`** — verifies the bus emits a TraceEvent at ERROR level when a subscriber raises

Test fixtures use `pytest` with `@pytest.fixture` for the EventBus and a mock TraceEmitter (use `unittest.mock.MagicMock` or a simple in-memory recorder).

After creating, run:
```bash
.venv/Scripts/python.exe -m pytest tests/test_event_bus.py -vvv
```

All 6 tests must pass. If any fail, STOP.

After tests pass, run `/verify`.

---

## S3 — TraceEmitter (Singleton)

### S3.1 — Create `sovereignai/shared/trace_emitter.py`

Per AR6: TraceEmitter is a single-responsibility typed object, NOT a context bag. It carries structured trace and observability data only.

Per P9: every component emits traces via the constructor-injected TraceEmitter. The Log drawer renders these events.

Per AR4: TraceEmitter is a DI-managed singleton.

Per criterion 25: every component emits traces via the constructor-injected TraceEmitter.

```python
"""Trace emitter — the single observability surface for all components.

Every component receives a TraceEmitter via constructor injection (per
AR4, AR6). Components emit structured trace events; the emitter records
them. The emitter is a singleton (per AR4) — one instance per process,
shared across all components.

The emitter is NOT a context bag (per AR6). It carries trace data only
— never business logic, configuration, or cross-component state.
"""
from __future__ import annotations

from threading import Lock
from typing import List

from sovereignai.shared.types import TraceEvent, TraceLevel


class TraceEmitter:
    """Record trace events from all components in a single in-memory log.

    The emitter is the sole observability surface (per P9). Components
    call emit() to record events; the Log drawer (in a UI process, built
    later) reads from this log via the Capability API (Plan 4).

    This is a singleton per AR4 — one instance per process, registered
    in the DI container. Components receive it via constructor injection.

    Thread-safe: multiple components may emit concurrently.
    """

    def __init__(self, max_events: int = 10000) -> None:
        """Create an empty trace emitter with a bounded in-memory log.

        Args:
            max_events: Maximum number of events to retain. When the log
                exceeds this, oldest events are dropped first. Keeps
                memory bounded over long-running sessions.
        """
        self._events: List[TraceEvent] = []
        self._lock = Lock()
        self._max_events = max_events

    def emit(self, component: str, level: TraceLevel, message: str,
             correlation_id: UUID | None = None) -> None:
        """Record a single trace event from a named component.

        Args:
            component: Name of the emitting component (e.g. "EventBus").
            level: Severity of the event.
            message: Plain-English description of what happened.
            correlation_id: Optional UUID grouping events from the same
                task. If None, the event is uncorrelated.
        """
        # Import here to avoid circular import at module load
        from sovereignai.shared.types import now_utc, new_correlation_id
        event = TraceEvent(
            component=component,
            level=level,
            message=message,
            timestamp=now_utc(),
            correlation_id=correlation_id or new_correlation_id(),
        )
        with self._lock:
            self._events.append(event)
            if len(self._events) > self._max_events:
                self._events.pop(0)

    def get_events(self, level: TraceLevel | None = None,
                   component: str | None = None) -> List[TraceEvent]:
        """Return a filtered list of recorded trace events.

        Args:
            level: If provided, return only events at this level or above.
            component: If provided, return only events from this component.

        Returns:
            List of matching events, oldest first.
        """
        with self._lock:
            events = list(self._events)
        if level is not None:
            # Ordered comparison via enum index
            min_idx = list(TraceLevel).index(level)
            events = [e for e in events
                      if list(TraceLevel).index(e.level) >= min_idx]
        if component is not None:
            events = [e for e in events if e.component == component]
        return events
```

**Verify:**
- Singleton (one instance per process — enforced by DI registration in S4)
- NOT a context bag — only carries trace data
- Thread-safe (Lock around `_events`)
- Bounded memory (`max_events` drops oldest)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S3.2 — Create `tests/test_trace_emitter.py`

Required tests:

1. **`test_emit_records_event`** — emit one event, get_events returns it
2. **`test_emit_with_level_filter`** — emit events at different levels, filter returns only matching level and above
3. **`test_emit_with_component_filter`** — emit events from different components, filter returns only matching component
4. **`test_max_events_drops_oldest`** — emit more than max_events, verify oldest is dropped
5. **`test_thread_safety`** — emit from multiple threads concurrently, no corruption
6. **`test_correlation_id_default_generated`** — emit without correlation_id, event has a non-None UUID

After tests pass, run `/verify`.

---

## S4 — DI Container (Passive Typed Registry)

### S4.1 — Create `sovereignai/shared/container.py`

Per AR4: `shared/container.py` is the DI container — the single wiring point. Per A8: passive typed registry, no `@inject` decorators, no auto-wiring magic. `main.py` does all explicit instantiation.

Per AR4: Orchestrator and Librarian (Layer 1) are DI-managed singletons. Managers and Workers are factories. (Plan 1 doesn't have these yet — Plan 2+ adds them. The container just needs to support both patterns.)

```python
"""Passive typed dependency injection container.

This module defines the container itself — a typed registry that holds
component instances and factories. The container does NOT auto-wire or
resolve dependencies. main.py (the Composition Root) explicitly
instantiates every component and registers it here.

Per A8: no @inject decorators, no auto-discovery, no runtime magic. The
container is a passive registry — put things in, take things out, by
type.

Per AR4: singletons (Orchestrator, Librarian Registry) are registered
as instances. Factories (Managers, Workers) are registered as callables
that produce a new instance per call.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Type, TypeVar
from threading import Lock

T = TypeVar("T")


class DIContainer:
    """Typed registry for component instances and factories.

    The container is passive — it does not resolve dependencies or
    construct objects. Callers register instances or factories by type;
    callers retrieve them by type. The container enforces type safety
    at retrieval: requesting a type that wasn't registered raises.

    Thread-safe: registration and retrieval may happen concurrently
    from different components.
    """

    def __init__(self) -> None:
        """Create an empty container with no registered components."""
        self._instances: Dict[Type[Any], Any] = {}
        self._factories: Dict[Type[Any], Callable[[], Any]] = {}
        self._lock = Lock()

    def register_singleton(self, interface: Type[T], instance: T) -> None:
        """Register a single instance that all callers will share.

        Use for long-lived components like the EventBus or TraceEmitter.
        Retrieving the same interface always returns the same instance.

        Args:
            interface: The type key callers will use to retrieve.
            instance: The singleton instance to store.
        """
        with self._lock:
            self._instances[interface] = instance

    def register_factory(self, interface: Type[T],
                         factory: Callable[[], T]) -> None:
        """Register a factory that produces a fresh instance per call.

        Use for short-lived components like per-task Workers. Each
        retrieve() call invokes the factory and returns a new instance.

        Args:
            interface: The type key callers will use to retrieve.
            factory: A callable that takes no args and returns a new
                instance of the interface type.
        """
        with self._lock:
            self._factories[interface] = factory

    def retrieve(self, interface: Type[T]) -> T:
        """Get a registered instance or invoke the registered factory.

        Singletons take precedence: if both a singleton and a factory
        are registered for the same type, the singleton is returned.

        Args:
            interface: The type key previously registered.

        Returns:
            The singleton instance, or a fresh factory-produced instance.

        Raises:
            KeyError: If no singleton or factory is registered for the
                given interface.
        """
        with self._lock:
            if interface in self._instances:
                return self._instances[interface]
            if interface in self._factories:
                return self._factories[interface]()
        raise KeyError(
            f"No singleton or factory registered for {interface!r}"
        )
```

**Verify:**
- Passive (no auto-wiring, no `@inject`)
- Typed (`Type[T]` keys, `T` returns)
- Supports both singletons and factories
- Thread-safe (single-threaded for now; Lock added in Plan 2 when concurrent access starts)
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S4.2 — Create `tests/test_di_container.py`

Required tests:

1. **`test_register_and_retrieve_singleton`** — register instance, retrieve returns same instance
2. **`test_register_and_retrieve_factory`** — register factory, retrieve returns fresh instance each call
3. **`test_singleton_takes_precedence_over_factory`** — both registered, singleton returned
4. **`test_retrieve_unregistered_raises_keyerror`** — KeyError on missing type
5. **`test_different_types_are_isolated`** — register type A, retrieve type B raises

7. **`test_di_container_thread_safety`** — Rev2 addition per Finding 3. Register and retrieve concurrently from multiple threads; verify no lost registrations or races.

After tests pass, run `/verify`.

### S5.1 — Create `sovereignai/main.py`

Per A3: Composition Root is incremental. This plan wires only Plan 1 components. Plans 2–4 extend `main.py` to add their components. Plan 4 performs the final wiring audit and Q26 is confirmed at Plan 4 `/close`.

Per AR5: `main.py` is exempt from the 15-arg constructor cap (it wires all components explicitly).

Per AR4: `main.py` is the only place that instantiates core components. Every other file receives dependencies via constructor.

```python
"""Composition root — wires all Plan 1 core components explicitly.

Per A3: this file is incremental. Plan 1 wires only the Event Bus,
TraceEmitter, DI container, and shared types. Plans 2, 3, and 4 will
extend this file to add their components. Plan 4 performs the final
wiring audit.

Per AR4: this is the ONLY file that instantiates core components.
Every other file receives dependencies via constructor injection.

Per AR5: this file is exempt from the 15-argument constructor cap —
it wires all components explicitly in topological order.
"""
from __future__ import annotations

from sovereignai.shared.container import DIContainer
from sovereignai.shared.event_bus import EventBus
from sovereignai.shared.trace_emitter import TraceEmitter


def build_container() -> DIContainer:
    """Create and populate the dependency injection container.

    Wires components in topological order: TraceEmitter first (no deps),
    then EventBus (depends on TraceEmitter). Registers both as singletons
    in the container. Returns the populated container.

    Plans 2-4 will extend this function to add their components after
    the EventBus registration.
    """
    container = DIContainer()

    # 1. TraceEmitter — no dependencies, singleton
    trace = TraceEmitter()
    container.register_singleton(TraceEmitter, trace)

    # 2. EventBus — depends on TraceEmitter, singleton
    bus = EventBus(trace=trace)
    container.register_singleton(EventBus, bus)

    return container


if __name__ == "__main__":
    """Run the composition root standalone for smoke testing.

    Builds the container, retrieves the EventBus and TraceEmitter, emits
    a startup trace event, and prints it. This verifies the wiring is
    functional before Plan 2 builds on top.
    """
    from sovereignai.shared.types import TraceLevel
    container = build_container()
    trace = container.retrieve(TraceEmitter)
    bus = container.retrieve(EventBus)

    trace.emit(
        component="main",
        level=TraceLevel.INFO,
        message="Composition root built successfully — Plan 1 components wired",
    )
    for event in trace.get_events():
        print(f"[{event.level.value}] {event.component}: {event.message}")
```

**Verify:**
- Topological order: TraceEmitter before EventBus
- Both registered as singletons
- `build_container()` is the canonical entry point (Plans 2–4 extend it)
- `__main__` block provides smoke test
- Every `def` has a docstring (AR21)

After creating, run `/verify`.

### S5.2 — Create `tests/test_composition_root.py`

Required tests:

1. **`test_build_container_returns_populated_container`** — `build_container()` returns a DIContainer with TraceEmitter and EventBus registered
2. **`test_trace_emitter_is_singleton`** — retrieve TraceEmitter twice, same instance
3. **`test_event_bus_is_singleton`** — retrieve EventBus twice, same instance
4. **`test_event_bus_has_trace_emitter_wired`** — emit via EventBus's subscriber failure path, verify TraceEmitter records the ERROR
5. **`test_main_smoke_test`** — invoke `python -m sovereignai.main`, verify exit code 0 and output contains "Composition root built successfully"

After tests pass, run `/verify`.

---

## S6 — Establish Test Baseline in PLANS.md

This plan establishes the first real test baseline. Update `PLANS.md`:

### S6.1 — Update Test Baseline section

Set the baseline test count. Expected: 6 (event bus) + 6 (trace emitter) + 5 (DI container) + 5 (composition root) = **22 tests**.

Old text:
```
**Current baseline**: Not yet established — set at Plan 1 `/close` (S_close step: full pytest run)
```

New text:
```
**Current baseline**: 22 tests (Plan 1 `/close`). Breakdown: 6 event_bus + 6 trace_emitter + 5 di_container + 5 composition_root.
```

### S6.2 — Update Static Analysis Baseline section

Set the baselines for tools that now have Python code to check:

Old text:
```
| **Ruff** | TBD | Plan 1 `/close` | 0 errors expected on fresh scaffold |
| **Mypy (file-scoped)** | TBD | Plan 1 `/close` | File-scoped per OR2 — not full repo |
| **Bandit** | TBD | Plan 1 `/close` | Count per OR4 (filter: `>> Issue: [B`) |
| **pip-audit** | TBD | Plan 1 `/close` | CVE count across all packages |
| **Vulture** | TBD | Plan 1 `/close` | High-confidence findings only |
| **detect-secrets** | TBD | Plan 1 `/close` | Baseline established with `.secrets.baseline` |
| **pre-commit** | TBD | Plan 1 | Hooks configured at scaffold |
```

New text:
```
| **Ruff** | 0 errors | Plan 1 `/close` | Fresh scaffold — D100/D104 excluded per pyproject.toml |
| **Mypy (file-scoped)** | 0 errors | Plan 1 `/close` | File-scoped per OR2 — Plan 1 files: shared/types.py, event_bus.py, trace_emitter.py, container.py, main.py + tests |
| **Bandit** | 0 findings | Plan 1 `/close` | Per OR4 (filter: `>> Issue: [B`) |
| **pip-audit** | 0 CVEs | Plan 1 `/close` | Scanned txt/requirements.txt only per OR39 — first runtime dep: dependency-injector>=1.2 |
| **Vulture** | 0 findings | Plan 1 `/close` | High-confidence (≥80) only |
| **detect-secrets** | pass | Plan 1 `/close` | Baseline established prompt-0; unchanged |
| **pre-commit** | pass | Plan 1 | Hooks configured at prompt-0 scaffold |
```

After edits, run `/verify`.

---

## S7 — Update CHANGELOG.md

Use the Edit tool to append to END of `CHANGELOG.md`:

```markdown
## prompt-1 — Core scaffold (Event Bus, TraceEmitter, DI container, types, Composition Root)

**Date**: {YYYY-MM-DD}
**Plan file**: prompts/plan-1-Rev1.md

**Files changed**:
- `txt/requirements.txt` (NO change in Rev2 — dependency-injector removed per Finding 5; remains empty)
- `sovereignai/shared/__init__.py` (new — marks shared/ as package)
- `sovereignai/shared/types.py` (new — frozen dataclasses: TraceLevel, TraceEvent, Channel, Event, ComponentId, helpers)
- `sovereignai/shared/event_bus.py` (new — in-order per channel, no silent failures per P10; imports TraceEmitter from trace_emitter.py per Finding 1)
- `sovereignai/shared/trace_emitter.py` (new — singleton observability surface, NOT a context bag per AR6; correlation_id typed per Finding 4)
- `sovereignai/shared/container.py` (new — passive typed DI registry, no auto-wiring per A8; thread-safe via Lock per Finding 3)
- `sovereignai/main.py` (new — incremental Composition Root, wires Plan 1 components only per A3; smoke test uses TraceLevel.INFO per Finding 2)
- `tests/test_event_bus.py` (new — 6 tests: ordering, fault isolation, channel isolation)
- `tests/test_trace_emitter.py` (new — 6 tests: emit, filter, bounded, thread-safe)
- `tests/test_di_container.py` (new — 5 tests: singleton, factory, precedence, missing; +1 thread-safety test per Finding 3 = 6 tests)
- `tests/test_composition_root.py` (new — 5 tests: populated, singleton retrieval, wiring, smoke)
- `DEBT.md` (add AR4 amendment deferral per Finding 5)
- `PLANS.md` (set test + static analysis baselines)

**Results**:
- Tests: 23 passed (Rev2: +1 thread-safety test for DIContainer per Finding 3)
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped to Plan 1 files per OR2/OR47)
- Bandit: 0 findings
- pip-audit: 0 CVEs (txt/requirements.txt remains empty — no runtime deps per Finding 5)
- Vulture: 0 findings
- Detect-secrets: pass

**Notes**:
- First code plan. Establishes test + static analysis baselines for all future plans.
- Q9 (test strategy) resolved: conformance + contract + property-based (property-based deferred until Plan 2+ when invariants are richer).
- Q32 (DEBT.md scaffold) resolved: already done in prompt-0.
- Event bus guarantees in-order delivery per typed channel (A9) — verified by test_multiple_subscribers_receive_in_registration_order.
- No silent failures (P10 criterion 28) — verified by test_subscriber_exception_does_not_silently_swallow.
- DI container is passive (A8) — no @inject, no auto-wiring. main.py does all explicit instantiation. Thread-safe via Lock (Rev2 Finding 3).
- Composition Root is incremental (A3) — wires Plan 1 components only. Plans 2-4 extend it. Q26 confirmed at Plan 4 /close.
- Rev2: dependency-injector NOT added to txt/requirements.txt (Finding 5 — hand-rolled container is correct per A8; AR4 amendment deferred to DEBT).
- Rev2: EventBus imports TraceEmitter from trace_emitter.py, not types.py (Finding 1).
- Rev2: main.py smoke test uses TraceLevel.INFO, not string (Finding 2).
```

After edit, run `/verify`.

---

## S8 — Commit and Tag Prompt-1

**STOP condition**: If any `/verify` step failed, STOP and report before committing.

1. Stage all changes:
   ```bash
   git add -A
   git status -s | tail -n 30
   ```
   Verify staged files match S1-S7. If anything unexpected (e.g., `.venv/`), STOP.

2. Commit (multiple `-m` per OR42):
   ```bash
   git commit -m "prompt-1: Core scaffold — Event Bus, TraceEmitter, DI container, types, Composition Root" -m "shared/types.py: frozen dataclasses (TraceLevel, TraceEvent, Channel, Event, ComponentId) — canonical types for all downstream plans per A2." -m "shared/event_bus.py: in-order delivery per typed channel (A9); no silent failures (P10) — subscriber exceptions caught and logged at ERROR." -m "shared/trace_emitter.py: singleton observability surface; NOT a context bag (AR6) — carries trace data only." -m "shared/container.py: passive typed DI registry (A8) — no @inject, no auto-wiring. main.py does all explicit instantiation." -m "main.py: incremental Composition Root (A3) — wires Plan 1 components only. Plans 2-4 extend it." -m "txt/requirements.txt: first runtime dep — dependency-injector>=1.2 per OR39." -m "Tests: 22 passed (6 event_bus + 6 trace_emitter + 5 di_container + 5 composition_root). Q9 test strategy established."
   ```

3. Tag:
   ```bash
   git tag prompt-1
   git tag --list prompt-1
   ```

4. Push:
   ```bash
   git push origin main
   git push origin prompt-1
   ```

5. Verify tag on origin:
   ```bash
   git ls-remote --tags origin | grep "prompt-1"
   ```

---

## Closing

Run `/close` workflow from `.devin/workflows/close.md`. Run all 21 steps. The new step 3 (mypy) will filter to `.py` files per OR47 — this plan has many `.py` files, so mypy will actually run.

**Expected results**:
- Tests: 22 passed
- Ruff: 0 errors
- Mypy: 0 errors (file-scoped to Plan 1 `.py` files)
- Bandit: 0 findings
- pip-audit: 0 CVEs (dependency-injector>=1.2 clean)
- Vulture: 0 findings
- Detect-secrets: pass
- Custom AR checks: pass (no globals in sovereignai/, ≤15 args, no context bags, docstrings verb-first ≥10 words)

**Key verifications**:
- Event bus ordering test passes (A9)
- Subscriber exception test passes (P10 criterion 28)
- DI container is passive (A8) — no @inject decorators anywhere
- TraceEmitter is not a context bag (AR6) — only carries trace data
- Composition Root wires in topological order (A3)
- `dependency-injector` in `txt/requirements.txt` (OR39), pip-audit clean

After `/close` completes, create `logs/execution-log-prompt-1.md`. User pastes execution log, then asks Executor to commit and push it.

**Reminder**: Step 21 (kill bash) is mandatory. Plan is NOT complete until it runs.

---

## Files WILL Create

- `sovereignai/shared/__init__.py`
- `sovereignai/shared/types.py`
- `sovereignai/shared/event_bus.py`
- `sovereignai/shared/trace_emitter.py`
- `sovereignai/shared/container.py`
- `sovereignai/main.py`
- `sovereignai/__init__.py` (marks sovereignai/ as package)
- `tests/__init__.py` (marks tests/ as package — needed for pytest collection)
- `tests/test_event_bus.py`
- `tests/test_trace_emitter.py`
- `tests/test_di_container.py`
- `tests/test_composition_root.py`
- `logs/execution-log-prompt-1.md` (created by `/close` step 14)

## Files WILL Edit

- `txt/requirements.txt` (append `dependency-injector>=1.2` per OR39)
- `PLANS.md` (set test + static analysis baselines at S6; add prompt-1 row at `/close` step 10)
- `CHANGELOG.md` (append prompt-1 entry at S7)

## Files WILL NOT Edit

- `AGENTS.md` (no new rules this plan)
- `AI_HANDOFF.md` (no changes)
- `.devin/workflows/*.md` (no changes — workflow files are stable from prompt-0.4)
- `documents/*` (archived — do not touch)
- `prompts/*` (no changes to existing plan files)
- `pyproject.toml`, `.pre-commit-config.yaml`, `.gitignore`, `README.md` (stable)
- `txt/vulture-whitelist.txt`, `txt/.secrets.baseline` (stable)
- All `.gitkeep` files (stable)
- `DECISIONS.md`, `DEBT.md`, `LANDMINES.md` (no new decisions, deferrals, or landmines this plan — unless execution surfaces new patterns)

---

*Plan 1 — Core Scaffold. Rev1. Architect draft. Part of Plans 1-4 batch — Round Table reviews this file alongside plan-2-Rev1.md, plan-3-Rev1.md, plan-4-Rev1.md, and plan-1-4-batch-Rev1-context-brief.md.*
