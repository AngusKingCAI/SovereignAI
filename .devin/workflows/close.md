# /close Workflow

Run at end of every plan. Don't skip steps. STOP only on failure.

Prerequisite: `.venv/` exists.

## Static analysis

1. `.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing` — STOP on failure. STOP if coverage <90%. STOP if N/A for `.py`-editing plan.

2. `.venv/Scripts/ruff.exe check .` — STOP on errors.

3. `FILES=$(git diff --name-only prompt-{N-1}..HEAD | grep '\.py$'); if [ -n "$FILES" ]; then echo $FILES | xargs -r .venv/Scripts/mypy.exe --ignore-missing-imports; else echo "N/A"; fi` — STOP on errors. At scan prompts: `.venv/Scripts/mypy.exe . --ignore-missing-imports`.

4. `.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache` — STOP on findings.

5. `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt` — STOP on CVEs.

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
   ```

## Mechanical enforcement

9. `.venv/Scripts/python.exe scripts/ar_checks/check_placeholders.py sovereignai/ shared/ web/ cli/ tui/ phone/ adapters/ databases/ services/ skills/` — STOP on any hit.

10. `.venv/Scripts/python.exe scripts/ar_checks/check_tracing.py` — STOP if exit≠0.

11. `diff <(git show prompt-{N-1}:tests/test_ar7_no_core_imports_in_ui.py | awk '/WEB_MAIN_ALLOWED_IMPORTS/{f=1} f' | grep -oE '"[^"]+"') <(awk '/WEB_MAIN_ALLOWED_IMPORTS/{f=1} f' tests/test_ar7_no_core_imports_in_ui.py | grep -oE '"[^"]+"')` — STOP on any unapproved addition.

## Documentation

12. Append to CHANGELOG.md:
    ```
    ## prompt-{N} — {title}
    **Date**: {YYYY-MM-DD}
    **Plan file**: prompts/plan-{N}-Rev{n}.md
    **Tests**: {count} passed, {count} skipped ({chronic} chronic)
    **Coverage**: {%}
    **Browser smoke test screenshots**: {paths from step 15, or "N/A"}
    **AR7 allowlist diff**: {entries from step 11, or "None"}
    **OR63 check result**: {result from step 9}
    {≤3 bullets, one line each, summarizing S1-Sn phase work — no restatement of the fields above}
    ```

13. Update `PLANS.md` baseline: test count, coverage, bandit count.

14. Add deferred items to `DEBT.md` with target plan.

14.1. `grep -c "prompt-{N}" DEBT.md` — compare to count added in step 14. STOP if mismatch.

14.6. Append to `LANDMINES.md` if: plan STOPped, new OR added, or AR check failed for novel reason. Else: log "N/A — no new patterns".

## Verification (before commit/tag)

15. Start dev server, load page. For each new UI element in plan's "WILL edit" scope: verify present in DOM, click + observe state change, capture screenshot `<element-id>.png` to `logs/screenshots/prompt-{N}/`. Verify each screenshot >1KB. "N/A — requires manual verification" without doing it = STOP. STOP if dev server won't start.

16. `DIFF_LINES=$(git diff prompt-{N-1}..HEAD | wc -l)` — if >5000, chunk review per phase, then run full-diff pass. `.venv/Scripts/python.exe scripts/ar_checks/spec_match.py` — STOP if exit≠0. No exceptions for "repo state issue" or similar — fix the repo or fix the plan.

## Git

17. `git add -A && git status -s` — verify no unintended files. If found: `git reset HEAD <file>` and `rm` or move to `/tmp/`.

18. `mv prompts/plan-{N}-* prompts/completed/` — `ls prompts/plan-{N}* 2>/dev/null` must return empty. STOP if not.

19. `git add -A && git status -s && git commit -m "prompt-{N}: {title}" -m "{note 1}" -m "{note 2}" -m "{note 3}"` — one `-m` flag per CHANGELOG Notes bullet from step 12. Never embed `\n` in a single `-m` string.

20. `git tag --list prompt-{N}` — STOP if not empty. Then `git tag prompt-{N}`.

21. `git push origin main --tags`

22. `git ls-remote --tags origin | grep prompt-{N}` — STOP if missing.

## Finalize

23. Create `logs/execution-log-prompt-{N}.md` if missing:
    ```
    # Execution Log - Prompt {N}
    **Status**:
    **Date**:
    **Plan**:

    ## Clarifications


    ## Notes


    ```
    Leave blank. Do not write content into this file.

24. `taskkill //F //IM bash.exe 2>&1 || true`
