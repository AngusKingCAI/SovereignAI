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

Operational Rules: See .agent/shared/OR_RULES.md
- Read UOR section (Universal) + OOR section (open-specific)

Run `/open` workflow. STOP on any failure.

1. Read `AGENTS.md`.
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. Read `.agent/shared/CHANGELOG.md` latest entry.
4. Check `.agent/executor/suggestions/` for new rule proposals. If suggestions exist, evaluate per RULE_LIFECYCLE.md TRIAGE before proceeding.
5. Identify ambiguities. Ask user. Wait for answers.
6. Log new patterns to `.agent/shared/LANDMINES.md`. For recurring patterns, document in execution log for Architect review.
7. Update `.agent/shared/PLANS.md` with new plan entry.
8. Begin Phase 1.
9. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
