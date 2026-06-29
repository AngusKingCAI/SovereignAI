# Plan 17 Rev2 — Models Panel (HuggingFace Catalog + Installed) + Memory Panel + Orchestrator Model Select + Options

**Special plan**: UI/functional. Gets all 9 panels populating + local model selection. Round Table vetoed.

Depends on: prompt-16
Vision principles: P2 (pluggable), P3 (no provider lock-in), P4 (local-first), P9 (observability)
Open questions resolved: none

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-16` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Note OR71, OR75/OR80/OR83, OR86 (backend+UI same plan), OR87 (no disabling features for tests).

**S0.3** — Add one rule:
- **OR91**: API keys and provider config are stored at `~/.sovereignai/config.json` (not in environment variables, not in source code). The file is created on first save with `chmod 600`. The Options panel UI provides a form to enter/save/delete keys. Adapters retrieve keys via `config_loader.get_api_key(provider)`. Source: Plan 17.

Commit: `docs: add OR91 for prompt-17`

---

## S1 — Config loader (for API keys, Ollama host, etc.)

**File**: `sovereignai/shared/config_loader.py` (new)

```python
"""Load and save user configuration from ~/.sovereignai/config.json."""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(os.path.expanduser("~/.sovereignai/config.json"))

def load_config() -> dict:
    """Load user config. Returns empty dict if not found."""
    if not CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

def save_config(config: dict) -> None:
    """Save user config with restrictive permissions."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
    try:
        os.chmod(CONFIG_PATH, 0o600)
    except OSError:
        pass

def get_config_value(key: str, default=None):
    """Get a config value by dotted key (e.g., 'ollama.host')."""
    config = load_config()
    for part in key.split("."):
        if not isinstance(config, dict):
            return default
        config = config.get(part, default)
    return config

def set_config_value(key: str, value) -> None:
    """Set a config value by dotted key."""
    config = load_config()
    parts = key.split(".")
    d = config
    for part in parts[:-1]:
        d = d.setdefault(part, {})
    d[parts[-1]] = value
    save_config(config)

def get_api_key(provider: str) -> str | None:
    """Get an API key for a provider."""
    return get_config_value(f"api_keys.{provider}")

def set_api_key(provider: str, key: str) -> None:
    """Set an API key for a provider."""
    set_config_value(f"api_keys.{provider}", key)

def delete_api_key(provider: str) -> None:
    """Delete an API key for a provider."""
    config = load_config()
    config.get("api_keys", {}).pop(provider, None)
    save_config(config)
```

---

## S2 — HuggingFace catalog API (no scraping, no API key needed)

**File**: `sovereignai/shared/hf_catalog.py` (new)

```python
"""Fetch model catalog from HuggingFace API. No API key needed for listing."""
import urllib.request
import urllib.parse
import json
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel

HF_API_BASE = "https://huggingface.co/api/models"

def fetch_gguf_models(trace: TraceEmitter, search: str = "", limit: int = 50) -> list[dict]:
    """Fetch GGUF models from HuggingFace API, sorted by downloads.
    
    Returns list of dicts with: id, publisher, downloads, tags, last_modified.
    """
    params = {
        "filter": "gguf",
        "sort": "downloads",
        "direction": "-1",
        "limit": str(limit),
    }
    if search:
        params["search"] = search
    
    url = f"{HF_API_BASE}?{urllib.parse.urlencode(params)}"
    trace.emit(component="hf_catalog", level=TraceLevel.INFO,
               message=f"Fetching GGUF models from HuggingFace: {url}")
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SovereignAI/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        models = []
        for m in data:
            model_id = m.get("id", "")
            publisher = model_id.split("/")[0] if "/" in model_id else "unknown"
            models.append({
                "id": model_id,
                "publisher": publisher,
                "name": model_id.split("/")[-1] if "/" in model_id else model_id,
                "downloads": m.get("downloads", 0),
                "likes": m.get("likes", 0),
                "tags": m.get("tags", []),
                "last_modified": m.get("lastModified", ""),
                "pipeline_tag": m.get("pipeline_tag", ""),
            })
        
        trace.emit(component="hf_catalog", level=TraceLevel.INFO,
                   message=f"Fetched {len(models)} GGUF models from HuggingFace")
        return models
    except Exception as exc:
        trace.emit(component="hf_catalog", level=TraceLevel.ERROR,
                   message=f"Failed to fetch HuggingFace catalog: {exc}")
        return []

def get_model_files(trace: TraceEmitter, model_id: str) -> list[dict]:
    """Get available GGUF files for a specific model (for quantization selection)."""
    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "SovereignAI/0.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        siblings = data.get("siblings", [])
        gguf_files = []
        for s in siblings:
            fname = s.get("rfilename", "")
            if fname.endswith(".gguf"):
                # Parse quantization from filename (e.g., "model-Q4_K_M.gguf")
                quant = "unknown"
                for q in ["Q4_K_M", "Q4_K_S", "Q5_K_M", "Q5_K_S", "Q6_K", "Q8_0", "Q3_K_M", "Q3_K_S", "Q2_K", "F16", "F32"]:
                    if q.lower() in fname.lower():
                        quant = q
                        break
                gguf_files.append({
                    "filename": fname,
                    "quantization": quant,
                    "download_url": f"https://huggingface.co/{model_id}/resolve/main/{fname}",
                })
        
        return gguf_files
    except Exception as exc:
        trace.emit(component="hf_catalog", level=TraceLevel.ERROR,
                   message=f"Failed to get files for {model_id}: {exc}")
        return []
```

---

## S3 — Models panel API

**File**: `web/main.py`

### S3.1 — Installed models (from Ollama)

```python
@app.get("/api/models/installed", dependencies=[Depends(get_current_user)])
async def get_installed_models(request: Request) -> list[dict]:
    """List models installed locally via Ollama."""
    container: Any = request.app.state.container
    models = []
    try:
        import ollama
        result = ollama.list()
        for m in result.get("models", []):
            models.append({
                "id": m.get("name", "unknown"),
                "provider": "ollama",
                "size": m.get("size", 0),
                "status": "installed",
            })
    except Exception as exc:
        # Ollama not running or not installed
        pass
    return models
```

### S3.2 — HuggingFace catalog (browse available GGUF models)

```python
@app.get("/api/models/catalog", dependencies=[Depends(get_current_user)])
async def get_model_catalog(
    request: Request,
    search: str = "",
    limit: int = 50,
) -> list[dict]:
    """Browse available GGUF models from HuggingFace."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    from sovereignai.shared.hf_catalog import fetch_gguf_models
    return fetch_gguf_models(trace, search=search, limit=limit)

