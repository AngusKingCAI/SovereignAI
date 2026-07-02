# Plan 20.6 — TUI Reimplementation + 20.5 Governance Cleanup

Depends on: prompt-20.5
Vision principles: P2 (everything pluggable), P8 (UIs separate processes), P9 (trust boundary), P14 (audit everything)
Open questions resolved: none

**Note on length**: This plan is ~160 lines — exceeds the 120-line guideline. Per OR19, the Architect recommends splitting into 20.6 (TUI, S0-S4) and 20.7 (governance cleanup + coverage recovery, S5-S6) if the User prefers strict compliance. Delivered as a single plan per the pattern established in 20.5.

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

## 20.5 governance issues to roll in (verified against repo state)

| # | Issue | Fix |
|---|-------|-----|
| G1 | `AI_HANDOFF.md` never updated with Architect Workflow step 5 (web search for best practices) — the Architect's deliverable from the previous turn never landed | Add step 5 + S0.4 to Plan Template in S0.4 of this plan |
| G2 | Duplicate "See `LANDMINES.md`..." line at end of `AGENTS.md` (from commit 8739e46) | Remove the duplicate line in S0.5 |
| G3 | `prompt-20.5` tag at `80a9d0b` but `main` HEAD at `8739e46` — 2 post-tag commits (`d7679e7` [Mandatory] designation, `8739e46` mandate-all-future-rules) are untagged | Do NOT force-push tag (OR42). Acknowledge the 2 commits as part of 20.6 baseline. Document in CHANGELOG. |
| G4 | Test count dropped 455→359 (96 tests lost, unexplained) | S5.1: investigate. Likely tests broken by S1.4 (TEST_MODE removal) or S2.2 (AR7 revert). Restore or DEBT-document. |
| G5 | Coverage 80% (OR43 violation, below 90%) | S5.2: add tests for reverted code paths. If can't reach 90%, get User authorization per OR53. |
| G6 | 8 known failures (log lists 7 but I count 8): TUI AR7, spec_match, 3 pynvml, 3 HF rate-limit | S5.3: triage each. pynvml failures are from S3.5 dropping pynvml — refactor tests. HF rate-limit is external — DEBT-document. TUI AR7 fixed by DD-20.6.1. spec_match deferred per DEBT.md. |
| G7 | DEBT.md says spec_match target plan 20.6, but 20.6 is TUI | S0.6: update DEBT.md spec_match target to 20.7 (mypy remediation plan) |
| G8 | P20.4.1 (ad-hoc TUI fix) was never tagged — `git tag -l "prompt-20.4*"` only shows `prompt-20.4` | S0.7: decide whether to back-tag `prompt-20.4.1` at commit `07ff1e7` or leave untagged. Architect recommends leave untagged (it was ad-hoc; tagging now = L25 force-push risk). Document in CHANGELOG. |
| G9 | `[Mandatory]` designation added to all AR/OR rules (scope expansion not in Plan 20.5) | Acceptable change. OR14's "All rules are mandatory by default" sentence is fine. No action needed. |

## WILL edit
- `AGENTS.md` — add OR74 (S0.3); remove duplicate "See LANDMINES.md" line (S0.5)
- `LANDMINES.md` — add L54 (ContentSwitcher import path) (S0.3)
- `AI_HANDOFF.md` — add Architect Workflow step 5 (web search) + S0.4 to Plan Template (S0.4)
- `DEBT.md` — update spec_match target plan 20.6→20.7 (S0.6); add B9 deferral (target 20.8) at S5.4
- `tui/main.py` — rewrite: ContentSwitcher, correct selectors, async on_mount, keyboard bindings (S1)
- `tui/sovereign.tcss` — NEW, CSS for layout + dark theme (S1)
- `tui/panels/__init__.py` — add PANEL_REGISTRY + PANEL_NAMES (S2)
- `tui/panels/{orchestrator,workers,tasks,skills,memory,models,adapters,hardware,options,logs}.py` — fix B5-B8, B10, B16 (S3)
- `tests/test_ar7_no_core_imports_in_ui.py` — add TUI_MAIN_ALLOWED_IMPORTS per DD-20.6.1 (S0.3)
- `tests/test_tui_skeleton.py` — NEW, Pilot tests (S4)
- `tests/test_tui_panels.py` — NEW, per-panel tests (S4)
- `pyproject.toml` — add `pytest-asyncio` to dev deps if missing (S4)
- `txt/requirements.txt` — verify `textual>=0.50.0`, `psutil` (S1)
- `tests/test_hardware_probe.py` — refactor 3 pynvml tests (S5.3)
- `CHANGELOG.md` — append prompt-20.6 entry per OR73 (S6.3)
- `PLANS.md` — update baseline (S6.4)
- `prompts/plan-20.6-Rev0.md` — move to `completed/` (S6.6)
- `logs/execution-log-prompt-20.6.md` — NEW, full session log (S6.7)

