# Plan 15.1 Rev2 — Fix Critical Issues from Log Scan

**Clean restart.** Previous attempt (15.1 Rev1) failed due to terminal timeouts and indentation errors. This version is simpler, more prescriptive, and uses exact line numbers from the verified prompt-15 state.

Depends on: prompt-15
Skips Round Table (per User veto).

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-15` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full.

**S0.3** — Add OR87-OR90 + L41-L47 (see log-scan-findings-11-15.md for full text). Commit: `docs: add OR87-OR90, L41-L47 for prompt-15.1`

---

## S1 — Create `tests/conftest.py`

**Create new file** `tests/conftest.py` with exactly this content:

```python
"""Test configuration — sets SOVEREIGNAI_TEST_MODE before any tests run."""
import os

os.environ["SOVEREIGNAI_TEST_MODE"] = "1"
```

This MUST be the first file loaded by pytest. It sets the env var before any test imports `main.py`.

---

## S2 — Add `_test_mode` to `build_container()` in `main.py`

**File**: `sovereignai/main.py`

**Find** (line ~60, the first line inside `build_container` after the docstring):
```python
    # Create container with event_bus and trace for remove() support (per Rev9)
    # We'll set these after they're created
    container = DIContainer()
```

**Replace with** (4-space indent — INSIDE the function):
```python
    import os
    _test_mode = os.environ.get("SOVEREIGNAI_TEST_MODE") == "1"

    # Create container with event_bus and trace for remove() support (per Rev9)
    container = DIContainer()
```

**CRITICAL**: The `import os` and `_test_mode = ...` lines MUST be indented 4 spaces (inside the function). If they're at column 0, they're at module level and won't work. After editing, verify:
```bash
.venv/Scripts/python.exe -c "import ast; ast.parse(open('sovereignai/main.py').read()); print('syntax OK')"
```

---

## S3 — Register all 4 memory backends with test-mode `:memory:` paths

**File**: `sovereignai/main.py`

**Find** (lines 161-174, the current memory section):
```python
    # 12. Register memory backends + Librarian (Plan 11)
    # NOTE: Memory backends are initialized but their persistence is disabled in tests
    # to avoid database file I/O during test runs. The backends are functional for
    # in-memory operations.
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.working_backend import WorkingMemoryBackend

    # Instantiate working memory backend (in-process, no disk I/O)
    working_backend = WorkingMemoryBackend(trace=trace)
    container.register_singleton(WorkingMemoryBackend, working_backend)

    # Instantiate and register Librarian
    librarian = Librarian(capability_graph=graph, trace=trace)
    container.register_singleton(Librarian, librarian)
```

**Replace with**:
```python
    # 12. Register memory backends + Librarian (Plan 11)
    # Per L41 fix: ALL backends registered. Test mode uses :memory: SQLite.
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.memory.working_backend import WorkingMemoryBackend
    from sovereignai.memory.trace_backend import TraceMemoryBackend

    episodic_backend = EpisodicMemoryBackend(
        trace=trace, db_path=":memory:" if _test_mode else None
    )
    container.register_singleton(EpisodicMemoryBackend, episodic_backend)

    procedural_backend = ProceduralMemoryBackend(
        trace=trace, file_path=None if _test_mode else None
    )
    container.register_singleton(ProceduralMemoryBackend, procedural_backend)

    working_backend = WorkingMemoryBackend(trace=trace)
    container.register_singleton(WorkingMemoryBackend, working_backend)

    trace_backend = TraceMemoryBackend(
        trace=trace, db_path=":memory:" if _test_mode else None
    )
    container.register_singleton(TraceMemoryBackend, trace_backend)

    if not _test_mode:
        librarian = Librarian(capability_graph=graph, trace=trace)
        container.register_singleton(Librarian, librarian)
```

**NOTE**: The backends need to accept `db_path` and `file_path` parameters. Check if they already do — if not, add them (see S3.1 below).

### S3.1 — Add `db_path` parameter to backend constructors (if missing)

**File**: `sovereignai/memory/episodic_backend.py`

If the constructor doesn't already accept `db_path`, change:
```python
def __init__(self, trace: TraceEmitter) -> None:
    self._db_path = os.path.expanduser("~/.sovereignai/episodic.db")
```
To:
```python
def __init__(self, trace: TraceEmitter, db_path: str | None = None) -> None:
    self._db_path = db_path if db_path else os.path.expanduser("~/.sovereignai/episodic.db")
```

And in `_initialize_db` (or wherever it connects):
```python
if self._db_path != ":memory:":
    os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
