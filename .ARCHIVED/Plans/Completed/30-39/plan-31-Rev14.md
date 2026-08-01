Depends on: Plan 26 (Orchestrator), Plan 27 (Messaging), Plan 28 (Options), Plan 29 (Model Registry)
Vision principles: P8 (UIs are separate processes), P11 (Quality), P13 (Strong and robust), P14 (Modularity)
AR rules: AR4, AR12, AR13, AR14
OR rules: UOR-1, UOR-2
Open questions resolved: DD-31.1, DD-31.2, DD-31.3, DD-31.4, DD-31.5, DD-31.6, DD-31.7, DD-31.8
**Revision**: Rev15

## Executor Manifest
**Plan**: 31
**Phases**: 9 (S1–S9; S0 excluded from count)
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

**Coverage target**: ≥90% (closing gate: `pytest --cov=app/web --cov-report=term-missing app/web/tests/ -v --cov-fail-under=90`)
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(web): add Web API layer with SSE broker, auth, and DTOs`

## S0 — Opening
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Web DTOs
S1.1: Create `app/web/schemas.py` — Pydantic DTOs for all HTTP responses per AR14
S1.2: Complete DTO inventory (authoritative — Plans 32/33/34 MUST use these names): `OrchestratorResponse`, `MessageRequest`, `OrchestratorStatus`, `CrossDepartmentMessage`, `AuditPage`, `AuditEntry`, `CircuitStateList`, `HealthSnapshot`, `LoginRequest`, `LoginResponse`, `OptionsUpdate`, `ModelQuery`, `SyncTrigger`, `TraceEvent`, `GraphNodeDTO`, `GraphEdgeDTO`, `GraphQueryRequest`, `GraphQueryResponse`, `EpisodicQueryRequest`, `EpisodicQueryResponse`, `EpisodicEventDTO`, `TaskEventDTO`, `TaskListResponse`, `LifecycleEventDTO`, `TraceLogRequest`, `TraceLogResponse`, `LifecycleReadyResponse`, `MemoryNotReadyResponse`, `MergeConflictDTO`, `MergeConflictPage`. DTO field definitions:
  - `OrchestratorResponse`: `task_id: str, status: str, response_text: str, error: Optional[str], created_at: str` (ISO 8601)
  - `LoginRequest`: `username: str, password: str, setup_token: Optional[str]`
  - `LoginResponse`: `session_id: str, expires_at: str` (ISO 8601)
  - `HealthSnapshot`: `status: str` ("READY" | "DEGRADED" | "UNHEALTHY"), `subsystems: list[SubsystemHealth]`, `cache_age_ms: int`
  - `SubsystemHealth`: `name: str, status: str` ("HEALTHY" | "DEGRADED" | "UNHEALTHY"), `details: Optional[str]`
  - `LifecycleReadyResponse`: `ready: bool, server_pid: int, instance_uuid: str`
  - `AuditPage`: generic `items: list[T], total_count: int, offset: int, limit: int` (T varies by endpoint)
  - `MergeConflictPage`: `items: list[MergeConflictDTO], total_count: int, offset: int, limit: int`
  - `GraphQueryRequest`: `query_type: str` ("entity_search" | "relation_traversal"), `entity_name: Optional[str]`, `entity_type: Optional[str]`, `relation_type: Optional[str]`, `max_depth: int = 1`
  - `GraphQueryResponse`: `nodes: list[GraphNodeDTO], edges: list[GraphEdgeDTO]`
  - `EpisodicQueryRequest`: `event_type: Optional[str], since: Optional[str]` (ISO 8601), `until: Optional[str]` (ISO 8601), `offset: int = 0, limit: int = 500`
  - `EpisodicQueryResponse`: `events: list[EpisodicEventDTO], total_count: int, offset: int, limit: int`
  - `CircuitStateList`: `circuits: list[CircuitState]` where `CircuitState: {worker_id: str, state: str, error_count: int, last_error: Optional[str]}`
  - `OrchestratorStatus`: `state: str, uptime_seconds: float, tasks_completed: int, tasks_failed: int`
  - `CrossDepartmentMessage`: `source_department: str, target_department: str, content: str, correlation_id: str`
  - `OptionsUpdate`: `key: str, value: str`
  - `ModelQuery`: `model_id: Optional[str], provider: Optional[str]`
  - `SyncTrigger`: `model_id: str`
  - `TraceEvent`: `timestamp: str, level: str, source: str, message: str, event_type: Optional[str]`
  - `TraceLogRequest`: `event_type: Optional[str], since: Optional[str], until: Optional[str], offset: int = 0, limit: int = 500`
  - `TraceLogResponse`: `events: list[TraceEvent], total_count: int, offset: int, limit: int`
  - `GraphNodeDTO`: `uuid: str, name: str, type: str, attributes: dict`
  - `GraphEdgeDTO`: `src_id: str, dst_id: str, type: str, attributes: dict`
  - `EpisodicEventDTO`: `id: int, event_type: str, timestamp: str, correlation_id: Optional[str], summary: str`
  - `TaskEventDTO`: `event_id: int, task_id: str, event_type: str, timestamp: str, details: Optional[dict]`
  - `LifecycleEventDTO`: `event_type: str, timestamp: str, server_pid: Optional[int], instance_uuid: Optional[str], drain_timeout_seconds: Optional[int]`
  - `MergeConflictDTO`: `conflict_id, entity_name, entity_type, canonical_uuid, candidate_uuids: list[str], first_observed_at: str` (ISO 8601), `resolution_status: str` (v1: `"unresolved" | "suppressed_by_dedup"`)
  - `MemoryNotReadyResponse`: `error_code: "memory_not_ready", message: "Memory subsystem still loading", retry_after_seconds: 5`
  - `TaskListResponse`: `events: list[TaskEventDTO], total_count: int, next_event_id: Optional[int], page_size: int`
S1.3: No core types returned directly; all conversions in `app/sovereignai/web_bridge/converters.py` (core-side bridge)
S1.4: `check_web_dto_completeness.py` (S9.2) ensures `LoginRequest` never passes core types or unhashed passwords beyond Web boundary.
S1.5: Test: `pytest app/web/tests/test_schemas.py -v` — `test_dto_inventory_complete`, `test_no_core_types_in_schemas`, `test_merge_conflict_dto_fields_valid`, `test_memory_not_ready_response_fields_valid`, `test_task_list_response_fields_valid`, `test_dto_round_trip_all_schemas`

## S2 — SSE Broker
S2.1: Create `app/web/sse_broker.py` — `SSEBroker` shared utility for Plan 31+ SSE endpoints
S2.2: Per-connection bounded queue: max 100 events (send queue, discarded on disconnect). Auth validation, event subscription, keepalive (30s), reconnection, disconnect via `request.is_disconnected()`. **Buffer architecture**: the per-endpoint replay buffer (S2.6, max 100 events) is a separate data structure that persists across connection disconnects. The send queue is per-connection and ephemeral.
S2.3: Endpoints mounted on broker: `/api/orchestrator/stream` (orchestrator events), `/api/events/tasks` (task lifecycle; SSE vs REST discriminated by `Accept: text/event-stream`, absent→REST per S3.5), `/api/trace/stream` (TraceEmitter logs), `/api/lifecycle/stream` (lifecycle state), `/api/options/stream` (Plan 28 events), `/api/models/stream` (Plan 29 events)
S2.4: Plans 28/29 SSE: Plan 31 owns all mounting via SSEBroker. Plans 28/29 emit via EventBus only; SSEBroker subscribes. **Precondition**: verify Plans 28/29 have no active SSE routes: `grep -rn 'text/event-stream\|SSEBroker\|sse_broker' app/options/ app/models/` should return no route registrations; if found, remove before mounting. AR check `check_sse_mounting_ownership.py`.
S2.5: SSE not_ready: if core service not initialized, broker emits `event: not_ready` and holds connection until ready or timeout (30s). On timeout: close connection with `event: not_ready_timeout`. Plan 31 emits both HTTP `Retry-After` header and JSON envelope `retry_after_seconds` for all retryable 503/429 responses (TUI reads header first, falls back to envelope). Client behavior (Plan 32 S3.12): `not_ready` = Hold (keep connection open, silence UI hint, do not increment retry counter); `not_ready_timeout` = Terminal (close, surface 'Server still initializing', manual restart).
S2.6: SSE wire contract: all endpoints emit `id:` field (monotonic counter per endpoint). On reconnect with `Last-Event-ID` header, replay missed events from buffer (max 100 events per endpoint). **Epoch protection**: broker assigns a `stream_epoch: int` at startup (derived from `time.time_ns() // 1_000_000_000`). SSE event ID format: `{epoch}:{counter}`. Counter is per-endpoint, monotonically increasing within each endpoint's stream epoch. On reconnect with `Last-Event-ID` from a different epoch, emit `event: replay_unavailable`. After emitting `replay_unavailable`, the server closes the connection; the client must re-open SSE or fall back to REST resynchronization. Buffer predates reconnect = emit `replay_unavailable`.
S2.7: Overflow control: on queue overflow (drop oldest), emit `event: overflow, data: {"dropped": N}` **outside the bounded queue** (bypass queue so client always receives it; note that extreme TCP receive buffer saturation may still drop this event). Single per-connection writer lock serializes control and data writes; overflow does NOT participate in per-endpoint monotonic stream ID. Overflow events carry **no `id:` field**; clients must not store overflow as `Last-Event-ID`.
S2.8: Auth during streaming: session validated at connection establishment. Mid-stream expiry detected by periodic session-check every 30s. On expiry: emit `event: auth_expired`, flush, close. Initial connect with invalid/expired cookie → HTTP 401 immediately, connection closed. v1 limitation: expired sessions may receive events for up to 30s. v1 limitation: per-username rate limiting with no IP-based component enables account lockout DoS; v2 should add per-IP rate limiting.
S2.9: Test: `pytest app/web/tests/test_sse_broker.py -v` — `test_bounded_queue_max_100`, `test_overflow_bypasses_queue`, `test_overflow_event_has_no_id_field`, `test_overflow_reports_correct_dropped_count`, `test_replay_buffer_persists_across_disconnect`, `test_reconnect_same_epoch_replays`, `test_reconnect_diff_epoch_replay_unavailable`, `test_not_ready_hold_before_timeout`, `test_not_ready_timeout_event_emitted`, `test_auth_expired_midstream`, `test_keepalive_30s`