@app.get("/api/models/catalog/{model_id:path}", dependencies=[Depends(get_current_user)])
async def get_model_detail(request: Request, model_id: str) -> dict:
    """Get available GGUF files (quantizations) for a specific model."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    from sovereignai.shared.hf_catalog import get_model_files
    files = get_model_files(trace, model_id)
    return {"model_id": model_id, "files": files}
```

### S3.3 — Pull model (download via Ollama)

```python
@app.post("/api/models/pull", dependencies=[Depends(get_current_user)])
async def pull_model(request: Request) -> dict:
    """Pull a model via Ollama. Returns task_id for progress tracking."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    data = await request.json()
    model_name = data.get("model", "")
    if not model_name:
        raise HTTPException(status_code=400, detail="model is required")
    
    trace.emit(component="models", level=TraceLevel.INFO,
               message=f"Pulling model: {model_name}")
    
    # Run ollama pull in background (it's a long operation)
    import subprocess, threading
    
    def _pull():
        try:
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True, text=True, timeout=3600,
            )
            if result.returncode == 0:
                trace.emit(component="models", level=TraceLevel.INFO,
                           message=f"Model {model_name} pulled successfully")
            else:
                trace.emit(component="models", level=TraceLevel.ERROR,
                           message=f"Model pull failed: {result.stderr}")
        except Exception as exc:
            trace.emit(component="models", level=TraceLevel.ERROR,
                       message=f"Model pull error: {exc}")
    
    thread = threading.Thread(target=_pull, daemon=True)
    thread.start()
    
    return {"status": "pulling", "model": model_name}
