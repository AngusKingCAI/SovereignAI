Depends on: prompt-20.9.9
Vision principles: P7 (modular and flexible), P9 (observability), P13 (strong and robust)
Open questions resolved: Q-22.1 through Q-22.6

Rev 15 patches P22-U (CRITICAL): unconditional `shutil.rmtree` on user-provided `overflow_dir` would delete persistent directories (e.g., `/var/log/sovereignai/`). Fixed via ownership flag.

Rev 16 patches P22-V (MEDIUM): `call_soon_threadsafe` raises `RuntimeError: Event loop is closed` synchronously in thread-pool worker during hard shutdown (loop closed, not just stopped). Existing `_safe_publish_internal` wrapper catches at callback execution, not at scheduling call. Fixed by wrapping scheduling call in try/except.

S0.5 research: Per-handler FIFO + circuit breakers prevent cascade. Async delivery prevents publisher blocking. Forward-compatible schemas avoid migration. SSE retry uses stream-body field, not HTTP header.

## S0 — Opening

S0.0 — Not resuming. Skip.
S0.1 — Run /open. Verify `prompt-20.9.9` tag. Working copy clean.
S0.2 — Read AGENTS.md.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant.
S0.5 — Verified: `app/sovereignai/librarian/librarian.py` has NO `handle_event` method. Plan 22 S5 DEFERRED. `ar_checks/run_all.py` auto-discovers via `*.py` glob (skips `run_all.py`, `_`-prefixed, 3 arg-required scripts).

## Plan Body

### S1 — Extend EventBus in app/sovereignai/shared/event_bus.py
- Breaking change: constructor `(trace)` → `(trace, registry, overflow_dir: Path | None = None)`. At runtime in `__init__`: if `overflow_dir is None`, set `self._overflow_dir = Path(tempfile.mkdtemp(prefix="eventbus_"))` and `self._owns_overflow_dir = True`; else `self._owns_overflow_dir = False` (P22-U — ownership tracking). Derive `critical_overflow_{instance_id}.sqlite` under `self._overflow_dir` (P22-A, N2).
- Before editing: `grep -R 'EventBus(' app/ .agent/executor/tests/` — update ALL call sites. Confirmed sites: `app/sovereignai/main.py:37`, `.agent/executor/tests/sovereignai/{test_event_bus.py, test_capability_api.py, test_capability_api_hardware.py, test_task_state_machine.py}` (P22-I).
- Update `app/sovereignai/main.py`: create `registry = EventRegistry()` before `bus = EventBus(trace=trace, registry=registry)`.
- Add `version: int = 1`, `trace_level: TraceLevel = TraceLevel.INFO` to Event. `channel` stored field; `event_type` read-only property alias. Frozen dataclass.
- Keep sync `publish()`; add `publish_async()`.

### S2 — Create EventRegistry in app/sovereignai/shared/event_registry.py
- `register(event_type, payload_class, handler, queue_maxsize=1000)`. Wildcard `*`: `payload_class=None`, validation skipped. `handlers_for(event_type)` returns matching handlers.
- **Post-start registration (P22-D)**: `register()` after `EventBus.start()` raises `RuntimeError`. Fail-fast.

### S2.1 — Create event payload classes in app/sovereignai/shared/events.py
- `TaskCreated`, `TaskUpdated`, `AgentStep`, `HardwareStatus`, etc. Optional fields with defaults. Major break = new class.

### S3 — Wire event registrations in app/sovereignai/main.py
- `registry.register("task.created", TaskCreated, task_handler)` per type.
- Lifespan in `app/web/main.py`: register handlers → `await event_bus.start()` → `await container.start()` → `try: yield finally: await event_bus.stop(); await container.stop()`.
- Create `.agent/executor/scripts/ar_checks/check_event_registration.py`. Test: `.agent/executor/tests/sovereignai/test_check_event_registration.py`. Auto-discovered by `run_all.py` (P22-C confirmed).

### S3.1 — Create .agent/executor/scripts/ar_checks/check_event_frozen.py
- Test: `.agent/executor/tests/sovereignai/test_check_event_frozen.py`. Auto-discovered.

