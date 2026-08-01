Depends on: prompt-20.9.9
Vision principles: P7 (modular and flexible), P9 (observability), P13 (strong and robust)
Open questions resolved: Q-23.1 (critical event timeout), Q-23.2 (queue.dropped feedback loop), Q-23.3 (lifespan ordering), Q-23.4 (_publish_internal definition), Q-23.5 (three-state EventBus), Q-23.6 (pre-start buffer overflow)

S0.4 best practices: Per-handler FIFO queues with circuit breakers prevent cascade failures. Async delivery prevents publisher blocking. Forward-compatible schemas (optional fields with defaults) avoid migration complexity. FastAPI SSE requires StreamingResponse with text/event-stream media type and proper disconnect handling. SSE retry uses field in stream body (retry: 3000), not HTTP Retry header.

## S0 — Opening

S0.1 — Run /open. Verify prompt-20.9.9 tag exists on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — No new rules for this plan.

## Plan Body

### S1 — Extend EventBus with typed event routing in sovereignai/shared/event_bus.py
- EventBus currently has NO start() or stop() methods — these are net-new additions introduced by this plan.
- Add version: int = 1, trace_level: TraceLevel = TraceLevel.INFO to Event dataclass as stored fields.
- Keep channel as stored dataclass field (primary). Add event_type as read-only property alias backed by channel (getter returns Channel(self.channel)). Do not add event_type as a stored field. Frozen dataclass — mutations must construct new Event.
- Keep existing sync publish() working — add publish_async() for new async path.
- No breaking change to existing Event(channel=...) constructors. EventBus is a single in-process instance owned by the core process (per P6, "same core"); TUI and Web UI are separate processes that communicate via CapabilityAPI/HTTP, not by importing EventBus directly.
- EventBus is initialized with an injected EventRegistry and dispatches each event to registry.handlers_for(event.event_type).

### S2 — Create EventRegistry in sovereignai/shared/event_registry.py
- Explicit registration: register(event_type, payload_class, handler, queue_maxsize: int = 1000).
- For wildcard event_type='*', payload_class may be None; signature validation is skipped. handlers_for('*') returns all wildcard subscribers for every event type.
- Signature validation via get_type_hints at registration time — fail fast on mismatch (skipped for wildcard).
- handlers_for(event_type) returns list of matching handlers (including wildcard "*").

### S2.1 — Create event payload classes in sovereignai/shared/events.py
- Define payload dataclasses: TaskCreated, TaskUpdated, AgentStep, HardwareStatus, etc.
- Forward-compatible: optional fields with defaults. Bump minor version.
- Major break = new class (TaskCreated_v2). Old class frozen for read — no longer instantiated for new events, retained only for deserialization of historical payloads.

### S3 — Wire event registrations in main.py
- One line per event type: registry.register("task.created", TaskCreated, handler).
- Lifespan order in web/main.py (lines 44-53): wrap FULL lifecycle in try/finally. Exact order:
  ```python
  container = build_container()
  event_bus = container.retrieve(EventBus)
  registry = container.retrieve(EventRegistry)
  # Register all handlers BEFORE starting EventBus
  registry.register("task.created", TaskCreated, task_handler)
  # ... other registrations ...
  await event_bus.start()  # Drain tasks created from current registry snapshot
  await container.start()  # Components may now publish; events are routable
  try:
      yield
  finally:
      await event_bus.stop()   # Drain remaining events, cancel drain tasks
      await container.stop()   # Tear down resources
  ```
- Handlers must be registered before event_bus.start() so drain tasks are created for all handlers. Components registered during container.start() may publish events; these are routed to existing drain tasks.
- Create scripts/check_event_registration.py. Test: tests/test_check_event_registration.py verifies it catches missing registrations and allows correct ones. Wire into pre-commit config.

### S3.1 — Create scripts/check_event_frozen.py
- Test: tests/test_check_event_frozen.py. Wire into pre-commit config.

### S4 — Add async delivery with per-handler FIFO in sovereignai/shared/event_bus.py
- EventBus uses THREE-STATE state machine: _state: Literal['INIT', 'RUNNING', 'STOPPING', 'STOPPED'] = 'INIT'.
- @property def is_started(self) -> bool: return self._state == 'RUNNING'
- EventBus.start():
  1. Assert _state == 'INIT'; set _state = 'RUNNING'.
  2. Capture self._loop via asyncio.get_running_loop(); store self._loop_thread = threading.current_thread().
  3. Create drain tasks for all handlers currently in registry.
  4. Drain pre_start_buffer (deque(maxlen=1000)) into handler queues via publish_async().
  5. Pre-start buffer overflow policy: drop-oldest (deque maxlen behavior). Log warning: "Pre-start buffer overflow: dropped N oldest events" when any events are dropped.
- EventBus.stop():
  1. If _state != 'RUNNING': return (idempotent).
  2. Set _state = 'STOPPING'.
  3. Cancel drain tasks and await them with return_exceptions=True.
  4. Set _state = 'STOPPED'.
