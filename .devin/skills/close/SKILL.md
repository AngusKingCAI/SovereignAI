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

0. `CURRENT_PLAN=$(.venv/Scripts/python.exe scripts/get_current_plan.py)` — this is the ONE plan file for the remainder of `/close`. Every later step referencing a plan filename uses `$CURRENT_PLAN`. STOP if empty.

0.5. Determine if scan plan: `IS_SCAN=$(.venv/Scripts/python.exe scripts/is_scan_plan.py $CURRENT_PLAN)` — returns "true" if plan number % 5 == 0, else "false". This drives test scope per OR29.

## Static analysis

1. Determine test scope per OR29:
   - If `IS_SCAN=true`: Run full suite with 5-minute timeout: `.venv/Scripts/python.exe -m pytest tests/ -q --tb=no 2>&1 | tail -20` — STOP on failure. Capture summary line (passed/failed/skipped) for CHANGELOG. Use 300000ms timeout (suite runtime ~183s, needs headroom). Next read call: timeout 300000.
   - Else:
     a. `CHANGED_PY=$(git diff --name-only prompt-{N-1}..HEAD | grep '\.py$')`
     b. If no `.py` files changed: echo "N/A — no Python files modified"
     c. Else: Run scoped tests using module reference matching: `SCOPED_TESTS=$(.venv/Scripts/python.exe scripts/get_scoped_tests.py $CHANGED_PY)` — this finds test files that import or reference changed modules. If `SCOPED_TESTS` is empty but `.py` files changed, STOP per OR9/OR19 (coverage gap). Then: `pytest $SCOPED_TESTS -vvv --cov=. --cov-report=term-missing` — STOP on failure. STOP if coverage <90%. Next read call: timeout 300000.

2. `.venv/Scripts/ruff.exe check .` — STOP on errors.

3. `FILES=$(git diff --name-only prompt-{N-1}..HEAD | grep '\.py$'); if [ -n "$FILES" ]; then echo $FILES | xargs -r .venv/Scripts/mypy.exe --ignore-missing-imports; else echo "N/A"; fi` — STOP on errors. At scan prompts: `.venv/Scripts/mypy.exe . --ignore-missing-imports`.

4. `.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache --baseline bandit/baseline.json` — STOP on findings.

5. `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt` — STOP on CVEs.

5.5. Invoke Snyk MCP scan on txt/requirements.txt + changed Python files. Document any new findings in DEBT.md with explicit target plan (not TBD — per OR64). Exit≠0 on CRITICAL/HIGH Snyk findings = STOP per OR81/L66.

6. `.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov` — STOP on new findings vs `txt/vulture-whitelist.txt`.

7. `.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline` — STOP if exit≠0. False positive: `detect-secrets audit txt/.secrets.baseline`.

8. Run each — STOP on violation:
   ```
   .venv/Scripts/python.exe scripts/ar_checks/no_globals.py sovereignai/
   .venv/Scripts/python.exe scripts/ar_checks/constructor_arg_cap.py sovereignai/ --max-args 15
   .venv/Scripts/python.exe scripts/ar_checks/no_context_bags.py sovereignai/
   .venv/Scripts/python.exe scripts/ar_checks/no_hardcoded_component_names.py web/ cli/ tui/ phone/
   .venv/Scripts/python.exe scripts/ar_checks/ui_does_not_touch_core.py
   .venv/Scripts/python.exe scripts/ar_checks/check_tracing.py
   .venv/Scripts/python.exe scripts/ar_checks/check_placeholders.py
   .venv/Scripts/python.exe scripts/ar_checks/check_p4_compliance.py
   ```

## Mechanical enforcement

9. `.venv/Scripts/python.exe scripts/ar_checks/check_placeholders.py sovereignai/ shared/ web/ cli/ tui/ phone/ adapters/ databases/ services/ skills/` — STOP on any hit.

10. `.venv/Scripts/python.exe scripts/ar_checks/check_tracing.py` — STOP if exit≠0.

11. `.venv/Scripts/python.exe scripts/check_ar7_allowlist.py prompt-{N-1} tests/test_ar7_no_core_imports_in_ui.py` — STOP on any unapproved addition.

## Documentation

12. Prepend to CHANGELOG.md:
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

13. Update `PLANS.md` baseline: test count, coverage, bandit count.

14. Add deferred items to `DEBT.md` with target plan.

14.1. `grep -c "prompt-{N}" DEBT.md` — compare to count added in step 14. STOP if mismatch.

14.6. Append to `LANDMINES.md` if: plan STOPped, new OR added, or AR check failed for novel reason. Else: log "N/A — no new patterns".

## Verification (before commit/tag)

15. Start dev server, load page. For each new UI element in plan's "WILL edit" scope: verify present in DOM, click + observe state change, capture screenshot `<element-id>.png` to `logs/screenshots/prompt-{N}/`. Verify each screenshot >1KB. STOP if not done. STOP if dev server won't start.

16. `DIFF_LINES=$(git diff prompt-{N-1}..HEAD | wc -l)`. `.venv/Scripts/python.exe scripts/ar_checks/spec_match.py $CURRENT_PLAN` — STOP if exit≠0. No exceptions. Blocks steps 17-22 until it passes.

## Git

17. `git add -A && git status -s` — verify no unintended files.

17.5. Run `python scripts/ar_checks/check_changelog.py <plan_number>`. Exit≠0 = STOP per OR73.

17.6. Run python scripts/ar_checks/check_dependencies.py. Exit≠0 = STOP per OR77.

17.7. Run python scripts/ar_checks/check_rule_conciseness.py. Exit≠0 = STOP per OR80.

17.8. rm .open_hash.

18. Move ALL plan-{N} revision files, not a single named revision:
   ```
   BEFORE_COUNT=$(ls prompts/plan-{N}-Rev*.md 2>/dev/null | wc -l)
   mv prompts/plan-{N}-Rev*.md prompts/completed/
   AFTER_COUNT=$(ls prompts/completed/plan-{N}-Rev*.md 2>/dev/null | wc -l)
   ls prompts/plan-{N}* 2>/dev/null
   ```
   Must be empty AND `AFTER_COUNT` = `BEFORE_COUNT` — STOP if not. Never substitute a specific filename for the glob.
   Note: If git mv fails with "bad source", use plain mv then git add -A. Per L23, mv + git add -A is safe (git add -A catches the rename).

18.5. `git add prompts/*.md && git status -s` — ensure ALL plan files in prompts/ are added to git (tracked or untracked). This prevents treating untracked plan files as cleanup artifacts per L69.

19. `git add -A && git status -s && git commit -m "prompt-{N}: {title}" -m "{note 1}" -m "{note 2}" -m "{note 3}"` — one `-m` per CHANGELOG Notes bullet.

20. `git tag --list prompt-{N}` — STOP if not empty. Then `git tag prompt-{N}`.

21. `git push origin main --tags`

22. `git ls-remote --tags origin | grep prompt-{N}` — STOP if missing.

## Finalize

23. Create `logs/execution-log-prompt-{N}.md` if missing (blank template only, no content).

24. `taskkill //F //IM bash.exe 2>&1 || true`
