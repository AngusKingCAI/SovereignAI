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
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. **Read Executor Manifest from plan file. If missing or malformed: STOP. (Invariant 12, UOR-4, GR14)**
4. **Run `.agent/executor/scripts/preflight_check.py --plan {N}`. If FAIL: STOP.**
5. **Run `.agent/executor/scripts/verify_execution.py --init --plan {N}`. If FAIL: STOP. (UOR-4)**
6. **Create `.agent/executor/traces/` directory if it does not exist. (Invariant 12)**
7. **Create `.agent/executor/hooks/` directory if it does not exist.**
8. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (listed rules only).
9. Read plan header OR rules from `.agent/executor/OR_RULES.md` (listed rules only).
10. Read `.agent/shared/CHANGELOG.md` latest entry.
11. Read `.agent/shared/DEBT.md` for deferred items.
12. **Initialize execution trace: create `.agent/executor/traces/trace-plan-{N}.jsonl` with manifest hash and timestamp. (Invariant 12)**
13. **Manually run `.agent/executor/hooks/append_trace.py --skill open --plan {N}` to log /open invocation. (Invariant 12 — fallback if hook fails)**
14. Organize log files from logs root into numbered subfolders (1-9, 10-19, 20-29, Misc) by running `.agent/executor/scripts/organize_logs.py`.
15. Identify ambiguities. Ask user. Wait for answers.
16. Update `.agent/shared/PLANS.md` with new plan entry (mark "In Progress", shift upcoming queue).
17. Begin Phase 1.
18. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
