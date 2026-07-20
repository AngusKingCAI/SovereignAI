---
name: close
authority: AGENTS.md
description: Run at end of every plan. Verify, document, commit, tag, push. Atomic — all green or STOP.
argument-hint: "[plan-number]"
triggers: ["user", "model"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
  - skill
---

Operational Rules: See .agent/executor/OR_RULES.md
- Universal: UOR-1, UOR-2, UOR-3, UOR-4, UOR-5, UOR-6
- Close-specific: COR-1, COR-2, COR-3

Run `/close` workflow. STOP on any failure. Atomic — all checks pass or nothing commits.

Non-HARD-GATE STOP (steps 1–10): fix and retry. HARD-GATE STOP (steps 11, 15): abort, do not commit.

0. **Quick trace check: Verify `.agent/executor/traces/trace-plan-{N}.jsonl` exists. If missing: STOP. (Invariant 12 — lightweight check before heavy verification)**
1. Resolve plan: `get_current_plan.py`.
2. Determine test scope: Apply COR-1 (test-fix plans run full suite). Otherwise use `get_scoped_tests.py` (auto-detects based on git changes).
   - Returns: `.agent/executor/tests/` (architect/executor only)
   - Returns: `.agent/executor/tests/app_tests/` (sovereignai only)
   - Returns: `.agent/executor/tests/` (both or all)
3. Tests: run scoped or full tests with 300s timeout. Use iterative approach:
   a. First run: `run_failing_tests.py <test_path> --full` to establish baseline and cache failures.
   b. On retry: `run_failing_tests.py <test_path>` to run only failing tests from cache.
   c. Once all specific tests pass: run `run_failing_tests.py <test_path> --full` for final verification.
   STOP on failure. STOP if coverage <90%.
4. Static analysis: `ruff check .`, `mypy`, `bandit`, `pip-audit`, `vulture`, `detect-secrets`. STOP on any failure.
5. AR checks: `ar_checks/run_all_ar_checks.py`. STOP on any failure.
6. Landmine checks: `landmine_checks/run_all_landmine_checks.py`. STOP if exit≠0.
7. OR checks: `or_checks/run_all_or_checks.py`. STOP if exit≠0.
8. Placeholders: `check_placeholders.py`. STOP on hit.
9. Spec match: `spec_match.py`. STOP if exit≠0.
10. Read `.agent/shared/DEBT.md`. For each debt marked for resolution in plan: verify resolved, update status to "Resolved" or delete entry. Document resolution in CHANGELOG.
11. HARD GATE — `verify_close.py`. Checks: execution log blank, CHANGELOG position, plan files moved, no uncommitted governance changes. If exit≠0: STOP. Do not commit. Do not tag.
12. **Verify `.agent/executor/ATTESTATION_TEMPLATE.md` exists. If missing: STOP. (COR-3, Invariant 13)**
13. **Produce execution attestation: `logs/execution-attestation-plan-{N}.md` using template at `.agent/executor/ATTESTATION_TEMPLATE.md`. (Invariant 13, COR-3)**
14. **Manually run `.agent/executor/hooks/verify_attestation.py --plan {N}` to verify attestation. (Invariant 13, COR-3 — fallback if config.json hook fails)**
15. HARD GATE — `.agent/executor/scripts/verify_execution.py --final --plan {N}`. Checks: manifest deliverables present in git history, no governance files modified, attestation present/complete, trace file exists. This performs complete trace integrity verification including hash validation against manifest. If FAIL: STOP. Do not commit. (UOR-4, COR-3, Invariant 12)
16. **Manually run `.agent/executor/hooks/append_trace.py --skill close --plan {N}` to log /close invocation. (Invariant 12 — fallback if config.json hook fails)**
17. Execution log: create BLANK execution log file at `logs/execution-log-{plan-name}.md` with ONLY the header template. Do NOT populate with chat transcript — user will populate after execution. Template:
    ```
    # Execution Log: {plan-name}

    **Date**: YYYY-MM-DD
    **Plan**: {plan-file}
    **Executor**: {executor-name}

    ---

    *Populate this file with the chat transcript from the {plan-name} plan execution.*
    ```
18. **Move completed plan files**: Run `.agent/executor/scripts/move_completed_plans.py {plan-number}` to move the completed plan and all its revisions to `plans/completed/`.
19. Documentation: prepend CHANGELOG, update PLANS.md (mark "Completed", shift upcoming queue).
20. Git: `git status` → identify session files only → `git add` specific files → commit → tag `plan-{N}` → push.
