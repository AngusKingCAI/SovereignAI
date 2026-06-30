# SovereignAI — Plan 18.1: prompt-18.1 — Logs Pivot + Ollama Diagnostics + HF Model DB + VRAM/Tok-s

## Context

Plan 18 (`prompt-18.0`) shipped and is closed. Testing surfaced new issues that pivot direction on three fronts:

1. **Logs panel** — the floating bottom drawer has no close button, no drag-resize, and obscures the Load More Models button. Instead of patching the drawer, move Logs to a 10th sidebar panel (structural fix, kills 3 bugs at once).
2. **Ollama** — won't start via the Start button. Log is not verbose enough to diagnose. Need TRACE-level Ollama subprocess logging + the Ollama update from Plan 18 (carried forward since 18 didn't actually update it).
3. **Models** — HuggingFace catalog is populated live per page-view, which is slow and gives no room for computed fields. Pivot to a standalone SQLite DB (per the locked `models-panel-design-reference.md` decision) with a background sync task. Compute VRAM badges + tokens-per-second estimates at insert time using the memory-bandwidth formula.

Auth persistence is confirmed working (`[AuthMiddleware] Loaded 2 user(s) from settings\auth.json` + successful login). No work needed there.

Tokens-per-second formula (researched and validated):
```
tok/s ≈ memory_bandwidth ÷ active_bytes_per_token
Realistic = ceiling × 0.65  (50–80% range, midpoint 65%)
```
- Dense models: `active_bytes = full GGUF file size`
- MoE models: `active_bytes = active_params × bytes_per_param` (needs per-model config)

GPU bandwidth table baked into DB detection layer:
- RTX 4090: 1008 GB/s · RTX 3090: 936 GB/s · RTX 5090: 1792 GB/s
- A100 80GB: 2039 GB/s · H100 80GB: 3350 GB/s
- Apple M3 Max: 400 GB/s · M4 Max: 546 GB/s
- DDR5 RAM (CPU fallback): 80 GB/s

## Plan Body

### Phase 1 — Logs Panel as 10th Sidebar Item

**1.1 Remove floating log drawer**
- File: `web/templates/index.html`, `web/static/app.js`, `web/static/style.css`
- Delete the bottom-drawer DOM, the toggle JS, the overlay CSS
- Delete localStorage keys for drawer height/open state (cleanup)

**1.2 Add "Logs" as 10th sidebar entry**
- Position: between Hardware and Options
- Icon: list/terminal icon
- Clicking loads the Logs panel into the main content area like the other 9 panels
- Panel takes full main content height — scrollable, filterable, no overlay

**1.3 Logs panel content**
- Top bar: search box ("Search traces..."), level filter chips (ERROR/WARN/INFO/DEBUG/TRACE), source filter dropdown (AuthMiddleware/conformance/main/models/SSE/etc.), Clear button
- Main area: scrollable trace list, auto-scroll-to-bottom toggle, line wrap toggle
- Each line: timestamp · level · source · message (current format preserved)
- Status strip at bottom of window: 1-line latest trace + click-to-jump-to-Logs (optional, lightweight)
- Persist filter state + scroll position in localStorage

### Phase 2 — Verbose Logging + Ollama Subprocess TRACE

**2.1 Default log level → DEBUG**
- File: `sovereignai/.../logging_or_event_bus.py` (wherever level is configured)
- Change default from INFO to DEBUG
- TRACE level reserved for Ollama subprocess specifically (see 2.2)
- Verify all existing INFO/WARN/ERROR traces still emit at DEBUG

**2.2 Ollama subprocess TRACE logging**
- File: wherever the Ollama Start button spawns `ollama serve`
- Log every step at TRACE level:
  - Exact command + args + working dir + env vars
  - PID on spawn
  - Each poll of `/api/tags` (attempt N/10, response code, body)
  - stdout/stderr lines from the subprocess (stream reader thread)
  - Exit code on termination
- All TRACE logs tagged with source `[ollama_subprocess]` so they filter cleanly in the Logs panel

