Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5, DD-32.6, DD-32.7
**Revision**: Rev6

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

**Governance files**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(tui): add TUI web client, 10-panel sidebar, and shutdown detection`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read `PRINCIPLES.md` in full.
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — TUI Web Client

S1.1: Create `app/tui/client.py` — `TUIWebClient` wraps httpx.AsyncClient
S1.2: Session cookie jar: stores cookie using `platformdirs` at `platformdirs.user_cache_dir("sovereignai") / "cookie"`; on write, call `os.makedirs(path.parent, exist_ok=True)` then `os.chmod(path, 0o600)` (Linux/macOS); Windows: document ACL limitation
S1.3: Base URL from `SOVEREIGNAI_API_URL` env var or default `http://localhost:8000`
S1.4: Test: `pytest app/tui/tests/test_client.py -v`

## S2 — DEBT-7 Verification Spike

S2.1: Before any panel wiring, verify: textual + httpx can attach `Cookie` header to SSE requests in actual runtime
S2.2: If verification fails: defer S3.3 (tasks SSE) and S3.8 (logs SSE) to v2; ship polling-based fallback (5s poll for tasks, 5s poll for logs)
S2.3: If verification succeeds: proceed with SSE panels; document verification evidence in execution log
S2.4: Test: `pytest app/tui/tests/test_debt7_verification.py -v` — mandatory, must run (not skip)

## S3 — Sidebar Panel Wiring (10 sections per P8)

S3.1: Update `app/tui/panels/orchestrator.py` — `/api/orchestrator/status`
S3.2: Update `app/tui/panels/workers.py` — `/api/health` polling
S3.3: Update `app/tui/panels/tasks.py` — SSE `/api/events/tasks` (or 5s polling fallback)
S3.4: Update `app/tui/panels/memory.py` — `/api/orchestrator/memory/graph` (Plan 34)
S3.5: Update `app/tui/panels/models.py` — `/api/models`
S3.6: Update `app/tui/panels/adapters.py` — `/api/health`
S3.7: Update `app/tui/panels/hardware.py` — `/api/health` (hardware metrics in health payload)
S3.8: Update `app/tui/panels/logs.py` — SSE `/api/trace/stream` (or 5s polling fallback)
S3.9: Update `app/tui/panels/options.py` — `/api/options/*`
S3.10: Update `app/tui/panels/audit.py` — `/api/messaging/audit` (10th panel)
S3.11: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S3.12: Error handling: 5s timeout on all HTTP calls; show `DISCONNECTED` badge if endpoint unavailable; retry with exponential backoff (base 1s, multiplier 2, max 30s, jitter ±50%). Terminal errors stop retry and surface login prompt. Error classification: auth_expired/401/403/not_ready_timeout → terminal; 4xx (except 429) → terminal; 5xx → transient; network errors → transient.
S3.13: Test: `pytest app/tui/tests/test_panels.py -v`

## S4 — Main Screen Integration

S4.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or polling fallback). Documented v1 limitation: "10-panel polling is a v1 simplification. v2 will consolidate to `/api/dashboard/state`."
S4.3: Error handling: `DEGRADED` badge on `/api/health` sub-system failure; `DISCONNECTED` badge on network failure
S4.4: Shutdown detection:
  - Primary: monitor SSE `/api/lifecycle/stream` for `lifecycle.shutting_down`.
  - Fallback: poll `/api/lifecycle/ready` every 5s; if 404 or false, exit client-side.
  - File sentinel: monitor `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{server_pid}.sentinel"` where `server_pid` is from `/api/lifecycle/ready` response. Poll interval: 2s. Sentinel content: `timestamp
` where timestamp is ISO 8601 of shutdown initiation. TUI exits only if PID matches AND timestamp is within 5 minutes of current time.
  - On sentinel match: set `shutting_down = True`, cancel active retries, attempt `POST /api/auth/logout` (5s timeout), close SSE connections, then exit. Graceful drain timeout: 10s max.
S4.5: Test: `pytest app/tui/tests/test_main.py -v`

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add `app/tui/client.py`, `app/tui/panels/audit.py` to TUI_ALLOWED_IMPORTS
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
