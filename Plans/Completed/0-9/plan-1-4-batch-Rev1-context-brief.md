# Round Table Brief — SovereignAI Plans 1–4 Batch (First Architectural Batch)

**Brief type**: Pre-execution review of 4 individual plan files drafted as a batch. Per AI_HANDOFF.md batch process: N individual plan files + 1 shared context brief. Round Table reviews all 5 documents together.

**Brief scaffold**: Per `AI_HANDOFF.md` 3-part scaffold.

**Documents to review**:
- `plan-1-Rev1.md` — Core Scaffold (Event Bus, TraceEmitter, DI container, shared/types.py, Composition Root)
- `plan-2-Rev1.md` — Discovery Layer (manifest parser, capability graph, ICapabilityIndex)
- `plan-3-Rev1.md` — Execution Layer (routing engine, lifecycle, task state machine, DAG validator, ITaskStateQuery)
- `plan-4-Rev1.md` — Interface Layer (auth, Capability API, relay placeholder, Q26 audit)
- This brief

---

## Part 1 — Roles and Rules

Your job is to find issues with these 4 plans, not to ratify them. Assume they will fail — identify how.

- You are reviewing **architectural plan files** — not code (no code exists yet). The plans will be executed sequentially by an Executor (Devin) following the S0–S8 structure in each file.
- Every issue you raise must include a **concrete failure scenario**: what breaks, when (which plan, which step), and why.
- Ban style, naming preference, and speculative-future comments. Substance only.
- Explicitly permitted: "No issues found" — do not invent problems to fill space.
- End your response with `**Panelist**: <your name/model>`. Anonymous responses will be flagged but still adjudicated; named responses are preferred for accountability.

**Severity rubric** (per AI_HANDOFF.md):
- **CRITICAL**: Would cause data loss, security vulnerability, or irreversible system damage. Blocks clean pass — no exceptions.
- **HIGH**: Would cause an Executor STOP condition, test failure, broken build, or Windows incompatibility. Blocks clean pass.
- **MEDIUM**: Degraded functionality, poor UX, or technical debt that should be addressed before execution but won't necessarily cause failure.
- **LOW**: Style, formatting, naming preferences, or speculative future concerns.

---

## Part 2 — Context

### What is being reviewed

This is the **first architectural batch** of SovereignAI. Plans 1–4 implement the 12-item Core Scope (v1) from `project-vision-Rev5.md`. The scope split was already round-table-reviewed and adjudicated — see `documents/plan-1-4-scope-adjudication.md` for the 9 accepted findings (A1–A9) and 3 rejected (R1–R3). **Do not re-litigate the scope split.** The plans below implement the locked split; your job is to find issues with the *implementation details*, not the scope.

### Repo state at start of batch

After prompt-0 through prompt-0.4 (5 mechanical cleanup plans), the repo has:
- 12 governance docs at root (`AGENTS.md`, `AI_HANDOFF.md`, `PLANS.md`, `CHANGELOG.md`, `LANDMINES.md`, `DECISIONS.md`, `DEBT.md`, `README.md`, `.gitignore`, `pyproject.toml`, `.pre-commit-config.yaml`, `txt/requirements.txt`, `txt/vulture-whitelist.txt`, `txt/.secrets.baseline`)
- 4 workflow files in `.devin/workflows/` (open, verify, close, scan — all use absolute venv paths per OR46)
- Empty directory structure: `sovereignai/{orchestrator,managers,workers,librarian,adapters,adapters/external,skills,skills/user,skills/external,shared}`, `web/`, `cli/`, `tui/`, `phone/`, `tests/`, `logs/`
- Project-local venv at `.venv/` (Python 3.11, dev deps installed, gitignored)
- 5 tags: `prompt-0` through `prompt-0.4`
- 47 AR/OR rules in AGENTS.md (AR1–AR21, OR1–OR47); 31 landmines in LANDMINES.md (L1–L9, L11, L12, L17 inherited; L24–L31 SovereignAI-specific)
- **No Python code yet** — Plans 1–4 are the first code

### The 4 plans (scope summary)