## S3 — Orchestrator Endpoints
S3.1: POST `/api/orchestrator/message` — accepts `MessageRequest`, returns `OrchestratorResponse`. Supports `Idempotency-Key: UUID4` header; server stores `(user_session_id, idempotency_key, endpoint_path, payload_hash, status_code, response_body, content_type, stored_at)` in audit DB SQLite with 5-min TTL. `payload_hash` computed via `hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',',':')).encode()).hexdigest()`. **Concurrent same-key race**: claim the composite key in a transaction before executing the side effect; on UNIQUE violation fetch existing cached response and compare `payload_hash` — return cached data if match, or HTTP 409 if mismatch. Retries with same key, same session, same payload return cached response (identical status + body). Cross-user replay prevented by session_id scoping. Test: `test_concurrent_idempotency_single_execution`.
S3.2: GET `/api/orchestrator/status` — returns `OrchestratorStatus`
S3.3: SSE `/api/orchestrator/stream` — mounts on `SSEBroker`, emits `orchestrator.response.ready` and `orchestrator.clarification_needed`
S3.4: SSE `/api/events/tasks` — mounts on `SSEBroker`, emits `task.created`, `task.updated`, `task.completed`, `task.failed`, `task.deleted` (SSE vs REST discrimination per S2.3 Accept-header rule)
S3.5: REST `GET /api/events/tasks` — paginated historical task events for TUI polling fallback (Plan 32 S3.3). Returns `TaskListResponse`. Min page_size 1, max page_size 500. Filters: `event_type`, `task_id`, `since_event_id: int` (optional). With `since_event_id`: returns events `id > since_event_id` ascending, capped at `page_size`. Without: returns most recent page descending; `next_event_id` represents the smallest event ID in the current page (for backward paging). TUI stores cursor per poll. Auth: session cookie.
S3.6: Memory endpoints: `/api/orchestrator/memory/*` routes delegate to Orchestrator facade, which calls `MemoryGateway`. When `MemoryGateway` is `None` (not yet constructed) OR `MemoryGateway.is_ready()` returns `False` (load incomplete or post-flush), return HTTP 503 with `Retry-After: 5` header and `MemoryNotReadyResponse` body. Route 503 to Plan 27's `InterDepartmentBus.audit()` facility (DI-injected, no separate table). DI returns one stable gateway instance once composed; requests during load return 503 and cannot trigger load. Plan 33 S2.6 governs the loading lifecycle.
S3.7: Test: `pytest app/web/tests/test_orchestrator_api.py -v` — `test_post_message_success`, `test_idempotency_5min_ttl`, `test_idempotency_409`, `test_concurrent_idempotency_single_execution`, `test_polling_since_event_id`, `test_polling_no_cursor_descending`, `test_polling_no_overlap`, `test_memory_not_ready_503`

