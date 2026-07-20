Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3, DD-31.4, DD-31.5, DD-31.6, DD-31.7, DD-31.8
**Revision**: Rev9

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
| S6 | Trace + Lifecycle SSE + REST trace + REST tasks endpoints | `pytest app/web/tests/test_trace_api.py -v` passes |
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
S1.2: Complete DTO inventory (authoritative list — all plans MUST use these names): `OrchestratorResponse`, `MessageRequest`, `OrchestratorStatus`, `CrossDepartmentMessage`, `AuditPage`, `AuditEntry`, `CircuitStateList`, `HealthSnapshot`, `LoginRequest`, `LoginResponse`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`, `TraceEvent`, `GraphEntityDTO`, `GraphRelationDTO`, `GraphQueryRequest`, `GraphQueryResponse`, `EpisodicQueryRequest`, `EpisodicQueryResponse`, `EpisodicEventDTO`, `TaskEventDTO`, `LifecycleEventDTO`, `TraceLogRequest`, `TraceLogResponse`, `LifecycleReadyResponse`, `TaskListResponse`, `MergeConflictDTO`. No core types returned directly.
S1.3: Conversions in `app/sovereignai/web_bridge/converters.py`. `web_bridge/` is canonical import surface from `app/web/` into `app/sovereignai/`. Update M3 ALLOWLIST with `app/sovereignai/web_bridge/__init__.py` and `converters.py`.
S1.4: Test: `pytest app/web/tests/test_schemas.py -v`

## S2 — SSE Broker

S2.1: Create `app/web/sse_broker.py` — `SSEBroker`
S2.2: Per-connection bounded queue (max 100 events). On queue overflow: drop oldest, emit `event: overflow, data: {"dropped": N}`. Client detects gaps via `id:` monotonicity. No client-ack required (standard SSE is unidirectional).
S2.3: Keepalive: emit `:` comment every 15s of inactivity (no events). Auth: session validated at connect; mid-stream expiry check every 30s → emit `event: auth_expired`, flush, close. Invalid cookie at connect → HTTP 401.
S2.4: Endpoints: `/api/orchestrator/stream`, `/api/events/tasks`, `/api/trace/stream`, `/api/lifecycle/stream`, `/api/options/stream`, `/api/models/stream`. Plans 28/29 emit via EventBus; SSEBroker subscribes and streams. Precondition: verify Plans 28/29 have no SSE routes; remove if present. AR check `check_sse_mounting_ownership.py`.
S2.5: Not-ready: if core not initialized, emit `event: not_ready`, hold ≤30s, then `event: not_ready_timeout` and close. Server-side behavior only. Client retry policy is defined in Plan 32 S3.12 (terminal classification).
S2.6: Wire contract: `id:` = per-endpoint monotonic counter (non-persistent, resets on restart). `Last-Event-ID` header: replay from in-memory buffer (max 100). If `Last-Event-ID` predates buffer: emit `event: replay_unavailable` with current `id`, client must resync.
S2.7: Test: `pytest app/web/tests/test_sse_broker.py -v`

## S3 — Orchestrator Endpoints

S3.1: POST `/api/orchestrator/message` — `MessageRequest` → `OrchestratorResponse`. `Idempotency-Key: UUID4` header. Cache: `(session_id, key, path, payload_hash, response_json, status, stored_at)` in audit DB (see S5.1a). TTL 5min per `stored_at`. Same key + same payload + same session → cached. Same key + different payload → HTTP 409 `{"error_code": "idempotency_conflict", "message": "Key reused with different payload"}`. Cross-user replay prevented by session_id.
S3.2: GET `/api/orchestrator/status` — `OrchestratorStatus`
S3.3: SSE `/api/orchestrator/stream` — on SSEBroker
S3.4: **REST** `GET /api/events/tasks` — paginated task list (for TUI polling fallback). Returns `TaskListResponse(TaskEventDTO[], total_count, page, page_size)`. Max page 500. Filters: event_type, task_id. Auth: session cookie. This is the REST fallback for Plan 32 S3.3 when SSE unavailable.
S3.5: Test: `pytest app/web/tests/test_orchestrator_api.py -v`

## S4 — Messaging Endpoints

S4.1: POST `/api/messaging/send` — `CrossDepartmentMessage` DTO → InterDepartmentBus
S4.2: GET `/api/messaging/audit` — paginated, max 1000/page, `AuditPage`
S4.3: GET `/api/messaging/circuits` — `CircuitStateList`
S4.4: Test: `pytest app/web/tests/test_messaging_api.py -v`

## S5 — Auth

S5.1: POST `/api/auth/login` → `LoginResponse` + session cookie. Cookie: `HttpOnly`, `SameSite=Strict`, max-age 24h. **`Secure` flag**: enabled only when request scheme is `https` **AND** `Host` header matches loopback allowlist (`localhost`, `127.0.0.1`, `[::1]`) OR is explicitly HTTPS. If scheme is `http` and Host is NOT in loopback allowlist: refuse login with HTTP 500 + `error_code: "insecure_deployment"`. Document: "HTTP sessions restricted to loopback; non-loopback HTTP is a configuration error."
  - **Bootstrap**: first run (no `users.json`) → generate 32-byte token (`secrets.token_urlsafe(32)`), print to stderr, store hashed in audit DB (bcrypt cost 14). Single-use, expires 24h. First login requires `LoginRequest.setup_token`. Audit logs token generation timestamp (not the token). Token deleted after use.
  - **Credential store**: `platformdirs.user_config_dir("sovereignai") / "users.json"` (bcrypt, 0o600).
  - **Password policy**: min 12 chars, 1 uppercase, 1 digit, 1 special.
  - **Rate limit**: per username (regardless of IP), 5 attempts per 60s sliding window + exponential backoff on consecutive failures. **Backoff formula**: 5th failure → 60s wait; 6th → 5min; Nth (N≥5) → `min(86400, 60 × 2^(N-5))` seconds. Backoff is independent of sliding window — both rules apply: window caps frequency, backoff adds penalty. Hard lockout after 20 consecutive failures. Lockout only when `users.json` exists.
  - **Unlock CLI**: `python -m sovereignai.auth.unlock <username>` (shell access required).
S5.1a: **Audit DB**: single SQLite file at `platformdirs.user_data_dir("sovereignai") / "audit.db"` (0o600). Stores rate-limit table + idempotency cache. Rate-limit schema: `(username TEXT PK, attempt_count INT, window_start TEXT, lockout_until TEXT)`. **Cleanup**: lazy — on each login check, if `window_start` >60s old, reset counter. If `lockout_until` in past, clear it. Idempotency: lazy delete on cache hit where `stored_at` >5min.
S5.2: POST `/api/auth/logout` — invalidate session, clear cookie, 204. CSRF: requires valid session.
S5.3: Session cookie per AR13; SSE endpoints require valid session. **Auth exemption**: `GET /api/lifecycle/ready` is unauthenticated (cross-process readiness probe, Plan 33 S3.7).
S5.4: CORS: same-origin only
S5.5: Mid-stream auth expiry → `event: auth_expired` → close. TUI treats as terminal.
S5.6: **Error envelope**: all `/api/auth/*` errors: `{"error_code": "<code>", "message": "<human>", "retry_after_seconds": <int|null>}`. Status mapping: `login_required`→401, `setup_token_required/invalid/authorization_denied`→403, `lockout`→423, `rate_limited`→429 + `Retry-After` header, `insecure_deployment`→500.
S5.7: Test: `pytest app/web/tests/test_auth.py -v`

## S6 — Trace & Lifecycle Endpoints

S6.1: SSE `/api/trace/stream` — on SSEBroker
S6.2: SSE `/api/lifecycle/stream` — on SSEBroker
S6.3: REST `GET /api/trace/logs` — paginated (max 500/page), time-range + event-type filters. `TraceLogResponse`
S6.4: Test: `pytest app/web/tests/test_trace_api.py -v`

## S7 — Options & Model Registry

S7.1: Mount Plan 28 `/api/options/*` REST. SSE `/api/options/stream` on SSEBroker.
S7.2: Mount Plan 29 `/api/models/*` REST. SSE `/api/models/stream` on SSEBroker.
S7.3: `GET /api/health` NOT registered by Plan 31. Plan 33 S3.6 is sole registrar.
S7.4: Test: `pytest app/web/tests/test_options_api.py app/web/tests/test_model_registry_api.py -v`

## S8 — DI Composition

S8.1: `app/web/main.py` — compose via DIContainer; no hardcoded names per AR4
S8.2: Lifespan: wires Web-only services (auth, SSEBroker); core services by Plan 33
S8.3: Separate process per AR12; imports from `app/sovereignai/` only via `web_bridge/` public surface
S8.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S9 — AR Checks

S9.1: `check_web_no_core_imports.py` — `app/web/` only via `web_bridge` public API
S9.2: `check_web_dto_completeness.py` — all endpoints return DTOs, scan `/api/health` too
S9.3: `check_auth_bootstrap.py` — setup token required, expires after use, no auto-provision
S9.4: `check_idempotency_scope.py` — cache key includes session_id + payload_hash; 409 on key+payload mismatch
S9.5: `check_sse_mounting_ownership.py` — no SSE routes outside SSEBroker
S9.6: `check_auth_error_codes.py` — all `/api/auth/*` errors include JSON `error_code` from canonical set
S9.7: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
