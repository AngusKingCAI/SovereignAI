Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
**Optional forward dependency**: Plan 34 (Librarian Events & Cross-Task Memory) — memory panel shows `PENDING` badge during Plan 32 execution; Plan 32 ships before Plan 34. Badge is operator-confirmation only, no runtime impact.
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5, DD-32.6, DD-32.7
**Revision**: Rev16

## Executor Manifest

**Plan**: 32
**Phases**: 5 (S1–S5; S0 excluded from count)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/tui/client.py` — `TUIWebClient` with cookie jar | `pytest app/tui/tests/test_client.py -v` passes |
| S2 | DEBT-7 verification spike + polling fallback decision | `pytest app/tui/tests/test_debt7_verification.py -v` passes |
| S3 | 10 sidebar panels wired to backend APIs (SSE where verified per S2.3, REST polling fallback per S2.2 otherwise) | `pytest app/tui/tests/test_panels.py -v` passes |
| S4 | `app/tui/main.py` with shutdown detection + auto-refresh | `pytest app/tui/tests/test_main.py -v` passes |
| S5 | AR check scripts + document hygiene | `pytest .agent/executor/tests/test_document_hygiene.py -v` passes |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(tui): add TUI web client, 10-panel sidebar, and shutdown detection`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — TUI Web Client

S1.1: Create `app/tui/client.py` — `TUIWebClient` wraps httpx.AsyncClient
S1.2: Session cookie jar: stores at `platformdirs.user_cache_dir("sovereignai") / "cookie"`. Atomic write restrictive mode: `open(path, 'wb', opener=lambda p, f: os.open(p, f, 0o600))`. After open, explicitly `os.chmod(path, 0o600)` to reset permissions on existing files. Parent: `makedirs(parent, mode=0o700, exist_ok=True)`. Windows: document ACL limitation.
S1.3: Base URL from `SOVEREIGNAI_API_URL` env var or default `http://localhost:8000`
S1.4: Test: `pytest app/tui/tests/test_client.py -v` — `test_cookie_jar_permissions`, `test_cookie_jar_permissions_reset_on_existing_file`, `test_base_url_env_var`, `test_base_url_default_localhost`

## S2 — DEBT-7 Verification Spike