```

### S3.4 — All models (combined view)

```python
@app.get("/api/models", dependencies=[Depends(get_current_user)])
async def get_all_models(request: Request) -> dict:
    """Get installed models + catalog summary."""
    container: Any = request.app.state.container
    
    # Installed
    installed = []
    try:
        import ollama
        result = ollama.list()
        for m in result.get("models", []):
            installed.append({
                "id": m.get("name", "unknown"),
                "provider": "ollama",
                "size": m.get("size", 0),
                "status": "installed",
            })
    except Exception:
        pass
    
    return {
        "installed": installed,
        "providers": [
            {"id": "huggingface", "name": "HuggingFace", "type": "catalog"},
            {"id": "ollama", "name": "Ollama (Installed)", "type": "local"},
        ],
    }
```

---

## S4 — Models panel UI

**File**: `web/templates/index.html`

Replace the Models panel:
```html
<section id="panel-models" class="panel">
    <h2>Models</h2>
    <div class="models-tabs">
        <button class="models-tab active" onclick="switchModelsTab('installed')">Installed</button>
        <button class="models-tab" onclick="switchModelsTab('huggingface')">HuggingFace</button>
    </div>
    <div id="models-installed" class="models-content">
        <div id="installed-models-list"></div>
    </div>
    <div id="models-huggingface" class="models-content" style="display:none;">
        <div class="models-search">
            <input type="text" id="hf-search" placeholder="Search GGUF models..." onkeyup="if(event.key==='Enter')loadHFCatalog()">
            <button onclick="loadHFCatalog()">Search</button>
        </div>
        <div id="hf-models-list"></div>
    </div>
</section>
```

**File**: `web/static/app.js`

```javascript
let currentModelsTab = 'installed';

function switchModelsTab(tab) {
    currentModelsTab = tab;
    document.querySelectorAll('.models-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.models-tab[onclick*="${tab}"]`).classList.add('active');
    document.getElementById('models-installed').style.display = tab === 'installed' ? 'block' : 'none';
    document.getElementById('models-huggingface').style.display = tab === 'huggingface' ? 'block' : 'none';
    if (tab === 'installed') loadInstalledModels();
    if (tab === 'huggingface') loadHFCatalog();
}

function loadInstalledModels() {
    fetch('/api/models/installed')
        .then(r => r.json())
        .then(models => {
            const list = document.getElementById('installed-models-list');
            list.innerHTML = '';
            if (models.length === 0) {
                list.innerHTML = '<p>No models installed. Pull a model from the HuggingFace tab or run <code>ollama pull llama3.2</code>.</p>';
                return;
            }
            models.forEach(m => {
                const entry = document.createElement('div');
                entry.className = 'model-entry installed';
                const size = m.size ? `${(m.size / 1e9).toFixed(1)}GB` : '';
                entry.innerHTML = `<span class="model-name">${m.id}</span> <span class="model-size">${size}</span>`;
                list.appendChild(entry);
            });
        });
}

function loadHFCatalog() {
    const search = document.getElementById('hf-search').value;
    const url = `/api/models/catalog${search ? '?search=' + encodeURIComponent(search) : ''}`;
    fetch(url)
        .then(r => r.json())
        .then(models => {
            const list = document.getElementById('hf-models-list');
            list.innerHTML = '';
            if (models.length === 0) {
                list.innerHTML = '<p>No models found. Try a different search.</p>';
                return;
            }
            // Group by publisher
            const byPublisher = {};
            models.forEach(m => {
                if (!byPublisher[m.publisher]) byPublisher[m.publisher] = [];
                byPublisher[m.publisher].push(m);
            });
            for (const [publisher, pubModels] of Object.entries(byPublisher)) {
                const section = document.createElement('div');
                section.className = 'model-publisher-section';
                section.innerHTML = `<h3>${publisher}</h3>`;
                pubModels.forEach(m => {
                    const entry = document.createElement('div');
                    entry.className = 'model-entry catalog';
                    const downloads = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : m.downloads;
                    entry.innerHTML = `
                        <span class="model-name">${m.name}</span>
                        <span class="model-downloads">⬇ ${downloads}</span>
                        <button class="pull-btn" onclick="pullModel('${m.id}')">Pull</button>
                    `;
                    section.appendChild(entry);
                });
                list.appendChild(section);
            }
        });
}

function pullModel(modelId) {
    if (!confirm(`Pull ${modelId}? This will download the model via Ollama.`)) return;
    fetch('/api/models/pull', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: modelId}),
        credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(result => {
        alert(`Pulling ${modelId}... Check the log drawer for progress.`);
    });
}
```

---

## S5 — Orchestrator model selector

**File**: `web/templates/index.html`

Add a model selector dropdown above the chat form in the Orchestrator panel:
```html
<section id="panel-orchestrator" class="panel active">
    <h2>Orchestrator</h2>
    <div class="orchestrator-controls">
        <select id="model-selector" onchange="selectModel(this.value)">
            <option value="">Select a model...</option>
        </select>
    </div>
    <div id="chat-log"></div>
    <div id="orchestrator-thinking" style="display: none;">
        <div id="thinking-header" onclick="toggleThinking()">
            <span id="thinking-status">Working...</span>
            <span id="thinking-arrow">▼</span>
        </div>
        <div id="thinking-content" style="display: none;"></div>
    </div>
    <form id="chat-form">
        <input type="text" id="chat-input" placeholder="Send a message..." autocomplete="off">
        <button type="submit">Send</button>
    </form>
