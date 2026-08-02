Depends on: prompt-20.9.9
Vision principles: P7 (modular and flexible), P9 (observability), P13 (strong and robust)
Open questions resolved: Q-22.1 through Q-22.6

S0.5 research: Per-handler FIFO + circuit breakers prevent cascade. Async delivery prevents publisher blocking. Forward-compatible schemas avoid migration. SSE retry uses stream-body field, not HTTP header.

## S0 — Opening

S0.0 — Not resuming. Skip.
S0.1 — Run /open. Verify `prompt-20.9.9` tag. Working copy clean.
S0.2 — Read AGENTS.md.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant.
S0.5 — Verified: `app/sovereignai/librarian/librarian.py` has NO `handle_event` method. Plan 22 S5 (Librarian subscription) DEFERRED. Add DEBT.md entry at /close: "Librarian.handle_event — target plan TBD". `ar_checks/run_all.py` auto-discovers via `*.py` glob (skips `run_all.py`, `_`-prefixed, and 3 arg-required scripts) — new scripts auto-discovered, no registration needed.

## Plan Body

### S1 — Extend EventBus in app/sovereignai/shared/event_bus.py
- Breaking change: constructor `(trace)` → `(trace, registry, overflow_dir: Path | None = None)`. Default `overflow_dir = tempfile.mkdtemp(prefix="eventbus_")`. Derive `critical_overflow.sqlite` and `librarian_overflow.sqlite` (note: deferred — see S5) under `overflow_dir` with `instance_id` suffix so concurrent instances don't collide (P22-A).
- Before editing: `grep -R 'EventBus(' app/ .agent/executor/tests/` — update ALL call sites. Confirmed sites: `app/sovereignai/main.py:37`, `.agent/executor/tests/sovereignai/{test_event_bus.py, test_capability_api.py, test_capability_api_hardware.py, test_task_state_machine.py}`. Each must construct `EventRegistry` + `overflow_dir` (use `tempfile.mkdtemp` in tests) (P22-I).
- Update `app/sovereignai/main.py`: create `registry = EventRegistry()` before `bus = EventBus(trace=trace, registry=registry)`.
- Add `version: int = 1`, `trace_level: TraceLevel = TraceLevel.INFO` to Event. Keep `channel` as stored field; add `event_type` as read-only property alias. Frozen dataclass.
- Keep sync `publish()`; add `publish_async()` for async path.

### S2 — Create EventRegistry in app/sovereignai/shared/event_registry.py
- `register(event_type, payload_class, handler, queue_maxsize=1000)`. Wildcard `event_type='*'`: `payload_class=None`, signature validation skipped.
- `handlers_for(event_type)` returns matching handlers (including wildcard).
- **Post-start registration (P22-D)**: `register()` called after `EventBus.start()` raises `RuntimeError('Cannot register handler after EventBus started')`. Fail-fast; no lazy drain creation.

### S2.1 — Create event payload classes in app/sovereignai/shared/events.py
- `TaskCreated`, `TaskUpdated`, `AgentStep`, `HardwareStatus`, etc. Optional fields with defaults. Major break = new class (`TaskCreated_v2`); old frozen for read.

### S3 — Wire event registrations in app/sovereignai/main.py
- `registry.register("task.created", TaskCreated, task_handler)` per type.
- Lifespan in `app/web/main.py`: register handlers → `await event_bus.start()` → `await container.start()` → `try: yield finally: await event_bus.stop(); await container.stop()`.
- Create `.agent/executor/scripts/ar_checks/check_event_registration.py`. Test: `.agent/executor/tests/sovereignai/test_check_event_registration.py`. Wire into pre-commit. Auto-discovered by `run_all.py` (P22-C confirmed: glob-based).

### S3.1 — Create .agent/executor/scripts/ar_checks/check_event_frozen.py
- Test: `.agent/executor/tests/sovereignai/test_check_event_frozen.py`. Auto-discovered by `run_all.py`.

