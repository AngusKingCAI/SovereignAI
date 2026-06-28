# Round Table Brief — SovereignAI Plans 1–4 Scope Split

**Brief type**: Pre-draft scope review — no plan files exist yet. The Round Table is reviewing a proposed 4-plan split of the Core Scope (v1) before any plan files are written.

**Brief scaffold**: Per `AI_HANDOFF.md` 3-part scaffold.

---

## Part 1 — Roles and Rules

Your job is to find problems with this scope split, not to ratify it. Assume it will fail — identify how.

- You are reviewing a **proposed scope split only** — not code, not plan files. The question is whether 12 core components are divided across 4 plans in a sensible order, with the right dependencies and the right amount of work per plan.
- Every issue you raise must include a **concrete failure scenario**: what breaks, when, and why.
- Ban style, naming preference, and speculative-future comments. Substance only.
- Explicitly permitted: "No issues found" — do not invent problems to fill space.
- End your response with `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated.

---

## Part 2 — Context

### What is being reviewed

The SovereignAI core has exactly 12 components in its v1 Core Scope (locked — adding to this list requires a Round Table review). These 12 components must be built across Plans 1–4. The Architect has proposed the following split:

| Plan | Components | Open questions resolved |
|---|---|---|
| **Plan 1** | Composition Root, Event Bus, TraceEmitter, DI container (`shared/container.py`) | Q9 (test strategy), Q32 (DEBT.md scaffold) |
| **Plan 2** | Capability manifest parser, Capability graph, Routing engine | Q1 (adapter contract), Q2 (skill discovery), Q4 (routing), Q8 (versioning) |
| **Plan 3** | Lifecycle manager, Task state machine, DAG validator | Q3 (memory abstraction), Q14 (persistence/crash recovery) |
| **Plan 4** | Auth middleware, Capability API, Relay server (stub) | none new |

### The 12 Core Scope components (locked)

1. **Composition root** — the single bootstrap file (`main.py`) that wires all core components explicitly in topological order. No runtime magic, no auto-discovery (Q26, locked).
2. **Event bus** — typed channels, in-process message routing between components.
3. **Capability manifest parser** — reads TOML/JSON manifests from adapters and skills.
4. **Capability graph** — the in-memory index of what's plugged in, populated from manifests.
5. **Routing engine** — matches requests to registered components based on capability declarations.
6. **Lifecycle manager** — starts, health-checks, stops components; manages circuit breaker unloads.
7. **TraceEmitter** — constructor-injected observability substrate; every component receives one.
8. **Task state machine** — RECEIVED → QUEUED → EXECUTING → COMPLETE/FAILED.
9. **DAG validator** — checks skill DAGs for acyclicity and type-matching before execution.
10. **Auth middleware** — login gate, session tokens for all UI connections (local and remote).
11. **Relay server** — E2EE endpoint for remote UIs (phone app, remote web) via WebSocket.
12. **Capability API** — the contract all UIs consume to query state and submit tasks. UIs import nothing from the core directly — they call this API only.

### Key architectural constraints (locked — from `AGENTS.md` and `project-vision-Rev5.md`)

- **AR4**: All shared state lives in the DI container (`shared/container.py`). No global mutable state anywhere.
- **AR5**: ≤15 constructor args per class. `main.py` (Composition Root) is exempt.
- **AR6**: No context bags. Every constructor argument is a single typed dependency.
- **AR7**: UIs consume the Capability API only — no imports from core internals.
- **P11**: DI everywhere — no component instantiates its own dependencies.
- **P9**: No silent failures — every component emits structured traces via TraceEmitter.
- **Q26 (locked)**: `main.py` instantiates all core components explicitly in topological order. No runtime magic.

### Architect's reasoning (attack this — don't ratify it)

**Why Plan 1 gets the DI container + Event Bus + TraceEmitter + Composition Root:**
These are the lowest-level dependencies. Every other component depends on at least one of them. The DI container must exist before anything can be injected. The TraceEmitter must exist before any component can emit observability. The Event Bus must exist before any component can publish or subscribe. The Composition Root wires them together. Nothing in Plans 2–4 is buildable without all four of these. I'm 90% confident this group is correct.

**Why Plan 2 gets the manifest parser + capability graph + routing engine:**
These three form the "discovery layer" — they're logically coupled (parser feeds graph, graph feeds router) and the routing engine is what makes the system actually dispatch work. Without these, Plans 3–4 have nothing to route through. I'm 75% confident the grouping is right but less confident about the size — this may be too much for one plan.

**Why Plan 3 gets lifecycle manager + task state machine + DAG validator:**
The lifecycle manager needs the capability graph (Plan 2) to know what to start/stop. The task state machine needs the event bus (Plan 1) to publish state transitions. The DAG validator is standalone but only becomes useful once skills can be wired (which requires the routing engine from Plan 2). I'm 70% confident on this group — the DAG validator in particular feels like it could move to Plan 4 without breaking anything.

**Why Plan 4 gets auth middleware + Capability API + relay server:**
Auth gates all UI connections, so it should be last in the core build — nothing needs it until a UI tries to connect. The Capability API is the surface UIs consume; it can only be written once the core state it exposes (tasks, capabilities, traces) is wired up by Plans 1–3. The relay server is the most complex component (E2EE WebSocket); I've labelled it a "stub" in Plan 4 — meaning: the WebSocket endpoint and key-generation scaffolding exist, but the full E2EE implementation may be deferred to a later plan. I'm 60% confident on calling the relay server a stub — the Round Table should push back if a stub leaves the system in a broken state for too long.

### Named open questions for the Round Table

**Q-A: Is Plan 2 too large?**
The manifest parser, capability graph, and routing engine are three distinct components. In the old sovereign-ai project, each of these was a multi-day build. If Plan 2 is too large to execute in one session, what's the right split — parser in Plan 2, graph + router in Plan 3, and everything in Plan 3 shifts to Plan 4?

**Q-B: Is the relay server a stub acceptable in Plan 4, or does it block something critical?**
The relay server is the only path for remote UIs (phone app, remote web). If it's a stub, remote UIs don't work until a later plan. The local UI (web, TUI, CLI via local socket) is unaffected. Given v1 is Windows-first and the phone app is a later deliverable, is a relay stub acceptable at Plan 4, or should the relay server be deferred entirely out of the first batch and replaced with a placeholder?

**Q-C: Does the DAG validator belong in Plan 3 or Plan 4?**
The DAG validator is only exercised when a composite skill is submitted. Composite skills require the routing engine (Plan 2) and the task state machine (Plan 3). But the DAG validator itself is a standalone algorithm with no runtime dependencies beyond the schema types defined in Plan 1. Could it move to Plan 4 to reduce Plan 3's scope, or does it logically belong with the task state machine?

**Q-D: What does Plan 1 produce that is independently testable?**
Plan 1's outputs (DI container, Event Bus, TraceEmitter, Composition Root) are infrastructure — they don't do visible work on their own. What tests prove Plan 1 is correct? The Round Table should flag if Plan 1's test surface is too thin to verify the scaffold is actually wired correctly before Plan 2 builds on top of it.

**Q-E: Are there hidden dependencies between Plans 3 and 4 that force a specific ordering?**
The Capability API (Plan 4) exposes task state (Plan 3's state machine) and registered capabilities (Plan 2's capability graph). Auth middleware (Plan 4) sits in front of the Capability API. If the state machine or capability graph have interfaces the Capability API needs to call, those interfaces must be locked before Plan 4 can be written. Does the current split create a risk of Plan 4 discovering it needs to rewrite Plan 3's interfaces mid-execution?

### Architect's confidence by plan

| Plan | Confidence | Where to attack hardest |
|---|---|---|
| Plan 1 | 90% | Test surface — is it thin? |
| Plan 2 | 75% | Size — too large for one plan? |
| Plan 3 | 70% | DAG validator placement; interface contracts Plan 4 will need |
| Plan 4 | 60% | Relay server stub — acceptable or blocks something critical? |

---

## Part 3 — Answer Format

No rigid boxes. Structure your response however makes your reasoning clearest.

For each issue you raise:
- State which plan and which component(s) are affected
- Severity (CRITICAL / HIGH / MEDIUM / LOW) with the rubric: CRITICAL = data loss or irreversible damage; HIGH = execution STOP, broken build, or a dependent plan can't proceed; MEDIUM = degraded output or significant rework risk; LOW = preference or minor risk
- Concrete failure scenario: what breaks, when, and why
- A proposed fix (optional but preferred)

Open field: flag anything not covered by the named questions above.

Explicitly permitted: "No issues found" or "Clean pass" if you find nothing substantive.

End with `**Panelist**: <your name/model>`.
