Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3, DD-32.4, DD-32.5
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — TUI Web Client

S1.1: Create `app/tui/client.py` — `TUIWebClient` wraps httpx.AsyncClient
S1.2: Session cookie jar: stores cookie using `platformdirs` at `~/.cache/sovereignai/cookie` (0700 dir, 0600 file); NOT in repo directory
S1.3: Base URL from `SOVEREIGNAI_API_URL` env var or default `http://localhost:8000`
S1.4: Test: `pytest app/tui/tests/test_client.py -v`

## S2 — DEBT-7 Verification Spike

S2.1: Before any panel wiring, verify: textual + httpx can attach `Cookie` header to SSE requests in the actual runtime
S2.2: If verification fails: defer S3.3 (tasks SSE) and S3.8 (logs SSE) to v2; ship polling-based fallback (5s poll for tasks, 5s poll for logs)
S2.3: If verification succeeds: proceed with SSE panels; document verification evidence in execution log
S2.4: Test: `pytest app/tui/tests/test_debt7_verification.py -v` — asserts SSE+cookie works or skips with clear reason

## S3 — Sidebar Panel Wiring (10 sections per P8)

S3.1: Update `app/tui/panels/orchestrator.py` — displays active session, current department, pending clarifications via `/api/orchestrator/status`
S3.2: Update `app/tui/panels/workers.py` — displays worker status via `/api/health` polling
S3.3: Update `app/tui/panels/tasks.py` — displays task stream via SSE `/api/orchestrator/stream` (or 5s polling fallback if DEBT-7 blocked)
S3.4: Update `app/tui/panels/memory.py` — displays memory stats via `/api/orchestrator/memory/graph` (Plan 34)
S3.5: Update `app/tui/panels/models.py` — displays model registry via `/api/models`
S3.6: Update `app/tui/panels/adapters.py` — displays adapter health via `/api/health`
S3.7: Update `app/tui/panels/hardware.py` — displays hardware via `/api/health` (hardware metrics included) or `/api/hardware` if Plan 31 adds it; no direct probe access
S3.8: Update `app/tui/panels/logs.py` — displays TraceEmitter logs via SSE `/api/trace/stream` (or 5s polling fallback if DEBT-7 blocked)
S3.9: Update `app/tui/panels/options.py` — displays/edits settings via `/api/options/*`
S3.10: Update `app/tui/panels/audit.py` — displays messaging audit log via `/api/messaging/audit` (10th panel per P8)
S3.11: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S3.12: Error handling: 5s timeout on all HTTP calls; show `DISCONNECTED` badge if endpoint unavailable; retry with exponential backoff
S3.13: Test: `pytest app/tui/tests/test_panels.py -v`

## S4 — Main Screen Integration

S4.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S4.2: Auto-refresh: 5s polling for status panels, SSE for stream panels (or polling fallback)
S4.3: Error handling: panel shows `DEGRADED` badge on any `/api/health` sub-system failure; `DISCONNECTED` badge on network failure
S4.4: Test: `pytest app/tui/tests/test_main.py -v`

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add `app/tui/client.py`, `app/tui/panels/audit.py` to TUI_ALLOWED_IMPORTS
S5.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
