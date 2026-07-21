Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5, DD-32.6, DD-32.7
**Revision**: Rev8

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
S1.2: Session cookie jar: stores cookie using `platformdirs` at `platformdirs.user_cache_dir("sovereignai") / "cookie"`. Atomic write with restrictive mode: `open(path, 'wb', opener=lambda p, f: os.open(p, f, 0o600))`. Parent directory: `makedirs(parent, mode=0o700, exist_ok=True)`. Windows: document ACL limitation.
S1.3: Base URL from `SOVEREIGNAI_API_URL` env var or default `http://localhost:8000`
S1.4: Test: `pytest app/tui/tests/test_client.py -v`

## S2 — DEBT-7 Verification Spike

S2.1: Integration test — start test HTTP server with SSE endpoint requiring `Cookie` header. Use textual `App.run_test()` to run TUI app connecting to SSE endpoint with session cookie. Assert cookie is sent and SSE events received.
S2.2: If verification fails: defer S3.3 (tasks SSE) and S3.8 (logs SSE) to v2; ship polling-based fallback (5s poll for tasks via `/api/events/tasks` REST, 5s poll for logs via `GET /api/trace/logs`).
S2.3: If verification succeeds: proceed with SSE panels; document verification evidence in execution log
S2.4: Test: `pytest app/tui/tests/test_debt7_verification.py -v` — mandatory, must run (not skip). Test asserts the fallback path is correctly wired when SSE fails, or SSE works — test always passes, documents pass/fail result.

## S3 — Sidebar Panel Wiring (10 sections per P8)

**Preamble**: S3 must not start until S2.4 passes (SSE-with-cookie auth verified OR polling fallback decision recorded).
S3.1: Update `app/tui/panels/orchestrator.py` — `/api/orchestrator/status`
S3.2: Update `app/tui/panels/workers.py` — `/api/health` polling
S3.3: Update `app/tui/panels/tasks.py` — SSE `/api/events/tasks` (or 5s polling fallback via REST)
S3.4: Update `app/tui/panels/memory.py` — forward dependency: Plan 34 endpoint. During Plan 32 execution, panel shows `PENDING` badge. Once `/api/orchestrator/memory/graph` returns 200 after Plan 34 execution, panel renders entity/relation graph. Add test asserting PENDING state.
S3.5: Update `app/tui/panels/models.py` — `/api/models`
S3.6: Update `app/tui/panels/adapters.py` — `/api/health`
S3.7: Update `app/tui/panels/hardware.py` — `/api/health` (hardware metrics in health payload)
S3.8: Update `app/tui/panels/logs.py` — SSE `/api/trace/stream` (or 5s polling fallback via `GET /api/trace/logs`)
S3.9: Update `app/tui/panels/options.py` — `/api/options/*`
S3.10: Update `app/tui/panels/audit.py` — `/api/messaging/audit` (10th panel)
S3.11: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S3.12: Error handling: 5s timeout on all HTTP calls; show `DISCONNECTED` badge if endpoint unavailable; retry with exponential backoff (base 1s, multiplier 2, max 30s, jitter ±50%). Error classification flat rule: **Terminal** = `auth_expired`, `not_ready_timeout`, 401, 403, 4xx (except 429); **Transient** = 429, 5xx, network errors; **Operator** = 501 → surface with retry button. Terminal errors stop retry, surface login prompt. Truth-table test covers all status codes.
S3.13: Test: `pytest app/tui/tests/test_panels.py -v`

## S4 — Main Screen Integration

S4.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or polling fallback). Documented v1 limitation: "10-panel polling is a v1 simplification. v2 will consolidate to `/api/dashboard/state`."
S4.3: Error handling: `DEGRADED` badge on `/api/health` sub-system failure; `DISCONNECTED` badge on network failure
S4.4: Shutdown detection:
  - Primary: monitor SSE `/api/lifecycle/stream` for `lifecycle.shutting_down`.
  - Fallback: poll `GET /api/lifecycle/ready` every 5s; response returns `{ready: bool, server_pid: int}`. If `ready: false` or 404, exit client-side.
  - File sentinel: monitor `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{server_pid}.sentinel"` where `server_pid` from `/api/lifecycle/ready`. Poll interval: 2s. Sentinel content: `timestamp\n{instance_uuid}\n` where timestamp is `datetime.now(timezone.utc).isoformat()` (UTC offset included). TUI parses with `datetime.fromisoformat()`, compares to `datetime.now(timezone.utc)`. TUI exits only if PID matches AND UUID matches AND timestamp within 5 minutes.
  - On sentinel match: set `shutting_down = True`, cancel active retries, attempt `POST /api/auth/logout` (5s timeout), close SSE connections, then exit. Graceful drain timeout: 10s max.
S4.5: Test: `pytest app/tui/tests/test_main.py -v`

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add all new TUI files to TUI_ALLOWED_IMPORTS: `app/tui/client.py`, `app/tui/panels/orchestrator.py`, `app/tui/panels/workers.py`, `app/tui/panels/tasks.py`, `app/tui/panels/memory.py`, `app/tui/panels/models.py`, `app/tui/panels/adapters.py`, `app/tui/panels/hardware.py`, `app/tui/panels/logs.py`, `app/tui/panels/options.py`, `app/tui/panels/audit.py`, `app/tui/main.py`
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`