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

Operational Rules: See .agent/shared/OR_RULES.md
- Universal: UOR-1, UOR-2, UOR-3
- Close-specific: COR-1

Run `/close` workflow. STOP on any failure. Atomic — all checks pass or nothing commits.

1. Resolve plan: `get_current_plan.py`.
2. Determine test scope: Apply COR-1 (test-fix plans run full suite). Otherwise use `get_scoped_tests.py` (auto-detects based on git changes).
   - Returns: `.agent/executor/tests/` (architect/executor only)
   - Returns: `.agent/executor/tests/sovereignai/` (sovereignai only)
   - Returns: `.agent/executor/tests/` (both or all)
3. Tests: run scoped or full tests with 300s timeout. STOP on failure. STOP if coverage <90%.
4. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
5. AR checks: `ar_checks/run_all.py`. STOP on any failure.
6. Landmine checks: `landmine_checks/run_all.py`. STOP if exit≠0.
7. OR checks: `or_checks/run_all.py`. STOP if exit≠0.
8. Placeholders: `check_placeholders.py`. STOP on hit.
9. Spec match: `spec_match.py`. STOP if exit≠0.
10. HARD GATE — `verify_close.py`. If exit≠0: STOP. Do not commit. Do not tag.
11. Execution log: create BLANK execution log file at `logs/execution-log-{plan-name}.md` with ONLY the header template. Do NOT populate with chat transcript — user will populate after execution. Template:
   ```
   # Execution Log: {plan-name}

   **Date**: YYYY-MM-DD
   **Plan**: {plan-file}
   **Executor**: Devin

   ---

   *Populate this file with the chat transcript from the {plan-name} plan execution.*
   ```
12. Documentation: prepend CHANGELOG, update PLANS.md, add to DEBT.md.
13. Git: `git status` → identify session files only → `git add` specific files → commit → tag `prompt-{N}` → push.