## S4 — Messaging Endpoints
S4.1: POST `/api/messaging/send` — accepts `CrossDepartmentMessage` DTO, routes via InterDepartmentBus
S4.2: GET `/api/messaging/audit` — paginated audit log, max page size 1000, returns `AuditPage`
S4.3: GET `/api/messaging/circuits` — returns `CircuitStateList`
S4.4: Test: `pytest app/web/tests/test_messaging_api.py -v` — `test_send_message`, `test_audit_pagination`, `test_circuit_state_list`

## S5 — Auth & Rate Limiting
S5.1: POST `/api/auth/login` — accepts `LoginRequest`, returns `LoginResponse` with session cookie; cookie attrs: `HttpOnly`, `Secure` (HTTPS only; omit for localhost HTTP via scheme check), `SameSite=Strict`, max-age 24h.
  - **Trusted-proxy model**: v1 requires direct TLS termination. `Secure` flag iff `scheme == "https"`. Reverse proxy must terminate TLS and forward HTTP on localhost. No `X-Forwarded-Proto` honored — prevents spoofing. Document in README.
  - **Loopback exception for Secure flag**: If `request.client.host` is loopback (`127.0.0.1` or `::1`) AND scheme is `http`, allow login without `Secure` flag (local development). Uses socket peer address, not `Host` header (client-controlled, spoofable). If `Host` is non-loopback AND scheme is `http`, return **HTTP 403** with `error_code: insecure_deployment` (not 500 — 500 implies server failure and triggers retries).
  - **Bootstrap**: On first run (no `users.json`), server generates a cryptographically random setup token (32 bytes, base64-encoded) and prints it to stderr only. Optional: `SOVEREIGNAI_BOOTSTRAP_TOKEN_FILE` env var — if set, write token to specified file with 0o600 permissions instead of (or in addition to) stderr. The token is single-use and expires after first successful login or 24h. First login request must include the setup token in `LoginRequest.setup_token`. Without a valid token, login returns 403. Token hash persisted in audit DB so `check_auth_bootstrap.py` can assert single-use across restarts. **Warning**: do not pipe stderr to shared logs during bootstrap. **Recovery**: if token expires without first login, delete `users.json` and restart.
  - **Credential store**: `platformdirs.user_config_dir("sovereignai") / "users.json"` (hashed bcrypt, cost factor 14). Atomic write: same-dir tmpfile (O_WRONLY|O_CREAT|O_EXCL, 0o600), flush+fsync, os.replace (fixes perms on existing permissive file). If O_EXCL fails (stale tmpfile from crash): delete stale tmpfile and retry once; if second attempt fails, raise IOError. Parent directory: `makedirs(parent, mode=0o700, exist_ok=True)`.
  - **Password policy**: min 12 chars, 1 uppercase, 1 digit, 1 special. Server-side enforced.
  - **Session storage**: server-side `sessions` table in audit DB (see S5.1a). Session ID: `secrets.token_urlsafe(32)`. Logout: DELETE from sessions table. Periodic validation (S2.8): check session exists and `expires_at > now()`. Sessions persist in SQLite across restarts; no signing key required.
  - **Rate limit**: per username (regardless of source IP), 5 attempts per 60s fixed window (window resets at window_start + 60s), exponential backoff on consecutive failures (formula: `min(86400, 60 * 2^(N-5))` for consecutive_failures N >= 5). N is the `consecutive_failures` counter, NOT the per-window `attempt_count`; a single failure after four successes resets `consecutive_failures` to 1 and does NOT trigger backoff. Hard lockout after 20 consecutive failures per username: duration 24h, set `lockout_until = current_time + 86400`. Recovery: `consecutive_failures` preserved across lockout expiry — a post-expiry successful login resets to zero; a post-expiry failure continues from preserved count. Manual recovery: DELETE or UPDATE the rate_limit row in audit DB. Document in README.
  - **Rate-limit UPSERT**: atomic SQL: `INSERT INTO rate_limit(username, window_start, attempt_count, consecutive_failures, last_attempt_time) VALUES(?, current_time, 1, 1, current_time) ON CONFLICT(username) DO UPDATE SET attempt_count = CASE WHEN current_time > window_start + 60 THEN 1 ELSE attempt_count + 1 END, window_start = CASE WHEN current_time > window_start + 60 THEN current_time ELSE window_start END, consecutive_failures = consecutive_failures + 1, last_attempt_time = current_time`. New usernames get a row on first attempt; window resets automatically when expired. SQLite WAL serializes writes.
  - **Login-attempt algorithm (ordered)**: (1) Load rate_limit record for username; (2) If row missing, INSERT new row (attempt_count=1, consecutive_failures=1); (3) If active lockout (lockout_until > now), return 423 with retry_after_seconds; (4) If active backoff (consecutive_failures >= 5), check backoff formula, return 429 if not elapsed; (5) Verify password; (6) On success: reset consecutive_failures to 0; (7) On failure: atomic UPDATE per UPSERT above. Attempt 5 is rejected by step 4. **Lockout applies only when `users.json` exists** — bootstrap phase exempt.
