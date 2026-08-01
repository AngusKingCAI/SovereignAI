Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
Optional forward dependency: Plan 34 — memory panel renders live graph only after Plan 34; shows PENDING until then.
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5, DD-32.6, DD-32.7
**Revision**: Rev9

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
S1.2: Cookie jar: `platformdirs.user_cache_dir("sovereignai") / "cookie"`. Atomic write, `0o600` permissions. Windows: document ACL limitation.
S1.3: Base URL from `SOVEREIGNAI_API_URL` or default `http://localhost:8000`
S1.4: Test: `pytest app/tui/tests/test_client.py -v`

## S2 — DEBT-7 Verification Spike

S2.1: Integration test — start test HTTP server with SSE endpoint requiring `Cookie` header. Use textual `App.run_test()` to connect with session cookie.
S2.2: If verification fails: defer SSE panels; ship 5s polling fallback.
S2.3: If verification succeeds: proceed with SSE panels; document in execution log.
S2.4: **Two tests** (both in `test_debt7_verification.py`):
  - `test_sse_cookie_auth`: asserts cookie sent + SSE events received within 5s. **xfail** if textual/httpx cannot attach Cookie to SSE — captures runtime evidence. Exit 0 if xfailed.
  - `test_polling_fallback_wired`: runs unconditionally. Asserts: (a) if `test_sse_cookie_auth` passed, SSE paths wired in tasks.py/logs.py; (b) if xfailed, REST polling paths wired (5s poll to `/api/events/tasks` REST + `GET /api/trace/logs`). **Fails build** if neither SSE nor polling path is correctly wired.
  Executor MUST record which path is active in execution log. Round table reviews log.
S2.5: Test: `pytest app/tui/tests/test_debt7_verification.py -v`

## S3 — Sidebar Panel Wiring (10 sections per P8)

**Preamble**: S3 blocked until S2.5 passes.
S3.1: `orchestrator.py` — `/api/orchestrator/status`
S3.2: `workers.py` — `/api/health` polling
S3.3: `tasks.py` — SSE `/api/events/tasks` (or 5s polling REST fallback via `GET /api/events/tasks`)
S3.4: `memory.py` — forward dep on Plan 34. During Plan 32 execution: shows `PENDING` badge, no graph rendering. After Plan 34 returns 200 on `/api/orchestrator/memory/graph`: renders entity/relation graph. Test: mock memory endpoint → 404, assert PENDING badge text displayed.
S3.5: `models.py` — `/api/models`
S3.6: `adapters.py` — `/api/health`
S3.7: `hardware.py` — `/api/health` (hardware metrics)
S3.8: `logs.py` — SSE `/api/trace/stream` (or 5s polling fallback via `GET /api/trace/logs`)
S3.9: `options.py` — `/api/options/*`
S3.10: `audit.py` — `/api/messaging/audit` (10th panel)
S3.11: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S3.12: Error handling truth table:
  - **Terminal** (stop retry, surface login prompt): `auth_expired`, `not_ready_timeout`, 401, 403, 4xx (except 429)
  - **Transient** (retry with exponential backoff base 1s, max 30s, jitter ±50%): 429, 5xx, network errors
  - **Operator** (surface with retry button): 501
  5s timeout on all HTTP calls; `DISCONNECTED` badge on network failure.
S3.13: Test: `pytest app/tui/tests/test_panels.py -v`

## S4 — Main Screen Integration

S4.1: `app/tui/main.py` — compose 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or fallback). v1 limitation documented.
S4.3: `DEGRADED` badge on `/api/health` subsystem failure; `DISCONNECTED` on network failure.
S4.4: Shutdown detection — **client-side state machine**:
  - **LIFECYCLE_INIT**: TUI launched, not yet seen `ready: true`. Poll `GET /api/lifecycle/ready` (unauthenticated) every 5s. `ready: false` → normal startup wait, do NOT exit. Obtain `server_pid` and `instance_uuid` from first response (always present per Plan 33 S3.7).
  - **LIFECYCLE_READY**: seen at least one `ready: true`. Transition to SHUTDOWN_DETECTED if: `ready: false`, 404, PID changes, or UUID changes.
  - **SHUTDOWN_DETECTED**: set `shutting_down = True`, cancel retries, attempt `POST /api/auth/logout` (5s timeout), close SSE, exit within 10s.
  - Primary: SSE `/api/lifecycle/stream` for `lifecycle.shutting_down`. Fallback: poll above. File sentinel: monitor `shutdown.{server_pid}.sentinel` (poll 2s). Exit only if PID + UUID + timestamp (<5min) all match.
S4.5: Test: `pytest app/tui/tests/test_main.py -v` — test each state transition (INIT→READY, READY→SHUTDOWN, INIT timeout graceful)

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add all new TUI files to TUI_ALLOWED_IMPORTS: `client.py`, `panels/{orchestrator,workers,tasks,memory,models,adapters,hardware,logs,options,audit}.py`, `main.py`
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
