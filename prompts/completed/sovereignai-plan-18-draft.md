# SovereignAI — Plan 18: prompt-18.0 — Web UI Polish + Download Pipeline Fix

## Context

prompt-17.6 shipped the 9-panel web UI but testing surfaced 9 concrete issues across the log drawer, Ollama integration, model metadata, auth persistence, and download pipeline. This plan addresses all 9 in a single batch per OR86 (backend + UI in same plan).

Key correction from earlier discussion: do NOT write compatibility shims for old Ollama. Update the environment first, then fix code only where latest still breaks.

## Plan Body

### Phase 1 — Environment + Diagnostics (do this FIRST, before any code)

**1.1 Update Ollama on the test machine to latest stable**
- Stop any running `ollama serve` processes
- Update via `winget upgrade Ollama.Ollama` (or download installer from ollama.com if winget unavailable)
- Verify: `ollama --version` shows the latest stable (capture the exact version string in the close report)
- Start `ollama serve` and confirm `GET http://localhost:11434/api/tags` returns 200

**1.2 Capture full download-pipeline failure**
- The 17.6 log shows: download reached 100% (1913MB), then `ollama create failed:` with the error truncated mid-line
- Re-run the same pull via the UI: `hf.co/lmstudio-community/gemma-4-E4B-it-GGUF:Q4_K_M`
- Capture the **full** error message from the `[models] ollama create failed:` line onward — do not truncate
- If `ollama create` succeeds on latest Ollama → close out item E.8, no code change needed
- If it still fails → record the full error and proceed to Phase 2 item 2.6 with the real root cause in hand

**1.3 Reproduce auth.json wipe**
- Before backend restart: `dir settings\auth.json` and record timestamp + size
- Restart backend (Options panel → Restart Backend button)
- After restart: `dir settings\auth.json` again — record new timestamp + size
- If timestamp changed or file is empty/missing → that's the bug, proceed to 2.5
- If file is intact but login still not persisted → bug is in `_load_users()` on startup, not in save. Capture which.
- Check `tests/conftest.py` `fresh_auth` fixture: confirm it does NOT touch the real `settings/auth.json`. If it does, that's the leak — fix per 2.5.

### Phase 2 — Code Fixes

**2.1 Log drawer — add close/toggle button**
- File: `web/templates/index.html`, `web/static/app.js`
- Add a visible close button (× icon) in the top-right of the log drawer header
- Clicking it collapses the drawer to a thin strip showing only "Logs" + a re-open chevron
- Re-open chevron expands it back to default height
- Persist open/closed state in `localStorage` so it survives page refresh

**2.2 Log drawer — drag-to-resize**
- Add a drag handle on the top edge of the log drawer
- Mouse-drag the handle to resize vertically between 80px and 60% of viewport height
- Persist height in `localStorage` so it survives refresh
- Touch-drag optional, not required for v1

**2.3 Load More Models button — verify rendering**
- The button was added in 17.6 JS but isn't appearing in the UI
- Likely cause: log drawer overlaying the Models panel content, OR the button only renders after pagination triggers and pagination never fires
- Diagnose in browser dev tools: is the button in the DOM but hidden? Is it never injected?
- Fix so it appears at the bottom of the HuggingFace catalog list when more pages exist
- Clicking loads the next page and appends to the list

**2.4 Ollama status panel — live status + Start button**
- File: `web/templates/index.html`, `web/static/app.js`, `web/main.py`
- Replace the static "Host: http://localhost:11434 / Ensure Ollama is running: ollama serve" text with a status block:
  - Green dot + "Running (vX.Y.Z)" when `GET /api/tags` returns 200 — version from `GET /api/version`
  - Red dot + "Not running" when connection refused
  - Button: "Start ollama serve" — visible only when status is down. Clicking POSTs to a new endpoint `POST /api/ollama/start` which spawns `ollama serve` as a subprocess and polls `/api/tags` for up to 10s. On success, refresh status to green. On timeout, show error in the status block.
- Status auto-refreshes every 10s via the existing SSE or a simple setInterval
- The Start button MUST run on Windows (subprocess with `creationflags=DETACHED_PROCESS` or equivalent — verify what works on the test machine)

**2.5 Auth persistence — fix `settings/auth.json` wipe**
- File: `sovereignai/shared/auth.py`, `tests/conftest.py`
- Based on Phase 1.3 findings: either fix `_save_users()` not being called on register, OR fix `_load_users()` failing silently on startup, OR fix conftest fixture leak
- Confirm: after register → restart → login state preserved
- conftest.py `fresh_auth` fixture MUST use a temp dir, never touch real `settings/auth.json`. Add an assertion at fixture teardown that real auth.json mtime is unchanged.

**2.6 Download pipeline — fix `ollama create` if Phase 1.2 shows it still fails on latest**
- File: `sovereignai/.../models_or_hf_catalog.py` (wherever the `ollama create` invocation lives)
- Use the full error from 1.2 to diagnose. Common causes on latest Ollama:
  - Wrong GGUF path passed to `ollama create`
  - Modelfile syntax wrong
  - Quant tag format mismatch
- If `ollama create` is the wrong API, switch to `ollama pull hf.co/<repo>:<quant>` directly (newer Ollama supports this natively — no separate download step)
- Whichever path: log every step to the trace bus so the user can see "downloading X% → importing to Ollama → ready"

