Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3, DD-31.4, DD-31.5, DD-31.6, DD-31.7, DD-31.8
**Revision**: Rev8

## Executor Manifest

**Plan**: 31
**Phases**: 9 (S0–S9)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/web/schemas.py` + complete DTO inventory | `pytest app/web/tests/test_schemas.py -v` passes |
| S2 | `app/web/sse_broker.py` + SSE endpoint mounting | `pytest app/web/tests/test_sse_broker.py -v` passes |
| S3 | Orchestrator REST + SSE endpoints | `pytest app/web/tests/test_orchestrator_api.py -v` passes |
| S4 | Messaging REST endpoints | `pytest app/web/tests/test_messaging_api.py -v` passes |
| S5 | Auth system (bootstrap, login, logout, lockout) | `pytest app/web/tests/test_auth.py -v` passes |
| S6 | Trace + Lifecycle SSE + REST trace endpoint | `pytest app/web/tests/test_trace_api.py -v` passes |
| S7 | Options + Model Registry endpoint mounting | `pytest app/web/tests/test_options_api.py app/web/tests/test_model_registry_api.py -v` passes |
| S8 | DI composition in `app/web/main.py` | `pytest app/web/tests/test_lifespan.py -v` passes |
| S9 | AR check scripts + document hygiene | `pytest .agent/executor/tests/test_document_hygiene.py -v` passes |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(web): add Web API layer with SSE broker, auth, and DTOs`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Web DTOs

S1.1: Create `app/web/schemas.py` — Pydantic DTOs for all HTTP responses per AR14
S1.2: Complete DTO inventory: `OrchestratorResponse`, `MessageRequest`, `OrchestratorStatus`, `CrossDepartmentMessage`, `AuditPage`, `AuditEntry`, `CircuitStateList`, `HealthSnapshot`, `LoginRequest`, `LoginResponse`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`, `TraceEvent`, `GraphNodeDTO`, `GraphEdgeDTO`, `GraphQueryRequest`, `GraphQueryResponse`, `EpisodicQueryRequest`, `EpisodicQueryResponse`, `EpisodicEventDTO`, `TaskEventDTO`, `LifecycleEventDTO`, `TraceLogRequest`, `TraceLogResponse`, `LifecycleReadyResponse`
S1.3: No core types returned directly; all conversions in `app/sovereignai/web_bridge/converters.py` (core-side bridge)
S1.4: Test: `pytest app/web/tests/test_schemas.py -v`

## S2 — SSE Broker

S2.1: Create `app/web/sse_broker.py` — `SSEBroker` shared utility for Plan 31+ SSE endpoints
S2.2: Handles: auth validation, event subscription, keepalive (30s), reconnection, disconnect cleanup via `request.is_disconnected()`
S2.3: Endpoints mounted on broker: `/api/orchestrator/stream` (orchestrator events), `/api/events/tasks` (task lifecycle), `/api/trace/stream` (TraceEmitter logs), `/api/lifecycle/stream` (lifecycle state), `/api/options/stream` (Plan 28 events), `/api/models/stream` (Plan 29 events)
S2.4: Plans 28/29 SSE integration: Plan 31 owns all SSE endpoint mounting via SSEBroker. Plans 28/29 emit events through EventBus only; Plan 31's SSEBroker subscribes to those events and streams them. No SSE endpoint code in Plans 28/29. **Precondition**: before S2, verify Plans 28/29 have no active SSE route registrations; if present, remove them before SSEBroker mounts. Add AR check `check_sse_mounting_ownership.py`.
S2.5: SSE not_ready: if core service not initialized, broker emits `event: not_ready` and holds connection until ready or timeout (30s). On timeout: close connection with `event: not_ready_timeout`. Client behavior: attempt-terminal (retry up to 3 times with 5s delay); if all attempts timeout, surface 'Server still initializing' and require manual restart. Do not auto-reconnect indefinitely.
S2.6: SSE wire contract: all endpoints emit `id:` field (monotonic counter). On reconnect with `Last-Event-ID` header, replay missed events from buffer (max 100 events per endpoint). Slow clients: backpressure via client-ack required within 30s. Event JSON schema per endpoint documented in test assertions.
S2.7: Auth during streaming: session validated at connection establishment. Mid-stream expiry detected by periodic session-check every 30s. On expiry: emit `event: auth_expired`, flush, close. Initial connect with invalid/expired cookie → HTTP 401 immediately, connection closed.
S2.8: Test: `pytest app/web/tests/test_sse_broker.py -v`

## S3 — Orchestrator Endpoints

S3.1: POST `/api/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse`. Supports `Idempotency-Key: UUID4` header; server stores `(user_session_id, idempotency_key, endpoint_path, payload_hash, status_code, response_body, content_type, stored_at)` in audit DB SQLite with 5-min TTL. Retries with same key, same session, same payload return cached response (identical status + body). Same key + different payload_hash → HTTP 409 Conflict (do not execute second request). Cross-user replay prevented by session_id scoping.
S3.2: GET `/api/orchestrator/status` — returns `OrchestratorStatus`
S3.3: SSE `/api/orchestrator/stream` — mounts on `SSEBroker`, emits `orchestrator.response.ready` and `orchestrator.clarification_needed`
S3.4: SSE `/api/events/tasks` — mounts on `SSEBroker`, emits `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted`
S3.5: Test: `pytest app/web/tests/test_orchestrator_api.py -v`

## S4 — Messaging Endpoints

S4.1: POST `/api/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S4.2: GET `/api/messaging/audit` — paginated audit log, max page size 1000, returns `AuditPage`
S4.3: GET `/api/messaging/circuits` — returns `CircuitStateList`
S4.4: Test: `pytest app/web/tests/test_messaging_api.py -v`

