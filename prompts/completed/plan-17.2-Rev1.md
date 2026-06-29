# Plan 17.2 — Fix Model Pull + Organize HF Catalog by Family

**Hotfix**: Fix pull buttons + organize 45K models into browsable family groups. Round Table vetoed.

Depends on: prompt-17.1

---

## S1 — Fix pull buttons

**Problem**: `ollama pull hf.co/{model}:{quant}` fails silently. The `confirmPull` function alerts "Pulling..." regardless of success/failure. No error feedback to the user.

### S1.1 — Fix pull endpoint to return errors properly

**File**: `web/main.py`

The `_pull()` function runs in a background thread. The HTTP response returns immediately with `{"status": "pulling"}`. The user never sees if it failed.

**Fix**: Store pull status in a dict that the frontend can poll:

```python
# Add at module level
_pull_status: dict[str, dict] = {}  # model_id -> {status, message, progress}

@app.post("/api/models/pull", dependencies=[Depends(get_current_user)])
async def pull_model(request: Request) -> dict:
    """Pull a model. Returns immediately; poll /api/models/pull-status for progress."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    data = await request.json()
    model_name = data.get("model", "")
    quant = data.get("quant", "Q4_K_M")
    if not model_name:
        raise HTTPException(status_code=400, detail="model is required")

    # Build ollama pull name
    if "/" in model_name and not model_name.startswith("hf.co/"):
        ollama_name = f"hf.co/{model_name}:{quant}"
    else:
        ollama_name = model_name

    # Initialize status
    _pull_status[model_name] = {"status": "pulling", "message": f"Pulling {ollama_name}...", "progress": 0}

    def _pull() -> None:
        import subprocess
        try:
            trace.emit(component="models", level=TraceLevel.INFO, message=f"Pulling: {ollama_name}")
            result = subprocess.run(
                ["ollama", "pull", ollama_name],
                capture_output=True, text=True, timeout=3600,
            )
            if result.returncode == 0:
                _pull_status[model_name] = {"status": "done", "message": f"Pulled {ollama_name} successfully", "progress": 100}
                trace.emit(component="models", level=TraceLevel.INFO, message=f"Pull success: {ollama_name}")
            else:
                err = result.stderr.strip()[:200] if result.stderr else "Unknown error"
                _pull_status[model_name] = {"status": "error", "message": f"Pull failed: {err}", "progress": 0}
                trace.emit(component="models", level=TraceLevel.ERROR, message=f"Pull failed: {err}")
        except Exception as exc:
            _pull_status[model_name] = {"status": "error", "message": f"Pull error: {exc}", "progress": 0}
            trace.emit(component="models", level=TraceLevel.ERROR, message=f"Pull error: {exc}")

    import threading
    thread = threading.Thread(target=_pull, daemon=True)
    thread.start()
    return {"status": "pulling", "model": model_name}

@app.get("/api/models/pull-status", dependencies=[Depends(get_current_user)])
async def get_pull_status(request: Request) -> dict:
    """Get status of all active/recent model pulls."""
    return _pull_status

@app.get("/api/models/pull-status/{model_id:path}", dependencies=[Depends(get_current_user)])
async def get_pull_status_for_model(model_id: str) -> dict:
    """Get status of a specific model pull."""
    return _pull_status.get(model_id, {"status": "unknown", "message": "No pull in progress"})
```

### S1.2 — Fix frontend to show pull status

**File**: `web/static/app.js`

Replace `confirmPull` with:

```javascript
function confirmPull(modelId) {
    const quant = document.getElementById('pull-quant').value;
    const btn = document.querySelector('.pull-dialog button');
    btn.textContent = 'Starting pull...';
    btn.disabled = true;

    fetch('/api/models/pull', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: modelId, quant: quant}),
        credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(result => {
        document.querySelector('.pull-dialog').remove();
        // Open log drawer so user sees progress
        document.getElementById('log-drawer').classList.add('open');
        // Poll for status
        pollPullStatus(modelId);
    })
    .catch(err => {
        alert('Failed to start pull: ' + err);
        document.querySelector('.pull-dialog').remove();
    });
}

function pollPullStatus(modelId) {
    const interval = setInterval(() => {
        fetch(`/api/models/pull-status/${encodeURIComponent(modelId)}`)
            .then(r => r.json())
            .then(status => {
                if (status.status === 'done') {
                    clearInterval(interval);
                    alert(`Model ${modelId} pulled successfully!`);
                    // Refresh installed models
                    loadInstalledModels();
                    loadModelSelector();
                } else if (status.status === 'error') {
                    clearInterval(interval);
                    alert(`Pull failed: ${status.message}`);
                }
                // Status updates are in the log drawer via traces
            })
            .catch(() => {});
    }, 5000); // Poll every 5 seconds
}
```

