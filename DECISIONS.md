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

## D2 — Hand-rolled DI container (no external dependency)

**Context**: AR4 requires a DI container for managing shared state and component lifecycles.
**Options considered**: A) Hand-rolled passive typed registry (no runtime magic); B) `dependency-injector` library; C) Other third-party DI framework.
**Decision**: Option A — Hand-rolled DI container in `shared/container.py`.
**Rationale**: A passive typed registry (no @inject decorators, no auto-wiring, no runtime magic) aligns with A8 (no hidden complexity). The container is a simple map of type → instance/factory. Explicit wiring in main.py (Composition Root) makes the dependency graph transparent and debuggable. No external dependency reduces attack surface and version drift.
**Trade-offs**: More verbose than auto-wiring frameworks. Requires manual registration of each component. Acceptable given the small component count (9) and the benefit of clarity and control.
**Status**: Active. Implemented at Plan 1. All 9 components registered: TraceEmitter, EventBus, CapabilityGraph, LifecycleManager, RoutingEngine, TaskStateMachine, AuthMiddleware, CapabilityAPI, RelayPlaceholder.
**Source**: `AGENTS.md` AR4, Plan 1 implementation.

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

## D4 — Single file instantiates all core components explicitly (Q26 resolution)

**Context**: Q26 asked whether core components should be instantiated in a single file (main.py) or via runtime magic/auto-discovery.
**Options considered**: A) Single file (main.py) instantiates all components explicitly in topological order; B) Runtime magic (reflection, auto-discovery, plugins); C) Hybrid (some explicit, some auto).
**Decision**: Option A — main.py build_container() instantiates all 9 components explicitly.
**Rationale**: Explicit wiring is transparent, debuggable, and aligns with AR4 (no global mutable state, DI container for shared state). Runtime magic obscures dependency graph and makes testing harder. Per A3, this decision is confirmed at Plan 4 /close.
**Trade-offs**: More verbose than auto-discovery. Requires manual updates when adding components. Acceptable given the small component count (9) and the benefit of clarity.
**Status**: Active. All 9 components wired: TraceEmitter, EventBus, CapabilityGraph, LifecycleManager, RoutingEngine, TaskStateMachine, AuthMiddleware, CapabilityAPI, RelayPlaceholder.
**Source**: `project-vision-Rev5.md` Q26 (resolved at Plan 4).

---

## How to add a new decision

At `/close` step (when a decision is codified), append an entry in the format above. Do not edit or remove existing entries — DECISIONS.md is append-only.