| Plan | Components | Locked deliverables | Open Qs resolved |
|---|---|---|---|
| **Plan 1** | Event Bus (in-order per channel per A9), TraceEmitter (singleton), DI container (passive registry per A8), `shared/types.py` (frozen dataclasses per A2), Composition Root (incremental per A3 — wires Plan 1 components only) | Wiring tests; event bus ordering tests; `shared/types.py` frozen types | Q9 (test strategy), Q32 (DEBT.md scaffold — already done) |
| **Plan 2** | Capability manifest parser (TOML), Capability graph → ships `ICapabilityIndex` protocol (A5) | `ICapabilityIndex` as locked named output; manifest schema; Q8 MVP only | Q1, Q2, Q8 (MVP) |
| **Plan 3** | Routing engine (uses Lifecycle Manager per A1), Lifecycle manager (circuit breaker per AR16), Task state machine → ships `ITaskStateQuery` protocol (A5), DAG validator (per A6), persistence in-memory only (per A7) | `ITaskStateQuery` as locked named output; event-store interface + in-memory replay | Q3 (interface), Q4 (routing), Q14 (in-memory) |
| **Plan 4** | Auth middleware (PBKDF2, 8h tokens), Capability API (consumes `ICapabilityIndex` + `ITaskStateQuery` only — AR7 enforced via static-import test), local-only relay placeholder (per A4 — returns structured error, does not accept connections), Composition Root final wiring audit (Q26 confirmed at `/close`) | Static-import test proving Capability API has no transitive core imports (AR7); Q26 confirmed; relay placeholder emits structured error | Q26 (confirmed at close) |

### Cross-plan dependency map (locked)

```
Plan 1 ──► Plan 2 ──► Plan 3 ──► Plan 4
           (ICapabilityIndex)  (ITaskStateQuery)
```

- Plan 2 depends on Plan 1's `shared/types.py` for manifest and capability types
- Plan 3 depends on Plan 2's `ICapabilityIndex` for routing and lifecycle queries
- Plan 4 depends on Plan 2's `ICapabilityIndex` and Plan 3's `ITaskStateQuery` for the Capability API; never imports core internals directly (AR7)

### Key architectural constraints (from AGENTS.md — already locked)

- **AR4**: All shared state in the DI container (`shared/container.py`). No global mutable state. `shared/` holds contracts, interfaces, and the DI container only.
- **AR5**: ≤15 constructor args per class. `main.py` (Composition Root) is exempt.
- **AR6**: No context bags. TraceEmitter is permitted as a typed single-responsibility argument, NOT a vehicle for bypassing explicit-argument discipline.
- **AR7**: UIs consume the Capability API only. No imports from `sovereignai/` internals.
- **AR9**: No hard-coded component names at runtime. Capability graph is the discovery path.
- **AR16**: Circuit breaker — >50 errors in 10 seconds triggers automatic unload.
- **AR21**: Every `def`/`async def` has a docstring. First line: verb-first, ≥10 words, plain English, no jargon.
- **OR39**: Runtime deps in `txt/requirements.txt` only. `pyproject.toml` uses `dynamic = ["dependencies"]`.
- **OR46**: Workflow commands use absolute venv paths (`.venv/Scripts/python.exe`), not `source activate`.
- **OR47**: Mypy on `.py` files only — never markdown.

### Architect's reasoning (attack this — don't ratify it)

**1. Why Plan 1 starts with `shared/types.py` (A2):**
Without a canonical type module in Plan 1, every downstream plan invents its own `Task`, `CapabilityDeclaration`, `ComponentManifest`, and `TraceEvent` types. By Plan 4 they would have drifted and the Capability API could not speak the same types as the state machine. Putting types in Plan 1 means Plans 2–4 import from one place. **Author confidence: 95%.**

**2. Why the event bus guarantees in-order delivery per channel (A9):**
Plan 3's task state machine publishes state transitions as events. If the bus does not guarantee ordering, transitions can arrive out of order and produce invalid state (e.g. a subscriber sees EXECUTING before RECEIVED). In-order per channel is the minimum guarantee that makes the state machine correct. Cross-channel ordering is NOT guaranteed — that would force serialization across unrelated event types. **Author confidence: 90%.**