self._conn = sqlite3.connect(self._db_path)
```

**File**: `sovereignai/memory/trace_backend.py` — same pattern, default `~/.sovereignai/trace.db`.

**File**: `sovereignai/memory/procedural_backend.py` — same pattern with `file_path`:
```python
def __init__(self, trace: TraceEmitter, file_path: str | None = None) -> None:
    self._path = file_path  # None = in-memory only
    if self._path:
        self._ensure_file_exists()
    else:
        self._patterns = {"schema_version": 1, "patterns": []}
```

In `store()`, `query()`, `delete()` — skip file I/O when `self._path is None`.

---

## S4 — Guard ALL production-only code with `if not _test_mode:`

**File**: `sovereignai/main.py`

Wrap the following blocks in `if not _test_mode:`. In test mode, these are ALL skipped:

### S4.1 — HardwareProbe + TeacherWorker (lines ~216-230)

**Find**:
```python
    # 16. HardwareProbe — no dependencies, singleton (Plan 14)
    from sovereignai.shared.hardware_probe import HardwareProbe
    hardware_probe = HardwareProbe()
    container.register_singleton(HardwareProbe, hardware_probe)

    # 17. Teacher worker ...
    from sovereignai.workers.education.teacher_worker import TeacherWorker
    ...
```

**Wrap in**:
```python
    if not _test_mode:
        # 16. HardwareProbe
        from sovereignai.shared.hardware_probe import HardwareProbe
        hardware_probe = HardwareProbe()
        container.register_singleton(HardwareProbe, hardware_probe)

        # 17. Teacher worker
        from sovereignai.workers.education.teacher_worker import TeacherWorker
        ...
```

### S4.2 — Self-correction skill (search for `SelfCorrectionSkill`)

Wrap the entire block that imports and registers `SelfCorrectionSkill` + subscribes to `TASK_STATE_CHANNEL` in `if not _test_mode:`.

### S4.3 — Crash recovery (lines ~249-260)

**Find**:
```python
    def run_crash_recovery(container, trace):
        ...
        pass  # Disabled
```

**Replace with**:
```python
    if not _test_mode:
        # Crash recovery (re-enabled per L41 fix)
        import os, sys
        from uuid import UUID
        from sovereignai.shared.types import new_correlation_id, now_utc

        marker_path = os.path.expanduser("~/.sovereignai/.shutdown_marker")
        try:
            if os.path.exists(marker_path):
                try:
                    with open(marker_path, "r") as f:
                        content = f.read()
                    if content.startswith("SOVEREIGNAI_CLEAN_SHUTDOWN_V1\n"):
                        os.unlink(marker_path)
                        trace.emit(component="recovery", level=TraceLevel.INFO,
                                   message="Clean shutdown detected — skipping crash recovery")
                except Exception:
                    pass

            from sovereignai.memory.trace_backend import TraceMemoryBackend
            tb = container.retrieve(TraceMemoryBackend)
            last_task_states = tb.get_last_task_states()
            for task_id_str, state in last_task_states.items():
                if state in ("received", "queued", "executing"):
                    trace.emit(component="recovery", level=TraceLevel.WARN,
                               message=f"Task {task_id_str} incomplete at crash; marking failed.")
                    tb.store(
                        data={"component": "recovery", "level": "warn",
                              "message": f"recovered: was {state}",
                              "correlation_id": task_id_str},
                        metadata={"task_id": task_id_str, "task_state": "failed"},
                    )
        except Exception as e:
            print(f"Crash recovery failed (non-fatal): {e}", file=sys.stderr)
```

### S4.4 — Trace subscriber (add new, guarded)

After the crash recovery block, add:
```python
    if not _test_mode:
        # Wire TraceEmitter → TraceMemoryBackend (deferred to background thread)
        import queue, threading
        _trace_queue = queue.Queue()

        def _on_trace_emitted(event):
            try:
                _trace_queue.put_nowait(event)
            except Exception:
                pass

        def _trace_writer():
            while True:
                try:
                    event = _trace_queue.get(timeout=5)
                    if event is None:
                        break
                    trace_backend.store(
                        data={"component": event.component, "level": event.level.value,
                              "message": event.message, "correlation_id": str(event.correlation_id)},
                        metadata={},
                    )
                except Exception:
                    pass

        if hasattr(trace, 'subscribe_callback'):
            _writer_thread = threading.Thread(target=_trace_writer, daemon=True)
            _writer_thread.start()
            trace.subscribe_callback(_on_trace_emitted)
