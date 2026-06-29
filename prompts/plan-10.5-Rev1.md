# Plan 10.5 — Web UI Hotfix: /api/tasks 500 + Panel Population

**Special plan**: Bug-fix patch. Fixes the `/api/tasks` 500 error (revealed after 10.4 fixed dispatch so tasks can now be submitted) and verifies all UI panels populate. No new features. Skips Round Table (mechanical bug fix with verified root cause).

Depends on: prompt-10.4
Vision principles: P9 (no silent failures), P13 (strong, robust)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-10.4` tag exists on origin (`1e8272d`). Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim), OR75/OR80/OR83 (`git add -A`), OR72 (don't edit tests to make failures pass — doesn't apply; we're fixing source).

**S0.3** — No new rules. This is a one-off bug, not a pattern. Proceed to S1.

---

## S1 — Fix Bug: `/api/tasks` 500 — Task dataclass has no `state`/`result`/`error` fields

**Root cause** (verified): The `Task` dataclass (`sovereignai/shared/types.py`) has fields `task_id`, `capability`, `payload`, `submitted_at` — **no `state`, `result`, or `error`**. State is tracked separately by `TaskStateMachine.get_state(task_id)`. `result` and `error` are not stored anywhere in v1 (no result-storage layer yet).

The `/api/tasks` list route (`web/main.py` line 291-295) reads `t.state.value`, `t.result`, `t.error` — all of which `AttributeError`. This was hidden before 10.4 because dispatch was broken (no tasks ever existed, so the list was always `[]`). Now that dispatch works, tasks exist and the route crashes.

**File**: `web/main.py`

### S1.1 — Fix `/api/tasks` route to use `get_state()` and null result/error

**Old** (line 280-296):
```python
@app.get("/api/tasks", dependencies=[Depends(get_current_user)])
async def get_tasks(request: Request) -> list[TaskResponseDTO]:
    """Return all tasks from the task state machine.

    Retrieve TaskStateMachine, call list_tasks(), map to TaskResponseDTO list.
    """
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    tasks = task_state_query.list_tasks()

    return [
        TaskResponseDTO(
            task_id=str(t.task_id),
            state=t.state.value,
            result=t.result,
            error=t.error,
        )
        for t in tasks
    ]
```

**New**:
```python
@app.get("/api/tasks", dependencies=[Depends(get_current_user)])
async def get_tasks(request: Request) -> list[TaskResponseDTO]:
    """Return all tasks from the task state machine.

    The Task dataclass holds task_id, capability, payload, submitted_at —
    NOT state/result/error. State is tracked separately by the state machine
    (get_state). result/error are not stored in v1 (no result-storage layer);
    return null until a future plan adds task result persistence.
    """
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    tasks = task_state_query.list_tasks()

    dtos: list[TaskResponseDTO] = []
    for t in tasks:
        state = task_state_query.get_state(t.task_id)
        state_str = state.value if state is not None else "unknown"
        dtos.append(
            TaskResponseDTO(
                task_id=str(t.task_id),
                state=state_str,
                result=None,   # v1: no result storage yet
                error=None,    # v1: no error storage yet
            )
        )
    return dtos
```

**Changes**:
- For each task, call `get_state(t.task_id)` to fetch the state from the state machine (not from the Task object).
- `result` and `error` are `None` in v1 (documented in the docstring). A future plan (memory layer, Plan 11+) adds result persistence.
- Handle `state is None` gracefully (returns `"unknown"` — shouldn't happen for a task in `list_tasks()`, but defensive).

### S1.2 — Verify the fix

```bash
# Start server
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8765 &

# Register + login
curl -s -X POST http://127.0.0.1:8765/api/auth/register -H "Content-Type: application/json" -d '{"username":"test","password":"testpass123"}'
curl -s -X POST http://127.0.0.1:8765/api/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"testpass123"}' -c /tmp/cookies.txt

# Submit a task (dispatch was fixed in 10.4)
curl -s -X POST http://127.0.0.1:8765/api/dispatch -H "Content-Type: application/json" -d '{"message":"hello"}' -b /tmp/cookies.txt

# NOW test /api/tasks — should return the task, NOT 500
curl -s http://127.0.0.1:8765/api/tasks -b /tmp/cookies.txt -w "\nStatus: %{http_code}\n"

# Expected: [{"task_id":"...","state":"received","result":null,"error":null}] Status: 200
# If 500, STOP — the fix didn't work.