**2.3 Capture full download-pipeline error**
- File: `sovereignai/.../models_or_hf_catalog.py`
- The 17.6 log truncated `ollama create failed: time=2026-06-30T14:33:41.076+08:00 lev...`
- Ensure no log line is truncated — increase max line length or chunk multi-line errors
- Capture stderr from `ollama create` separately and log at ERROR level with full content

### Phase 3 — Ollama Update + Status Panel + Start Button + Download Pipeline Fix

**3.1 Update Ollama on the test machine to latest stable**
- Stop any running `ollama serve` processes
- Update via `winget upgrade Ollama.Ollama` (or download installer from ollama.com if winget unavailable)
- Verify: `ollama --version` shows latest stable (capture version in close report)
- Start `ollama serve` and confirm `GET http://localhost:11434/api/tags` returns 200

**3.2 Ollama status panel — live status + Start button**
- File: `web/templates/index.html`, `web/static/app.js`, `web/main.py`
- Replace static "Host: http://localhost:11434 / Ensure Ollama is running" with:
  - Green dot + "Running (vX.Y.Z)" when `GET /api/tags` returns 200 (version from `GET /api/version`)
  - Red dot + "Not running" when connection refused
  - Button: "Start ollama serve" — visible only when status is down. Clicking POSTs to new endpoint `POST /api/ollama/start` which spawns `ollama serve` as a Windows subprocess (DETACHED_PROCESS or equivalent — verify what works), polls `/api/tags` up to 10s, refreshes status on success, shows full TRACE log on failure (visible in new Logs panel)
- Status auto-refreshes every 10s via setInterval

**3.3 Re-test download pipeline on latest Ollama**
- Re-run: `hf.co/lmstudio-community/gemma-4-E4B-it-GGUF:Q4_K_M`
- If `ollama create` succeeds on latest → close out, no code change needed
- If it still fails → use the full error from 2.3 to diagnose. Common causes: wrong GGUF path, Modelfile syntax wrong, quant tag mismatch. If `ollama create` is wrong API, switch to `ollama pull hf.co/<repo>:<quant>` directly (newer Ollama supports natively).

**3.4 Download destination surfaced in UI**
- During download: "Downloading to: C:\Users\...\downloads\<file>.gguf"
- After success: "Stored at: C:\Users\<you>\.ollama\models\..." 
- Add Settings → Storage section showing both paths with "Reveal in Explorer" button (Windows: `explorer /select,<path>`)

### Phase 4 — HuggingFace Model Database

**4.1 SQLite schema (standalone DB per locked spec)**
- File: `sovereignai/.../models_db.py` (new), DB file at `settings/models.db`
- Schema:
  ```sql
  CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id TEXT NOT NULL,              -- e.g. "lmstudio-community/gemma-4-E4B-it-GGUF"
    model_family TEXT,                  -- e.g. "gemma" (parsed from repo_id or config)
    architecture TEXT,                  -- "dense" | "moe" (from config.json)
    base_parameter_count INTEGER,       -- e.g. 4000000000 for 4B
    quantization TEXT,                  -- e.g. "Q4_K_M"
    filename TEXT NOT NULL,             -- e.g. "gemma-4-E4B-it-Q4_K_M.gguf"
    file_size_bytes INTEGER NOT NULL,
    file_size_gb REAL NOT NULL,
    context_length INTEGER,             -- from config.json
    license TEXT,
    downloads INTEGER,
    likes INTEGER,
    last_modified TEXT,                 -- ISO datetime from HF API
    tags TEXT,                          -- JSON array
    -- Computed at insert time (hardware-independent):
    vram_required_gb REAL,              -- file_size_gb × 1.2 (KV cache headroom)
    active_bytes_gb REAL,               -- for dense: file_size_gb; for MoE: active_params × bytes_per_param
    -- Note: NO per-GPU tok/s columns. Tok/s is computed at query time
    -- from active_bytes_gb × detected GPU bandwidth, so it always reflects
    -- the actual hardware present (Plan 19 upgrades the detector; tok/s
    -- recalculates automatically with no DB migration).
    sync_timestamp TEXT NOT NULL,       -- when this row was inserted/updated
    UNIQUE(repo_id, quantization)
  );
  CREATE INDEX idx_models_family ON models(model_family);
  CREATE INDEX idx_models_size ON models(file_size_gb);
  ```

