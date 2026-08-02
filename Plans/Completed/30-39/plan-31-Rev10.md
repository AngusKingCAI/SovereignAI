Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3, DD-31.4, DD-31.5, DD-31.6, DD-31.7, DD-31.8
**Revision**: Rev11

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
S1.2: Complete DTO inventory (authoritative — Plans 32/33/34 MUST use these names): `OrchestratorResponse`, `MessageRequest`, `OrchestratorStatus`, `CrossDepartmentMessage`, `AuditPage`, `AuditEntry`, `CircuitStateList`, `HealthSnapshot`, `LoginRequest`, `LoginResponse`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`, `TraceEvent`, `GraphNodeDTO`, `GraphEdgeDTO`, `GraphQueryRequest`, `GraphQueryResponse`, `EpisodicQueryRequest`, `EpisodicQueryResponse`, `EpisodicEventDTO`, `TaskEventDTO`, `TaskListResponse`, `LifecycleEventDTO`, `TraceLogRequest`, `TraceLogResponse`, `LifecycleReadyResponse`, `MemoryNotReadyResponse`, `MergeConflictDTO`. DTO field definitions:
  - `MergeConflictDTO`: `conflict_id, entity_name, entity_type, canonical_uuid, candidate_uuids: list[str], first_observed_at: str` (ISO 8601), `resolution_status: str` (v1: `"unresolved" | "suppressed_by_dedup"`; no PENDING — no resolution API until future plan).
  - `MemoryNotReadyResponse`: `error_code: "memory_not_ready"`, `message: "Memory subsystem still loading"`, `retry_after_seconds: 5`.
  - `TaskListResponse`: `events: list[TaskEventDTO]`, `total_count: int`, `next_event_id: Optional[int]`, `page_size: int`.
S1.3: No core types returned directly; all conversions in `app/sovereignai/web_bridge/converters.py` (core-side bridge)
S1.4: `check_web_dto_completeness.py` (S9.2) ensures `LoginRequest` never passes core types or unhashed passwords beyond Web boundary.
S1.5: Test: `pytest app/web/tests/test_schemas.py -v` — `test_dto_inventory_complete`, `test_no_core_types_in_schemas`, `test_merge_conflict_dto_fields_valid`, `test_memory_not_ready_response_fields_valid`, `test_task_list_response_fields_valid`

## S2 — SSE Broker

S2.1: Create `app/web/sse_broker.py` — `SSEBroker` shared utility for Plan 31+ SSE endpoints
S2.2: Per-connection bounded queue: max 100 events. Auth validation, event subscription, keepalive (30s), reconnection, disconnect via `request.is_disconnected()`.
S2.3: Endpoints mounted on broker: `/api/orchestrator/stream` (orchestrator events), `/api/events/tasks` (task lifecycle; SSE vs REST discriminated by `Accept: text/event-stream`, absent→REST per S3.5), `/api/trace/stream` (TraceEmitter logs), `/api/lifecycle/stream` (lifecycle state), `/api/options/stream` (Plan 28 events), `/api/models/stream` (Plan 29 events)
S2.4: Plans 28/29 SSE: Plan 31 owns all mounting via SSEBroker. Plans 28/29 emit via EventBus only; SSEBroker subscribes. **Precondition**: verify Plans 28/29 have no active SSE routes; if present, remove before mounting. AR check `check_sse_mounting_ownership.py`.
S2.5: SSE not_ready: if core service not initialized, broker emits `event: not_ready` and holds connection until ready or timeout (30s). On timeout: close connection with `event: not_ready_timeout`. Client behavior (Plan 32 S3.12): `not_ready` = Hold (keep connection open, silence UI hint, do not increment retry counter); `not_ready_timeout` = Terminal (close, surface 'Server still initializing', manual restart).
S2.6: SSE wire contract: all endpoints emit `id:` field (monotonic counter per endpoint). On reconnect with `Last-Event-ID` header, replay missed events from buffer (max 100 events per endpoint). **Epoch protection**: broker assigns a `stream_epoch: int` at startup (derived from `time.time_ns()`). SSE event ID format: `{epoch}:{counter}`. On reconnect with `Last-Event-ID` from a different epoch, emit `event: replay_unavailable` and require REST resynchronization. Buffer predates reconnect = emit `replay_unavailable`.
S2.7: Overflow control: on queue overflow (drop oldest), emit `event: overflow, data: {"dropped": N}` **outside the bounded queue** (bypass queue so client always receives it). Single per-connection writer lock serializes control and data writes; overflow does NOT participate in per-endpoint monotonic stream ID.
S2.8: Auth during streaming: session validated at connection establishment. Mid-stream expiry detected by periodic session-check every 30s. On expiry: emit `event: auth_expired`, flush, close. Initial connect with invalid/expired cookie → HTTP 401 immediately, connection closed.
S2.9: Test: `pytest app/web/tests/test_sse_broker.py -v` — `test_bounded_queue_max_100`, `test_overflow_bypasses_queue`, `test_reconnect_same_epoch_replays`, `test_reconnect_diff_epoch_replay_unavailable`, `test_auth_expired_midstream`, `test_keepalive_30s`

## S3 — Orchestrator Endpoints

S3.1: POST `/api/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse`. Supports `Idempotency-Key: UUID4` header; server stores `(user_session_id, idempotency_key, endpoint_path, payload_hash, status_code, response_body, content_type, stored_at)` in audit DB SQLite with 5-min TTL. Rationale for 5-min TTL: typical retry interval is <30s; session lifetime is 24h; 5-min TTL balances replay protection with storage growth. Retries with same key, same session, same payload return cached response (identical status + body). Same key + different payload_hash → HTTP 409 Conflict. Cross-user replay prevented by session_id scoping.
S3.2: GET `/api/orchestrator/status` — returns `OrchestratorStatus`
S3.3: SSE `/api/orchestrator/stream` — mounts on `SSEBroker`, emits `orchestrator.response.ready` and `orchestrator.clarification_needed`
S3.4: SSE `/api/events/tasks` — mounts on `SSEBroker`, emits `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted`
S3.5: REST `GET /api/events/tasks` — paginated historical task events for TUI polling fallback (Plan 32 S3.3). Returns `TaskListResponse`. Max page_size 500. Filters: `event_type`, `task_id`, `since_event_id: int` (optional). With `since_event_id`: returns events `id > since_event_id` ascending, capped at `page_size`. Without: returns most recent page descending. Response includes `next_event_id` cursor. TUI stores cursor per poll. Auth: session cookie.
S3.6: Memory endpoints: `/api/orchestrator/memory/*` routes delegate to Orchestrator facade, which calls `MemoryGateway`. When `MemoryGateway` resolves to `None` at request time (memory still loading, Plan 33 S2.6), return HTTP 503 with `MemoryNotReadyResponse` body: `{"error_code": "memory_not_ready", "message": "Memory subsystem still loading", "retry_after_seconds": 5}`. Audit DB records the 503. Plan 33 S2.6 governs the loading lifecycle.
S3.7: Test: `pytest app/web/tests/test_orchestrator_api.py -v` — `test_post_message_success`, `test_idempotency_5min_ttl`, `test_idempotency_409`, `test_polling_since_event_id`, `test_polling_no_cursor_descending`, `test_polling_no_overlap`, `test_memory_not_ready_503`

## S4 — Messaging Endpoints

S4.1: POST `/api/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S4.2: GET `/api/messaging/audit` — paginated audit log, max page size 1000, returns `AuditPage`
S4.3: GET `/api/messaging/circuits` — returns `CircuitStateList`
S4.4: Test: `pytest app/web/tests/test_messaging_api.py -v` — `test_send_message`, `test_audit_pagination`, `test_circuit_state_list`

## S5 — Auth & Rate Limiting

S5.1: POST `/api/auth/login` — accepts `LoginRequest`, returns `LoginResponse` with session cookie; cookie attrs: `HttpOnly`, `Secure` (HTTPS only; omit for localhost HTTP via scheme check), `SameSite=Strict`, max-age 24h.
  - **Trusted-proxy model**: v1 requires direct TLS termination. `Secure` flag iff `scheme == "https"`. Reverse proxy must terminate TLS and forward HTTP on localhost. No `X-Forwarded-Proto` honored — prevents spoofing. Document in README.
  - **Loopback exception for Secure flag**: If `Host` header resolves to loopback (127.0.0.1, ::1, localhost) AND scheme is `http`, allow login without `Secure` flag (local development). If `Host` is non-loopback AND scheme is `http`, return **HTTP 403** with `error_code: insecure_deployment` (not 500 — 500 implies server failure and triggers retries).
  - **Bootstrap**: On first run (no `users.json`), server generates a cryptographically random setup token (32 bytes, base64-encoded) and prints it to stderr only. The token is single-use and expires after first successful login or 24h. First login request must include the setup token in `LoginRequest.setup_token`. Without a valid token, login returns 403. Token hash persisted in audit DB so `check_auth_bootstrap.py` can assert single-use across restarts. **Warning**: do not pipe stderr to shared logs during bootstrap. **Recovery**: if token expires without first login, delete `users.json` and restart.
  - **Credential store**: `platformdirs.user_config_dir("sovereignai") / "users.json"` (hashed bcrypt, cost factor 14). Atomic write: same-dir tmpfile (O_WRONLY|O_CREAT|O_EXCL, 0o600), flush+fsync, os.replace (fixes perms on existing permissive file). Parent directory: `makedirs(parent, mode=0o700, exist_ok=True)`.
  - **Password policy**: min 12 chars, 1 uppercase, 1 digit, 1 special. Server-side enforced.
  - **Rate limit**: per username (regardless of source IP), 5 attempts per 60s fixed window (window resets at window_start + 60s), exponential backoff on consecutive failures (formula: `min(86400, 60 * 2^(N-5))` for attempt N >= 5). Hard lockout after 20 consecutive failures per username. Consecutive = strictly no success between failures; a single success resets counter to zero. **Lockout applies only when `users.json` exists** — bootstrap phase exempt.
S5.1a: **Audit DB** — path: `platformdirs.user_data_dir("sovereignai") / "audit.db"`. SQLite WAL mode, `busy_timeout=5000`. Schema: `idempotency_cache(id PK, user_session_id, idempotency_key, endpoint_path, payload_hash, status_code INT, response_body, content_type, stored_at)`, `rate_limit(username PK, window_start, attempt_count INT, consecutive_failures INT, last_failure_time, lockout_until, last_attempt_time)`, `bootstrap_tokens(token_hash PK, created_at, used_at NULL, expires_at)`. Lazy cleanup: delete `idempotency_cache` where `stored_at` >5min on cache hit; clear `rate_limit` lockout fields (`lockout_until=NULL, last_failure_time=NULL`) where expired; preserve `consecutive_failures` counter. Background: every 1h, prune all expired. Expected v1 footprint: <100KB idempotency, <50 rate-limit rows.
S5.2–S5.4: POST `/api/auth/logout` — 204, CSRF via valid session cookie. Session auth per AR13; no query-param tokens. CORS: same-origin only.
S5.5–S5.6: SSE auth expiry every 30s → emit `auth_expired`, flush, close (TUI treats as terminal). Error envelope: `{error_code, message, retry_after_seconds?}`. Status mapping: `login_required→401`, `setup_token_required/invalid→403`, `authorization_denied→403`, `lockout→423`, `rate_limited→429`, `insecure_deployment→403`, `idempotency_conflict→409`, `memory_not_ready→503`.
S5.7: Test: `pytest app/web/tests/test_auth.py -v` — named tests: `test_bootstrap_first_run_token_printed_to_stderr`, `test_bootstrap_token_single_use`, `test_bootstrap_token_expires_24h`, `test_bootstrap_token_hash_persisted_in_audit_db`, `test_audit_db_lazy_window_reset`, `test_audit_db_lazy_lockout_clear`, `test_audit_db_lazy_idempotency_prune`, `test_rate_limit_5_per_60s_window_enforced`, `test_rate_limit_exponential_backoff_formula`, `test_rate_limit_hard_lockout_20_consecutive`, `test_rate_limit_schema_persistent_consecutive_count`, `test_login_401_envelope`, `test_setup_token_403_envelope`, `test_lockout_423_retry_after`, `test_rate_limited_429_retry_after`, `test_insecure_deployment_403`, `test_secure_flag_https`, `test_secure_flag_omitted_localhost`

## S6 — Trace & Lifecycle Endpoints

S6.1: SSE `/api/trace/stream` — mounts on `SSEBroker`, streams `TraceEvent` from TraceEmitter
S6.2: SSE `/api/lifecycle/stream` — mounts on `SSEBroker`, streams `LifecycleEventDTO` for `lifecycle.*` events (`ready`, `shutting_down`, `stopped`). **Cross-plan (Plan 33)**: Plan 33 S4.1 emits `lifecycle.shutting_down` on SIGTERM `{timestamp, server_pid, instance_uuid, drain_timeout_seconds: 60}`. Plan 33 S4.3 emits `lifecycle.stopped` after shutdown completes. Plan 31 wires SSE endpoint.
S6.3: REST `GET /api/trace/logs` — paginated trace log retrieval (for TUI polling fallback when SSE unavailable). Returns `TraceLogResponse` with `TraceEvent[]`, max page size 500, supports time-range and event-type filters.
S6.4: Test: `pytest app/web/tests/test_trace_api.py -v` — `test_lifecycle_stream_shutting_down`, `test_lifecycle_stream_stopped`, `test_trace_log_pagination`

## S7 — Options, Model Registry, Health Endpoint Wiring

S7.1: Mount Plan 28 `/api/options/*` REST + SSE `/api/options/stream` (SSEBroker subscribes to EventBus).
S7.2: Mount Plan 29 `/api/models/*` REST + SSE `/api/models/stream` (SSEBroker subscribes to EventBus).
S7.3: `GET /api/health` not registered by Plan 31. Plan 33 S3.6 sole registrar — uses `HealthSnapshot` DTO per S1.2.
S7.3a: `/api/lifecycle/ready`: Plan 33 S3.7 owns backend + `LifecycleReadyResponse` DTO. Plan 31 mounts via Web bridge. Plan 33 supplies service through bridge; Plan 31 mounts route. Separates ownership from mounting per AR12.
S7.4: Test: `pytest app/web/tests/test_options_api.py app/web/tests/test_model_registry_api.py -v`

## S8 — DI Composition

S8.1–S8.3: `app/web/main.py` composes via DIContainer, no hardcoded names (AR4). Lifespan: wires Web-only services (auth, SSEBroker); core services by Plan 33. Separate process per AR12; imports via `web_bridge/` only.
S8.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S9 — AR Checks

S9.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S9.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs (S1.2 authoritative); scan `/api/health` (HealthSnapshot), `/api/lifecycle/ready` (LifecycleReadyResponse); ensure `LoginRequest` never passes core types/unhashed passwords beyond Web boundary.
S9.3: Add `check_auth_bootstrap.py` — verify setup token required, expires after use, token hash persisted proves single-use across restarts, auto-provisioning disabled
S9.4: Add `check_idempotency_scope.py` — verify cache key includes session_id + payload_hash; same key + different payload → 409
S9.5: Add `check_sse_mounting_ownership.py` — verify no SSE routes registered outside SSEBroker
S9.6: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
