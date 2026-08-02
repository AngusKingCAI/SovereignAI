Depends on: Plan 24 (SQLite pattern), Plan 22 (EventBus)
Vision principles: P3 (Reliability), P8 (UIs are separate processes), P11 (Quality), P14 (Modularity)
Open questions resolved: DD-28.1, DD-28.2, DD-28.3, DD-28.4
**Revision**: Rev5

## Executor Manifest

**Plan**: 28
**Phases**: 6 (S0–S6)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/sovereignai/options/schema.py` | `pytest app/sovereignai/tests/test_options_schema.py -v` passes |
| S2 | `app/sovereignai/options/backend.py` + `options.db` | `pytest app/sovereignai/tests/test_options_backend.py -v` passes |
| S3 | `app/sovereignai/options/migrations.py` | `pytest app/sovereignai/tests/test_options_migrations.py -v` passes |
| S4 | EventBus integration + SSE endpoint | `pytest app/sovereignai/tests/test_options_events.py -v` passes |
| S5 | FastAPI routes (`/api/options/*`) | `pytest app/sovereignai/tests/test_options_api.py -v` passes |
| S6 | AR check script + hygiene test | `pytest .agent/executor/tests/test_document_hygiene.py -v` passes |

**Governance files**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(options): add Options Panel persistence with encryption, migrations, and EventBus integration`

## S0 — Opening

S0.0: Clone latest repo. Verify Plans 22-24 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md`, `PRINCIPLES.md`
S0.3: Read `.agent/architect/documents/SovereignAI_Options_Panel_Persistence_Design_v1.0.md`
S0.4: Run baseline: `pytest app/sovereignai/tests/ -x --tb=short`

## S1 — Schema

S1.1: Create `app/sovereignai/options/schema.py` — Pydantic models
S1.2: `APIKey(BaseModel)`: provider: str, key: EncryptedStr (generic, extensible)
S1.3: `DisplaySettings`: theme, font_size, panel_layout, language
S1.4: `BehaviorSettings`: auto_save, confirm_destructive, default_department, max_iterations, conversation_retention_days: int = 7, model_sync_interval_hours: int = 24, enabled_providers: list[str] | None = None, sync_error_retention_days: int = 30. `enabled_providers`: None = all registered adapters; list = filter to specific provider IDs. Old `options.db` files load new defaults silently (no migration needed for additive fields with defaults).
S1.5: Test: `pytest app/sovereignai/tests/test_options_schema.py -v`

## S2 — OptionsBackend

S2.1: Create `app/sovereignai/options/backend.py` — `OptionsBackend`
S2.2: SQLite + WAL (`options.db`, separate file) using Plan 24 TaskGraphCache pattern
S2.3: Tables: `options` (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP), `api_keys` (provider TEXT PRIMARY KEY, key TEXT)
S2.4: Encryption: Fernet key from `SOVEREIGNAI_ENCRYPTION_KEY` env var or `.secrets/fernet.key` (gitignored). `.secrets/` directory created with `0700` if missing. Key file mode `0600`. Runtime check: if key file permissions > 0600, log WARNING and refuse to start. Key must be 32-byte url-safe base64. Provide `python -m sovereignai.options.generate_key` helper. Precedence: env var wins; if both present with different values, log WARNING and use env var. If both present, log WARNING that key file is ignored. Empty env var string treated as unset (fall through to key file). Fail-closed: if encrypted data exists and key is invalid/missing, refuse to start. Rotation: new key encrypts new data, old key decrypts legacy for 30 days. Define primary+previous key rotation procedure.
S2.5: Test: `pytest app/sovereignai/tests/test_options_backend.py -v`

## S3 — Migration System

S3.1: Create `app/sovereignai/options/migrations.py` — versioned schema upgrades
S3.2: Table: `schema_version` (version INTEGER)
S3.3: Migration script: `migrate_v1_to_v2.py` pattern
S3.4: Test: `pytest app/sovereignai/tests/test_options_migrations.py -v`

## S4 — Event Integration

S4.1: On any setting change, emit `options.changed` event via Plan 22 EventBus
S4.2: SSE endpoint: `/api/options/stream` for real-time UI updates
S4.3: Commit-then-publish: write to DB before emitting event. If publish fails after successful commit, log warning. Do NOT roll back. SSE is best-effort; consumers reconcile via `GET /api/options` (full refresh) or `GET /api/options/stream?since=<last_event_id>` (delta). Document subscriber-side reconciliation: poll every 30s on reconnect, refresh on startup. Outbox/retry is v2 scope per DD-28.3.
S4.4: Test: `pytest app/sovereignai/tests/test_options_events.py -v`

## S5 — API Layer

S5.1: FastAPI routes: GET /api/options, PUT /api/options/{key}, DELETE /api/options/{key}
S5.2: DELETE guarded by `confirm_destructive` flag; refuses without `?force=true`, returns 409 Conflict with body `{ "error": "destructive_operation_requires_force", "detail": "Add ?force=true to confirm" }`. Idempotent: returns 404 if target no longer exists.
S5.3: Validation: Pydantic models enforce type safety
S5.4: Test: `pytest app/sovereignai/tests/test_options_api.py -v`

## S6 — AR Checks

S6.1: Add `check_options_encryption_at_rest.py` — verify API keys never stored plaintext
S6.2: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