**3. Why the DI container is passive (A8 — no `@inject`, no auto-wiring):**
Auto-wiring is "runtime magic" — Q26 explicitly forbids it ("no runtime magic, no auto-discovery"). A passive registry means `main.py` does all explicit instantiation in topological order, making the full dependency graph auditable in one file. The trade-off is verbosity: `main.py` grows with each plan. But that's the point — every wiring decision is visible. **Author confidence: 90%.**

**4. Why the Composition Root is incremental (A3 — not final in Plan 1):**
Writing the final `main.py` in Plan 1 when only Plan 1 components exist would force Plans 2, 3, and 4 to each rewrite the system's single bootstrap file — each edit risks breaking topological order and Plan 1's regression tests. Instead, each plan extends `build_container()`. Plan 4 performs the final audit and Q26 is confirmed there. **Author confidence: 85%.**

**5. Why Plan 2 ships `ICapabilityIndex` as a Protocol (A5):**
Plan 4's Capability API cannot be drafted if Plan 2's capability graph and Plan 3's task state machine do not expose locked query interfaces. Using `typing.Protocol` (structural subtyping) means Plan 4 imports the protocol, not the concrete class — AR7 enforcement is a static-import test, not a runtime check. The trade-off: Protocol doesn't enforce implementation at runtime (a class that doesn't implement the methods would still pass `isinstance` via Protocol's default `runtime_checkable` behavior). But the test suite catches missing methods. **Author confidence: 80%.**

**6. Why the routing engine moved to Plan 3 (A1):**
The routing engine must know whether a component is ACTIVE, DEGRADED, or CIRCUIT_BROKEN — that's the Lifecycle Manager's job (Plan 3). A router built in Plan 2 (before the Lifecycle Manager) would be a static dispatcher that requires a rewrite when Plan 3 lands. Co-locating them in Plan 3 means the router can query the lifecycle manager from day one. **Author confidence: 90%.**

**7. Why the DAG validator stays in Plan 3 (A6):**
If Plan 3's state machine accepts composite skill tasks without validating their DAG, composite tasks enter the state machine unvalidated until Plan 4 — a silent failure (P9 violation). The validator is a prerequisite for composite tasks entering the state machine safely. It stays in Plan 3 alongside the state machine. **Author confidence: 85%.**

**8. Why persistence is in-memory only in Plan 3 (A7):**
Full event-sourced persistence + crash recovery + durable backends in Plan 3 alongside four other components is too much. In-memory replay establishes the event-store interface; durable backends are deferred to DEBT. The trade-off: on crash, all task state is lost. Acceptable for v1 single-user local-first. **Author confidence: 80%.**

**9. Why the relay server is a placeholder in Plan 4 (A4):**
A relay stub that accepts connections without E2EE means Auth Middleware and Capability API are designed around plaintext — retrofitting E2EE later forces a complete rewrite. A stub that does nothing means Plan 4 ships an incomplete component. The placeholder returns a structured error ("remote transport not yet supported") and emits a trace — it does not accept connections. Remote UIs are explicitly a later deliverable. **Author confidence: 85%.**

