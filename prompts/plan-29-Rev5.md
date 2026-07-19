Depends on: Plan 28 (Options), Plan 22 (EventBus)
Vision principles: P3 (Reliability), P8 (UIs are separate processes), P11 (Quality), P14 (Modularity)
Open questions resolved: DD-29.1, DD-29.2, DD-29.3, DD-29.4, DD-29.5
**Revision**: Rev5

## S0 — Opening

S0.0: Clone latest repo. Verify Plans 22 and 28 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PRINCIPLES.md`
S0.3: Read `.agent/architect/documents/SovereignAI_Models_Panel_Drill_Down_Design_v1.0.md`
S0.4: Run baseline: `pytest app/sovereignai/tests/test_options_*.py -v`

## S1 — Schema

S1.1: Create `app/sovereignai/model_registry/schema.py` — Pydantic models
S1.2: `Provider`: id, name, api_base_url, auth_type, is_enabled
S1.3: `ModelFamily`: id, provider_id, name, description
S1.4: `Model`: id, family_id, name
S1.5: `ModelVersion`: id, model_id, version_string, release_date, is_latest, context_window, supports_vision, supports_tools, capabilities JSON
S1.6: Define `NormalizedModelData` Pydantic model in `schema.py` — fields: provider_id, model_id, model_name, version_string, release_date, context_window, supports_vision, supports_tools, capabilities dict. All adapters return `list[NormalizedModelData]`.
S1.7: Create `SyncRun` table in `model_registry.db` — fields: id (PK), provider_id (FK), started_at, completed_at, status (SUCCESS/FAILED), error_class (nullable). Index on (provider_id, completed_at). S3.2 reads `MAX(completed_at) WHERE status='SUCCESS' AND provider_id=?` as `last_successful_sync_at`.
S1.8: Test: `pytest app/sovereignai/tests/test_model_registry_schema.py -v`

## S2 — Sync Service

S2.1: Create `app/sovereignai/model_registry/sync.py` — `ModelSyncService`
S2.2: Define `ProviderAdapterProtocol` in `sync.py`: `async def fetch_models(api_key: str) -> list[NormalizedModelData]`. Adapters may raise `ProviderAuthError`, `ProviderRateLimitError`, `ProviderUnavailableError` (defined in `sync.py`). Wrap all adapter calls with `asyncio.wait_for(..., timeout=60)`.
S2.3: Provider adapters: `app/sovereignai/model_registry/adapters/{provider}.py` implement `ProviderAdapterProtocol`
S2.4: Registry: `adapters/__init__.py` with `ADAPTER_REGISTRY: dict[str, ProviderAdapterProtocol]`. Registry contract: normalized provider IDs (lowercase, no spaces), explicit registration at app composition time, duplicate-key rejection, no auto-import from untrusted config. Filter registry by `BehaviorSettings.enabled_providers` at startup (default = all registered). Fake-adapter conformance test required.
S2.5: Fetch from provider APIs using Plan 28's API keys
S2.6: Cache results in SQLite (`model_registry.db`, separate file), update existing records, mark stale records
S2.7: Background task: FastAPI BackgroundTasks for manual sync; `asyncio.create_task` with interval loop for scheduled sync. Interval from Plan 28's `BehaviorSettings.model_sync_interval_hours`. Graceful-degrade: if BehaviorSettings unavailable, default to 24h, start scheduler regardless. Use FastAPI lifespan context manager (`@asynccontextmanager`) for task lifecycle: startup creates task, stores reference on `app.state.sync_task`; shutdown cancels task, awaits cancellation. Prevent overlap: skip if prior sync still running. Exception logging. Scoped as best-effort for single-process; durable scheduler is v2.
S2.8: On sync error, log to `sync_errors` table (fields: timestamp, provider_adapter_name, error_class, safe_error_message; NO credentials or raw upstream responses). `safe_error_message` schema: max 500 chars, structured fields (code, message, http_status, provider_error_id), strip API key patterns (sk-..., AKIA..., ghp_...). Error retention: read from `BehaviorSettings.sync_error_retention_days` (default 30). Emit `models.sync.failed` event. After recovery, emit `models.sync.succeeded`. Stale badge continues showing existing data.
S2.9: Test: `pytest app/sovereignai/tests/test_model_registry_sync.py -v`

## S3 — Offline Mode

S3.1: All browse operations work from local cache
S3.2: Stale threshold: `max(24h, 2 × sync_interval)` from `last_successful_sync_at` per `SyncRun` table (not last attempted). Immediate stale if no successful sync exists. Expose last error separately. 24h floor is UX choice for default users; tests can lower via fixture. Consider upper bound `min(30d, ...)` for very large intervals (v2).
S3.3: Auto-trigger sync on app startup if data is older than threshold
S3.4: Test: `pytest app/sovereignai/tests/test_model_registry_offline.py -v`

## S4 — SSE Updates

S4.1: Emit `models.sync.completed` event after each sync terminal attempt with outcome field `{status: 'success'|'failed', provider_id, timestamp}`. Consumers subscribe to single unambiguous completion event.
S4.2: SSE endpoint: `/api/models/stream` for real-time availability
S4.3: Future Integration: Plan 27's MessagingAdapter can subscribe to `models.sync.completed` and forward to CodingManager via public API (optional, no Plan 27 dependency). Verify no Plan 27 imports/message contracts/test fixtures in Plan 29 scope.
S4.4: Test: `pytest app/sovereignai/tests/test_model_registry_sse.py -v`

## S5 — API Layer

S5.1: FastAPI routes: GET /api/models, GET /api/models/{id}, GET /api/providers, POST /api/models/sync
S5.2: Query params: filter by provider_id, family_name (case-insensitive), supports_vision, supports_tools
S5.3: Test: `pytest app/sovereignai/tests/test_model_registry_api.py -v`

## S6 — UI Data Contract (P8 Compliant)

S6.0: Per P8, TUI is separate process. This plan produces backend endpoints only.
S6.1: JSON data contract for TUI: tree-shaped response (Provider → Family → Model → Version)
S6.2: Detail view JSON: capabilities, context_window, pricing (from provider API if available, else null)
S6.3: Test: `pytest app/sovereignai/tests/test_model_registry_ui_contract.py -v`

## S7 — AR Checks

S7.1: Add `check_model_registry_no_direct_provider_calls.py` — verify all provider access goes through SyncService
S7.2: Add `check_model_registry_adapter_registry.py` — verify all adapter modules in `adapters/` register into `ADAPTER_REGISTRY`
S7.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