S5.1a: **Audit DB** — path: `platformdirs.user_data_dir("sovereignai") / "audit.db"`. SQLite WAL mode, `busy_timeout=5000`. Schema: `idempotency_cache(id PK, user_session_id, idempotency_key, endpoint_path, payload_hash, status_code INT, response_body, content_type, stored_at, UNIQUE(user_session_id, idempotency_key, endpoint_path))`, `rate_limit(username PK, window_start, attempt_count INT, consecutive_failures INT, last_failure_time, lockout_until, last_attempt_time)`, `bootstrap_tokens(token_hash PK, created_at, used_at NULL, expires_at)`, `sessions(session_id TEXT PK, username TEXT, created_at TEXT, expires_at TEXT, last_seen_at TEXT)`. Index: `CREATE INDEX idx_idempotency_stored_at ON idempotency_cache(stored_at)`. Insert uses INSERT OR FETCH: attempt insert, on UNIQUE violation fetch existing cached response. Lazy cleanup: delete `idempotency_cache` where `(now() - stored_at) > 5 minutes` on cache hit; clear `rate_limit` lockout fields (`lockout_until=NULL, last_failure_time=NULL`) where expired; preserve `consecutive_failures` counter. Background: every 1h, prune all expired `idempotency_cache` entries; prune expired `bootstrap_tokens` where `expires_at < now()` AND `used_at IS NULL`; prune used tokens where `used_at < now() - 24h`; clear expired rate-limit lockout fields. Expected v1 footprint: <100KB idempotency, <50 rate-limit rows.
S5.2–S5.4: POST `/api/auth/logout` — 204, DELETE from sessions table. CSRF via valid session cookie. Session auth per AR13; no query-param tokens. CORS: same-origin only.
S5.5–S5.6: SSE auth expiry every 30s → emit `auth_expired`, flush, close (TUI treats as terminal). Error envelope: `{error_code, message, retry_after_seconds?}`. All 429, 423, and retryable 503 responses MUST include both HTTP `Retry-After` header and `retry_after_seconds` in JSON envelope. Status mapping: `login_required→401`, `setup_token_required/invalid→403`, `authorization_denied→403`, `lockout→423`, `rate_limited→429`, `insecure_deployment→403`, `idempotency_conflict→409`, `memory_not_ready→503`.
S5.7: Test: `pytest app/web/tests/test_auth.py -v` — named tests: `test_bootstrap_first_run_token_printed_to_stderr`, `test_bootstrap_token_single_use`, `test_bootstrap_token_expires_24h`, `test_bootstrap_token_hash_persisted_in_audit_db`, `test_audit_db_lazy_window_reset`, `test_audit_db_lazy_lockout_clear`, `test_audit_db_lazy_idempotency_prune`, `test_rate_limit_row_created_on_first_attempt`, `test_rate_limit_window_resets_after_60s`, `test_rate_limit_5_per_60s_window_enforced`, `test_rate_limit_exponential_backoff_formula`, `test_rate_limit_hard_lockout_20_consecutive`, `test_rate_limit_schema_persistent_consecutive_count`, `test_consecutive_failures_resets_on_success`, `test_session_revoked_on_logout`, `test_login_401_envelope`, `test_setup_token_403_envelope`, `test_lockout_423_retry_after`, `test_rate_limited_429_retry_after`, `test_insecure_deployment_403`, `test_secure_flag_https`, `test_secure_flag_omitted_localhost`

