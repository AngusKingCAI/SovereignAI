Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Web DTOs

S1.1: Create `app/web/schemas.py` — Pydantic DTOs for all HTTP responses per AR14
S1.2: DTOs: `OrchestratorResponse`, `MessageRequest`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`, `ErrorResponse` (new)
S1.3: No core types returned directly; all responses wrapped in DTOs with `to_core()` / `from_core()` methods
S1.4: Add API versioning: prefix all routes with `/api/v1/` for future evolution
S1.5: Specify DTO bidirectional mapping: request DTOs use `from_core()`, response DTOs use `to_core()`
S1.6: Test: `pytest app/web/tests/test_schemas.py -v`

## S2 — Orchestrator Endpoints

S2.1: POST `/api/v1/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse` or `ErrorResponse`
S2.2: GET `/api/v1/orchestrator/status` — returns active session, current department, pending clarifications
S2.3: SSE `/api/v1/orchestrator/stream` — streams `orchestrator.response.ready` and `orchestrator.clarification_needed` events per AR13
S2.4: SSE headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-store`, `X-Content-Type-Options: nosniff`
S2.5: SSE requires `{ withCredentials: true }` for cookie transmission; server sets `Access-Control-Allow-Credentials: true` with specific origin
S2.6: Test: `pytest app/web/tests/test_orchestrator_api.py -v`

## S3 — Messaging Endpoints

S3.1: POST `/api/v1/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S3.2: GET `/api/v1/messaging/audit` — paginated audit log from `messaging_audit.db`, redacted per Plan 27 S4.1
S3.3: GET `/api/v1/messaging/circuits` — returns open circuit breakers
S3.4: Test: `pytest app/web/tests/test_messaging_api.py -v`

## S4 — Options & Model Registry Endpoints

S4.1: Mount Plan 28 routes: `/api/v1/options/*` and `/api/v1/options/stream`
S4.2: Mount Plan 29 routes: `/api/v1/models/*` and `/api/v1/models/stream`
S4.3: Unified health check: GET `/api/v1/health` — aggregates via HealthAggregator facade (Plan 33) rather than direct dependencies
S4.4: Health check response schema: Pydantic DTO shared with Plan 33 to ensure contract consistency
S4.5: Test: `pytest app/web/tests/test_options_api.py test_model_registry_api.py -v`

## S5 — Auth & SSE

S5.1: Session cookie auth per AR13; no query-param tokens
S5.2: Cookie security attributes: `HttpOnly`, `Secure` (conditional for localhost HTTP), `SameSite=Strict`, `Max-Age` configurable
S5.3: Session ID generation: cryptographically secure random with minimum 128 bits entropy
S5.4: Session rotation: rotate session ID after privilege changes per OWASP recommendations
S5.5: SSE endpoints require valid session; 401 on missing/invalid cookie with explicit error handling
S5.6: SSE 401 handling: return error event to client, show degraded state in TUI, no silent retry loops
S5.7: CORS: same-origin only; no wildcard; specific origin for credentials
S5.8: Localhost HTTPS consideration: conditional Secure attribute for development (false for localhost HTTP, true for production)
S5.9: Test: `pytest app/web/tests/test_auth.py -v`

## S6 — DI Composition

S6.1: `app/web/main.py` composes web-layer services via DIContainer; no hardcoded names per AR4
S6.2: Web layer composition limit: ≤15 constructor args per P11; use sub-composers if exceeded
S6.3: Web layer owns in-process service wiring (Orchestrator, Messaging, Options, ModelRegistry) via public API surface only
S6.4: Process lifecycle (startup/shutdown) owned by Plan 33's AgentLifecycleManager, not web layer
S6.5: Lifespan context: startup delegates to Plan 33 lifecycle manager; shutdown graceful via lifecycle coordination
S6.6: Separate process per AR12; imports from `app/sovereignai/` only via public API surface
S6.7: Test: `pytest app/web/tests/test_lifespan.py -v`

## S7 — AR Checks

S7.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S7.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs, no core types
S7.3: Add `check_cookie_security_attributes.py` — verify HttpOnly, Secure, SameSite attributes set correctly
S7.4: Add `check_sse_security_headers.py` — verify SSE security headers present
S7.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