### S4 — Async delivery with per-handler FIFO in app/sovereignai/shared/event_bus.py
- Four-state: `_state: Literal['INIT', 'RUNNING', 'STOPPING', 'STOPPED'] = 'INIT'`. `@property is_started -> bool: return self._state == 'RUNNING'`.
- `start()` synchronous: state set to RUNNING before any `await` (P22-M rejected — no async window). Guard: if `_state != 'INIT'`: raise. Capture `self._loop`, `self._loop_thread`. Create drain tasks. Drain buffers via `publish_async()`.
- `stop()`: idempotent; INIT→STOPPING→cancel drain tasks (`return_exceptions=True`)→STOPPED. **Cleanup (P22-Q, P22-U)**: after STOPPED, `if self._owns_overflow_dir: shutil.rmtree(self._overflow_dir, ignore_errors=True)`. NEVER delete user-provided directories (P22-U CRITICAL — protects against data loss when caller passes persistent `overflow_dir` like `/var/log/sovereignai/`).
- `publish()`/`publish_async()`: before start → buffer. STOPPING/STOPPED → raise.
- Drain task per handler: `asyncio.Queue(maxsize=queue_maxsize)`. Wraps handler in try/except; on exception log + emit `trace.handler_crash` via `__publish_internal()` (wrapped in try/except, never re-raise, P22-G). Continue draining.
- **Sync handlers (P22-K)**: check `inspect.iscoroutinefunction(handler)`. If False, run via `asyncio.to_thread(handler, event)` unless `loop_safe=True`.
- **Circuit breaker (P22-E)**: separate `error_counter` (unhandled exceptions) from `drop_counter` (QueueFull). >50 errors/10s = unsubscribe. `drop_counter` MUST NOT trigger breaker.
- **QueueFull**: drop newest, increment `drop_counter`, emit ≤1 `queue.dropped` per handler per second.
- **Critical routing**: `trace_level=CRITICAL` or `event_type` ending `.error`/`.completed` → reserved bounded queue (maxsize=100). Same drain task, higher priority.
- **Critical overflow (P22-A, P22-F, P22-R, P22-V)**: write to `{overflow_dir}/critical_overflow_{instance_id}.sqlite` via `asyncio.to_thread()` (timeout=5.0). After write completes, schedule emission via `try: self._loop.call_soon_threadsafe(self._safe_publish_internal, event) except RuntimeError: pass` (P22-V — loop closed during hard shutdown; drop event silently). The `_safe_publish_internal` wrapper also catches `RuntimeError` at execution time as belt-and-suspenders (P22-R). Emit at `TraceLevel.ERROR` (not CRITICAL, avoids feedback loop, DD-22.11.1). If SQLite write fails, log at ERROR, continue.
- Critical overflow = best-effort, not guaranteed (DD-22.11.3).
- Pre-start buffers: non-critical = drop-oldest with `dropped_count` (DD-22.11.7). Critical = drop oldest with separate counter, log warning.
- `__publish_internal(event)`: name-mangled. **Early-return guard (P22-R)**: `if self._state in ('STOPPING', 'STOPPED'): log DEBUG "dropped late trace after stop"; return`. Otherwise: checks `asyncio.get_running_loop() is self._loop` and `_state == 'RUNNING'`. Drain tasks are instance-scoped coroutines; `self.__publish_internal` resolves via closure (P22-N rejected).
- Drain tasks MUST NEVER call `publish()` synchronously. Use `__publish_internal()`.

### S5 — Librarian subscription — DEFERRED (P22-H)
- Librarian has NO `handle_event` (verified S0.5). S5 deferred.
- Add DEBT.md entry at /close: "Librarian.handle_event method + episodic event consumer — target plan TBD".
- Remove from S9: `test_event_persistence.py`, `test_librarian_never_drops_events`.

### S6 — Add event versioning in app/sovereignai/shared/types.py
- On major bump, `_deprecated_events` map. Consumers receive `trace.deprecated_event_type` + `warnings.warn(DeprecationWarning)`. Startup log once per type.

### S7 — Create web endpoints in app/web/main.py
- `/api/events/types` GET → `EventTypeListDTO`. `/api/events/subscriptions` GET → `SubscriptionListDTO`. DTOs in `app/web/schemas.py`.

### S8 — Harden /api/hardware/stream SSE in app/web/main.py
- WILL edit: `app/web/main.py`. Verify `StreamingResponse` + `text/event-stream`. `asyncio.CancelledError` handling. `retry: 3000` as SSE field. Enforce session cookie auth; 403 unauthenticated.
- **Existing consumers (P22-L)**: audit and update any existing tests of `/api/hardware/stream` expecting unauthenticated 200 → expect 403.

### S9 — Tests in .agent/executor/tests/sovereignai/
- `test_typed_event_bus.py`: routing, version handling, backward-compat, channel alias, constructor.
- `test_event_registry.py`: signature validation, fail-fast, wildcard, `post-start-register-raises` (P22-D).
- `test_async_delivery.py`: FIFO, `circuit breaker on error_counter only` (P22-E), `QueueFull increments drop_counter only`, sync publish same/cross-thread, `queue_full_drops_newest`, `test_critical_event_routing`, `test_drain_task_crash_recovery`, `test_publish_before_start_buffers`, `test_publish_after_stop_raises`, `test_queue_dropped_aggregated`, `test_critical_queue_overflow_sqlite` (P22-F `call_soon_threadsafe`), `test_event_bus_four_state`, `test_is_started_property`, `test_stopping_publish_raises`, `test_publish_state_check_before_loop`, `test_pre_start_critical_buffer`, `test_critical_overflow_emits_error_level`, `test_sync_handler_runs_in_thread` (P22-K), `test_concurrent_overflow_dir_isolation` (P22-A), `test_overflow_dir_cleaned_on_stop` (P22-Q), `test_publish_internal_safe_after_stop` (P22-R), `test_user_provided_overflow_dir_not_deleted` (P22-U — verifies ownership flag prevents rmtree on caller-provided dir), `test_call_soon_threadsafe_loop_closed_handled` (P22-V — verifies no unhandled exception when loop closed during hard shutdown).
- `test_hardware_stream_requires_cookie.py`: SSE auth + existing-consumer migration (P22-L).
- `test_events_api.py`, `test_check_event_registration.py`, `test_check_event_frozen.py`.

### S10 — Landmine compliance
- M1: `sovereignai.*` imports. M2: update `WEB_MAIN_ALLOWED_IMPORTS` for `app/web/main.py`. M3: update `ALLOWLIST` in `spec_match.py` for `app/sovereignai/shared/{event_registry,events}.py`. M4: tests in `tests/sovereignai/`.

### S11 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-22.1, DD-22.11.1, DD-22.11.2, DD-22.11.3, DD-22.11.7, DD-22.11.9, DD-22.11.10 to `.agent/shared/DECISIONS.md` as Proposed (P22-B — explicit list, no ranges).
- At /close step 12, add DEBT.md entry: "Librarian.handle_event method + episodic event consumer — target plan TBD" (P22-H).
