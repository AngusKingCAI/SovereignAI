Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
**Optional forward dependency**: Plan 34 (Librarian Events & Cross-Task Memory) — memory panel shows `PENDING` badge during Plan 32 execution; Plan 32 ships before Plan 34. Badge is operator-confirmation only, no runtime impact.
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5, DD-32.6, DD-32.7
**Revision**: Rev13

## Executor Manifest

**Plan**: 32
**Phases**: 5 (S0–S5)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/tui/client.py` — `TUIWebClient` with cookie jar | `pytest app/tui/tests/test_client.py -v` passes |
| S2 | DEBT-7 verification spike + polling fallback decision | `pytest app/tui/tests/test_debt7_verification.py -v` passes |
| S3 | 10 sidebar panels wired to backend APIs | `pytest app/tui/tests/test_panels.py -v` passes |
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

S2.1: Integration test — start test HTTP server with SSE endpoint requiring `Cookie` header. Use textual `App.run_test()` to run TUI connecting to SSE with session cookie. Assert cookie sent and SSE events received.
S2.2: If verification fails: defer S3.3 (tasks SSE) and S3.8 (logs SSE) to v2; ship polling-based fallback (5s poll tasks via `/api/events/tasks` REST, 5s poll logs via `GET /api/trace/logs`). On `SSE_FAIL`: lifecycle SSE also disabled; rely on `/api/lifecycle/ready` polling (2s interval) and file sentinel for shutdown detection.
S2.3: If verification succeeds: proceed with SSE panels; document evidence in execution log.
S2.4: **Mechanism**: `app/tui/tests/conftest.py` defines `@pytest.fixture(scope="session", autouse=True) def spike_probe(request)` — executes SSE cookie auth probe once at session start. Uses module-level `_SPIKE_RESULT_KEY = pytest.StashKey[str]()`; writes result (`"SSE_OK"` or `"SSE_FAIL"`) to `request.config.stash[_SPIKE_RESULT_KEY]`. Assert `hasattr(request.config, 'stash')` in fixture. On probe error/exception: sets `"SSE_FAIL"`. Two consumer tests:
  - `test_sse_paths_wired`: reads `request.config.stash[_SPIKE_RESULT_KEY]`; asserts SSE paths wired if `"SSE_OK"`, REST polling paths if `"SSE_FAIL"`. Runs unconditionally; fails build if neither wired correctly.
  - `test_spike_decision_recorded_in_log`: checks execution log for spike outcome. Operator-visibility only.
  Pin `pytest>=7.0` in test dependencies.
  **No cross-test dependency** — autouse session fixture guarantees single execution before any consumer test.
S2.5: Test: `pytest app/tui/tests/test_debt7_verification.py -v` — `test_sse_paths_wired`, `test_spike_decision_recorded_in_log`

## S3 — Sidebar Panel Wiring (10 sections per P8)

**Preamble**: S3 must not start until S2.5 passes (SSE verified OR polling fallback recorded).
S3.1: Update `app/tui/panels/orchestrator.py` — `/api/orchestrator/status`
S3.2: Update `app/tui/panels/workers.py` — `/api/health` polling
S3.3: Update `app/tui/panels/tasks.py` — SSE `/api/events/tasks` (or 5s polling REST fallback with `since_event_id` cursor per Plan 31 S3.5)
S3.4: Update `app/tui/panels/memory.py` — forward dep: Plan 34 endpoint. Panel shows `PENDING` badge until `/api/orchestrator/memory/graph` returns 200 after Plan 34. Add test asserting PENDING state. Memory panel state: 404→`PENDING` (not implemented); 503 with `error_code=memory_not_ready`→`Loading…` (transient); 200→live.
S3.5: Update `app/tui/panels/models.py` — `/api/models`
S3.6: Update `app/tui/panels/adapters.py` — `/api/health`
S3.7: Update `app/tui/panels/hardware.py` — `/api/health` (hardware metrics)
S3.8: Update `app/tui/panels/logs.py` — SSE `/api/trace/stream` (or 5s polling REST fallback via `GET /api/trace/logs`)
S3.9: Update `app/tui/panels/options.py` — `/api/options/*`
S3.10: Update `app/tui/panels/audit.py` — `/api/messaging/audit` (10th panel)
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
S3.13: Test: `pytest app/tui/tests/test_panels.py -v` — `test_error_terminal_auth_expired`, `test_error_transient_429_respects_retry_after`, `test_error_transient_503_retry_after_60_delays`, `test_error_lockout_no_login_prompt`, `test_sse_overflow_shows_banner`, `test_not_ready_hold_keeps_connection`, `test_truth_table_all_codes`

## S4 — Main Screen Integration

S4.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or polling fallback). Documented v1 limitation: "10-panel polling is a v1 simplification. v2 will consolidate to `/api/dashboard/state`."
S4.3: Error handling: `DEGRADED` badge on `/api/health` subsystem failure; `DISCONNECTED` badge on network failure
S4.4: Shutdown detection with client-side state machine:
  - **States**: `LIFECYCLE_INIT` → `LIFECYCLE_READY` → `LIFECYCLE_SHUTDOWN_DETECTED`
  - **LIFECYCLE_INIT**: on startup, poll `GET /api/lifecycle/ready` every 2s. `ready: false` is **normal** (core still starting) — stay in INIT. On `ready: true` → transition to READY. On 404 or connection failure → stay in INIT (server may not be started yet). First successful poll response establishes the PID/UUID baseline regardless of `ready` value; only subsequent mismatches count as change. PID/UUID change during INIT → stay in INIT (server restarting). Timeout: 120s; if never reached READY, surface error, do NOT exit.
  - **LIFECYCLE_READY**: active monitoring. Sentinel monitoring begins here (after first `ready: true`); on PID/UUID change, update monitored sentinel path. Transitions to SHUTDOWN_DETECTED if: (a) SSE `lifecycle.shutting_down` received; (b) `ready: false` received AND previously saw `ready: true` (true→false transition); (c) HTTP 404; (d) PID changes from previous poll; (e) UUID changes from previous poll.
  - **LIFECYCLE_SHUTDOWN_DETECTED**: set `shutting_down = True`, cancel active retries, attempt `POST /api/auth/logout` (5s timeout, best-effort — 503/timeout during drain is acceptable), close SSE connections, then exit. Graceful drain timeout: 10s max. After 10s: cancel remaining local tasks, persist cookie state, terminate TUI process.
  - **File sentinel fallback**: monitor `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{server_pid}.sentinel"` where `server_pid` from `/api/lifecycle/ready`. Poll interval: 2s. Sentinel content: `{iso8601_utc_timestamp}\n{instance_uuid}\n` (datetime.now(timezone.utc).isoformat()). TUI exits only if PID matches AND UUID matches AND timestamp within 5 minutes. If sentinel file not found during monitoring, log DEBUG and continue polling. **Limitation**: sentinel valid only for same process lifetime; if Web process restarts, old sentinel won't match new UUID.
S4.5: Test: `pytest app/tui/tests/test_main.py -v` — `test_init_stays_on_ready_false`, `test_init_transitions_to_ready_on_ready_true`, `test_init_pid_change_stays_in_init`, `test_ready_true_to_false_triggers_shutdown`, `test_sentinel_match_triggers_shutdown`, `test_sentinel_mismatch_no_shutdown`

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add all new TUI files to TUI_ALLOWED_IMPORTS: `app/tui/client.py`, `app/tui/panels/orchestrator.py`, `app/tui/panels/workers.py`, `app/tui/panels/tasks.py`, `app/tui/panels/memory.py`, `app/tui/panels/models.py`, `app/tui/panels/adapters.py`, `app/tui/panels/hardware.py`, `app/tui/panels/logs.py`, `app/tui/panels/options.py`, `app/tui/panels/audit.py`, `app/tui/main.py`
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`