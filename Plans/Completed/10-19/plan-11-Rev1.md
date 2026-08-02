Depends on: prompt-10 (Scan 10)
Vision principles: P3 (memory is modular), P9 (no silent data loss), P14 (provenance)
Open questions resolved: Q3 (memory abstraction), Q14 (persistence — partial, in-memory → durable)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-10 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules:
- **OR54**: Memory backends are pluggable components discovered via the CapabilityGraph, not hardcoded in the core. The Librarian queries the graph for backends declaring `memory_storage` and `memory_query` capabilities. Source: Plan 11.
- **OR55**: The SQLite memory database file lives at `~/.sovereignai/memory.db` and is created automatically on first access. The directory is created with `os.makedirs(..., exist_ok=True)`. Source: Plan 11.
- **OR56**: Crash recovery replays the last incomplete trace from trace memory on startup. If the last trace has state != COMPLETE and != FAILED, the system emits a WARN trace and prompts the user via the CapabilityAPI (which the web UI consumes). Source: Plan 11.

Commit: `docs: add OR54-OR56 for prompt-11`

---

## Plan Body

### S1 — Create sovereignai/librarian/librarian.py

The Librarian is the memory router. It does not store data itself — it routes queries to backends based on capability.

**Constructor** (≤15 args per AR5):
```python
def __init__(
    self,
    capability_graph: CapabilityGraph,
    trace: TraceEmitter,
) -> None:
```

**Methods**:
- `store(memory_type: str, key: str, data: dict, metadata: dict = None) -> bool`: Route store request to backend declaring `memory_storage` for `memory_type`.
- `query(memory_type: str, query: dict) -> list[dict]`: Route query to backend declaring `memory_query` for `memory_type`. Scatter-gather if multiple backends match.
- `delete(memory_type: str, key: str) -> bool`: Route delete to appropriate backend.
- `_route(memory_type: str, capability: str) -> list[ComponentId]`: Query CapabilityGraph for backends.

**Memory types** (hardcoded enum for v1):
- `episodic` — conversation history, ordered events
- `procedural` — learned patterns, routing decisions
- `trace` — debug logs, observability
- `working` — volatile, in-process, task-scoped

### S2 — Create sovereignai/memory/episodic_backend.py

SQLite backend for episodic memory.

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    component TEXT NOT NULL,
    task_id TEXT,
    event_type TEXT NOT NULL,
    data TEXT NOT NULL  -- JSON
);
CREATE INDEX idx_episodes_task ON episodes(task_id);
CREATE INDEX idx_episodes_time ON episodes(timestamp);
```

**Methods**:
- `store(key: str, data: dict, metadata: dict) -> bool`: Insert into episodes table.
- `query(query: dict) -> list[dict]`: Query by time range, component, task_id, event_type.
- `delete(key: str) -> bool`: Delete by id.

**Manifest**: `adapters/internal/episodic_memory/manifest.toml`
```toml
[component]
id = "episodic_memory"
name = "Episodic Memory (SQLite)"
version = "0.1.0"
author = "user"

[[capabilities]]
category = "memory_storage"
name = "episodic"
priority = 100

[[capabilities]]
category = "memory_query"
name = "episodic"
priority = 100
```

### S3 — Create sovereignai/memory/procedural_backend.py

JSON file backend for procedural memory.

**Storage**: `~/.sovereignai/procedural_memory.json`

**Schema**:
```json
{
  "patterns": [
    {
      "id": "uuid",
      "pattern": "...",
      "confidence": 0.85,
      "last_used": "iso_timestamp",
      "success_count": 12,
      "failure_count": 2
    }
  ]
}
```

**Methods**:
- `store(key: str, data: dict, metadata: dict) -> bool`: Append to patterns list, write file.
- `query(query: dict) -> list[dict]`: Filter by pattern match, confidence threshold, last_used.
- `delete(key: str) -> bool`: Remove by id, write file.

**Manifest**: `adapters/internal/procedural_memory/manifest.toml`

### S4 — Create sovereignai/memory/working_backend.py

In-memory backend for working memory (already exists implicitly in TaskStateMachine, now formalized).

**Storage**: Python dict, task-scoped, auto-cleanup on task completion.

**Methods**:
- `store(key: str, data: dict, metadata: dict) -> bool`: Store in dict.
- `query(query: dict) -> list[dict]`: Lookup by key or task_id.
- `delete(key: str) -> bool`: Remove from dict.
- `cleanup(task_id: str) -> None`: Remove all entries for task_id.

**Manifest**: `adapters/internal/working_memory/manifest.toml`

### S5 — Create sovereignai/memory/trace_backend.py

SQLite backend for trace memory (durable version of TraceEmitter's in-memory storage).

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    level TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    trace_id TEXT NOT NULL
);
CREATE INDEX idx_traces_trace_id ON traces(trace_id);
CREATE INDEX idx_traces_time ON traces(timestamp);
```

