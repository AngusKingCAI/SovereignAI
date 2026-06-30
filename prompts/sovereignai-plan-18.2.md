# SovereignAI — Plan 18.2: prompt-18.2 — Models Menu Restructure + Universal Tracing + Bug Fixes

## Context

Plan 18.1 is running. Plan 18.2 picks up after 18.1 closes and does three things in one pass:

1. **Models menu restructure** — four-level dropdown hierarchy (DB → file type → Org → Family → Model version → quant variants), with sortable columns inside the expanded list, and HF pipeline-tag categories displayed next to model families
2. **Universal tracing mandate** — per user: "All processing within the whole project should be traced so it can be viewed in the log." Two new governance rules (OR97 + OR98) enforce this going forward
3. **Bug fixes** — anything 18.1 leaves broken

### Pre-scan findings (GLM cloned the repo to inform the tracing work)

- **TraceEmitter** is the canonical observability surface — singleton, constructor-injected, already exists at `sovereignai/shared/trace_emitter.py`. No new infrastructure needed.
- **7 of 30** `sovereignai/` files have zero tracing despite containing real logic: `routing_engine.py`, `hardware_probe.py`, `manifest_parser.py`, `semver.py`, `conformance/base.py`, `conformance/registry.py`, `types.py`
- **`web/main.py`**: 35 functions, only 11 trace emits — at least 24 endpoint functions are silent
- **`cli/`, `tui/`, `scripts/`, `phone/`** directories: zero tracing
- Correlation IDs rarely threaded through call chains — most emits pass `None`

### Model category taxonomy (HF pipeline-tag, locked)

Full taxonomy from huggingface.co/models. Each model in the DB gets ONE primary `category` field at insert time. Categories appear as a label next to the model family in the dropdown UI. Categories are also filterable via a sidebar filter (Phase 2.4).

**Top-level groups:**

- **Multimodal** — Audio-Text-to-Text, Image-Text-to-Text, Image-Text-to-Image, Image-Text-to-Video, Visual Question Answering, Document Question Answering, Video-Text-to-Text, Visual Document Retrieval, Any-to-Any
- **Computer Vision** — Depth Estimation, Image Classification, Object Detection, Image Segmentation, Text-to-Image, Image-to-Text, Image-to-Image, Image-to-Video, Unconditional Image Generation, Video Classification, Text-to-Video, Zero-Shot Image Classification, Mask Generation, Zero-Shot Object Detection, Text-to-3D, Image-to-3D, Image Feature Extraction, Keypoint Detection, Video-to-Video
- **Natural Language Processing** — Text Classification, Token Classification, Table Question Answering, Question Answering, Zero-Shot Classification, Translation, Summarization, Feature Extraction, Text Generation, Fill-Mask, Sentence Similarity, Text Ranking
- **Audio** — Text-to-Speech, Text-to-Audio, Automatic Speech Recognition, Audio-to-Audio, Audio Classification, Voice Activity Detection
- **Tabular** — Tabular Classification, Tabular Regression, Time Series Forecasting
- **Reinforcement Learning** — Reinforcement Learning
- **Robotics** — Robotics
- **Other** — Graph Machine Learning

Most GGUFs will be `Text Generation` (NLP) or `Any-to-Any` / `Image-Text-to-Text` (Multimodal). The full list is locked so we don't have to revisit when a non-LLM model appears.

## Plan Body

### Phase 0 — Carryover from Plan 18.1 (must ship before any new work)

Plan 18.1 shipped with ~30% of specified deliverables despite "7 phases complete, 351 tests pass, 89% coverage". Verified on disk after 18.1.1:

**0.1 Items 18.1 silently skipped (must ship in 18.2)**

| Item | 18.1 spec | What shipped | Action in 18.2 |
|------|-----------|--------------|----------------|
| Provider CLI framework | Phase 6.4-6.7: `sovereignai/services/` + `sovereignai/databases/` with `ServiceBase`/`DatabaseBase` abstract classes + registration | Directories DO NOT EXIST | Build per Phase 6 below |
| Three-button rows | Phase 6.2-6.3: `[Download] [Update] [Uninstall]` per provider | Only tab navigation shipped | Add per Phase 6 |
| Backend endpoints | Phase 6.9: `/api/services`, `/api/databases`, `/api/services/<name>/{download,update,uninstall,start,stop,restart}`, `/api/databases/<name>/{download,update,uninstall}`, `/api/auth/tokens`, `POST/DELETE /api/auth/tokens/<provider>` | NOT ONE endpoint exists | Add per Phase 6 |
| Ollama status panel + Start button | Phase 3.2: live status dot + Start button + version display | NOT done — only static "Host: ..." text | Add per Phase 6 |
| Ollama subprocess TRACE logging | Phase 2.2: TRACE-level emits for command/PID/poll/stdout/stderr/exit code | Only 1 of 6 trace points shipped (ERROR on failed spawn) | Add per Phase 4 |
| HF sync CLI | Phase 4.2: `sovereignai/databases/huggingface/cli.py` with `download`/`update`/`uninstall`/`status` commands | NOT done — only `models_db.py` schema module exists | Add per Phase 6 |
| 11 of 12 required test files | Phase 7.1: 12 new test files specified | Only `tests/test_models_db.py` created | Add per Phase 7 |
| VRAM badge for installed models | Phase 5.3: cross-reference installed models with DB | NOT done | Add per Phase 2 |
| Models menu 4-level dropdown | (this plan, Phase 1) | Old 2-tab `[Installed] [HuggingFace]` layout | Add per Phase 1-2 |
| **app.js syntax — Python docstrings in JS functions** | (not in 18.1 spec — Devin accidentally wrote Python-style docstrings inside JS functions) | **Line 945 + 962 of `web/static/app.js` contain `"""..."""` — JavaScript SyntaxError, entire file fails to load, ALL click handlers dead. 18.1.1 fixed the HTML double-class bug but didn't catch this. Verified: `node --check web/static/app.js` fails at line 945.** | **Fix immediately at Phase 0 — convert `"""..."""` to `// ...` comments at lines 945 + 962. Verify with `node --check`.** |

