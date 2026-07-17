---
name: close
authority: AGENTS.md
description: Run at end of every plan. Verify, document, commit, tag, push. Atomic — all green or STOP.
argument-hint: "[plan-number]"
triggers: ["user"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Run `/close` workflow. STOP on any failure. Atomic — all checks pass or nothing commits.

1. Resolve plan: `get_current_plan.py`.
2. Scan check: `is_scan_plan.py $CURRENT_PLAN`.
   - If "true": full pytest suite. 300s timeout.
   - If "false": `get_scoped_tests.py $CHANGED_PY`. If empty + .py changes: STOP.
3. Tests: run scoped or full. STOP on failure. STOP if coverage <90%.
4. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
5. AR checks: `ar_checks/run_all.py`. STOP on any failure.
6. Placeholders: `check_placeholders.py`. STOP on hit.
7. Spec match: `spec_match.py`. STOP if exit≠0.
8. HARD GATE — `verify_close.py`. If exit≠0: STOP. Do not commit. Do not tag.
9. Documentation: prepend CHANGELOG, update PLANS.md, add to DEBT.md.
10. Git: `git status` → identify session files only → `git add` specific files → commit → tag `prompt-{N}` → push.