</section>
```

**File**: `web/static/app.js`

```javascript
let selectedModel = null;

function loadModelSelector() {
    fetch('/api/models/installed')
        .then(r => r.json())
        .then(models => {
            const selector = document.getElementById('model-selector');
            const current = selector.value;
            selector.innerHTML = '<option value="">Select a model...</option>';
            models.forEach(m => {
                const option = document.createElement('option');
                option.value = m.id;
                option.textContent = m.id;
                if (m.id === current) option.selected = true;
                selector.appendChild(option);
            });
            if (models.length === 0) {
                selector.innerHTML = '<option value="">No models installed — pull one first</option>';
            }
        });
}

function selectModel(modelId) {
    selectedModel = modelId;
}

// Update the dispatch handler to include the selected model:
// In setupChatForm, change the fetch body to include model:
//   body: JSON.stringify({message: message, model: selectedModel})
```

**File**: `web/main.py` — update the dispatch endpoint to accept a `model` parameter:

```python
@app.post("/api/dispatch", dependencies=[Depends(get_current_user)])
async def dispatch(request: Request) -> TaskResponseDTO:
    """Submit a message to the orchestrator with optional model selection."""
    # ... existing code ...
    data = await request.json()
    message = data.get("message", "")
    model = data.get("model", None)  # NEW: optional model selection
    
    # If a model is selected, use Ollama directly for chat
    if model:
        try:
            import ollama
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": message}],
            )
            return TaskResponseDTO(
                task_id=str(uuid4()),
                state="complete",
                result=response.get("message", {}).get("content", ""),
                error=None,
            )
        except Exception as exc:
            return TaskResponseDTO(
                task_id=str(uuid4()),
                state="failed",
                result=None,
                error=str(exc),
            )
    
    # No model selected — use existing websearch dispatch
    # ... existing code ...
```

---

## S6 — Memory panel API + UI

### S6.1 — API

**File**: `web/main.py`

```python
@app.get("/api/memory/backends", dependencies=[Depends(get_current_user)])
async def get_memory_backends(request: Request) -> list[dict]:
    """List registered memory backends with type and storage info."""
    container: Any = request.app.state.container
    backends = []
    
    backend_specs = [
        ("episodic", "EpisodicMemoryBackend", "~/.sovereignai/episodic.db", "SQLite"),
        ("procedural", "ProceduralMemoryBackend", "~/.sovereignai/procedural_memory.json", "JSON"),
        ("trace", "TraceMemoryBackend", "~/.sovereignai/trace.db", "SQLite"),
        ("working", "WorkingMemoryBackend", "in-memory (volatile)", "Python dict"),
    ]
    
    for mem_type, class_name, storage, engine in backend_specs:
        registered = False
        record_count = 0
        try:
            module_path, cls_name = {
                "EpisodicMemoryBackend": ("sovereignai.memory.episodic_backend", "EpisodicMemoryBackend"),
                "ProceduralMemoryBackend": ("sovereignai.memory.procedural_backend", "ProceduralMemoryBackend"),
                "TraceMemoryBackend": ("sovereignai.memory.trace_backend", "TraceMemoryBackend"),
                "WorkingMemoryBackend": ("sovereignai.memory.working_backend", "WorkingMemoryBackend"),
            }[class_name]
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, cls_name)
            backend = container.retrieve(cls)
            registered = True
            if hasattr(backend, 'query'):
                try:
                    record_count = len(backend.query({}))
                except Exception:
                    record_count = 0
        except (KeyError, Exception):
            pass
        
        backends.append({
            "type": mem_type,
            "storage": storage,
            "engine": engine,
            "registered": registered,
            "records": record_count,
        })
    
    return backends