- If publish() or publish_async() called before start(): buffer event in pre_start_buffer. No RuntimeError. Buffer is drained on start().
- If publish() or publish_async() called after stop(): raise RuntimeError('EventBus is stopped.').
- Sync publish() detects current thread; if same as event loop thread (self._loop_thread), uses self._loop.create_task(self.publish_async(...)); otherwise uses asyncio.run_coroutine_threadsafe(self.publish_async(...), self._loop).
- Each handler gets asyncio.Queue(maxsize=queue_maxsize from registry.register()).
- Dedicated asyncio drain task per handler. Drain task wraps handler call in try/except; on unhandled exception, log error, emit trace.handler_crash event via __publish_internal(), and continue draining. Do not stop the drain task.
- Per-handler circuit breaker: >50 errors/10s = unsubscribe (AR7 pattern extension to handlers, documented in DECISIONS.md as DD-23.1). Circuit breaker key is (handler_id, event_type) tuple, not handler_id alone.
- On QueueFull: drop newest incoming event (preserve oldest), increment error counter (counted toward handler's circuit breaker), and record drop toward per-handler aggregate. Emit at most one queue.dropped report per handler per second, with count of dropped events in payload.
- CRITICAL EVENT ROUTING: Events with trace_level=CRITICAL or event_type ending in .error or .completed are routed to a RESERVED BOUNDED QUEUE per handler (maxsize=100, separate from normal queue). This queue is drained by the SAME drain task but with higher priority (critical queue checked before normal queue). Circuit breaker applies to critical queue errors too. On critical queue overflow: write to critical_overflow.sqlite and emit trace.critical_overflow event.
- Pre-start critical events: ALL events including critical go to pre_start_buffer before start(). No bypass. On start(), buffer drain routes critical events to reserved queues.
- __publish_internal(event: Event) is a private method (name-mangled) on EventBus that: (1) skips pre-start/post-stop guards, (2) skips circuit breaker checks, (3) directly enqueues to handler queues or calls synchronous handlers, (4) checks asyncio.get_running_loop() is self._loop — raises RuntimeError if called from wrong thread, (5) checks self._state == 'RUNNING' — raises RuntimeError if not running. Used ONLY by drain tasks for trace emissions.
- Drain tasks must never call publish() synchronously from within their own callback. Any trace emission from drain uses __publish_internal().

### S5 — Subscribe Librarian to all events
- Librarian consumes events for episodic memory (DD-20.10.8).
- Async drain, non-blocking. Librarian registers with queue_maxsize=10000 (bounded, not unbounded). Librarian events are never dropped via the normal drop-newest policy, but QueueFull can still occur if the drain falls behind.
- Overflow policy: On QueueFull for the Librarian queue, write the event to librarian_overflow.sqlite and ack. A background replay task drains the SQLite table back into the queue when the queue size drops below 1000.
- Librarian subscription uses separate circuit breaker config: >500 errors/60s = log warning only, no auto-unsubscribe. Librarian is system-critical consumer per AR8.
- Librarian circuit breaker evaluated as single aggregate counter across all event types (handler_id only), not per-(handler_id, event_type) tuple.
- One subscription: registry.register("*", None, librarian.handle_event, queue_maxsize=10000). Wildcard "*" subscription is evaluated at dispatch time — any event type registered at any point matches.

### S6 — Add event versioning in sovereignai/shared/types.py
- On major version bump, EventRegistry maintains _deprecated_events map. Consumers subscribed to old event type receive trace.deprecated_event_type trace event AND warnings.warn(..., DeprecationWarning) for developer visibility. Also add startup-time log: "WARNING: Event type 'TaskCreated' is deprecated. Update subscriptions to 'TaskCreated_v2'." Only log once per deprecated event type at app boot.
- The warnings.warn fires once at the first publish of a deprecated event. Both are deduplicated per event type.
- Script-enforced check: check_event_frozen.py enforces frozen classes.

### S7 — Create web endpoints in web/main.py
- /api/events/types GET: list registered event types. Returns EventTypeListDTO.
- /api/events/subscriptions GET: list active subscriptions. Returns SubscriptionListDTO.
- DTOs in web/schemas.py: EventTypeListDTO, SubscriptionListDTO.

### S8 — Harden /api/hardware/stream SSE
- WILL edit: web/main.py — verify StreamingResponse with text/event-stream.
- Add asyncio.CancelledError handling for client disconnect.
- Send retry: 3000 as SSE field in stream body, not HTTP header.
- Enforce session cookie auth on /api/hardware/stream; reject unauthenticated connections with 403.
- Verify that the SSE stream endpoint emits the retry field in every event. Server-side must include `retry=3000` in each stream message.

### S9 — Create tests
- test_typed_event_bus.py: routing by event_type, version handling, backward-compat, channel alias stays synced with event_type, event_channel_constructor_backward_compat.
- test_event_registry.py: signature validation, fail-fast, wildcard dispatch, test_register_wildcard_none_payload.
- test_async_delivery.py: FIFO order, circuit breaker trigger, sync publish same-thread (create_task), sync publish cross-thread (run_coroutine_threadsafe), queue_full_drops_newest, test_critical_event_routing (verifies .error/.completed events use reserved queue), test_librarian_never_drops_events, test_drain_task_crash_recovery, test_publish_before_start_buffers (verifies event lands in pre_start_buffer and is delivered after start), test_publish_after_stop_raises, test_queue_dropped_aggregated (verifies at most one report per second per handler), test_critical_queue_overflow_sqlite (verifies critical overflow writes to SQLite), test_event_bus_three_state (verifies INIT→RUNNING→STOPPING→STOPPED transitions), test_is_started_property (verifies event_bus.is_started returns correct bool).
- test_event_persistence.py: Librarian integration, episodic storage, Librarian survives transient SQLite lock errors, events registered after "*" subscription are still persisted.
- test_hardware_stream_requires_cookie.py: verifies SSE auth.
- test_events_api.py: list types endpoint, list subscriptions endpoint.

### S10 — Run /verify after each edit. Run /close.