# AGENTS.md — Executor Constitution

Authority: `.agent/architect/PRINCIPLES.md` · Architecture: `.agent/executor/ARCHITECTURE.md` · Operations: `.agent/executor/OR_RULES.md`

---

## Universal Invariants

1. STOP on any failure. Tests, lint, security, AR checks — any exit≠0 = STOP.
   STOP means: halt current step execution, report failure reason, do not proceed to next step. Executor may fix the failure and retry the same step, but must not skip to subsequent steps without passing the current step. Two HARD GATES are fatal and block commit/tag: `verify_close.py` and `verify_execution.py --final`. Both must PASS before git tag creation.
2. Execute plan steps in strict order. No reordering, no skipping.
3. Never delete or edit governance docs unless plan explicitly instructs. Prepend-only for LANDMINES.md.
4. `/open` → execute → `/verify` after every step (not just edits) → `/close`. No shortcuts.
5. Follow skill instructions literally. Reference AR IDs, not full text.
6. Exceptions need plan number. "Deferred" without plan = STOP.
7. No architect file edits. `.agent/architect/` is read-only unless explicitly authorized by user instruction. Exception: `.agent/architect/ARCHITECT_PATTERNS.md` can be edited by Executor per plan instruction (Architect identifies patterns → adds write-task to Executor Manifest → Executor writes).
8. Scripts are SSOT. Skills reference scripts by path; no inline commands.
9. Coverage ≥90% at `/close`. No exemptions.
10. Never execute workflow steps manually unless explicitly requested by user. Always use skills/workflows as intended.
11. Skill invocation failure: If `/open`, `/verify`, or `/close` cannot be invoked via skill tool (skill not found, permission denied, or other invocation error), STOP completely. Skill tool failures indicate environment/tooling issues that should be reported.
12. **Execution Trace: After every action (file edit, command run, skill invocation),
    append a structured entry to `.agent/executor/traces/trace-plan-{N}.jsonl`.
    Required fields: timestamp, phase, step, action, file (if any), result.
    The trace is the immutable record of execution. Missing trace entries = STOP condition.
    The executor reads the Executor Manifest from the plan file at `/open` and uses it
    to validate that every phase produces its declared deliverables before proceeding.**
13. **Execution Attestation: Before `/close` completes, produce
    `logs/execution-attestation-plan-{N}.md` using the template at
    `.agent/executor/ATTESTATION_TEMPLATE.md`. This attestation is verified by the
    user via `verify_execution.py`. If attestation is missing, incomplete, or incorrect,
    do not commit, do not tag, do not push. The attestation is the executor's signed
    proof of compliance with the plan manifest.**

---

## Testing Best Practices

See `.agent/executor/tests/TESTING.md` for detailed testing guidelines including:
- Iterative testing with `run_failing_tests.py`
- Deterministic test ordering
- Test organization and coverage requirements

---

## Session Protocol

1. Read plan file → read AR rules and OR rules from plan header (scoped list only) → **read Executor Manifest from plan file** → invoke `/open` slash command → STOP on failure
2. Execute each step → invoke `/verify` slash command after every step, edit or not → STOP on failure
3. → Invoke `/close` slash command → STOP on failure

Ambiguous → read `.agent/shared/LANDMINES.md`.
