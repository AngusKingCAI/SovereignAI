Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3
**Revision**: Rev1

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Web DTOs

S1.1: Create `app/web/schemas.py` — Pydantic DTOs for all HTTP responses per AR14
S1.2: DTOs: `OrchestratorResponse`, `MessageRequest`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`
S1.3: No core types returned directly; all responses wrapped in DTOs with `to_core()` / `from_core()` methods
S1.4: Test: `pytest app/web/tests/test_schemas.py -v`

## S2 — Orchestrator Endpoints

S2.1: POST `/api/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse`
S2.2: GET `/api/orchestrator/status` — returns active session, current department, pending clarifications
S2.3: SSE `/api/orchestrator/stream` — streams `orchestrator.response.ready` and `orchestrator.clarification_needed` events per AR13
S2.4: Test: `pytest app/web/tests/test_orchestrator_api.py -v`

## S3 — Messaging Endpoints

S3.1: POST `/api/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S3.2: GET `/api/messaging/audit` — paginated audit log from `messaging_audit.db`, redacted per Plan 27 S4.1
S3.3: GET `/api/messaging/circuits` — returns open circuit breakers
S3.4: Test: `pytest app/web/tests/test_messaging_api.py -v`

## S4 — Options & Model Registry Endpoints

S4.1: Mount Plan 28 routes: `/api/options/*` and `/api/options/stream`
S4.2: Mount Plan 29 routes: `/api/models/*` and `/api/models/stream`
S4.3: Unified health check: GET `/api/health` — aggregates Orchestrator, Messaging, Options, ModelRegistry status
S4.4: Test: `pytest app/web/tests/test_options_api.py test_model_registry_api.py -v`

## S5 — Auth & SSE

S5.1: Session cookie auth per AR13; no query-param tokens
S5.2: SSE endpoints require valid session; 401 on missing/invalid cookie
S5.3: CORS: same-origin only; no wildcard
S5.4: Test: `pytest app/web/tests/test_auth.py -v`

## S6 — DI Composition

S6.1: `app/web/main.py` composes all services via DIContainer; no hardcoded names per AR4
S6.2: Lifespan context: startup wires Orchestrator + Messaging + Options + ModelRegistry; shutdown graceful
S6.3: Separate process per AR12; imports from `app/sovereignai/` only via public API surface
S6.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S7 — AR Checks

S7.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S7.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs, no core types
S7.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
