# SovereignAI -- Cross-Department Messaging Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect (Round Table bypass per User preference)  
**Depends on**: `principles.md`, `AGENTS.md`, `DECISIONS.md`, `AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`

---

## 1. Context

The existing EventBus (48 lines) already implements:
- Typed frozen dataclass `Event` (channel, correlation_id, timestamp)
- Fan-out delivery with per-subscriber try/except
- AR22 trace emission on subscribe and publish
- AR23 correlation_id propagation

What it lacks:
- event_type routing (uses `Channel` NewType string)
- versioned payload schemas
- per-handler circuit breaker
- async delivery
- episodic persistence
- mechanical enforcement of registration/frozen classes

This document specifies the delta from existing code to full cross-department messaging.

---

## 2. Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 20.10.4 | **Event schema** -- 8-field base: event_id, timestamp, source, event_type, version, correlation_id, trace_level, payload | P9/P10/AR22/AR23. Universal tracing. Versioned from day one. |
| 20.10.5 | **Event type registry** -- Pydantic classes with ClassVar event_type/version/source, explicit register() in main.py | P1/P5/D2/D4. No manifest overhead for pure types. |
| 20.10.6 | **Consumer registration** -- EventRegistry.subscribe(PayloadClass, handler) with get_type_hints validation | D2/D4/P1. No decorators, no auto-wiring. Mechanical enforcement. |
| 20.10.7 | **Delivery** -- Async fan-out, per-handler FIFO, priority ordering, per-handler breaker | P9/P13/AR22. Error isolation. In-order per handler. |
| 20.10.8 | **Persistence** -- All events to episodic memory via Librarian subscription | P4/P9. Full audit trail. No classification tax. |
| 20.10.9 | **Versioning** -- Forward-compatible (C) default; new class per major version (B) escape hatch | P4/P5/AR6/AR17. Frozen classes enforced by OR28. |
| 20.10.10 | **Integration** -- Extend existing EventBus in place. 5 callsites. No wrapper. | P5. Existing code already does fan-out + traces. Delta only. |
| 20.10.11 | **Plan scope** -- Two plans: 20.10.1 (typed foundation) + 20.10.2 (delivery hardening + persistence) | 120-line limit. Coherent intermediate state. |

---

## 3. Event Schema

```python
# sovereignai/shared/types.py -- AMENDED
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from sovereignai.versioning.semver import Version
from sovereignai.shared.trace_levels import TraceLevel

@dataclass(frozen=True)
class Event:
    event_id: UUID
    timestamp: datetime        # UTC, timezone-aware
    source: str                # component that emitted
    event_type: str           # routing key, replaces Channel
    version: Version
    correlation_id: UUID       # AR23: trace across services
    trace_level: TraceLevel    # per-event granularity
    payload: BaseModel         # typed per event type
```

**Removed:** `Channel = NewType("Channel", str)` -- event_type IS the routing key.

---

## 4. Event Type Registry

```python
# sovereignai/shared/event_registry.py
from typing import Callable, get_type_hints
from pydantic import BaseModel
from sovereignai.versioning.semver import Version

class EventRegistry:
    def __init__(self) -> None:
        self._types: dict[str, type[BaseModel]] = {}
        self._handlers: dict[str, list[tuple[int, Callable]]] = {}
        self._active: dict[str, str] = {}  # event_type -> version

    def register(self, payload_cls: type[BaseModel]) -> None:
        et = payload_cls.event_type
        if et in self._types:
            raise ValueError(f"Duplicate event_type: {et}")
        self._types[et] = payload_cls
        self._active[et] = payload_cls.version

    def subscribe(
        self,
        payload_cls: type[BaseModel],
        handler: Callable[[BaseModel], None],
        priority: int = 1000
    ) -> None:
        # Mechanical signature validation (AR6)
        hints = get_type_hints(handler)
        event_param = next(iter(hints.values()))
        if event_param is not payload_cls:
            raise TypeError(
                f"Handler {handler.__qualname__} expects {event_param}, "
                f"registered for {payload_cls.__name__}"
            )
        self._handlers[payload_cls.event_type].append((priority, handler))

    def get(self, event_type: str) -> type[BaseModel] | None:
        return self._types.get(event_type)

    def all_types(self) -> dict[str, type[BaseModel]]:
        return dict(self._types)
```

**Registration in main.py (D4 explicit wiring):**
```python
# sovereignai/main.py build_container()
event_registry = EventRegistry()
event_registry.register(CodingTaskCreated)
event_registry.register(CodingTaskUpdated)
event_registry.register(ResearchBriefRequested)
# ... one line per event type
event_registry.subscribe(CodingTaskCreated, coding_manager.on_task_created)
# ... one line per consumer
```

---

## 5. Payload Class Pattern

```python
# sovereignai/coding/events.py
from typing import ClassVar
from uuid import UUID
from pydantic import BaseModel
from sovereignai.versioning.semver import Version

class CodingTaskCreated(BaseModel):
    event_type: ClassVar[str] = "coding.task.created"
    version: ClassVar[Version] = Version(1, 0, 0)
    frozen: ClassVar[bool] = False
    source: ClassVar[str] = "sovereignai.coding"

    task_id: UUID
    description: str
    priority: str = "normal"  # forward-compatible default
```

**Major bump (new class, old frozen):**
```python
class CodingTaskCreated(BaseModel):
    event_type: ClassVar[str] = "coding.task.created"
    version: ClassVar[Version] = Version(1, 1, 0)  # minor: add field
    frozen: ClassVar[bool] = False
    # ... same fields + new optional field with default

class CodingTaskCreated_v2(BaseModel):
    event_type: ClassVar[str] = "coding.task.created"
    version: ClassVar[Version] = Version(2, 0, 0)
    frozen: ClassVar[bool] = False
    # ... breaking change: removed field, renamed field, etc.
    # Old class auto-marked frozen=True on promotion
```