**2.7 Download destination — surface in UI**
- File: `web/static/app.js`, `web/templates/index.html`
- During an active download, show the destination path: "Downloading to: C:\Users\...\downloads\<file>.gguf"
- After download completes: show "Stored at: C:\Users\<you>\.ollama\models\..." (Ollama's final path) if `ollama create` succeeded
- Add a Settings → Storage section showing both paths (SovereignAI cache dir + Ollama models dir) with a "Reveal in Explorer" button on Windows

**2.8 VRAM badges — implement per spec**
- File: `web/static/app.js`, `web/templates/index.html`, `web/main.py`
- Reference: `documents/models-panel-design-reference.md` (locked spec)
- For each model in the HuggingFace catalog, compute a badge:
  - **VRAM** — model size ≤ detected VRAM (fits fully in GPU)
  - **VRAM+RAM** — model size > VRAM but ≤ VRAM+RAM (split offload)
  - **Diskspace** — model size > VRAM+RAM (only fits on disk, will be slow)
  - **N/A** — VRAM not detected (no GPU or detection failed)
- Get VRAM from the Hardware panel's existing detection (extend if needed — Vulkan/CUDA probe)
- Badge appears next to each model's size in the catalog list
- Color: green (VRAM), amber (VRAM+RAM), red (Diskspace), gray (N/A)

### Phase 3 — Tests + Coverage

**3.1 New tests required**
- `tests/web/test_ollama_status.py` — mock `GET /api/tags`, verify green/red states, verify Start button endpoint
- `tests/web/test_auth_persistence.py` — register user, restart backend (call `_load_users()` again), verify user still present
- `tests/web/test_vram_badge.py` — given model size + VRAM, verify correct badge computation
- `tests/web/test_log_drawer_state.py` — verify localStorage persistence of open/closed + height (if testable without browser; skip if not)
- All existing tests must still pass

**3.2 Coverage floor**
- OR77 applies: coverage ≥ 89% at `/close`. Target ~91%.
- Run: `pytest --cov=sovereignai --cov=web --cov-report=term-missing`
- If below 89%, add tests — do not disable production features to game coverage (OR87)

### Phase 4 — Close Workflow

- Follow `.devin/workflows/close.md` — ALL 22 steps, no skipping (OR92/OR96)
- Step 17: `git add -A` (NOT `git rm` — L40 fix)
- Commit per OR75/OR80/OR83: `git add -A` for every commit, no exceptions
- Tag: `prompt-18.0` — only after all 22 steps pass (OR76)
- Mypy: clean, no errors. OR90 = STOP if any. No "pre-existing" exemption.
- Investigate every "Command errored" output (OR88)

## Closing

This plan fixes the 9 known issues from prompt-17.6 testing in one batch. Phase 1 (env + diagnostics) MUST run before any code changes — the Ollama update alone may resolve the download pipeline failure, and the auth.json reproduction determines which code path to fix. Phase 2 implements the UI fixes and code fixes informed by Phase 1. Phase 3 enforces the coverage floor. Phase 4 closes per the standard 22-step workflow.

If Phase 1.2 shows `ollama create` works on latest Ollama, skip 2.6 and note it in the close report. If Phase 1.3 shows auth.json is being wiped by conftest, the fix is in `tests/conftest.py` not `auth.py` — note that in the close report.

Report back when:
- Phase 1 complete (with findings on Ollama version, full create error, auth.json reproduction)
- Phase 2 complete (with screenshots of the new log drawer, Ollama status panel, VRAM badges)
- Phase 3 complete (coverage number + test count)
- Phase 4 complete (tag pushed)

If blocked on any step, STOP and report — do not push partial work.

---

## Appendix A — STOP Conditions

- Mypy errors (OR90) — STOP, no exemption
- Coverage < 89% at close (OR77) — STOP, add tests
- Any "Command errored" uninvestigated (OR88) — STOP, investigate
- conftest fixture touching real `settings/auth.json` — STOP, fix isolation
- Skip any of the 22 close steps (OR92/OR96) — STOP, run all steps
- Premature git tag before all steps pass (OR76) — STOP
- Disable production feature to make test pass (OR87) — STOP

## Appendix B — Files to Modify

**Backend:**
- `sovereignai/shared/auth.py` — auth persistence fix (if 1.3 points here)
- `sovereignai/.../models_or_hf_catalog.py` — `ollama create` fix (if 1.2 points here)
- `web/main.py` — new endpoint `POST /api/ollama/start`, VRAM detection, Ollama status endpoint
- `tests/conftest.py` — `fresh_auth` fixture isolation fix (if 1.3 points here)

**Frontend:**
- `web/templates/index.html` — log drawer close button, drag handle, Ollama status block, download path display, Settings → Storage section
- `web/static/app.js` — log drawer state, drag-resize, Load More button rendering, Ollama status polling + Start button, VRAM badge rendering, download path display

**Tests:**
- `tests/web/test_ollama_status.py` (new)
- `tests/web/test_auth_persistence.py` (new)
- `tests/web/test_vram_badge.py` (new)
- `tests/web/test_log_drawer_state.py` (new, if browser-testable)

**Docs:**
- `documents/plan-18-report.md` (new — close report with Phase 1 findings + screenshots references)

## Appendix C — Files NOT to Modify

- Any existing OR rule numbering — gaps are permanent (OR84)
- Any existing landmine numbering — gaps are permanent (OR84)
- `documents/models-panel-design-reference.md` — locked spec, do not edit
- Other department specs — out of scope for this plan
