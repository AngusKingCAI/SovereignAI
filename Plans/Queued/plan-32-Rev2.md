Depends on: Plan 31 (Web API), Plan 26 (Orchestrator), Plan 28 (Options)
Vision principles: P8 (UIs are separate processes, 10-section sidebar), P11 (Quality), P13 (Strong and robust)
AR rules: AR7, AR12
OR rules: UOR-1, UOR-2
Open questions resolved: DD-32.1, DD-32.2, DD-32.3
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — TUI Web Client

S1.1: Create `app/tui/client.py` — `TUIWebClient` wraps httpx.AsyncClient with typed interface
S1.2: Session cookie jar: reads cookie from `app/tui/.session/cookie` (0700 dir, 0600 file)
S1.3: Cookie storage encryption: encrypt cookie content at rest using platform keyring or file-based encryption
S1.4: Cookie validation: validate cookie format and integrity on read before use in httpx requests
S1.5: Base URL from `SOVEREIGNAI_API_URL` env var or default `http://localhost:8000`
S1.6: Client configuration: connection timeout 5s, read timeout 30s, long-lived session per TUI process
S1.7: Typed endpoint methods: separate methods for each API endpoint with proper error translation
S1.8: Test: `pytest app/tui/tests/test_client.py -v`

## S2 — Sidebar Panel Wiring

S2.1: Update `app/tui/panels/orchestrator.py` — displays active session, current department, pending clarifications
S2.2: Update `app/tui/panels/workers.py` — displays worker status via `/api/v1/health` polling
S2.3: Update `app/tui/panels/tasks.py` — displays task stream via SSE `/api/v1/orchestrator/stream` with reconnection
S2.4: Update `app/tui/panels/memory.py` — displays memory stats via `/api/v1/options` (memory retention settings)
S2.5: Update `app/tui/panels/models.py` — displays model registry via `/api/v1/models`
S2.6: Update `app/tui/panels/adapters.py` — displays adapter health via `/api/v1/health`
S2.7: Update `app/tui/panels/hardware.py` — displays hardware via existing probe (no web dependency)
S2.8: Update `app/tui/panels/logs.py` — displays TraceEmitter logs via dedicated `/api/v1/logs/stream` (new endpoint)
S2.9: Update `app/tui/panels/options.py` — displays/edits settings via `/api/v1/options/*`
S2.10: All panels use `TUIWebClient`; no direct sovereignai.* imports per AR7
S2.11: Error handling granularity: different panels have different failure modes (critical vs informational)
S2.12: Offline/degraded mode: TUI shows clear degraded state when API unavailable
S2.13: Test: `pytest app/tui/tests/test_panels.py -v`

## S3 — Main Screen Integration

S3.1: Update `app/tui/main.py` — compose all 10 sidebar sections per P8
S3.2: Auto-refresh: 5s polling for status panels, SSE for stream panels
S3.3: Error handling: panel shows `DEGRADED` badge on any `/api/v1/health` sub-system failure
S3.4: SSE reconnection strategy: explicit reconnection logic with Last-Event-ID handling on connection drop
S3.5: Hotkey display: show hotkeys inline per TUI best practices for discoverability
S3.6: Test: `pytest app/tui/tests/test_main.py -v`

## S4 — Cookie Auth Resolution (DEBT-7)

S4.1: TUI login flow: POST `/api/v1/auth/login` → store encrypted cookie → all subsequent requests attach cookie
S4.2: Cookie expiration handling: proactive refresh before expiry during SSE streams; reconnection logic on expiration
S4.3: SSE cookie attachment: test with specific TUI library (textual); if Cookie header cannot be set, use httpx client with manual Cookie header
S4.4: 401 error handling: prompt for re-authentication, attempt cookie refresh, show degraded state (no silent retry loops)
S4.5: DEBT-7 resolution criteria: (1) test with textual library, (2) if Cookie header cannot be set, document limitation, (3) create tracking issue for future resolution
S4.6: Fallback: query-param token rejected per AR13; if cookie impossible, document limitation and defer
S4.7: Test: `pytest app/tui/tests/test_auth.py -v`

## S5 — AR Checks

S5.1: Update `test_ar7_no_core_imports_in_ui.py` — add TUI_ALLOWED_IMPORTS for new `app/tui/client.py`
S5.2: Add `check_tui_client_abstraction.py` — verify panels use TUIWebClient, not direct HTTP
S5.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
