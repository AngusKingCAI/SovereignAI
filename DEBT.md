# DEBT.md � SovereignAI Deferred Items Register

Prepend-only (newest entries at top). Each entry: deferred at, reason, trigger condition, target plan.

---

## Deferred: diskcache CVE-2025-69872 (transitive dependency)

**Deferred at**: prompt-20.9.1
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive dependency from huggingface_hub). This is a path traversal vulnerability. Upgrading diskcache may break compatibility with huggingface_hub. This is a pre-existing issue not introduced by this plan.
**Trigger condition**: When huggingface_hub updates to a version that uses a patched diskcache or when upgrading to a newer huggingface_hub version.
**Target plan**: TBD (dependency upgrade plan)

---

## Deferred: AR6 violations - 15 pre-existing context bag violations

**Deferred at**: prompt-20.9.1
**Reason**: no_context_bags.py check fails with 15 AR6 violations (memory backends, librarian, conformance, routing_engine, self_correction). These are pre-existing issues not introduced by this plan. AR6 forbids context objects, untyped dicts, or **kwargs across component boundaries. Fixing requires major memory system refactoring with typed dataclasses.
**Trigger condition**: When AR6 violations retirement decision is made per DEBT entry "AR6 violations retirement decision".
**Target plan**: TBD (memory system refactoring plan)

---

## Deferred: First-run experience UI edits

**Deferred at**: prompt-20.9.1
**Reason**: Plan S4 (first-run experience UI) was deferred per OR17 (deliverables ship in full or defer). The plan specified 5-step wizard with HTML/JS/web endpoints, but this was not implemented due to time constraints and scope considerations. The existing auth system already has /api/auth/register, so the first-run UI would be a frontend wrapper around existing functionality.
**Trigger condition**: When first-run experience UI implementation is prioritized.
**Target plan**: prompt-20.9.2 (UI experience plan)

---

## Deferred: web/hardware_probe.py nvidia_ml_py3 dependency

**Deferred at**: prompt-20.7.3
**Reason**: check_dependencies.py reports web/hardware_probe.py imports nvidia_ml_py3 which is not in txt/requirements.txt. This is a pre-existing issue not introduced by this plan. The web layer uses nvidia-ml-py while sovereignai/shared/hardware_probe.py was cleaned of pynvml in S8.3. Dependency restored to txt/requirements.txt since web layer still requires it for NVIDIA GPU detection.
**Trigger condition**: When web layer hardware probe is refactored to use shared layer only.
**Target plan**: TBD (web layer cleanup plan)
**Status**: Resolved at prompt-20.7.3 /close step 17 — nvidia-ml-py>=12.535.133 restored to txt/requirements.txt for web layer compatibility.

---


---

## Deferred: tui/panels/adapters.py AR7 refactoring not completed

**Deferred at**: prompt-20.7.3
**Reason**: Plan S8.2b specified refactoring tui/panels/adapters.py to consume Capability API only per DD-20.6.1, but execution found the AR7 violation was in tui/panels/workers.py instead. adapters.py was not edited during execution. The plan's WILL-edit list includes adapters.py but the actual diff does not, causing spec_match.py to fail. This is a documentation discrepancy between plan and execution.
**Trigger condition**: When TUI panel AR7 refactoring is revisited.
**Target plan**: TBD (TUI refactoring plan)
**Status**: Resolved at prompt-20.9.1 — adapters.py already using CapabilityAPI, was not the actual violation source.

---
---


---

## Deferred: TUI memory.py AR7 compliance

**Deferred at**: prompt-20.7.3
**Reason**: tui/panels/memory.py imports concrete memory backends (EpisodicMemoryBackend, ProceduralMemoryBackend, WorkingMemoryBackend, TraceMemoryBackend) directly from sovereignai.memory.*, violating AR7. Per DD-20.6.1, TUI panels may import from sovereignai.shared.* but not from sovereignai.memory.*. Refactoring would require a Capability API layer for memory operations that doesn't exist yet. Added back to TUI_PANELS_ALLOWED_IMPORTS as temporary exception per OR64.
**Trigger condition**: When Capability API is extended with memory query operations or a separate memory panel API is designed.
**Target plan**: TBD (TUI refactoring plan)
**Status**: Resolved at prompt-20.9.1 — CapabilityAPI extended with query_memory_backends() method, memory.py refactored to use CapabilityAPI only.

