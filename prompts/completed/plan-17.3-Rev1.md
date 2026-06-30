# Plan 17.3 — Fix Auth Tests + Resizable Log + Verbose Pull Logging + Close Discipline

**Hotfix**: Fix 32 test failures from auth persistence, add resizable log drawer, add verbose pull progress in log, mandate close workflow compliance. Round Table vetoed.

Depends on: prompt-17.2

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-17.2` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Read `close.md` in full (per OR71).

**S0.3** — Add one rule:
- **OR92**: The `/close` workflow is MANDATORY and must complete ALL 22 steps. If any step fails (tests, ruff, mypy, bandit, etc.), STOP and report to the User — do NOT skip remaining steps, do NOT commit with known failures, do NOT tag until all steps pass. The plan is NOT complete until `/close` step 22 (kill Git Bash) runs. Source: L42 (reinforced), prompt-17.2 close failure.

Commit: `docs: add OR92 for prompt-17.3`

---

## S1 — Fix auth test failures (32 failures)

**Problem**: Auth persistence (Plan 17) saves users to `settings/auth.json`. Tests call `register_user("testuser")` which fails on the second run because the user already exists from the previous run's persisted state.

### S1.1 — Fix tests to use isolated AuthMiddleware instances

**Problem**: Tests call `container.retrieve(AuthMiddleware)` which returns the production AuthMiddleware — the one that loads persisted users from `settings/auth.json`. When a test calls `register_user("testuser")`, it succeeds on the first run but fails on subsequent runs because "testuser" was persisted.

**Fix**: Tests should create their own fresh `AuthMiddleware(trace=mock_trace)` instance instead of retrieving the production one. This gives each test a clean slate with no persisted users.

**File**: `tests/conftest.py`

Add a shared fixture:

```python
"""Pytest configuration and shared fixtures."""
import os
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import web.main

# Set test mode BEFORE any imports that trigger build_container
os.environ["SOVEREIGNAI_TEST_MODE"] = "1"


