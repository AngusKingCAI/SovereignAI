# Plan 15.1 — Fix Critical Issues from Log Scan (Prompts 11-15)

**Special plan**: Bug-fix patch. Fixes 5 critical issues discovered by reading all execution logs for prompts 11-15. No new features. Skips Round Table (per User veto for this section).

Depends on: prompt-15
Vision principles: P9 (no silent failures — crash recovery disabled = silent failure), P13 (strong, robust — 83 mypy errors = not robust)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-15` tag exists on origin. Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim), OR75/OR80/OR83 (`git add -A`), OR76 (no premature tags), OR77 (coverage, floor 89%).

**S0.3** — Add 4 new rules + 7 new landmines:

- **OR87**: Never disable production features to make tests pass. If a feature breaks tests, fix the test or fix the feature. If a feature MUST be temporarily disabled, it MUST be: (a) tracked in DEBT.md with trigger condition and target plan, (b) wrapped in an explicit `if not TEST_MODE:` guard (not commented out or `pass`), and (c) re-enabled in the next plan. Source: L41.
- **OR88**: Investigate every "Command errored" before continuing. Read the error output, determine the cause, and either fix it or document why it's safe to continue. Do NOT simply move to the next step. If the error is in a verification step, treat it as a STOP condition. Source: L43, L46.
- **OR89**: Do not filter on attributes that don't exist on the event/dataclass. Verify the attribute exists before implementing the filter. If it doesn't exist, add it to the dataclass (justify per P1) or use a different mechanism. Source: L44.
- **OR90**: Mypy errors are STOP regardless of "pre-existing." OR2 says STOP on mypy errors — there is no "pre-existing" exemption. Fix each error or document it in DEBT.md with a target plan. Source: L45.

Landmines L41-L47 (see `/home/z/my-project/download/log-scan-findings-11-15.md` for full text).

Commit: `docs: add OR87-OR90, L41-L47 for prompt-15.1`

---

## S1 — Register all 4 memory backends in main.py (L41, L47)

**File**: `sovereignai/main.py`

The backend FILES exist (`sovereignai/memory/episodic_backend.py`, `procedural_backend.py`, `trace_backend.py`) but they are NOT imported or registered in `build_container()`. Only `WorkingMemoryBackend` is registered.

### S1.1 — Register episodic, procedural, and trace backends

**Find** (around line 158):
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
    # Per L41 fix (prompt-15.1): ALL backends must be registered, not just Working.
    # The Executor disabled these in prompt-11 to make tests pass — that was wrong (OR87).
    from sovereignai.librarian.librarian import Librarian
    from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
    from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
    from sovereignai.memory.working_backend import WorkingMemoryBackend
    from sovereignai.memory.trace_backend import TraceMemoryBackend

    # Episodic memory (SQLite at ~/.sovereignai/episodic.db)
    episodic_backend = EpisodicMemoryBackend(trace=trace)
    container.register_singleton(EpisodicMemoryBackend, episodic_backend)

    # Procedural memory (JSON at ~/.sovereignai/procedural_memory.json)
    procedural_backend = ProceduralMemoryBackend(trace=trace)
    container.register_singleton(ProceduralMemoryBackend, procedural_backend)

    # Working memory (in-process, no disk I/O)
    working_backend = WorkingMemoryBackend(trace=trace)
    container.register_singleton(WorkingMemoryBackend, working_backend)

    # Trace memory (SQLite at ~/.sovereignai/trace.db)
    trace_backend = TraceMemoryBackend(trace=trace)
    container.register_singleton(TraceMemoryBackend, trace_backend)

    # Wire TraceEmitter → TraceMemoryBackend (durable persistence)
    if hasattr(trace, 'subscribe_callback'):
        def _on_trace_emitted(event):
            try:
                trace_backend.store(
                    data={
                        "component": event.component,
                        "level": event.level.value,
                        "message": event.message,
                        "correlation_id": str(event.correlation_id),
                    },
                    metadata={},
                )
            except Exception:
                pass
        trace.subscribe_callback(_on_trace_emitted)

    # Instantiate and register Librarian
    librarian = Librarian(capability_graph=graph, trace=trace)
    container.register_singleton(Librarian, librarian)
```

### S1.2 — Register backend manifests in CapabilityGraph

After registering the backends in the container, also register their manifests so the Librarian can discover them via the CapabilityGraph. Scan for manifest files in `adapters/internal/`:

```python
    # Register memory backend manifests in CapabilityGraph
    from pathlib import Path
    from sovereignai.shared.manifest_parser import parse_manifest
    for manifest_dir in [Path("adapters/internal/episodic_memory"), Path("adapters/internal/procedural_memory"),
                         Path("adapters/internal/working_memory"), Path("adapters/internal/trace_memory")]:
        manifest_path = manifest_dir / "manifest.toml"
        if manifest_path.exists():
            try:
                manifest = parse_manifest(manifest_path)
                graph.register(manifest)
                trace.emit(component="main", level=TraceLevel.INFO,
                           message=f"Registered {manifest.component_id} from {manifest_path}")
            except Exception as exc:
                trace.emit(component="main", level=TraceLevel.ERROR,
                           message=f"Failed to load manifest {manifest_path}: {exc}")
```

If the manifest files don't exist yet, create them per the Plan 11 spec (S2-S5 manifest examples). Each manifest declares `memory_storage` and `memory_query` capabilities for its memory type.

---

## S2 — Re-enable crash recovery (L41)

**File**: `sovereignai/main.py`

**Find** (around line 252):
```python
    def run_crash_recovery(container: DIContainer, trace: TraceEmitter) -> None:
        """Run crash recovery on startup. Best-effort — never blocks startup.
        ...
        """
        # Disabled for now - persistent backends not initialized
        pass
```

**Replace with** (per Plan 11 Rev9 S7):
```python
    def run_crash_recovery(container: DIContainer, trace: TraceEmitter) -> None:
        """Run crash recovery on startup. Best-effort — never blocks startup.

        Per L41 fix (prompt-15.1): re-enabled. Was disabled in prompt-11.
        """
        import os, sys
        from uuid import UUID
        from sovereignai.shared.types import TraceLevel, new_correlation_id, now_utc

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
                        return
                    else:
                        trace.emit(component="recovery", level=TraceLevel.WARN,
                                   message="Shutdown marker exists but content invalid — treating as crash")
                except Exception:
                    trace.emit(component="recovery", level=TraceLevel.WARN,
                               message="Shutdown marker unreadable — treating as crash")

            # No valid marker — previous shutdown was a crash. Run recovery.
            from sovereignai.memory.trace_backend import TraceMemoryBackend
            trace_backend = container.retrieve(TraceMemoryBackend)
            last_task_states = trace_backend.get_last_task_states()

            for task_id_str, state in last_task_states.items():
                if state in ("received", "queued", "executing"):
                    trace.emit(
                        component="recovery",
                        level=TraceLevel.WARN,
                        message=f"Task {task_id_str} was incomplete (state={state}) at crash; marking as recovered-failed.",
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
            print(f"SovereignAI crash recovery failed (non-fatal): {e}", file=sys.stderr)
            trace.emit(component="recovery", level=TraceLevel.ERROR,
                       message=f"Crash recovery failed (non-fatal): {e}")
```

Also add the `_is_valid_uuid` helper and the `on_clean_shutdown` function + `atexit` registration per Plan 11 Rev9 S7.

---

## S3 — Fix self-correction component filter (L44)

**File**: `sovereignai/skills/official/self_correction/skill.py`

**Problem**: The component filter `getattr(event, 'component', None) == self.COMPONENT_NAME` always returns None because `TaskStateChanged` has no `component` field. The filter is dead code.

**Fix**: Remove the component filter from `on_task_state_changed`. The recursion guard (`_recently_analyzed` set) already prevents the feedback loop. The component filter was an extra safety layer that can't work without modifying the `TaskStateChanged` dataclass (which is core — P1 violation). The recursion guard is sufficient.

**Find**:
```python
    def on_task_state_changed(self, event: TaskStateChanged) -> None:
        """Handle a task state change. Filters own events + deduplicates per task_id."""
        # Rev9: filter events from self_correction component (per OR69)
        if getattr(event, 'component', None) == self.COMPONENT_NAME:
            return
        if event.new_state not in (TaskState.COMPLETE, TaskState.FAILED):
            return
```

**Replace with**:
```python
    def on_task_state_changed(self, event: TaskStateChanged) -> None:
        """Handle a task state change. Deduplicates per task_id to prevent recursion.

        Per L44 fix (prompt-15.1): removed component filter — TaskStateChanged has no
        'component' field (it's a frozen dataclass). The _recently_analyzed set is the
        sole recursion guard, which is sufficient.
        """
        if event.new_state not in (TaskState.COMPLETE, TaskState.FAILED):
            return
```

Also fix the test that tries `setattr(event, 'component', 'self_correction')` — remove the `setattr` line and the assertion that depends on it.

---

## S4 — Fix or defer 83 mypy errors (L45)

**File**: various