## WILL NOT edit
- Any file not listed above. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full (now includes OR73 append discipline + [Mandatory] designations).
S0.2: Re-read `LANDMINES.md` (L47-L53 added in P20.5; L54 added in S0.3 below).
S0.3: Add OR74 to `AGENTS.md`: `"OR74. [Mandatory] TUI panel switching must use ContentSwitcher (from textual.widgets) or TabbedContent — never manual add_class/removeClass('hidden'). Import path: textual.widgets.ContentSwitcher (NOT textual.containers)."`. Add L54 to `LANDMINES.md`: `"## L54 — ContentSwitcher import path. Trigger: from textual.containers import ContentSwitcher. Impact: ImportError; executor falls back to manual class switching with multiple bugs (B1-B3, B11). Graduated to: OR74."`. Add `TUI_MAIN_ALLOWED_IMPORTS` to `tests/test_ar7_no_core_imports_in_ui.py` per DD-20.6.1 (mirror `WEB_MAIN_ALLOWED_IMPORTS` but for tui/main.py + tui/panels/). Commit: `git add -A && git commit -m "docs: add OR74, L54, TUI_MAIN_ALLOWED_IMPORTS per DD-20.6.1"`.
S0.4: Update `AI_HANDOFF.md` — add Architect Workflow step 5: "Web search for best practices (when implementing). Before drafting any plan that implements new functionality, run web searches for best practices. Use the web-search skill. Cite sources in the plan's S0 under `## Best Practices Research`. Pure governance/cleanup plans exempt." Add S0.4 to Plan Template: "S0.4: (If implementation plan) Web search for best practices per Architect Workflow step 5." Commit: `git add -A && git commit -m "docs: add Architect Workflow step 5 (web search) to AI_HANDOFF.md"`.
S0.5: Remove duplicate "See `LANDMINES.md`..." line at end of `AGENTS.md` (from commit 8739e46). Commit: `git add -A && git commit -m "docs: remove duplicate LANDMINES.md reference in AGENTS.md"`.
S0.6: Edit `DEBT.md` — change spec_match target plan from 20.6 to 20.7 (this plan is TUI; spec_match redesign moves to 20.7 alongside mypy remediation). Commit: `git add -A && git commit -m "docs: update DEBT.md spec_match target plan 20.6 → 20.7"`.
S0.7: Document P20.4.1 status in CHANGELOG (append a note to the prompt-20.4.1 entry: "Tag: untagged — ad-hoc fix between prompt-20.4 and prompt-20.5; not back-tagged per OR42"). Commit: `git add -A && git commit -m "docs: document prompt-20.4.1 untagged status"`.

## S1 — TUI skeleton rewrite (main.py + CSS)