@pytest.fixture
def fresh_auth():
    """Provide a fresh AuthMiddleware with no persisted users.
    
    Tests that need to register users should use this fixture instead of
    retrieving AuthMiddleware from the container (which has persisted users).
    """
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    return AuthMiddleware(trace=trace)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app with auth bypass."""
    web.main.app.dependency_overrides[web.main.get_current_user] = (
        lambda request: MagicMock(username="test")
    )
    client = TestClient(web.main.app)
    yield client
    web.main.app.dependency_overrides.clear()
```

**File**: `tests/test_web_auth.py`

Every test that does `auth = container.retrieve(AuthMiddleware)` should instead use the `fresh_auth` fixture. For example:

**Find** (in each test function):
```python
def test_valid_credentials_set_cookie():
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpassword123")
```

**Replace with**:
```python
def test_valid_credentials_set_cookie(fresh_auth):
    fresh_auth.register_user("testuser", "testpassword123")
```

Do this for ALL test functions in `test_web_auth.py` that call `register_user`:
- `test_valid_credentials_set_cookie` → use `fresh_auth` fixture
- `test_invalid_credentials_return_401` → use `fresh_auth` fixture
- `test_registration_fails_when_user_exists` → use `fresh_auth` fixture
- `test_protected_endpoints_return_401_without_cookie` → use `fresh_auth` fixture
- `test_protected_endpoints_return_200_with_cookie` → use `fresh_auth` fixture
- `test_register_after_user_exists_redirects` → use `fresh_auth` fixture

**File**: `tests/test_first_run.py` — same pattern: replace `container.retrieve(AuthMiddleware)` with `fresh_auth` fixture.

**File**: `tests/test_auth.py` — same pattern.

**File**: `tests/test_e2e_task_submission.py` — same pattern (if it calls register_user).

**File**: `tests/test_capability_api.py` — same pattern (if it calls register_user).

**Do NOT delete or modify `settings/auth.json`** — that file holds the user's real login credentials. Tests must not touch it.

### S1.2 — Keep auth.py path as-is

**File**: `sovereignai/shared/auth.py`

**Do NOT change** `_AUTH_FILE`. Leave it at whatever path it currently uses (`settings/auth.json`). The tests now use isolated `AuthMiddleware` instances (via `fresh_auth` fixture) that don't load from disk, so the persisted file is irrelevant to tests.

### S1.3 — Fix ruff SIM105 in auth.py

**File**: `sovereignai/shared/auth.py`

Find:
```python
        try:
            os.chmod(_AUTH_FILE, 0o600)
        except OSError:
            pass
```

Replace with:
```python
        import contextlib
        with contextlib.suppress(OSError):
            os.chmod(_AUTH_FILE, 0o600)
```

---

## S2 — Make log drawer resizable

**File**: `web/static/styles.css`

**Find**:
```css
#log-drawer {
    position: fixed;
    bottom: 0;
    left: 200px;
    right: 0;
    height: 0;
    background-color: #1e1e1e;
    border-top: 2px solid #3d3d3d;
    display: flex;
    flex-direction: column;
    z-index: 1000;
```

**Add `resize: vertical` and `overflow: hidden`**:
```css
#log-drawer {
    position: fixed;
    bottom: 0;
    left: 200px;
    right: 0;
    height: 0;
    background-color: #1e1e1e;
    border-top: 2px solid #3d3d3d;
    display: flex;
    flex-direction: column;
    z-index: 1000;
    resize: vertical;
    overflow: hidden;
    min-height: 0;
```

Also update the `.open` class to allow resizing:
```css
#log-drawer.open {
    height: 200px;
    min-height: 100px;
}
```

The `resize: vertical` property adds a drag handle at the top-right corner of the log drawer. User can drag it up to make it taller or down to make it shorter.

---

## S3 — Add verbose pull progress in log

**Problem**: When pulling a model, the log only shows "Pulling model: X" and then "Pull failed" or "Pull success." No download progress.

### S3.1 — Stream ollama pull output to traces

**File**: `web/main.py`

In the `_pull()` function inside the `/api/models/pull` endpoint, change from `capture_output=True` to streaming stdout line-by-line:

**Find** the `_pull()` function and **replace with**:

```python
    def _pull() -> None:
        import subprocess
        try:
            trace.emit(component="models", level=TraceLevel.INFO,
                       message=f"Starting pull: {ollama_name}")
            _pull_status[model_name] = {"status": "pulling", "message": f"Pulling {ollama_name}...", "progress": 0}

            # Stream output line by line so progress appears in log drawer
            process = subprocess.Popen(
                ["ollama", "pull", ollama_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            for line in process.stdout:
                line = line.strip()
                if line:
                    # Emit each line as a trace — shows download progress in log drawer
                    trace.emit(component="models", level=TraceLevel.INFO,
                               message=f"Pull: {line}")

            process.wait(timeout=3600)

            if process.returncode == 0:
                _pull_status[model_name] = {"status": "done", "message": f"Pulled {ollama_name}", "progress": 100}
                trace.emit(component="models", level=TraceLevel.INFO,
                           message=f"Pull complete: {ollama_name}")
            else:
                _pull_status[model_name] = {"status": "error", "message": f"Pull failed (exit {process.returncode})", "progress": 0}
                trace.emit(component="models", level=TraceLevel.ERROR,
                           message=f"Pull failed (exit {process.returncode}): {ollama_name}")
        except Exception as exc:
            _pull_status[model_name] = {"status": "error", "message": f"Pull error: {exc}", "progress": 0}
            trace.emit(component="models", level=TraceLevel.ERROR,
                       message=f"Pull error: {exc}")
```

**Key change**: `subprocess.Popen` with `stdout=PIPE` instead of `subprocess.run` with `capture_output=True`. Each line of `ollama pull` output (which includes download progress like "pulling 1.2GB... 45%") is emitted as a trace event, appearing in the log drawer in real-time.

---

## S4 — Fix mypy errors (OR90)

**File**: various

Run mypy and fix all errors. No "pre-existing" exemptions (per OR90).

```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 20
```

Fix each error. For errors that require significant refactoring, document in DEBT.md.

---

## S5 — Fix .gitignore for settings/

**File**: `.gitignore`

Add:
```
# User settings (API keys, auth, local state)
settings/
```

---

## S6 — Run FULL /close workflow (ALL 22 steps — per OR92)

**CRITICAL**: Do NOT skip any close steps. Run every step in order. If any step fails, STOP and report — do NOT continue to the next step.

Per OR92:
- Step 1: Tests MUST pass (fix all failures first)
- Step 2: Ruff MUST be 0 errors
- Step 3: Mypy MUST be 0 errors (or documented in DEBT.md)
- Step 4: Bandit — record count
- Step 5: pip-audit — 0 CVEs
- Step 6: Vulture — 0 new findings
- Step 7: detect-secrets — pass
- Step 8: AR checks — all pass
- Steps 9-14: Governance docs
- Step 15: Commit code
- Step 16: Tag (verify empty first per OR76)
- Step 17: Archive plan files (use `git add -A` per OR83 — NEVER `git rm`)
- Step 18: Commit docs
- Step 19: Push
- Step 20: Verify tag on origin
- Step 21: Final summary
- Step 22: Kill Git Bash

If tests fail after S1 fixes, investigate and fix BEFORE continuing to Step 2. Do NOT skip.

---

## STOP Conditions

- If ANY test fails after S1 fixes, STOP and fix before continuing.
- If ruff reports errors after S1.3, STOP and fix.
- If mypy reports errors after S4, STOP and fix or document in DEBT.md.
- If coverage is unavailable (test failures prevent it), STOP — do NOT continue.
- If ANY `/close` step fails, STOP and report to User (per OR92).

---

## Files WILL Edit
- `tests/conftest.py` (S1.1 — clean settings/ before each test)
- `sovereignai/shared/auth.py` (S1.2 — settings/auth.json path, S1.3 — ruff fix)
- `web/static/styles.css` (S2 — resize: vertical)
- `web/main.py` (S3.1 — stream pull output to traces)
- `.gitignore` (S5 — settings/)
- `AGENTS.md` (S0.3 — OR92)
- Various .py files (S4 — mypy fixes)

## Files WILL NOT Edit
- `sovereignai/main.py` (unless mypy requires it)
- `txt/requirements.txt`

---

## Closing

Run `/close`. Tag: `prompt-17.3`. 

**MANDATORY (per OR92)**: Complete ALL 22 steps of `/close`. Do NOT skip steps. Do NOT commit with known failures. Do NOT tag until all steps pass. The plan is NOT complete until step 22 runs.