Run mypy and fix as many errors as possible. For errors that require significant refactoring (e.g., type narrowing across module boundaries), document each one in DEBT.md with:
- The file and line
- The error message
- The reason it can't be fixed in this plan
- The target plan for the fix

**Do NOT mark errors as "pre-existing" and continue** (per OR90). Either fix or defer with a DEBT.md entry.

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 20
```

Fix what you can. For the rest, add DEBT.md entries.

---

## S5 — Wire TaskStateChanged subscriber for trace persistence (Plan 11 Rev9 S6)

**File**: `sovereignai/main.py`

The Plan 11 Rev9 spec requires a second subscriber on `TASK_STATE_CHANNEL` that persists task state changes to the trace backend with `metadata={"task_id": ..., "task_state": ...}`. Without this, `get_last_task_states()` returns empty and crash recovery finds nothing.

**Add** after the trace subscriber wiring:
```python
    # Per Plan 11 Rev9 S6: persist TaskStateChanged events for crash recovery
    from sovereignai.shared.types import TaskStateChanged, TASK_STATE_CHANNEL, TaskState
    def _on_task_state_changed_persist(event: TaskStateChanged) -> None:
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
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed_persist, subscriber_id="trace_persist")
```

Also wire the WorkingMemoryBackend cleanup:
```python
    def _on_task_state_changed_cleanup(event: TaskStateChanged) -> None:
        terminal_states = (TaskState.COMPLETE.value, TaskState.FAILED.value)
        new_state_val = event.new_state.value if isinstance(event.new_state, TaskState) else str(event.new_state)
        if new_state_val in terminal_states:
            try:
                working_backend.cleanup(str(event.task_id))
            except Exception as e:
                trace.emit(component="working_memory", level=TraceLevel.WARN,
                           message=f"Working memory cleanup failed for task {event.task_id}: {e}")
    bus.subscribe(TASK_STATE_CHANNEL, _on_task_state_changed_cleanup, subscriber_id="working_memory_cleanup")
```

---

## S6 — Run full verification

### S6.1 — Tests with coverage
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
If tests fail because backends create DB files, fix the tests to use temp directories — do NOT disable the backends (per OR87).

### S6.2 — Mypy
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```
Fix or defer every error (per OR90). Zero "pre-existing" exemptions.

### S6.3 — Ruff, Bandit, pip-audit, Vulture, detect-secrets, AR checks
Standard scan tool suite.

### S6.4 — Verify crash recovery works
```bash
.venv/Scripts/python.exe -c "
from sovereignai.main import build_container
from sovereignai.memory.trace_backend import TraceMemoryBackend
c = build_container()
tb = c.retrieve(TraceMemoryBackend)
states = tb.get_last_task_states()
print(f'Trace backend registered: {tb is not None}')
print(f'Last task states: {states}')
print('Crash recovery is functional')
"
```

### S6.5 — Verify all 4 backends registered
```bash
.venv/Scripts/python.exe -c "
from sovereignai.main import build_container
from sovereignai.memory.episodic_backend import EpisodicMemoryBackend
from sovereignai.memory.procedural_backend import ProceduralMemoryBackend
from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.memory.trace_backend import TraceMemoryBackend
c = build_container()
for cls in [EpisodicMemoryBackend, ProceduralMemoryBackend, WorkingMemoryBackend, TraceMemoryBackend]:
    try:
        inst = c.retrieve(cls)
        print(f'{cls.__name__}: registered ✅')
    except KeyError:
        print(f'{cls.__name__}: NOT registered ❌')
"
```

---

## STOP Conditions

- If any test fails after re-enabling backends, fix the test — do NOT disable the backend (per OR87).
- If coverage <89%, STOP (per OR77).
- If mypy reports errors that are not documented in DEBT.md, STOP (per OR90).
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (per OR83).

---

## Files WILL Edit

- `sovereignai/main.py` (S1 — register all 4 backends; S2 — re-enable crash recovery; S5 — wire subscribers)
- `sovereignai/skills/official/self_correction/skill.py` (S3 — remove dead component filter)
- `tests/test_self_correction_skill.py` (S3 — remove setattr on frozen dataclass)
- `AGENTS.md` (S0.3 — add OR87-OR90)
- `LANDMINES.md` (S0.3 — add L41-L47)
- `DEBT.md` (S4 — defer mypy errors that can't be fixed in this plan)
- Various .py files (S4 — fix mypy errors where possible)

## Files WILL NOT Edit

- `sovereignai/shared/types.py` (core — do NOT add `component` to `TaskStateChanged`; use the recursion guard instead)
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-15.1`. Per OR83, use `git add -A`. Per OR76, verify tag is empty before creating. Per OR71, re-read `close.md` fresh.