---

---


---

## Deferred: pynvml test refactoring after S3.5

**Deferred at**: prompt-20.5
**Reason**: S3.5 removed pynvml fallback (dual-import strategy). Tests test_shared_sample_with_pynvml_gpu, test_shared_sample_pynvml_exception, test_shared_sample_gpu_memory_type_mapping mock the old pynvml import path. Need to refactor to mock nvidia_ml_py3 correctly or delete if testing dual-import behavior is no longer relevant.
**Trigger condition**: When pynvml test strategy is decided.
**Target plan**: 20.6
**Resolved at**: prompt-20.7.3 (deleted pynvml skip stubs and pynvml code from hardware_probe.py per S8.3 Option A - clean removal of dead code).

---


---

## Deferred: TUI AR7 compliance after S2.2 revert

**Deferred at**: prompt-20.5
**Reason**: S2.2 reverted the tui/panels allowlist exception for sovereignai.shared imports. TUI panels (adapters.py, hardware.py, models.py, memory.py, options.py, services.py) import sovereignai.shared.capability_api and sovereignai.shared.types to use the Capability API. Per AR7, UIs must not import sovereignai.* packages directly. Fixing requires either: (a) adding TUI allowlist back (weakens AR7), or (b) refactoring TUI to avoid sovereignai.shared imports (non-trivial - needs Architect decision on TUI architecture).
**Trigger condition**: Architect next session.
**Target plan**: Architect next session
**Status**: Resolved at prompt-20.9.1 — All TUI panels (memory, models, tasks, hardware, options, logs, workers) refactored to use CapabilityAPI with unified TUI_ALLOWED_IMPORTS allowlist. AR7 test now passes with zero exceptions.

---


---

## Deferred: Plan 20.3 execution log deletion

**Deferred at**: prompt-20.6
**Reason**: P20.5 S3.1 deleted the P20.3 log stub (L731) instead of backfilling. Original content unrecoverable.
**Trigger condition**: N/A (irreversible).
**Target plan**: N/A

---


---

## Deferred: Plan 20.3 execution log content

**Deferred at**: prompt-20.5
**Reason**: The in-repo logs/execution-log-prompt-20.3.md is a 26-token stub (per P20.3 log L1254-1256). Original session log content unrecoverable.
**Trigger condition**: N/A (irreversible).
**Target plan**: N/A

---


---

## Deferred: AR-check output caching investigation

**Deferred at**: prompt-20.5
**Reason**: AR-check scripts may have byte-identical output (per P20.4 log L3964-3999). Likely subprocess stdout capture bug. Need investigation to fix or document.
**Trigger condition**: When AR-check output caching is investigated.
**Target plan**: 20.12

---


---

## Deferred: GPU testing infrastructure

**Deferred at**: prompt-20.5
**Reason**: web/hardware_probe.py GPU paths need ≥90% coverage. Mocking strategy (mock subprocess.run for nvidia-smi, mock pynvml/nvidia-ml-py imports) may not reach 90%. If mocking can't reach 90%, need GPU testing infrastructure.
**Trigger condition**: When GPU testing infrastructure is implemented or mocking strategy validated.
**Target plan**: 20.9

---


---

## Deferred: CVE dependency upgrades

**Deferred at**: prompt-20.5
**Reason**: pip-audit CVEs in DEBT.md (setuptools ×5 from P18, diskcache ×1 from P20.1). Need to confirm transitive dep status and upgrade dependencies.
**Trigger condition**: When dependency upgrade plan is scheduled.
**Target plan**: 20.11

---


---

## Deferred: SSE thread safety IndexError

**Deferred at**: prompt-20.5
**Reason**: PytestUnhandledThreadExceptionWarning: IndexError: pop from empty list in tests/test_web_ui_panels.py::test_hardware_stream_endpoint_sse (per P20.2 log L5280, L6493). Likely thread-safety issue in the SSE infinite-loop generator. Fix may require bounding the generator or using client.stream() in the test.
**Trigger condition**: When SSE thread safety investigation is completed.
**Target plan**: 20.10

---


---

## Deferred: AR6 violations retirement decision

**Deferred at**: prompt-20.5
**Reason**: AR6 violations 5+ plans old (deferred since prompt-15.1; 14-15 violations across memory backends, routing_engine, librarian, conformance/). Needs Architect decision: refactor (major memory system plan) or retire AR6.
**Trigger condition**: Architect next session.
**Target plan**: Architect next session

