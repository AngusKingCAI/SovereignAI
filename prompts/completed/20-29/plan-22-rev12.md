Depends on: prompt-20.9.9
Vision principles: P7 (modular and flexible), P9 (observability), P13 (strong and robust)
Open questions resolved: Q-22.1 (critical event timeout), Q-22.2 (queue.dropped feedback loop), Q-22.3 (lifespan ordering), Q-22.4 (_publish_internal definition), Q-22.5 (four-state EventBus), Q-22.6 (pre-start buffer overflow)

S0.5 research: Per-handler FIFO queues with circuit breakers prevent cascade failures. Async delivery prevents publisher blocking. Forward-compatible schemas (optional fields with defaults) avoid migration complexity. FastAPI SSE requires StreamingResponse with text/event-stream media type. SSE retry uses field in stream body (retry: 3000), not HTTP Retry header.

## S0 — Opening

S0.0 — Not resuming (first plan in queue). Skip resume check.
S0.1 — Run /open. Verify `prompt-20.9.9` tag exists on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: DEBT-1 (diskcache CVE) and DEBT-3 (first-run UI) — neither affects this plan.
S0.5 — Research findings documented in plan header above.

## Plan Body

### S1 — Extend EventBus in app/sovereignai/shared/event_bus.py
- Breaking change: EventBus constructor signature changes from `(trace)` to `(trace, registry)`. Update `app/sovereignai/main.py` line 37: create registry before bus, pass as `bus = EventBus(trace=trace, registry=registry)`.
- Add `version: int = 1`, `trace_level: TraceLevel = TraceLevel.INFO` to Event dataclass as stored fields.
- Keep `channel` as stored field. Add `event_type` as read-only property alias backed by `channel` (getter returns `Channel(self.channel)`). Frozen dataclass — mutations construct new Event.
- Keep existing sync `publish()` working — add `publish_async()` for new async path.
- No breaking change to `Event(channel=...)` constructors.
- EventBus initialized with injected EventRegistry; dispatches each event to `registry.handlers_for(event.event_type)`.

### S2 — Create EventRegistry in app/sovereignai/shared/event_registry.py
- `register(event_type, payload_class, handler, queue_maxsize: int = 1000)`.
- For wildcard `event_type='*'`, `payload_class` may be None; signature validation skipped. `handlers_for('*')` returns all wildcard subscribers for every event type.
- Signature validation via `get_type_hints` at registration time — fail fast on mismatch (skipped for wildcard).
- `handlers_for(event_type)` returns list of matching handlers (including wildcard "*").

### S2.1 — Create event payload classes in app/sovereignai/shared/events.py
- Define payload dataclasses: `TaskCreated`, `TaskUpdated`, `AgentStep`, `HardwareStatus`, etc.
- Forward-compatible: optional fields with defaults. Bump minor version.
- Major break = new class (`TaskCreated_v2`). Old class frozen for read — retained only for deserialization of historical payloads.

### S3 — Wire event registrations in app/sovereignai/main.py
- One line per event type: `registry.register("task.created", TaskCreated, task_handler)`.
- Lifespan order in `app/web/main.py` (lines 44-53): wrap FULL lifecycle in try/finally:
  ```python
  container = build_container()
  event_bus = container.retrieve(EventBus)
  registry = container.retrieve(EventRegistry)
  registry.register("task.created", TaskCreated, task_handler)
  await event_bus.start()
  await container.start()
  try:
      yield
  finally:
      await event_bus.stop()
      await container.stop()
  ```
- Handlers registered before `event_bus.start()` so drain tasks created for all handlers.
- Create `.agent/executor/scripts/ar_checks/check_event_registration.py`. Test: `.agent/executor/tests/sovereignai/test_check_event_registration.py`. Wire into pre-commit config.

### S3.1 — Create .agent/executor/scripts/ar_checks/check_event_frozen.py
- Test: `.agent/executor/tests/sovereignai/test_check_event_frozen.py`. Wire into pre-commit config.

