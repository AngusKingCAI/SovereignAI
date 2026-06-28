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

## D5 — Governance documentation optimization (SSOT cleanup + script externalization)

**Context**: A documentation review found duplicate maintenance burden across the governance docs: `scan.md` restated `close.md`'s tool commands verbatim; open questions were tracked in both `PLANS.md` and `project-vision-Rev5.md`; the Test Baseline's per-suite breakdown was hand-summed and had already drifted once (Plan 5); Custom AR checks (`/close` step 8) were free-text prose re-derived from memory each close instead of committed code; CHANGELOG entries were exceeding OR14's line guidance with implementation rationale that duplicated DECISIONS.md's purpose; DEBT.md had logged the same Q8 versioning deferral twice.
**Options considered**: A) Leave as-is — duplication is explicit and intentional caching; B) Fix each instance individually, converting prose-duplicated facts to single-source pointers and prose-duplicated commands to committed scripts; C) Full rewrite of governance doc structure.
**Decision**: Option B — targeted fixes, no structural rewrite.
**Rationale**: The underlying document-responsibility design (one fact, one writer) stated in `AI_HANDOFF.md`'s SSOT mapping was already correct; the duplication was drift from that design, not a design flaw. Minimal targeted fixes restore the original intent without requiring re-validation of the whole governance system.
**Trade-offs**: `scan.md` is now less self-contained — a reader must open `close.md` to see the actual commands. Accepted: the alternative (restating commands) is what caused the drift being fixed. Custom AR check scripts (`scripts/ar_checks/`) need to be validated against the real `sovereignai/` codebase before they're trustworthy — they're committed as a starting point, not verified against the actual source tree in this pass.
**Status**: Active. Affects: `scan.md` step 1 (now references `/close`), `close.md` steps 8/9/10/12, `AGENTS.md` OR14 (amended) and OR48 (new), `PLANS.md` (Open Questions → pointer, Test Baseline → generated count, Reconciliation Notes → delta-only), `DEBT.md` (duplicate-check requirement + cross-reference note for the Q8 duplicate).
**Source**: Governance review, prompt-5 follow-up, 2026-06-28.

---

## How to add a new decision

At `/close` step (when a decision is codified), append an entry in the format above. Do not edit or remove existing entries — DECISIONS.md is append-only.
