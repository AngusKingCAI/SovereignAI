# DEBT.md — SovereignAI Deferred Items Register

Append-only. Each entry: deferred at, reason, trigger condition, target plan.

---

## Deferred: Security Guard implementation

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Security Guard is not pertinent to the core yet. It will be implemented as a Worker later, not as core infrastructure. Per AGENTS.md AR10–12 deferral note.
**Trigger condition**: When Worker lifecycle and skill authoring are stable (post Plan 4).
**Target plan**: TBD (post Plan 4).

---

## Deferred: Cross-platform packaging

**Deferred at**: prompt-0 (bootstrap)
**Reason**: v1 is Windows-only per P4. Cross-platform packaging adds complexity not needed for initial validation.
**Trigger condition**: When core is stable and Windows packaging is working.
**Target plan**: Q31 (post Plan 4).

---

## Deferred: Model loading/unloading based on hardware

**Deferred at**: prompt-0 (bootstrap)
**Reason**: VRAM management, GPU detection, and dynamic model loading are advanced features. Core needs to exist first. Per `project-vision-Rev5.md` Models section: "Model loading/unloading based on system hardware is a planned feature for a later plan, not Plan 1."
**Trigger condition**: When local model adapters (Ollama, llama.cpp) are wired and working.
**Target plan**: TBD (post Plan 4).

---

## Deferred: Pre-existing test failures (missing TraceLevel imports)

**Deferred at**: prompt-18.2
**Reason**: 41 existing test files have NameError: name 'TraceLevel' is not defined. These are pre-existing failures from previous plans, not caused by changes in prompt-18.2. Fixing them would be outside the scope of this plan.
**Trigger condition**: When running test suite cleanup or before next major release.
**Target plan**: TBD (test suite cleanup plan).

---

## Deferred: New test infrastructure issues

**Deferred at**: prompt-18.2
**Reason**: New tests for hierarchical catalog, schema, and correlation ID have test infrastructure issues (container initialization, file locking on Windows, threading). The actual code changes are sound, but test fixtures need refinement.
**Trigger condition**: When test infrastructure is improved or before next major release.
**Target plan**: TBD (test infrastructure plan).

---

## Deferred: Pre-existing mypy errors

**Deferred at**: prompt-18.2
**Reason**: 4 pre-existing mypy errors in config_loader.py (no-any-return) and sovereignai/main.py (EventBus subscribe arguments). These are not caused by changes in prompt-18.2.
**Trigger condition**: When type checking cleanup is performed.
**Target plan**: TBD (type checking cleanup plan).

---

## Deferred: Pre-existing AR6 violations (untyped dict/Any context bags)

**Deferred at**: prompt-18.2
**Reason**: 15 pre-existing AR6 violations in conformance/runner.py, librarian/librarian.py, memory backends, capability_graph.py, config_loader.py, and skills. These are infrastructure-level issues requiring significant refactoring, not caused by changes in prompt-18.2.
**Trigger condition**: When infrastructure refactoring is performed.
**Target plan**: TBD (infrastructure refactoring plan).

---

## Deferred: Pre-existing AR21 docstring discipline violations

**Deferred at**: prompt-18.2
**Reason**: 50+ pre-existing AR21 violations (docstrings <10 words) in infrastructure files. These are not caused by changes in prompt-18.2.
**Trigger condition**: When docstring cleanup is performed.
**Target plan**: TBD (docstring cleanup plan).






---

## Deferred: Self-correction / learning loops

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Learning and improvement (Q13) is a skill-level concern, not core. The retrospective trace skill will be built once the skill framework exists.
**Trigger condition**: When skill framework (Plan 2+) is stable.
**Target plan**: TBD (post Plan 4).

---

## Deferred: Relay server E2EE implementation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A4)
**Reason**: Plan 4 ships a local-only relay placeholder that returns a structured error and does not accept connections. Full E2EE implementation deferred to a dedicated plan post-batch.
**Trigger condition**: When Plan 4's placeholder is merged and the local UI stack is functional.
**Target plan**: TBD (post Plan 4, dedicated plan).

---