**Integration with TraceEmitter**: The trace backend subscribes to TraceEmitter events and persists them. On startup, it replays the last N traces (configurable, default 1000) into TraceEmitter's in-memory buffer.

**Manifest**: `adapters/internal/trace_memory/manifest.toml`

### S6 — Update main.py composition root

Register all memory backends in `build_container()`:
```python
# 10. EpisodicMemoryBackend
from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
episodic = EpisodicMemoryBackend(trace=trace)
container.register_singleton(EpisodicMemoryBackend, episodic)

# 11. ProceduralMemoryBackend
from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
procedural = ProceduralMemoryBackend(trace=trace)
container.register_singleton(ProceduralMemoryBackend, procedural)

# 12. WorkingMemoryBackend
from sovereignai.memory.working_backend import WorkingMemoryBackend
working = WorkingMemoryBackend(trace=trace)
container.register_singleton(WorkingMemoryBackend, working)

# 13. TraceMemoryBackend
from sovereignai.memory.trace_backend import TraceMemoryBackend
trace_backend = TraceMemoryBackend(trace=trace)
container.register_singleton(TraceMemoryBackend, trace_backend)

# 14. Librarian
from sovereignai.librarian.librarian import Librarian
librarian = Librarian(capability_graph=container.retrieve(CapabilityGraph), trace=trace)
container.register_singleton(Librarian, librarian)
```

### S7 — Crash recovery

On startup (in `main.py` or as a startup event in the web server):
```python
# Check for incomplete traces
trace_backend = container.retrieve(TraceMemoryBackend)
last_trace = trace_backend.get_last_incomplete_trace()
if last_trace:
    trace.emit(TraceLevel.WARN, "recovery", f"Incomplete trace found: {last_trace.trace_id}. State: {last_trace.state}")
    # Emit event for UI to consume
    bus.publish("recovery.incomplete_trace", {
        "trace_id": last_trace.trace_id,
        "state": last_trace.state,
        "message": "Resume or discard?"
    })
```

The web UI (Plan 8) listens for `recovery.incomplete_trace` events and shows a dialog.

### S8 — Tests

- `tests/test_librarian.py`: Test routing, scatter-gather, missing backend handling.
- `tests/test_episodic_backend.py`: Test store/query/delete, time range queries, task_id filtering.
- `tests/test_procedural_backend.py`: Test store/query/delete, confidence filtering, JSON file integrity.
- `tests/test_working_backend.py`: Test store/query/delete, cleanup, size limits.
- `tests/test_trace_backend.py`: Test persistence, replay, last incomplete trace detection.
- `tests/test_crash_recovery.py`: Test incomplete trace detection, event emission, UI integration.

---

## STOP Conditions

- If Librarian constructor exceeds 15 arguments, STOP.
- If any backend fails to degrade gracefully (e.g., SQLite file locked, JSON file corrupted), STOP.
- If crash recovery blocks startup for more than 5 seconds, STOP.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/librarian/librarian.py`
- `sovereignai/librarian/__init__.py`
- `sovereignai/memory/episodic_backend.py`
- `sovereignai/memory/procedural_backend.py`
- `sovereignai/memory/working_backend.py`
- `sovereignai/memory/trace_backend.py`
- `adapters/internal/episodic_memory/manifest.toml`
- `adapters/internal/procedural_memory/manifest.toml`
- `adapters/internal/working_memory/manifest.toml`
- `adapters/internal/trace_memory/manifest.toml`
- `tests/test_librarian.py`
- `tests/test_episodic_backend.py`
- `tests/test_procedural_backend.py`
- `tests/test_working_backend.py`
- `tests/test_trace_backend.py`
- `tests/test_crash_recovery.py`

## Files WILL Edit

- `sovereignai/main.py` (extend build_container)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (core is sacred per P1)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-11`. Update CHANGELOG, PLANS.md.