kill %1
```

---

## S2 — Add Regression Test for `/api/tasks` with submitted tasks

**File**: `tests/test_web_ui_integration.py` (extend the file created in 10.4)

The integration tests added in 10.4 tested dispatch but did NOT test `/api/tasks` after a task was submitted. That's the gap that let this bug ship.

### S2.1 — Add test class `TestTasksRouteAfterDispatch`

Append to `tests/test_web_ui_integration.py`:

```python
class TestTasksRouteAfterDispatch:
    """Bug: /api/tasks 500s after a task is submitted (Task has no state/result/error fields)."""

    def test_tasks_empty_initially(self, client_authenticated: TestClient) -> None:
        """Verify /api/tasks returns [] before any task is submitted."""
        response = client_authenticated.get("/api/tasks")
        assert response.status_code == 200
        assert response.json() == []

    def test_tasks_returns_submitted_task(self, client_authenticated: TestClient) -> None:
        """Verify /api/tasks returns the task after dispatch (not a 500)."""
        # Submit a task
        dispatch_resp = client_authenticated.post(
            "/api/dispatch", json={"message": "test task"}
        )
        assert dispatch_resp.status_code == 200
        task_id = dispatch_resp.json()["task_id"]

        # List tasks — must not 500
        response = client_authenticated.get("/api/tasks")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        tasks = response.json()
        assert len(tasks) >= 1, f"Expected >=1 task, got {len(tasks)}"
        assert tasks[0]["task_id"] == task_id, f"Task ID mismatch: {tasks[0]['task_id']} != {task_id}"
        assert tasks[0]["state"] in ("received", "queued", "executing", "complete", "failed", "unknown")
        # result/error are null in v1 (no result storage yet)
        assert tasks[0]["result"] is None
        assert tasks[0]["error"] is None

    def test_tasks_after_multiple_dispatches(self, client_authenticated: TestClient) -> None:
        """Verify /api/tasks handles multiple tasks without 500ing."""
        for i in range(3):
            client_authenticated.post("/api/dispatch", json={"message": f"task {i}"})
        response = client_authenticated.get("/api/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 3, f"Expected >=3 tasks, got {len(tasks)}"
```

### S2.2 — Run the tests

```bash
.venv/Scripts/python.exe -m pytest tests/test_web_ui_integration.py -vvv
```

All tests (the 8 from 10.4 + the 3 new ones = 11) must pass. If any fail, STOP.

---

## S3 — Verify All UI Panels Populate

After the fix, do a manual panel-by-panel check to confirm the UI windows populate (the User reported "none of the windows populate").

### S3.1 — Panel data endpoints check

```bash
# Start server, register, login
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8765 &
sleep 2
curl -s -X POST http://127.0.0.1:8765/api/auth/register -H "Content-Type: application/json" -d '{"username":"panel","password":"testpass123"}'
curl -s -X POST http://127.0.0.1:8765/api/auth/login -H "Content-Type: application/json" -d '{"username":"panel","password":"testpass123"}' -c /tmp/cookies.txt

# Submit a task so tasks panel has data
curl -s -X POST http://127.0.0.1:8765/api/dispatch -H "Content-Type: application/json" -d '{"message":"panel test"}' -b /tmp/cookies.txt

echo "=== Panel data check ==="
echo -n "Orchestrator (traces stream): "; timeout 2 curl -s -N http://127.0.0.1:8765/api/traces/stream -b /tmp/cookies.txt 2>&1 | grep -c "^data:"; echo " events"
echo -n "Workers: "; curl -s http://127.0.0.1:8765/api/workers -b /tmp/cookies.txt | python -c "import json,sys; print(len(json.load(sys.stdin)), 'items')"
echo -n "Tasks: "; curl -s http://127.0.0.1:8765/api/tasks -b /tmp/cookies.txt | python -c "import json,sys; print(len(json.load(sys.stdin)), 'items')"
echo -n "Skills (capabilities filtered to tool): "; curl -s http://127.0.0.1:8765/api/capabilities -b /tmp/cookies.txt | python -c "import json,sys; print(len([c for c in json.load(sys.stdin) if c['category']=='tool']), 'items')"
echo -n "Adapters (capabilities filtered to model_inference): "; curl -s http://127.0.0.1:8765/api/capabilities -b /tmp/cookies.txt | python -c "import json,sys; print(len([c for c in json.load(sys.stdin) if c['category']=='model_inference']), 'items')"
echo -n "Hardware: "; curl -s http://127.0.0.1:8765/api/hardware -b /tmp/cookies.txt | python -c "import json,sys; d=json.load(sys.stdin); print(d)"
echo -n "Memory: "; echo "(no /api/memory endpoint yet — Plan 11 adds it)"
echo -n "Models: "; echo "(no /api/models endpoint yet — future plan)"

kill %1
```

Expected:
- Traces: ≥3 events (registration traces)
- Workers: 2 items (websearch_skill, ollama_adapter)
- Tasks: ≥1 item (the dispatched task) — **this was 500ing before the fix**
- Skills: 1 item (web_search capability)
- Adapters: 2 items (text_generation, chat_completion)
- Hardware: CPU/RAM data
- Memory/Models: not yet implemented (Plan 11+ / future)

### S3.2 — Frontend rendering check

Open `http://127.0.0.1:8765/` in a browser (or verify via curl that `index.html` references all panel IDs):

```bash
# Verify all 9 panel sections exist in index.html
grep -c 'id="panel-' web/templates/index.html
# Expected: 9 (orchestrator, workers, tasks, skills, memory, models, adapters, hardware, options)
```

If any panel is missing from the HTML, STOP — that's a separate frontend issue.

---

## S4 — Run Full Verification

Per `/close` steps 1–8 (re-read close.md fresh per OR71). **Per OR83, use `git add -A` for ALL commits.**

### S4.1 — Tests with coverage
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
Expected: 177 + 3 new = 180 passed, 3 skipped. Coverage ≥93%.

### S4.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
Expected: 0 errors.

### S4.3 — Mypy (full repo)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```
Expected: 0 errors.

### S4.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: ~343 Low (B101) — grows by ~3 from new test assertions. Update PLANS.md baseline per OR78.

### S4.5 — pip-audit
```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```
Expected: 0 CVEs.

### S4.6 — Vulture
```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```
Expected: 0 new findings.

### S4.7 — detect-secrets
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
Expected: exit 0.

### S4.8 — Custom AR checks
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```
All must pass.

---

## STOP Conditions

- If S1.2 `/api/tasks` returns 500 after the fix, STOP.
- If any test in S2.2 fails, STOP.
- If any panel data endpoint in S3.1 returns 500 or unexpected empty data, STOP.
- If any static analysis tool in S4 fails, STOP.
- If coverage <88%, STOP (per OR77).
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (per OR83).

---

## Files WILL Edit

- `web/main.py` (S1 — fix `/api/tasks` route to use `get_state()`)
- `tests/test_web_ui_integration.py` (S2 — add 3 regression tests)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (the `Task` dataclass is correct — it's the route that was wrong)
- Any AR check script
- `txt/.secrets.baseline`
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-10.5`.

**Critical per OR83**: Every `git commit` MUST use `git add -A`.

**Critical per OR76**: Before `git tag prompt-10.5`, verify `git tag --list prompt-10.5` is empty.

**Critical per OR71**: Re-read `.devin/workflows/close.md` in full before running `/close`.

After `prompt-10.5`, the Web UI is fully functional:
- All 9 panels populate (orchestrator, workers, tasks, skills, memory, models, adapters, hardware, options)
- Memory and Models panels show "not yet implemented" placeholders (Plan 11 adds memory; a future plan adds models)
- Tasks panel shows submitted tasks without 500ing
- Chat (dispatch) works end-to-end

---

## Adjudication Summary

This patch addresses 1 bug revealed after 10.4 fixed dispatch:

**Bug**: `/api/tasks` 500s when tasks exist. The route reads `t.state`, `t.result`, `t.error` from the `Task` dataclass, but `Task` only has `task_id`, `capability`, `payload`, `submitted_at`. State lives in the state machine (`get_state(task_id)`); result/error aren't stored in v1.

**Why 10.4 didn't catch it**: Before 10.4, dispatch was broken (wrong kwargs), so no tasks ever existed, so `/api/tasks` always returned `[]` — the bug was dormant. 10.4 fixed dispatch, tasks now exist, the list route crashed. The 10.4 integration tests tested dispatch but not the tasks-list-after-dispatch path.

**Fix**: Route calls `get_state(t.task_id)` per task; returns `None` for result/error (v1 has no result storage; Plan 11+ adds it).

**Regression tests**: 3 new tests in `TestTasksRouteAfterDispatch` — empty initially, returns submitted task, handles multiple tasks.

Not addressed (out of scope — future plans):
- `result`/`error` storage (Plan 11 memory layer or a future task-result plan)
- Memory panel data endpoint (Plan 11)
- Models panel data endpoint (future plan)
