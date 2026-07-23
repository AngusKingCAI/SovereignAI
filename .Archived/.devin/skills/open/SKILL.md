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
8. **Read plan header AR rules from cache** (listed rules only). Use `.agent/executor/scripts/rules_cache_lib.py` to read cached rules with automatic validation.
9. **Read plan header OR rules from cache** (listed rules only). Use `.agent/executor/scripts/rules_cache_lib.py` to read cached rules with automatic validation.
10. Read `.agent/shared/CHANGELOG.md` latest entry.
11. **Validate and regenerate rules cache if needed**: `python .agent/executor/scripts/rules_cache_lib.py invalidate_if_needed`. This ensures cache is up-to-date when governance files change.
12. Read `.agent/shared/DEBT.md` for deferred items.
13. **Read execution attestation from previous plan**: Read `logs/execution-attestation-plan-{N-1}.md` if it exists. Verify attestation phases match the previous plan's Executor Manifest phases and that `verify_execution.py --final` result is PASS.
14. **Read execution trace from previous plan** (if attestation shows issues): Read `.agent/executor/traces/trace-plan-{N-1}.jsonl` to identify any drift.
15. **Initialize execution trace: create `.agent/executor/traces/trace-plan-{N}.jsonl` with manifest hash and timestamp. (Invariant 12)**
16. **Manually run `.agent/executor/hooks/append_trace.py --skill open --plan {N}` to log /open invocation. (Invariant 12 — fallback if hook fails)**
17. Identify ambiguities. Ask user. Wait for answers.
18. Update `.agent/shared/PLANS.md` with new plan entry (mark "In Progress", shift upcoming queue).
19. **Organize log files**: Run `.agent/executor/scripts/organize_logs.py` to move log files from root to numbered subfolders (0-9, 10-19, 20-29, 30-39, Misc).
20. Begin Phase 1.
21. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
