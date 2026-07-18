# AGENTS.md — Executor Constitution

Authority: `.agent/architect/PRINCIPLES.md` · Architecture: `.agent/shared/ARCHITECTURE.md`

---

## Universal Invariants

1. STOP on any failure. Tests, lint, security, AR checks — any exit≠0 = STOP.
   STOP means: halt current step execution, report failure reason, do not proceed to next step. Executor may fix the failure and retry the same step, but must not skip to subsequent steps without passing the current step. Only verify_close.py HARD GATE is fatal: do not commit or tag if it fails.
2. Execute plan steps in strict order. No reordering, no skipping.
3. Never delete or edit governance docs. Prepend-only for LANDMINES.md. Architect detects patterns from execution logs.
4. Execute `.devin/skills/open/SKILL.md` → execute plan steps → execute `.devin/skills/verify/SKILL.md` per edit → execute `.devin/skills/close/SKILL.md`. No shortcuts.
5. Follow skill instructions literally. Reference AR IDs, not full text.
6. Exceptions need plan number. "Deferred" without plan = STOP.
7. No architect file edits. AGENTS.md, PRINCIPLES.md, AI_HANDOFF.md are read-only unless explicitly authorized by Architect plan or user instruction.
8. Scripts are SSOT. Skills reference scripts by path; no inline commands.
9. Coverage ≥90% at `/close`. No exemptions.
10. Never execute workflow steps manually unless explicitly requested by user. Always read and execute local skill files from `.devin/skills/` directly.

---

## Session Protocol

1. Read plan file → Read and execute `.devin/skills/open/SKILL.md` instructions
2. Execute steps → Read and execute `.devin/skills/verify/SKILL.md` instructions after each edit
3. Read and execute `.devin/skills/close/SKILL.md` instructions → STOP on any failure

Ambiguous → read `.agent/shared/LANDMINES.md`.