S2.1: Integration test — start test HTTP server with SSE endpoint requiring `Cookie` header. Use textual `App.run_test()` to run TUI connecting to SSE with session cookie. Assert cookie sent and SSE events received. Fixture: `app/tui/tests/conftest.py` defines **sse_test_server**: An async context-manager fixture that launches an ASGI test server (via httpx.ASGITransport or uvicorn) on a bound localhost port (e.g., 127.0.0.1:0 for OS-assigned port). Yields the full URL (http://127.0.0.1:{port}). Guarantees cleanup on exit (server shutdown). Fixture scope: function. Usage: async with sse_test_server() as base_url: client = httpx.AsyncClient(base_url=base_url). **Partial header failure**: If textual HTTP client can set some headers but not Cookie, treat as SSE_FAIL (all-or-nothing). The Cookie header is required for auth; without it, SSE is non-functional. Log outcome: SPIKE_OUTCOME: SSE_FAIL reason=cookie_header_unsupported.
S2.2: If verification fails: defer S3.3 (tasks SSE) and S3.8 (logs SSE) to v2; ship polling-based fallback (5s poll tasks via `/api/events/tasks` REST, 5s poll logs via `GET /api/trace/logs`). On `SSE_FAIL`: lifecycle SSE also disabled; rely on `/api/lifecycle/ready` polling (2s interval) and file sentinel for shutdown detection.
S2.3: If verification succeeds: proceed with SSE panels; document evidence in execution log.
S2.4: **Mechanism**: S2 probes cookie/SSE capability ONLY. `test_sse_paths_wired` is REMOVED from S2. Spike writes `SSE_OK` or `SSE_FAIL` to `request.config.stash[_SPIKE_RESULT_KEY]`. Consumer tests for path-wiring assertions are in S3/S4 (after implementation). S2.5 verification: `pytest app/tui/tests/test_debt7_verification.py -v` — `test_spike_decision_recorded_in_log` only. Path-wiring verified in S3.13 and S4.5.
  Spike execution log: writes outcome to `build/execution.log` (relative to repo root). Format: `SPIKE_OUTCOME: SSE_OK|SSE_FAIL timestamp={iso8601}`. Operator-visibility only. **File-writing responsibility**: The session-scoped fixture (not the individual test function) appends the outcome to build/execution.log after writing to stash. Format: SPIKE_OUTCOME: SSE_OK|SSE_FAIL timestamp={iso8601}.
  `app/tui/tests/conftest.py` defines `@pytest.fixture(scope="session", autouse=True) def spike_probe(request)` — executes SSE cookie auth probe once at session start. Uses module-level `_SPIKE_RESULT_KEY = pytest.StashKey[str]()`; writes result (`"SSE_OK"` or `"SSE_FAIL"`) to `request.config.stash[_SPIKE_RESULT_KEY]`. Assert `hasattr(request.config, 'stash')` in fixture. On probe error/exception: sets `"SSE_FAIL"`.
  Pin `pytest>=7.0` in test dependencies.
  **No cross-test dependency** — autouse session fixture guarantees single execution before any consumer test.
S2.5: Test: `pytest app/tui/tests/test_debt7_verification.py -v` — `test_spike_decision_recorded_in_log`
S2.6: **Conditional branching**: If SPIKE_OUTCOME=SSE_OK → applicable panels (orchestrator, tasks, logs, audit) use SSE for live updates. If SPIKE_OUTCOME=SSE_FAIL or spike deferred (DEBT-7 unresolved) → all panels use REST polling exclusively. This transition is explicit and test-documented.

## S3 — Sidebar Panel Wiring (10 sections per P8)

**Preamble**: S3 must not start until S2.5 passes (SSE verified OR polling fallback recorded).
S3.1: Update `app/tui/panels/orchestrator.py` — `/api/orchestrator/status`. Extract `OrchestratorStatus` fields: `state`, `uptime_seconds`, `tasks_completed`, `tasks_failed`; display each metric with label.
S3.2: Update `app/tui/panels/workers.py` — `/api/health` polling. Extract `subsystems[]` from `HealthSnapshot`; display each adapter with `name` + `status` badge.
S3.3: Update `app/tui/panels/tasks.py` — SSE `/api/events/tasks` (or 5s polling REST fallback with `since_event_id` cursor per Plan 31 S3.5). Extract `TaskEventDTO` fields: `event_id`, `task_id`, `event_type`, `timestamp`, `details`; render as scrollable event list grouped by task_id.
S3.4: Update `app/tui/panels/memory.py` — forward dep: Plan 34 endpoint. Panel shows `PENDING` badge until `/api/orchestrator/memory/graph` returns 200 after Plan 34. Add test asserting PENDING state. Memory panel state: 404→`PENDING` (Plan 31 not yet deployed); 503 with `error_code=memory_not_ready`→`Loading…` (transient, Plan 34 backend not loaded); 200→`Live`. **v1 normal flow**: after Plan 31 deploys, memory routes always exist (return 503 until Plan 34 activates backend). 404 is only reachable if Plan 31 itself hasn't deployed. Poll interval for PENDING state: 30s.
S3.5: Update `app/tui/panels/models.py` — `/api/models`. Extract `ModelQuery` response fields; display model ID, provider, sync status.
S3.6: Update `app/tui/panels/adapters.py` — `/api/health`. Extract `subsystems[]` from `HealthSnapshot`; display each adapter with `name` + `status` badge; highlight DEGRADED/UNHEALTHY adapters.
S3.7: Update `app/tui/panels/hardware.py` — `/api/health` (hardware metrics). Extract hardware-specific subsystem details from `HealthSnapshot.subsystems[].details`.
S3.8: Update `app/tui/panels/logs.py` — SSE `/api/trace/stream` (or 5s polling REST fallback via `GET /api/trace/logs`). Extract `TraceEvent` fields: `timestamp`, `level`, `source`, `message`; render as color-coded log view (ERROR=red, WARN=yellow, INFO=default).
S3.9: Update `app/tui/panels/options.py` — `/api/options/*`. Extract `OptionsUpdate` fields; display option key-value pairs in editable list.
S3.10: Update `app/tui/panels/audit.py` — `/api/messaging/audit` (10th panel). Extract `AuditPage.items` with `source_department`, `target_department`, `content`; display as paginated table with timestamp, source→target columns, content preview.
S3.11: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S3.12: Error classification by API error code (not just HTTP status):
  - **Terminal**: `auth_expired`, `login_required`, `authorization_denied` — stop retry, surface login prompt. `not_ready_timeout` — surface 'Server still initializing' with manual reconnect (no login prompt).
  - **Terminal (no login)**: `lockout` — surface lockout message with `retry_after_seconds` from envelope; `idempotency_conflict` — surface "duplicate request" warning.
  - **Transient**: 429 and 503 with `Retry-After` header (respect interval; if exceeds 30s, surface 'Server shutting down' status), other 5xx (generic exp-backoff: base 1s, max 30s, jitter ±50%).
  - **Transient (SSE control)**: `not_ready` = Hold (keep connection open, silence UI hint, do not increment retry counter, wait up to SSE broker 30s window).
  - **Operator**: 501 → surface with retry button.
  - All 4xx except 429/423/409/401/403: Terminal — surface error, no retry.
  - **Explicit classifications**: 408→Transient (exp-backoff), 500/502/504→Transient (generic exp-backoff), 501→Operator. Truth-table test enumerates all codes.
  - **Overflow handling**: on SSE `event: overflow`, surface one-shot banner "X events dropped during slow consumption" in panel; log via TraceEmitter.
  Error classification truth table (authoritative for `test_truth_table_all_codes`):
  | Code/Error | Classification | Action |
  |-----------|---------------|--------|
  | 200 | Success | Process normally |
  | 401 login_required | Terminal | Surface login prompt |
  | 403 authorization_denied | Terminal | Surface error |
  | 403 setup_token_required | Terminal | Surface setup token prompt |
  | 403 insecure_deployment | Terminal | Surface error |
  | 409 idempotency_conflict | Terminal (no login) | Surface 'duplicate request' warning |
  | 423 lockout | Terminal (no login) | Surface lockout message with retry_after_seconds |
  | 429 rate_limited | Transient | Respect Retry-After, backoff |
  | 501 | Operator | Not implemented, report |
  | 503 memory_not_ready | Transient/Loading | Respect retry_after_seconds, show Loading |
  | 503 (other) | Transient | Respect Retry-After, backoff |
  | 503 service_draining | Transient (Retry-After: 60) | Server shutting down, drain rejection |
  | SSE not_ready | Transient (hold) | Hold connection, silence UI |
  | SSE not_ready_timeout | Terminal (no login) | Surface 'Server still initializing', manual reconnect |
  | SSE auth_expired | Terminal | Surface login prompt |
  | SSE replay_unavailable | Terminal (no login) | Close connection, reopen or fall back to REST resynchronization |
  | SSE overflow | Operator (one-shot) | Banner 'X events dropped', auto-dismiss 10s |
  | All other 4xx (except 401, 403, 404, 408, 409, 429) | Terminal | Surface error, no retry |
  | 500/502/504 | Transient | Generic exp-backoff (base 1s, max 30s, jitter ±50%) |
  | 408 | Transient (exp-backoff) | Client timeout, retry |
  Client reads `Retry-After` HTTP header when present; falls back to `retry_after_seconds` from JSON error envelope. If both present and conflicting: header takes precedence. Test: `test_retry_after_header_preferred_over_envelope`.
S3.13: Test: `pytest app/tui/tests/test_panels.py -v` — `test_error_terminal_auth_expired`, `test_error_transient_429_respects_retry_after`, `test_error_transient_503_retry_after_60_delays`, `test_error_lockout_no_login_prompt`, `test_sse_overflow_shows_banner`, `test_not_ready_hold_keeps_connection`, `test_truth_table_all_codes`, `test_orchestrator_panel_renders_status` (canonical OrchestratorStatus DTO), `test_tasks_panel_polls_since_event_id` (TaskListResponse with events), `test_memory_panel_shows_pending_before_plan34` (MemoryNotReadyResponse), `test_options_panel_fetches_and_displays_options` (OptionsData DTO), `test_models_panel_renders_model_list` (ModelListResponse from RF-10), `test_workers_panel_displays_adapters` (HealthSnapshot subsystems), `test_hardware_panel_displays_details` (HealthSnapshot subsystems with kind discriminator), `test_log_panel_renders_log_entries` (paginated AuditPage), `test_audit_panel_pagination` (AuditPage with MessagingAuditEntryDTO), `test_messaging_panel_renders_messages` (CrossDepartmentMessage list), `test_task_panel_uses_sse_after_spike_ok`, `test_task_panel_uses_polling_after_spike_fail`, `test_log_panel_transport_decision_follows_spike_outcome`

## S4 — Main Screen Integration

S4.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or polling fallback). Documented v1 limitation: "10-panel polling is a v1 simplification. v2 will consolidate to `/api/dashboard/state`."
S4.3: Error handling: `DEGRADED` badge on `/api/health` subsystem failure; `DISCONNECTED` badge on network failure
S4.4: Shutdown detection with client-side state machine:
  - **States**: `LIFECYCLE_INIT` → `LIFECYCLE_READY` → `LIFECYCLE_SHUTDOWN_DETECTED`
  - **LIFECYCLE_INIT**: on startup, poll `GET /api/lifecycle/ready` every 2s. `ready: false` is **normal** (core still starting) — stay in INIT. On `ready: true` → transition to READY. On 404 or connection failure → stay in INIT (server may not be started yet). During LIFECYCLE_INIT: every accepted poll response atomically replaces the PID/UUID baseline (even if ready=false). Subsequent matching `ready: true` observation from the NEW baseline is required before transitioning to READY. PID/UUID change during INIT → stay in INIT (server restarting). Timeout: 120s; after 120s timeout: polling continues at 2s interval indefinitely; TUI remains interactive; persistent error banner shown: 'Core process not ready after 120s. Still waiting…'. No exit.
  - **LIFECYCLE_READY**: active monitoring. Sentinel monitoring begins here (after first `ready: true`); on PID/UUID change, update monitored sentinel path. Transitions to SHUTDOWN_DETECTED if: (a) SSE `lifecycle.shutting_down` received; (b) `ready: false` received AND previously saw `ready: true` (true→false transition); (c) HTTP 404; (d) PID changes from previous poll; (e) UUID changes from previous poll.
  - **LIFECYCLE_SHUTDOWN_DETECTED**: (1) set shutting_down = True, cancel active retries, (2) close all SSE connections, (3) attempt POST /api/auth/logout (5s timeout, best-effort), (4) persist cookie state, (5) exit. Graceful drain timeout: 10s max after step 1.
  - **File sentinel fallback**: monitor `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{server_pid}.sentinel"` where `server_pid` from `/api/lifecycle/ready`. Poll interval: 2s. Sentinel content: `{iso8601_utc_timestamp}\n{instance_uuid}\n` (datetime.now(timezone.utc).isoformat()). TUI exits only if PID matches AND UUID matches AND timestamp within 5 minutes. If sentinel file not found during monitoring, log DEBUG and continue polling. **Limitation**: sentinel valid only for same process lifetime; if Web process restarts, old sentinel won't match new UUID. Sentinel validation: file must contain exactly 2 non-empty lines (timestamp + UUID). Fewer lines → log DEBUG, ignore sentinel. Extra lines → log WARN, use first two lines only. Empty file (0 bytes) → log DEBUG, delete sentinel file. Sentinel parser: accepts timezone-aware ISO 8601 timestamps only. Malformed timestamps → log DEBUG, ignore sentinel. Naive (no timezone) → log DEBUG, ignore. Future timestamps (timestamp > now) → log WARN, ignore. Acceptance window: `0 <= now - timestamp <= 300s` (5 minutes).
  Compact state transition table:
  | Current State | Trigger | Next State |
  |---------------|---------|-----------|
  | INIT | ready: true | READY |
  | INIT | ready: false / 404 / connection failure / PID change / UUID change | INIT (baseline replaced) |
  | INIT | 120s timeout (never saw ready:true) | INIT (continues polling, error banner) |
  | READY | SSE lifecycle.shutting_down | SHUTDOWN_DETECTED |
  | READY | ready: false (after previously true) | SHUTDOWN_DETECTED |
  | READY | HTTP 404 | SHUTDOWN_DETECTED |
  | READY | PID change (from established baseline) | SHUTDOWN_DETECTED |
  | READY | UUID change (from established baseline) | SHUTDOWN_DETECTED |
  | READY | Sentinel match (PID+UUID+timestamp) | SHUTDOWN_DETECTED |
