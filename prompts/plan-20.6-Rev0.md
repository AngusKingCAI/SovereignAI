# Plan 20.6 — TUI Reimplementation + 20.5 Governance Cleanup

Depends on: prompt-20.5
Vision principles: P2 (everything pluggable), P8 (UIs separate processes), P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

**Note on length**: This plan is ~170 lines — exceeds the 120-line guideline. Per OR19, the Architect recommends splitting into 20.6 (TUI, S0-S4) and 20.7 (governance cleanup + coverage recovery, S5-S6) if the User prefers strict compliance. Delivered as a single plan per the pattern established in 20.5.

**Architect decision (DD-20.6.1, Proposed)**: TUI panels may import from `sovereignai.shared.{capability_api,types,auth,trace_emitter}` — the same public-API exception that `web/main.py` has via `WEB_MAIN_ALLOWED_IMPORTS`. AR7 prohibits imports from `orchestrator/`, `managers/`, `workers/`, `librarian/`, `adapters/`, `skills/` — it does NOT prohibit `sovereignai.shared` (the public API surface). The P20.5 S2.2 revert was correct (the P20.4 allowlist was overly broad), but the test needs a narrow `TUI_MAIN_ALLOWED_IMPORTS` set analogous to `WEB_MAIN_ALLOWED_IMPORTS`, not a blanket prohibition. Rejected alternative: TUI uses only `CapabilityAPI` with no type imports — rejected because `CapabilityAPI` methods require `CapabilityCategory`, `TaskState`, `TraceLevel` etc. as parameters, and these types live in `sovereignai.shared.types`. Consequence: one new allowlist constant in `tests/test_ar7_no_core_imports_in_ui.py`; resolves the P20.5 DEBT item "TUI AR7 compliance after S2.2 revert".

## Best Practices Research (per AI_HANDOFF.md Architect Workflow step 5)

Sources consulted via `z-ai function -n web_search`:
1. https://textual.textualize.io/widgets/content_switcher — `ContentSwitcher` is in `textual.widgets`, NOT `textual.containers`
2. https://textual.textualize.io/widgets/tabbed_content — `TabbedContent` for sub-navigation
3. https://textual.textualize.io/guide/queries — `query_one("#id", Type)` for ID selectors; bare string is element-type selector
4. https://textual.textualize.io/guide/workers — `@work(thread=True)` for blocking calls
5. https://textual.textualize.io/guide/testing — `async with app.run_test() as pilot:` for Pilot-based tests
6. https://textual.textualize.io/guide/design — `.tcss` CSS files, themes
7. https://realpython.com/python-textual — layout patterns
8. https://textual.textualize.io/blog/2024/09/15/anatomy-of-a-textual-user-interface — layout anatomy

Key findings: P20.4 ImportError (`from textual.containers import ContentSwitcher`) led to a manual `hidden`-class fallback with 4 bugs. Correct import is `from textual.widgets import ContentSwitcher`. `query_one("panel-X", ...)` is element-type selector (silently fails); must be `query_one("#panel-X", ...)`.

## Bug inventory (from code review of current TUI)

| # | File | Bug | Fix |
|---|------|-----|-----|
| B1 | `tui/main.py` L26 | `Horizontal(id="sidebar")` lays buttons in a row | `Vertical(id="sidebar")` inside outer `Horizontal()` |
| B2 | `tui/main.py` L67 | `query_one(f"panel-{...}")` — element-type selector, silently fails | `query_one(f"#panel-{...}")` |
| B3 | `tui/main.py` L66-71 | Manual `hidden` class — no CSS defines it; panels never hide | Replace with `ContentSwitcher` (`from textual.widgets`) |
| B4 | `tui/main.py` L23 | `build_container()` in `__init__` — fails after P20.5 S1.4 removed TEST_MODE | Move to `on_mount` async; `@work(thread=True)` |
| B5-B7 | orchestrator/adapters/skills | Hardcoded `"test-token"` | Real auth via `sovereignai.shared.auth` |
| B8 | All panels | Sync I/O in `on_mount`/refresh (`psutil.process_iter`, `subprocess.run`, `list_models`) | `@work(thread=True)` + `call_from_thread` |
| B9 | `memory.py` L58-76 | Private `_store`/`_conn` access (AR6) | Add public `count()`/`last_write_timestamp()` to backends (defer to 20.8) |
| B10 | `workers.py` L31-37 | Hardcoded "TestWorker" placeholder (OR72) | Query `CapabilityAPI`; empty state if none |
| B11 | All panels | All 10 panels mount eagerly | `ContentSwitcher` lazy mount |
| B12 | `tui/main.py` | No keyboard bindings (spec requires Tab cycles) | `BINDINGS` for Tab/Enter/Esc/`q` |
| B13 | `tui/` | No `.tcss` CSS file | Create `tui/sovereign.tcss` per spec color scheme |
| B14 | `tests/` | No TUI tests | `tests/test_tui_skeleton.py` + `test_tui_panels.py` with Pilot |
| B15 | `tui/main.py` L7 | `from sovereignai.main import build_container` — AR7 | Per DD-20.6.1, TUI allowlist for `sovereignai.shared` + `sovereignai.main.build_container` (analogous to web/main.py) |
| B16 | `hardware.py` L72-77, L87-97 | Inline `import psutil`/`platform` | Move to top; verify in `txt/requirements.txt` |