**4.2 Background sync task — runs as an external CLI program**
- File: `sovereignai/providers/huggingface/cli.py` (new, see Phase 6 for full CLI design)
- The Options UI shells out to this CLI; Devin can run it standalone in terminal for testing
- On first run (`download` command): populate DB from HuggingFace API (filter `library=gguf` or files ending `.gguf`)
- Pagination: HF API returns ~30 per page, fetch all pages with backoff
- Per model: fetch config.json for architecture/params/context, parse GGUF filename for quant tag
- Store raw fields only — `vram_required_gb` and `active_bytes_gb` computed at insert; tok/s NEVER stored (computed at view time from detected hardware)
- On subsequent runs (`update` command): incremental update (compare `last_modified` from HF, update changed rows only)
- Schedule: daily refresh via background thread (or APScheduler if already a dep)
- User can trigger manual refresh via UI button ("Update" under [Hugging Face] in Options)
- All sync activity logged to trace bus with source `[huggingface_cli]`

**4.3 Models panel reads from DB, computes tok/s at query time**
- File: `web/main.py`, `web/static/app.js`
- `GET /api/models/catalog?page=N&search=Q&family=F` reads from SQLite with pagination (50/page)
- For each model row, the endpoint computes tok/s using detected hardware:
  ```python
  detected_gpus = hardware_detector.list_gpus()  # Plan 19 will upgrade this; 18.1 uses whatever exists
  for model in rows:
      model.toks_per_sec = []
      for gpu in detected_gpus:
          bandwidth_gb_s = gpu.bandwidth_gb_s  # from GPU's bandwidth table
          toks = bandwidth_gb_s / model.active_bytes_gb * 0.65
          model.toks_per_sec.append({
              "gpu_name": gpu.name,
              "gpu_type": gpu.type,  # "integrated" | "discrete"
              "toks_per_sec": round(toks, 1),
              "fits": model.vram_required_gb <= gpu.vram_gb
          })
      # CPU fallback
      cpu_toks = 80 / model.active_bytes_gb * 0.65  # DDR5 ~80 GB/s
      model.toks_per_sec.append({
          "gpu_name": "CPU (DDR5)",
          "gpu_type": "cpu",
          "toks_per_sec": round(cpu_toks, 1),
          "fits": True  # CPU always "fits" via system RAM
      })
  ```
- Response includes computed `toks_per_sec` array per model
- Family grouping: collapse by default, expand on click, "Load all from provider" button when expanded
- Search box filters by repo_id/family/quantization

**4.4 Load More button (now trivial)**
- Since catalog is DB-backed, Load More just fetches next page from `/api/models/catalog?page=N+1`
- Button appears at bottom of list when more pages exist
- Clicking appends to list, persists current page in localStorage

### Phase 5 — VRAM Badges + Tok/s Display

