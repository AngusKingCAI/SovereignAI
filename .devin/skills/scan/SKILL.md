---
name: scan
description: Run at scan prompts (5, 10, 15...). Whole-repo scan. No new features. Fixes only. More thorough than /close.
argument-hint: "[plan-number]"
triggers: ["user"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Run `/scan` workflow. Whole-repo scan. No new features. Fixes only. STOP on failure.

1. Resolve plan: `get_current_plan.py`.
2. Full pytest suite. 300s timeout. STOP on failure. STOP if coverage <90%.
3. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
4. AR checks: `ar_checks/run_all.py`. STOP on any failure.
5. Placeholders: `check_placeholders.py`. STOP on hit.
6. Cross-reference check: `check_rule_crossrefs.py`. STOP on failure.
7. Dependency check: `check_dependencies.py`. STOP on failure.
8. Rule conciseness: `check_rule_conciseness.py`. STOP on failure.
9. Changelog: `check_changelog.py`. STOP on failure.
10. Spec match: `spec_match.py`. STOP if exit≠0. No new features.
11. HARD GATE — `verify_close.py`. If exit≠0: STOP. Do not commit.
12. Documentation: prepend CHANGELOG, update PLANS.md, add to DEBT.md.
13. Git: commit, tag `prompt-{N}`, push.
