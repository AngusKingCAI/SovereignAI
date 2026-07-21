# AGENTS.md — Executor Constitution

Authority: `.agent/architect/PRINCIPLES.md` · Architecture: `.agent/executor/ARCHITECTURE.md` · Operations: `.agent/executor/OR_RULES.md`

---

## Universal Invariants

1. STOP on any failure (exit≠0). Halt execution, report reason, fix/retry. No skipping steps. HARD GATES: `verify_close.py` and `verify_execution.py --final` must PASS before commit/tag.
2. Execute plan steps in strict order. No reordering, no skipping.
3. Never delete/edit governance docs unless plan instructs. Prepend-only for LANDMINES.md.
4. Never delete plan files. Move only (e.g., to plans/completed/).
5. `/open` → execute → `/verify` after every step → `/close`. No shortcuts.
6. Follow skill instructions literally. Reference AR IDs, not full text.
7. Exceptions need plan number. "Deferred" without plan = STOP.
8. No architect file edits. `.agent/architect/` is read-only unless authorized. Exception: `.agent/architect/ARCHITECT_PATTERNS.md` per plan instruction.
9. Scripts are SSOT. Skills reference scripts by path; no inline commands.
10. Coverage ≥90% at `/close`. No exemptions.
11. Never execute workflow steps manually unless requested. Use skills/workflows as intended.
12. Skill invocation failure (`/open`, `/verify`, `/close`) = STOP completely. Report environment/tooling issues.
13. **Execution Trace: After every action, append entry to `.agent/executor/traces/trace-plan-{N}.jsonl` (timestamp, phase, step, action, file, result). Missing entries = STOP. Executor reads Manifest at `/open` to validate phase deliverables.**
14. **Execution Attestation: Before `/close`, produce `logs/execution-attestation-plan-{N}.md` using `.agent/executor/ATTESTATION_TEMPLATE.md`. Verified by `verify_execution.py`. Missing/incomplete/incorrect = no commit/tag/push.**

---

## Testing Best Practices

See `.agent/executor/tests/TESTING.md` for: iterative testing (`run_failing_tests.py`), deterministic ordering, organization, coverage requirements.

---

## Session Protocol

1. Read plan file → read AR/OR rules (scoped) → **read Executor Manifest** → invoke `/open` → STOP on failure
2. Execute each step → invoke `/verify` after every step → STOP on failure
3. → Invoke `/close` → STOP on failure

Ambiguous → read `.agent/shared/LANDMINES.md`.
