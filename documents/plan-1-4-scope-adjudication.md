# Round Table — SovereignAI Plans 1–4 Scope Split: Adjudication & Revised Split

**Document type**: Post-review adjudication. No new brief needed — the Round Table reviews this adjudication and the revised split directly. Flag any remaining CRITICAL or HIGH issues only; LOW/MEDIUM accepted items do not need re-review.

---

## Part 1 — Roles and Rules

Your job is to find problems with the **revised split** below, not to re-litigate the original. Assume the revised split will fail — identify how.

- Every issue must include a concrete failure scenario.
- Focus on the revised split only — findings already accepted and addressed below do not need to be re-raised.
- Explicitly permitted: "Clean pass" or "No new issues" if you find nothing.
- End your response with `**Panelist**: <your name/model>`.

---

## Part 2 — What the Panel Found and What Was Decided

### Accepted findings (all applied to the revised split)

**A1 — Routing engine moves from Plan 2 to Plan 3** *(GPT-5.4-mini, Claude, Gemini, Qwen — convergent)*
The routing engine must know whether a component is active, degraded, or circuit-broken — that is the Lifecycle Manager's job (Plan 3). A routing engine built before the Lifecycle Manager is a static dispatcher that requires a rewrite when Plan 3 lands. Accepted. Routing engine now in Plan 3.

**A2 — `shared/types.py` added to Plan 1** *(GPT-5.4-mini, Claude — convergent)*
Without a canonical type module in Plan 1, every downstream plan invents its own `Task`, `CapabilityDeclaration`, `ComponentManifest`, and `TraceEvent` types. By Plan 4 they have drifted and the Capability API cannot speak the same types as the state machine. `shared/types.py` added to Plan 1 — core domain types defined here as frozen dataclasses, all downstream plans import from this module only.

**A3 — Composition Root is incremental, not final in Plan 1** *(Kimi — accepted)*
Writing the final `main.py` in Plan 1 when only Plan 1 components exist forces Plans 2, 3, and 4 to each rewrite the system's single bootstrap file — each edit risks breaking topological order and Plan 1's regression tests. Plan 1 produces a `main.py` that wires its own components only. Each subsequent plan extends it. Plan 4 performs the final wiring audit and Q26 is confirmed at Plan 4 `/close`.

**A4 — Relay server deferred out of Plan 4 entirely** *(Claude CRITICAL, Gemini HIGH, Kimi HIGH — convergent)*
A relay stub that accepts connections without E2EE means Auth Middleware and Capability API are designed around plaintext — retrofitting E2EE later forces a complete rewrite of both. A stub that does nothing means Plan 4 ships an incomplete component as its final deliverable. Resolution: relay server deferred out of the first batch. Plan 4 ships a local-only placeholder that returns a structured error ("remote transport not yet supported") and emits a trace — it does not accept connections. Remote UIs are explicitly a later deliverable; the phone app is not a Plan 1–4 concern.

**A5 — Plans 2 and 3 must ship named interface protocols** *(Qwen, Claude, Kimi — convergent)*
Plan 4's Capability API cannot be drafted if Plan 2's capability graph and Plan 3's task state machine do not expose locked query interfaces. Plan 2 ships `ICapabilityIndex`. Plan 3 ships `ITaskStateQuery`. Plan 4 imports only those protocols — never core internals. A static-import test in Plan 4 confirms no transitive imports from core (AR7 enforcement).

**A6 — DAG validator stays in Plan 3** *(Claude, Kimi — accepted over Qwen/Gemini dissent)*
If Plan 3's state machine can accept composite skill tasks without validating their DAG, composite tasks enter the state machine unvalidated until Plan 4 — a silent failure (P9 violation). The validator is a prerequisite for composite tasks entering the state machine safely. It stays in Plan 3. Plan 3's scope is manageable: routing engine + lifecycle manager + state machine + DAG validator, with persistence scoped to in-memory only (see A7).

**A7 — Q14 persistence scoped to in-memory only in Plan 3** *(Kimi — accepted)*
Full event-sourced persistence + crash recovery + durable backends in Plan 3 alongside four other components is too much. Plan 3 implements the event-store interface and in-memory replay only. Durable backends and full crash recovery deferred to DEBT.

**A8 — Passive DI container clarification in Plan 1** *(Gemini — accepted)*
`shared/container.py` is a passive typed registry. `main.py` does all explicit instantiation in topological order. No `@inject` decorators, no auto-wiring magic. Specified as a Plan 1 scope constraint, not left implicit.

