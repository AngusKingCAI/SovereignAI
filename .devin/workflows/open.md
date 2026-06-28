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

3. Read `AGENTS.md` in full.

4. Add any new rules the plan specifies to `AGENTS.md`. Commit:
   ```
   git add AGENTS.md
   git commit -m "docs: add rules for prompt-{N}"
   ```

5. Check for untracked governance docs or plan files:
   ```
   git status -s | grep -E "AGENTS.md|AI_HANDOFF.md|PLANS.md|CHANGELOG.md|LANDMINES.md|DECISIONS.md|CONTEXT.md|DEBT.md|project-vision|prompts/"
   ```
   If any found, commit separately:
   ```
   git add <files>
   git commit -m "docs: cleanup pre-prompt-{N}"
   git tag docs-cleanup-{N}
   ```

6. Proceed to plan body (S1 onward). Run `/verify` after each file edit.
