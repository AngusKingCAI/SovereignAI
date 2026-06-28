# DECISIONS.md — SovereignAI Architectural Decisions Record

Append-only. Each entry: context, options considered, decision, rationale, trade-offs, status.

---

## D1 — Python for v1, Rust migration deferred

**Context**: Language choice for initial implementation (vision open question Q10).
**Options considered**: A) Python for v1, migrate to Rust later; B) Rust from day one; C) Hybrid — core in Rust, adapters in Python.
**Decision**: Option A — Python for v1.
**Rationale**: Speed of iteration for a single developer. Python's ecosystem (pydantic, pytest, ruff, mypy) provides mature tooling. Contracts are language-agnostic; future Rust rewrite is not precluded.
**Trade-offs**: Slower runtime, higher memory usage, GIL limits parallelism. Acceptable for v1 single-user local-first target.
**Status**: Active. Revisit after Plan 20+.
**Source**: `project-vision-Rev5.md` Q10 (resolved).

---

## D2 — `dependency-injector` as the DI container library

**Context**: AR4 requires a DI container and names `dependency-injector` specifically.
**Options considered**: Not separately debated. The choice was made during AR4 drafting and encoded directly in the rule text.
**Decision**: `dependency-injector` (per AR4).
**Rationale**: AR4 asserts this library meets the DI-managed singleton (Orchestrator, Librarian Registry) and factory (Managers, Workers) requirements. Full options/rationale not separately debated — this ADR records that gap.
**Trade-offs**: External dependency. If abandoned, manual DI is the fallback. If Plan 1+ implementation reveals issues, this entry should be expanded with the options/rationale and re-submitted to the Round Table.
**Status**: Active, pending separate debate. Revisit at Plan 1 if implementation surfaces friction.
**Source**: `AGENTS.md` AR4.

---

## D3 — Windows-only for v1

**Context**: Platform target (vision principle P4).
**Options considered**: A) Windows-only v1, cross-platform later; B) Cross-platform from day one.
**Decision**: Option A — Windows-only for v1.
**Rationale**: Single developer on Windows. Reduces complexity. Architecture must not foreclose cross-platform support.
**Trade-offs**: Linux/macOS users cannot run v1. Path handling uses forward slashes (Windows accepts both).
**Status**: Active. Revisit for packaging plan (Q31).
**Source**: `project-vision-Rev5.md` P4, Q31 (open).

---

## How to add a new decision

At `/close` step (when a decision is codified), append an entry in the format above. Do not edit or remove existing entries — DECISIONS.md is append-only.