**10. Why `submit_task` in Plan 4's Capability API is a stub:**
The full routing pipeline (Plan 3's RoutingEngine → a Worker dispatch) is post-batch. Plan 4's `submit_task` validates the token, creates a Task object, emits a trace, and returns a UUID — but does NOT actually route the task to a worker. This is documented explicitly in the plan and the code. The alternative (implementing full routing in Plan 4) would balloon Plan 4's scope. **Author confidence: 70%.** — this is the weakest point. The Round Table should push back if a stub leaves the system in a state where Plans 6–9 can't build on it cleanly.

### Architect's confidence by plan

| Plan | Confidence | Where to attack hardest |
|---|---|---|
| Plan 1 | 90% | Test surface — is 22 tests enough to verify the scaffold? Is the event bus ordering test sufficient? |
| Plan 2 | 80% | Manifest schema — is TOML the right choice? Is the parser too permissive? Does `ICapabilityIndex` expose enough for Plan 4? |
| Plan 3 | 75% | Circuit breaker timing — is the 10-second window test reliable? Does the DAG validator handle all composite skill patterns? Is in-memory persistence a real problem? |
| Plan 4 | 65% | `submit_task` stub — does it leave a gap? Is PBKDF2 with 100k iterations sufficient? Does the AR7 static-import test actually enforce AR7? |

### Sequencing risks

- **Plan 2 depends on Plan 1's `shared/types.py`** — if Plan 1's types are wrong, Plan 2 inherits the error. The Round Table should verify Plan 1's types are sufficient for Plan 2's needs.
- **Plan 3 depends on Plan 2's `ICapabilityIndex`** — if the protocol is missing a method Plan 3 needs, Plan 3 stops. The Round Table should verify the protocol's method set.
- **Plan 4 depends on both protocols** — if either is insufficient, Plan 4 can't be drafted.
- **All 4 plans execute sequentially** — a STOP in any plan halts all subsequent plans that depend on it (per AI_HANDOFF.md execution-failure-within-a-batch rule).

### Named open questions for the Round Table

**Q-A: Is Plan 1's `shared/types.py` sufficient for Plans 2–4?**
Plan 1 defines: `TraceLevel`, `TraceEvent`, `Channel`, `Event`, `ComponentId`, helpers (`now_utc`, `new_correlation_id`). Plan 2 adds: `CapabilityCategory`, `CapabilityDeclaration`, `ComponentManifest`. Plan 3 adds: `TaskState`, `TaskStateChanged`, `Task`, `ComponentStatus`, `TASK_STATE_CHANNEL`. Plan 4 adds: `SessionToken`, `AuthError`, `CapabilityQuery`, `CapabilityResponse`. Is this incremental approach (each plan extends `shared/types.py`) sound, or should all types be defined upfront in Plan 1?

**Q-B: Is the event bus's "in-order per channel" guarantee testable?**
Plan 1's `test_multiple_subscribers_receive_in_registration_order` verifies registration order. Plan 3's `test_transitions_published_in_order` verifies task state transitions arrive in order. Is this sufficient to prove A9, or are there edge cases (concurrent publishers, slow subscribers) the tests miss?

**Q-C: Does the `ICapabilityIndex` protocol expose enough for Plan 3's RoutingEngine?**
Plan 2's `ICapabilityIndex` has `find_providers(category, name)` and `list_all_components()`. Plan 3's RoutingEngine calls `find_providers()` then filters by lifecycle status. Is this sufficient, or does Plan 3 need additional query methods (e.g. `find_by_priority_threshold()`)?

**Q-D: Is the circuit breaker's 10-second rolling window reliable?**
Plan 3's LifecycleManager uses `time.monotonic()` and a `deque` to track errors in a rolling 10-second window. Test 5 (`test_old_errors_expire_from_window`) uses `unittest.mock.patch` on `monotonic`. Is this a reliable test, or does it mask real-world timing issues (clock drift, GC pauses)?

**Q-E: Is Plan 4's `submit_task` stub acceptable?**
The stub validates the token, creates a Task, emits a trace, returns a UUID — but does not route to a worker. The task is NOT submitted to the TaskStateMachine (the comment notes this). Is this acceptable for Plan 4, or does it create a gap where the Capability API appears to accept tasks but they vanish? Should the stub at least call `TaskStateMachine.submit()` so the task is trackable, even if no worker picks it up?

**Q-F: Does the AR7 static-import test actually enforce AR7?**
Plan 4's `test_ar7_no_core_imports_in_ui.py` uses `ast.parse` to scan imports. It checks for a denylist of module names. Is this sufficient, or could a UI import a core module via a different path (e.g. `from sovereignai.shared import event_bus` vs `import sovereignai.shared.event_bus`)? Should the test also check `from ... import` forms?

**Q-G: Is the relay placeholder's "structured error" actually structured?**
Plan 4's RelayPlaceholder returns a plain string (`RELAY_NOT_SUPPORTED_MESSAGE`). The plan calls this a "structured error" but it's just a string. Should it return a typed error object (e.g. `RelayNotSupportedError`) so callers can distinguish it from other errors programmatically?

### Vision principle compliance

Each plan's header lists which principles it satisfies. Cross-reference:

| Plan | Principles claimed | Verification |
|---|---|---|
| Plan 1 | 1, 5, 7, 9, 11, 12, 13 | P1 (sacred core — minimal types), P5 (wire as you go — only types Plan 1+ need), P7 (modular — DI + bus + trace are separate), P9 (TraceEmitter), P11 (DI, no globals), P12 (docstrings), P13 (robust — bus catches subscriber errors) |
| Plan 2 | 1, 2, 3, 5, 7, 9, 11, 12, 13 | P2 (pluggable — manifest + graph), P3 (no lock-in — capability-based discovery), P5 (manifest schema is the contract), P7 (modular), P9 (graph emits traces), P11 (DI), P12 (docstrings), P13 (robust) |
| Plan 3 | 1, 5, 7, 9, 11, 12, 13 | P5 (wire as you go — in-memory only), P7 (modular — 4 separate components), P9 (state transitions traced), P11 (DI), P12 (docstrings), P13 (robust — invalid transitions logged not raised) |
| Plan 4 | 1, 2, 3, 5, 7, 8, 9, 11, 12, 13, 14 | P8 (UIs separate processes consuming Capability API), P14 (provenance — auth is the gate; full provenance deferred with adapters) |

The Round Table should verify these claims are accurate — flag any principle claimed but not actually satisfied by the plan's content.

### What is explicitly deferred (DEBT items — already in DEBT.md or to be added)

- Relay server E2EE implementation — post-batch, dedicated plan (A4)
- Full Q8 versioning/capability negotiation — post-Plan 2 MVP (already in DEBT)
- Durable persistence backends and crash recovery — post-Plan 3 in-memory (A7, to be added in Plan 3)
- Security Guard worker — post-batch (already in AGENTS.md AR10–12 deferral note)
- Cross-platform packaging — explicitly post-v1 (already in DEBT)
- Memory abstraction implementation — post Plan 4 (to be added in Plan 3)
- Full routing pipeline (Worker dispatch from RoutingEngine) — post-batch (noted in Plan 4's `submit_task` stub)
- Real UI implementations (web, CLI, TUI, phone) — post-batch (the AR7 test will activate once UI files exist)

---

## Part 3 — Answer Format

Structure your response flexibly. Suggested sections:

1. **Pre-mortem** — "Assume the batch failed in 6 months. List the 3–5 most plausible reasons why." Focus on failures introduced by these 4 plans, not failures the scope adjudication already addressed.

2. **Issues by plan** — For each plan (1, 2, 3, 4), list issues with:
   - Severity (CRITICAL / HIGH / MEDIUM / LOW)
   - Concrete failure scenario (which step, what breaks, why)
   - Proposed fix (optional but preferred)

3. **Cross-plan issues** — Issues that span multiple plans (e.g. protocol sufficiency, type drift, sequencing risks).

4. **Open question engagement** — For each named question (Q-A through Q-G), propose a resolution or explain why the question is malformed.

5. **Vision principle compliance check** — Verify each plan's claimed principles are actually satisfied. Flag any false claims.

6. **Other concerns** — Anything not covered above.

7. **Sign-off** — `**Panelist**: <name/model>` (mandatory per GR3).

You may respond with "No issues found" or "Clean pass" for any plan if you genuinely find nothing. Do not invent problems to fill space. Each issue must cite a concrete failure scenario and evidence from the plan file.

**Ban**: style/formatting comments, speculative future features, naming preferences, "consider also..." suggestions without a failure scenario.

---

## Adjudication note (for the user, not the panel)

The Architect will collect all panel responses and adjudicate per the AI_HANDOFF.md severity rubric. A clean pass requires:
- (a) No panelist reports a substantiated CRITICAL or HIGH issue that hasn't been addressed.
- (b) Any remaining MEDIUM/LOW items are documented as accepted/rejected with reasoning.

If clean pass: User copies the 4 plan files to `C:/SovereignAI/prompts/plan-{1,2,3,4}.md` and points the Executor at Plan 1.

If not clean pass: Architect applies findings to produce Rev2 files. Rev2+ does not need a new brief — the Round Table reviews the revised files directly.

---

*Plan 1-4 Batch Context Brief. Rev1. Architect draft. Per AI_HANDOFF.md batch process: 4 individual plan files + 1 shared brief. Round Table reviews all 5 together.*
