# /close Workflow

Run at end of every plan. Don't skip steps. STOP only on failure.

**Prerequisite**: `.venv/` exists (verified at `/open`). All commands use absolute venv paths (OR29).

## Static analysis

1. **Tests + coverage**: `.venv/Scripts/python.exe -m pytest tests/ -vvv --cov=. --cov-report=term-missing` — STOP on failure. STOP if coverage <90% (OR43). STOP if N/A for `.py`-editing plan.

2. **Ruff**: `.venv/Scripts/ruff.exe check .` — STOP on errors.

3. **Mypy** (`.py` only): `FILES=$(git diff --name-only prompt-{N-1}..HEAD | grep '\.py$'); if [ -n "$FILES" ]; then echo $FILES | xargs -r .venv/Scripts/mypy.exe --ignore-missing-imports; else echo "N/A — no .py changes"; fi` — STOP on errors (OR53). At scan prompts: `.venv/Scripts/mypy.exe . --ignore-missing-imports`.

4. **Bandit**: `.venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache` — STOP on findings.

5. **pip-audit**: `.venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt` — STOP on CVEs.

6. **Vulture**: `.venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov` — STOP on new findings vs `txt/vulture-whitelist.txt`.

7. **detect-secrets**: `.venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline` — STOP if exit≠0. False positive → `detect-secrets audit txt/.secrets.baseline`.

8. **AR checks**: run each script in `scripts/ar_checks/` — STOP on violation:
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

9. **OR63 placeholder check**: `.venv/Scripts/python.exe scripts/ar_checks/check_placeholders.py sovereignai/ shared/ web/ cli/ tui/ phone/ adapters/ databases/ services/ skills/` — STOP on any hit. Implement or defer per OR51 with target plan.

10. **OR61 tracing check**: `.venv/Scripts/python.exe scripts/ar_checks/check_tracing.py` — STOP if exit≠0.

11. **AR7 allowlist diff**: `diff <(git show prompt-{N-1}:tests/test_ar7_no_core_imports_in_ui.py | awk '/WEB_MAIN_ALLOWED_IMPORTS/{f=1} f' | grep -oE '"[^"]+"') <(awk '/WEB_MAIN_ALLOWED_IMPORTS/{f=1} f' tests/test_ar7_no_core_imports_in_ui.py | grep -oE '"[^"]+"')` — report added/removed entries. STOP on any unapproved addition.

## Documentation

12. **CHANGELOG**: append entry (≤15 lines):
    ```
    ## prompt-{N} — {title}
    **Date**: {YYYY-MM-DD}
    **Plan file**: prompts/plan-{N}-Rev{n}.md
    **Tests**: {count} passed, {count} skipped ({chronic} chronic)
    **Coverage**: {%}
    {≤3 Notes bullets}
    ```

13. **PLANS.md**: update baseline (test count, coverage, bandit count).

14. **DEBT.md**: add deferred items with target plan (OR54 for skipped tests).

14.1. **OR51 verification**: extract deferred item count from execution log, then `grep -c "prompt-{N}" DEBT.md` — if counts don't match, STOP.

14.5. **Close report**: write `documents/plan-{N}-report.md` with: plan title, test count, coverage %, deferred items, browser smoke test screenshot paths, AR7 allowlist diff, OR63 check result. Verify: `test -f documents/plan-{N}-report.md || STOP "Close report missing"`.

14.6. **LANDMINES.md**: append entry if any of: plan STOPped, new OR added, AR check failed for novel reason. Otherwise log "N/A — no new patterns".

## Verification (before commit/tag)

15. **Browser smoke test** (OR57 — mandatory for HTML/CSS/JS plans): start dev server, load page. For each new UI element listed in plan's "WILL edit" UI scope: verify present in DOM, verify interactive (click + observe state change), capture screenshot named `<element-id>.png` to `logs/screenshots/prompt-{N}/`. Verify each screenshot >1KB (non-blank). "Manual verification available" without doing it = STOP.

16. **Post-execution spec-match review** (OR65): 
    - Size guard: `DIFF_LINES=$(git diff prompt-{N-1}..HEAD | wc -l)` — if >5000 lines, chunk per phase. After chunked review, run `spec_match.py` on FULL diff for cross-chunk reconciliation.
    - Run `.venv/Scripts/python.exe scripts/ar_checks/spec_match.py` — mechanical gate. Exit≠0 = STOP.
    - If `spec_match.py` passes, spec-match review complete. No LLM review layer.

## Git (after verification passes)

17. **Stray-file scan** (OR59): `git add -A && git status -s` — verify no unintended files. If found: `git reset HEAD <file>` and `rm` or move to `/tmp/`.

18. **Commit**: `git add -A && git status -s && git commit -m "prompt-{N}: {title}"` (OR27: multi `-m` flags. OR41: `git add -A` only).

19. **Tag**: `git tag --list prompt-{N}` — STOP if not empty (premature tag per OR42). Then `git tag prompt-{N}`.

20. **Push**: `git push origin main --tags`

21. **Verify tag on origin**: `git ls-remote --tags origin | grep prompt-{N}` — STOP if missing.

## Finalize

22. **Execution log**: paste full chat log into `logs/execution-log-prompt-{N}.md`.

23. **Kill bash**: `taskkill //F //IM bash.exe 2>&1 || true`
