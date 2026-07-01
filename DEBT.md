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
**Reason**: VRAM management, GPU detection, and dynamic model loading are advanced features. Core needs to exist first. Per `principles.md` Models section: "Model loading/unloading based on system hardware is a planned feature for a later plan, not Plan 1."
**Trigger condition**: When local model adapters (Ollama, llama.cpp) are wired and working.
**Target plan**: TBD (post Plan 4).

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

## Deferred: TeacherWorker.curate_dataset() criteria parameter

**Deferred at**: prompt-15.1
**Reason**: Tests in test_teacher_worker.py pass a `criteria` parameter to `curate_dataset()` but the actual implementation signature doesn't accept it. This causes 3 test failures (test_curate_dataset_consent_false, test_curate_dataset_pii_filter, test_curate_dataset_retention_filter). The parameter was likely added to tests but not to the implementation during Plan 14.
**Trigger condition**: When TeacherWorker implementation is updated to match test expectations.
**Target plan**: Plan 16 or next Education department plan.
**Status**: Still failing at prompt-16 (3 tests). Not in scope for Logs panel implementation.

---

## Deferred: AR6 violations - memory backend dict parameters

**Deferred at**: prompt-15.1
**Reason**: Memory backend interfaces (episodic, procedural, trace, working) and Librarian use `dict` parameters for data/query. This violates AR6 (no untyped dict/Any context bags) but is a foundational architectural pattern. Refactoring would require defining typed dataclasses for all memory operations, which is a significant scope change.
**Trigger condition**: When memory backend interfaces are redesigned with typed contracts.
**Target plan**: TBD (major memory system refactoring).

---

## Deferred: AR21 violations - docstring discipline

**Deferred at**: prompt-15.1
**Reason**: Multiple components have docstrings that don't meet AR21 requirements (≥10 words, verb-first, no jargon). These include conformance framework, versioning components, and self-correction skill. Fixing all violations would be a large docstring rewrite effort across many files.
**Trigger condition**: When a focused docstring cleanup plan is scheduled.
**Target plan**: TBD (docs-only cleanup plan).
**Resolved at**: prompt-cleanup (AR21 retired in workflow rev 12. Docstrings now prohibited per AR17. Reversed by design — see DECISIONS.md D6.)

---

## Deferred: TeacherWorker.curate_dataset() criteria parameter

**Deferred at**: prompt-15.1
**Reason**: Tests in test_teacher_worker.py pass a `criteria` parameter to `curate_dataset()` but the actual implementation signature doesn't accept it. This causes 3 test failures (test_curate_dataset_consent_false, test_curate_dataset_pii_filter, test_curate_dataset_retention_filter). The parameter was likely added to tests but not to the implementation during Plan 14.
**Trigger condition**: When TeacherWorker implementation is updated to match test expectations.
**Target plan**: Plan 16 or next Education department plan.
**Status**: Still failing at prompt-17 (3 tests). Not in scope for Plan 17 (Database/Service providers).
