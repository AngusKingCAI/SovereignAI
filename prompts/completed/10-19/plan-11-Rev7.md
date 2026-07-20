Depends on: prompt-10.5 (Rev5 — addresses Rev4 Round Table finding F1: trace subscriber metadata={} breaks crash recovery)
Vision principles: P3 (memory is modular), P9 (no silent data loss), P14 (provenance)
Open questions resolved: Q3 (memory abstraction), Q14 (persistence — partial, in-memory → durable)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-10.5 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full. Note the governance rules added in prompts 10.1–10.3 (these apply to this plan's execution and close):
- OR71 (run workflow commands verbatim — re-read `close.md` fresh, do not paraphrase)
- OR75/OR80/OR83 (`git add -A` for ALL commits — no explicit `git add <file>` lists; after every `git add -A`, run `git status -s` to verify staging is clean)
- OR76 (no premature tags — verify `git tag --list prompt-11` is empty before creating)
- OR77 (coverage mandatory at `/close` — STOP if >5% drop from baseline; current baseline: 94%, floor: 89%)
- OR78 (bandit reconciliation — update PLANS.md Low count at every `/close` where tests were added)
- OR82 (never `git mv` — use `mv` + `git add -A` + verify `git ls-files`)

S0.3 — Add new rules (revised from Rev2 per Round Table re-review):
- **OR54**: Memory backends are pluggable components discovered via the CapabilityGraph, not hardcoded in the core. The Librarian queries the graph for backends declaring `memory_storage` and `memory_query` capabilities. Routing is by capability `name` string — any backend declaring a new memory type name is routed to automatically. Source: Plan 11 Rev2 (F-15).
- **OR55**: Each SQLite memory backend owns a separate database file: `~/.sovereignai/episodic.db`, `~/.sovereignai/trace.db`. Procedural memory uses a JSON file at `~/.sovereignai/procedural_memory.json`. Working memory is in-process only. Source: Plan 11 Rev2 (F-3).
- **OR56** (revised): Crash recovery is automatic and non-blocking. On startup, if a `~/.sovereignai/.shutdown_marker` file exists (indicating a clean previous shutdown), skip recovery entirely. If the marker does NOT exist (indicating a crash), scan for tasks whose last `TaskStateChanged` event has a non-terminal state; mark each as FAILED with a WARN trace. Side effects are NOT replayed. The entire recovery loop is wrapped in `try/except` — on any failure, log to stderr and continue startup. Source: Plan 11 Rev3 (N5, N9).
- **OR66** (revised): All durable memory backends use atomic writes. SQLite backends use transactions (WAL mode, `busy_timeout=5000`). The JSON procedural backend writes to a temp file then `os.replace()`. No backend may use bare `open().write()`. The procedural backend's lock file is NEVER force-acquired — if the lock is held >5 seconds, the write fails with a WARN trace (preserving mutex safety per P9). Source: Plan 11 Rev3 (N8).

Commit: `docs: add OR54-OR56, OR66 for prompt-11`

---

## Plan Body

### S1 — Create sovereignai/librarian/librarian.py

(Unchanged from Rev2 — no findings against S1.)

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
- `store(memory_type: str, data: dict, metadata: dict = None) -> str`: Route store request to the highest-priority backend declaring `memory_storage` for `memory_type`. Returns the generated record id.
- `query(memory_type: str, query: dict) -> list[dict]`: Route query to backends declaring `memory_query` for `memory_type`. Scatter-gather if multiple backends match, with merge semantics per memory type.
- `delete(memory_type: str, record_id: str) -> bool`: Route delete to the backend that owns the record.
- `_route(memory_type: str, capability: str) -> list[ComponentId]`: Query CapabilityGraph for backends.

**Scatter-gather merge semantics** (unchanged from Rev2):
- `episodic`: union, dedupe by id, sort by timestamp ascending.
- `procedural`: union, dedupe by pattern id, keep highest confidence.
- `trace`: union, dedupe by id, sort by timestamp ascending.
- `working`: first-backend-wins.
- Future types: union, dedupe by id (documented default).

### S2 — Create sovereignai/memory/episodic_backend.py

(Unchanged from Rev2.)

**NOTE on manifest format**: All manifest files in this plan use `component_id = "..."` (NOT `id = "..."`). The manifest parser (verified in prompt-10.4) requires `component_id` as the field name inside the `[component]` table. Existing manifests (`skills/user/websearch_skill/manifest.toml`, `adapters/external/ollama_adapter/manifest.toml`) use this format — match them.

**Storage**: `~/.sovereignai/episodic.db`
**PRAGMAs**: `journal_mode=WAL`, `busy_timeout=5000`

**Schema**:
```sql
CREATE TABLE IF NOT EXISTS episodes (
    id TEXT PRIMARY KEY,
    timestamp REAL NOT NULL,
    component TEXT NOT NULL,
    task_id TEXT,
    event_type TEXT NOT NULL,
    data TEXT NOT NULL,
    metadata TEXT
);
CREATE INDEX IF NOT EXISTS idx_episodes_task ON episodes(task_id);
CREATE INDEX IF NOT EXISTS idx_episodes_time ON episodes(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodes_task_time ON episodes(task_id, timestamp);
```

**Methods**:
- `store(data: dict, metadata: dict = None) -> str`
- `query(query: dict) -> list[dict]` (supports `task_ids: list[str]` for batch via `WHERE task_id IN (?,?,...)`)
- `delete(record_id: str) -> bool`

### S3 — Create sovereignai/memory/procedural_backend.py

(Revised per Rev3 N8, N19.)

**Storage**: `~/.sovereignai/procedural_memory.json`

**Atomic write** (unchanged): temp file + `os.replace()`.

**File lock** (REVISED per N8 — no force-acquire):
```python
def _acquire_lock(self, timeout_s: float = 5.0) -> bool:
    """Try to acquire the lock file. Return True if acquired, False on timeout.

    NEVER force-acquires. If the lock is held longer than timeout_s,
    returns False (preserving mutex safety per P9).
    """
    import time
    lock_path = self._path + ".lock"
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            time.sleep(0.1)
    return False  # Timed out — do NOT force-acquire

def _release_lock(self) -> None:
    """Release the lock file."""
    lock_path = self._path + ".lock"
    try:
        os.unlink(lock_path)
    except FileNotFoundError:
        pass
```

**store() failure handling** (REVISED per N8):
```python
def store(self, data: dict, metadata: dict = None) -> str:
    """Store a pattern. Returns record id, or raises if lock acquisition fails."""
    if not self._acquire_lock():
        self._trace.emit(
            component="procedural_memory",
            level=TraceLevel.WARN,
            message="Procedural memory write skipped — lock held by another operation for >5s",
        )
        raise ProceduralMemoryLockTimeout("Lock acquisition timed out")
    try:
        # ... read, append, atomic-write ...
        if len(patterns) > MAX_PATTERNS:
            self.prune_low_confidence(0.3)
            # REVISED per N19: if still over cap, evict oldest by last_used
            while len(patterns) > MAX_PATTERNS:
                patterns.sort(key=lambda p: p.get("last_used", ""))
                patterns.pop(0)  # Evict oldest
        # ... atomic write ...
    finally:
        self._release_lock()
```

**Schema** (unchanged), **corruption recovery** (unchanged — rename to `.corrupted.{ts}`, start fresh, WARN).

### S4 — Create sovereignai/memory/working_backend.py

(Unchanged from Rev2.)

**Methods**: `store`, `query`, `delete`, `cleanup(task_id)`. Cleanup wired to `TaskStateChanged` in S6.

### S5 — Create sovereignai/memory/trace_backend.py

(Revised per Rev3 N2 — store signature unified to standard memory contract.)

**Storage**: `~/.sovereignai/trace.db`
**PRAGMAs**: WAL, `busy_timeout=5000`

**Schema** (unchanged from Rev2 — `correlation_id` + `task_state` columns):
```sql
CREATE TABLE IF NOT EXISTS traces (
    id TEXT PRIMARY KEY,
    timestamp REAL NOT NULL,
    level TEXT NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    correlation_id TEXT NOT NULL,
    task_id TEXT,
    task_state TEXT
);
CREATE INDEX IF NOT EXISTS idx_traces_correlation ON traces(correlation_id);
CREATE INDEX IF NOT EXISTS idx_traces_time ON traces(timestamp);
CREATE INDEX IF NOT EXISTS idx_traces_task ON traces(task_id);
```

**store() signature** (REVISED per N2 — unified to standard memory contract):
```python
def store(self, data: dict, metadata: dict = None) -> str:
    """Store a trace event. Conforms to the standard memory backend contract.

    Args:
        data: Trace event fields. Must contain: component (str), level (str),
            message (str), correlation_id (str). Optional: timestamp (float).
        metadata: Optional dict with task_id (str) and task_state (str).

    Returns:
        The generated record id (UUID string).
    """
    import uuid
    from sovereignai.shared.types import TraceEvent, TraceLevel, now_utc
    from datetime import datetime

    record_id = str(uuid.uuid4())
    event = TraceEvent(
        component=data["component"],
        level=TraceLevel(data["level"]),
        message=data["message"],
        timestamp=data.get("timestamp") or now_utc(),
        correlation_id=uuid.UUID(data["correlation_id"]),  # Rev7: use uuid.UUID not bare UUID
    )
    task_id = (metadata or {}).get("task_id")
    task_state = (metadata or {}).get("task_state")

    # INSERT into traces table ...
    return record_id
```

This makes `TraceMemoryBackend.store()` conform to the same `store(data: dict, metadata: dict) -> str` contract as every other memory backend. The Plan 13 conformance test now passes for the trace backend.

**Integration with TraceEmitter**: The subscriber callback (wired in S6) calls `trace_backend.store()` with `data={"component": e.component, "level": e.level.value, "message": e.message, "correlation_id": str(e.correlation_id)}` and `metadata={"task_id": ..., "task_state": ...}`.

**Other methods** (unchanged): `query`, `delete`.

**`get_last_task_states() -> dict[str, str]`** (Per Rev7 — SQL fixed: uses `MAX(timestamp)` not `MAX(id)` because `id` is UUID4 which is NOT monotonic):
```sql
SELECT task_id, task_state FROM traces
WHERE rowid IN (
    SELECT rowid FROM traces t1
    WHERE t1.task_id IS NOT NULL AND t1.task_state IS NOT NULL
    AND t1.timestamp = (
        SELECT MAX(timestamp) FROM traces t2
        WHERE t2.task_id = t1.task_id AND t2.task_state IS NOT NULL
    )
)
```
This returns the LAST recorded state for each task by `timestamp` (a `REAL` column that IS monotonically increasing). Per Rev7 Claude finding: the Rev6 SQL used `MAX(id)` on UUID4 strings — UUID4 is random, so string comparison is NOT temporal ordering. Using `MAX(timestamp)` fixes this. Without this fix, crash recovery would get the wrong state (whichever UUID sorts last lexicographically, not the most recent).

### S6 — Update main.py composition root

(Revised per Rev3 N20 — robust enum comparison in cleanup handler.)

```python
# 10-14. Register memory backends + Librarian (unchanged from Rev2)
# ...

# Wire TraceEmitter → TraceMemoryBackend (durable persistence)
# Per Rev5 F1: regular trace events do NOT carry task_state (TraceEvent has no such field).
# TaskStateChanged events are persisted separately by the subscriber below.
def _on_trace_emitted(event: TraceEvent) -> None:
    """Persist every trace event to the durable trace backend."""
    try:
        trace_backend.store(
            data={
                "component": event.component,
                "level": event.level.value,
                "message": event.message,
                "correlation_id": str(event.correlation_id),
            },
            metadata={},  # Regular traces have no task_state — that's fine.
        )
    except Exception:
        pass
trace.subscribe_callback(_on_trace_emitted)

# Per Rev5 F1: ALSO subscribe to TaskStateChanged events and persist them with
# task_id + task_state metadata. This populates the task_state column that
# get_last_task_states() queries for crash recovery. Without this, crash
# recovery finds no incomplete tasks (the Rev4 bug).
def _on_task_state_changed_persist(event: TaskStateChanged) -> None:
    """Persist task state transitions to the trace backend for crash recovery."""
    try:
        trace_backend.store(
            data={
                "component": "TaskStateMachine",
                "level": "info",
                "message": f"Task {event.task_id} transitioned {event.old_state} → {event.new_state}",
                "correlation_id": str(event.correlation_id) if hasattr(event, 'correlation_id') and event.correlation_id else str(new_correlation_id()),
            },
            metadata={
                "task_id": str(event.task_id),
                "task_state": event.new_state.value if hasattr(event.new_state, 'value') else str(event.new_state),
            },
        )
    except Exception:
        pass
bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed_persist, subscriber_id="trace_persist")  # Rev7: subscriber_id for unsubscribe tracking

# Wire WorkingMemoryBackend.cleanup to TaskStateChanged (per Rev3 N20)
def _on_task_state_changed(event: TaskStateChanged) -> None:
    """Free working memory when a task reaches a terminal state.

    Per Rev6: wrapped in try/except so a cleanup failure doesn't kill the dispatch loop
    (which would prevent the persist handler from running on future events).
    Ordering: this handler runs AFTER _on_task_state_changed_persist (registration order).
    """
    # Compare against enum VALUES for robustness against string deserialization
    terminal_states = (TaskState.COMPLETE.value, TaskState.FAILED.value)
    new_state_val = event.new_state.value if isinstance(event.new_state, TaskState) else str(event.new_state)
    if new_state_val in terminal_states:
        try:
            working_backend.cleanup(str(event.task_id))
        except Exception as e:
            trace.emit(
                component="working_memory",
                level=TraceLevel.WARN,
                message=f"Working memory cleanup failed for task {event.task_id}: {e}",
            )
bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed, subscriber_id="working_memory_cleanup")  # Rev7: subscriber_id for unsubscribe tracking
```

**`trace.subscribe_callback`** (unchanged from Rev2 — minimal core addition to `trace_emitter.py`).

### S7 — Crash recovery (non-blocking, automatic, failure-isolated)

(Revised per Rev3 N5 — shutdown marker; N9 — try/except isolation.)

```python
import sys, os

def run_crash_recovery(container, trace) -> None:
    """Run crash recovery on startup. Best-effort — never blocks startup.

    Per Rev3 N5: if a shutdown marker exists, the previous shutdown was clean — skip recovery.
    Per Rev3 N9: the entire recovery loop is wrapped in try/except — on any failure,
    log to stderr and continue.
    """
    marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
    try:
        if os.path.exists(marker_path):
            # Per Rev5 F6: validate marker content (magic string) before trusting it.
            # A partial/corrupted marker (from a crash mid-write) must NOT skip recovery.
            try:
                with open(marker_path, "r") as f:
                    content = f.read()
                if content.startswith("SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"):
                    # Valid marker — previous shutdown was clean
                    os.unlink(marker_path)
                    trace.emit(component="recovery", level=TraceLevel.INFO,
                               message="Clean shutdown detected — skipping crash recovery")
                    return
                else:
                    # Invalid marker content — treat as no marker (crash)
                    trace.emit(component="recovery", level=TraceLevel.WARN,
                               message="Shutdown marker exists but content invalid — treating as crash")
            except Exception:
                # Can't read marker — treat as no marker (crash)
                trace.emit(component="recovery", level=TraceLevel.WARN,
                           message="Shutdown marker unreadable — treating as crash")

        # No marker — previous shutdown was a crash. Run recovery.
        trace_backend = container.retrieve(TraceMemoryBackend)
        last_task_states = trace_backend.get_last_task_states()

        for task_id_str, state in last_task_states.items():
            if state in ("received", "queued", "executing"):
                trace.emit(
                    component="recovery",
                    level=TraceLevel.WARN,
                    message=f"Task {task_id_str} was incomplete (state={state}) at crash; marking as recovered-failed. Side effects not replayed.",
                    correlation_id=UUID(task_id_str) if _is_valid_uuid(task_id_str) else None,
                )
                trace_backend.store(
                    data={
                        "component": "recovery",
                        "level": "warn",
                        "message": f"recovered: incomplete at crash (was {state})",
                        "correlation_id": task_id_str if _is_valid_uuid(task_id_str) else str(new_correlation_id()),
                    },
                    metadata={"task_id": task_id_str, "task_state": "failed"},
                )
    except Exception as e:
        # N9: never let recovery break startup
        print(f"SovereignAI crash recovery failed (non-fatal): {e}", file=sys.stderr)
        trace.emit(component="recovery", level=TraceLevel.ERROR,
                   message=f"Crash recovery failed (non-fatal): {e}")

def on_clean_shutdown(container, trace) -> None:
    """Write shutdown marker on clean shutdown. Called from main.py shutdown handler.

    Per Rev5 F6: uses atomic write (temp + os.replace) and a magic string for
    validation. A partial write (crash mid-write) produces an invalid marker
    that is treated as 'no marker' (crash) on next startup.
    """
    marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
    magic = "SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"
    try:
        os.makedirs(os.path.dirname(marker_path), exist_ok=True)
        # Atomic write: temp file + os.replace (per OR66 pattern)
        tmp_path = marker_path + ".tmp"
        with open(tmp_path, "w") as f:
            f.write(magic + now_utc().isoformat())
        os.replace(tmp_path, marker_path)  # Atomic on Windows and POSIX
    except Exception:
        pass  # Best-effort — if marker missing on next start, recovery runs
```

**Wire `on_clean_shutdown`** to `main.py`'s shutdown handler (atexit or signal handler):
```python
import atexit
atexit.register(on_clean_shutdown, container, trace)
```

### S8 — Tests

(Updated per Rev3 changes.)

- `tests/test_librarian.py`: Test routing, scatter-gather, missing backend handling.
- `tests/test_episodic_backend.py`: Test store/query/delete, batch query, separate db isolation.
- `tests/test_procedural_backend.py`: Test store/query/delete, atomic write, corruption recovery, **lock timeout returns False (N8)**, **hard cap enforcement (N19)**.
- `tests/test_working_backend.py`: Test cleanup, **enum/string comparison robustness (N20)**.
- `tests/test_trace_backend.py`: Test persistence, query, `get_last_task_states()`, **store() accepts standard contract (N2)**.
- `tests/test_crash_recovery.py`: Test incomplete task detection, **shutdown marker skips recovery (N5)**, **recovery failure does not block startup (N9)**, non-blocking.

---

## STOP Conditions

- If Librarian constructor exceeds 15 arguments, STOP.
- If any backend fails to degrade gracefully (SQLite locked >5s, JSON corrupted), STOP. Graceful degradation = log WARN + continue; never raise.
- If crash recovery blocks startup for more than 2 seconds, STOP.
- If procedural memory atomic write loses data on simulated crash, STOP.
- If procedural memory lock is force-acquired (violating mutex safety per N8), STOP.
- If crash recovery raises an unhandled exception that blocks startup (violating N9), STOP.
- If coverage drops below 89% (5% drop from 94% baseline), STOP (per OR77).
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/librarian/librarian.py`
- `sovereignai/librarian/__init__.py`
- `sovereignai/memory/__init__.py`
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

- `sovereignai/main.py` (extend build_container; wire trace subscriber; wire cleanup callback with robust enum comparison; add crash recovery + shutdown marker + atexit handler)
- `sovereignai/shared/trace_emitter.py` (add `subscribe_callback` — minimal core addition)
- `sovereignai/shared/types.py` (add `_is_valid_uuid` helper)

## Files WILL NOT Edit

- Any other file in `sovereignai/shared/`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-11`. Update CHANGELOG, PLANS.md.

## Adjudication summary (Rev2 → Rev3)

New findings addressed: N2 (trace store signature unified), N5 (shutdown marker), N8 (no force-acquire), N9 (try/except isolation), N14 (guard logging — in Plan 14), N19 (hard cap eviction), N20 (enum/string comparison), N22 (trace DB durability — DEBT.md entry).

DEBT.md additions: dedicated task-state ledger (N22); batched/background trace inserts (N15).