---


---

## Deferred: plan file immutability pre-commit hook

**Deferred at**: prompt-20.5
**Reason**: Plan file immutability hook (block edits to prompts/plan-*.md during execution) needs pre-commit infrastructure. This prevents mid-execution plan mutations (L50 pattern).
**Trigger condition**: When pre-commit hook infrastructure is implemented.
**Target plan**: 20.8

---


---

## Deferred: mypy 156 errors across 29 files

**Deferred at**: prompt-20.5
**Reason**: 156 mypy errors across 29 files accumulated since plans 16-20.4 (per Plan 20.2 log L5414). Per OR53, no "pre-existing" exemption. Fixing requires a dedicated type remediation plan.
**Trigger condition**: When type remediation plan is scheduled.
**Target plan**: 20.7

---


---

## Deferred: spec_match failures across plans 16-20.4

**Deferred at**: prompt-20.5
**Reason**: After S1.2 reverted the spec_match.py self-exemption, spec_match will fail across plans 16-20.4 diffs. This indicates real scope drift accumulated over 7 plans. Fixing this requires a dedicated plan to either clean up the drift or redesign spec_match to handle accumulated changes.
**Trigger condition**: When spec_match redesign + scope drift cleanup plan is scheduled.
**Target plan**: 20.7

---


---

## Deferred: hardware_probe.py GPU path coverage gap

**Deferred at**: prompt-20
**Reason**: hardware_probe.py has 55% coverage (83% overall sovereignai coverage). GPU detection paths (nvidia-smi subprocess calls, pynvml/nvidia-ml-py library calls) are hard to test without actual NVIDIA hardware. These paths require GPU hardware or complex mocking that may not reflect real behavior.
**Trigger condition**: When GPU hardware testing infrastructure is available or when mocking strategy is validated against real GPU behavior.
**Target plan**: TBD (hardware testing infrastructure plan).

---


---

## Deferred: diskcache CVE-2025-69872 (transitive dependency)

**Deferred at**: prompt-20.1
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive dependency from huggingface_hub). This is a path traversal vulnerability. Upgrading diskcache may break compatibility with huggingface_hub.
**Trigger condition**: When huggingface_hub updates to a version that uses a patched diskcache or when upgrading to a newer huggingface_hub version.
**Target plan**: TBD (dependency upgrade plan).
**Status**: Still present at prompt-20.2 (no dependency changes in this plan).

---


---

## Deferred: generate() metadata-only path documentation

**Deferred at**: prompt-19
**Reason**: generate() has side effect of loading model into VRAM. For metadata-only queries, users should call database_registry.find_model() directly. This is a documentation note, no code change needed.
**Trigger condition**: N/A (documentation only).
**Target plan**: N/A (documented in adapter docstring).
**Resolved at**: prompt-20.1 (added DEBUG trace emit to llama_cpp_adapter.generate() for metadata-only path documentation).

---


---

## Deferred: AdapterCapability enum for GPU capability probing

**Deferred at**: prompt-19
**Reason**: GPU capability probing is adapter-specific (llama-cpp has llama_supports_gpu_offload(), other adapters may have different probes). Future adapters must add their own probe in health_check(). Defer AdapterCapability enum to post-Plan-19.
**Trigger condition**: When a third adapter with different GPU probing needs is added.
**Target plan**: TBD (post-Plan-19).

---


---

## Deferred: subscribe_callback bounded queue

**Deferred at**: prompt-19
**Reason**: TraceEmitter.subscribe_callback needs per-subscriber bounded queue + drain thread to prevent memory leaks. Current implementation may accumulate unprocessed callbacks. Defer to post-Plan-19.
**Trigger condition**: When callback-based tracing shows memory growth in production.
**Target plan**: TBD (post-Plan-19).

---


---

## Deferred: health_check caching in RoutingEngine

**Deferred at**: prompt-19
**Reason**: health_check() is called on every route() invocation. TTL cache would reduce overhead but adds statefulness. Defer to post-Plan-19.
**Trigger condition**: When performance profiling shows health_check overhead is significant.
**Target plan**: TBD (post-Plan-19).

---


---

## Deferred: generate() timeout implementation

