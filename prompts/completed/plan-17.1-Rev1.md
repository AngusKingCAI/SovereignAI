Depends on: prompt-17
Vision principles: P1 (modular core), P9 (UI is separate process), P11 (no hidden complexity)
Open questions resolved: none

## S0 — Opening

- **S0.1**: Run `/open` per `.devin/workflows/open.md`
- **S0.2**: Read `AGENTS.md` in full
- **S0.3**: No new rules for this hotfix

## Plan Body

### S1 — Fix model pull to use `hf.co/` prefix

**File:** `web/main.py`

The `pull_model` endpoint currently passes the raw HuggingFace model ID (e.g., `unsloth/Llama-3.2-3B-Instruct-GGUF`) directly to `ollama.pull()`. This fails because Ollama requires the `hf.co/` prefix for HuggingFace models.

**Current (broken):**
```python
ollama.pull(model_name)  # "unsloth/Llama-3.2-3B-Instruct-GGUF"
```

**Fix:** Prefix with `hf.co/` when the model ID contains a `/` (indicating it's a HF namespace/repo format):

```python
# In pull_model(), before calling ollama.pull():
if "/" in model_name and not model_name.startswith("hf.co/"):
    ollama_name = f"hf.co/{model_name}"
else:
    ollama_name = model_name

ollama.pull(ollama_name)
```

Also add optional `quant` parameter support:
```python
quant = data.get("quant", "")  # e.g., "Q4_K_M"
if quant:
    ollama_name = f"{ollama_name}:{quant}"
```

### S2 — Add quant selection to catalog detail endpoint

**File:** `web/main.py` — `get_model_detail()`

Currently returns raw file list. Add `quant` field to each file so the UI can offer a dropdown:

```python
files = get_model_files(trace, model_id)
# Enrich with quant labels
for f in files:
    f["quant"] = extract_quant_from_filename(f["path"])  # e.g., "Q4_K_M"
```

### S3 — Fix Models panel UI layout

**File:** `web/static/app.js`

Current issues:
- Flat list instead of tabs
- No quant selection on Pull
- No progress indication

**Fix the `loadHFCatalog()` function:**

```javascript
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
                const pub = m.id.split('/')[0];
                if (!byPublisher[pub]) byPublisher[pub] = [];
                byPublisher[pub].push(m);
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
                        <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                    `;
                    section.appendChild(entry);
                });
                list.appendChild(section);
            }
        });
}

function showPullDialog(modelId) {
    // Fetch available quants first
    fetch(`/api/models/catalog/${encodeURIComponent(modelId)}`)
        .then(r => r.json())
        .then(data => {
            const files = data.files || [];
            const quants = files.map(f => f.quant).filter(Boolean);
            const defaultQuant = quants.includes('Q4_K_M') ? 'Q4_K_M' : quants[0] || '';

            const quantSelect = quants.length > 0 
                ? `<select id="pull-quant">${quants.map(q => `<option value="${q}" ${q===defaultQuant?'selected':''}>${q}</option>`).join('')}</select>`
                : '<input type="text" id="pull-quant" placeholder="quant (e.g., Q4_K_M)" />';

            const dialog = document.createElement('div');
            dialog.className = 'pull-dialog';
            dialog.innerHTML = `
                <h3>Pull ${modelId}</h3>
                <label>Quantization: ${quantSelect}</label>
                <button onclick="confirmPull('${modelId}')">Pull</button>
                <button onclick="this.closest('.pull-dialog').remove()">Cancel</button>
            `;
            document.body.appendChild(dialog);
        });
}

function confirmPull(modelId) {
    const quant = document.getElementById('pull-quant').value;
    fetch('/api/models/pull', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({model: modelId, quant: quant}),
        credentials: 'same-origin',
    })
    .then(r => r.json())
    .then(result => {
        alert(`Pulling ${modelId}:${quant}... Check the log drawer for progress.`);
        document.querySelector('.pull-dialog').remove();
    });
}
```

### S4 — Add CSS for tabbed layout

**File:** `web/static/styles.css`

Add tab styles:

```css
.model-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
    border-bottom: 1px solid #3d3d3d;
}

.model-tab {
    padding: 10px 20px;
    background: #2d2d2d;
    border: none;
    color: #e0e0e0;
    cursor: pointer;
    border-bottom: 2px solid transparent;
}

.model-tab.active {
    border-bottom-color: #4a9eff;
    background: #3d3d3d;
}

.tab-content {
    display: none;
}

.tab-content.active {
    display: block;
}

.pull-dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: #2d2d2d;
    border: 1px solid #3d3d3d;
    padding: 20px;
    border-radius: 8px;
    z-index: 2000;
}
```

### S5 — Update HTML template for tabbed models panel

**File:** `web/templates/index.html` (or wherever the models panel HTML is)

Ensure the models panel has:

```html
<div id="panel-models" class="panel">
    <h2>Models</h2>
    <div class="model-tabs">
        <button class="model-tab active" data-tab="installed" onclick="switchModelsTab('installed')">Installed</button>
        <button class="model-tab" data-tab="huggingface" onclick="switchModelsTab('huggingface')">HuggingFace</button>
    </div>
    <div id="tab-installed" class="tab-content active">
        <div id="installed-models-list"></div>
    </div>
    <div id="tab-huggingface" class="tab-content">
        <input type="text" id="hf-search" placeholder="Search models..." onkeyup="if(event.key==='Enter')loadHFCatalog()"/>
        <button onclick="loadHFCatalog()">Search</button>
        <div id="hf-models-list"></div>
    </div>
</div>
```

### S6 — Add `switchModelsTab` function

**File:** `web/static/app.js`

```javascript
function switchModelsTab(tab) {
    document.querySelectorAll('.model-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
    if (tab === 'installed') loadInstalledModels();
    if (tab === 'huggingface') loadHFCatalog();
}
```

### S7 — Verify and test

1. Start server: `.venv/Scripts/python.exe -m uvicorn web.main:app --host 127.0.0.1 --port 8765`
2. Open Models panel → HuggingFace tab
3. Search "llama" → click Pull on a model
4. Select quant (e.g., Q4_K_M) → confirm
5. Check log drawer for `ollama pull hf.co/...` progress
6. Switch to Installed tab → verify model appears after pull completes

## Closing

Run `/close` per `.devin/workflows/close.md`

## STOP Conditions

- If `ollama.pull()` still fails after `hf.co/` prefix, check Ollama version (needs 0.1.24+ for HF support)
- If HF API returns empty list, verify network connectivity to `huggingface.co`

## Files WILL Create/Edit/NOT Edit

| File | Action | Reason |
|---|---|---|
| `web/main.py` | Edit | Fix pull endpoint to prefix `hf.co/` |
| `web/static/app.js` | Edit | Add tab switching, quant selection dialog |
| `web/static/styles.css` | Edit | Add tab and dialog styles |
| `web/templates/index.html` | Edit | Add tabbed layout structure |
| `sovereignai/shared/hf_catalog.py` | NOT edit | Already working — returns correct model IDs |
| `adapters/external/ollama_adapter/` | NOT edit | Unrelated to UI pull flow |
