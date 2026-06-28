# /open Workflow

Run at the start of every plan.

## Steps

1. Kill orphaned bash.exe processes from previous sessions (Windows-specific):
   ```
   taskkill //F //IM bash.exe 2>&1 || true
   ```
   This kills all `bash.exe` processes, including the current session. The Executor's agent process is not affected — it spawns a fresh bash session for the next command automatically. This step cleans up orphans from previous sessions that may have crashed, been interrupted, or skipped `/close` step 21. The `|| true` ensures the workflow continues even if no bash.exe processes are running (taskkill exits non-zero when no processes match). Do NOT skip this step — orphaned bash processes accumulate across sessions and consume system resources.
   
   Note: a second `taskkill //F //IM bash.exe` runs at `/close` step 21 to clean up the current session's bash processes. Both are mandatory.

2. Verify previous plan's tag on origin:
   ```
   git fetch origin
   git ls-remote --tags origin | grep "prompt-{N-1}"
   ```
   If missing, STOP. Skip if Plan 1.

3. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

4. Verify the project-local venv exists (per OR45). If `.venv/` does not exist, create it and install dev dependencies:
   ```
   if [ ! -d ".venv" ]; then
     py -3.11 -m venv .venv
     .venv/Scripts/pip.exe install -e .[dev]
   fi
   ```
   Verify the venv is functional:
   ```
   .venv/Scripts/python.exe --version
   .venv/Scripts/pip.exe --version
   ```
   Both commands must succeed. If either fails, STOP and report — the venv is broken and must be recreated (`rm -rf .venv && py -3.11 -m venv .venv && .venv/Scripts/pip.exe install -e .[dev]`).
   
   Note: per OR46, all subsequent commands in this plan and in `/close` use absolute venv paths (`.venv/Scripts/python.exe`, `.venv/Scripts/ruff.exe`, etc.). Do not rely on `source .venv/Scripts/activate` — it does not reliably persist in Git Bash on Windows (L30).

5. Read `AGENTS.md` in full.

6. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

7. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

8. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