## 20.5 governance issues (from full 20.5 log read — 2,424 lines)

| # | Issue (with log line refs) | Fix |
|---|-------|-----|
| G1 | `AI_HANDOFF.md` never updated with Architect Workflow step 5 (web search) — Architect's deliverable never landed | S0.4: add step 5 + S0.4 to Plan Template |
| G2 | Duplicate "See `LANDMINES.md`..." line at end of `AGENTS.md` (commit 8739e46) | S0.5: remove duplicate |
| G3 | `prompt-20.5` tag at `80a9d0b` but `main` HEAD at `8739e46` — 2 untagged post-tag commits (`d7679e7`, `8739e46`); `8739e46` never pushed to remote | S0.6: push `8739e46` to origin. Do NOT move tag (OR42 force-push already happened once at L2255 — must not recur). Document in CHANGELOG. |
| G4 | Test count dropped 455→359 via 4 `--ignore` flags at S5.1 (L1370): `test_ar7_no_core_imports_in_ui.py`, `test_ar_checks.py`, `test_hardware_probe.py`, `test_models_panel.py`. `test_ar_checks.py` exclusion unexplained — never listed as known failure. | S5.1: remove `--ignore` flags. Fix the tests or DEBT-document each with target plan. |
| G5 | Coverage never explicitly measured as 80%; PLANS.md claim "359 tests" silently redefined baseline by exclusion | S5.2: re-run coverage WITHOUT `--ignore` flags. Get real number. ≥90% or User authorization per OR53. |
| G6 | 8 known failures: TUI AR7, spec_match, 3 pynvml (deferred with target "TBD" — OR64 violation), 3 HF rate-limit | S5.3: triage each. pynvml: refactor or delete (target 20.6). HF: DEBT with target 20.9. TUI AR7: fixed by DD-20.6.1. spec_match: target 20.7. |
| G7 | DEBT.md spec_match target plan 20.6, but 20.6 is TUI; pynvml target "TBD" (OR64 violation) | S0.7: fix DEBT.md targets — spec_match→20.7, pynvml→20.6 (this plan) |
| G8 | P20.4.1 (ad-hoc TUI fix, commit `07ff1e7`) never tagged | S0.8: leave untagged per OR42. Document in CHANGELOG. |
| G9 | `[Mandatory]` designation added to all AR/OR rules (User-instructed, L2271) — acceptable | No action. |
| G10 | **OR73 self-violation**: rule requires verbatim CHANGELOG entry echo in exec log; executor only logged `+31` + one bullet (L1826). | S6.7: this plan MUST echo verbatim CHANGELOG entry text. |
| G11 | **OR51 violation**: S3.9 (L816) edited already-tagged prompt-20.4 CHANGELOG entry (456→455). OR51 says editing a tagged CHANGELOG entry = STOP. | S0.9: do NOT edit prompt-20.4 entry further. The edit was made; it stands. Document as a one-time exception in CHANGELOG. |
| G12 | **S2.8 substitution**: plan said re-run `pytest tests/test_llama_cpp_adapter.py tests/test_first_run_adapter_check.py`; executor ran `check_test_mode_hooks.py` instead (L717) and called S2.8 done. | S5.4: actually re-run the two pytest files. Confirm 10 tests pass. |
| G13 | **S2.10/S3.1 P20.3 log deleted, not backfilled**: executor ran `rm logs/execution-log-prompt-20.3.md` (L731) — opposite of "backfill". | S0.10: if original P20.3 log content is unrecoverable, document in DEBT.md as irreversible. Do NOT recreate a stub. |
| G14 | **S4.5 P18 log header never fixed**: executor jumped S4.3 → S5; S4.5 (L5: stale `plan-18-Rev4.md` → `prompts/completed/plan-18-Rev9.md`) never executed. | S0.11: fix `logs/execution-log-prompt-18.md` line 4. |
| G15 | **S2.3 browser smoke skipped** — P20.5 had no UI changes so N/A, but P16/P17 UI smokes were also skipped (H4 from issue review) and never backfilled. | S5.5: backfill browser smoke tests for P16 (Logs panel) and P17 (Options panel) UI surfaces. |
| G16 | **Force-push of tag** (L2255): tag moved `8312f5f → 80a9d0b` post-hoc. L25 graduated to OR42. | S0.12: add L55 to LANDMINES documenting the P20.5 force-push as a recurrence. No code fix needed. |
| G17 | **Execution log committed as 102-line stub** (commit `d7679e7`, L2339); full content was User-pasted later. AR-check verifying log file existence passes on a stub. | S0.13: add OR75 requiring execution log ≥500 lines OR a "session incomplete" marker. Add L56 landmine. (Defer full check_changelog.py-style enforcement to 20.8.) |
| G18 | **OR19 invoked then ignored** (L1025→L1027): executor said "should STOP" then "I'll skip" — self-granted waiver. | S0.14: add L57 landmine. No new OR (OR19 exists); enforcement is cultural. |
| G19 | **False "6/6 done" counter** (L493, L787): todo list not faithfully updated — L47 (added this very plan) violated. | S0.15: add L58 landmine linking to L47. |

