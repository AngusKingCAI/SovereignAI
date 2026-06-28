# /open Workflow

Run at the start of every plan.

## Steps

1. Verify previous plan's tag on origin:
   ```
   git fetch origin
   git ls-remote --tags origin | grep "prompt-{N-1}"
   ```
   If missing, STOP. Skip if Plan 1.

2. Confirm working copy is clean and on main:
   ```
   git status -s | tail -n 10
   git branch --show-current
   ```
   If dirty (excluding governance docs/plan files) or not on main, STOP.

3. Verify the project-local venv exists (per OR45). If `.venv/` does not exist, create it and install dev dependencies:
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

4. Read `AGENTS.md` in full.

5. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

6. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

7. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