```

### S6.2 — Memory panel UI

**File**: `web/templates/index.html`

```html
<section id="panel-memory" class="panel">
    <h2>Memory</h2>
    <div id="memory-backends"></div>
</section>
```

**File**: `web/static/app.js`

```javascript
function loadMemory() {
    fetch('/api/memory/backends')
        .then(r => r.json())
        .then(backends => {
            const list = document.getElementById('memory-backends');
            list.innerHTML = '';
            backends.forEach(b => {
                const entry = document.createElement('div');
                entry.className = 'memory-backend-entry';
                const status = b.registered ? '✅' : '❌';
                entry.innerHTML = `
                    <h3>${b.type} ${status}</h3>
                    <p>Engine: ${b.engine}</p>
                    <p>Storage: ${b.storage}</p>
                    <p>Records: ${b.records}</p>
                `;
                list.appendChild(entry);
            });
        });
}
```

---

## S7 — Options panel API + UI (API keys + Ollama config)

**File**: `web/main.py`

```python
@app.get("/api/options/config", dependencies=[Depends(get_current_user)])
async def get_options_config(request: Request) -> dict:
    """Get user configuration (API keys are masked)."""
    from sovereignai.shared.config_loader import load_config
    config = load_config()
    # Mask API keys
    api_keys = {}
    for provider, key in config.get("api_keys", {}).items():
        api_keys[provider] = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    return {
        "api_keys": api_keys,
        "ollama_host": config.get("ollama", {}).get("host", "http://localhost:11434"),
    }

@app.post("/api/options/api-keys", dependencies=[Depends(get_current_user)])
async def set_api_key_endpoint(request: Request) -> dict:
    from sovereignai.shared.config_loader import set_api_key
    data = await request.json()
    provider = data.get("provider", "")
    key = data.get("key", "")
    if not provider or not key:
        raise HTTPException(status_code=400, detail="provider and key required")
    set_api_key(provider, key)
    return {"status": "saved"}

@app.delete("/api/options/api-keys/{provider}", dependencies=[Depends(get_current_user)])
async def delete_api_key_endpoint(provider: str) -> dict:
    from sovereignai.shared.config_loader import delete_api_key
    delete_api_key(provider)
    return {"status": "deleted"}
```

**File**: `web/templates/index.html`

```html
<section id="panel-options" class="panel">
    <h2>Options</h2>
    <div class="options-section">
        <h3>API Keys</h3>
        <div id="api-keys-list"></div>
        <div class="api-key-form">
            <input type="text" id="api-key-provider" placeholder="Provider (e.g., openai)">
            <input type="password" id="api-key-value" placeholder="API Key">
            <button onclick="saveApiKey()">Save</button>
        </div>
    </div>
    <div class="options-section">
        <h3>Ollama</h3>
        <p>Host: <span id="ollama-host-display">Loading...</span></p>
        <p>Ensure Ollama is running: <code>ollama serve</code></p>
    </div>
