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

Run `/open` workflow. STOP on any failure.

1. Read `AGENTS.md`.
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. Read `.agent/shared/CHANGELOG.md` latest entry.
4. Identify ambiguities. Ask user. Wait for answers.
5. Log new patterns to `.agent/shared/LANDMINES.md`. Do not add AR/OR rules.
6. Update `.agent/shared/PLANS.md` with new plan entry.
7. Begin Phase 1.
8. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