**Deferred at**: prompt-19
**Reason**: generate() in llama_cpp_adapter has no timeout mechanism. Cross-platform timeout infrastructure is non-trivial (signal handling differs on Windows vs Unix). Defer to post-Plan-19.
**Trigger condition**: When timeout infrastructure is implemented across adapters.
**Target plan**: TBD (post-Plan-19).

---


---

## Deferred: llama-cpp-python 0.2.50 testing

**Deferred at**: prompt-19
**Reason**: llama-cpp-python 0.2.50 added as dependency but not tested with real binary. Need to verify compatibility with actual GGUF models and GPU offload before v1.0.
**Trigger condition**: Before v1.0 release or when real model testing infrastructure is available.
**Target plan**: TBD (pre-v1.0 testing plan).

---


---

## Deferred: setuptools vulnerabilities (transitive dependency)

**Deferred at**: prompt-18
**Reason**: pip-audit reports 5 known vulnerabilities in setuptools 65.5.0 (transitive dependency from Python 3.11.9): CVE-2022-43012, CVE-2024-6345, and PYSEC-2025-49. These are ReDoS and path traversal vulnerabilities in package_index.py. Upgrading setuptools may break compatibility with Python 3.11.9.
**Trigger condition**: When upgrading to a newer Python version that bundles a patched setuptools.
**Target plan**: TBD (Python version upgrade plan).

---


---

## Deferred: GPU bandwidth lookup is substring-based placeholder

**Deferred at**: prompt-18
**Reason**: GPU memory type and bandwidth lookup in hardware_probe.py uses substring matching on GPU names (e.g., "RTX 4090" -> "GDDR6X"). This is a best-effort placeholder that may miss GPUs or misclassify them. Accurate lookup requires PCI-ID-based detection.
**Trigger condition**: When GPU detection accuracy is needed for production deployments.
**Target plan**: Plan-19 or later.
**Resolved at**: prompt-20.1 (added exact PCI-ID mapping for RTX 3060 Laptop and common GPUs to hardware_probe.py).

---


---

## Deferred: TeacherWorker.curate_dataset() criteria parameter

**Deferred at**: prompt-15.1
**Reason**: Tests in test_teacher_worker.py pass a `criteria` parameter to `curate_dataset()` but the actual implementation signature doesn't accept it. This causes 3 test failures (test_curate_dataset_consent_false, test_curate_dataset_pii_filter, test_curate_dataset_retention_filter). The parameter was likely added to tests but not to the implementation during Plan 14.
**Trigger condition**: When TeacherWorker implementation is updated to match test expectations.
**Target plan**: Plan 16 or next Education department plan.
**Status**: Still failing at prompt-17 (3 tests). Not in scope for Plan 17 (Database/Service providers).

---


---

## Deferred: AR21 violations - docstring discipline

**Deferred at**: prompt-15.1
**Reason**: Multiple components have docstrings that don't meet AR21 requirements (≥10 words, verb-first, no jargon). These include conformance framework, versioning components, and self-correction skill. Fixing all violations would be a large docstring rewrite effort across many files.
**Trigger condition**: When a focused docstring cleanup plan is scheduled.
**Target plan**: TBD (docs-only cleanup plan).
**Resolved at**: prompt-cleanup (AR21 retired in workflow rev 12. Docstrings now prohibited per AR17. Reversed by design — see DECISIONS.md D6.)

---


---

## Deferred: AR6 violations - memory backend dict parameters

**Deferred at**: prompt-15.1
**Reason**: Memory backend interfaces (episodic, procedural, trace, working) and Librarian use `dict` parameters for data/query. This violates AR6 (no untyped dict/Any context bags) but is a foundational architectural pattern. Refactoring would require defining typed dataclasses for all memory operations, which is a significant scope change.
**Trigger condition**: When memory backend interfaces are redesigned with typed contracts.
**Target plan**: TBD (major memory system refactoring).

---


---

## Deferred: TeacherWorker.curate_dataset() criteria parameter

**Deferred at**: prompt-15.1
**Reason**: Tests in test_teacher_worker.py pass a `criteria` parameter to `curate_dataset()` but the actual implementation signature doesn't accept it. This causes 3 test failures (test_curate_dataset_consent_false, test_curate_dataset_pii_filter, test_curate_dataset_retention_filter). The parameter was likely added to tests but not to the implementation during Plan 14.
**Trigger condition**: When TeacherWorker implementation is updated to match test expectations.
**Target plan**: Plan 16 or next Education department plan.
**Status**: Still failing at prompt-16 (3 tests). Not in scope for Logs panel implementation.
**Resolved at**: prompt-20.1 (TeacherWorker implementation and all tests removed per user request).