</section>
```

---

## S8 — Wire panel loaders + load model selector on startup

**File**: `web/static/app.js`

In `loadPanelContent`:
```javascript
function loadPanelContent(panelName) {
    switch(panelName) {
        case 'orchestrator': loadModelSelector(); break;
        case 'workers': loadWorkers(); break;
        case 'tasks': loadTasks(); break;
        case 'skills': loadSkills(); break;
        case 'memory': loadMemory(); break;
        case 'models': loadInstalledModels(); break;
        case 'adapters': loadAdapters(); break;
        case 'hardware': loadHardware(); break;
        case 'options': loadOptions(); break;
    }
}
```

Also call `loadModelSelector()` on page load (in the DOMContentLoaded handler).

---

## S9 — CSS

**File**: `web/static/styles.css`

```css
/* Models panel */
.models-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.models-tab { padding: 6px 16px; background: #2d2d2d; border: 1px solid #3d3d3d; color: #888; cursor: pointer; border-radius: 4px; }
.models-tab.active { background: #3d3d3d; color: #fff; }
.models-search { display: flex; gap: 8px; margin-bottom: 12px; }
.models-search input { flex: 1; padding: 6px; background: #2d2d2d; border: 1px solid #4d4d4d; color: #ddd; border-radius: 4px; }
.model-entry { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-bottom: 1px solid #333; }
.model-name { color: #ddd; font-weight: 500; }
.model-size { color: #888; font-size: 12px; }
.model-downloads { color: #666; font-size: 12px; }
.pull-btn { padding: 4px 12px; background: #3d3d3d; border: 1px solid #4d4d4d; color: #ccc; border-radius: 4px; cursor: pointer; font-size: 12px; }
.pull-btn:hover { background: #4d4d4d; }
.model-publisher-section { margin-bottom: 16px; }
.model-publisher-section h3 { color: #aaa; margin: 8px 0 4px; font-size: 14px; }

/* Orchestrator model selector */
.orchestrator-controls { margin-bottom: 12px; }
#model-selector { padding: 6px; background: #2d2d2d; border: 1px solid #4d4d4d; color: #ddd; border-radius: 4px; width: 100%; max-width: 300px; }

/* Memory panel */
.memory-backend-entry { padding: 12px; border: 1px solid #3d3d3d; margin-bottom: 8px; border-radius: 4px; }
.memory-backend-entry h3 { color: #ccc; margin: 0 0 4px; }
.memory-backend-entry p { color: #999; margin: 2px 0; font-size: 13px; }

/* Options panel */
.options-section { margin-bottom: 24px; }
.api-key-entry { display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #333; color: #ddd; }
.api-key-form { display: flex; gap: 8px; margin-top: 12px; }
.api-key-form input { padding: 6px; background: #2d2d2d; border: 1px solid #4d4d4d; color: #ddd; border-radius: 4px; }
```

---

## S10 — Tests

- `tests/test_hf_catalog.py`: Test fetch_gguf_models (mock urllib), test get_model_files (mock)
- `tests/test_config_loader.py`: Test load/save/delete, test dotted keys
- `tests/test_models_api.py`: Test /api/models/installed, /api/models/catalog, /api/models/pull
- `tests/test_memory_api.py`: Test /api/memory/backends
- `tests/test_options_api.py`: Test API key CRUD

---

## S11 — Verify all 9 panels

Start server, register, login, then:
1. Orchestrator: model selector dropdown shows installed models
2. Workers: shows registered components
3. Tasks: empty list (works)
4. Skills: shows capabilities
5. Memory: shows 4 backends with status
6. Models: [Installed] tab shows Ollama models, [HuggingFace] tab shows searchable GGUF catalog
7. Adapters: shows capabilities
8. Hardware: shows CPU/RAM
9. Options: shows API key form + Ollama host

---

## Files WILL Create
- `sovereignai/shared/config_loader.py`
- `sovereignai/shared/hf_catalog.py`
- `tests/test_hf_catalog.py`
- `tests/test_config_loader.py`
- `tests/test_models_api.py`
- `tests/test_memory_api.py`
- `tests/test_options_api.py`

## Files WILL Edit
- `web/main.py` (S3, S5, S6, S7 — API endpoints)
- `web/templates/index.html` (S4, S5, S6, S7 — panel UIs)
- `web/static/app.js` (S4, S5, S6, S7, S8 — panel loaders + model selector)
- `web/static/styles.css` (S9 — styles)
- `AGENTS.md` (S0.3 — OR91)

## Files WILL NOT Edit
- `sovereignai/main.py` (no new backend registration needed — Ollama already registered)
- `txt/requirements.txt`
- `project-vision-Rev5.md`

---

## Closing

Run `/close`. Tag: `prompt-17`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh.

After this plan:
- All 9 panels populate
- Models panel has [Installed] + [HuggingFace] tabs
- HuggingFace catalog is searchable via API (no scraping)
- Pull button downloads models via Ollama
- Orchestrator has a model selector dropdown
- Selecting a model + sending a message → chat via Ollama locally
- Memory panel shows 4 backends
- Options panel shows API key management
