# SovereignAI — Plan 18.3: Full Repair + HF Scraper + Missing Rules

## Context

Plan 18.2 shipped with `prompt-18.2` tag despite:
- 46 failing tests (dismissed as "pre-existing TraceLevel imports")
- Coverage reported as N/A (violates OR77)
- HF sync.py is a placeholder with `# TODO: Fetch actual data from HuggingFace API` — zero HTTP calls, zero rows in DB
- Ollama `start()` spawns a second instance without checking if one is already running (causes "bind: Only one usage of each socket address" error)
- Option button endpoints emit traces only on exception, not on success (violates the tracing mandate Devin just added)
- 30 of 45 tracing violations unfixed; `check_tracing.py` AR check would fail
- Devin dropped 6 critical rules from Plan 18.2's spec when adding to AGENTS.md (the rules that would have prevented these failures)

User reverted the attempted 18.2.1 hotfix. Plan 18.3 absorbs everything: the HF scraper implementation, the test fixes, the Ollama start fix, the missing rules, the tracing completion, and the UI stub fixes.

### Pre-scan: Rules Devin dropped from Plan 18.2

Plan 18.2 Appendix E specified 12 new rules (OR97-OR108). Devin added only 6 of them to AGENTS.md, renumbered, and dropped 6 critical ones:

| Plan 18.2 spec | Devin's AGENTS.md | Status |
|----------------|-------------------|--------|
| OR97 — Plan deliverables must ship in full | (not added) | **DROPPED** — would have caught 18.2 shipping with placeholder sync.py |
| OR98 — Universal Tracing Mandate | OR97 (renumbered) | Added |
| OR99 — Correlation ID Propagation | OR98-OR100 (split into 3) | Added |
| OR100 — "Already done" claims require executed verification | (not added) | **DROPPED** — would have caught "Phase 6 complete" with 1 of 9 sub-items |
| OR101 — Test failures have no "pre-existing" exemption | (not added) | **DROPPED** — Devin then violated this by shipping with 46 failures |
| OR102 — Skipped tests need target-resolution plan | (not added) | **DROPPED** |
| OR103 — CHANGELOG must not claim unshipped scope | (not added) | **DROPPED** — commit message claims "Models Menu Restructure + Universal Tracing" shipped |
| OR104 — HTML/CSS/JS syntax validation before tests | (not added) | **DROPPED** — would have caught the Python docstrings in app.js |
| OR105 — Tests must use real-shape fixtures | (not added) | **DROPPED** |
| OR106 — Web UI plans require browser smoke test | (not added) | **DROPPED** — would have caught unclickable tabs |
| OR107 — Stray-file pre-commit scan | (not added) | **DROPPED** |
| OR108 — Plan re-read at start of each phase | (not added) | **DROPPED** |
| (not in plan) | OR101-OR106 (tracing sub-rules) | Added (narrower than plan) |
| (not in plan) | OR107-OR108 (meta-rules about enforcement tools) | Added |