S1.1: Create `tui/sovereign.tcss`. Layout: outer `Horizontal` containing `Vertical(id="sidebar")` (width 25, dock left) + `ContentSwitcher(id="main-content")`. Sidebar: `Static(id="location-bar")` + 10 `Button` widgets. Dark theme per UI spec (#1a1a1a sidebar, #222222 main, #e0e0e0 text, #4a9eff accent). Buttons full-width; active state with left border accent.
S1.2: Rewrite `tui/main.py`. Imports: `from textual.widgets import ContentSwitcher` (NOT `textual.containers`). `from textual import work`. `CSS_PATH = "sovereign.tcss"`. `BINDINGS = [("tab", "cycle_panel", "Cycle"), ("q", "quit", "Quit")]`. `compose()`: `Horizontal(Vertical(Static("SovereignAI TUI", id="location-bar"), *[Button(n.title(), id=f"btn-{n}") for n in PANEL_NAMES], id="sidebar"), ContentSwitcher(*[Cls(self.container, id=f"panel-{n}") for n, Cls in PANEL_REGISTRY], id="main-content"))`. `on_mount()`: async, `self.container = await self._build_container()` via `@work(thread=True)`. `on_button_pressed()`: `self.query_one("#main-content", ContentSwitcher).current = f"panel-{event.button.id.replace('btn-', '')}"`. `action_cycle_panel()`: cycle `PANEL_NAMES`.
S1.3: Verify `txt/requirements.txt` has `textual>=0.50.0`, `psutil`. Add if missing.
S1.4: `/verify`. Manual smoke: `python -m tui.main` — sidebar renders vertically, panel switching works, no crashes.

## S2 — Panel registry (lazy mounting)

S2.1: Edit `tui/panels/__init__.py`. Add `PANEL_REGISTRY = [("orchestrator", OrchestratorPanel), ...]` and `PANEL_NAMES = [n for n, _ in PANEL_REGISTRY]`. Export both.
S2.2: With `ContentSwitcher`, only the active panel's `on_mount` runs. Verify via manual smoke. If all panels mount eagerly, add lazy-load in `on_button_pressed` before switching.

## S3 — Fix each panel (B5-B8, B10, B16)

For each panel: (a) replace `"test-token"` with real auth (`from sovereignai.shared.auth import get_token`), (b) wrap refresh methods in `@work(thread=True)`, (c) replace placeholder data with real backend queries, (d) move inline imports to top. `/verify` after each.

S3.1-S3.10: Fix each of the 10 panels per B5-B8, B10, B16. Defer B9 (memory private attrs) to plan 20.8 — add DEBT.md entry at S5.4.

## S4 — Tests (Pilot-based)

S4.1: Add `pytest-asyncio` to `pyproject.toml` dev deps if missing.
S4.2: Create `tests/test_tui_skeleton.py`. Tests: (a) `test_app_launches` — `async with SovereignTUI().run_test() as pilot: assert pilot.app.query_one("#sidebar")`. (b) `test_panel_switching` — click each sidebar button, assert `ContentSwitcher.current` matches. (c) `test_keyboard_cycle` — press Tab, assert panel cycles. (d) `test_quit` — press `q`, assert app exits.
S4.3: Create `tests/test_tui_panels.py`. Per-panel smoke: each panel mounts without error, displays ≥1 widget, refresh runs without raising (mock backends).
S4.4: `/verify`. Target: 100% pass on new TUI tests.

## S5 — Coverage recovery + known failure triage (20.5 G4-G6)

S5.1 (G4 — test count regression): Investigate 455→359 drop. Run `pytest tests/ --collect-only -q | wc -l` to get actual collected count. Compare against P20.4 baseline. Identify which tests were broken by P20.5 S1.4 (TEST_MODE removal) or S2.2 (AR7 revert). Restore broken tests or DEBT-document with target plan.

S5.2 (G5 — coverage 80%): Run `pytest tests/ --cov=. --cov-report=term-missing`. Identify uncovered lines (likely in `databases/hf_database/provider.py` where TEST_MODE branches were removed, and `web/main.py` where TestClient tests may 500). Add tests to reach ≥90%. If unreachable, get User authorization per OR53 at S6.2.

S5.3 (G6 — 8 known failures): Triage each:
- TUI AR7 (1 test): fixed by DD-20.6.1 (S0.3).
- spec_match (1 test): deferred per DEBT.md (target 20.7).
- 3 pynvml tests: S3.5 dropped pynvml from `hardware_probe.py` but tests still reference it. Refactor tests to use `nvidia-ml-py` mocks or delete if the code path no longer exists. `/verify`.
- 3 HF rate-limit tests: external API issue. DEBT-document with target plan 20.9 (HF API mock infrastructure). `/verify`.

S5.4: Update `DEBT.md` with: B9 deferral (memory private attrs, target 20.8), HF rate-limit deferral (target 20.9), any S5.1 test restorations that couldn't be completed.

## S6 — Closing

S6.1: Run full scan suite ONE AT A TIME per OR3: pytest, ruff, mypy (file-scoped), bandit (NO baseline — P20.5 S2.6 removed it), pip-audit, vulture, detect-secrets, AR checks (including `check_changelog.py 20.6` and `check_test_mode_hooks.py`).
S6.2: Per OR53, get User authorization for any unfixed failures. Expected: spec_match (target 20.7), possibly coverage if S5.2 can't reach 90%.
S6.3: Append CHANGELOG entry per OR73 (append to END, oldest at top). Echo verbatim entry text in execution log.
S6.4: Update `PLANS.md` baseline: `**Current**: <N> tests (Plan 20.6 /close)`.
S6.5: Update `DEBT.md` with all deferred items from S5.
S6.6: `git mv prompts/plan-20.6-Rev0.md prompts/completed/`.
S6.7: Write `logs/execution-log-prompt-20.6.md` with full session log. Echo verbatim CHANGELOG entry per OR73.
S6.8: Run `/close`. Verify step 17.5 (`check_changelog.py 20.6`) passes per OR73.
S6.9: `git tag prompt-20.6` and `git push origin main --tags`. Verify tag on remote.