S4.5: Test: `pytest app/tui/tests/test_main.py -v` — `test_init_stays_on_ready_false`, `test_init_transitions_to_ready_on_ready_true`, `test_init_pid_change_stays_in_init` (scenario: poll returns `ready: false, pid: 100, uuid: A`; baseline replaced. Next poll returns `ready: true, pid: 101, uuid: B`; stay in INIT — PID and UUID changed from baseline), `test_ready_true_to_false_triggers_shutdown`, `test_sentinel_match_triggers_shutdown`, `test_sentinel_mismatch_no_shutdown`, `test_lifecycle_sse_triggers_shutdown`, `test_ready_pid_change_triggers_shutdown`, `test_ready_uuid_change_triggers_shutdown`, `test_ready_404_triggers_shutdown`, `test_init_120s_timeout_surfaces_error_without_exit`, `test_drain_deadline_cancels_remaining_tasks`
  **test_memory_not_ready_503 ownership**: Plan 31 S3.7 owns this test in test_orchestrator_api.py (Web layer). Plan 34 does NOT list this test — Plan 34 owns backend readiness tests only (test_memory_is_ready_returns_true_after_load, test_memory_is_ready_returns_false_after_flush). No overlap.
  15-second timeout derived from Plan 33 S4.3 sentinel 5-minute (300s) window / 20 = 15s (conservative divisor for TUI responsiveness).

## S5 — AR Checks

S5.1: Update `.agent/executor/tests/test_ar7_no_core_imports_in_ui.py` — add all new TUI files to TUI_ALLOWED_IMPORTS: `app/tui/client.py`, `app/tui/panels/orchestrator.py`, `app/tui/panels/workers.py`, `app/tui/panels/tasks.py`, `app/tui/panels/memory.py`, `app/tui/panels/models.py`, `app/tui/panels/adapters.py`, `app/tui/panels/hardware.py`, `app/tui/panels/logs.py`, `app/tui/panels/options.py`, `app/tui/panels/audit.py`, `app/tui/main.py`
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`
S5.3: **Coverage closing gate**: pytest --cov=app/tui --cov-report=term-missing app/tui/tests/ -v --cov-fail-under=90. This runs after document hygiene as an additional gate.

## Closing

Run `/close`