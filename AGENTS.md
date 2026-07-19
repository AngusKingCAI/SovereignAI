# AGENTS.md — Executor Constitution

Authority: `.agent/architect/PRINCIPLES.md` · Architecture: `.agent/executor/ARCHITECTURE.md` · Operations: `.agent/executor/OR_RULES.md`

---

## Universal Invariants

1. STOP on any failure. Tests, lint, security, AR checks — any exit≠0 = STOP.
   STOP means: halt current step execution, report failure reason, do not proceed to next step. Executor may fix the failure and retry the same step, but must not skip to subsequent steps without passing the current step. Only verify_close.py HARD GATE is fatal: do not commit or tag if it fails.
2. Execute plan steps in strict order. No reordering, no skipping.
3. Never delete or edit governance docs unless plan explicitly instructs. Prepend-only for LANDMINES.md.
4. `/open` → execute → `/verify` per edit → `/close`. No shortcuts.
5. Follow skill instructions literally. Reference AR IDs, not full text.
6. Exceptions need plan number. "Deferred" without plan = STOP.
7. No architect file edits. `.agent/architect/` is read-only unless explicitly authorized by user instruction.
8. Scripts are SSOT. Skills reference scripts by path; no inline commands.
9. Coverage ≥90% at `/close`. No exemptions.
10. Never execute workflow steps manually unless explicitly requested by user. Always use skills/workflows as intended.
11. Skill invocation failure: If `/open`, `/verify`, or `/close` cannot be invoked via skill tool (skill not found, permission denied, or other invocation error), STOP completely. Skill tool failures indicate environment/tooling issues that should be reported.

---

## Session Protocol

1. Read plan file → read AR rules and OR rules from plan header → invoke `/open` slash command → STOP on failure
2. Execute steps → invoke `/verify` slash command after each edit → STOP on failure
3. → Invoke `/close` slash command → STOP on failure

Ambiguous → read `.agent/shared/LANDMINES.md`.
