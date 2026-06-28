# /close Workflow

Run at the end of every plan. Do not pause between steps — run straight through. STOP only on failure.

## Steps

**Prerequisite**: The project-local venv (`.venv/`) must exist and be functional before running any step in this workflow. The venv is verified at `/open` step 3 (per OR45). If the venv does not exist, STOP and run `/open` first. Per OR46, all commands below use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc.) — do not rely on `source .venv/Scripts/activate` (it does not reliably persist in Git Bash on Windows per L30).

**N/A handling**: When a step's result is N/A (e.g., no Python code to test, no new landmines discovered), the Executor runs the step, observes the N/A result, and reports it in the final summary (step 20). The Executor does NOT skip the step. Skipping steps because "the result would be N/A" is an OR34 violation. The only steps that may be skipped are those explicitly marked "skip if N/A" in this workflow file.

1. Run full test suite (use absolute venv path per OR46):
   ```
   .venv/Scripts/python.exe -m pytest tests/ -vvv
   ```
   If any test fails, STOP. If pytest reports "no tests ran" and the plan was supposed to add tests, STOP — test collection may have failed silently.

2. Run ruff (full repo, use absolute venv path per OR46):
   ```
   .venv/Scripts/ruff.exe check . 2>&1 | tail -n 3
   ```
   If errors, STOP.

3. Run mypy on Python files only (per OR47 — never pass markdown or other non-Python files to mypy):
   - At scan prompts (5, 10, 15...): `.venv/Scripts/mypy.exe . --ignore-missing-imports` (scans whole repo, naturally skips non-Python files)
   - At regular prompts: filter edited files to `.py` only, then run mypy:
     ```
     EDITED_PY_FILES=$(git diff --name-only HEAD~1 | grep '\.py$' | tr '\n' ' ')
     if [ -n "$EDITED_PY_FILES" ]; then
       .venv/Scripts/mypy.exe $EDITED_PY_FILES --ignore-missing-imports 2>&1 | tail -n 3
     else
       echo "mypy: N/A (no Python files edited this plan)"
     fi
     ```
     If no `.py` files were edited, mypy is N/A — report "N/A (no Python files edited)" in the final summary (step 20) and continue to step 4. Do NOT pass markdown or other non-Python files to mypy — it will fail with "Duplicate module named __main__" or similar errors (L31).
   
   If mypy reports errors on `.py` files, STOP.

4. Run bandit (use absolute venv path per OR46):
   ```
   .venv/Scripts/bandit.exe -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
   ```
   If findings, STOP.

5. Run pip-audit (use absolute venv path per OR46; scan requirements file only per OR39):
   ```
   .venv/Scripts/pip-audit.exe --strict --requirement txt/requirements.txt 2>&1 | tail -n 5
   ```
   If CVEs, STOP.

6. Run vulture (use absolute venv path per OR46):
   ```
   .venv/Scripts/vulture.exe . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
   ```
   Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.

7. Run detect-secrets (use absolute venv path per OR46):
   ```
   .venv/Scripts/detect-secrets.exe scan --baseline txt/.secrets.baseline
   ```
   If exit code != 0, STOP — a new secret was introduced. Either update the baseline (if false positive, use `.venv/Scripts/detect-secrets.exe audit txt/.secrets.baseline` per OR40) or remove the secret. Do not commit until this passes.

