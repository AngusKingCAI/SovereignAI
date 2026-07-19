---
name: open
description: Run at start of every plan. Read context, resolve ambiguities, set up workspace.
argument-hint: "[plan-number]"
triggers: ["user"]
allowed-tools:
  - read
  - grep
  - exec
  - edit
  - write
---

Operational Rules: See .agent/executor/OR_RULES.md
- Read UOR section (Universal) + OOR section (open-specific)

Run `/open` workflow. STOP on any failure.

**FALLBACK**: If skill tool invocation fails, execute steps manually via read/exec tools.

1. Read `AGENTS.md`.
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md` (listed rules only).
4. Read plan header OR rules from `.agent/executor/OR_RULES.md` (listed rules only).
5. Read `.agent/shared/CHANGELOG.md` latest entry.
6. Read `.agent/shared/DEBT.md` for deferred items.
7. Identify ambiguities. Ask user. Wait for answers.
8. Update `.agent/shared/PLANS.md` with new plan entry (mark "In Progress", shift upcoming queue).
9. Begin Phase 1.
10. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
