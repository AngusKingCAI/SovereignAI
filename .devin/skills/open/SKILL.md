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

OR17. Deliverables ship in full or defer — no partial implementations
OR19. Test/mypy/static-analysis failures: no "pre-existing" exemption
OR63. diskcache CVE monitoring — check DEBT.md for CVE status before close
OR65. Architect must evaluate all suggestions before creating plan — if suggestions exist, read and evaluate per RULE_LIFECYCLE.md TRIAGE

Run `/open` workflow. STOP on any failure.

1. Read `AGENTS.md`.
2. Read plan file `prompts/plan-{N}-Rev{X}.md`.
3. Read `.agent/shared/CHANGELOG.md` latest entry.
4. Check `.agent/executor/suggestions/` for new rule proposals. If suggestions exist, evaluate per RULE_LIFECYCLE.md TRIAGE before proceeding.
5. Identify ambiguities. Ask user. Wait for answers.
6. Log new patterns to `.agent/shared/LANDMINES.md`. For recurring patterns, run suggest_rule.py.
7. Update `.agent/shared/PLANS.md` with new plan entry.
8. Begin Phase 1.
9. After each phase: run `verify_syntax.py`, `ruff check`, scoped `pytest`. STOP on failure.