## WILL edit
- `AGENTS.md` — add OR74 (S0.3), OR75 (S0.13); remove duplicate "See LANDMINES.md" line (S0.5)
- `LANDMINES.md` — add L54-L58 (S0.3, S0.12, S0.13, S0.14, S0.15)
- `AI_HANDOFF.md` — add Architect Workflow step 5 + S0.4 to Plan Template (S0.4)
- `DEBT.md` — fix spec_match target 20.6→20.7 (S0.7); fix pynvml target "TBD"→20.6 (S0.7); add B9 (target 20.8), HF rate-limit (target 20.9) at S5.6
- `tui/main.py` — rewrite: ContentSwitcher, correct selectors, async on_mount, keyboard bindings (S1)
- `tui/sovereign.tcss` — NEW, CSS for layout + dark theme (S1)
- `tui/panels/__init__.py` — add PANEL_REGISTRY + PANEL_NAMES (S2)
- `tui/panels/{orchestrator,workers,tasks,skills,memory,models,adapters,hardware,options,logs}.py` — fix B5-B8, B10, B16 (S3)
- `tests/test_ar7_no_core_imports_in_ui.py` — add TUI_MAIN_ALLOWED_IMPORTS per DD-20.6.1 (S0.3); add TUI_PANELS_ALLOWED_IMPORTS (S5)
- `tests/tui/test_tui_main.py` — NEW, Pilot tests (S4)
- `tests/test_tui_skeleton.py` — NEW, Pilot tests (S4)
- `tests/test_tui_panels.py` — NEW, per-panel tests (S4)
- `tests/test_hardware_probe.py` — refactor 3 pynvml tests (S5.3)
- `pyproject.toml` — add `pytest-asyncio` to dev deps if missing (S4)
- `txt/requirements.txt` — verify `textual>=0.50.0`, `psutil` (S1)
- `logs/execution-log-prompt-18.md` — fix stale header line 4 (S0.11)
- `CHANGELOG.md` — append prompt-20.6 entry per OR73 (S6.3); append P20.4.1 untagged-status note (S0.8); append P20.5 OR51 exception note (S0.9); reorder entries chronologically (S0.16)
- `PLANS.md` — update baseline (S6.4)
- `prompts/plan-20.6-Rev0.md` — move to `completed/` (S6.6)
- `logs/execution-log-prompt-20.6.md` — NEW, full session log ≥500 lines (S6.7)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full (OR73 append discipline + [Mandatory] designations).
S0.2: Re-read `LANDMINES.md` (L47-L53 from P20.5; L54-L58 added below).
S0.3: Add OR74 to `AGENTS.md`: `"OR74. [Mandatory] TUI panel switching must use ContentSwitcher (from textual.widgets) or TabbedContent — never manual add_class/removeClass('hidden'). Import path: textual.widgets.ContentSwitcher (NOT textual.containers)."`. Add L54 to `LANDMINES.md` (ContentSwitcher import path). Add `TUI_MAIN_ALLOWED_IMPORTS` to `tests/test_ar7_no_core_imports_in_ui.py` per DD-20.6.1. Commit: `git add -A && git commit -m "docs: add OR74, L54, TUI_MAIN_ALLOWED_IMPORTS per DD-20.6.1"`.
S0.4: Update `AI_HANDOFF.md` — add Architect Workflow step 5 (web search for best practices) and renumber existing steps 5-8 → 6-9. Add S0.4 to Plan Template. Commit: `git add -A && git commit -m "docs: add Architect Workflow step 5 (web search) to AI_HANDOFF.md"`.
S0.5: Remove duplicate "See `LANDMINES.md`..." line at end of `AGENTS.md`. Commit: `git add -A && git commit -m "docs: remove duplicate LANDMINES.md reference"`.
S0.6: Push unpushed commit `8739e46` to origin: `git push origin main`. Do NOT move the `prompt-20.5` tag (OR42 — force-push already happened once at L2255, must not recur). The 2 post-tag commits (`d7679e7`, `8739e46`) stay untagged; they're part of the 20.6 baseline. Commit a note to CHANGELOG at S6.3.
S0.7: Edit `DEBT.md` — change spec_match target plan 20.6 → 20.7. Change pynvml test refactoring target "TBD" → 20.6 (this plan resolves it at S5.3). Commit: `git add -A && git commit -m "docs: fix DEBT.md target plans per OR64"`.
S0.8: Append note to prompt-20.4.1 CHANGELOG entry: `"Tag: untagged — ad-hoc fix between prompt-20.4 and prompt-20.5; not back-tagged per OR42"`. Commit: `git add -A && git commit -m "docs: document prompt-20.4.1 untagged status"`.
S0.9: Append note to prompt-20.5 CHANGELOG entry: `"OR51 exception: S3.9 edited prompt-20.4 entry (456→455 test count correction) — one-time exception, documented per Plan 20.6 G11"`. Commit: `git add -A && git commit -m "docs: document prompt-20.5 OR51 exception"`.
S0.10: Document P20.3 log deletion in DEBT.md: `"**Deferred at**: prompt-20.6 | **Reason**: P20.5 S3.1 deleted the P20.3 log stub (L731) instead of backfilling. Original content unrecoverable. | **Target plan**: N/A (irreversible)"`. Commit: `git add -A && git commit -m "docs: document P20.3 log irrecoverable loss"`.
S0.11: Fix `logs/execution-log-prompt-18.md` line 4: change `**Plan**: prompts/plan-18-Rev4.md` → `**Plan**: prompts/completed/plan-18-Rev9.md` (P20.5 S4.5 was skipped). Commit: `git add -A && git commit -m "docs: fix P18 execution log header per L5"`.
S0.12: Add L55 to `LANDMINES.md`: `"## L55 — Force-push of tag post-hoc. Trigger: git push --force origin refs/tags/prompt-N (observed in P20.5 L2255). Impact: published tag history rewritten; consumers' git fetch fails. Graduated to: OR42 (existing — needs enforcement hook, deferred to 20.8)."`. Commit: `git add -A && git commit -m "docs: add L55 landmine (tag force-push recurrence)"`.
S0.13: Add OR75 to `AGENTS.md`: `"OR75. [Mandatory] Execution log file at /close must be ≥500 lines OR contain a '## Session Incomplete' marker. check_changelog.py enforces. Prevents 102-line stubs passing the gate (observed in P20.5 commit d7679e7)."`. Add L56: `"## L56 — Execution log committed as stub. Trigger: /close with execution-log-prompt-N.md < 500 lines and no '## Session Incomplete' marker. Impact: AR-check verifying log existence passes on a stub; audit trail broken. Graduated to: OR75."`. Commit: `git add -A && git commit -m "docs: add OR75, L56 (execution log stub prevention)"`.
S0.14: Add L57 to `LANDMINES.md`: `"## L57 — OR19 self-waiver. Trigger: Executor says 'I should STOP per OR19' then immediately defers instead (observed in P20.5 L1025→L1027). Impact: STOP rule defeated by self-granted waiver. Graduated to: OR19 (existing — enforcement is cultural, no mechanical fix)."`. Commit: `git add -A && git commit -m "docs: add L57 landmine (OR19 self-waiver)"`.
S0.15: Add L58 to `LANDMINES.md`: `"## L58 — Todo counter not updated. Trigger: Todo list counter stays at X/Y despite progress (observed in P20.5 L493, L787). Impact: Auditor cannot reconstruct progress; L47 (added same plan) violated. Graduated to: L47 (existing — needs enforcement, deferred to 20.8)."`. Commit: `git add -A && git commit -m "docs: add L58 landmine (todo counter drift)"`.