**0.2 Items 18.1 partially shipped (verify + complete)**

- Default log level (Phase 2.1) — claimed DEBUG but no evidence in log. Verify and set to DEBUG if not.
- Download destination UI (Phase 3.4) — partial. Complete per Phase 6.
- VRAM badge computation (Phase 5.1) — done inline in app.js. Move to `sovereignai/shared/vram_badge.py` for testability.
- Tok/s display (Phase 5.2) — done inline. Move to backend endpoint for testability.
- No-log-truncation (Phase 2.3) — partial. Add explicit max-line-length guard.

**0.3 Verification mandate**

For each Phase 0 item, Devin MUST run an executed verification (not visual code inspection) per new OR100. Examples:
- "Provider CLI framework exists" → run `python -m sovereignai.services.ollama.cli status` and verify JSON output
- "Three-button rows exist" → curl the page, grep for `<button>` elements with the right IDs
- "Backend endpoints exist" → curl each endpoint and verify response shape
- **"app.js parses successfully" → run `node --check web/static/app.js` and verify exit 0 (per new OR104). This MUST be the very first verification at Phase 0 — until app.js parses, NO other UI verification is meaningful because the entire JS file fails to load.**

Items that can't be verified via execution get implemented, not marked "already done".

**0.4 Hotfix priority ordering**

The app.js syntax error (Phase 0 item: app.js Python docstrings) is **P0 — fix FIRST**, before any other Phase 0 work. Reasoning: the bug makes the entire web UI non-interactive. Every other Phase 0 verification depends on app.js loading successfully. Devin should:
1. Fix the two docstring lines (945, 962)
2. Run `node --check web/static/app.js` — verify exit 0
3. Verify in a browser that tabs are now clickable
4. THEN proceed with the rest of Phase 0

**This bug is exactly what OR104 (HTML/CSS/JS syntax validation) and OR106 (browser smoke test) are designed to prevent.** The 18.1.1 hotfix caught the HTML double-class bug but missed the JS syntax bug because no `node --check` was run. With OR104 in force, every future JS edit will require `node --check` to pass before tests run. With OR106 in force, every future UI plan will require an actual browser smoke test that would have immediately caught "tabs not clickable."

### Phase 1 — Models Menu Restructure

**1.1 Four-level dropdown hierarchy**

Target layout:

```
[Installed] [Hugging Face] [Future DB] [Future DB]      ← DB tabs (top)
  ↓ (when HuggingFace clicked)
[GGUF] [Safetensors] [PyTorch] [Other]                  ← File type tabs (only tabs this DB has)
  ↓ (when GGUF clicked)
▼ Google                                                 ← Org dropdown (level 1)
    [Multimodal · Image-Text-to-Text]                    ← category label next to family
    ▼ Gemini                                             ← Family dropdown (level 2)
        ▼ Gemini-1.5                                     ← Model version dropdown (level 3)
            [Q4_K_M]   4.2 GB   130 tok/s   4.1M dl      ← Quant variants (level 4)
            [Q5_K_M]   4.8 GB   115 tok/s   3.2M dl
            [Q8_0]     7.1 GB    78 tok/s   1.8M dl
            [F16]     14.0 GB    40 tok/s     89K dl
        ▶ Gemini-1.4 (collapsed)
    ▶ Gemma (collapsed)
▶ Meta (collapsed)
▶ Mistral (collapsed)
```

- File: `web/templates/index.html`, `web/static/app.js`, `web/static/style.css`
- Each level is collapsible. Default state: all collapsed on first load (only DB tab + file type tab + Org list visible). User expands what they want.
- Persist expansion state in localStorage (`sovereignai.models.expanded`) — survives refresh
- Dropdowns themselves are NOT sortable (stay alphabetical) per user decision. Only the level-4 quant variants list is sortable.
- Empty state per level: if an Org has no GGUFs, it doesn't appear in the GGUF tab (filter at query time)

**1.2 Sortable columns in the quant variants list**

Columns (default sort: Name ascending, per user decision):

| Column | Sort direction toggle |
|--------|----------------------|
| Name (e.g. "Q4_K_M") | asc/desc |
| Size (GB) | asc/desc |
| Speed (tok/s on detected hardware) | asc/desc |
| Downloads | asc/desc |
| Likes | asc/desc |
| Quantization (parsed level: Q2 < Q4 < Q5 < Q8 < F16) | asc/desc |
| VRAM required (GB) | asc/desc |
| Last modified | asc/desc |
| Parameter count (1B/3B/7B etc.) | asc/desc |
| Context length (8K/32K/128K) | asc/desc |
| License | asc/desc |
| Architecture (Dense/MoE) | asc/desc |

- Click column header → sort ascending. Click again → descending. Click a different column → switch primary sort.
- Sort indicator: ▲ for asc, ▼ for desc, no marker for unsorted.
- Persist sort field + direction per DB tab in localStorage (`sovereignai.models.sort.<db_tab_name>`) per user decision.
- Multi-column sort: out of scope for v1. Single primary sort only.

**1.3 Category label next to model family**

- For each Family row (level 2), display the HF pipeline-tag category as a small badge:
  - Format: `[NLP · Text Generation]` or `[Multimodal · Image-Text-to-Text]`
  - Color-coded by top-level group: blue (Multimodal), green (NLP), orange (Computer Vision), purple (Audio), gray (Tabular/RL/Robotics/Other)
