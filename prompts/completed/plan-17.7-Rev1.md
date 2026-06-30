# Plan 17.7 — Fix Auth Deletion + Pull Method + Load More + Log Toggle Button

**Hotfix**: Fix auth.json being overwritten by tests, fix model pull for older Ollama, restore Load More button, restore log toggle button. Round Table vetoed.

Depends on: prompt-17.6

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-17.6` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Read `close.md` in full (per OR71).

**S0.3** — No new rules. Proceed to S1.

---

## S1 — Fix auth.json being overwritten by tests (CRITICAL)

**Problem**: Tests call `container.retrieve(AuthMiddleware)` which returns the PRODUCTION AuthMiddleware. When tests call `register_user("testuser")`, it calls `_save_users()` which **overwrites** `settings/auth.json` with only test users — wiping the user's real account.

### S1.1 — Fix test_e2e_task_submission.py container fixture

**File**: `tests/test_e2e_task_submission.py`

**Find**:
```python
@pytest.fixture
def container(client: TestClient) -> Any:
    """Get the container from the app state and clear auth users for fresh test state."""
    container = client.app.state.container
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth._password_hashes.clear()
    auth._salts.clear()
    return container
```

**Replace with** (do NOT clear production users — use a mock instead):
```python
@pytest.fixture
def container(client: TestClient) -> Any:
    """Get the container from the app state."""
    return client.app.state.container


@pytest.fixture
def authenticated_client(client: TestClient) -> TestClient:
    """Create an authenticated test client using dependency override (no real auth needed)."""
    from unittest.mock import MagicMock
    client.app.dependency_overrides[web.main.get_current_user] = lambda: MagicMock(username="test")
    return client
```

### S1.2 — Fix all tests that call register_user on container AuthMiddleware

**File**: `tests/test_web_auth.py`

Every test that does `auth = container.retrieve(AuthMiddleware)` then `auth.register_user(...)` is writing to the production auth file. Replace ALL of them to use `fresh_auth` fixture instead.

**For each test function**, change:
```python
def test_login_success(client: TestClient, container: Any) -> None:
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpassword123")
```

To:
```python
def test_login_success(fresh_auth) -> None:
    fresh_auth.register_user("testuser", "testpassword123")
```

Do this for ALL test functions in `test_web_auth.py` that use `container.retrieve(AuthMiddleware)` + `register_user`.

### S1.3 — Fix test_first_run.py

**File**: `tests/test_first_run.py`

Same pattern — replace `container.retrieve(AuthMiddleware)` + `register_user` with `fresh_auth` fixture.

### S1.4 — Fix test_thinking_display.py

**File**: `tests/test_thinking_display.py`

Same pattern — replace `container.retrieve(AuthMiddleware)` + `register_user` with `fresh_auth` fixture.

### S1.5 — Fix test_log_drawer_integration.py

**File**: `tests/test_log_drawer_integration.py`

Same pattern — replace `container.retrieve(AuthMiddleware)` + `register_user` with `fresh_auth` fixture.

### S1.6 — Fix test_composition_root.py

**File**: `tests/test_composition_root.py`

Same pattern — any test that calls `register_user` on the container auth should use `fresh_auth` instead.

### S1.7 — Make _save_users safe in test mode

**File**: `sovereignai/shared/auth.py`

As a belt-and-suspenders fix, make `_save_users()` skip writing to disk when `SOVEREIGNAI_TEST_MODE=1`:

**Find**:
```python
    def _save_users(self) -> None:
        """Persist user hashes and salts to disk."""
        _AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
```

**Replace with**:
```python
    def _save_users(self) -> None:
        """Persist user hashes and salts to disk. Skipped in test mode."""
        import os
        if os.environ.get("SOVEREIGNAI_TEST_MODE") == "1":
            return  # Never write auth file in test mode
        _AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