```

### S4.5 — TaskStateChanged subscribers (add new, guarded)

```python
    if not _test_mode:
        from sovereignai.shared.types import TaskStateChanged, TASK_STATE_CHANNEL, TaskState

        def _on_task_state_persist(event: TaskStateChanged) -> None:
            try:
                trace_backend.store(
                    data={"component": "TaskStateMachine", "level": "info",
                          "message": f"Task {event.task_id}: {event.old_state} → {event.new_state}",
                          "correlation_id": str(event.task_id)},
                    metadata={"task_id": str(event.task_id),
                              "task_state": event.new_state.value if hasattr(event.new_state, 'value') else str(event.new_state)},
                )
            except Exception:
                pass
        bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_persist)

        def _on_task_cleanup(event: TaskStateChanged) -> None:
            terminal = (TaskState.COMPLETE.value, TaskState.FAILED.value)
            val = event.new_state.value if isinstance(event.new_state, TaskState) else str(event.new_state)
            if val in terminal:
                try:
                    working_backend.cleanup(str(event.task_id))
                except Exception as e:
                    trace.emit(component="working_memory", level=TraceLevel.WARN,
                               message=f"Cleanup failed for {event.task_id}: {e}")
        bus.subscribe(TASK_STATE_CHANNEL, _on_task_cleanup)
```

---

## S5 — Fix smoke test to pass env var

**File**: `tests/test_composition_root.py`

**Find**:
```python
    result = subprocess.run(
        [sys.executable, "-m", "sovereignai.main"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
    )
```

**Replace with**:
```python
    import os as _os
    env = {**_os.environ, "SOVEREIGNAI_TEST_MODE": "1"}
    result = subprocess.run(
        [sys.executable, "-m", "sovereignai.main"],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        env=env,
    )
```

---

## S6 — Fix self-correction component filter (L44)

**File**: `sovereignai/skills/official/self_correction/skill.py`

**Find**:
```python
        if getattr(event, 'component', None) == self.COMPONENT_NAME:
            return
```

**Remove this line entirely.** `TaskStateChanged` has no `component` field — the filter is dead code. The `_recently_analyzed` recursion guard is sufficient.

**File**: `tests/test_self_correction_skill.py`

Find any `setattr(event, 'component', ...)` lines and delete them — they crash with `FrozenInstanceError`.

---

## S7 — Fix mypy errors (OR90)

Run mypy. Fix what you can. For errors that require significant refactoring, add DEBT.md entries with file, line, error message, and target plan. Zero "pre-existing" exemptions.

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 20
```

---

## S8 — Verify

Run EACH command separately. If any hangs, the `--timeout=30` kills it.

```bash
# 1. Syntax check
.venv/Scripts/python.exe -c "import ast; ast.parse(open('sovereignai/main.py').read()); print('OK')"

# 2. Build container in test mode
.venv/Scripts/python.exe -c "import os; os.environ['SOVEREIGNAI_TEST_MODE']='1'; from sovereignai.main import build_container; c=build_container(); print('Container built OK')"

# 3. Tests with timeout
.venv/Scripts/python.exe -m pytest tests/test_composition_root.py -vvv --timeout=30

# 4. Full test suite with timeout + coverage
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing --timeout=30

# 5. Mypy
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```

---

## STOP Conditions

- If `build_container()` hangs in test mode after all guards are applied, STOP and report which `print("DBG: ...")` line it stops at.
- If any test hangs past 30 seconds, `--timeout=30` kills it — report which test hung.
- If coverage <89%, STOP (per OR77).
- If mypy reports undocumented errors, STOP (per OR90).

---

## Files WILL Edit

- `sovereignai/main.py` (S2, S3, S4 — test mode + backends + guards)
- `sovereignai/memory/episodic_backend.py` (S3.1 — db_path param, if missing)
- `sovereignai/memory/trace_backend.py` (S3.1 — db_path param, if missing)
- `sovereignai/memory/procedural_backend.py` (S3.1 — file_path param + in-memory mode)
- `sovereignai/skills/official/self_correction/skill.py` (S6 — remove dead filter)
- `tests/test_composition_root.py` (S5 — smoke test env var)
- `tests/test_self_correction_skill.py` (S6 — remove setattr)
- `AGENTS.md` (S0.3 — OR87-OR90)
- `LANDMINES.md` (S0.3 — L41-L47)
- `DEBT.md` (S7 — mypy deferrals)

## Files WILL Create

- `tests/conftest.py` (S1 — SOVEREIGNAI_TEST_MODE=1)

---

## Closing

Run `/close`. Tag: `prompt-15.1`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh.