## S6 — Trace & Lifecycle Endpoints
S6.1: SSE `/api/trace/stream` — mounts on `SSEBroker`, streams `TraceEvent` from TraceEmitter
S6.2: SSE `/api/lifecycle/stream` — mounts on `SSEBroker`, streams `LifecycleEventDTO` for `lifecycle.*` events (`ready`, `shutting_down`, `stopped`). **Cross-plan (Plan 33)**: Plan 33 S4.1 emits `lifecycle.shutting_down` on SIGTERM `{timestamp, server_pid, instance_uuid, drain_timeout_seconds: 60}`. Plan 33 S4.3 emits `lifecycle.stopped` after shutdown completes. Plan 31 wires SSE endpoint.
S6.3: REST `GET /api/trace/logs` — paginated trace log retrieval (for TUI polling fallback when SSE unavailable). Returns `TraceLogResponse` with `TraceEvent[]`, max page size 500, supports time-range and event-type filters.
S6.4: Test: `pytest app/web/tests/test_trace_api.py -v` — `test_lifecycle_stream_shutting_down`, `test_lifecycle_stream_stopped`, `test_trace_log_pagination`

## S7 — Options, Model Registry, Health Endpoint Wiring
S7.1: Mount Plan 28 `/api/options/*` REST + SSE `/api/options/stream` (SSEBroker subscribes to EventBus).
S7.2: Mount Plan 29 `/api/models/*` REST + SSE `/api/models/stream` (SSEBroker subscribes to EventBus).
S7.3: `GET /api/health` — Plan 33 exposes handler via `web_bridge` (sole handler provider); Plan 31 mounts the FastAPI route. Uses `HealthSnapshot` DTO per S1.2.
S7.3a: `/api/lifecycle/ready` — Plan 33 exposes handler via `web_bridge` (sole handler provider); Plan 31 mounts the FastAPI route. Example bridge pattern: `from app.web_bridge import get_lifecycle_ready_handler; router.get("/api/lifecycle/ready")(get_lifecycle_ready_handler())`. Separates ownership from mounting per AR12.
S7.4: Test: `pytest app/web/tests/test_options_api.py app/web/tests/test_model_registry_api.py -v`

