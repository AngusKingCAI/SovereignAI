# DECISIONS.md — SovereignAI Architectural Decisions

Append-only. Status: `Proposed | Accepted | Superseded`.

---

## Active Decisions

| ID | Decision | Consequences | Revisit |
|----|----------|--------------|---------|
| D1 | Python for v1 | Slower runtime, GIL limits. Revisit Plan 20+. | Plan 20+ |
| D2 | Hand-rolled DI container | Verbose wiring. Transparent dependency graph. No external deps. | — |
| D3 | Windows-only for v1 | Linux/macOS excluded. Forward-slash paths. | Q31 |
| D4 | Explicit component instantiation | Verbose but testable. No runtime magic. | — |
| D5 | Targeted governance doc fixes | scan.md less self-contained. AR checks need validation. | — |
| D6-v2 | Prohibit docstrings | Naming must be descriptive. No docstring maintenance. | — |
| D7 | Remove OR references from code | Lost code-to-rule traceability. Governance docs are SSOT. | — |
| D8 | Scoped tests during iteration | Untouched-area regressions may persist up to 4 plans. | — |
| DD-23.11.1 | DIContainer dual-registration (protocol + concrete) | Double registration overhead. Protocol-key retrieval for testability. | — |
| DD-23.11.3 | GraphMemory duck-typed protocol satisfaction | Runtime type checking overhead. No concrete GraphMemory class. | — |

## Superseded Decisions

| ID | Superseded By | Date |
|----|---------------|------|
| D6 | D6-v2 | 2026-07-02 |

---

## D1 — Python for v1

**Status**: Accepted
**Context**: Language choice for initial implementation (Q10 resolved).
**Decision**: Python for v1. Rust migration deferred.
**Consequences**: Slower runtime, higher memory usage, GIL limits parallelism. Acceptable for v1 single-user local-first.

---

## D2 — Hand-rolled DI container

**Status**: Accepted
**Context**: AR4 requires DI container for shared state and component lifecycles.
**Decision**: Hand-rolled passive typed registry in `shared/container.py`. No auto-wiring, no `@inject`, no runtime magic.
**Consequences**: Verbose wiring. Transparent dependency graph. No external dependency attack surface.

---

## D3 — Windows-only for v1

**Status**: Accepted
**Context**: Platform target (vision principle P4).
**Decision**: Windows-only for v1. Cross-platform support not precluded.
**Consequences**: Linux/macOS users cannot run v1. Path handling uses forward slashes (Windows accepts both).

---

## D4 — Explicit component instantiation

**Status**: Accepted
**Context**: Q26 — single file vs runtime magic for component instantiation.
**Decision**: `main.py` `build_container()` instantiates all 9 components explicitly in topological order.
**Consequences**: Verbose but testable. No runtime magic. Manual updates when adding components.

---

## D5 — Targeted governance doc fixes

**Status**: Accepted
**Context**: Duplicate maintenance burden across governance docs. scan.md restated close.md commands. Open questions tracked in both PLANS.md and PRINCIPLES.md. Test baseline hand-summed and drifted.
**Decision**: Targeted fixes restoring original SSOT design. No structural rewrite.
**Consequences**: scan.md less self-contained — reader must open close.md for commands. AR check scripts need validation against actual source tree.

---

## D6-v2 — Prohibit docstrings

**Status**: Accepted
**Context**: AR21 docstring discipline created maintenance burden. Violated self-documenting code principle.
**Decision**: Prohibit all docstrings per AR11. Code must be self-documenting via clear naming.
**Consequences**: No inline documentation. IDE hover shows signatures only. External docs (DECISIONS.md, CHANGELOG.md) provide architectural context.

---

## D7 — Remove OR references from code

**Status**: Accepted
**Context**: OR references embedded in code comments, docstrings, config files. Created coupling between governance numbering and implementation.
**Decision**: Remove all OR references from code and config. Keep only in governance docs.
**Consequences**: Lost traceability from code to specific rules. Code explains the "what" not the "why". Governance docs are SSOT for rule citations.

---

## D8 — Scoped tests during iteration

**Status**: Accepted
**Context**: Full pytest suite (~183s) caused output-truncation thrashing mid-plan. Agent repeatedly failed to find final summary line.
**Decision**: Scoped execution during non-scan plans. Full suite on scan plans (divisible by 5).
**Consequences**: Untouched-area regressions may persist up to 4 plans. Full suite timeout increased to 300s. Scoped failures still governed by UOR-2 — no exemption.

---

## DD-23.11.1 — DIContainer dual-registration (protocol + concrete)

**Status**: Proposed
**Context**: Plan 23 S10 requires ReActLoop to be retrievable via both protocol key (ReActLoopFactory) and concrete key (ReActLoop) for testability and runtime flexibility.
**Decision**: DIContainer supports dual-registration: both protocol key and concrete key map to same factory instance. Protocol classes are hashable and work as dict keys.
**Consequences**: Double registration overhead (minimal). Protocol-key retrieval enables duck-typed testing while concrete-key retrieval provides direct instance access.

---

## DD-23.11.3 — GraphMemory duck-typed protocol satisfaction

**Status**: Proposed
**Context**: Plan 23 S2.3 requires GraphMemory as @runtime_checkable Protocol for duck-typed satisfaction without concrete class.
**Decision**: GraphMemory defined as Protocol with @runtime_checkable decorator. Plan 24 TaskGraphCache must satisfy this protocol (locked contract).
**Consequences**: Runtime type checking overhead (minimal). No concrete GraphMemory class exists — any class with matching method signature satisfies protocol. Enables flexible memory implementations.