The 6 dropped rules are exactly the ones that would have prevented the 18.1 and 18.2 failures. They must be re-added in 18.3 under OR109+ (OR97-OR108 are now taken by Devin's version).

## Plan Body

### Phase 1 — Fix the 46 failing tests (BLOCKER — must pass before any other work)

**1.1 Triage all 46 failures**
- Run full test suite, capture every failure with: test name, error type, error message, file:line
- Output: `temp/plan-18.3-test-triage.md` (committed)
- Classify each failure:
  - **TraceLevel import errors** — `NameError: name 'TraceLevel' is not defined` in `sovereignai/versioning/negotiator.py`, `sovereignai/main.py`, test files. Fix: add missing `from sovereignai.shared.trace_emitter import TraceLevel` imports.
  - **AR7 violations** — `web/hardware_probe.py` imports `sovereignai.shared.trace_emitter`. Per AR7, UI must not import core. Fix: either move the import behind a function boundary (lazy import) OR refactor hardware_probe to receive trace via DI OR add hardware_probe to AR7 allowlist with justification.
  - **TestClient SSE issues** — `test_sse_stream_emits_events` skipped chronically. Per OR112 (new, Phase 3), either fix or document with target plan.
  - **Windows file lock** — `test_ensure_latest_schema` PermissionError on tmp models.db. Fix: ensure `conn.close()` is called in finally block, or use `:memory:` SQLite for tests.
  - **Correlation ID thread test** — `AttributeError: '_thread._local' object has no attribute 'captured_id'`. Fix: initialize the thread-local attribute in `__init__` or use `getattr` with default.
  - **Composition root failures** — cascade from TraceLevel import errors. Fixed by 1.1 above.
  - **Hierarchical catalog test failures** — `AttributeError: 'State' object has no attribute 'container'`. Fix: test setup must initialize `app.state.container` via `build_container()` in fixture.
  - **Schema migration test** — `assert "org" in columns` fails because `ensure_latest_schema` doesn't actually migrate. Fix: implement the migration OR fix the test to match actual behavior.
  - **Other** — investigate each per OR88 (no uninvestigated "Command errored").

**1.2 Fix each failure**
- One commit per failure class (not one commit per test — group by root cause)
- Each fix MUST emit traces per OR97 (Devin's version) — verify the fix itself is traced
- After each fix, re-run the affected test to confirm it passes
- Do NOT mark the triage item complete until the test passes AND stays passing after a full suite run

**1.3 Verify full suite passes**
- Run: `pytest tests/ -vvv --cov=. --cov-report=term-missing`
- Required: 0 failures, 0 errors, coverage ≥ 89% (OR77)
- If any test is skipped, it MUST have a `# TODO(prompt-N): reason` comment per new OR112 (Phase 3)
- If coverage < 89%, add tests — do not disable production features (OR87)

### Phase 2 — Implement the HF scraper (the placeholder must go)

**2.1 Replace sync.py placeholder with real implementation**
- File: `sovereignai/databases/huggingface/sync.py`
- Current state (lines 71-77):
  ```python
  # In a real implementation, this would fetch from HuggingFace API
  # For now, create empty database with schema
  ...
  # TODO: Fetch actual data from HuggingFace API
  # This is a placeholder for the actual sync logic
  ```
- Required implementation:
  - Use `requests` or `httpx` to call HuggingFace API: `GET https://huggingface.co/api/models?library=gguf&full=true&limit=100&offset=N`
  - Paginate through all results (HF returns ~100 per page)
  - For each model: fetch `config.json` for architecture/params/context, parse GGUF filename for quant tag
  - Populate all DB fields: `repo_id`, `org`, `family`, `model_version`, `quantization`, `quant_level`, `filename`, `file_size_bytes`, `file_size_gb`, `context_length`, `license`, `downloads`, `likes`, `last_modified`, `tags`, `vram_required_gb`, `active_bytes_gb`, `file_type`, `category`, `category_group`, `architecture`, `base_parameter_count`, `sync_timestamp`
  - Use the architecture→family, quant→level, category→group mappings already defined in `__init__`
  - Respect HF rate limits: 1 request/sec anonymous, faster with API token
  - Read HF API token from `settings/config.json` if present (anonymous if absent)
- All fetch activity logged at DEBUG with source `[huggingface_sync]` — every page fetched, every model parsed, every error
- On completion: emit INFO "Synced N models in M seconds"

**2.2 Implement `update()` for incremental sync**
- Compare `last_modified` from HF API with DB; only update changed rows
- Don't re-fetch models that haven't changed
- Log: "Found N changed models, updating..."

**2.3 Implement `uninstall()`**
- Delete the DB file
- Clear HF token from `settings/config.json` (with user confirmation)
- Log: "HuggingFace database uninstalled, N models removed"

**2.4 Test the scraper**
- New test: `tests/databases/test_huggingface_sync_real.py`
- Mock HF API responses (don't hit real API in tests)
- Verify: scraper populates DB with correct fields, pagination works, rate limiting works, error handling works
- Integration test (optional, manual): run `python -m sovereignai.databases.huggingface.cli download` against real HF API, verify DB has thousands of rows

**2.5 Verify dropdown populates**
- After scraper runs, the Models panel HuggingFace tab should show real orgs (google, meta-llama, mistralai, etc.)
- Clicking an org should expand to show families (gemma, llama, mistral, etc.)
- Clicking a family should expand to show model versions (gemma-2, llama-3.1, etc.)
- Clicking a model version should expand to show quant variants (Q4_K_M, Q5_K_M, Q8_0, F16)
- Capture screenshot for close report per OR115

### Phase 3 — Fix Ollama start() to check if already running

**3.1 Add pre-flight check to OllamaService.start()**
- File: `sovereignai/services/ollama/service.py`
- Before spawning `ollama serve`, call `GET http://localhost:11434/api/tags`
- If 200: emit INFO "Ollama already running on port 11434, skipping spawn", return success without spawning
- If connection refused: proceed with spawn (current behavior)
- If other status: emit WARN, proceed with spawn (defensive)
- This fixes the user-reported error: `Error: listen tcp 127.0.0.1:11434: bind: Only one usage of each socket address`

**3.2 Add pre-flight check to the web endpoint**
- File: `web/main.py` `/api/services/{service_name}/start` endpoint
- Same logic: check `/api/tags` first, if running return `{"success": True, "already_running": True}`, if not proceed with `service.start()`
- Emit INFO trace on success (currently only emits on exception — violates OR97/OR101 and new OR116)

**3.3 Test the fix**
- New test: `tests/services/test_ollama_start.py`
- Test 1: mock `/api/tags` returning 200, verify `start()` does NOT spawn subprocess, returns success
- Test 2: mock `/api/tags` connection refused, verify `start()` DOES spawn subprocess
- Test 3: mock subprocess spawn, verify it works end-to-end

### Phase 4 — Add missing governance rules (OR109+)

Devin dropped 6 critical rules from Plan 18.2. Re-add them under new numbers (OR97-OR108 are taken).

**4.1 OR109 — Plan deliverables must ship in full or be explicitly deferred per item**
- A phase marked "complete" must have shipped every numbered sub-item. Deferred items must be listed by number in the execution log + close report Notes + DEBT.md with a named target plan. Silently dropping sub-items = STOP.
- Source: prompt-18.1 Phase 6 (8 of 9 sub-items dropped), prompt-18.2 (sync.py shipped as placeholder, 30 of 45 tracing violations unfixed)
- STOP level: YES

**4.2 OR110 — "Already done" claims require executed verification**
- Before declaring a step "already complete" without changes, run a verification (test, curl, script, browser action). Reading code is NOT verification.
- Source: prompt-17.7 S1-S4 (all marked "already complete" via visual inspection, bugs persisted)
- STOP level: YES

**4.3 OR111 — Test failures have no "pre-existing" exemption**
- If N tests fail at `/close`, STOP and either fix them, document each in DEBT.md with a target plan, or get explicit User authorization per item. "Coverage: N/A" is itself a STOP condition.
- Source: prompt-17.1 (31 failed), prompt-17.2 (32 failed), prompt-18.2 (46 failed, Coverage: N/A)
- STOP level: YES

**4.4 OR112 — Skipped tests need target-resolution plan and max age**
- Skipped tests must carry `# TODO(prompt-N): reason`. Tests skipped for ≥3 consecutive prompts must be fixed, deleted, or escalated.
- Source: prompt-17.1 through 18.2 — 12 tests chronically skipped for 5+ prompts
- STOP level: No (warn + escalate if chronic count >15)

**4.5 OR113 — CHANGELOG and commit messages must not claim scope that wasn't shipped**
- If Phase 6 shipped only tab navigation, CHANGELOG must say "Phase 6: tab navigation (framework + endpoints deferred to plan N)" — NOT "Phase 6: Restructured Options panel"
- Source: prompt-18.1 commit `d658439`, prompt-18.2 commit `4973b70` (claims "Models Menu Restructure + Universal Tracing" shipped, but sync.py is a placeholder)
- STOP level: YES

**4.6 OR114 — HTML/CSS/JS syntax validation before tests**
- After any edit to `web/templates/*.html`: `python -c "from html.parser import HTMLParser; HTMLParser().feed(open('<file>').read())"`
- After any edit to `web/static/app.js`: `node --check web/static/app.js`
- After any edit to `web/static/style.css`: CSS lint (tinycss2 or equivalent)
- Failures are STOP per OR6's pattern
- Source: prompt-18.1 (Python docstrings in app.js lines 945, 962), prompt-18.1.1 (double class attribute in HTML)
- STOP level: YES

**4.7 OR115 — Web UI plans require browser smoke test before `/close`**
- Any plan editing HTML/CSS/JS MUST include a browser smoke test step: start dev server, load page, verify each new UI element is present AND interactive, capture screenshot/DOM snapshot to execution log
- "Manual verification available via browser preview" without actual verification = STOP
- Source: prompt-17 (Memory panel placeholder never verified), prompt-18.1 (double-class bug shipped), prompt-18.2 (options buttons don't update UI on success — stub `loadServicesStatus`)
- STOP level: YES

**4.8 OR116 — Option button success traces mandatory**
- Every web endpoint that performs an action (POST/PUT/DELETE) MUST emit an INFO trace on success, not just on exception. Currently `download_service_endpoint` only emits on error — success is silent, making it impossible to debug "did the button click do anything?" from the log.
- Source: prompt-18.2 — user reported "buttons don't produce any log"
- STOP level: YES

**4.9 OR117 — Placeholder code must not ship as "complete"**
- If a function contains `# TODO`, `# placeholder`, `# In a real implementation`, or similar markers indicating incomplete logic, the containing phase MUST NOT be marked complete. The TODO must be implemented or the phase must be explicitly deferred per OR109.
- Source: prompt-18.2 `sovereignai/databases/huggingface/sync.py` lines 71-77 — `# TODO: Fetch actual data from HuggingFace API` — shipped as "complete"
- STOP level: YES

**4.10 Update AGENTS.md + LANDMINES.md**
- Add OR109-OR117 to AGENTS.md
- Add L48-L56 (or next available numbers) to LANDMINES.md for each rule's failure pattern
- Each landmine: trigger, symptom, fix/rule mapping, source prompt

### Phase 5 — Finish the 30 unfixed tracing violations

**5.1 Re-run check_tracing.py**
- File: `scripts/ar_checks/check_tracing.py`
- Capture current violation count
- Output: `temp/plan-18.3-tracing-violations.md` (committed)

**5.2 Fix each violation**
- For each function `check_tracing.py` flags:
  - If MUST TRACE: add emit() call at entry (INFO) + exit (DEBUG)
  - If DELEGATE ONLY: add single DEBUG "entered X" emit
  - If PURE/ABSTRACT/exempt: add `# EXEMPT_<TYPE>: <reason>` comment so the auditor can be updated to skip it
- After each fix, re-run `check_tracing.py` to confirm violation count decreased
- Target: 0 violations (or all remaining are documented exemptions)

**5.3 Update check_tracing.py to recognize exemption comments**
- If a function has `# EXEMPT_PURE: <reason>` as its first body line, the auditor should skip it
- Same for `# EXEMPT_ABSTRACT`, `# EXEMPT_DATACLASS_INIT`, `# EXEMPT_PROPERTY`, `# EXEMPT_DUNDER`
- This lets legitimate exemptions be documented inline rather than silently ignored

**5.4 Add success traces to all action endpoints**
- File: `web/main.py`
- For every POST/PUT/DELETE endpoint: add INFO emit on success path (not just exception path)
- Per new OR116
- Verify in browser: click Download/Update/Uninstall, confirm trace appears in Logs panel

### Phase 6 — Fix stub status loaders

**6.1 Implement loadServicesStatus() and loadDatabasesStatus()**
- File: `web/static/app.js` lines 1106-1126
- Currently: `console.log(data)` — does nothing visible
- Replace with: update the status dot color + status text for each provider section based on the response
- Status dot rules (per Plan 18.2 spec):
  - Green = installed + running
  - Amber = installed but not running
  - Gray = not installed
  - Red = error
- Persist nothing (status is live, not cached)

**6.2 Verify options buttons update UI on success**
- After clicking Download: status dot should turn from gray → amber (installed but not running) or green (if service auto-starts)
- After clicking Start (Ollama): status dot should turn from amber → green
- After clicking Uninstall: status dot should turn from any → gray
- Capture before/after screenshots for the close report per OR115

### Phase 7 — Tests + Coverage

**7.1 New tests required**
- `tests/databases/test_huggingface_sync_real.py` — verify scraper populates DB with mocked HF API (Phase 2.4)
- `tests/services/test_ollama_start.py` — verify start() checks if already running (Phase 3.3)
- `tests/web/test_option_button_traces.py` — verify success traces emitted on Download/Update/Uninstall (OR116)
- `tests/web/test_options_status_ui.py` — verify loadServicesStatus updates the status dot (Phase 6)
- `tests/test_check_tracing_exemptions.py` — verify EXEMPT_ comments are recognized by the auditor (Phase 5.3)
- All existing tests must still pass (Phase 1 ensures this)

**7.2 Coverage floor**
- OR77 applies: coverage ≥ 89% at `/close`. Target ~91%.
- This plan's whole point is to get coverage back to measurable + passing. If still N/A at close, STOP.

### Phase 8 — Close Workflow

- Follow `.devin/workflows/close.md` — ALL 22 steps, no skipping (OR92/OR96)
- Step 17: `git add -A`. Must include `temp/plan-18.3-test-triage.md` and `temp/plan-18.3-tracing-violations.md`.
- Commit per OR75/OR80/OR83: `git add -A` for every commit
- Tag: `prompt-18.3` — only after all 22 steps pass (OR76)
- Mypy: clean. OR90 = STOP if any. No "pre-existing" exemption (OR95) — and now OR111 reinforces this for tests too.
- Investigate every "Command errored" output (OR88)
- AR checks must pass — including `check_tracing.py` (now with exemption support per Phase 5.3)
- **Browser smoke test MANDATORY** per new OR115 — capture screenshots of:
  - Models dropdown populated with real orgs after HF scraper runs
  - Options buttons clickable + status dots updating after click
  - Logs panel showing traces on button clicks (success path, not just errors)
  - Ollama Start button working without "bind: Only one usage" error

## Closing

This plan cleans up the mess from 18.2. Phase 1 fixes the 46 failing tests that should have blocked the tag. Phase 2 implements the HF scraper that 18.2 shipped as a placeholder. Phase 3 fixes the Ollama double-spawn. Phase 4 adds the 6 rules Devin dropped from Plan 18.2 plus 2 new rules surfaced by the 18.2 audit (OR116 success traces, OR117 no-placeholder-as-complete). Phase 5 finishes the tracing work 18.2 left half-done. Phase 6 fixes the stub status loaders that make option buttons feel broken.

The core lesson: adding rules to AGENTS.md is meaningless if you violate them in the same plan. 18.3 enforces this by making the rules STOP conditions AND by adding OR117 (no placeholders as complete) which would have caught the sync.py issue at 18.2 close.

**Do NOT push the tag if any test fails.** That's the entire point of this plan. OR111 (no pre-existing exemption) is now a STOP condition. If 46 tests fail at `/close`, STOP and fix them — do not dismiss as "pre-existing" and push.

Report back when:
- Phase 1 complete (0 test failures, coverage ≥ 89%)
- Phase 2 complete (HF scraper runs, DB populated with real models, dropdown shows orgs)
- Phase 3 complete (Ollama start verified to not double-spawn)
- Phase 4 complete (OR109-OR117 in AGENTS.md, L48-L56 in LANDMINES.md)
- Phase 5 complete (check_tracing.py reports 0 violations or all-exempted)
- Phase 6 complete (option buttons update UI on success, screenshots captured)
- Phase 7-8 complete (coverage + tag pushed, browser smoke test screenshots in execution log)

If blocked on any step, STOP and report — do not push partial work.

---

## Appendix A — STOP Conditions

- Mypy errors (OR90) — STOP
- Coverage < 89% or N/A at close (OR77) — STOP
- Any "Command errored" uninvestigated (OR88) — STOP
- Skip any of the 22 close steps (OR92/OR96) — STOP
- Premature git tag before all steps pass (OR76) — STOP
- Disable production feature to make test pass (OR87) — STOP
- New function added during this plan that lacks tracing — STOP (OR97)
- AR check `check_tracing.py` fails — STOP
- **Any test failure at `/close` (new OR111)** — STOP, no "pre-existing" exemption
- **Phase marked complete with sub-items silently dropped (new OR109)** — STOP
- **"Already done" claim without executed verification (new OR110)** — STOP
- **CHANGELOG/commit overstates shipped scope (new OR113)** — STOP
- **HTML/CSS/JS edit without syntax validation (new OR114)** — STOP
- **Web UI plan without browser smoke test at `/close` (new OR115)** — STOP
- **Action endpoint without success trace (new OR116)** — STOP
- **Placeholder code shipped as "complete" (new OR117)** — STOP

## Appendix B — Files to Modify

**Tests (Phase 1):**
- `sovereignai/versioning/negotiator.py` — add missing `TraceLevel` import
- `sovereignai/main.py` — add missing `TraceLevel` import
- `web/hardware_probe.py` — fix AR7 violation (lazy import or DI or allowlist)
- `sovereignai/shared/correlation.py` — fix thread-local attribute initialization
- `tests/databases/test_huggingface_schema.py` — fix Windows file lock (use `:memory:` or finally close)
- `tests/web/test_hierarchical_catalog.py` — fix `app.state.container` setup in fixture
- Other files as identified by triage in Phase 1.1

**HF scraper (Phase 2):**
- `sovereignai/databases/huggingface/sync.py` — replace placeholder with real implementation
- `tests/databases/test_huggingface_sync_real.py` (new)

**Ollama start fix (Phase 3):**
- `sovereignai/services/ollama/service.py` — add pre-flight check to `start()`
- `web/main.py` — add pre-flight check to `/api/services/{name}/start` endpoint
- `tests/services/test_ollama_start.py` (new)

**Governance rules (Phase 4):**
- `AGENTS.md` — add OR109-OR117
- `LANDMINES.md` — add L48-L56 (or next available)

**Tracing (Phase 5):**
- All files identified by `check_tracing.py` re-run (Phase 5.1)
- `scripts/ar_checks/check_tracing.py` — add exemption comment recognition (Phase 5.3)
- `web/main.py` — add success traces to all action endpoints (Phase 5.4)

**UI fixes (Phase 6):**
- `web/static/app.js` — implement `loadServicesStatus()` and `loadDatabasesStatus()` (currently stubs)

**Tests (Phase 7):**
- `tests/databases/test_huggingface_sync_real.py` (new)
- `tests/services/test_ollama_start.py` (new)
- `tests/web/test_option_button_traces.py` (new)
- `tests/web/test_options_status_ui.py` (new)
- `tests/test_check_tracing_exemptions.py` (new)

**Docs:**
- `temp/plan-18.3-test-triage.md` (new, committed) — Phase 1.1 output
- `temp/plan-18.3-tracing-violations.md` (new, committed) — Phase 5.1 output
- `documents/plan-18.3-report.md` (new) — close report with test pass count, coverage %, browser smoke test screenshots

## Appendix C — Files NOT to Modify

- Any existing OR rule numbering — gaps are permanent (OR84). OR97-OR108 are taken by Devin's 18.2; new rules start at OR109.
- Any existing landmine numbering — gaps are permanent. L1-L47 exist; new landmines start at L48.
- `documents/models-panel-design-reference.md` — locked spec
- `sovereignai/shared/trace_emitter.py` — already correct
- `sovereignai/shared/event_bus.py` — already correct

## Appendix D — New Governance Rules Summary (OR109-OR117)

| Rule | Title | STOP? | Source |
|------|-------|-------|--------|
| OR109 | Plan deliverables must ship in full or be explicitly deferred per item | YES | 18.1 Phase 6, 18.2 sync.py placeholder |
| OR110 | "Already done" claims require executed verification | YES | 17.7 S1-S4 |
| OR111 | Test failures have no "pre-existing" exemption | YES | 17.1, 17.2, 18.2 (46 failures) |
| OR112 | Skipped tests need target-resolution plan + max age | warn | 17.1-18.2 (12 chronic skips) |
| OR113 | CHANGELOG must not claim unshipped scope | YES | 18.1 commit d658439, 18.2 commit 4973b70 |
| OR114 | HTML/CSS/JS syntax validation before tests | YES | 18.1 Python docstrings in app.js |
| OR115 | Web UI plans require browser smoke test | YES | 17, 18.1, 18.2 (stub status loaders) |
| OR116 | Action endpoints must emit success traces | YES | 18.2 (options buttons silent on success) |
| OR117 | Placeholder code must not ship as "complete" | YES | 18.2 sync.py `# TODO: Fetch actual data` |

End of Plan 18.3.