---

## 6. Delivery

### 6.1 Async Fan-Out

```python
# EventBus.publish() -- AMENDED
from queue import Queue
from threading import Thread

class EventBus:
    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._handler_queues: dict[str, Queue] = {}  # handler_id -> Queue
        self._worker_pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=8)

    def publish(self, event: Event) -> None:
        # Enqueue to all subscribers, return immediately
        for handler_id, (priority, handler) in self._handlers[event.event_type]:
            if handler_id not in self._handler_queues:
                self._handler_queues[handler_id] = Queue(maxsize=1000)
                self._worker_pool.submit(self._drain, handler_id, handler)
            self._handler_queues[handler_id].put(event)

    def _drain(self, handler_id: str, handler: Callable) -> None:
        while True:
            event = self._handler_queues[handler_id].get()
            if event is DRAIN_SHUTDOWN:
                break
            try:
                handler(event)
            except Exception as exc:
                self._emit_handler_error(event, handler, exc)
                self._check_breaker(handler_id)
```

### 6.2 Per-Handler Circuit Breaker

```python
class EventBus:
    ERROR_THRESHOLD = 50      # errors
    ERROR_WINDOW = 10         # seconds

    def _check_breaker(self, handler_id: str) -> None:
        count = self._error_counts[handler_id].count_in_window(self.ERROR_WINDOW)
        if count > self.ERROR_THRESHOLD:
            self._unsubscribe(handler_id)
            self._trace.emit(
                level=TraceLevel.ERROR,
                component="event_bus",
                event="handler.unloaded",
                handler=handler_id,
                error_count=count,
                window_s=self.ERROR_WINDOW
            )
```

### 6.3 Error Trace Event

```python
# Emitted when handler raises
{
    "event_id": original_event.event_id,           # AR23 correlation
    "correlation_id": original_event.correlation_id,
    "handler_name": handler.__qualname__,
    "error_type": type(exc).__name__,
    "error_message": str(exc)[:200],               # bounded
    # payload intentionally excluded -- P14 hygiene
}
```

---

## 7. Persistence

```python
# Librarian subscription in main.py
librarian = container.resolve(Librarian)
event_registry.subscribe(
    AnyEvent,  # or specific types
    librarian.on_event,
    priority=100  # audit/observability = early
)
```

**Librarian handler:**
```python
class Librarian:
    def on_event(self, event: Event) -> None:
        # All events persist to episodic memory
        self._episodic_backend.write(
            event_id=event.event_id,
            event_type=event.event_type,
            version=str(event.version),
            timestamp=event.timestamp,
            source=event.source,
            correlation_id=event.correlation_id,
            payload_json=event.payload.model_dump_json(),
        )
```

**Payload cap:** 64KB. Truncated events emit `event.persisted.truncated` trace.

---

## 8. Mechanical Enforcement

### 8.1 check_event_registration.py (OR29)

```python
# scripts/ar_checks/check_event_registration.py
# Scans **/events.py for Pydantic classes with event_type: ClassVar[str]
# Parses main.py for event_registry.register(ClassName) calls
# Diff: every event class must have register call; every register must reference existing class
# Exit non-zero on mismatch (STOP)
```

### 8.2 check_event_frozen.py (OR28)

```python
# scripts/ar_checks/check_event_frozen.py
# Scans **/events.py for classes with frozen: ClassVar[bool] = True
# Flags any edit to frozen class (field add, remove, type change, default change)
# Exit non-zero on edit (STOP)
```

---

## 9. AR17 Contract Tests

### 9.1 Round-Trip Test
```python
def test_event_round_trip():
    event = CodingTaskCreated(task_id=uuid4(), description="test")
    json_str = event.model_dump_json()
    restored = CodingTaskCreated.model_validate_json(json_str)
    assert event == restored
```

### 9.2 Replay Test
```python
def test_event_replay():
    fixture = load_fixture("tests/fixtures/events/coding.task.created.v1.json")
    event = CodingTaskCreated.model_validate(fixture)
    assert event.task_id is not None
```

### 9.3 Major-Bump Test
```python
def test_major_bump_isolation():
    v1_fixture = load_fixture("tests/fixtures/events/coding.task.created.v1.json")
    # v1 fixture does NOT deserialize as v2
    with pytest.raises(ValidationError):
        CodingTaskCreated_v2.model_validate(v1_fixture)
```

---

## 10. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Sync publish_sync() | Test-only needs | EventBus.publish_sync() |
| Librarian replay | Historical query | Librarian.replay(event_type, version, time_range) |
| Payload migration | Major version break | Explicit migration function, one-shot |
| Event TTL | Storage pressure | EpisodicBackend.purge(older_than=) |
| Cross-system events | External integration | EventRegistry.register_external(schema_url) |

---

## 11. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-20.10.5 | Can old frozen classes ever be removed from codebase? | Deferred to future Round Table |
| Q-20.10.6 | Should event replay support time-travel (point-in-time query)? | Deferred |
| Q-20.10.7 | Should events support encryption-at-rest for sensitive payloads? | Deferred |

---

## 12. Implementation Plan Queue

| Plan | Scope | Depends On |
|------|-------|------------|
| **20.10.1** | Typed Event Foundation (schema + registry + versioning + checks + OR28/OR29) | None |
| **20.10.2** | Delivery Hardening + Persistence (async + breaker + Librarian + payload cap) | 20.10.1 |
| **20.11** | Trace Queue Hardening (DD-20.10.1/2/3 -- independent) | None |

---

*End of document.*
