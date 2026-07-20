---
name: scan
authority: AGENTS.md
description: Run at scan prompts (5, 10, 15...). Whole-repo scan. No new features. Fixes only. More thorough than /close. Self-contained except for shared verify_close.py hard gate.
argument-hint: "[plan-number]"
triggers: ["user", "model"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Operational Rules: See .agent/executor/OR_RULES.md
- Read UOR section (Universal: UOR-1, UOR-2, UOR-3, UOR-4, UOR-5, UOR-6)
- Read COR section (Close-specific: COR-1, COR-2, COR-3) — scan performs same closing checks

Run `/scan` workflow. Whole-repo scan. No new features. Fixes only. STOP on failure.

Note: Log organization not required in scan mode — logs are organized at session open via /open skill.

1. Resolve plan: `get_current_plan.py`.
2. Full pytest suite. 300s timeout. STOP on failure. STOP if coverage <90%.
3. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
4. AR checks: `ar_checks/run_all_ar_checks.py`. STOP on any failure.
5. Landmine checks: `landmine_checks/run_all_landmine_checks.py`. STOP if exit≠0.
6. OR checks: `or_checks/run_all_or_checks.py`. STOP if exit≠0.
7. Placeholders: `check_placeholders.py`. STOP on hit.
8. Cross-reference check: `check_rule_crossrefs_doc.py`. STOP on failure.
9. Dependency check: `check_dependencies.py`. STOP on failure.
10. Rule conciseness: `check_rule_conciseness.py`. STOP on failure.
11. Changelog: `check_changelog.py`. STOP on failure.
12. Spec match: `spec_match.py`. STOP if exit!=0. No new features.
13. Read `.agent/shared/DEBT.md`. Verify trigger conditions for external debts. Document status.
14. HARD GATE - `verify_close.py`. Checks: execution log blank, CHANGELOG position, plan files moved, no uncommitted governance changes. If exit!=0: STOP. Do not commit.
15. **Trace integrity check: Verify `.agent/executor/traces/trace-plan-{N}.jsonl` exists and contains entries for all phases declared in Executor Manifest. If gaps found: STOP. (Invariant 12)**
16. **Verify `.agent/executor/ATTESTATION_TEMPLATE.md` exists. If missing: STOP. (COR-3, Invariant 13)**
17. **Produce execution attestation: `logs/execution-attestation-plan-{N}.md` using template at `.agent/executor/ATTESTATION_TEMPLATE.md`. (Invariant 13, COR-3)**
18. **Manually run `.agent/executor/hooks/verify_attestation.py --plan {N}` to verify attestation. (Invariant 13, COR-3 — fallback if config.json hook fails)**
19. **Run `.agent/executor/scripts/verify_execution.py --final --plan {N}`. Checks: manifest deliverables present in git history, no governance files modified, attestation present/complete, trace file exists. If FAIL: STOP. Do not commit. (UOR-4, COR-3)**
20. **Manually run `.agent/executor/hooks/append_trace.py --skill scan --plan {N}` to log /scan invocation. (Invariant 12 — fallback if config.json hook fails)**
21. Documentation: prepend CHANGELOG, update PLANS.md.
22. Git: commit, tag `plan-{N}`, push.