## S5 — Auth & SSE

S5.1: POST `/api/auth/login` — accepts `LoginRequest`, returns `LoginResponse` with session cookie; cookie attrs: `HttpOnly`, `Secure` (HTTPS only; omit for localhost HTTP via scheme check), `SameSite=Strict`, max-age 24h.
  - **Bootstrap**: On first run (no `users.json`), server generates a cryptographically random setup token (32 bytes, base64-encoded) and prints it to stderr only. The token is single-use and expires after first successful login or 24h. First login request must include the setup token in `LoginRequest.setup_token`. Without a valid token, login returns 403. This proves shell access and eliminates network race for admin creation. **Warning**: do not pipe stderr to shared logs during bootstrap.
  - **Credential store**: `platformdirs.user_config_dir("sovereignai") / "users.json"` (hashed bcrypt, cost factor 14). Atomic write with restrictive mode: `open(path, 'wb', opener=lambda p, f: os.open(p, f, 0o600))`. Parent directory: `makedirs(parent, mode=0o700, exist_ok=True)`.
  - **Password policy**: min 12 chars, 1 uppercase, 1 digit, 1 special. Server-side enforced.
  - **Rate limit**: per username (regardless of source IP), 5 attempts per 60s window, exponential backoff on consecutive failures (5th → 60s wait, 6th → 5min, etc.). Hard lockout after 20 consecutive failures per username. Consecutive = strictly no success between failures; a single success resets counter to zero. **Lockout applies only when `users.json` exists** — bootstrap phase exempt. Rate limit state stored in SQLite audit DB.
  - **Admin unlock CLI**: `python -m sovereignai.auth.unlock <username>` — resets lockout state. Requires shell access.
S5.2: POST `/api/auth/logout` — invalidates server-side session, clears cookie, returns 204. CSRF protection: requires valid session cookie on logout request.
S5.3: Session cookie auth per AR13; no query-param tokens; SSE endpoints require valid session. Initial connect with invalid/expired cookie → HTTP 401, connection closed.
S5.4: CORS: same-origin only; no wildcard
S5.5: SSE auth expiry: mid-stream expiry detected every 30s; emit `event: auth_expired`, flush, close. TUI treats as terminal — stops retry, surfaces login prompt
S5.6: Error responses include machine-readable error codes: `login_required`, `setup_token_required`, `setup_token_invalid`, `authorization_denied`, `lockout`, `rate_limited`
S5.7: Test: `pytest app/web/tests/test_auth.py -v`

## S6 — Trace & Lifecycle Endpoints

S6.1: SSE `/api/trace/stream` — mounts on `SSEBroker`, streams `TraceEvent` from TraceEmitter
S6.2: SSE `/api/lifecycle/stream` — mounts on `SSEBroker`, streams `LifecycleEventDTO` wrapping `lifecycle.*` events (ready, shutting_down, stopped)
S6.3: REST `GET /api/trace/logs` — paginated trace log retrieval (for TUI polling fallback when SSE unavailable). Returns `TraceLogResponse` with `TraceEvent[]`, max page size 500, supports time-range and event-type filters.
S6.4: Test: `pytest app/web/tests/test_trace_api.py -v`

## S7 — Options & Model Registry Endpoints

S7.1: Mount Plan 28 routes: `/api/options/*` REST endpoints. SSE `/api/options/stream` mounts on SSEBroker; Plan 28 emits options events through EventBus, SSEBroker subscribes and streams.
S7.2: Mount Plan 29 routes: `/api/models/*` REST endpoints. SSE `/api/models/stream` mounts on SSEBroker; Plan 29 emits model events through EventBus, SSEBroker subscribes and streams.
S7.3: `GET /api/health` is NOT registered by Plan 31. Plan 33 S3.6 is the sole registrar.
S7.4: Test: `pytest app/web/tests/test_options_api.py app/web/tests/test_model_registry_api.py -v`

## S8 — DI Composition

S8.1: `app/web/main.py` composes all services via DIContainer; no hardcoded names per AR4
S8.2: Lifespan context: startup wires Web-only services (auth, SSEBroker); core services initialized by Plan 33 lifecycle manager
S8.3: Separate process per AR12; imports from `app/sovereignai/` only via public API surface
S8.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S9 — AR Checks

S9.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S9.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs, no core types
S9.3: Add `check_auth_bootstrap.py` — verify setup token required for first login, token expires after use, auto-provisioning disabled
S9.4: Add `check_idempotency_scope.py` — verify cache key includes session_id and payload_hash; verify same key + different payload returns 409
S9.5: Add `check_sse_mounting_ownership.py` — verify no SSE routes registered outside SSEBroker
S9.6: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`