```

This ensures that even if a test accidentally calls `register_user` on the production AuthMiddleware, it won't overwrite `settings/auth.json`.

---

## S2 — Fix model pull for older Ollama versions

**Problem**: `ollama pull hf.co/...` requires Ollama 0.4+. The user has Ollama 0.30.7 which doesn't support this syntax.

**File**: `web/main.py`

In the `_pull()` function, change the pull approach to download the GGUF file directly from HuggingFace and create the model via `ollama create`:

**Find** the `_pull()` function and **replace with**:

```python
    def _pull() -> None:
        import subprocess
        import os
        import tempfile
        import urllib.request
        import json as _json
        try:
            trace.emit(component="models", level=TraceLevel.INFO,
                       message=f"Starting pull: {model_name} ({quant})")
            _pull_status[model_name] = {"status": "pulling", "message": f"Downloading {model_name}...", "progress": 0}

            # Step 1: Get GGUF file list from HuggingFace
            hf_api_url = f"https://huggingface.co/api/models/{model_name}"
            req = urllib.request.Request(hf_api_url, headers={"User-Agent": "SovereignAI/0.1"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                model_data = _json.loads(resp.read().decode("utf-8"))

            siblings = model_data.get("siblings", [])
            gguf_files = [s.get("rfilename", "") for s in siblings if s.get("rfilename", "").endswith(".gguf")]

            if not gguf_files:
                _pull_status[model_name] = {"status": "error", "message": "No GGUF files found", "progress": 0}
                trace.emit(component="models", level=TraceLevel.ERROR, message=f"No GGUF files in {model_name}")
                return

            # Step 2: Find the requested quantization
            target_file = None
            for f in gguf_files:
                if quant.lower() in f.lower():
                    target_file = f
                    break
            if not target_file:
                # Fallback: find Q4_K_M, then any file
                for f in gguf_files:
                    if "q4_k_m" in f.lower():
                        target_file = f
                        break
            if not target_file:
                target_file = gguf_files[0]

            download_url = f"https://huggingface.co/{model_name}/resolve/main/{target_file}"
            trace.emit(component="models", level=TraceLevel.INFO,
                       message=f"Downloading {target_file} from HuggingFace...")

            # Step 3: Download to temp directory
            temp_dir = tempfile.mkdtemp(prefix="sovereignai_pull_")
            local_path = os.path.join(temp_dir, os.path.basename(target_file))

            req = urllib.request.Request(download_url, headers={"User-Agent": "SovereignAI/0.1"})
            with urllib.request.urlopen(req, timeout=3600) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(local_path, "wb") as f:
                    while True:
                        chunk = resp.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = int(downloaded * 100 / total)
                            trace.emit(component="models", level=TraceLevel.INFO,
                                       message=f"Download: {pct}% ({downloaded // 1048576}MB / {total // 1048576}MB)")

            trace.emit(component="models", level=TraceLevel.INFO,
                       message=f"Download complete, creating Ollama model...")

            # Step 4: Create Modelfile and register with Ollama
            ollama_name = model_name.replace("/", "_").lower()
            modelfile_path = os.path.join(temp_dir, "Modelfile")
            with open(modelfile_path, "w") as f:
                f.write(f"FROM {local_path}\n")

            result = subprocess.run(
                ["ollama", "create", ollama_name, "-f", modelfile_path],
                capture_output=True, text=True, timeout=300,
            )

            if result.returncode == 0:
                _pull_status[model_name] = {"status": "done", "message": f"Created {ollama_name}", "progress": 100}
                trace.emit(component="models", level=TraceLevel.INFO,
                           message=f"Model {ollama_name} created successfully")
            else:
                err = result.stderr.strip()[:200] if result.stderr else "Unknown error"
                _pull_status[model_name] = {"status": "error", "message": f"ollama create failed: {err}", "progress": 0}
                trace.emit(component="models", level=TraceLevel.ERROR,
                           message=f"ollama create failed: {err}")

            # Cleanup temp files
            try:
                os.remove(local_path)
                os.remove(modelfile_path)
                os.rmdir(temp_dir)
            except OSError:
                pass

        except Exception as exc:
            _pull_status[model_name] = {"status": "error", "message": f"Pull error: {exc}", "progress": 0}
            trace.emit(component="models", level=TraceLevel.ERROR,
                       message=f"Pull error: {exc}")
```

**Key changes**:
- Downloads the GGUF file directly from HuggingFace (works with any Ollama version)
- Creates a Modelfile pointing to the downloaded file
- Runs `ollama create` (not `ollama pull`) — works with Ollama 0.30+
- Shows download progress in the log drawer (percentage + MB)
- Cleans up temp files after

---

## S3 — Restore "Load More" button

**File**: `web/static/app.js`

Check if `loadHFCatalog` has the Load More button code. If missing or broken, ensure the pagination code from Plan 17.6 is present:

```javascript
// At the end of loadHFCatalog, after rendering models:
if (models.length === HF_PAGE_SIZE) {
    hfOffset += HF_PAGE_SIZE;
    const btn = document.createElement('button');
    btn.id = 'load-more-btn';
    btn.className = 'load-more-btn';
    btn.textContent = 'Load More Models';
    btn.onclick = function() { loadHFCatalog(false); };
    list.appendChild(btn);
}
```

Also ensure `hfOffset` and `HF_PAGE_SIZE` variables exist at the top of the file:
```javascript
let hfOffset = 0;
const HF_PAGE_SIZE = 50;
```

And ensure the catalog API endpoint accepts `offset` (from Plan 17.6 S6). Verify `hf_catalog.py` passes `offset` to the HF API.

---

## S4 — Restore log toggle button

**File**: `web/templates/index.html`

Check if the "Logs" toggle button exists. If missing, add it before the log drawer:

```html
<button id="log-toggle">Logs</button>
<div id="log-drawer" class="open">
```

**File**: `web/static/app.js`

Ensure `setupLogDrawer()` is called on page load and the toggle works:

```javascript
function setupLogDrawer() {
    const toggleButton = document.getElementById('log-toggle');
    const logDrawer = document.getElementById('log-drawer');
    if (!toggleButton || !logDrawer) return;
    toggleButton.addEventListener('click', () => {
        logDrawer.classList.toggle('open');
    });
    // ... rest of log drawer setup (filters, search, clear)
}
```

---

## S5 — Run /close (ALL 22 steps per OR96)

Run the full `/close` workflow. Do NOT skip any steps. Do NOT commit with known failures. Do NOT tag until all steps pass.

**CRITICAL**: After running tests, verify that `settings/auth.json` still has the user's real account. If tests overwrite it, S1 is not complete — fix before continuing.

---

## Files WILL Edit
- `tests/test_e2e_task_submission.py` (S1.1)
- `tests/test_web_auth.py` (S1.2)
- `tests/test_first_run.py` (S1.3)
- `tests/test_thinking_display.py` (S1.4)
- `tests/test_log_drawer_integration.py` (S1.5)
- `tests/test_composition_root.py` (S1.6)
- `sovereignai/shared/auth.py` (S1.7 — skip _save_users in test mode)
- `web/main.py` (S2 — fix pull method)
- `web/static/app.js` (S3 — load more, S4 — log toggle)
- `web/templates/index.html` (S4 — log toggle button)

## Files WILL NOT Edit
- `sovereignai/main.py`

---

## Closing

Run `/close`. Tag: `prompt-17.7`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh. Per OR96, complete ALL 22 steps.