---

## S2 — Organize HF catalog by model family (not HF username)

**Problem**: 45K GGUF models listed by HF username (bartowski, unsloth, etc.) is not browsable. The spec calls for: Provider → Publisher/Family (Meta/Llama, Google/Gemma, etc.) → Model → Version/Tag.

### S2.1 — Add family detection to HF catalog

**File**: `sovereignai/shared/hf_catalog.py`

Add a function that maps model IDs to families:

```python
# Model family detection — maps keywords in model ID to a family name
FAMILY_PATTERNS = [
    ("llama", "Meta / Llama"),
    ("Llama", "Meta / Llama"),
    ("gemma", "Google / Gemma"),
    ("Gemma", "Google / Gemma"),
    ("qwen", "Alibaba / Qwen"),
    ("Qwen", "Alibaba / Qwen"),
    ("deepseek", "DeepSeek"),
    ("DeepSeek", "DeepSeek"),
    ("mistral", "Mistral"),
    ("Mistral", "Mistral"),
    ("mixtral", "Mistral"),
    ("phi", "Microsoft / Phi"),
    ("Phi", "Microsoft / Phi"),
    ("yi", "01.AI / Yi"),
    ("Yi", "01.AI / Yi"),
    ("codellama", "Meta / CodeLlama"),
    ("CodeLlama", "Meta / CodeLlama"),
    ("starcoder", "BigCode / StarCoder"),
    ("dolphin", "Cognitive Computations / Dolphin"),
    ("nous", "NousResearch / Nous"),
    ("hermes", "NousResearch / Hermes"),
    ("orca", "Microsoft / Orca"),
    ("vicuna", "LMSYS / Vicuna"),
    ("wizard", "Eric Hartford / Wizard"),
    ("zephyr", "HuggingFace / Zephyr"),
    ("solar", "Upstage / Solar"),
    ("command-r", "Cohere / Command-R"),
    ("gemma", "Google / Gemma"),
    ("bert", "Google / BERT"),
    ("nomic", "Nomic / Embed"),
    ("bge", "BAAI / BGE"),
    ("e5", "Intel / E5"),
    ("mxbai", "MixedBread / mxbai"),
]

def detect_family(model_id: str) -> str:
    """Detect model family from model ID (e.g., 'unsloth/Llama-3.2-3B-Instruct-GGUF' -> 'Meta / Llama')."""
    model_lower = model_id.lower()
    for pattern, family in FAMILY_PATTERNS:
        if pattern.lower() in model_lower:
            return family
    # Use the HF publisher as fallback
    publisher = model_id.split("/")[0] if "/" in model_id else "Other"
    return f"Other / {publisher}"
```

### S2.2 — Update fetch_gguf_models to include family

In `fetch_gguf_models()`, add `family` to each model dict:

```python
        models.append({
            "id": model_id,
            "publisher": publisher,
            "family": detect_family(model_id),  # NEW
            "name": model_id.split("/")[-1] if "/" in model_id else model_id,
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "tags": m.get("tags", []),
            "pipeline_tag": m.get("pipeline_tag", ""),
        })
```

### S2.3 — Update frontend to group by family (not publisher)

**File**: `web/static/app.js`

In `loadHFCatalog()`, group by `family` instead of publisher:

```javascript
            // Group by family (Meta / Llama, Google / Gemma, etc.)
            const byFamily = {};
            models.forEach(m => {
                const fam = m.family || 'Other';
                if (!byFamily[fam]) byFamily[fam] = [];
                byFamily[fam].push(m);
            });

            // Sort families by total downloads (most popular first)
            const sortedFamilies = Object.entries(byFamily)
                .sort((a, b) => {
                    const aTotal = a[1].reduce((s, m) => s + m.downloads, 0);
                    const bTotal = b[1].reduce((s, m) => s + m.downloads, 0);
                    return bTotal - aTotal;
                });

            for (const [family, familyModels] of sortedFamilies) {
                const section = document.createElement('div');
                section.className = 'model-family-section';
                const totalDownloads = familyModels.reduce((s, m) => s + m.downloads, 0);
                section.innerHTML = `<h3 onclick="this.parentElement.classList.toggle('collapsed')">${family} (${familyModels.length} models, ⬇${(totalDownloads/1000).toFixed(0)}K)</h3>`;
                const modelList = document.createElement('div');
                modelList.className = 'family-models';
                familyModels.forEach(m => {
                    const entry = document.createElement('div');
                    entry.className = 'model-entry catalog';
                    const downloads = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : m.downloads;
                    entry.innerHTML = `
                        <span class="model-publisher">${m.publisher}</span>
                        <span class="model-name">${m.name}</span>
                        <span class="model-downloads">⬇ ${downloads}</span>
                        <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                    `;
                    modelList.appendChild(entry);
                });
                section.appendChild(modelList);
                list.appendChild(section);
            }
```

