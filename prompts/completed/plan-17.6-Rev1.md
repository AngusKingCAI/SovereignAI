# Plan 17.6 — Fix Model Pull 500 + Collapsible Family Sections + Load More + Provider Search

**Hotfix**: Fix pull dialog 500 error, add collapsible model families, load more pagination, and provider-specific search. Round Table vetoed.

Depends on: prompt-17.5

---

## S0 — Opening

**S0.1** — Run `/open`. Verify `prompt-17.5` tag on origin. Clean working copy on `main`.

**S0.2** — Read `AGENTS.md` in full. Read `close.md` in full (per OR71).

**S0.3** — No new rules. Proceed to S1.

---

## S1 — Fix 500 error on model catalog detail endpoint (pull dialog)

**File**: `web/main.py`

The endpoint accesses `f["path"]` but `get_model_files()` returns dicts with key `"filename"`, not `"path"`. This causes a `KeyError` → 500 Internal Server Error when clicking "Pull" on any model.

**Find** (in `get_model_detail`):
```python
    files = get_model_files(trace, model_id)
    # Enrich with quant labels
    for f in files:
        f["quant"] = extract_quant_from_filename(f["path"])
    return {"model_id": model_id, "files": files}
```

**Replace with**:
```python
    files = get_model_files(trace, model_id)
    # Enrich with quant labels
    for f in files:
        f["quant"] = extract_quant_from_filename(f["filename"])
    return {"model_id": model_id, "files": files}
```

**Change**: `f["path"]` → `f["filename"]` (matches the actual dict key returned by `get_model_files()`).

---

## S2 — Collapsible model families + load more pagination

**File**: `web/static/app.js`

Replace the entire `loadHFCatalog` function and add pagination state:

```javascript
let hfOffset = 0;
const HF_PAGE_SIZE = 50;

function loadHFCatalog(reset) {
    if (reset === undefined) reset = true;
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

            // Remove existing Load More button
            const existingBtn = document.getElementById('load-more-btn');
            if (existingBtn) existingBtn.remove();

            // Group by family
            const byFamily = {};
            models.forEach(m => {
                const fam = m.family || 'Other';
                if (!byFamily[fam]) byFamily[fam] = [];
                byFamily[fam].push(m);
            });

            // Sort families by total downloads
            const sortedFamilies = Object.entries(byFamily)
                .sort((a, b) => {
                    const aTotal = a[1].reduce((s, m) => s + (m.downloads || 0), 0);
                    const bTotal = b[1].reduce((s, m) => s + (m.downloads || 0), 0);
                    return bTotal - aTotal;
                });

            for (const [family, familyModels] of sortedFamilies) {
                // Find existing family section or create new
                let section = document.querySelector(`[data-family="${family}"]`);
                if (!section) {
                    section = document.createElement('div');
                    section.className = 'model-family-section collapsed';
                    section.setAttribute('data-family', family);
                    const totalDl = familyModels.reduce((s, m) => s + (m.downloads || 0), 0);
                    const dlStr = totalDl > 1000 ? `${(totalDl / 1000).toFixed(0)}K` : totalDl;
                    section.innerHTML = `<h3 onclick="this.parentElement.classList.toggle('collapsed')">${family} (${familyModels.length} models, ⬇${dlStr}) ▶</h3>`;
                    const modelList = document.createElement('div');
                    modelList.className = 'family-models';
                    section.appendChild(modelList);
                    list.appendChild(section);
                }

                const modelList = section.querySelector('.family-models');
                familyModels.forEach(m => {
                    const entry = document.createElement('div');
                    entry.className = 'model-entry catalog';
                    const dl = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : (m.downloads || 0);
                    entry.innerHTML = `
                        <span class="model-publisher">${m.publisher || ''}</span>
                        <span class="model-name">${m.name}</span>
                        <span class="model-downloads">⬇ ${dl}</span>
                        <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                    `;
                    modelList.appendChild(entry);
                });
            }

            // Add Load More button if full page returned
            if (models.length === HF_PAGE_SIZE) {
                hfOffset += HF_PAGE_SIZE;
                const btn = document.createElement('button');
                btn.id = 'load-more-btn';
                btn.className = 'load-more-btn';
                btn.textContent = 'Load More Models';
                btn.onclick = function() { loadHFCatalog(false); };
                list.appendChild(btn);
            }
        });
}
```

---

## S3 — Provider-specific search (search within a family when expanded)

When a user expands a family section, load ALL models from that provider (not just the first 50). Add a "Load all from this provider" button inside each family section.

**File**: `web/static/app.js`

Add after the `loadHFCatalog` function:

