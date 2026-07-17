---
name: close
description: Run at end of every plan. Don't skip steps. STOP only on failure.
argument-hint: "[plan-number]"
allowed-tools:
  - read
  - grep
  - glob
  - exec
  - edit
  - write
---

Run the /close workflow for the current plan. Follow all steps in order. Don't skip steps. STOP only on failure.

Prerequisite: `.venv/` exists.

## Resolve current plan file

□ Step 0: `CURRENT_PLAN=$(.venv/Scripts/python.exe .agent/executor/scripts/get_current_plan.py)` — STOP if empty.

□ Step 0.5: `IS_SCAN=$(.venv/Scripts/python.exe .agent/executor/scripts/is_scan_plan.py $CURRENT_PLAN)` — "true" if plan % 5 == 0.

## Static analysis

□ Step 1: Tests per OR29
  - If `IS_SCAN=true`: `.venv/Scripts/python.exe -m pytest .agent/executor/tests/ -q --tb=no` (300s timeout). STOP on failure.
  - Else: `CHANGED_PY=$(git diff --name-only prompt-{N-1}..HEAD | grep '\.py$')`
    - If empty: echo "N/A"
    - Else: `SCOPED_TESTS=$(.venv/Scripts/python.exe .agent/executor/scripts/get_scoped_tests.py $CHANGED_PY)` — STOP if empty.
    - Then: `pytest $SCOPED_TESTS -vvv --cov=. --cov-report=term-missing` — STOP on failure. STOP if coverage <90%.

□ Step 2: `.venv/Scripts/ruff.exe check .` — STOP on errors.

□ Step 3: Mypy on changed files (or full suite at scan). STOP on errors.

□ Step 4: `.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache --baseline .agent/executor/bandit/baseline.json` — STOP.

□ Step 5: `.venv/Scripts/pip-audit.exe --strict --requirement app/txt/requirements.txt` — STOP on CVEs.

□ Step 5.5: Snyk MCP scan. CRITICAL/HIGH = STOP. Document in .agent/executor/DEBT.md with target plan.

□ Step 6: `.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,.agent/executor/htmlcov` — STOP on new findings.

□ Step 7: `.venv/Scripts/detect-secrets.exe scan --baseline .agent/executor/txt/.secrets.baseline` — STOP if exit≠0.

□ Step 8: AR checks — run each, STOP on any violation:
  ```
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/no_globals.py app/sovereignai/
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/constructor_arg_cap.py app/sovereignai/ --max-args 15
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/no_context_bags.py app/sovereignai/
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/no_hardcoded_component_names.py app/web/ app/cli/ app/tui/ app/phone/
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/ui_does_not_touch_core.py
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/check_tracing.py
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/check_placeholders.py
  .venv/Scripts/python.exe .agent/executor/scripts/ar_checks/check_p4_compliance.py
  ```

□ Step 9: Placeholders — `.venv/Scripts/python.exe .agent/executor/scripts/ar_checks/check_placeholders.py app/sovereignai/ app/web/ app/cli/ app/tui/ app/phone/ app/adapters/ app/databases/ app/services/ app/skills/` — STOP on hit.

□ Step 10: Tracing — `.venv/Scripts/python.exe .agent/executor/scripts/ar_checks/check_tracing.py` — STOP if exit≠0.

□ Step 11: AR7 allowlist — `.venv/Scripts/python.exe .agent/executor/scripts/check_ar7_allowlist.py prompt-{N-1} .agent/executor/tests/test_ar7_no_core_imports_in_ui.py` — STOP on unapproved addition.

## Documentation

□ Step 12: CHANGELOG — PREPEND (not append) new entry at top:
  ```
  ## prompt-{N} — {title}
  **Date**: {YYYY-MM-DD}
  **Plan**: $CURRENT_PLAN
  **Tests**: {passed} passed, {skipped} skipped ({chronic} chronic)
  **Coverage**: {%}
  **Screenshots**: {paths or "N/A"}
  **AR7 diff**: {entries or "None"}
  **OR63**: {result}
  {≤3 bullets summarizing work}
  ```

□ Step 13: Update `.agent/executor/PLANS.md` baseline.

□ Step 14: Add deferred items to `.agent/executor/DEBT.md` with target plan.

□ Step 14.1: `grep -c "prompt-{N}" .agent/executor/DEBT.md` — compare to count added. STOP if mismatch.

□ Step 14.6: Append to `.agent/executor/LANDMINES.md` if plan STOPped, new OR added, or AR check failed for novel reason. Else: log "N/A — no new patterns".

## Verification (before commit/tag)

□ Step 15: Dev server + UI verification. Screenshots to `app/logs/screenshots/prompt-{N}/`. STOP if not done.

□ Step 16: Spec match — `.venv/Scripts/python.exe .agent/executor/scripts/ar_checks/spec_match.py $CURRENT_PLAN` — STOP if exit≠0. Blocks steps 17-22 until pass.

## Git

□ Step 17: `git add -A && git status -s` — verify no unintended files.

□ Step 17.5: `python .agent/executor/scripts/ar_checks/check_changelog.py <plan_number>` — STOP if exit≠0.

□ Step 17.6: `python .agent/executor/scripts/ar_checks/check_dependencies.py` — STOP if exit≠0.

□ Step 17.7: `python .agent/executor/scripts/ar_checks/check_rule_conciseness.py` — STOP if exit≠0.

□ Step 17.8: `rm .open_hash`.

□ Step 18: Move plan files — BEFORE_COUNT, mv, AFTER_COUNT, verify empty. STOP if mismatch.

□ Step 18.5: `git add prompts/*.md && git status -s` — ensure ALL plan files added.

□ Step 19: `git add -A && git status -s && git commit -m "prompt-{N}: {title}" -m "{note 1}" -m "{note 2}" -m "{note 3}"`

## HARD GATE — Step 19.5 (BEFORE tag)

□ Step 19.5: RUN `python .agent/executor/scripts/verify_close.py`
  - If exit 0: ☑ proceed to Step 20
  - If exit 1: ⛔ STOP. Do not create tag. Do not proceed. Do not explain or justify. Fix failures and re-run.

## Tag and push

□ Step 20: `git tag --list prompt-{N}` — STOP if not empty. Then `git tag prompt-{N}`.

□ Step 21: `git push origin main --tags`

□ Step 22: `git ls-remote --tags origin | grep prompt-{N}` — STOP if missing.

## Finalize

□ Step 23: Create `logs/execution-log-prompt-{N}.md` — BLANK TEMPLATE ONLY. VERIFY `wc -c < 500`.

□ Step 24: `taskkill //F //IM bash.exe 2>&1 || true`