**A9 — Event bus ordering semantics locked in Plan 1** *(Qwen — accepted)*
Plan 3's task state machine publishes state transitions as events. If the bus does not guarantee ordering, transitions can arrive out of order and produce invalid state. Plan 1 must specify and test ordering semantics before Plan 3 is drafted. Decision: the event bus guarantees in-order delivery per typed channel. This must be verified by Plan 1's test suite.

### Rejected findings

**R1 — SovereignAI-Reviewer-Model** (anonymous panelist)
Invented fictional components not present in the brief or Core Scope (Component-8, Component-9, API Gateway, etc.). Non-substantive. Not adjudicated.

**R2 — Lifecycle Manager / Librarian as missing core component** *(Gemini Issue 4)*
Gemini flagged that the Librarian is absent from the 12 Core Scope components. This is correct — the Librarian is a pluggable component per the vision, not a core component. Memory routing is not in Core Scope v1. Task state persistence (Q14) is handled in-memory by Plan 3's state machine (see A7); durable backends are pluggable and deferred. No core component is missing.

**R3 — Q26 resolved at Plan 1** *(Kimi — noted and converted to A3)*
Q26 ("single file instantiates all core components explicitly") cannot be confirmed until all 12 components exist. Plan 1 cannot resolve it. Resolved by A3: Q26 is confirmed at Plan 4 `/close`, not Plan 1.

---

## Part 3 — Revised Split

| Plan | Components | Explicit deliverables | Open questions resolved |
|---|---|---|---|
| **Plan 1** | Event Bus (in-order per channel), TraceEmitter (singleton), DI container (passive registry), `shared/types.py` (core domain types), Composition Root (`main.py` wires Plan 1 components only) | Wiring tests; event bus ordering tests; `shared/types.py` frozen types | Q9 (test strategy), Q32 (DEBT.md scaffold) |
| **Plan 2** | Capability manifest parser, Capability graph → ships `ICapabilityIndex` protocol | `ICapabilityIndex` as a locked named output; manifest schema (TOML/JSON); Q8 MVP only (full versioning negotiation deferred) | Q1 (adapter contract), Q2 (skill discovery), Q8 (MVP) |
| **Plan 3** | Routing engine, Lifecycle manager, Task state machine, DAG validator → ships `ITaskStateQuery` protocol; persistence in-memory only | `ITaskStateQuery` as a locked named output; event-store interface + in-memory replay; Lifecycle↔StateMachine coupling via event bus (loose) | Q3 (memory abstraction interface), Q4 (routing), Q14 (in-memory only) |
| **Plan 4** | Auth middleware, Capability API (consumes `ICapabilityIndex` + `ITaskStateQuery` only), local-only relay placeholder, Composition Root final wiring audit | Static-import test proving Capability API has no transitive core imports (AR7); Q26 confirmed at `/close`; relay placeholder emits structured error, does not accept connections | Q26 (confirmed at close) |

### Cross-plan dependency map

```
Plan 1 ──► Plan 2 ──► Plan 3 ──► Plan 4
           (ICapabilityIndex)  (ITaskStateQuery)
```

- Plan 2 depends on Plan 1's `shared/types.py` for manifest and capability types
- Plan 3 depends on Plan 2's `ICapabilityIndex` for routing and lifecycle queries
- Plan 4 depends on Plan 2's `ICapabilityIndex` and Plan 3's `ITaskStateQuery` for the Capability API; never imports core internals directly

### What is explicitly deferred (DEBT items)

- Relay server E2EE implementation — post-batch, dedicated plan
- Full Q8 versioning/capability negotiation — post-Plan 2 MVP
- Durable persistence backends and crash recovery — post-Plan 3 in-memory
- Security Guard worker — post-batch (already in AGENTS.md AR10–12 deferral note)
- Cross-platform packaging — explicitly post-v1

---

## Part 4 — What the Panel Should Check in This Pass

The revised split addresses all CRITICAL and HIGH findings from the first pass. The Round Table's job in this pass is:

1. **Does the routing engine move to Plan 3 introduce any new dependency problem?** Plan 2 now ships manifest parser + capability graph only. Plan 3 adds routing engine + lifecycle + state machine + DAG validator. Is Plan 3 now overloaded?

2. **Is the `ICapabilityIndex` / `ITaskStateQuery` interface protocol pattern sufficient to unblock Plan 4?** Or does Plan 4 still need more from Plans 2 and 3 than two named protocols?

3. **Is the relay server deferral clean?** Does deferring the relay server create any gap in the Plan 4 deliverable that makes the core unusable for local UIs?

4. **Is Plan 2 now too small?** With the routing engine removed, Plan 2 is manifest parser + capability graph + `ICapabilityIndex`. Is that too thin for one plan, or is it correctly scoped?

5. **Anything else** not covered above.