---


---

## Deferred: AR6 context bag violations

**Deferred at**: prompt-20.7.1
**Reason**: no_context_bags.py check fails with "AR6 violations found". This is a pre-existing issue not introduced by this docs-only plan. AR6 forbids context objects, untyped dicts, or **kwargs across component boundaries.
**Trigger condition**: When AR6 violations are identified and fixed.
**Target plan**: TBD (governance-focused plan)

---

## Note: duplicate entry — Full Q8 versioning / capability negotiation

**Logged at**: prompt-5 (governance review)
**Issue**: This item was logged twice under near-identical wording — once at prompt-0 (bootstrap, generic Plan 1–4 scope adjudication) and again at prompt-2 (Plan 2 scope adjudication). Both describe the same deferred capability-negotiation work; the prompt-0 entry's trigger condition and the prompt-2 entry's reason are restatements of each other.
**Resolution**: Track resolution against the prompt-0 entry only. When Q8 negotiation work begins, add a single "Resolved at" line to the prompt-0 entry and reference it from the prompt-2 entry rather than resolving both independently.

---


---

## Deferred: Vulture unused variables in test files

**Deferred at**: prompt-20.7.1
**Reason**: Vulture detected unused variables in tests/test_models_panel.py:56 ('filter') and tests/test_options_panel.py:43 ('filter'). These are pre-existing issues not introduced by this docs-only plan. Variables are likely used in test setup but vulture flags them.
**Trigger condition**: When test cleanup or refactoring is done.
**Target plan**: TBD (test-focused plan)

---


---

## Deferred: diskcache CVE-2025-69872

**Deferred at**: prompt-20.7.1
**Reason**: pip-audit detected CVE-2025-69872 in diskcache 5.6.3. This is an existing dependency not modified in this docs-only plan. CVE resolution requires version upgrade which may have breaking changes.
**Trigger condition**: When diskcache version with CVE fix is available and compatibility verified.
**Target plan**: TBD (security-focused plan)

---


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


---

## Deferred: Memory abstraction implementation

**Deferred at**: prompt-3 (per Plan 3 scope adjudication)
**Reason**: Plan 3 defines the interface shape (via ITaskStateQuery protocol pattern) but does not implement memory routing. The Librarian is a pluggable component, not a core component.
**Trigger condition**: When the Librarian Registry is needed (post Plan 4).
**Target plan**: TBD (post Plan 4).

---


---

## Deferred: Full Q8 versioning / capability negotiation (post-MVP)

**Deferred at**: prompt-2 (per Plan 1-4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only — manifests declare semver versions, but no capability negotiation (resolving incompatible versions at startup) is implemented.
**Trigger condition**: When a second adapter version is needed and two components declare incompatible versions of the same capability.
**Target plan**: TBD (post Plan 2).

---


---

## Deferred: AR4 amendment — remove dependency-injector reference

**Deferred at**: prompt-1 (per Plan 1-4 batch Round Table Rev2 adjudication, Finding 5)
**Reason**: AR4 names `dependency-injector` as the DI library, but A8 mandates a passive registry (no `@inject`, no auto-wiring). The hand-rolled DIContainer in `shared/container.py` satisfies A8 without using the `dependency-injector` library. AR4's reference is stale.
**Trigger condition**: When the Architect next drafts a plan's S0.3 (next batch, Plan 5+).
**Target plan**: Plan 5 (Scan) or first plan in next batch.
**Resolved at**: prompt-5 (Scan 5 S2.2 — AR4 rewritten to reference hand-rolled DI container; DECISIONS.md D2 updated).

---


---

## Deferred: Full Q8 versioning / capability negotiation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication)
**Reason**: Plan 2 ships Q8 MVP only. Full versioning/capability negotiation deferred.
**Trigger condition**: When Plan 2's manifest schema is stable and a second adapter version is needed.
**Target plan**: TBD (post Plan 2).

---


---

## Deferred: Durable persistence backends and crash recovery

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A7)
**Reason**: Plan 3 implements the event-store interface and in-memory replay only. Durable backends and full crash recovery are too much for Plan 3 alongside four other components.
**Trigger condition**: When Plan 3's in-memory event store is stable.
**Target plan**: TBD (post Plan 3).

