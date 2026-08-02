# Plan 10.4 — Web UI Hotfix Patch

**Special plan**: Bug-fix patch. Fixes 3 bugs found by manual Web UI testing (see `web-ui-test-report.md`) that make the app non-functional for its primary purpose (chat + task submission). No new features. No new architecture. Skips Round Table (mechanical bug fixes with verified root causes).

Depends on: prompt-10.3
Vision principles: P9 (no silent failures — Bug 1 silently swallows manifest errors), P13 (strong, robust — Bugs 2+3 crash on normal usage)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open` workflow from `.devin/workflows/open.md`. Verify `prompt-10.3` tag exists on origin (`b1f9106`). Confirm clean working copy on `main`. Activate venv (OR45).

**S0.2** — Read `AGENTS.md` in full. Note OR71 (verbatim commands), OR75/OR80/OR83 (`git add -A` for all commits), OR72 (never edit AR check scripts or tests to make failures pass — does NOT apply here; we're fixing source code, not tests).

**S0.3** — No new rules this plan. The bugs are implementation defects, not recurring patterns. No new landmines (these are one-off bugs, not pattern failures). Proceed to S1.

Commit: (none — no S0.3 rules to commit)

---

## S1 — Fix Bug 1 (CRITICAL): Manifest parser unwraps `[component]` table

**Root cause**: Manifest files use a `[component]` TOML table, but the parser reads flat top-level fields. Result: zero capabilities/workers register; the app is non-functional for chat.

**File**: `sovereignai/shared/manifest_parser.py`

### S1.1 — Unwrap `[component]` table in `parse_manifest`

**Old** (line 44-49):
```python
    with path.open("rb") as f:
        data = tomllib.load(f)

    # Required top-level fields
    component_id = data.get("component_id")
    version = data.get("version")
    author = data.get("author")
    content_hash = data.get("content_hash")
```

**New**:
```python
    with path.open("rb") as f:
        data = tomllib.load(f)

    # Support both flat format (component_id at root) and [component] table format.
    # The [component] table is idiomatic TOML and used by all real manifest files;
    # flat format is used by tests for simplicity. Unwrap if needed.
    if "component" in data and isinstance(data["component"], dict):
        data = {**data["component"], **{k: v for k, v in data.items() if k != "component"}}

    # Required top-level fields (now flat after unwrap)
    component_id = data.get("component_id")
    version = data.get("version")
    author = data.get("author")
    content_hash = data.get("content_hash")
```

**Why this approach**: The unwrap is backward-compatible — flat-format manifests (used by tests) have no `component` key, so the `if` is skipped and behavior is unchanged. Table-format manifests (used by real files) get unwrapped. The merge order (`**data["component"]` first, then other top-level keys like `provides`) preserves both the component fields and the `[[provides]]` array.

### S1.2 — Verify the fix

After editing, run:
```bash
.venv/Scripts/python.exe -c "
from pathlib import Path
from sovereignai.shared.manifest_parser import parse_manifest

# Test real manifests (table format)
m1 = parse_manifest(Path('skills/user/websearch_skill/manifest.toml'))
print(f'websearch: {m1.component_id} v{m1.version}, provides={len(m1.provides)}')
assert m1.component_id == 'websearch_skill'
assert len(m1.provides) >= 1

m2 = parse_manifest(Path('adapters/external/ollama_adapter/manifest.toml'))
print(f'ollama: {m2.component_id} v{m2.version}, provides={len(m2.provides)}')
assert m2.component_id == 'ollama_adapter'
assert len(m2.provides) >= 2

print('Both real manifests parse correctly.')
"
```

Then verify build_container registers them:
```bash
.venv/Scripts/python.exe -c "
from sovereignai.main import build_container
from sovereignai.shared.capability_graph import ICapabilityIndex
c = build_container()
idx = c.retrieve(ICapabilityIndex)
comps = idx.list_all_components()
print(f'Components registered: {len(comps)}')
for comp in comps:
    print(f'  - {comp.component_id} v{comp.version} ({len(comp.provides)} capabilities)')
