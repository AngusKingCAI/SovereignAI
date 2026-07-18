---
name: scan
authority: AGENTS.md
description: Run at scan prompts (5, 10, 15...). Whole-repo scan. No new features. Fixes only. More thorough than /close. Self-contained except for shared verify_close.py hard gate.
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
- Read UOR section (Universal)

Run `/scan` workflow. Whole-repo scan. No new features. Fixes only. STOP on failure.

1. Resolve plan: `get_current_plan.py`.
2. Full pytest suite. 300s timeout. STOP on failure. STOP if coverage <90%.
3. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
4. AR checks: `ar_checks/run_all.py`. STOP on any failure.
5. Landmine checks: `landmine_checks/run_all.py`. STOP if exit≠0.
6. OR checks: `or_checks/run_all.py`. STOP if exit≠0.
7. Placeholders: `check_placeholders.py`. STOP on hit.
8. Cross-reference check: `check_rule_crossrefs.py`. STOP on failure.
9. Dependency check: `check_dependencies.py`. STOP on failure.
10. Rule conciseness: `check_rule_conciseness.py`. STOP on failure.
11. Changelog: `check_changelog.py`. STOP on failure.
12. Spec match: `spec_match.py`. STOP if exit!=0. No new features.
13. HARD GATE - `verify_close.py`. If exit!=0: STOP. Do not commit.
14. Documentation: prepend CHANGELOG, update PLANS.md, add to DEBT.md.
15. Git: commit, tag `prompt-{N}`, push.