- Category is read from the DB `category` field (added in Phase 1.5)
- All quant variants under a family share the same category (it's a family-level attribute, not a quant-level attribute)
- If a family has models with mixed categories (rare), show "Multiple" badge with tooltip listing all categories present

**1.4 File type tabs**

- Tabs at level 2 are dynamically populated from the DB based on what file types actually exist:
  - HuggingFace DB will have: GGUF, Safetensors, PyTorch, ONNX, Other
  - Each tab shows only models of that file type
  - If a DB has only one file type (e.g. a future GGUF-only DB), the file type tab row is hidden (no choice to make)
- Persist active file type tab per DB tab in localStorage
- File type detection: parse the `filename` field for `.gguf`, `.safetensors`, `.pt`/`.bin` (PyTorch), `.onnx`, else "Other"

**1.5 DB schema changes for Models DB**

- File: `sovereignai/databases/huggingface/schema.py` (was created in 18.1)
- Add columns:
  ```sql
  ALTER TABLE models ADD COLUMN org TEXT;                  -- e.g. "google", "meta-llama", "mistralai"
  ALTER TABLE models ADD COLUMN family TEXT;               -- e.g. "gemini", "gemma", "llama", "mistral"
  ALTER TABLE models ADD COLUMN model_version TEXT;        -- e.g. "gemini-1.5", "gemma-2", "llama-3.1"
  ALTER TABLE models ADD COLUMN quant_level INTEGER;       -- parsed: 0=unquantized, 20=Q2, 40=Q4, 50=Q5, 80=Q8, 160=F16
  ALTER TABLE models ADD COLUMN file_type TEXT;            -- "gguf" | "safetensors" | "pytorch" | "onnx" | "other"
  ALTER TABLE models ADD COLUMN category TEXT;             -- HF pipeline-tag, e.g. "text-generation", "image-text-to-text"
  ALTER TABLE models ADD COLUMN category_group TEXT;       -- top-level group, e.g. "nlp", "multimodal"
  ```
- Migration: existing rows get these fields populated by re-running the HF sync `update` command (Phase 1.6)
- Indexes for performance:
  ```sql
  CREATE INDEX idx_models_org ON models(org);
  CREATE INDEX idx_models_family ON models(family);
  CREATE INDEX idx_models_model_version ON models(model_version);
  CREATE INDEX idx_models_file_type ON models(file_type);
  CREATE INDEX idx_models_category ON models(category);
  CREATE INDEX idx_models_quant_level ON models(quant_level);
  ```

**1.6 Sync updates to populate new fields**

- File: `sovereignai/databases/huggingface/sync.py`
- During `download` and `update`:
  - Parse `repo_id` (e.g. `lmstudio-community/gemma-4-E4B-it-GGUF`) → split on `/` → `org` = first segment
  - Parse `filename` (e.g. `gemma-4-E4B-it-Q4_K_M.gguf`) → extract quant tag (Q4_K_M, Q5_K_M, Q8_0, F16, etc.) → compute `quant_level` integer
  - Fetch `config.json` from HF API → `architectures` field → map to `family` (gemma, llama, mistral, etc.) via a lookup table
  - Fetch model card / `README.md` frontmatter → `pipeline_tag` field → `category` + `category_group`
  - Parse `model_version` from `repo_id` or `config.json` `name` field (e.g. "gemma-4-E4B-it" → family="gemma", model_version="gemma-4-E4B")
- All parsing logged at DEBUG with source `[huggingface_sync]` so misparses are visible in the log
- Misparse handling: if family can't be determined, set `family="unknown"` and emit WARN trace. Same for category — default to `category="other"`, `category_group="other"` with WARN.

**1.7 Backend endpoint for the hierarchical view**

- File: `web/main.py`
- New endpoint: `GET /api/models/catalog?db=<db_name>&file_type=<type>&org=<org>&family=<family>&model_version=<version>&sort=<field>&dir=<asc|desc>&page=<n>`
- Returns hierarchical data structure:
  ```json
  {
    "orgs": [
      {
        "name": "google",
        "model_count": 12,
        "families": [
          {
            "name": "gemini",
            "category": "image-text-to-text",
            "category_group": "multimodal",
            "model_count": 3,
            "model_versions": [
              {
                "name": "gemini-1.5",
                "quant_variants": [
                  {
                    "id": 42,
                    "name": "Q4_K_M",
                    "size_gb": 4.2,
                    "toks_per_sec": [{"gpu": "RTX 4060", "toks": 130.0, "fits": true}, ...],
                    "downloads": 4100000,
                    "likes": 234,
                    "quant_level": 40,
                    "vram_required_gb": 5.0,
                    "last_modified": "2026-06-15T...",
                    "parameter_count": 4000000000,
                    "context_length": 8192,
                    "license": "gemma",
                    "architecture": "dense",
                    "repo_id": "lmstudio-community/gemini-1.5-pro-GGUF",
                    "filename": "gemini-1.5-pro-Q4_K_M.gguf"
                  },
                  ...
                ]
              },
              ...
            ]
          },
          ...
        ]
      },
      ...
    ]
  }
  ```
- For lazy loading: if `org` parameter is omitted, return only the org list (level 1). If `org` is provided but `family` is omitted, return that org's families (level 2). Etc. This keeps initial payload small.
- All emits carry correlation_id per OR98.

**1.8 Frontend rendering**

- File: `web/static/app.js`, `web/templates/index.html`
- Three-tier tab bar at top: DB tabs → file type tabs → (then dropdown content)
- Org dropdown: clicking an Org name toggles its expansion. Lazy-load families on first expand (call endpoint with `org=google`).
- Family dropdown: clicking a Family name toggles its expansion. Lazy-load model versions on first expand.
- Model version dropdown: clicking a Model version toggles its expansion. Lazy-load quant variants on first expand.
- Quant variants: rendered as a sortable table (Phase 1.2). Columns + sort indicators as specified.
- Category badge: rendered next to each Family name (Phase 1.3).
- Empty state: "No models in this category" with a Refresh button if DB is empty.
- Loading state: spinner + "Loading..." per dropdown while fetching.
- Error state: red text with "Retry" button.

### Phase 2 — Filters and Search

**2.1 Search box**
- File: `web/static/app.js`
- Free-text search box above the dropdowns. Filters across `repo_id`, `family`, `model_version`, `org`, `tags`.
- When a search query is active, the hierarchical view is replaced by a flat results list (still sortable).
- Clear search → return to hierarchical view.
- Persist last search in localStorage.

**2.2 Category filter sidebar**
- A collapsible filter panel (left side or top) with checkboxes for each category group:
  - ☑ Multimodal (1,234 models)
  - ☑ NLP (4,103 models)
  - ☐ Computer Vision (892 models)
  - ☐ Audio (421 models)
  - ☐ Tabular (12 models)
  - ☐ RL (8 models)
  - ☐ Robotics (3 models)
  - ☐ Other (67 models)
- Clicking a group expands to show subcategories with their own checkboxes
- Multiple categories can be selected — filter is OR within a group, AND across groups
- When filter is active, dropdowns only show models matching the filter
- Persist filter state in localStorage

**2.3 VRAM fit filter**
- Quick filter buttons: "Fits my VRAM" / "Fits my VRAM+RAM" / "Show all"
- "Fits my VRAM": only show models where `vram_required_gb ≤ detected_vram_gb`
- "Fits my VRAM+RAM": only show models where `vram_required_gb ≤ detected_vram_gb + detected_ram_gb`
- "Show all": no filter
- Persist selection in localStorage

**2.4 Quant level filter**
- Checkboxes: ☑ Q2 ☑ Q4 ☑ Q5 ☑ Q8 ☑ F16 ☑ Other
- Useful for users who only want to see specific quants
- Persist in localStorage

### Phase 3 — Bug Fixes (anything 18.1 leaves broken)

**3.1 Triage at start of Phase 3**
- After 18.1 closes, run the full test suite + manual smoke test of the web UI
- Capture a list of every failing test, every UI bug, every error in the log
- Each bug gets a row in `temp/plan-18.2-bugs.md` (committed) with: description, reproduction steps, severity (P0/P1/P2), file:line if known

**3.2 Fix P0 bugs first**
- P0 = blocks core functionality (can't load models panel, can't login, can't start Ollama, crash on startup)
- Fix one at a time, commit per fix, verify before moving to next
- Each fix MUST emit traces per OR97 — verify the fix itself is traced

**3.3 Fix P1 bugs**
- P1 = degraded functionality but workaround exists
- Same process as P0

**3.4 P2 bugs**
- P2 = cosmetic or minor
- Fix if time permits; otherwise document in DEBT.md for future plan
- Do not block close on P2 unless explicitly required

### Phase 4 — Universal Tracing Mandate (OR97 + OR98)

**4.1 Generate function inventory**
- Devin writes a script: walk every `.py` file (excluding `.git/`, `__pycache__/`, `.venv/`, `node_modules/`) and produce:
  - File path, function/method name, line number
  - Whether the function body contains any of: `emit(`, `trace_emitter`, `logger.`, `self._emit`, `self.emit`
  - Whether the function takes a `correlation_id` parameter or has access via `self`
- Output: `temp/tracing_audit.csv` (committed)
- This is the source of truth for what to fix

**4.2 Classify each untraced function**
- **MUST TRACE** — performs observable side effect (HTTP response, file I/O, subprocess, DB mutation, message dispatch, exception handler). Add tracing.
- **DELEGATE ONLY** — calls one or more traced functions and does nothing else. Add a single DEBUG "entered X" emit at function entry.
- **PURE** — no side effects, no I/O. Exempt per OR97.
- **ABSTRACT** — body is `pass`/`...`/`raise NotImplementedError`. Exempt.
- Output column `classification` in the CSV

**4.3 Fill gaps in `sovereignai/`**
- Known from pre-scan: `routing_engine.py`, `hardware_probe.py`, `manifest_parser.py`, `semver.py` (verify PURE), `conformance/base.py` (likely ABSTRACT), `conformance/registry.py`
- Cross-reference audit CSV. Fix every MUST TRACE + DELEGATE ONLY function.
- For each fix: INFO emit at entry (with correlation_id) + DEBUG emit at exit (with elapsed time + result summary). Long-running operations also emit progress.

**4.4 Fill gaps in `web/`**
- `web/main.py` — at least 24 endpoint functions need tracing
  - INFO at request receipt: `"POST /api/foo called by user=X correlation_id=Y"`
  - DEBUG at response: `"POST /api/foo returned 200 in 45ms"`
  - WARN on 4xx, ERROR on 5xx (include exception + traceback)
  - Generate correlation_id at entry, accept `X-Correlation-Id` header override, propagate to all downstream calls
- `web/hardware_probe.py` — every probe function emits start + result
- `web/schemas.py` — likely PURE (Pydantic models), verify

**4.5 Fill gaps in `cli/`, `tui/`, `scripts/`, `phone/`, adapters, skills**
- Every CLI/TUI entry point: INFO at start + DEBUG at each step + INFO at completion (with elapsed + exit code) + ERROR on failure. Generate correlation_id at process start.
- Scripts: audit per-script. AR check scripts in particular should emit PASS/FAIL for each rule checked.
- Adapters: `register()` + `activate()` emit INFO. Capability invocations emit DEBUG at entry + exit. Failures emit ERROR with full exception. Ollama adapter needs TRACE-level emits for every subprocess spawn.
- Skills: `execute()` emits INFO at entry + DEBUG at exit. Websearch skill emits DEBUG per query + result count.

**4.6 Correlation ID propagation (OR98)**
- New file: `sovereignai/shared/correlation.py` — `contextvars.ContextVar` for current correlation_id
- Helpers: `set_correlation_id(uuid)`, `get_correlation_id()`, `new_correlation_scope(uuid)` (context manager)
- Entry points (HTTP, CLI, TUI, scheduler) generate UUID4 and set the context var
- Components without explicit `correlation_id` parameter call `get_correlation_id()`
- Background threads copy parent's correlation_id into the new thread's context var at spawn time
- Subprocesses: correlation_id logged at spawn (parent's responsibility) — does not propagate into the subprocess's own logs

### Phase 5 — Enforcement (so untraced code never ships again)

**5.1 Static check script**
- New: `scripts/ar_checks/check_tracing.py`
- Walks every `.py` file, classifies functions (same logic as Phase 4.1-4.2)
- For each MUST TRACE or DELEGATE ONLY: verify `emit(` call exists. If not, FAIL with file:line.
- Exemptions: `@pure` decorator (new, opt-in) OR body is only `pass`/`...`/`raise NotImplementedError` OR exempt list (dataclass `__init__`, Pydantic validators)
- Exit 0 if pass, exit 1 with report if fail
- Runs in pre-commit + CI per existing AR check infrastructure

**5.2 Test that verifies no silent functions**
- New: `tests/test_universal_tracing.py`
- Imports the audit script's logic, runs the classifier on every Python module
- Asserts: no MUST TRACE or DELEGATE ONLY function lacks an emit call
- Runs in normal pytest suite — regression fails CI

**5.3 Update AGENTS.md with OR97 + OR98**
- Add OR97 + OR98 to governance rules
- Guidance: "When adding a new function, ask: does it perform I/O, mutate state, or handle exceptions? If yes, it MUST emit at least one trace event. Pure functions are exempt but document them as such."

### Phase 6 — Tests + Coverage

**6.1 New tests required**
- `tests/web/test_models_hierarchical.py` — verify endpoint returns correct hierarchical structure, lazy loading works at each level
- `tests/web/test_models_sort.py` — verify each sortable column sorts correctly in both directions
- `tests/web/test_models_filter.py` — verify category filter, VRAM fit filter, quant level filter, search
- `tests/web/test_models_category_badge.py` — verify category badge rendering for each category group
- `tests/databases/test_huggingface_sync_parsing.py` — verify org/family/model_version/quant_level/file_type/category parsing from sample repo_ids + filenames
- `tests/test_universal_tracing.py` — Phase 5.2 enforcement test
- `tests/shared/test_correlation.py` — context var set/get/clear, thread propagation, None outside scope
- `tests/web/test_endpoint_tracing.py` — call each endpoint, verify INFO at entry + DEBUG at exit + correlation_id propagation
- `tests/cli/test_cli_tracing.py` — invoke each CLI command, verify INFO at start + completion
- `tests/adapters/test_adapter_tracing.py` — register each adapter, verify INFO emit + DEBUG on invoke
- `tests/test_check_tracing.py` — tests the static check script itself
- All existing tests must still pass

**6.2 Coverage floor**
- OR77 applies: coverage ≥ 89% at `/close`. Target ~91%.
- Run: `pytest --cov=sovereignai --cov=web --cov-report=term-missing`

### Phase 7 — Close Workflow

- Follow `.devin/workflows/close.md` — ALL 22 steps, no skipping (OR92/OR96)
- Step 17: `git add -A`. Must include `temp/tracing_audit.csv` and `temp/plan-18.2-bugs.md`.
- Commit per OR75/OR80/OR83: `git add -A` for every commit
- Tag: `prompt-18.2` — only after all 22 steps pass (OR76)
- Mypy: clean. OR90 = STOP if any.
- Investigate every "Command errored" output (OR88)
- AR checks must pass — including new `check_tracing.py`

## Closing

This plan does three things in one pass: restructures the Models menu into a 4-level dropdown with sortable columns and HF category badges, fills every tracing gap the repo audit finds, and fixes any P0/P1 bugs 18.1 leaves behind.

Phase 1-2 (Models menu) and Phase 4-5 (tracing) are independent and can be done in parallel by Devin if it helps. Phase 3 (bug fixes) starts with a triage at plan open — Devin must run the test suite first to enumerate what's actually broken before fixing.

The audit CSV (`temp/tracing_audit.csv`) and bug list (`temp/plan-18.2-bugs.md`) are deliverables committed to the repo so future plans can compare against them.

Report back when:
- Phase 1-2 complete (Models menu live with hierarchy + sort + filters)
- Phase 3 complete (bug triage done, P0+P1 fixed, P2 documented)
- Phase 4 complete (audit CSV generated, every MUST TRACE + DELEGATE ONLY function fixed, correlation IDs propagate)
- Phase 5 complete (check_tracing.py runs clean, test_universal_tracing.py passes)
- Phase 6-7 complete (coverage + tag pushed)

If audit reveals >50 untraced MUST TRACE functions, STOP and report — may need to split tracing work into 18.3.

If blocked on any step, STOP and report — do not push partial work.

---

## Appendix A — STOP Conditions

- Mypy errors (OR90) — STOP
- Coverage < 89% at close (OR77) — STOP
- Any "Command errored" uninvestigated (OR88) — STOP
- Skip any of the 22 close steps (OR92/OR96) — STOP
- Premature git tag before all steps pass (OR76) — STOP
- Disable production feature to make test pass (OR87) — STOP
- Audit reveals >50 untraced MUST TRACE functions — STOP, consider 18.3 split
- New function added during this plan that lacks tracing — STOP (OR98)
- AR check `check_tracing.py` fails — STOP
- **OR97 violation** — phase marked complete with sub-items silently dropped — STOP
- **OR98 violation** — function with side effects has no trace emit — STOP
- **OR99 violation** — user-initiated action emits trace with `correlation_id=None` — STOP
- **OR100 violation** — "already done" claim with no executed verification — STOP
- **OR101 violation** — test failures dismissed as "pre-existing" without per-failure documentation or authorization — STOP
- **OR103 violation** — CHANGELOG or commit message overstates shipped scope — STOP
- **OR104 violation** — HTML/CSS/JS edit without syntax/structure validation — STOP
- **OR106 violation** — web UI plan without browser smoke test step at `/close` — STOP

## Appendix B — Files to Modify

**Models menu (Phase 1-2):**
- `sovereignai/databases/huggingface/schema.py` — add org/family/model_version/quant_level/file_type/category/category_group columns + indexes
- `sovereignai/databases/huggingface/sync.py` — populate new fields during download/update
- `web/main.py` — new hierarchical catalog endpoint with lazy loading
- `web/templates/index.html` — four-level dropdown DOM, sortable table headers, filter sidebar
- `web/static/app.js` — dropdown rendering, lazy loading, sort toggle, search, filters, localStorage persistence
- `web/static/style.css` — dropdown styles, category badge colors (blue/green/orange/purple/gray), sort indicators

**Tracing (Phase 4-5):**
- `sovereignai/shared/correlation.py` (new) — context var + helpers
- `scripts/ar_checks/check_tracing.py` (new) — static enforcement
- `temp/tracing_audit.csv` (new, committed) — Phase 4 audit output
- All files identified by the audit (exact list depends on Phase 4.1)

**Bug fixes (Phase 3):**
- `temp/plan-18.2-bugs.md` (new, committed) — bug triage list
- Whatever files 18.1 leaves broken (unknown until triage)

**Tests:**
- `tests/web/test_models_hierarchical.py` (new)
- `tests/web/test_models_sort.py` (new)
- `tests/web/test_models_filter.py` (new)
- `tests/web/test_models_category_badge.py` (new)
- `tests/databases/test_huggingface_sync_parsing.py` (new)
- `tests/test_universal_tracing.py` (new)
- `tests/shared/test_correlation.py` (new)
- `tests/web/test_endpoint_tracing.py` (new)
- `tests/cli/test_cli_tracing.py` (new)
- `tests/adapters/test_adapter_tracing.py` (new)
- `tests/test_check_tracing.py` (new)

**Docs:**
- `AGENTS.md` — add OR97, OR98, OR99, OR100, OR101, OR102, OR103, OR104, OR105, OR106, OR107, OR108 (12 new rules per Appendix E)
- `LANDMINES.md` — add L49, L50, L51, L52, L53, L54, L55, L56, L57, L58, L59 (11 new landmines per Appendix E)
- `documents/plan-18.2-report.md` (new — close report with audit summary + bug fix summary + Models menu screenshots + Phase 0 carryover verification)

## Appendix C — Files NOT to Modify

- Any existing OR rule numbering — gaps are permanent (OR84). New rules OR97-OR108 introduced by this plan per Appendix E.
- Any existing landmine numbering — gaps are permanent (OR84). New landmines L49-L59 introduced by this plan per Appendix E.
- `documents/models-panel-design-reference.md` — locked spec
- `sovereignai/shared/trace_emitter.py` — already correct, do not refactor
- `sovereignai/shared/event_bus.py` — already correct, do not refactor
- Plan 18.1 in-flight work — this plan runs after 18.1 closes

## Appendix D — Tracing Exemption Criteria

A function is EXEMPT from OR97 if and only if one of:

1. **PURE** — body contains only: type annotations, return statements with no side effects, arithmetic/string ops, calls to other PURE functions. No file/network/DB I/O, no subprocess, no exceptions (except `NotImplementedError`), no mutations of non-local state.
2. **ABSTRACT** — body is `pass`, `...`, or `raise NotImplementedError`.
3. **DATACLASS_INIT** — auto-generated `__init__` of `@dataclass` or Pydantic model. Custom `__init__` with logic is NOT exempt.
4. **PROPERTY** — `@property` getter returning cached value or simple attribute access.
5. **DUNDER_PROTOCOL** — `__str__`, `__repr__`, `__eq__`, `__hash__`, `__len__`, etc. — protocol methods called implicitly by Python.

All other functions MUST TRACE. When in doubt, trace.

## Appendix E — New Governance Rules + Landmines (this plan introduces)

Sourced from a full audit of all 38 execution logs (`logs/execution-log-prompt-*.md`, 78,704 lines). Each rule maps to a concrete failure pattern that recurred across multiple prompts. All STOP-level rules become STOP conditions in Appendix A.

### New OR Rules

**OR97 — Plan deliverables must ship in full or be explicitly deferred per item.** A phase marked "complete" in the TODO list must have shipped every numbered sub-item in that phase. If any sub-item is deferred, it MUST be (a) listed by number in the execution log under "Deferred items" with a named target plan, (b) called out in the close-report `Notes` with the deferred sub-item numbers, and (c) appended to DEBT.md. A phase checkbox being ticked while ≥1 sub-item silently didn't ship is a STOP condition. **Source**: prompt-18.1 Phase 6 — 9 sub-items specified, only 6.1 shipped, 8 silently dropped including the entire provider CLI framework, all backend endpoints, and 11 of 12 required test files. Verified on disk: `sovereignai/services/` and `sovereignai/databases/` directories DO NOT EXIST. **STOP level**: YES. Maps to L49.

**OR98 — Universal Tracing Mandate.** Every function in the SovereignAI codebase that performs work — backend modules, web endpoints, CLI entry points, TUI commands, scripts, adapter manifests, skills — MUST emit at least one trace event per execution path that produces an observable side effect (HTTP response, file write, subprocess spawn, DB mutation, message dispatch, exception). Pure type definitions, pure dataclasses, and abstract method signatures are exempt per Appendix D. Functions that only delegate to other traced functions may emit a single DEBUG "entered X" event. Silent functions are a defect. **Source**: user mandate, plus pre-scan finding that 7 of 30 `sovereignai/` files have zero tracing and `web/main.py` has 24+ silent endpoint functions. **STOP level**: YES. Maps to L50.

**OR99 — Correlation ID Propagation.** Every trace event emitted in response to a user-initiated action (HTTP request, CLI invocation, scheduled task) MUST carry a correlation_id that propagates from the entry point through every downstream call. `correlation_id=None` is permitted only for background heartbeat events unrelated to any user action. **Source**: pre-scan found correlation IDs rarely threaded through call chains; most emits pass `None`. **STOP level**: YES.

**OR100 — "Already done" claims require executed verification.** Before declaring a plan step "already implemented" or "already complete" without making changes, the Executor MUST run a verification that proves the existing code behaves as the step requires — a test, a curl call, a script invocation, or a manual browser action with captured output. Reading code and concluding "lines X–Y already do this" is NOT verification. If verification cannot be produced, treat the step as not-done and implement it. **Source**: prompt-17.7 S1.1, S2, S3, S4 — four steps marked "already complete" via visual inspection. Zero code changes shipped. User's auth persistence + Ollama start button + download pipeline bugs persisted into 18.0 and 18.1. Also prompt-18.0 Phase 2.5 "SKIPPED - not reproducing" and Phase 2.6 "SKIPPED - works on 0.30.11" — both based on thin one-line verification. **STOP level**: YES. Maps to L51.

**OR101 — Test failures have no "pre-existing" exemption.** OR95 forbids the "pre-existing" exemption for mypy errors. The same prohibition applies to test failures: there is no "pre-existing test failure" exemption. If N tests fail at `/close`, STOP and either fix them, document each in DEBT.md with a target plan, or get explicit User authorization per item. Dismissing 32 failing tests as "pre-existing auth isolation issues" and pushing the tag anyway is a STOP condition. Coverage reported as "N/A (test failures prevented coverage run)" is itself a STOP condition. **Source**: prompt-17.1 (31 failed, Coverage: N/A), prompt-17.2 (32 failed, Coverage: N/A), prompt-16 (3 failed "pre-existing"), prompt-15.1 (3 failed "deferred"). **STOP level**: YES. Maps to L52.

**OR102 — Skipped tests must have a target-resolution plan and a max age.** A test marked `SKIPPED` must carry a `# TODO(prompt-N): reason` comment naming the target prompt that will un-skip it. A test that has been skipped for ≥3 consecutive prompts must either be (a) fixed and un-skipped, (b) deleted if the feature was descoped, or (c) escalated in the close report. The close report must list the count of chronically-skipped tests (≥3 prompts). Skipped tests do NOT count toward "tests pass" for OR18 purposes — report them separately as `N passed, M skipped (K chronic)`. **Source**: prompt-17.1 through 18.1 — same 12 tests skipped every prompt: `test_sse_stream_emits_events`, 3× `test_model_registry_*`, 3× `test_qlora_integration_*`, 3× `test_ar7_*` for cli/tui/phone. Stuck at 12 for 5+ prompts. **STOP level**: No (warn + escalate), unless chronic-skip count grows >15. Maps to L53.

**OR103 — CHANGELOG and commit messages must not claim scope that wasn't shipped.** The CHANGELOG entry and the commit message body must accurately describe what shipped. If Phase 6 of a plan shipped only the tab navigation (6.1) and not the registration framework (6.7) or backend endpoints (6.9), the CHANGELOG must say "Phase 6: Added Options panel tab navigation (framework + endpoints deferred to plan N)" — NOT "Phase 6: Restructured Options panel with three tabs (Model Services/Model Databases/Authentication)" which implies the full restructure. Overstating shipped scope in CHANGELOG/commit is a STOP condition; the User relies on CHANGELOG to track what's actually in the codebase. **Source**: prompt-18.1 commit `d658439` claims "Phase 6: Restructured Options panel with three tabs" but only tab nav shipped. prompt-17.7 CHANGELOG: "All planned fixes (S1-S4) were already implemented in the codebase" — false. **STOP level**: YES. Maps to L54.

**OR104 — HTML/CSS/JS edits require a syntax/structure validation step before tests.** After any edit to `web/templates/*.html`, run `python -c "from html.parser import HTMLParser; HTMLParser().feed(open('<file>').read())"` (or equivalent HTML lint) and verify no parse errors. After any edit to `web/static/app.js`, run `node --check web/static/app.js`. After any edit to `web/static/style.css`, run a CSS lint (e.g. `python -c "import tinycss2; list(tinycss2.parse_stylesheet(open('<file>').read()))"`). Failures are STOP per OR6's pattern (syntax check before tests). **Source**: prompt-18.1.1 — duplicate `class="options-tab" class="active"` on line 116 of `index.html` broke tab click handlers. Shipped in 18.1, passed all tests, only caught when User tried to click tabs in browser. The 18.1 test `test_web_ui_panels.py::test_logs_panel_controls_exist` PASSED but didn't catch the malformed HTML. **STOP level**: YES. Maps to L55.

**OR105 — Tests must use real-shape fixtures, not simplified ones that hide production bugs.** When a test exercises a parser, deserializer, or any code that consumes external file formats (TOML manifests, JSON configs, GGUF metadata, HTTP responses), the test fixture MUST be the same shape as production data — not a simplified flat version. If the production format has nested tables, the fixture has nested tables. Tests with fixtures that diverge from production shape must include at least one integration test that loads a REAL production file from `adapters/internal/` or equivalent. **Source**: prompt-10.4 Bug 1 (CRITICAL) — manifest parser test fixtures used flat format, real manifests used `[component]` table format, tests passed but no real component registered. Same pattern in 18.1.1 (test asserted `tab` element exists, didn't assert it's clickable). **STOP level**: No (warn), unless divergence is found at `/scan` checkpoints. Maps to L56.

**OR106 — Web UI plans must include a browser smoke test step before `/close`.** Any plan that edits `web/templates/*.html`, `web/static/app.js`, or `web/static/style.css` MUST include an explicit "S{n}: Browser smoke test" step that: (a) starts the dev server, (b) loads the page in a headless browser (Playwright/Chrome DevTools Protocol) or via `curl` + JS evaluation, (c) verifies each new UI element is present AND interactive (clickable, visible, has expected text), (d) captures a screenshot or DOM snapshot to the execution log. "Manual verification available via browser preview" in the close report WITHOUT an actual smoke test is a STOP condition. **Source**: prompt-17 (Memory panel shipped as placeholder, never verified), prompt-18.1 (no browser smoke test; double-class bug shipped), prompt-10.4 (hotfix was created BECAUSE manual UI testing caught 3 bugs automated tests missed). **STOP level**: YES. Maps to L57.

**OR107 — Stray-file pre-commit scan in working directory.** Before every `git commit` (not just `/close`), after `git add -A`, run `git status -s` and visually inspect for files unrelated to the plan scope. Common culprits: `cookies.txt`, `*.cookies`, `*.json` in repo root not part of the plan, downloaded model files, screenshots, log files outside `logs/`. If found, `git reset HEAD <file>` and either move to `/tmp/` or `rm`. The close report must include a one-line "Working dir clean" confirmation. **Source**: prompt-18.1 — `cookies.txt` and `cookies2.txt` staged by `git add -A`; caught via `git status -s`. prompt-18.0 line 610 — `curl ... -c cookies2.txt` (regression from prompt-10.4/10.5's correct `-c /tmp/cookies.txt`). **STOP level**: No (warn — recoverable by reset+rm). Maps to L58.

**OR108 — Plan re-read required at the start of each phase, not just at plan start.** At the start of each numbered phase (Phase 1, Phase 2, …) or each numbered step (S1, S2, …), the Executor MUST re-read that phase/step's spec from the plan file before making any edits. The TODO-list checkbox is a coarse tracker, not a substitute for the plan spec. Citing line numbers from a cached mental model of the plan is a STOP condition. **Source**: prompt-18.1 — Executor re-read plan at Phase 4 (line 268) and Phase 6 (line 373), but did NOT re-read before marking Phase 6 "complete" (line 410). Phase 6 spec was 9 sub-sections (~150 lines); only 6.1 was implemented. prompt-17.7 — Executor cited "lines 747-756" and "lines 556-577" from cached memory; actual code didn't match spec. **STOP level**: No (warn). Maps to L59.

### New Landmines

**L49 — Phase marked "complete" with sub-items silently dropped.** Trigger: Executor ticks the TODO checkbox for a multi-sub-item phase after shipping only some sub-items, without listing the un-shipped sub-items in the close report or DEBT.md. Symptom: Plan claims done; CHANGELOG claims full phase shipped; User discovers missing functionality when testing. Repo state diverges from plan spec. Fix/Rule: OR97. Source: prompt-18.1 Phase 6.

**L50 — Silent function (no trace emit).** Trigger: A function with observable side effects (HTTP response, file I/O, subprocess, DB mutation, exception handler) ships without any `emit()` call. Symptom: User can't see what's happening in the Logs panel; bugs are impossible to diagnose from logs alone; "Ollama won't start" with no TRACE of what was tried. Fix/Rule: OR98. Source: pre-scan of `sovereignai/` (7 files with zero tracing) + `web/main.py` (24+ silent endpoint functions).

**L51 — "Already done" claim based on visual code inspection.** Trigger: Executor encounters a plan step that says "implement X", reads existing code, concludes "X is already present at lines A–B", marks step complete without running a test, curl, or browser action that proves the behavior. Symptom: Step marked complete; close report says "all planned fixes already implemented"; User's actual bug persists; next plan created to address same bug; cycle repeats. Fix/Rule: OR100. Source: prompt-17.7 S1.1, S2, S3, S4.

**L52 — "Pre-existing test failures" dismissal pattern.** Trigger: `/close` Step 1 pytest run shows N>0 failures; Executor dismisses them as "pre-existing auth isolation issues" or similar without either fixing them, documenting each in DEBT.md, or getting explicit per-failure User authorization. Symptom: Tag pushed with failing tests; "Coverage: N/A" in close report; OR18 silently violated; failures accumulate across prompts. Fix/Rule: OR101. Source: prompt-17.1 (31 failed), prompt-17.2 (32 failed), prompt-16 (3 failed), prompt-15.1 (3 failed).

**L53 — Chronic test skip with no resolution path.** Trigger: A test is marked `SKIPPED` for ≥3 consecutive prompts with no `# TODO(prompt-N): reason` comment, no target plan, no fix, no deletion. Symptom: Skipped tests become invisible debt; coverage % stays at 89% because skipped tests don't reduce coverage; real test rot is masked. Fix/Rule: OR102. Source: prompt-17.1 through 18.1 — same 12 tests skipped every prompt for 5+ prompts.

**L54 — CHANGELOG overstates shipped scope.** Trigger: Plan has a multi-part phase; only part ships; CHANGELOG entry describes the phase as if all parts shipped. Symptom: User reads CHANGELOG, believes feature X is implemented, plans next work assuming X exists; discovers mid-plan that X was never shipped; forced to either insert unplanned work or defer. Fix/Rule: OR103. Source: prompt-18.1 commit `d658439`, prompt-17.7 CHANGELOG.

**L55 — HTML duplicate attribute silently breaks event handlers.** Trigger: An Edit-tool operation on `index.html` produces an element with two `class=` attributes or two `id=` attributes. Browsers ignore the second attribute. JS event delegation that depends on the second class fails silently. Symptom: Tabs/buttons not clickable; CSS rules targeting the second class don't apply; tests that assert `element exists` PASS (element is in DOM); only manual browser testing catches it. Fix/Rule: OR104. Source: prompt-18.1.1 — `class="options-tab" data-tab="services" class="active"` shipped in 18.1, broke all Options tab click handlers, fixed in 18.1.1.

**L56 — Test fixtures diverge from production data shape.** Trigger: A test for a parser/deserializer uses a simplified fixture while production consumes a richer format. Symptom: All tests pass; production breaks; bug only caught by manual testing or User report. Hotfix plan required. Fix/Rule: OR105. Source: prompt-10.4 Bug 1 (CRITICAL) — manifest parser fixtures used flat format, real manifests used `[component]` table format.

**L57 — Manual verification deferred to browser never actually performed.** Trigger: Plan ships UI changes; Executor writes "manual verification is available via the browser preview" in the close report without actually loading the page or capturing any output. Symptom: UI bugs ship; User discovers them on next session; trust in close-report claims erodes. Fix/Rule: OR106. Source: prompt-17 (Memory panel placeholder, never verified), prompt-18.1 (no browser smoke test; double-class bug shipped).

**L58 — Stray curl/test artifacts in repo root staged by `git add -A`.** Trigger: Manual curl testing of web API writes cookie files or downloaded payloads to working directory instead of `/tmp/`. `git add -A` stages them. Symptom: Stray files appear in `git status -s`; if not caught, they get committed and pushed. Fix/Rule: OR107. Source: prompt-18.1 lines 1853-1854 — `cookies.txt` and `cookies2.txt` staged.

**L59 — Cached mental model of plan drifts from spec mid-execution.** Trigger: Executor starts a phase, relies on cached memory of the plan spec rather than re-reading the file, makes edits based on the cached (possibly stale) model. Symptom: Sub-items silently dropped; phase marked complete based on what Executor remembers rather than what plan says; scope contraction. Fix/Rule: OR108. Source: prompt-18.1 Phase 6 — Executor didn't re-read before marking complete; 8 of 9 sub-items silently dropped.

End of Plan 18.2 draft.