assert len(comps) >= 2, 'Expected at least 2 components registered'
"
```

Expected: 2 components (websearch_skill, ollama_adapter). If 0, STOP — the unwrap didn't work.

---

## S2 — Fix Bug 2 (HIGH): `/api/dispatch` wrong keyword arguments

**Root cause**: The dispatch route calls `submit_task()` with wrong parameter names (`capability=`, `name=`) vs the actual signature (`category=`, `capability_name=`). Every chat message 500s.

**File**: `web/main.py`

### S2.1 — Fix the keyword argument names

**Old** (line 386-392):
```python
    try:
        task_id = capability_api.submit_task(
            capability=CapabilityCategory.TOOL,
            name="websearch",
            payload=message,
            token=token,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

**New**:
```python
    try:
        task_id = capability_api.submit_task(
            token=token,
            category=CapabilityCategory.TOOL,
            capability_name="websearch",
            payload=message,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
```

**Changes**:
- `capability=` → `category=` (matches `CapabilityAPI.submit_task` parameter name)
- `name=` → `capability_name=` (matches parameter name)
- Reordered to put `token` first (matches signature order — not required but improves readability)

### S2.2 — Verify the fix

After editing, launch the server and test dispatch:
```bash
# Start server
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8765 &

# Register + login
curl -s -X POST http://127.0.0.1:8765/api/auth/register -H "Content-Type: application/json" -d '{"username":"test","password":"testpass123"}'
curl -s -X POST http://127.0.0.1:8765/api/auth/login -H "Content-Type: application/json" -d '{"username":"test","password":"testpass123"}' -c /tmp/cookies.txt

# Test dispatch (should return a task_id, NOT a 500)
curl -s -X POST http://127.0.0.1:8765/api/dispatch -H "Content-Type: application/json" -d '{"message":"hello"}' -b /tmp/cookies.txt -w "\nStatus: %{http_code}\n"

# Expected: {"task_id":"...","state":"received","result":null,"error":null} Status: 200
# If 500, STOP — the kwarg fix didn't work.

# Cleanup
kill %1
```

**Note**: The dispatch route hardcodes `capability_name="websearch"`. This is a known limitation (OR56 — MessageDispatcher v1 doesn't do intent parsing). For v1 with one skill, this is acceptable. A future plan adds intent-based routing. Document this in the execution log but do NOT fix it here — out of scope.

---

## S3 — Fix Bug 3 (MEDIUM): Unauth API requests return 500 instead of 401

**Root cause**: The `first_run_redirect` middleware raises `HTTPException(401)` inside a `BaseHTTPMiddleware`. Starlette's `BaseHTTPMiddleware` swallows exceptions raised inside middleware and turns them into 500s. The frontend's auth check (`app.js` line 36) expects 401 → gets 500 → silent failure.

**File**: `web/main.py`

### S3.1 — Return JSONResponse instead of raising HTTPException

**Old** (line 86-93):
```python
    if len(auth._password_hashes) == 0:
        if path.startswith("/api/"):
            raise HTTPException(
                status_code=401, detail="No user registered — complete first-run setup"
            )
        return RedirectResponse(url="/register")  # type: ignore[no-any-return]

    return await call_next(request)  # type: ignore[no-any-return]
```

**New**:
```python
    if len(auth._password_hashes) == 0:
        if path.startswith("/api/"):
            # Return JSONResponse directly — raising HTTPException inside BaseHTTPMiddleware
            # gets swallowed by Starlette and turned into a 500. The frontend's auth check
            # (app.js) expects a clean 401 JSON response.
            return JSONResponse(
                status_code=401,
                content={"detail": "No user registered — complete first-run setup"},
            )
        return RedirectResponse(url="/register")  # type: ignore[no-any-return]

    return await call_next(request)  # type: ignore[no-any-return]
```

**Add import** at the top of `web/main.py` (if not already present):
```python
from starlette.responses import JSONResponse
```
(Check existing imports first — `RedirectResponse` is already imported from `starlette.responses`, so add `JSONResponse` to the same line.)

### S3.2 — Verify the fix

```bash
# Start server (fresh — no users registered yet)
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8766 &

# Test unauthenticated API request (should be 401, NOT 500)
curl -s http://127.0.0.1:8766/api/capabilities -w "\nStatus: %{http_code}\n"

# Expected: {"detail":"No user registered — complete first-run setup"} Status: 401
# If 500, STOP — the JSONResponse fix didn't work.

# Cleanup
kill %1
```

---

## S4 — Add Integration Tests (test coverage gaps)

**File**: `tests/test_web_ui_integration.py` (NEW)

The existing tests did not catch these bugs because:
- Manifest tests use flat format, not the real `[component]` table format
- The e2e test mocks `CapabilityAPI.submit_task()` — doesn't test real signature match
- No test checks API endpoints in first-run state

### S4.1 — Create `tests/test_web_ui_integration.py`

```python
"""Integration tests for the Web UI — load real manifests, test real endpoints.

These tests catch bugs that unit tests with mocks miss:
- Manifest format mismatch (Bug 1: [component] table vs flat)
- Dispatch route signature mismatch (Bug 2: wrong kwarg names)
- First-run API 401 handling (Bug 3: HTTPException in middleware → 500)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_no_users() -> TestClient:
    """Provide a TestClient with no registered users (first-run state)."""
    from web.main import app
    return TestClient(app)


@pytest.fixture
def client_authenticated() -> TestClient:
    """Provide a TestClient with a registered and logged-in user."""
    from web.main import app
    client = TestClient(app)
    client.post("/api/auth/register", json={"username": "testuser", "password": "testpass123"})
    client.post("/api/auth/login", json={"username": "testuser", "password": "testpass123"})
    return client


class TestManifestLoading:
    """Bug 1: manifests must load correctly (table format unwrap)."""

    def test_real_manifests_parse(self) -> None:
        """Verify the actual manifest files in skills/ and adapters/ parse without error."""
        from sovereignai.shared.manifest_parser import parse_manifest

        manifest_paths = [
            Path("skills/user/websearch_skill/manifest.toml"),
            Path("adapters/external/ollama_adapter/manifest.toml"),
        ]
        for mp in manifest_paths:
            manifest = parse_manifest(mp)
            assert manifest.component_id is not None, f"{mp} has no component_id"
            assert manifest.version is not None, f"{mp} has no version"
            assert len(manifest.provides) >= 1, f"{mp} has no capabilities"

    def test_build_container_registers_components(self) -> None:
        """Verify build_container() registers the real manifests in the capability graph."""
        from sovereignai.main import build_container
        from sovereignai.shared.capability_graph import ICapabilityIndex

        container = build_container()
        idx = container.retrieve(ICapabilityIndex)
        components = idx.list_all_components()
        component_ids = {str(c.component_id) for c in components}

        assert "websearch_skill" in component_ids, "websearch_skill not registered"
        assert "ollama_adapter" in component_ids, "ollama_adapter not registered"

    def test_flat_format_still_works(self) -> None:
        """Verify flat-format manifests (used by existing tests) still parse after the unwrap fix."""
        from sovereignai.shared.manifest_parser import parse_manifest
        from sovereignai.shared.types import CapabilityCategory

        manifest_file = Path("test_flat_manifest.toml")
        manifest_file.write_text(
            'component_id = "TestAdapter"\n'
            'version = "1.0.0"\n'
            'author = "test"\n'
            'content_hash = "sha256:abc"\n\n'
            '[[provides]]\n'
            'category = "model_inference"\n'
            'name = "text_generation"\n'
            'version = "1.0.0"\n'
            'priority = 10\n'
        )
        try:
            manifest = parse_manifest(manifest_file)
            assert manifest.component_id == "TestAdapter"
            assert len(manifest.provides) == 1
        finally:
            manifest_file.unlink()


class TestDispatchRoute:
    """Bug 2: /api/dispatch must use correct submit_task kwarg names."""

    def test_dispatch_returns_task_id(self, client_authenticated: TestClient) -> None:
        """Verify dispatch returns a task_id (not a 500 from wrong kwargs)."""
        response = client_authenticated.post(
            "/api/dispatch",
            json={"message": "test message"},
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "task_id" in data, f"Response missing task_id: {data}"
        assert "state" in data, f"Response missing state: {data}"


class TestFirstRunAuthHandling:
    """Bug 3: unauthenticated API requests must return 401, not 500."""

    def test_api_capabilities_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify API endpoints return 401 (not 500) when no users are registered."""
        response = client_no_users.get("/api/capabilities")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data, f"Response missing detail: {data}"

    def test_api_workers_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify /api/workers returns 401 (not 500) on first run."""
        response = client_no_users.get("/api/workers")
        assert response.status_code == 401

    def test_api_tasks_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify /api/tasks returns 401 (not 500) on first run."""
        response = client_no_users.get("/api/tasks")
        assert response.status_code == 401

    def test_authenticated_capabilities_returns_200(self, client_authenticated: TestClient) -> None:
        """Verify /api/capabilities returns 200 (with content) after login."""
        response = client_authenticated.get("/api/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # After Bug 1 fix, there should be at least 2 capabilities (websearch + ollama)
        assert len(data) >= 2, f"Expected >=2 capabilities, got {len(data)}: {data}"
```

### S4.2 — Run the new tests

```bash
.venv/Scripts/python.exe -m pytest tests/test_web_ui_integration.py -vvv
```

All tests must pass. If any fail, STOP — the corresponding bug fix didn't work.

---

## S5 — Run Full Verification

Per `/close` steps 1–8 (re-read close.md fresh per OR71). **Per OR83, use `git add -A` for ALL commits.**

### S5.1 — Tests with coverage (per OR77)
```bash
.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing
```
Expected: 169 + 8 new tests = 177 passed, 3 skipped. Coverage ≥93% (may tick up slightly from new tests). If coverage <88%, STOP.

### S5.2 — Ruff
```bash
.venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
```
Expected: 0 errors.

### S5.3 — Mypy (full repo)
```bash
.venv/Scripts/mypy.exe . --ignore-missing-imports 2>&1 | tail -n 5
```
Expected: 0 errors.

### S5.4 — Bandit
```bash
.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
```
Expected: ~340 Low (B101) — count grows by ~8 from new test assertions. Update PLANS.md baseline per OR78.

### S5.5 — pip-audit
```bash
.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
```
Expected: 0 CVEs.

### S5.6 — Vulture
```bash
.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
```
Expected: 0 new findings.

### S5.7 — detect-secrets (per OR81)
```bash
.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
```
Expected: exit 0.

### S5.8 — Custom AR checks
```bash
.venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
.venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/docstring_discipline.py sovereignai/
.venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
.venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
```
All must pass. Per OR72 — do NOT edit these scripts to make failures pass.

### S5.9 — Manual smoke test (end-to-end)

After all automated tests pass, do a manual smoke test:
```bash
# Start server
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8765 &

# Register + login
curl -s -X POST http://127.0.0.1:8765/api/auth/register -H "Content-Type: application/json" -d '{"username":"smoke","password":"smokepass123"}'
curl -s -X POST http://127.0.0.1:8765/api/auth/login -H "Content-Type: application/json" -d '{"username":"smoke","password":"smokepass123"}' -c /tmp/smoke-cookies.txt

# Verify capabilities (should now show websearch + ollama)
curl -s http://127.0.0.1:8765/api/capabilities -b /tmp/smoke-cookies.txt | python -m json.tool
# Expected: list with >=2 entries

# Verify dispatch works (should return task_id, not 500)
curl -s -X POST http://127.0.0.1:8765/api/dispatch -H "Content-Type: application/json" -d '{"message":"hello"}' -b /tmp/smoke-cookies.txt
# Expected: {"task_id":"...","state":"received",...}

# Verify first-run 401 (start a second server on a different port with no users)
.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8766 &
curl -s http://127.0.0.1:8766/api/capabilities -w "\nStatus: %{http_code}\n"
# Expected: {"detail":"No user registered..."} Status: 401

# Cleanup
kill %1 %2
```

If any smoke test fails, STOP.

---

## STOP Conditions

- If S1.2 verification shows 0 components registered after the parser fix, STOP.
- If S2.2 dispatch test returns 500, STOP.
- If S3.2 first-run test returns 500 instead of 401, STOP.
- If any test in S4.2 fails, STOP.
- If any static analysis tool in S5 fails, STOP.
- If S5.9 manual smoke test fails, STOP.
- If coverage <88%, STOP (per OR77).
- If `git status -s` after any `git add -A` shows unstaged changes, STOP (per OR83).

---

## Files WILL Edit

- `sovereignai/shared/manifest_parser.py` (S1 — unwrap `[component]` table)
- `web/main.py` (S2 — fix dispatch kwargs; S3 — JSONResponse instead of HTTPException in middleware; add JSONResponse import)

## Files WILL Create

- `tests/test_web_ui_integration.py` (S4 — 8 integration tests)

## Files WILL NOT Edit

- Any other file in `sovereignai/shared/` (only `manifest_parser.py` is edited — minimal core change, justified by Bug 1)
- Any AR check script (per OR72)
- `txt/.secrets.baseline` (per OR81)
- `txt/requirements.txt`
- `project-vision-Rev5.md`
- Existing tests (the new tests are additive — do not modify existing test files)

---

## Closing

Run `/close`. Tag: `prompt-10.4`.

**Critical per OR83**: Every `git commit` MUST use `git add -A` — no explicit `git add <file>` lists.

**Critical per OR76**: Before `git tag prompt-10.4`, verify `git tag --list prompt-10.4` is empty.

**Critical per OR71**: Re-read `.devin/workflows/close.md` in full before running `/close`.

After `prompt-10.4` completes, the Web UI is functional:
- Manifests load → capabilities/workers visible in UI
- Dispatch works → chat form submits tasks
- First-run API returns clean 401 → frontend auth check works

The repo is then ready for Plan 11 (memory layer) with a working Web UI for testing it.

---

## Adjudication Summary

This patch addresses 3 bugs found by manual Web UI testing (see `web-ui-test-report.md`):

1. **Bug 1 (CRITICAL)**: Manifest parser unwraps `[component]` table — fixes zero-capabilities registration. 1-line core change to `manifest_parser.py`, backward-compatible with flat-format tests.
2. **Bug 2 (HIGH)**: Dispatch route uses correct `submit_task()` kwarg names (`category=`, `capability_name=`) — fixes 500 on every chat message.
3. **Bug 3 (MEDIUM)**: First-run middleware returns `JSONResponse(401)` instead of raising `HTTPException` — fixes 500-on-unauth and unblocks frontend auth check.

Plus 8 integration tests that would have caught all 3 bugs — covering the test coverage gaps identified in the report.

Not addressed (out of scope):
- Hardcoded `capability_name="websearch"` in dispatch route (OR56 defers intent parsing to a future plan)
- `intent_keywords` field in manifests not used (same deferral)
- `/api/workers` returns `c.version` as `name` (minor cosmetic — Issue 4 in the report)
