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
- Read UOR section (Universal) + OOR section (open-specific)

Run `/open` workflow. STOP on any failure.

1. Read `AGENTS.md`.
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (listed rules only).
4. Read plan header OR rules from `.agent/executor/OR_RULES.md` (listed rules only).
5. Read `.agent/shared/CHANGELOG.md` latest entry.
6. Read `.agent/shared/DEBT.md` for deferred items.
7. Move all log files from subfolders (1-9, 10-19, 20-29, Misc) to logs root directory for easy access by running `.agent/executor/scripts/move_logs_to_root.py`.
8. Identify ambiguities. Ask user. Wait for answers.
9. Update `.agent/shared/PLANS.md` with new plan entry (mark "In Progress", shift upcoming queue).
10. Begin Phase 1.
11. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