### S4 — Add async delivery with per-handler FIFO in app/sovereignai/shared/event_bus.py
- EventBus uses FOUR-STATE state machine: `_state: Literal['INIT', 'RUNNING', 'STOPPING', 'STOPPED'] = 'INIT'`.
- `@property def is_started(self) -> bool: return self._state == 'RUNNING'`.
- `EventBus.start()`: guard against concurrent calls (if `self._state != 'INIT'`: raise `RuntimeError`); set `_state = 'RUNNING'`; capture `self._loop` via `asyncio.get_running_loop()`, `self._loop_thread = threading.current_thread()`; create drain tasks for all handlers in registry; drain `pre_start_buffer` and `pre_start_critical_buffer` via `publish_async()`.
- `EventBus.stop()`: if `_state != 'RUNNING'`: return (idempotent); set `_state = 'STOPPING'`; cancel drain tasks and await with `return_exceptions=True`; set `_state = 'STOPPED'`.
- `publish()`/`publish_async()` before start: buffer in `pre_start_buffer` (non-critical) or `pre_start_critical_buffer` (critical). No `RuntimeError`. Drained on start().
- `publish()`/`publish_async()` while STOPPING: raise `RuntimeError('EventBus is stopping; not accepting new events.')`.
- `publish()`/`publish_async()` after stop: raise `RuntimeError('EventBus is stopped.')`.
- Sync `publish()` order: FIRST check `_state`, THEN detect current thread/loop. State check precedes loop detection (avoids `AttributeError` on `self._loop` being None).
- Each handler gets `asyncio.Queue(maxsize=queue_maxsize)`. Dedicated drain task per handler. Drain task wraps handler call in try/except; on unhandled exception, log error, emit `trace.handler_crash` via `__publish_internal()`, continue draining.
- Per-handler circuit breaker: >50 errors/10s = unsubscribe (DD-22.1: AR7 circuit-breaker pattern extended to handlers). Key is `(handler_id, event_type)` tuple.
- On `QueueFull`: drop newest, increment error counter, record drop. Emit at most one `queue.dropped` report per handler per second, with count of dropped events in payload.
- CRITICAL EVENT ROUTING: Events with `trace_level=CRITICAL` or `event_type` ending in `.error` or `.completed` routed to RESERVED BOUNDED QUEUE per handler (maxsize=100). Same drain task, higher priority. Circuit breaker applies.
- On critical queue overflow: write to `critical_overflow.sqlite` via SEPARATE SQLite connection (timeout=5.0) using `asyncio.to_thread()`. Emit `trace.critical_overflow` via `__publish_internal()` with `trace_level=TraceLevel.ERROR` (NOT CRITICAL — avoids feedback loop, DD-22.11.1). If SQLite write fails, log at ERROR level and continue.
- Document: critical queue overflow = best-effort with SQLite fallback, not guaranteed delivery (DD-22.11.3).
- Pre-start critical events: `pre_start_critical_buffer` (separate, maxsize=10000). No bypass, but protected from eviction by non-critical events (DD-22.11.2).
- Pre-start non-critical buffer overflow: drop-oldest via custom wrapper tracking `dropped_count` (DD-22.11.7). Log warning with count. Reset counter after logging.
- Pre-start critical buffer overflow: drop oldest critical events, log warning with separate counter. Last-resort degradation.
- `__publish_internal(event)`: private (name-mangled) method. Skips pre-start/post-stop guards, skips circuit breaker. Directly enqueues to handler queues. Checks `asyncio.get_running_loop() is self._loop` (raises `RuntimeError` if wrong thread) and `self._state == 'RUNNING'` (raises if not). Used ONLY by drain tasks for trace emissions and critical overflow reporting.
- Drain tasks must NEVER call `publish()` synchronously from within their callback. Use `__publish_internal()`.
- Critical overflow emission MUST use `__publish_internal()` with `trace_level=ERROR` (DD-22.11.9).