```javascript
function loadAllFromFamily(family) {
    // Search HuggingFace for the family name to get all models from that publisher/family
    const search terms = family.split(' / ').pop().toLowerCase(); // e.g., "Meta / Llama" -> "llama"
    const list = document.querySelector(`[data-family="${family}"] .family-models`);
    if (!list) return;

    // Show loading indicator
    const loading = document.createElement('p');
    loading.textContent = 'Loading all models...';
    loading.className = 'loading-text';
    list.appendChild(loading);

    // Fetch all models matching this family name (up to 200)
    fetch(`/api/models/catalog?search=${encodeURIComponent(searchTerms)}&limit=200`)
        .then(r => r.json())
        .then(models => {
            loading.remove();
            // Filter to only models matching this family
            const familyModels = models.filter(m => m.family === family);
            familyModels.forEach(m => {
                // Check if already in list
                const existing = list.querySelector(`[data-model-id="${m.id}"]`);
                if (existing) return;
                const entry = document.createElement('div');
                entry.className = 'model-entry catalog';
                entry.setAttribute('data-model-id', m.id);
                const dl = m.downloads > 1000 ? `${(m.downloads / 1000).toFixed(0)}K` : (m.downloads || 0);
                entry.innerHTML = `
                    <span class="model-publisher">${m.publisher || ''}</span>
                    <span class="model-name">${m.name}</span>
                    <span class="model-downloads">⬇ ${dl}</span>
                    <button class="pull-btn" onclick="showPullDialog('${m.id}')">Pull</button>
                `;
                list.appendChild(entry);
            });
        });
}
```

Update the family section header in `loadHFCatalog` to include a "Load all" button:

In the section creation code, change the `innerHTML` to:
```javascript
section.innerHTML = `<h3 onclick="this.parentElement.classList.toggle('collapsed')">${family} (${familyModels.length} models, ⬇${dlStr}) ▶</h3>`;
```

And add a load-all button after the model list in the section:
```javascript
const loadAllBtn = document.createElement('button');
loadAllBtn.className = 'load-all-btn';
loadAllBtn.textContent = `Load all ${family} models`;
loadAllBtn.onclick = function() { loadAllFromFamily(family); };
section.appendChild(loadAllBtn);
```

---

## S4 — CSS for collapsible families

**File**: `web/static/styles.css`

```css
.model-family-section {
    margin-bottom: 8px;
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
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.model-family-section h3:hover {
    background: #333;
}
.model-family-section.collapsed .family-models,
.model-family-section.collapsed .load-all-btn {
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
.model-publisher { color: #888; font-size: 12px; }
.model-name { color: #ddd; font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.model-downloads { color: #666; font-size: 12px; text-align: right; }
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
.load-more-btn:hover { background: #4d4d4d; }
.load-all-btn {
    display: block;
    margin: 8px auto;
    padding: 4px 16px;
    background: transparent;
    border: 1px solid #4d4d4d;
    color: #888;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}
.load-all-btn:hover { background: #333; color: #ccc; }
.loading-text { color: #666; font-size: 12px; padding: 8px; text-align: center; }
```

---

## S5 — Fix password field not in form (DOM warning)

**File**: `web/templates/index.html`

The API key input in the Options panel is a password field not wrapped in a `<form>`. Wrap it:

**Find**:
```html
<div class="api-key-form">
    <input type="text" id="api-key-provider" placeholder="Provider (e.g., openai)">
    <input type="password" id="api-key-value" placeholder="API Key">
    <button onclick="saveApiKey()">Save</button>
</div>
```

**Replace with**:
```html
<form class="api-key-form" onsubmit="saveApiKey(); return false;">
    <input type="text" id="api-key-provider" placeholder="Provider (e.g., openai)" autocomplete="off">
    <input type="password" id="api-key-value" placeholder="API Key" autocomplete="new-password">
    <button type="submit">Save</button>
</form>
```

---

## S6 — Add offset parameter to catalog API endpoint

**File**: `web/main.py`

The catalog endpoint needs to accept `offset` for pagination:

**Find**:
```python
async def get_model_catalog(
    request: Request,
    search: str = "",
    limit: int = 50,
) -> list[dict]:
```

**Replace with**:
```python
async def get_model_catalog(
    request: Request,
    search: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
```

And pass `offset` to `fetch_gguf_models`:

**Find**:
```python
    return fetch_gguf_models(trace, search=search, limit=limit)
```

**Replace with**:
```python
    return fetch_gguf_models(trace, search=search, limit=limit, offset=offset)
```

**File**: `sovereignai/shared/hf_catalog.py`

**Find** `fetch_gguf_models` signature:
```python
def fetch_gguf_models(trace: TraceEmitter, search: str = "", limit: int = 50) -> list[dict]:
```

**Replace with**:
```python
def fetch_gguf_models(trace: TraceEmitter, search: str = "", limit: int = 50, offset: int = 0) -> list[dict]:
```

And add `offset` to the API params:
```python
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
```

---

## S7 — Run /close (ALL 22 steps per OR96)

Run the full `/close` workflow. Do NOT skip any steps. Do NOT commit with known failures. Do NOT tag until all steps pass.

---

## Files WILL Edit
- `web/main.py` (S1 — fix key mismatch, S6 — offset param)
- `web/static/app.js` (S2 — collapsible families + pagination, S3 — provider search)
- `web/static/styles.css` (S4 — CSS)
- `web/templates/index.html` (S5 — form wrapper)
- `sovereignai/shared/hf_catalog.py` (S6 — offset param)

## Files WILL NOT Edit
- `sovereignai/main.py`
- `sovereignai/shared/auth.py`

---

## Closing

Run `/close`. Tag: `prompt-17.6`. Per OR83, use `git add -A`. Per OR71, re-read `close.md` fresh. Per OR96, complete ALL 22 steps.
