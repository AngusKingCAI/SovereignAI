# SovereignAI -- Options Panel Persistence Design Document v1.0

**Status**: Draft -- approved for implementation  
**Date**: 2026-07-03  
**Author**: Architect  
**Depends on**: `../PRINCIPLES.md`, `../AGENTS.md`, `../DECISIONS.md`, `../AI_HANDOFF.md`, `SovereignAI_Skill_Agent_System_Design_v1.0.md`, `SovereignAI_Cross_Department_Messaging_Design_v1.0.md`

---

## 1. Context

**Gap**: #15 -- Options Panel Persistence  
**Problem**: The Options panel UI exists but settings aren't persisted. No config file, no schema, no validation. Changes are lost on restart.  
**Scope**: How the Options panel saves, loads, and validates settings with type safety.

---

## 2. Design Decision

**DD-21.15.1**: Options panel persistence (Proposed, P4/P5/AR6/AR21/AR22-aligned): SQLite backend with Pydantic-validated typed settings. One row per settings category (model, worker, display, etc.), value column stores serialized Pydantic model JSON. get(category, model_cls) -> T validates on read. set(category, value: BaseModel) validates on write. AR21 atomic writes (WAL + transactions). AR22 trace on every get/set.

---

## 3. Schema

```sql
CREATE TABLE options (
    category TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    version TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

**One row per category**, not per individual option. Pydantic handles the nested structure. Fewer rows, simpler schema.

**Why not per-option rows**: Options are retrieved by category ("give me all model settings"), not queried by attribute ("find all settings with value > X"). EAV would be overkill -- appropriate for graph memory (DD-21.12.1) but not options.

---

## 4. Interface

```python
class OptionsBackend:
    def __init__(self, db_path: Path, trace: TraceEmitter) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS options ("
            "    category TEXT PRIMARY KEY,"
            "    value TEXT NOT NULL,"
            "    version TEXT NOT NULL,"
            "    updated_at TEXT NOT NULL"
            ")"
        )
        self._trace = trace

    def get(self, category: str, model_cls: type[T]) -> T:
        row = self._conn.execute(
            "SELECT value FROM options WHERE category = ?", (category,)
        ).fetchone()
        if row:
            return model_cls.model_validate_json(row[0])
        return model_cls()  # defaults

    def set(self, category: str, value: BaseModel) -> None:
        self._conn.execute(
            "INSERT INTO options (category, value, version, updated_at) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(category) DO UPDATE SET "
            "    value = excluded.value,"
            "    version = excluded.version,"
            "    updated_at = excluded.updated_at",
            (category, value.model_dump_json(), "1.0.0",
             datetime.now(timezone.utc).isoformat())
        )
        self._conn.commit()
        self._trace.emit(
            component="options",
            level=TraceLevel.INFO,
            event="options.updated",
            category=category,
            version="1.0.0"
        )  # AR22
```

---

## 5. Settings Classes

```python
class ModelSettings(BaseModel):
    default_model: str = "llama3.2"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=32768)

class WorkerSettings(BaseModel):
    max_workers: int = Field(default=4, ge=1, le=16)
    timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0)

class DisplaySettings(BaseModel):
    theme: str = "dark"
    font_size: int = Field(default=14, ge=8, le=32)
    sidebar_width: int = Field(default=250, ge=150, le=400)

class HardwareSettings(BaseModel):
    gpu_offload: bool = True
    vram_limit_mb: int = Field(default=4096, ge=512, le=65536)
    cpu_threads: int = Field(default=4, ge=1, le=32)
