# SovereignAI -- Models Panel Drill-Down Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`, `SovereignAI_Cross_Department_Messaging_Design_v1.0.md`, `SovereignAI_Hardware_SSE_Streaming_Design_v1.0.md`, `SovereignAI_Options_Panel_Persistence_Design_v1.0.md`

---

## 1. Context

**Gap**: #13 -- Models Panel Drill-Down  
**Problem**: The v1 Models panel is a flat sortable table. The models-panel-spec.md describes a 4-level drill-down tree (Provider → Family → Model → Version) with offline browse capability. This was deferred post-Plan-19.  
**Scope**: How to implement the drill-down catalog with sync, persistence, and UI.

---

## 2. Design Decision

**DD-21.13.1**: Models panel drill-down (Proposed, P4/P5/AR6/AR21/AR25/AR26-aligned): 4-table normalized SQLite schema per existing models-panel-spec.md Section 3 (providers, families, models, model_versions). Foreign-key linked with indexes on FK columns. 4 cheap indexed SELECTs render the full drill-down tree (one per level). No recursive CTE (depth is fixed at 4), no materialized path (no subtree queries needed).

---

## 3. Schema

Per models-panel-spec.md Section 3:

```sql
CREATE TABLE providers (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    capabilities TEXT,  -- JSON array: ["chat", "embeddings", "vision"]
    is_installed BOOLEAN NOT NULL DEFAULT 0,
    last_synced_at TEXT,
    sync_status TEXT DEFAULT 'idle',
    sync_error TEXT,
    model_count INTEGER DEFAULT 0
);

CREATE TABLE families (
    id TEXT PRIMARY KEY,
    provider_id TEXT NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    FOREIGN KEY (provider_id) REFERENCES providers(id)
);
CREATE INDEX idx_families_provider ON families(provider_id);

CREATE TABLE models (
    id TEXT PRIMARY KEY,
    family_id TEXT NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    FOREIGN KEY (family_id) REFERENCES families(id)
);
CREATE INDEX idx_models_family ON models(family_id);

CREATE TABLE model_versions (
    id TEXT PRIMARY KEY,
    model_id TEXT NOT NULL,
    name TEXT NOT NULL,
    quant TEXT,
    size_mb INTEGER,
    vram_mb_estimate INTEGER,
    tokens_per_sec INTEGER,
    is_downloaded BOOLEAN DEFAULT 0,
    raw_metadata TEXT,  -- JSON for forward-compat
    FOREIGN KEY (model_id) REFERENCES models(id)
);
CREATE INDEX idx_versions_model ON model_versions(model_id);
```

**capabilities**: JSON array justified — short string list, no join table benefit.
**raw_metadata**: JSON for forward-compat per spec. Not queried.

---

## 4. Why Not Other Options

### 4.1 A -- Adjacency List (parent_id + recursive CTE)
- **Why rejected**: Fixed-depth hierarchy (4 levels). Recursive CTE adds complexity for no benefit when depth is known at design time. One table with parent_id conflates 4 distinct entity types.
- **Consequence**: CTE can't fully use indexes. Self-referential schema is less clear.

### 4.2 C -- Materialized Path
- **Why rejected**: Solves subtree queries ("all descendants of node X"), which the models panel doesn't need. Path maintenance on parent move is brittle.
- **Consequence**: LIKE prefix matches are moderate index efficiency. Path rewrites on rename.

### 4.3 Auto-Sync Background Job
- **Why rejected**: P5 violation. Ship manual sync only in v1. Auto-sync is opt-in config added when concrete need arrives.
- **Consequence**: Options setting can ship first (no-op until job exists). P5-clean.

---

## 5. DatabaseProvider Extension

Per AR26: "health_check() returns typed dataclass; init no I/O -- lazy in start()/list_models()."

```python
@dataclass(frozen=True)
class DatabaseStatus:
    installed: bool
    last_synced_at: datetime | None
    sync_status: SyncStatus  # IDLE | SYNCING | ERROR
    sync_error: str | None
    model_count: int  # cached count for badge

class SyncStatus(Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    ERROR = "error"
```

**Single source of truth**: Both Options panel and Models panel consume DatabaseStatus via capability API. No UI-local state copies per AR2/AR19.

---

## 6. Sync Semantics

### 6.1 Manual Sync (v1)
- Trigger: Options panel "Update Databases" button
- Scope: Full refresh per provider in a transaction (OR50/AR21)
- Behavior: Delete existing provider data, re-import from source