8. Run custom static analysis checks (AR rules). Each is a separate command. STOP on any violation:
   - No globals in `sovereignai/`
   - Constructor arg cap (15) in `sovereignai/`
   - No context bags in `sovereignai/`
   - Docstring verb-first, ≥10 words on first line
   - No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`
   - UI changes don't touch `sovereignai/` (check `git diff --name-only HEAD~1`)

9. Update `CHANGELOG.md` — append entry to END:
   ```
   ## prompt-{N} — {Plan title}
   
   **Date**: {YYYY-MM-DD}
   **Plan file**: prompts/plan-{N}-Rev{n}.md
   
   **Files changed**:
   - {file1}
   - {file2}
   
   **Results**:
   - Tests: {count} passed, {count} failed
   - Ruff: {count} findings
   - Mypy: {count} findings
   - Bandit: {count} findings
   - Vulture: {count} findings
   - Detect-secrets: pass/fail
   
   **Notes**:
   - {observations}
   ```
   Use temp-file pattern: write to `temp/changelog-entry-{N}.md`, `cat >> CHANGELOG.md`, delete temp.

10. Update `PLANS.md`:
   - Update baselines (test count, ruff, mypy, bandit, vulture, detect-secrets, coverage %) with actual numbers
   - Add completed prompt row: `| prompt-{N} | {date} | {title} | {test count} | {notes} |`
   - Update "Active prompt" to none, "Next prompt" to `prompt-{N+1}`
   - Shift next-5-queue

11. Update `LANDMINES.md` if a new failure pattern was discovered. Append-only. New landmines start at L24 (L1-L23 inherited from sovereign-ai).

12. Update `DEBT.md` if any items deferred this plan. Format:
    ```
    ## Deferred: {item name}
    
    **Deferred at**: prompt-{N}
    **Reason**: {why}
    **Trigger condition**: {when to address}
    **Target plan**: {number or TBD}
    ```

13. Propose new AR/OR rules via C9 if the Architect spotted a recurring pattern. Put proposal in the execution log.

14. Create execution log file (header only, do NOT commit yet):
    ```
    mkdir -p logs
    cat > logs/execution-log-prompt-{N}.md << 'EOF'
    # Execution Log — prompt-{N}
    
    **Plan**: {plan title}
    **Tag**: prompt-{N}
    **Date**: {YYYY-MM-DD}
    
    ---
    
    <!-- USER: Paste the full Executor execution log below this line. -->
    
    EOF
    ```
    The User will paste content into this file after `/close` completes, then ask the Executor to commit and push it.

15. Commit code changes:
    ```
    git add <files-changed-this-plan>
    git commit -m "{plan title} (prompt-{N})
    
    {multi-line description}"
    ```
    Never use `--no-verify`. If a pre-commit hook fails, fix or STOP.

16. Tag:
    ```
    git tag prompt-{N}
    git tag --list prompt-{N}
    ```
    If tag not created, STOP.

17. Move completed prompt files to `prompts/completed/`:
    ```
    mkdir -p prompts/completed
    git mv prompts/plan-{N}*.md prompts/completed/
    git mv prompts/plan-{N}-brief.md prompts/completed/ 2>/dev/null || true  # brief may not exist
    ```
    This archives all revisions and the brief file for the completed prompt.

18. Commit docs (do NOT include the execution log file — it's committed separately after the User pastes content):
    ```
    git add CHANGELOG.md PLANS.md LANDMINES.md DEBT.md prompts/completed/
    git commit -m "docs: prompt-{N} governance updates"
    ```

19. Push:
    ```
    git push origin main
    git push origin prompt-{N}
    ```
    If push fails, STOP.

20. Verify tag on origin:
    ```
    git ls-remote --tags origin | grep "prompt-{N}"
    ```
    If missing, STOP.

21. Final summary:
    ```
    === prompt-{N} COMPLETE ===
    
    Code commit: {hash}
    Docs commit: {hash}
    Tag: prompt-{N} (verified on origin)
    
    Tests: {count} passed
    Ruff: {count} findings
    Mypy: {count} findings
    Bandit: {count} findings
    Vulture: {count} findings
    Detect-secrets: pass/fail
    Coverage: {%}
    
    New landmines: {count or none}
    New deferred items: {count or none}
    New rule proposals: {count or none}
    
    === REMINDER ===
    The Executor created logs/execution-log-prompt-{N}.md with a header template.
    After this session ends:
    1. Open logs/execution-log-prompt-{N}.md in your editor
    2. Paste the full chat log content below the comment block
    3. Save the file
    4. Ask the Executor to commit and push it (e.g., "commit and push the execution log for prompt-{N}")
    ```

21. Close Git Bash sessions (Windows-specific). **STOP CONDITION: the plan is NOT complete until this step executes.** Do not report "Plan X Complete" in step 20's final summary until step 21 has run. If you find yourself about to end the session after step 20, STOP — you have not finished. Run step 21 now:
    ```
    taskkill //F //IM bash.exe 2>&1 || true
    ```
    The `|| true` ensures the step succeeds even if no bash.exe processes are running. This kills all `bash.exe` processes including the current session — no further commands will execute after this step. 
    
    This step is mandatory for ALL plans, including docs-only plans. N/A results from prior steps (e.g., "Tests: N/A") do NOT make this step N/A — this step always runs. A second `taskkill` runs at the START of the next plan's `/open` step 1 to clean up any orphans if this step was somehow skipped.