### S2.4 — Add pagination

Add `offset` parameter support (from Plan 17.1 Rev1 S3) + "Load More" button:

```javascript
let hfOffset = 0;
const HF_PAGE_SIZE = 50;

function loadHFCatalog(reset = true) {
    if (reset) {
        hfOffset = 0;
        document.getElementById('hf-models-list').innerHTML = '';
    }
    const search = document.getElementById('hf-search').value;
    let url = `/api/models/catalog?limit=${HF_PAGE_SIZE}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (hfOffset > 0) url += `&offset=${hfOffset}`;

    fetch(url)
        .then(r => r.json())
        .then(models => {
            const list = document.getElementById('hf-models-list');
            if (reset && models.length === 0) {
                list.innerHTML = '<p>No models found. Try a different search.</p>';
                return;
            }

            // Remove existing Load More
            const existingBtn = document.getElementById('load-more-btn');
            if (existingBtn) existingBtn.remove();

            // Group by family (code from S2.3 above)
            // ... (same grouping logic)

            // Add Load More if full page returned
            if (models.length === HF_PAGE_SIZE) {
                hfOffset += HF_PAGE_SIZE;
                const btn = document.createElement('button');
                btn.id = 'load-more-btn';
                btn.className = 'load-more-btn';
                btn.textContent = 'Load More Models';
                btn.onclick = () => loadHFCatalog(false);
                list.appendChild(btn);
            }
        });
}
```

Also update `web/main.py` catalog endpoint to accept `offset`:

```python
async def get_model_catalog(
    request: Request,
    search: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Browse available GGUF models from HuggingFace."""
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    from sovereignai.shared.hf_catalog import fetch_gguf_models
    return fetch_gguf_models(trace, search=search, limit=limit, offset=offset)
```

And `hf_catalog.py`:

```python
def fetch_gguf_models(trace: TraceEmitter, search: str = "", limit: int = 50, offset: int = 0) -> list[dict]:
    params = {
        "filter": "gguf",
        "sort": "downloads",
        "direction": "-1",
        "limit": str(limit),
    }
    if search:
        params["search"] = search
    if offset:
        params["offset"] = str(offset)
    # ... rest unchanged
```

---

## S3 — CSS for family sections (collapsible)

**File**: `web/static/styles.css`

```css
.model-family-section {
    margin-bottom: 12px;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    overflow: hidden;
}
.model-family-section h3 {
    padding: 10px 12px;
    background: #2d2d2d;
    color: #ccc;
    cursor: pointer;
    margin: 0;
    font-size: 14px;
    user-select: none;
}
.model-family-section h3:hover {
    background: #333;
}
.model-family-section.collapsed .family-models {
    display: none;
}
.family-models {
    padding: 4px 0;
}
.model-entry.catalog {
    display: grid;
    grid-template-columns: 120px 1fr 80px 60px;
    gap: 8px;
    padding: 6px 12px;
    border-bottom: 1px solid #2a2a2a;
    align-items: center;
}
.model-publisher {
    color: #888;
    font-size: 12px;
}
.model-name {
    color: #ddd;
    font-size: 13px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.model-downloads {
    color: #666;
    font-size: 12px;
    text-align: right;
}
.load-more-btn {
    display: block;
    margin: 16px auto;
    padding: 8px 24px;
    background: #3d3d3d;
    border: 1px solid #4d4d4d;
    color: #ccc;
    border-radius: 4px;
    cursor: pointer;
}
.load-more-btn:hover {
    background: #4d4d4d;
}
```

---

## S4 — Verify

1. Start server, login
2. Models → [HuggingFace] tab → models grouped by family (Meta / Llama, Google / Gemma, etc.)
3. Families are collapsible (click to expand/collapse)
4. Families sorted by total downloads (most popular first)
5. "Load More" button at bottom loads 50 more
6. Search "qwen" → shows only Qwen models
7. Click "Pull" on a model → quant dialog → confirm → log drawer shows progress → alert on success/failure
8. Check [Installed] tab → newly pulled model appears
9. Orchestrator model selector → shows new model

---

## Files WILL Edit
- `web/main.py` (S1.1 — pull status endpoint + offset param)
- `web/static/app.js` (S1.2 — poll pull status, S2.3 — family grouping + pagination)
- `sovereignai/shared/hf_catalog.py` (S2.1 — family detection, S2.2 — add family field, offset param)
- `web/static/styles.css` (S3 — family section CSS)

## Files WILL NOT Edit
- `sovereignai/main.py`
- `sovereignai/shared/auth.py`
- `txt/requirements.txt`

---

## Closing

Run `/close`. Tag: `prompt-17.2`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh.