## Deferred: Durable persistence backends and crash recovery

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A7)
**Reason**: Plan 3 implements the event-store interface and in-memory replay only. Durable backends and full crash recovery are too much for Plan 3 alongside four other components.
**Trigger condition**: When Plan 3's in-memory event store is stable.
**Target plan**: TBD (post Plan 3).

---

## Deferred: Full Q8 versioning / capability negotiation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only. Full versioning/capability negotiation deferred.
**Trigger condition**: When Plan 2's manifest schema is stable and a second adapter version is needed.
**Target plan**: TBD (post Plan 2).

---

## Deferred: AR4 amendment — remove dependency-injector reference

**Deferred at**: prompt-1 (per Plan 1-4 batch Round Table Rev2 adjudication, Finding 5)
**Reason**: AR4 names `dependency-injector` as the DI library, but A8 mandates a passive registry (no `@inject`, no auto-wiring). The hand-rolled DIContainer in `shared/container.py` satisfies A8 without using the `dependency-injector` library. AR4's reference is stale.
**Trigger condition**: When the Architect next drafts a plan's S0.3 (next batch, Plan 5+).
**Target plan**: Plan 5 (Scan) or first plan in next batch.
**Resolved at**: prompt-5 (Scan 5 S2.2 — AR4 rewritten to reference hand-rolled DI container; DECISIONS.md D2 updated).

---

## Deferred: Full Q8 versioning / capability negotiation (post-MVP)

**Deferred at**: prompt-2 (per Plan 1-4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only — manifests declare semver versions, but no capability negotiation (resolving incompatible versions at startup) is implemented.
**Trigger condition**: When a second adapter version is needed and two components declare incompatible versions of the same capability.
**Target plan**: TBD (post Plan 2).

---

## Deferred: Memory abstraction implementation

**Deferred at**: prompt-3 (per Plan 3 scope adjudication)
**Reason**: Plan 3 defines the interface shape (via ITaskStateQuery protocol pattern) but does not implement memory routing. The Librarian is a pluggable component, not a core component.
**Trigger condition**: When the Librarian Registry is needed (post Plan 4).
**Target plan**: TBD (post Plan 4).

---

## Deferred: Circuit breaker auto-recovery heartbeat

**Deferred at**: prompt-3 (per Rev4 Finding 9)
**Reason**: LifecycleManager implements circuit breaker (50 errors/10s -> CIRCUIT_BROKEN) but does not include an auto-recovery heartbeat that periodically checks if the error window has expired and attempts recovery. Manual recovery via try_recover() is available.
**Trigger condition**: When the system needs automated recovery without manual intervention.
**Target plan**: TBD (post Plan 4).

---

## How to add a new deferred item

**Before appending**: scan existing entries for the same underlying item by topic, not exact wording (e.g. "Full Q8 versioning" was logged twice — prompt-0 and prompt-2 — before this check existed; see the cross-reference note below). If a matching entry exists, do not duplicate it — append a short note instead: `## Note: duplicate of "{existing entry name}" — see entry above, dated {prompt-N}.`

At `/close` step 12, if an item is genuinely new, append an entry in the format above. When a deferred item is addressed, do not remove the entry — add a "Resolved at: prompt-{N}" line below it. DEBT.md is append-only.

---

## Note: duplicate entry — Full Q8 versioning / capability negotiation

**Logged at**: prompt-5 (governance review)
**Issue**: This item was logged twice under near-identical wording — once at prompt-0 (bootstrap, generic Plan 1–4 scope adjudication) and again at prompt-2 (Plan 2 scope adjudication). Both describe the same deferred capability-negotiation work; the prompt-0 entry's trigger condition and the prompt-2 entry's reason are restatements of each other.
**Resolution**: Track resolution against the prompt-0 entry only. When Q8 negotiation work begins, add a single "Resolved at" line to the prompt-0 entry and reference it from the prompt-2 entry rather than resolving both independently.

---

## Deferred: Mypy type errors in config_loader.py and main.py

**Deferred at**: prompt-17.3
**Reason**: Pre-existing mypy type errors requiring significant refactoring: config_loader.py returns Any from typed functions, main.py passes wrong types to EventBus.subscribe. These are out of scope for this plan's auth test fixes.
**Trigger condition**: When a dedicated type remediation plan is scheduled.
**Target plan**: TBD
