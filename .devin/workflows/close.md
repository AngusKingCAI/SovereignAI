# /close Workflow

Run at the end of every plan. Do not pause between steps — run straight through. STOP only on failure.

## Steps

1. Run full test suite:
   ```
   python -m pytest tests/ -vvv
   ```
   If any test fails, STOP.

2. Run ruff (full repo):
   ```
   ruff check . 2>&1 | tail -n 3
   ```
   If errors, STOP.

3. Run mypy:
   - At scan prompts (5, 10, 15...): `mypy . --ignore-missing-imports`
   - At regular prompts: `mypy <files-edited-this-plan> --ignore-missing-imports`
   
   Pipe through `tail -n 3`. If errors, STOP.

4. Run bandit:
   ```
   bandit -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5
   ```
   If findings, STOP.

5. Run pip-audit:
   ```
   pip-audit --strict 2>&1 | tail -n 5
   ```
   If CVEs, STOP.

6. Run vulture:
   ```
   vulture . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5
   ```
   Compare against `txt/vulture-whitelist.txt`. If new findings, STOP.

7. Run detect-secrets:
   ```
   detect-secrets scan --baseline txt/.secrets.baseline
   ```
   If exit code != 0, STOP — a new secret was introduced. Either update the baseline (if false positive) or remove the secret. Do not commit until this passes.

8. Run custom static analysis checks (AR rules). Each is a separate command. STOP on any violation:
   - No globals in `core/`
   - Constructor arg cap (15) in `core/`
   - No context bags in `core/`
   - Docstring verb-first, ≥10 words on first line
   - No hard-coded component names in `web/`, `cli/`, `tui/`, `phone/`
   - UI changes don't touch `core/` (check `git diff --name-only HEAD~1`)

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

17. Commit docs (do NOT include the execution log file — it's committed separately after the User pastes content):
    ```
    git add CHANGELOG.md PLANS.md LANDMINES.md DEBT.md prompts/plan-{N}*.md
    git commit -m "docs: prompt-{N} governance updates"
    ```

18. Push:
    ```
    git push origin main
    git push origin prompt-{N}
    ```
    If push fails, STOP.

19. Verify tag on origin:
    ```
    git ls-remote --tags origin | grep "prompt-{N}"
    ```
    If missing, STOP.

20. Final summary:
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

21. Close Git Bash sessions (Windows-specific):
    ```
    taskkill //F //IM bash.exe
    ```
    No output expected. Kills all `bash.exe` processes including the current session. This is the final step — no further commands will execute.
