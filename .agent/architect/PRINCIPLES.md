# Principles — SovereignAI

Living document. Amend when principles change. Old founding vision at `project-vision-Rev5.md` (historical reference only).

---

P1. Core is sacred. 12 core modules only. Anything else is pluggable.
P2. Everything pluggable. Adapters, skills, memory backends, models, UIs — all equal, all interchangeable.
P3. No provider lock-in. Delete any component, system keeps running.
P4. Local-first. Runs fully offline. Cloud is escalation, not foundation. v1: Windows only.
P5. Wire as you go. No speculative contracts. No empty placeholder directories.
P6. One user, one system, accessible anywhere. All UIs connect to same core. (Phone/relay deferred.)
P7. Modular and flexible over simple. Parts break, not the whole.
P8. UIs are separate processes consuming capability API. 10-section sidebar (Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options).
P9. Observability by default. No silent failures. All traces local via TraceEmitter.
P10. Security via reasoning. Security Guard is a tool the user invokes, not a gate. (Deferred.)
P11. DI only. No globals. No context bags. ≤15 constructor args.
P12. No docstrings. Code must be self-documenting via clear naming. (Reversed from original P12.)
P13. Strong and robust. Fail gracefully, isolate faults, recover without manual intervention.
P14. Provenance enforcement for external components. (Deferred.)

---

## Workflow principles

- Plans ≤120 lines. Executable steps only.
- Coverage ≥90% at `/close`.
- Mechanical enforcement > judgment-based rules.
- No governance rule references (OR/AR) in source code.
- No external tool dependencies in governance files.
- Architecture constraints: `.agent/shared/ARCHITECTURE.md`.
- `/close` is atomic: verify before commit/tag/push.
- Round table runs until clean pass. Each rev brings new evidence.
