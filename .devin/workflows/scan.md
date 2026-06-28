# /scan Workflow

Run at scan prompts (Plan 5, 10, 15, 20, ...). Whole-repo scan. No new features. No new architecture. Fixes only. If any scan reveals a structural problem requiring design decisions, STOP and report — do not guess.

## Steps

1. Run all scan tools in full, one at a time (parallel execution corrupts output streams):
   - `python -m pytest tests/ -vvv` (full verbose, no piping)
   - `ruff check . 2>&1 | tail -n 3`
   - `mypy . --ignore-missing-imports 2>&1 | tail -n 3` (full repo at scan prompts)
   - `bandit -r . -ll --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache 2>&1 | tail -n 5`
   - `pip-audit --strict 2>&1 | tail -n 5`
   - `vulture . --min-confidence 80 --exclude .venv,venv,env,.git,node_modules,__pycache__,build,dist,.tox,.eggs,.pytest_cache,.mypy_cache,.ruff_cache,htmlcov 2>&1 | tail -n 5` (compare against `txt/vulture-whitelist.txt`)
   - `detect-secrets scan --baseline txt/.secrets.baseline`
   - Custom AR static analysis checks (same as `/close` step 8)
   - **Auto-discovered tools**: any test suite or static analysis tool configured in `pyproject.toml`, `pytest.ini`, `.pre-commit-config.yaml`, or similar. Run them all automatically.
   
   If any tool reports new findings, STOP.

2. Scan `LANDMINES.md` — for any landmine without a corresponding rule in `AGENTS.md`, propose the missing rule via C9.

3. Scan `CHANGELOG.md` — verify every plan in the completed batch has an entry.

4. Scan `PLANS.md` — verify baselines are current and next-5-queue reflects actual state. Update if stale.

5. Scan all docstrings for references to removed/renamed modules. Fix stale references mechanically.

6. Run full test suite (final confirmation after any fixes from steps 2-5):
   ```
   python -m pytest tests/ -vvv
   ```

7. Verify coverage hasn't dropped >5% from baseline:
   ```
   python -m pytest tests/ --cov=. --cov-report=term 2>&1 | tail -n 10
   ```

8. Audit against the principles in `project-vision-Rev5.md`. For each of the 14 principles, verify the codebase complies. If any principle is violated, STOP — architectural violations require a regular plan with Round Table review, not a scan fix.

9. Audit against the success criteria in `project-vision-Rev5.md`. For each of the 40 criteria, verify the codebase passes. If any criterion fails, STOP.

10. Review `DEBT.md` — for each deferred item, check if its trigger condition has been met. If yes, flag for the next plan.

11. Audit open questions in `project-vision-Rev5.md` — check if any have been implicitly resolved by recent plans. If yes, move to "Resolved Open Questions" with a note.

12. Final summary:
    ```
    === SCAN COMPLETE (prompt-{N}) ===
    
    Tools run:
    - pytest: {count} tests, {count} passed
    - ruff: {count} findings
    - mypy: {count} findings
    - bandit: {count} findings
    - pip-audit: {count} CVEs
    - vulture: {count} findings ({count} new)
    - custom AR checks: all pass / {count} failures
    
    Fixes applied:
    - {list of mechanical fixes}
    
    Vision principle audit: 14/14 pass / {count} violations
    Success criteria audit: 40/40 pass / {count} failures
    
    DEBT.md review: {count} items reviewed, {count} flagged
    Open questions audit: {count} resolved, {count} remain
    
    === REMINDER ===
    Copy the chat log to logs/execution-log-prompt-{N}.md before closing this session.
    ```

13. Close Git Bash sessions (Windows-specific):
    ```
    taskkill //F //IM bash.exe
    ```
    No output expected. Kills all `bash.exe` processes including the current session. This is the final step.