### S5 — Subscribe Librarian to all events
- Librarian consumes events for episodic memory (DD-20.10.8 — verify Librarian has `handle_event` method; if not, defer S5 to future plan and add DEBT.md entry).
- Async drain, non-blocking. `queue_maxsize=10000` (bounded). Librarian events never dropped via normal drop-newest, but `QueueFull` can still occur.
- Overflow policy: on `QueueFull`, write event to `librarian_overflow.sqlite` and ack. Background replay task drains SQLite table back into queue when queue size drops below 1000.
- Replay task lifecycle (DD-22.11.10): child of Librarian drain task; cancelled when drain task cancelled in `stop()`.
- Librarian circuit breaker: >500 errors/60s = log warning only, no auto-unsubscribe (DD-22.1: Librarian is system-critical consumer). Evaluated as single aggregate counter across all event types (`handler_id` only).
- One subscription: `registry.register("*", None, librarian.handle_event, queue_maxsize=10000)`.

### S6 — Add event versioning in app/sovereignai/shared/types.py
- On major version bump, EventRegistry maintains `_deprecated_events` map. Consumers subscribed to old event type receive `trace.deprecated_event_type` AND `warnings.warn(..., DeprecationWarning)`. Also startup-time log: "WARNING: Event type 'TaskCreated' is deprecated. Update subscriptions to 'TaskCreated_v2'." Log once per deprecated event type at app boot.
- `warnings.warn` fires once at first publish of deprecated event. Both deduplicated per event type.
- `check_event_frozen.py` enforces frozen classes.

### S7 — Create web endpoints in app/web/main.py
- `/api/events/types` GET: list registered event types. Returns `EventTypeListDTO`.
- `/api/events/subscriptions` GET: list active subscriptions. Returns `SubscriptionListDTO`.
- DTOs in `app/web/schemas.py`: `EventTypeListDTO`, `SubscriptionListDTO`.

### S8 — Harden /api/hardware/stream SSE in app/web/main.py
- WILL edit: `app/web/main.py` — verify `StreamingResponse` with `text/event-stream`.
- Add `asyncio.CancelledError` handling for client disconnect.
- Send `retry: 3000` as SSE field in stream body, not HTTP header.
- Enforce session cookie auth on `/api/hardware/stream`; reject unauthenticated with 403.
- Verify SSE stream emits `retry` field in every event.

### S9 — Create tests in .agent/executor/tests/sovereignai/
- `test_typed_event_bus.py`: routing by event_type, version handling, backward-compat, channel alias synced with event_type, constructor backward compat.
- `test_event_registry.py`: signature validation, fail-fast, wildcard dispatch, `test_register_wildcard_none_payload`.
- `test_async_delivery.py`: FIFO order, circuit breaker trigger, sync publish same-thread (`create_task`), sync publish cross-thread (`run_coroutine_threadsafe`), `queue_full_drops_newest`, `test_critical_event_routing`, `test_librarian_never_drops_events`, `test_drain_task_crash_recovery`, `test_publish_before_start_buffers`, `test_publish_after_stop_raises`, `test_queue_dropped_aggregated`, `test_critical_queue_overflow_sqlite`, `test_event_bus_four_state`, `test_is_started_property`, `test_stopping_publish_raises`, `test_publish_state_check_before_loop`, `test_pre_start_critical_buffer`, `test_critical_overflow_emits_error_level`.
- `test_event_persistence.py`: Librarian integration, episodic storage, Librarian survives transient SQLite lock errors, events registered after "*" subscription still persisted.
- `test_hardware_stream_requires_cookie.py`: SSE auth.
- `test_events_api.py`: list types endpoint, list subscriptions endpoint.

### S10 — Landmine compliance
- M1: All imports use `sovereignai.*` package path. Verified by `check_import_paths.py`.
- M2: Update `WEB_MAIN_ALLOWED_IMPORTS` in `.agent/executor/tests/sovereignai/test_ar7_no_core_imports_in_ui.py` for new imports in `app/web/main.py`.
- M3: Update `ALLOWLIST` in `.agent/executor/scripts/ar_checks/spec_match.py` for new paths: `app/sovereignai/shared/event_registry.py`, `app/sovereignai/shared/events.py`.
- M4: All test files in `.agent/executor/tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-22.1, DD-22.11.1 through DD-22.11.11 to `.agent/shared/DECISIONS.md` as Proposed status.