---


---

## Deferred: Relay server E2EE implementation

**Deferred at**: prompt-0 (bootstrap, per Plan 1–4 scope adjudication A4)
**Reason**: Plan 4 ships a local-only relay placeholder that returns a structured error and does not accept connections. Full E2EE implementation deferred to a dedicated plan post-batch.
**Trigger condition**: When Plan 4's placeholder is merged and the local UI stack is functional.
**Target plan**: TBD (post Plan 4, dedicated plan).

---


---

## Deferred: Self-correction / learning loops

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Learning and improvement (Q13) is a skill-level concern, not core. The retrospective trace skill will be built once the skill framework exists.
**Trigger condition**: When skill framework (Plan 2+) is stable.
**Target plan**: TBD (post Plan 4).

---


---

## Deferred: Model loading/unloading based on hardware

**Deferred at**: prompt-0 (bootstrap)
**Reason**: VRAM management, GPU detection, and dynamic model loading are advanced features. Core needs to exist first. Per `principles.md` Models section: "Model loading/unloading based on system hardware is a planned feature for a later plan, not Plan 1."
**Trigger condition**: When local model adapters (Ollama, llama.cpp) are wired and working.
**Target plan**: TBD (post Plan 4).

---


---

## Deferred: Cross-platform packaging

**Deferred at**: prompt-0 (bootstrap)
**Reason**: v1 is Windows-only per P4. Cross-platform packaging adds complexity not needed for initial validation.
**Trigger condition**: When core is stable and Windows packaging is working.
**Target plan**: Q31 (post Plan 4).

---


---

## Deferred: Security Guard implementation

**Deferred at**: prompt-0 (bootstrap)
**Reason**: Security Guard is not pertinent to the core yet. It will be implemented as a Worker later, not as core infrastructure. Per AGENTS.md AR10–12 deferral note.
**Trigger condition**: When Worker lifecycle and skill authoring are stable (post Plan 4).
**Target plan**: TBD (post Plan 4).

---


---

## Deferred: AdapterCapability enum for GPU probing

**Deferred at**: prompt-19
**Reason**: GPU capability probing is adapter-specific. Future adapters must add their own probe in health_check(). A centralized AdapterCapability enum would standardize this but is deferred.
**Trigger condition**: When multiple adapters with different GPU capabilities are implemented.
**Target plan**: TBD (post Plan 19)

---


---

## Deferred: subscribe_callback bounded queue

**Deferred at**: prompt-19
**Reason**: Per-subscriber queue + drain thread adds complexity. Current implementation uses unbounded queues.
**Trigger condition**: When memory pressure or queue overflow issues are observed.
**Target plan**: TBD (post Plan 19)

---


---

## Deferred: health_check caching in RoutingEngine

**Deferred at**: prompt-19
**Reason**: TTL cache adds statefulness to RoutingEngine. Current implementation calls health_check() on every route() invocation.
**Trigger condition**: When performance profiling shows health_check() is a bottleneck.
**Target plan**: TBD (post Plan 19)

---


---

## Deferred: generate() timeout

**Deferred at**: prompt-19
**Reason**: Cross-platform timeout infrastructure is non-trivial. LlamaCppAdapter.generate() currently has no timeout protection.
**Trigger condition**: When cross-platform timeout infrastructure is implemented.
**Target plan**: TBD (post Plan 19)

---


---

## Deferred: llama-cpp-python binary testing

**Deferred at**: prompt-19
**Reason**: llama-cpp-python 0.2.50 added to requirements.txt but not tested with real binary. Need validation before v1.0 release.
**Trigger condition**: When preparing for v1.0 release or when llama.cpp adapter is used in production.
**Target plan**: TBD (pre v1.0)

---


---

## Deferred: First-run experience UI edits

**Deferred at**: prompt-19
**Reason**: Plan 19 S3.3 UI edits (web/templates/index.html, web/static/app.js) deferred to focus on backend API and tests. Backend /api/first-run-check endpoint is complete and tested.
**Trigger condition**: When backend first-run check is validated in production use.
**Target plan**: TBD (post Plan 19)

---
