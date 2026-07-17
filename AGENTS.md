# AGENTS.md — Executor Constitution

Authority: `.agent/architect/PRINCIPLES.md` · Architecture: `.agent/shared/ARCHITECTURE.md`

---

## Universal Invariants

1. STOP on any failure. Tests, lint, security, AR checks — any exit≠0 = STOP.
2. Execute plan steps in strict order. No reordering, no skipping.
3. Never delete or edit governance docs. Prepend-only for LANDMINES.md.
4. `/open` → execute → `/verify` per edit → `/close`. No shortcuts.
5. Follow skills literally. Reference AR IDs, not full text.
6. Exceptions need plan number. "Deferred" without plan = STOP.
7. No architect file edits. AGENTS.md, PRINCIPLES.md, AI_HANDOFF.md are read-only.
8. Scripts are SSOT. Skills reference scripts by path; no inline commands.
9. Coverage ≥90% at `/close`. No exemptions.

---

## Session Protocol

1. Read plan file → invoke `@skills:open`
2. Execute steps → invoke `@skills:verify` after each edit
3. Invoke `@skills:close` → STOP on any failure

Ambiguous → read `.agent/shared/LANDMINES.md`.
