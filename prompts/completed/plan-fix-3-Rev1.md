Depends on: plan-fix-2-Rev1
Vision principles: P3 (Reliability), P7 (Testability), P11 (Quality)
Open questions resolved: none

## S0 — Opening

S0.0: Clone latest repo. Verify plan-fix-2-Rev1 completed.
S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Check `.agent/executor/suggestions/` — confirm empty
S0.4: Check `.agent/shared/DEBT.md`
S0.5: Run `pytest .agent/executor/tests/app_tests/test_tool_call_parser.py -v` — confirm 3 failures

## F1 — Fix ToolCallParser isinstance Module Identity (Critical)

**Problem**: `isinstance(result, ToolCallErrorObservation)` returns `False` because the class used to create instances in `_parse_json()` is from a different module object than the class imported in `parse()`.

**Root cause**: `parser.py` imports `from sovereignai.skills.observation` but when the module is loaded from `app/sovereignai/skills/parser.py` (source) vs the installed package, Python creates duplicate module objects.

**Fix**: Use `type(result).__name__` or duck-typing instead of `isinstance()` for cross-module safety.

F1.1: Read `app/sovereignai/skills/parser.py`
F1.2: Edit `parse()` method: replace `isinstance(result, ToolCallErrorObservation)` with `hasattr(result, 'error_type') and hasattr(result, 'message')`
F1.3: Alternative: use `type(result).__name__ == 'ToolCallErrorObservation'` as fallback
F1.4: Run `pytest .agent/executor/tests/app_tests/test_tool_call_parser.py -v` — verify all 6 tests pass

## F2 — Execute Skipped Governance Fixes from plan-fix-2

**Problem**: plan-fix-2 executor skipped F1–F7 (governance loop fixes).

F2.1: Edit `AGENTS.md` Invariant #7: add "unless explicitly authorized by Architect plan or user instruction"
F2.2: Remove `.agent/executor/scripts/suggest_rule.py` and empty `suggestions/` subdirectories
F2.3: Edit `verify/SKILL.md` — remove step 8 suggest_rule.py reference
F2.4: Edit `close/SKILL.md` — fix DEBT.md scope note
F2.5: Edit `LANDMINES.md` — fix "prepend-only" to "prepend within severity bucket"
F2.6: Edit `RULE_LIFECYCLE.md` — remove SUGGEST stage, update directory tree
F2.7: Edit `AI_HANDOFF.md` step 4 — reflect actual Architect-driven rule detection flow
F2.8: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F3 — Add Landmine Detection Scripts (from plan-fix-2 F3)

F3.1: Create `.agent/executor/scripts/landmine_checks/detect_m1.py` — check for `app.sovereignai.*` imports in files under `app/sovereignai/`
F3.2: Create `.agent/executor/scripts/landmine_checks/detect_m4.py` — check test directory structure for namespace collisions
F3.3: Update `landmine_checks/run_all.py` to discover and run `detect_*.py` scripts
F3.4: Update `or_checks/run_all.py` to report "no OR checks defined" instead of "not yet implemented"
F3.5: Run `python .agent/executor/scripts/landmine_checks/run_all.py` — verify detects M1 if any dual imports exist

## F4 — Update PLANS.md Baseline

F4.1: Update "Current Baseline" to 531 tests, plan-fix-2-Rev1
F4.2: Ensure "Recent Completed" has exactly 10 entries
F4.3: Add plan-fix-2-Rev1 to "Recent Completed"
F4.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## F5 — Rewrite README.md

F5.1: Edit `README.md` Status: "Post-Plan 21. Active development. Core system complete with 531 tests."
F5.2: Remove dead links to `project-vision-Rev5.md` and `SovereignAI_Architecture_Decisions.md`
F5.3: Add links to actual docs
F5.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v` — verify pass

## Closing

Run `/close`
