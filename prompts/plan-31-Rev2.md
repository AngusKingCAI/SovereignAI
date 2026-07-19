Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3, DD-31.4, DD-31.5, DD-31.6
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Web DTOs

S1.1: Create `app/web/schemas.py` — Pydantic DTOs for all HTTP responses per AR14
S1.2: Complete DTO inventory: `OrchestratorResponse`, `MessageRequest`, `OrchestratorStatus`, `CrossDepartmentMessage`, `AuditPage`, `CircuitStateList`, `HealthSnapshot`, `LoginRequest`, `LoginResponse`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`
S1.3: No core types returned directly; all responses wrapped in DTOs with `to_core()` / `from_core()` methods in `app/sovereignai/web_bridge/converters.py` (core-side bridge, not in `app/web/`)
S1.4: Test: `pytest app/web/tests/test_schemas.py -v`

## S2 — SSE Broker

S2.1: Create `app/web/sse_broker.py` — `SSEBroker` shared utility for all SSE endpoints
S2.2: Handles: auth validation, event subscription, keepalive (30s), reconnection, client disconnect cleanup via `request.is_disconnected()` polling
S2.3: Domain-specific endpoints mount on broker: `/api/orchestrator/stream` (orchestrator events), `/api/options/stream` (Plan 28), `/api/models/stream` (Plan 29), `/api/trace/stream` (TraceEmitter logs)
S2.4: Test: `pytest app/web/tests/test_sse_broker.py -v`

## S3 — Orchestrator Endpoints

S3.1: POST `/api/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse`; idempotency key optional (v2 scope)
S3.2: GET `/api/orchestrator/status` — returns `OrchestratorStatus` (active session, current department, pending clarifications)
S3.3: SSE `/api/orchestrator/stream` — mounts on `SSEBroker`, emits `orchestrator.response.ready` and `orchestrator.clarification_needed`
S3.4: Test: `pytest app/web/tests/test_orchestrator_api.py -v`

## S4 — Messaging Endpoints

S4.1: POST `/api/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S4.2: GET `/api/messaging/audit` — paginated audit log from `messaging_audit.db`, max page size 1000, redacted per Plan 27 S4.1
S4.3: GET `/api/messaging/circuits` — returns `CircuitStateList`
S4.4: Test: `pytest app/web/tests/test_messaging_api.py -v`

## S5 — Auth & SSE

S5.1: POST `/api/auth/login` — accepts `LoginRequest`, returns `LoginResponse` with session cookie; cookie attrs: `HttpOnly`, `Secure`, `SameSite=Strict`, max-age 24h
S5.2: Session cookie auth per AR13; no query-param tokens; SSE endpoints require valid session; 401 on missing/invalid cookie
S5.3: CORS: same-origin only (TUI runs on same origin as web server per P8); no wildcard
S5.4: SSE auth expiry: server sends `event: auth_expired` before closing connection; client re-authenticates and reconnects
S5.5: Test: `pytest app/web/tests/test_auth.py -v`

## S6 — Options & Model Registry Endpoints

S6.1: Mount Plan 28 routes: `/api/options/*` and `/api/options/stream` via `SSEBroker`
S6.2: Mount Plan 29 routes: `/api/models/*` and `/api/models/stream` via `SSEBroker`
S6.3: `GET /api/health` — stub returns 503 `{"status": "health_backend_not_initialized"}` until Plan 33 registers `HealthAggregator`
S6.4: Test: `pytest app/web/tests/test_options_api.py test_model_registry_api.py -v`

## S7 — DI Composition

S7.1: `app/web/main.py` composes all services via DIContainer; no hardcoded names per AR4
S7.2: Lifespan context: startup wires Web-only services (auth, SSEBroker); core services (Orchestrator, Messaging, Options, ModelRegistry) initialized by Plan 33 lifecycle manager, not web lifespan
S7.3: Separate process per AR12; imports from `app/sovereignai/` only via public API surface
S7.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S8 — AR Checks

S8.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S8.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs, no core types
S8.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