**5.1 VRAM badge computation**
- File: `web/main.py` (or `sovereignai/.../vram_badge.py`)
- For each model in catalog response, compute badge using:
  - `vram_required_gb` (from DB)
  - Detected VRAM (from hardware panel — for Plan 18.1 use whatever's currently detected; Plan 19 will upgrade this)
  - Detected system RAM
- Badge rules (per `models-panel-design-reference.md`):
  - **VRAM** (green): `vram_required_gb ≤ detected_vram_gb`
  - **VRAM+RAM** (amber): `vram_required_gb > detected_vram_gb` AND `vram_required_gb ≤ detected_vram_gb + detected_ram_gb`
  - **Diskspace** (red): `vram_required_gb > detected_vram_gb + detected_ram_gb`
  - **N/A** (gray): VRAM not detected (no GPU or detection failed)

**5.2 Tok/s display in catalog — based on detected hardware only**
- File: `web/static/app.js`, `web/templates/index.html`
- For each model row, show estimated tok/s for **each detected GPU** on this machine, plus CPU fallback
- Format: 
  - If 1 GPU detected: "~130 tok/s (RTX 4060)"
  - If 2 GPUs detected (e.g. IGPU + DGPU): "~130 tok/s (RTX 4060) · ~22 tok/s (Intel Arc IGPU) · ~5 tok/s (CPU)"
  - If no GPU detected: "~5 tok/s (CPU)"
- Each tok/s value color-coded: green if `fits=True` (model fits in that GPU's VRAM), amber if `fits=False` (would need CPU offload — actual tok/s would be much lower)
- Hover tooltip: "Estimate = GPU memory bandwidth × 0.65 efficiency ÷ model active bytes. Actual varies with context length, batch size, kernel. CPU estimate assumes DDR5 ~80 GB/s."
- NO hypothetical GPU comparison (no "what if you had a 4090" columns) — only what's actually in this machine
- Plan 19 will upgrade GPU detection; this display automatically picks up new GPUs with no UI changes

**5.3 Installed models tab**
- File: `web/static/app.js`, `web/main.py`
- Existing `[Installed]` tab reads from `GET /api/tags` (Ollama's installed list)
- Cross-reference with DB to show tok/s + VRAM badge for installed models too
- If installed model not in DB (custom import), show "N/A — not in catalog"

### Phase 6 — Options Menu Restructure (Three Tabs + External Provider CLIs)

**6.1 Top-level tab navigation in Options**
- File: `web/templates/index.html`, `web/static/app.js`, `web/static/style.css`
- Three tabs at the top of the Options panel:
  - **[Model Services]** — services that actually run models (Ollama, LM Studio, vLLM, etc.)
  - **[Model Databases]** — catalog fetchers that build local databases from remote sources (HuggingFace, future: ModelScope, OpenRouter catalog, etc.)
  - **[Authentication]** — API tokens + user account management
- Active tab persisted in localStorage (`sovereignai.options.activeTab`)
- Tabs are horizontal buttons, full-width, with underline indicator on active

**6.2 [Model Services] tab — services that run models**
- Each service gets its own section with a header + state indicator + three action buttons + service-control buttons
- Layout pattern:
  ```
  ┌─ Ollama ──────────────────── ● running ────┐
  │  State: installed · running (v0.x.x)      │
  │  Host: http://localhost:11434             │
  │  Models path: C:\Users\...\.ollama\models │
  │                                           │
  │  [Download]  [Update]  [Uninstall]        │
  │                                           │
  │  [Start] [Stop] [Restart]                 │
  └───────────────────────────────────────────┘
  ┌─ LM Studio ───────────────── ○ not installed ─┐
  │  State: not installed                     │
  │  [Download]  [Update]  [Uninstall]        │
  │  (Update + Uninstall disabled when not    │
  │   installed)                              │
  └───────────────────────────────────────────┘
  ```
- State indicator dot:
  - Green (●) = installed + running
  - Amber (●) = installed but not running
  - Gray (○) = not installed
  - Red (●) = installed but error state
- Service-control buttons ([Start]/[Stop]/[Restart]) only appear for services that have a daemon process
- Action buttons disabled when not applicable (e.g. Uninstall disabled if not installed, Update disabled if not installed)

**6.3 [Model Databases] tab — catalog fetchers**
- Each database gets its own section with a header + state indicator + three action buttons
- Layout pattern:
  ```
  ┌─ Hugging Face ───────────── ● installed ──┐
  │  State: installed · 4,827 models in DB    │
  │  Last sync: 2026-06-30 14:23              │
  │  DB path: settings\models.db              │
  │                                           │
  │  [Download]  [Update]  [Uninstall]        │
  └───────────────────────────────────────────┘
  ┌─ ModelScope ──────────────── ○ not installed ─┐
  │  State: not installed                     │
  │  [Download]  [Update]  [Uninstall]        │
  │  (Update + Uninstall disabled when not    │
  │   installed)                              │
  └───────────────────────────────────────────┘
  ```
- State indicator dot:
  - Green (●) = installed (DB exists with rows)
  - Amber (●) = installed but DB empty (downloaded but never synced)
  - Gray (○) = not installed (DB file doesn't exist)
  - Red (●) = installed but error state (last sync failed)
- No service-control buttons — databases are not daemons, they don't Start/Stop
- Action buttons disabled when not applicable

**6.4 External CLI programs per provider (testable in isolation)**

Each provider has its own standalone CLI module. Services live under `sovereignai/services/<name>/cli.py`, databases live under `sovereignai/databases/<name>/cli.py`. These can be invoked from the terminal by Devin for testing and debugging, independent of the web UI. The Options panel shells out to these (or imports the same functions) so the UI and CLI share one code path.

**Common CLI interface (all services AND databases must implement):**

```bash
# Get provider state as JSON
python -m sovereignai.<services|databases>.<name>.cli status

# Download/install provider (full install — DB build, package install, etc.)
python -m sovereignai.<services|databases>.<name>.cli download

# Update provider (incremental sync, version upgrade, etc.)
python -m sovereignai.<services|databases>.<name>.cli update

# Uninstall provider (delete DB, remove package, etc.)
python -m sovereignai.<services|databases>.<name>.cli uninstall [--yes]
```

`status` returns JSON:
```json
{
  "kind": "service",            // "service" | "database"
  "name": "ollama",
  "installed": true,
  "state": "running",          // "running" | "installed" | "not_installed" | "error"
  "version": "v0.6.2",         // if applicable
  "details": {                 // provider-specific
    "models_in_db": 4827,        // databases only
    "last_sync": "2026-06-30T14:23:00Z",  // databases only
    "host": "http://localhost:11434",     // services only
    "models_path": "C:\\Users\\...\\.ollama\\models"  // services only
  },
  "error": null                // error message if state == "error"
}
```

Each CLI command exits 0 on success, non-zero on failure. Stderr contains human-readable progress. All operations emit trace events to the bus with source `[<name>_cli]`.

**6.5 [Hugging Face] database CLI**

File: `sovereignai/databases/huggingface/cli.py` (new), `sovereignai/databases/huggingface/__init__.py` (new)

- This is a Model Database — fetches catalog data from huggingface.co and stores it in local SQLite. No daemon.
- `status` — return `kind="database"` + installed/state + DB row count + last sync timestamp + DB file path
- `download` — full sync from HF API, populate `settings/models.db` from scratch (create schema if missing)
- `update` — incremental sync (compare `last_modified` from HF, update changed rows only)
- `uninstall` — confirm prompt, delete `settings/models.db` file, clear any HF token from `settings/config.json`
- Reads HF API token from `settings/config.json` if present (anonymous if absent — lower rate limit)
- Logs all activity to trace bus with source `[huggingface_cli]`
- Standalone testable: Devin can run `python -m sovereignai.databases.huggingface.cli download` in terminal without the web server running

**6.6 [Ollama] service CLI**

File: `sovereignai/services/ollama/cli.py` (new), `sovereignai/services/ollama/__init__.py` (new)

- This is a Model Service — actually runs models locally. Has a daemon process.
- `status` — return `kind="service"` + installed/running state + version (via `ollama --version`) + models path + host URL
- `download` — install Ollama via `winget install Ollama.Ollama` (Windows) or appropriate package manager on Linux/macOS. Verify install with `ollama --version`. Do NOT start the service (user clicks Start in UI).
- `update` — `winget upgrade Ollama.Ollama` (Windows) or equivalent. If already latest, exit 0 with message "Already up to date".
- `uninstall` — `winget uninstall Ollama.Ollama` (Windows) or equivalent. Confirm prompt. Note: does NOT delete `~/.ollama/models` directory (user data) — only removes the binary. Print path to models dir so user can manually delete if desired.
- Additional service-control commands (NOT part of the standard 3-button interface, used by the [Start]/[Stop]/[Restart] buttons in the UI):
  - `python -m sovereignai.services.ollama.cli start` — spawn `ollama serve` as detached subprocess, return PID, poll `/api/tags` up to 10s
  - `python -m sovereignai.services.ollama.cli stop` — terminate the PID SovereignAI spawned; refuse if SovereignAI didn't spawn it
  - `python -m sovereignai.services.ollama.cli restart` — stop + start
- All spawn/poll/exit activity logged at TRACE level with source `[ollama_cli]` (feeds Phase 2.2 TRACE logging)
- Standalone testable: Devin can run `python -m sovereignai.services.ollama.cli status` in terminal

**6.7 Registration framework (services + databases)**

Files: `sovereignai/services/__init__.py` (new), `sovereignai/services/base.py` (new), `sovereignai/databases/__init__.py` (new), `sovereignai/databases/base.py` (new)

- Define `ServiceBase` abstract class for model services (services that run models): `name`, `status()`, `download()`, `update()`, `uninstall()`, plus optional `start()`, `stop()`, `restart()` if the service has a daemon
- Define `DatabaseBase` abstract class for model databases (catalog fetchers): `name`, `status()`, `download()`, `update()`, `uninstall()` — no service-control methods
- Each subclass registers via entry points or a simple registry file
- The Options [Model Services] tab auto-discovers registered services and renders a section for each
- The Options [Model Databases] tab auto-discovers registered databases and renders a section for each
- Adding a new service (LM Studio, vLLM, etc.): implement `ServiceBase`, register, section appears in [Model Services] tab — no UI code changes
- Adding a new database (ModelScope, OpenRouter catalog, etc.): implement `DatabaseBase`, register, section appears in [Model Databases] tab — no UI code changes
- Ollama registered as service by default; HuggingFace registered as database by default
- Providers that are not yet installed show with gray state dot + "not installed" label

**6.8 [Authentication] tab**
- Two sections:
  - **API Tokens** — manage tokens for services + databases:
    - HuggingFace token (password field) — saved to `settings/config.json` with chmod 600 per OR91
    - Future: tokens declared by other services/databases via the registration framework (each provider can declare a `token_field` descriptor)
    - Each token: label + password input + Save button + Clear button + Test button
    - Test button validates the token by calling provider's API (HF: whoami-v2 endpoint)
  - **User Accounts** (existing functionality, moved here from old Options layout):
    - Current logged-in user display
    - Logout button
    - List of registered users (admin only) with delete button
- All token save/clear operations logged at INFO level with source `[auth_tab]` (token values themselves never logged)

**6.9 Backend endpoints for the Options panel**
- File: `web/main.py`
- `GET /api/services` — returns list of registered services with their `status()` JSON
- `GET /api/databases` — returns list of registered databases with their `status()` JSON
- `POST /api/services/<name>/download` — invokes service's `download()` (async, returns job ID, progress via SSE)
- `POST /api/services/<name>/update` — invokes service's `update()` (async, returns job ID, progress via SSE)
- `POST /api/services/<name>/uninstall` — invokes service's `uninstall()` (sync, returns result)
- `POST /api/services/<name>/start` — invokes service's `start()` (sync, returns PID + status)
- `POST /api/services/<name>/stop` — invokes service's `stop()` (sync)
- `POST /api/services/<name>/restart` — invokes service's `restart()` (sync)
- `POST /api/databases/<name>/download` — invokes database's `download()` (async, returns job ID, progress via SSE)
- `POST /api/databases/<name>/update` — invokes database's `update()` (async, returns job ID, progress via SSE)
- `POST /api/databases/<name>/uninstall` — invokes database's `uninstall()` (sync, returns result)
- `GET /api/auth/tokens` — returns list of token field descriptors (provider kind, provider name, field name, has_value: bool) — never returns the actual token values
- `POST /api/auth/tokens/<provider>` — save token value
- `DELETE /api/auth/tokens/<provider>` — clear token value
- All long-running operations emit SSE events with progress so the UI can show spinners + status updates

### Phase 7 — Tests + Coverage

**7.1 New tests required**
- `tests/web/test_logs_panel.py` — verify Logs panel loads as 10th sidebar item, filters work, no floating drawer
- `tests/web/test_options_tabs.py` — verify [Model Services] + [Model Databases] + [Authentication] tabs switch correctly, persist active tab
- `tests/services/test_registry.py` — verify ServiceBase registration, auto-discovery, status aggregation
- `tests/databases/test_registry.py` — verify DatabaseBase registration, auto-discovery, status aggregation
- `tests/databases/test_huggingface_cli.py` — invoke `download`/`update`/`uninstall`/`status` directly (mocked HF API), verify DB state changes
- `tests/services/test_ollama_cli.py` — invoke `status`/`start`/`stop`/`restart` (mocked subprocess), verify TRACE logs, PID tracking
- `tests/web/test_service_endpoints.py` — verify `GET /api/services`, `POST /api/services/<name>/download` etc. all return correct shapes
- `tests/web/test_database_endpoints.py` — verify `GET /api/databases`, `POST /api/databases/<name>/download` etc. all return correct shapes
- `tests/web/test_auth_tokens.py` — verify token save/clear endpoints, verify chmod 600 on config.json, verify tokens never echoed back
- `tests/web/test_models_db.py` — schema creation, insert, query, pagination, search
- `tests/web/test_toks_per_sec_runtime.py` — given model active_bytes_gb + detected GPU bandwidth, verify runtime tok/s computation matches formula
- `tests/web/test_vram_badge.py` — given model size + VRAM + RAM, verify correct badge
- All existing tests must still pass

**7.2 Coverage floor**
- OR77 applies: coverage ≥ 89% at `/close`. Target ~91%.
- Run: `pytest --cov=sovereignai --cov=web --cov-report=term-missing`
- If below 89%, add tests — do not disable production features to game coverage (OR87)

### Phase 7 — Close Workflow

- Follow `.devin/workflows/close.md` — ALL 22 steps, no skipping (OR92/OR96)
- Step 17: `git add -A` (NOT `git rm` — L40 fix)
- Commit per OR75/OR80/OR83: `git add -A` for every commit, no exceptions
- Tag: `prompt-18.1` — only after all 22 steps pass (OR76)
- Mypy: clean, no errors. OR90 = STOP if any. No "pre-existing" exemption.
- Investigate every "Command errored" output (OR88)

## Closing

This plan is a patch on top of completed Plan 18. It pivots the Logs panel from a floating drawer to a 10th sidebar item (killing 3 drawer bugs structurally), carries forward the Ollama update + diagnostics that 18 didn't actually execute, and pivots the HuggingFace catalog from live API calls to a standalone SQLite DB with computed VRAM badges and tok/s estimates using the memory-bandwidth formula.

Phase 3 (Ollama update) must run before Phase 3.3 (download pipeline retest) — the update alone may fix the `ollama create` failure. Phase 4 (DB) must complete before Phase 5 (badges + tok/s display) since the display reads pre-computed fields from the DB.

Plan 19 (separate, hardware-focused) will upgrade the Hardware panel to Task Manager style with multi-GPU detection, live graphs, and SSE sampling. Plan 18.1's VRAM badge computation will use whatever hardware detection is currently available; Plan 19 will upgrade the detector and the badges will automatically benefit.

Report back when:
- Phase 1 + 2 complete (Logs panel live, verbose logging visible)
- Phase 3 complete (Ollama updated, Start button works, download pipeline tested)
- Phase 4 complete (DB populated, sync task running)
- Phase 5 complete (VRAM badges + tok/s visible in catalog)
- Phase 6 + 7 complete (coverage number + tag pushed)

If blocked on any step, STOP and report — do not push partial work.

---

## Appendix A — STOP Conditions

- Mypy errors (OR90) — STOP, no exemption
- Coverage < 89% at close (OR77) — STOP, add tests
- Any "Command errored" uninvestigated (OR88) — STOP, investigate
- conftest fixture touching real `settings/auth.json` — STOP, fix isolation (carry-over from 18, verify still clean)
- Skip any of the 22 close steps (OR92/OR96) — STOP, run all steps
- Premature git tag before all steps pass (OR76) — STOP
- Disable production feature to make test pass (OR87) — STOP
- Workaround for old Ollama instead of updating — STOP, update the environment

## Appendix B — Files to Modify

**Backend — Services:**
- `sovereignai/services/__init__.py` (new) — service registry
- `sovereignai/services/base.py` (new) — `ServiceBase` abstract class
- `sovereignai/services/ollama/__init__.py` (new)
- `sovereignai/services/ollama/cli.py` (new) — Ollama CLI: `status`/`download`/`update`/`uninstall`/`start`/`stop`/`restart`
- `sovereignai/services/ollama/subprocess_manager.py` (new) — TRACE-logged subprocess spawn/poll/kill

**Backend — Databases:**
- `sovereignai/databases/__init__.py` (new) — database registry
- `sovereignai/databases/base.py` (new) — `DatabaseBase` abstract class
- `sovereignai/databases/huggingface/__init__.py` (new)
- `sovereignai/databases/huggingface/cli.py` (new) — HF CLI: `status`/`download`/`update`/`uninstall`
- `sovereignai/databases/huggingface/sync.py` (new) — HF API fetcher + parser
- `sovereignai/databases/huggingface/schema.py` (new) — SQLite schema for `settings/models.db`

**Backend — Web:**
- `web/main.py` — new endpoints: `GET /api/services`, `GET /api/databases`, `POST /api/services/<name>/{download,update,uninstall,start,stop,restart}`, `POST /api/databases/<name>/{download,update,uninstall}`, `GET /api/auth/tokens`, `POST /api/auth/tokens/<provider>`, `DELETE /api/auth/tokens/<provider>`, `GET /api/models/catalog` (DB-backed with runtime tok/s computation), VRAM badge endpoint
- `sovereignai/.../logging_or_event_bus.py` — default level DEBUG, no log truncation
- `sovereignai/.../hardware_detector.py` (existing, used as-is by 18.1; Plan 19 will upgrade) — provides `list_gpus()` with `name`, `vram_gb`, `bandwidth_gb_s`, `type`

**Frontend:**
- `web/templates/index.html` — add Logs as 10th sidebar item, remove floating drawer, three-tab Options layout ([Model Services] / [Model Databases] / [Authentication]), provider section rendering, VRAM badge + tok/s display in Models panel
- `web/static/app.js` — Logs panel loader, tab switching, provider section rendering with state polling, DB-backed catalog with pagination, Load More button, family collapse/expand, VRAM badge + tok/s display, token save/clear/test
- `web/static/style.css` — remove drawer styles, add Logs panel styles, tab styles, badge colors (green/amber/red/gray), provider section styles

**Tests:**
- `tests/web/test_logs_panel.py` (new)
- `tests/web/test_options_tabs.py` (new)
- `tests/services/test_registry.py` (new)
- `tests/services/test_ollama_cli.py` (new)
- `tests/databases/test_registry.py` (new)
- `tests/databases/test_huggingface_cli.py` (new)
- `tests/web/test_service_endpoints.py` (new)
- `tests/web/test_database_endpoints.py` (new)
- `tests/web/test_auth_tokens.py` (new)
- `tests/web/test_models_db.py` (new)
- `tests/web/test_toks_per_sec_runtime.py` (new)
- `tests/web/test_vram_badge.py` (new)

**Docs:**
- `documents/plan-18.1-report.md` (new — close report with Phase 3 Ollama findings + DB row count + sample tok/s calculations)

## Appendix C — Files NOT to Modify

- Any existing OR rule numbering — gaps are permanent (OR84)
- Any existing landmine numbering — gaps are permanent (OR84)
- `documents/models-panel-design-reference.md` — locked spec, do not edit
- Other department specs — out of scope for this plan
- Hardware panel detection logic — Plan 19 owns this; 18.1 uses whatever exists
