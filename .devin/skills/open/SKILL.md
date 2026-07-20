---
name: open
description: Run at start of every plan. Read context, resolve ambiguities, set up workspace.
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
- Read UOR section (Universal: UOR-1, UOR-2, UOR-3, UOR-4, UOR-5, UOR-6) + OOR section (open-specific)

Run `/open` workflow. STOP on any failure.

1. Read `AGENTS.md` (Invariants 1-13).
2. Read plan file `plans/plan-{N}-Rev{X}.md`.
3. **Read Executor Manifest from plan file. If missing or malformed: STOP. (Invariant 12, UOR-4, GR13)**
4. **Run `.agent/executor/hooks/preflight_check.py --plan {N}`. If FAIL: STOP.**
5. **Run `.agent/executor/scripts/verify_execution.py --init --plan {N}`. If FAIL: STOP. (UOR-4)**
6. **Create `.agent/executor/traces/` directory if it does not exist. (Invariant 12)**
7. **Create `.agent/executor/hooks/` directory if it does not exist.**
8. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (listed rules only).
9. Read plan header OR rules from `.agent/executor/OR_RULES.md` (listed rules only).
10. Read `.agent/shared/CHANGELOG.md` latest entry.
11. Read `.agent/shared/DEBT.md` for deferred items.
12. **Read execution attestation from previous plan**: Read `logs/execution-attestation-plan-{N-1}.md` if it exists. Verify attestation phases match the previous plan's Executor Manifest phases and that `verify_execution.py --final` result is PASS.
13. **Read execution trace from previous plan** (if attestation shows issues): Read `.agent/executor/traces/trace-plan-{N-1}.jsonl` to identify any drift.
14. **Initialize execution trace: create `.agent/executor/traces/trace-plan-{N}.jsonl` with manifest hash and timestamp. (Invariant 12)**
15. **Manually run `.agent/executor/hooks/append_trace.py --skill open --plan {N}` to log /open invocation. (Invariant 12 — fallback if hook fails)**
16. Identify ambiguities. Ask user. Wait for answers.
17. Update `.agent/shared/PLANS.md` with new plan entry (mark "In Progress", shift upcoming queue).
18. Begin Phase 1.
19. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