### S4 — Async delivery with per-handler FIFO in app/sovereignai/shared/event_bus.py
- Four-state: `_state: Literal['INIT', 'RUNNING', 'STOPPING', 'STOPPED'] = 'INIT'`. `@property is_started -> bool: return self._state == 'RUNNING'`.
- `start()` is synchronous: state set to RUNNING before any `await` (P22-M rejected — no async window). Guard: if `_state != 'INIT'`: raise `RuntimeError`. Capture `self._loop`, `self._loop_thread`. Create drain tasks for all handlers. Drain buffers via `publish_async()`.
- `stop()`: idempotent; INIT→STOPPING→cancel drain tasks (`return_exceptions=True`)→STOPPED.
- `publish()`/`publish_async()`: before start → buffer (non-critical: `pre_start_buffer`; critical: `pre_start_critical_buffer`, maxsize=10000). STOPPING → raise. STOPPED → raise. Sync `publish()`: check `_state` FIRST, then detect thread/loop.
- Drain task per handler: `asyncio.Queue(maxsize=queue_maxsize)`. Wraps handler in try/except; on exception log + emit `trace.handler_crash` via `__publish_internal()` (wrapped in try/except — never re-raise, P22-G). Continue draining.
- **Sync handlers (P22-K)**: before invoking, check `inspect.iscoroutinefunction(handler)`. If False, run via `asyncio.to_thread(handler, event)` unless registered with `loop_safe=True`.
- **Circuit breaker (P22-E)**: separate `error_counter` (unhandled exceptions) from `drop_counter` (QueueFull). >50 errors/10s = unsubscribe. `drop_counter` MUST NOT trigger breaker.
- **QueueFull**: drop newest, increment `drop_counter`, emit ≤1 `queue.dropped` per handler per second.
- **Critical routing**: `trace_level=CRITICAL` or `event_type` ending `.error`/`.completed` → reserved bounded queue (maxsize=100) per handler. Same drain task, higher priority.
- **Critical overflow (P22-A, P22-F)**: write to `{overflow_dir}/critical_overflow_{instance_id}.sqlite` via `asyncio.to_thread()` with timeout=5.0. After write completes, schedule emission back to event loop via `self._loop.call_soon_threadsafe(self.__publish_internal, event)` — NEVER call `__publish_internal()` directly from thread-pool thread. Emit at `TraceLevel.ERROR` (not CRITICAL, avoids feedback loop, DD-22.11.1). If SQLite write fails, log at ERROR, continue.
- Critical overflow = best-effort, not guaranteed (DD-22.11.3).
- **Pre-start buffers**: non-critical = drop-oldest with `dropped_count` (DD-22.11.7). Critical = drop oldest with separate counter, log warning.
- `__publish_internal(event)`: name-mangled private method. Skips pre-start/post-stop guards, skips circuit breaker. Checks `asyncio.get_running_loop() is self._loop` and `_state == 'RUNNING'`. Drain tasks are instance-scoped coroutines; `self.__publish_internal` resolves correctly via closure (P22-N rejected).
- Drain tasks MUST NEVER call `publish()` synchronously. Use `__publish_internal()`. Critical overflow emission MUST use `__publish_internal()` at ERROR level (DD-22.11.9).

### S5 — Librarian subscription — DEFERRED (P22-H)
- **Librarian has NO `handle_event` method** (verified in S0.5). S5 deferred.
- Add DEBT.md entry at /close: "Librarian.handle_event method + episodic event consumer — target plan TBD".
- Remove from S9: `test_event_persistence.py`, `test_librarian_never_drops_events`.

### S6 — Add event versioning in app/sovereignai/shared/types.py
- On major bump, `_deprecated_events` map. Consumers receive `trace.deprecated_event_type` + `warnings.warn(DeprecationWarning)`. Startup log once per type. `warnings.warn` fires once at first publish.

### S7 — Create web endpoints in app/web/main.py
- `/api/events/types` GET → `EventTypeListDTO`. `/api/events/subscriptions` GET → `SubscriptionListDTO`. DTOs in `app/web/schemas.py`.

### S8 — Harden /api/hardware/stream SSE in app/web/main.py
- WILL edit: `app/web/main.py`. Verify `StreamingResponse` with `text/event-stream`. `asyncio.CancelledError` handling. `retry: 3000` as SSE field in body. Enforce session cookie auth; 403 unauthenticated.
- **Existing consumers (P22-L)**: audit and update any existing tests of `/api/hardware/stream` expecting unauthenticated 200 → expect 403.

### S9 — Tests in .agent/executor/tests/sovereignai/
- `test_typed_event_bus.py`: routing, version handling, backward-compat, channel alias, constructor.
- `test_event_registry.py`: signature validation, fail-fast, wildcard, post-start-register-raises (P22-D).
- `test_async_delivery.py`: FIFO, circuit breaker on `error_counter` only (P22-E), QueueFull increments `drop_counter` only, sync publish same/cross-thread, `queue_full_drops_newest`, `test_critical_event_routing`, `test_drain_task_crash_recovery`, `test_publish_before_start_buffers`, `test_publish_after_stop_raises`, `test_queue_dropped_aggregated`, `test_critical_queue_overflow_sqlite` (verifies `call_soon_threadsafe`, P22-F), `test_event_bus_four_state`, `test_is_started_property`, `test_stopping_publish_raises`, `test_publish_state_check_before_loop`, `test_pre_start_critical_buffer`, `test_critical_overflow_emits_error_level`, `test_sync_handler_runs_in_thread` (P22-K), `test_concurrent_overflow_dir_isolation` (P22-A).
- `test_hardware_stream_requires_cookie.py`: SSE auth + existing-consumer migration (P22-L).
- `test_events_api.py`: list types, list subscriptions.
- `test_check_event_registration.py`, `test_check_event_frozen.py`.

### S10 — Landmine compliance
- M1: `sovereignai.*` imports. M2: update `WEB_MAIN_ALLOWED_IMPORTS` for `app/web/main.py`. M3: update `ALLOWLIST` in `spec_match.py` for `app/sovereignai/shared/{event_registry,events}.py`. M4: tests in `tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-22.1, DD-22.11.1, DD-22.11.2, DD-22.11.3, DD-22.11.7, DD-22.11.9, DD-22.11.10 to `.agent/shared/DECISIONS.md` as Proposed (P22-B — explicit list, no ranges).
- At /close step 12, add DEBT.md entry: "Librarian.handle_event method + episodic event consumer — target plan TBD" (P22-H).
