# DEBT.md — SovereignAI Deferred Items Register

Append-only. Each entry: deferred at, reason, trigger condition, target plan.

---

## Deferred: First-run experience UI edits

**Deferred at**: prompt-19
**Reason**: Plan 19 S3.3 UI edits (web/templates/index.html, web/static/app.js) deferred to focus on backend API and tests. Backend /api/first-run-check endpoint is complete and tested.
**Trigger condition**: When backend first-run check is validated in production use.
**Target plan**: TBD (post Plan 19)

---

## Deferred: llama-cpp-python binary testing

**Deferred at**: prompt-19
**Reason**: llama-cpp-python 0.2.50 added to requirements.txt but not tested with real binary. Need validation before v1.0 release.
**Trigger condition**: When preparing for v1.0 release or when llama.cpp adapter is used in production.
**Target plan**: TBD (pre v1.0)

---

## Deferred: generate() timeout

**Deferred at**: prompt-19
**Reason**: Cross-platform timeout infrastructure is non-trivial. LlamaCppAdapter.generate() currently has no timeout protection.
**Trigger condition**: When cross-platform timeout infrastructure is implemented.
**Target plan**: TBD (post Plan 19)

---

## Deferred: health_check caching in RoutingEngine

**Deferred at**: prompt-19
**Reason**: TTL cache adds statefulness to RoutingEngine. Current implementation calls health_check() on every route() invocation.
**Trigger condition**: When performance profiling shows health_check() is a bottleneck.
**Target plan**: TBD (post Plan 19)

---

## Deferred: subscribe_callback bounded queue

**Deferred at**: prompt-19
**Reason**: Per-subscriber queue + drain thread adds complexity. Current implementation uses unbounded queues.
**Trigger condition**: When memory pressure or queue overflow issues are observed.
**Target plan**: TBD (post Plan 19)

---

## Deferred: AdapterCapability enum for GPU probing

**Deferred at**: prompt-19
**Reason**: GPU capability probing is adapter-specific. Future adapters must add their own probe in health_check(). A centralized AdapterCapability enum would standardize this but is deferred.
**Trigger condition**: When multiple adapters with different GPU capabilities are implemented.
**Target plan**: TBD (post Plan 19)

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
**Resolved at**: prompt-20.1 (TeacherWorker implementation and all tests removed per user request).

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

---

## Deferred: GPU bandwidth lookup is substring-based placeholder

**Deferred at**: prompt-18
**Reason**: GPU memory type and bandwidth lookup in hardware_probe.py uses substring matching on GPU names (e.g., "RTX 4090" -> "GDDR6X"). This is a best-effort placeholder that may miss GPUs or misclassify them. Accurate lookup requires PCI-ID-based detection.
**Trigger condition**: When GPU detection accuracy is needed for production deployments.
**Target plan**: Plan-19 or later.
**Resolved at**: prompt-20.1 (added exact PCI-ID mapping for RTX 3060 Laptop and common GPUs to hardware_probe.py).

---

## Deferred: setuptools vulnerabilities (transitive dependency)

**Deferred at**: prompt-18
**Reason**: pip-audit reports 5 known vulnerabilities in setuptools 65.5.0 (transitive dependency from Python 3.11.9): CVE-2022-43012, CVE-2024-6345, and PYSEC-2025-49. These are ReDoS and path traversal vulnerabilities in package_index.py. Upgrading setuptools may break compatibility with Python 3.11.9.
**Trigger condition**: When upgrading to a newer Python version that bundles a patched setuptools.
**Target plan**: TBD (Python version upgrade plan).

---

## Deferred: llama-cpp-python 0.2.50 testing

**Deferred at**: prompt-19
**Reason**: llama-cpp-python 0.2.50 added as dependency but not tested with real binary. Need to verify compatibility with actual GGUF models and GPU offload before v1.0.
**Trigger condition**: Before v1.0 release or when real model testing infrastructure is available.
**Target plan**: TBD (pre-v1.0 testing plan).

---

## Deferred: generate() timeout implementation

**Deferred at**: prompt-19
**Reason**: generate() in llama_cpp_adapter has no timeout mechanism. Cross-platform timeout infrastructure is non-trivial (signal handling differs on Windows vs Unix). Defer to post-Plan-19.
**Trigger condition**: When timeout infrastructure is implemented across adapters.
**Target plan**: TBD (post-Plan-19).

---

## Deferred: health_check caching in RoutingEngine

**Deferred at**: prompt-19
**Reason**: health_check() is called on every route() invocation. TTL cache would reduce overhead but adds statefulness. Defer to post-Plan-19.
**Trigger condition**: When performance profiling shows health_check overhead is significant.
**Target plan**: TBD (post-Plan-19).

---

## Deferred: subscribe_callback bounded queue

**Deferred at**: prompt-19
**Reason**: TraceEmitter.subscribe_callback needs per-subscriber bounded queue + drain thread to prevent memory leaks. Current implementation may accumulate unprocessed callbacks. Defer to post-Plan-19.
**Trigger condition**: When callback-based tracing shows memory growth in production.
**Target plan**: TBD (post-Plan-19).

---

## Deferred: AdapterCapability enum for GPU capability probing

**Deferred at**: prompt-19
**Reason**: GPU capability probing is adapter-specific (llama-cpp has llama_supports_gpu_offload(), other adapters may have different probes). Future adapters must add their own probe in health_check(). Defer AdapterCapability enum to post-Plan-19.
**Trigger condition**: When a third adapter with different GPU probing needs is added.
**Target plan**: TBD (post-Plan-19).

---

## Deferred: generate() metadata-only path documentation

**Deferred at**: prompt-19
**Reason**: generate() has side effect of loading model into VRAM. For metadata-only queries, users should call database_registry.find_model() directly. This is a documentation note, no code change needed.
**Trigger condition**: N/A (documentation only).
**Target plan**: N/A (documented in adapter docstring).
**Resolved at**: prompt-20.1 (added DEBUG trace emit to llama_cpp_adapter.generate() for metadata-only path documentation).

---

## Deferred: diskcache CVE-2025-69872 (transitive dependency)

**Deferred at**: prompt-20.1
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive dependency from huggingface_hub). This is a path traversal vulnerability. Upgrading diskcache may break compatibility with huggingface_hub.
**Trigger condition**: When huggingface_hub updates to a version that uses a patched diskcache or when upgrading to a newer huggingface_hub version.
**Target plan**: TBD (dependency upgrade plan).
**Status**: Still present at prompt-20.2 (no dependency changes in this plan).

---

## Deferred: hardware_probe.py GPU path coverage gap

**Deferred at**: prompt-20
**Reason**: hardware_probe.py has 55% coverage (83% overall sovereignai coverage). GPU detection paths (nvidia-smi subprocess calls, pynvml/nvidia-ml-py library calls) are hard to test without actual NVIDIA hardware. These paths require GPU hardware or complex mocking that may not reflect real behavior.
**Trigger condition**: When GPU hardware testing infrastructure is available or when mocking strategy is validated against real GPU behavior.
**Target plan**: TBD (hardware testing infrastructure plan).