### 6.2 Auto-Sync (deferred per P5)
- Setting stored via DD-21.15.1 OptionsBackend
- Background job ships when concrete need arrives
- Setting exists but no-op until job implemented

### 6.3 Sync Progress (SSE)
```
POST /api/catalog/sync -> kicks off sync job, returns job_id
GET /api/catalog/sync/{job_id}/stream -> SSE:
  event: sync.progress {"families": 12, "models": 45, "versions": 120}
  event: sync.completed {"total": 120}
  event: sync.error {"message": "..."}
```

**Pattern**: Same as DD-21.5.1 (hardware SSE) and AR24 (trace SSE). One SSE pattern for all streaming core data.

---

## 7. REST Endpoints

```python
@app.get("/api/catalog/providers")
def list_providers() -> list[ProviderResponse]: ...

@app.get("/api/catalog/families")
def list_families(provider_id: str) -> list[FamilyResponse]: ...

@app.get("/api/catalog/models")
def list_models(family_id: str) -> list[ModelResponse]: ...

@app.get("/api/catalog/versions")
def list_versions(model_id: str) -> list[VersionResponse]: ...

@app.post("/api/catalog/sync")
def kickoff_sync() -> SyncJobResponse: ...

@app.get("/api/catalog/sync/{job_id}/stream")
def sync_progress_stream(job_id: str) -> StreamingResponse: ...  # SSE
```

---

## 8. UI Behavior

Per models-panel-spec.md Section 6:
- **Drill-down tree**: Provider tab → Family list → Model list → Version detail
- **Empty state**: "No catalog data yet -- go to Options → Update Databases."
- **Stale indicator**: `last_synced_at` displayed in panel header
- **Badges**: Model count per provider/family

---

## 9. VRAM Estimation

Per models-panel-spec.md Section 4:
```python
def estimate_vram_mb(context_length: int, quantization_bits: float, 
                     hidden_size: int, num_layers: int) -> int:
    return int((context_length * hidden_size * 2 + 
                hidden_size * hidden_size * num_layers * 4 * quantization_bits / 32) / (1024 * 1024))
```

Already used by Plan 18's runtime fit check. Applied at catalog time during sync.

---

## 10. Rationale

| Principle | How B Honors It |
|-----------|----------------|
| P4 (local-first) | SQLite catalog. No cloud dependency. Offline browse. |
| P5 (no speculative contracts) | Manual sync in v1. Auto-sync deferred. |
| AR6 (no context bags) | Typed schema. FK constraints. Indexed columns. |
| AR21 (atomic writes) | Full-refresh-per-provider in transaction. |
| AR25 (root-level packages) | databases/ for catalog, services/ for runtime. |
| AR26 (typed health_check) | DatabaseStatus with sync fields. |

---

## 11. Cross-DD Consistency

| DD | How B Uses It |
|----|---------------|
| DD-21.5.1 (hardware SSE) | Same SSE pattern for sync progress. ✓ |
| DD-21.15.1 (options persistence) | Sync settings stored via OptionsBackend. ✓ |
| DD-20.10.4/9 (events) | Sync events as Pydantic payloads in EventRegistry. ✓ |
| DD-20.10.8 (persistence) | Sync events persist to episodic memory. ✓ |
| AR25 | databases/ for catalog, services/ for runtime. ✓ |
| AR26 | Extended DatabaseStatus. ✓ |

No conflicts.

---

## 12. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Auto-sync | User demand | Background job + OptionsBackend setting |
| Incremental sync | Large catalog | Diff-based update instead of full refresh |
| Model download | User clicks "Download" | Integration with adapter download APIs |
| VRAM calculator | User wants custom estimate | Expose estimate_vram_mb() via capability API |

---

## 13. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.13.1 | Should sync support incremental updates (diff) for large catalogs? | Deferred |
| Q-21.13.2 | Should model download progress be tracked in the catalog? | Deferred |
| Q-21.13.3 | Should the catalog store benchmark scores (tokens/sec)? | Deferred |

---

## 14. Implementation Plan

**Plan 21.13** (Models Panel Drill-Down):
- S1: 4-table SQLite schema
- S2: DatabaseProvider health_check() extension
- S3: Sync modules (one per provider)
- S4: REST endpoints (4 list + sync kickoff + SSE)
- S5: UI drill-down tree
- S6: Tests for sync, query, VRAM estimation

**Depends on**: Plan 21.15 (Options Persistence) for sync settings storage.

---

*End of document.*