```

**Forward compatibility per DD-20.10.9**:
- Minor bump: Add optional field with default. Same class.
- Major bump: New class (e.g., `ModelSettings_v2`). Old class stays for read.

---

## 6. Why Not Other Options

### 6.1 A -- SQLite + JSON Blob + Any Interface
- **Why rejected**: AR6 violation at interface layer. `get() -> Any` defeats type safety. mypy can't catch `options.get("max_workers", "four")` (wrong default type), `options.set("max_workers", -1)` (invalid value), `options.set("max_workers", 4.0)` (float vs int).
- **Consequence**: Runtime errors instead of static analysis. Silent failures propagate.

### 6.2 B -- TOML File
- **Why rejected**: No atomic writes (AR21 violation). New dependency. File corruption risk on crash. No type safety.
- **Consequence**: Settings lost on crash. Human-editable but unvalidated.

### 6.3 C -- Pydantic Settings / Env Vars
- **Why rejected**: Read-only at runtime. Requires restart. Not UI-editable. Wrong use case for a settings panel.
- **Consequence**: User changes in UI don't persist without restart. UX broken.

### 6.4 D -- Hybrid SQLite + TOML
- **Why rejected**: Two sources of truth. TOML dependency. P5 violation (speculative complexity).
- **Consequence**: Sync issues between SQLite and TOML. Which wins?

### 6.5 EAV Pattern
- **Why rejected**: Overkill for category-keyed retrieval. Appropriate for graph memory (DD-21.12.1) where entities have arbitrary attributes. Options have fixed schemas per category.
- **Consequence**: Unnecessary complexity. 5 tables instead of 1.

---

## 7. AR6 Compliance

| Layer | A (rejected) | E (accepted) |
|-------|-------------|--------------|
| Storage | JSON blob (adjacent) | JSON blob (adjacent) -- same |
| Interface | `get() -> Any` | `get(category, model_cls) -> T` |
| Validation | None | Pydantic Field constraints |
| Type evolution | Ad hoc magic strings | DD-20.10.9 pattern |
| IDE autocomplete | None | mypy knows types |

E fixes AR6 at the interface layer without changing the storage choice. Storage JSON blob is acceptable -- options don't need indexed queries.

---

## 8. OR7 Compliance

**A's example used `datetime.utcnow().isoformat()`** -- OR7 violation. `utcnow()` returns naive datetime.

**E uses `datetime.now(timezone.utc).isoformat()`** -- OR7 compliant. timezone-aware.

**Flag for executor**: Any existing code using `utcnow()` is an OR7 violation to fix on touch.

---

## 9. Rationale

| Principle | How E Honors It |
|-----------|----------------|
| P4 (local-first) | SQLite is already a dependency. No new libraries. |
| P5 (no speculative contracts) | One table, typed interface. No TOML, no EAV, no env vars. |
| AR6 (no context bags) | `get() -> T` instead of `get() -> Any`. Pydantic validation. |
| AR21 (atomic writes) | WAL + transactions. No corruption on crash. |
| AR22 (observability) | Trace on every get/set. Audit trail. |
| DD-20.10.9 (versioning) | Forward-compatible Pydantic models. |

---

## 10. UI Integration

```python
# Web UI (FastAPI)
@app.get("/api/options/{category}")
def get_options(category: str) -> BaseModel:
    model_cls = SETTINGS_REGISTRY[category]
    return options_backend.get(category, model_cls)

@app.put("/api/options/{category}")
def update_options(category: str, value: BaseModel) -> BaseModel:
    options_backend.set(category, value)
    return value

# TUI (Textual)
class OptionsPanel:
    def on_save(self, category: str, values: dict) -> None:
        model_cls = SETTINGS_REGISTRY[category]
        validated = model_cls.model_validate(values)
        options_backend.set(category, validated)
```

---

## 11. Extension Points

| Extension | Trigger | Interface |
|-----------|---------|-----------|
| Settings export/import | User wants to backup/restore | `export_to_json()` / `import_from_json()` |
| Settings migration | Major version bump | Migration function per DD-20.10.9 |
| Per-user settings | Multi-user support (P6 violation) | Add user_id column |
| Settings sync | Cloud backup (P4 violation) | Deferred |

---

## 12. Open Questions

| ID | Question | Status |
|----|----------|--------|
| Q-21.15.1 | Should settings support export/import (JSON backup)? | Deferred |
| Q-21.15.2 | Should UI show validation errors inline (Pydantic error messages)? | Deferred |
| Q-21.15.3 | Should settings changes trigger restart-required warnings? | Deferred |

---

## 13. Implementation Plan

**Plan 21.15** (Options Panel Persistence):
- S1: OptionsBackend class with SQLite schema
- S2: Settings classes (ModelSettings, WorkerSettings, DisplaySettings, HardwareSettings)
- S3: Web UI endpoints (`/api/options/{category}`)
- S4: TUI panel integration
- S5: Tests for validation, persistence, atomic writes

**Estimated**: ~150 lines (backend + 4 settings classes + tests).

---

*End of document.*