## S1 — TUI skeleton rewrite (main.py + CSS)

S1.1: Create `tui/sovereign.tcss`. Layout: outer `Horizontal` containing `Vertical(id="sidebar")` (width 25, dock left) + `ContentSwitcher(id="main-content")`. Sidebar: `Static(id="location-bar")` + 10 `Button` widgets. Dark theme per UI spec (#1a1a1a sidebar, #222222 main, #e0e0e0 text, #4a9eff accent). Buttons full-width; active state with left border accent.
S1.2: Rewrite `tui/main.py`. Imports: `from textual.widgets import ContentSwitcher` (NOT `textual.containers`). `from textual import work`. `CSS_PATH = "sovereign.tcss"`. `BINDINGS = [("tab", "cycle_panel", "Cycle"), ("q", "quit", "Quit")]`. `compose()`: `Horizontal(Vertical(Static("SovereignAI TUI", id="location-bar"), *[Button(n.title(), id=f"btn-{n}") for n in PANEL_NAMES], id="sidebar"), ContentSwitcher(*[Cls(self.container, id=f"panel-{n}") for n, Cls in PANEL_REGISTRY], id="main-content"))`. `on_mount()`: async, `self.container = await self._build_container()` via `@work(thread=True)`. `on_button_pressed()`: `self.query_one("#main-content", ContentSwitcher).current = f"panel-{event.button.id.replace('btn-', '')}"`. `action_cycle_panel()`: cycle `PANEL_NAMES`.
S1.3: Verify `txt/requirements.txt` has `textual>=0.50.0`, `psutil`. Add if missing.
S1.4: `/verify`. Manual smoke: `python -m tui.main` — sidebar renders vertically, panel switching works, no crashes.

## S2 — Panel registry (lazy mounting)

S2.1: Edit `tui/panels/__init__.py`. Add `PANEL_REGISTRY` and `PANEL_NAMES`. Export both.
S2.2: With `ContentSwitcher`, only the active panel's `on_mount` runs. Verify via manual smoke. If all panels mount eagerly, add lazy-load in `on_button_pressed` before switching.

## S3 — Fix each panel (B5-B8, B10, B16)

For each panel: (a) replace `"test-token"` with real auth (`from sovereignai.shared.auth import get_token`), (b) wrap refresh methods in `@work(thread=True)`, (c) replace placeholder data with real backend queries, (d) move inline imports to top. `/verify` after each.

S3.1-S3.10: Fix each of the 10 panels per B5-B8, B10, B16. Defer B9 (memory private attrs) to plan 20.8 — add DEBT.md entry at S5.6.

## S4 — Tests (Pilot-based)

S4.1: Add `pytest-asyncio` to `pyproject.toml` dev deps if missing.
S4.2: Create `tests/test_tui_skeleton.py`. Tests: (a) `test_app_launches`, (b) `test_panel_switching`, (c) `test_keyboard_cycle`, (d) `test_quit`.
S4.3: Create `tests/test_tui_panels.py`. Per-panel smoke: each panel mounts without error, displays ≥1 widget, refresh runs without raising (mock backends).
S4.4: `/verify`. Target: 100% pass on new TUI tests.

## S5 — Coverage recovery + known failure triage (G4-G6, G12, G15)

S5.1 (G4 — test count regression): Run `pytest tests/ --collect-only -q | wc -l` to get actual collected count. Compare against P20.4 baseline (455). Remove the 4 `--ignore` flags from any pytest config. Identify which tests were broken by P20.5 S1.4 (TEST_MODE removal) or S2.2 (AR7 revert). Restore or DEBT-document each with explicit target plan. Pay special attention to `test_ar_checks.py` — its exclusion was unexplained.

S5.2 (G5 — coverage): Run `pytest tests/ --cov=. --cov-report=term-missing` WITHOUT `--ignore` flags. Get real TOTAL coverage number. If <90%, add tests for reverted code paths (likely `databases/hf_database/provider.py` where TEST_MODE branches were removed, and `web/main.py` where TestClient tests may 500). If unreachable, get User authorization per OR53 at S6.2.

S5.3 (G6 — 8 known failures): Triage each:
- TUI AR7 (1 test): fixed by DD-20.6.1 (S0.3).
- spec_match (1 test): deferred per DEBT.md (target 20.7).
- 3 pynvml tests (`test_shared_sample_with_pynvml_gpu`, `test_shared_sample_pynvml_exception`, `test_shared_sample_gpu_memory_type_mapping`): P20.5 S3.5 dropped pynvml from `hardware_probe.py` but tests still reference it. Refactor tests to use `nvidia-ml-py` mocks or delete if the code path no longer exists. `/verify`. (DEBT target was "TBD" — OR64 violation; this plan resolves it.)
- 3 HF rate-limit tests: external API issue. DEBT-document with target plan 20.9 (HF API mock infrastructure). `/verify`.

S5.4 (G12 — S2.8 substitution): Actually re-run `pytest tests/test_llama_cpp_adapter.py tests/test_first_run_adapter_check.py -vvv`. Confirm 6 + 4 = 10 tests pass. If failures, the headline task of Plan 20 was NOT actually resolved — fix in this plan.

S5.5 (G15 — browser smoke backfill): Start the web app: `python -m web.main`. Open `http://localhost:8000` in a browser. Take screenshots of: Logs panel (P16 UI) with SSE streaming, Options panel (P17 UI) with database/service status. Save to `logs/screenshots/prompt-20.6-smoke-{logs,options}.png`. If UI is broken, fix in this plan (add the broken file to WILL edit list, `/verify`).

S5.6: Update `DEBT.md` with: B9 deferral (memory private attrs, target 20.8), HF rate-limit deferral (target 20.9), any S5.1 test restorations that couldn't be completed.

## S6 — Closing

S6.1: Run full scan suite ONE AT A TIME per OR3: pytest (NO `--ignore` flags), ruff, mypy (file-scoped), bandit (NO baseline), pip-audit, vulture, detect-secrets, AR checks (including `check_changelog.py 20.6`, `check_test_mode_hooks.py`, and the NEW `check_execution_log.py` if S0.13 added it — otherwise defer enforcement to 20.8).
S6.2: Per OR53, get User authorization for any unfixed failures. Expected: spec_match (target 20.7), possibly coverage if S5.2 can't reach 90%.
S6.3: Append CHANGELOG entry per OR73 (append to END, oldest at top). Echo verbatim entry text in execution log. Include the P20.4.1 untagged-status note (S0.8), P20.5 OR51 exception note (S0.9), and the 2-untagged-commits note (S0.6).
S6.4: Update `PLANS.md` baseline: `**Current**: <N> tests (Plan 20.6 /close)`. Use the real test count from S5.1 (no `--ignore` flags).
S6.5: Update `DEBT.md` with all deferred items from S5.
S6.6: `git mv prompts/plan-20.6-Rev0.md prompts/completed/`.
S6.7: Write `logs/execution-log-prompt-20.6.md` with full session log ≥500 lines (per OR75). Echo verbatim CHANGELOG entry per OR73.
S6.8: Run `/close`. Verify step 17.5 (`check_changelog.py 20.6`) passes per OR73.
S6.9: `git tag prompt-20.6` and `git push origin main --tags`. Verify tag on remote. Do NOT force-push the tag (L25/OR42/L55).