## S8 — DI Composition
S8.1–S8.3: `app/web/main.py` composes via DIContainer, no hardcoded names (AR4). Lifespan: wires Web-only services (auth, SSEBroker); core services by Plan 33. Separate process per AR12; imports via `web_bridge/` only.
S8.4: Test: `pytest app/web/tests/test_lifespan.py -v`

## S9 — AR Checks
S9.1: Add `check_web_no_core_imports.py` — verify `app/web/` only imports via public API
S9.2: Add `check_web_dto_completeness.py` — verify all endpoints return DTOs (S1.2 authoritative); scan `/api/health` (HealthSnapshot), `/api/lifecycle/ready` (LifecycleReadyResponse); ensure `LoginRequest` never passes core types/unhashed passwords beyond Web boundary.
S9.3: Add `check_auth_bootstrap.py` — verify setup token required, expires after use, token hash persisted proves single-use across restarts, auto-provisioning disabled
S9.4: Add `check_idempotency_scope.py` — verify cache key includes session_id + payload_hash; same key + different payload → 409; UNIQUE constraint enforced
S9.5: Add `check_sse_mounting_ownership.py` — verify no SSE routes registered outside SSEBroker
S9.6: Add `check_rate_limit_window_and_lockout.py` — verify UPSERT creates row for new usernames, resets window after 60s, enforces hard lockout at 20 consecutive failures with 24h duration. Run `pytest .agent/executor/tests/test_document_hygiene.py -v`. All `check_*.py` scripts (S9.1–S9.6) are imported and executed as test functions within `test_document_hygiene.py`. **Gate policy**: all 6 checks must pass as a single gate — the closing gate is all-or-nothing. Individual checks can be debugged via: `python -m pytest .agent/executor/tests/test_document_hygiene.py::test_check_web_no_core_imports -v`. Closing coverage: `pytest --cov=app/web --cov-report=term-missing app/web/tests/ -v --cov-fail-under=90`.

## Closing
Run `/close`
