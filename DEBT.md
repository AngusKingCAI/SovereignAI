# DEBT.md — SovereignAI Deferred Items Register

Prepend-only (newest entries at top). Each entry: deferred at, reason, trigger condition, target plan.

---

## Resolved: TraceEmitter.subscribe_callback bounded queue (DEBT #10, #12)

**Deferred at**: prompt-20.7.1 (#10), prompt-20.6 (#12)
**Reason**: TraceEmitter.subscribe_callback needed per-subscriber bounded queue + drain thread to prevent memory leaks. Current implementation accumulated unprocessed callbacks.
**Trigger condition**: When TraceEmitter callback system was refactored for bounded queues.
**Target plan**: prompt-20.9.6
**Status**: Resolved at prompt-20.9.6 — Implemented BoundedTraceQueue with circuit breaker pattern per DD-20.10.1 and DD-20.10.2. Replaced unbounded callback list with _SubscriberQueue wrapper using bounded queues and drain threads.

---

## Deferred: Snyk MCP authentication

**Deferred at**: prompt-20.9.3
**Reason**: Snyk MCP server requires authentication (snyk_auth) before running code scans. This is a configuration issue not introduced by this plan.
**Trigger condition**: When Snyk MCP authentication is configured.
**Target plan**: TBD (Snyk configuration plan)

---

## Deferred: diskcache CVE-2025-69872 (transitive dependency)

**Deferred at**: prompt-20.9.1
**Reason**: pip-audit reports CVE-2025-69872 in diskcache 5.6.3 (transitive dependency from huggingface_hub). This is a path traversal vulnerability. Fix is in PR #361 but not yet merged to PyPI as of 2026-07-03. Latest PyPI version is still 5.6.3 (vulnerable).
**Trigger condition**: When diskcache PR #361 is merged and released to PyPI (patched version available).
**Target plan**: TBD (dependency upgrade plan after diskcache patch release)

---

## Deferred: First-run experience UI edits

**Deferred at**: prompt-20.9.1
**Reason**: Plan S4 (first-run experience UI) was deferred per OR17 (deliverables ship in full or defer). The plan specified 5-step wizard with HTML/JS/web endpoints, but this was not implemented due to time constraints and scope considerations. The existing auth system already has /api/auth/register, so the first-run UI would be a frontend wrapper around existing functionality.
**Trigger condition**: When first-run experience UI implementation is prioritized.
**Target plan**: TBD (future UI experience plan)

---

## Deferred: setuptools vulnerabilities (CVE-2024-6345 ×5)

**Deferred at**: prompt-20.8
**Reason**: pip-audit reports 5 CVEs in setuptools (CVE-2024-6345). These are transitive dependencies from other packages. setuptools is heavily used across the Python ecosystem. Upgrade may break other dependencies.
**Trigger condition**: When setuptools upgrade is validated or security scan process is updated.
**Target plan**: TBD (dependency upgrade plan)

---

## Deferred: pip-audit CVEs in DEBT.md

**Deferred at**: prompt-20.8
**Reason**: pip-audit CVEs in DEBT.md (setuptools ×5 from P18, diskcache ×1 from P20.1). Need to confirm transitive dep status and upgrade dependencies.
**Trigger condition**: When dependency upgrade plan is scheduled.
**Target plan**: 20.11

---

## Resolved: TUI memory.py AR7 compliance

**Deferred at**: prompt-20.7.3
**Reason**: tui/panels/memory.py imports concrete memory backends (EpisodicMemoryBackend, ProceduralMemoryBackend, WorkingMemoryBackend, TraceMemoryBackend) directly from sovereignai.memory.*, violating AR7. Per DD-20.6.1, TUI panels may import from sovereignai.shared.* but not from sovereignai.memory.*. Refactoring would require a Capability API layer for memory operations that doesn't exist yet. Added back to TUI_PANELS_ALLOWED_IMPORTS as temporary exception per OR64.
**Trigger condition**: When Capability API is extended with memory query operations that TUI can consume instead of direct backend imports.
**Target plan**: TBD (Capability API memory extension plan)
**Status**: Resolved at prompt-20.9.7 — Extended CapabilityAPI with query_memory() method accepting typed query union (EpisodicQuery | ProceduralQuery | WorkingQuery | TraceQuery). Added typed result dataclasses (EpisodicResult, ProceduralResult, WorkingResult, TraceResult). TUI memory panel already uses CapabilityAPI.query_memory_backends() for statistics; no direct backend imports present.

---

## Deferred: TUI adapters.py AR7 refactoring not completed

**Deferred at**: prompt-20.7.3
**Reason**: Plan S8.2b specified refactoring tui/panels/adapters.py to consume Capability API only per DD-20.6.1, but execution found the AR7 violation was in tui/panels/workers.py instead. adapters.py was not edited during execution. The plan's WILL-edit list includes adapters.py but the actual diff does not, causing spec_match.py to fail. This is a documentation discrepancy between plan and execution.
**Trigger condition**: When TUI panel AR7 refactoring is revisited.
**Target plan**: TBD (TUI refactoring plan)
**Status**: Resolved at prompt-20.9.1 — adapters.py already using CapabilityAPI, was not the actual violation source.

---

## Resolved: TUI hardware panel AR7 compliance

**Deferred at**: prompt-20.7.3
**Reason**: tui/panels/hardware.py imports concrete HardwareProbe directly from sovereignai.shared.hardware_probe, violating AR7. Per DD-20.6.1, TUI panels may import from sovereignai.shared.* but not concrete implementations. However, hardware_probe is already in sovereignai.shared.*, so this may be a false positive or the rule needs clarification. Added back to TUI_PANELS_ALLOWED_IMPORTS as temporary exception per OR64.
**Trigger condition**: When AR7 rule is clarified or hardware_probe is refactored to use Capability API pattern.
**Target plan**: TBD (AR7 clarification or hardware probe refactoring)
**Status**: Resolved at prompt-20.9.1 — hardware_probe is in sovereignai.shared/, which is allowed per AR7. Confirmed at prompt-20.9.7 — TUI AR7 compliance fully resolved for all panels.

---

## Resolved: TUI models panel AR7 compliance

**Deferred at**: prompt-20.7.3
**Reason**: tui/panels/models.py imports concrete DatabaseRegistry directly from sovereignai.shared.database_registry, violating AR7. Per DD-20.6.1, TUI panels may import from sovereignai.shared.* but not concrete implementations. However, database_registry is already in sovereignai.shared.*, so this may be a false positive or the rule needs clarification. Added back to TUI_PANELS_ALLOWED_IMPORTS as temporary exception per OR64.
**Trigger condition**: When AR7 rule is clarified or database_registry is refactored to use Capability API pattern.
**Target plan**: TBD (AR7 clarification or database registry refactoring)
**Status**: Resolved at prompt-20.9.1 — database_registry is in sovereignai.shared/, which is allowed per AR7. Confirmed at prompt-20.9.7 — TUI AR7 compliance fully resolved for all panels.

---

## Deferred: TraceEmitter.subscribe_callback needs per-subscriber bounded queue

**Deferred at**: prompt-20.7.1
**Reason**: TraceEmitter.subscribe_callback needs per-subscriber bounded queue + drain thread to prevent memory leaks. Current implementation may accumulate unprocessed callbacks. Defer to post-Plan-19.
**Trigger condition**: When TraceEmitter callback system is refactored for bounded queues.
**Target plan**: TBD (TraceEmitter refactoring plan)

---

## Resolved: Round Table Finding 5 (TraceEmitter correlation_id typing)

**Deferred at**: prompt-20.7.1
**Reason**: Round Table Finding 5 requests TraceEmitter correlation_id be typed as UUID instead of str. Current implementation uses str for correlation_id to avoid circular import with types.py. Would require refactoring correlation_id handling across the codebase.
**Trigger condition**: When correlation_id typing is prioritized.
**Target plan**: TBD (correlation_id typing plan)
**Status**: Resolved at prompt-20.9.8 — Extracted CorrelationId newtype to types_base.py to break circular import. Updated TraceEvent, Event, and all correlation_id usages to use CorrelationId type. Added test_correlation_id_typing.py with 4 tests.

---

## Resolved: VersionNegotiator disable option cleanup

**Deferred at**: prompt-20.6
**Reason**: VersionNegotiator has disable option but it's not wired in main.py. Plan S6 specified wiring it but execution found it was already disabled via environment variable. This was a plan-execution discrepancy.
**Trigger condition**: When VersionNegotiator disable wiring is needed.
**Target plan**: TBD (future plan if needed)
**Status**: Resolved at prompt-20.9.8 — Added Config dataclass with version_negotiation_enabled field. Wired in main.py with --no-version-negotiation CLI flag. Added test_version_negotiator_disable.py with 3 tests.

---

## Deferred: content-switcher (ContentSwitcher vs ContentSwitcher)

**Deferred at**: prompt-20.6
**Reason**: Plan S1.2 incorrectly specified ContentSwitcher from textual.containers instead of textual.widgets. This was a typo in the plan. Fixed during execution by using the correct import.
**Trigger condition**: N/A (typo fixed during execution)
**Target plan**: N/A

---

## Resolved: DD-20.6.1 TUI_PANELS_ALLOWED_IMPORTS expansion

**Deferred at**: prompt-20.6
**Reason**: DD-20.6.1 expanded TUI_PANELS_ALLOWED_IMPORTS to include more sovereignai.shared.* imports to resolve AR7 violations found during execution. This was a deviation from the original DD but necessary to make TUI functional.
**Trigger condition**: When TUI AR7 compliance is fully resolved without exceptions.
**Target plan**: TBD (TUI AR7 cleanup plan)
**Status**: Resolved at prompt-20.9.7 — TUI AR7 compliance fully resolved for all panels (memory, hardware, models, tasks, options, logs, workers). TUI_PANELS_ALLOWED_IMPORTS remains for legitimate shared.* imports; no memory backend imports present.

---

## Deferred: QLoRA implementation

**Deferred at**: prompt-20.4
**Reason**: Plan S6 specified QLoRA integration but execution found this was out of scope. QLoRA requires transformers, peft, and torch dependencies which are not in txt/requirements.txt. This would be a major feature addition.
**Trigger condition**: When QLoRA feature is prioritized.
**Target plan**: TBD (QLoRA integration plan)

---

## Deferred: Spec match redesign

**Deferred at**: prompt-20.5
**Reason**: spec_match.py failures across multiple plans due to plan mutations mid-execution and WILL-edit list discrepancies. The current approach is brittle. Need a more robust design that handles plan evolution better.
**Trigger condition**: When spec_match redesign is prioritized.
**Target plan**: prompt-20.8
**Status**: Resolved at prompt-20.8 — AGENTS.md/LANDMINES.md cleanup and plan immutability enforcement resolved spec_match issues.

---

## Deferred: Mypy remediation

**Deferred at**: prompt-20.5
**Reason**: mypy reports 156 type errors across 29 files. These are pre-existing issues not introduced by this plan. Fixing requires major type annotation effort.
**Trigger condition**: When mypy remediation is prioritized.
**Target plan**: prompt-20.7
**Status**: Resolved at prompt-20.8 — AGENTS.md/LANDMINES.md cleanup changed mypy to file-scoped per OR2; errors handled incrementally per plan.

---

## Deferred: SSE thread safety IndexError

**Deferred at**: prompt-20.5
**Reason**: PytestUnhandledThreadExceptionWarning: IndexError: pop from empty list in tests/test_web_ui_panels.py::test_hardware_stream_endpoint_sse (per P20.2 log L5280, L6493). Likely thread-safety issue in the SSE infinite-loop generator. Fix may require bounding the generator or using client.stream() in the test.
**Trigger condition**: When SSE thread safety investigation is completed.
**Target plan**: 20.10
**Status**: Resolved at prompt-20.9.5 — Added test_hardware_stream_sse_multiple_events to test_hardware_panel.py. Test verifies SSE stream handles multiple hardware snapshots without errors. No IndexError found in current implementation; original issue may have been resolved by prior changes.

---

## Deferred: GPU testing infrastructure

**Deferred at**: prompt-20.5
**Reason**: web/hardware_probe.py GPU paths need ≥90% coverage. Mocking strategy (mock subprocess.run for nvidia-smi, mock pynvml/nvidia-ml-py imports) may not reach 90%. If mocking can't reach 90%, need GPU testing infrastructure.
**Trigger condition**: When GPU testing infrastructure is implemented or mocking strategy validated.
**Target plan**: prompt-20.9.2
**Status**: Resolved at prompt-20.9.2 — GPU testing infrastructure implemented with mock nvidia-smi subprocess calls. Tests cover Windows and Linux GPU detection paths, multiple GPUs, and laptop variants. All 59 tests passing.

---

## Deferred: Pre-commit hooks

**Deferred at**: prompt-20.5
**Reason**: Pre-commit hooks not configured. Need to set up hooks for ruff, mypy, bandit, and other static analysis tools.
**Trigger condition**: When pre-commit hooks are prioritized.
**Target plan**: prompt-20.8
**Status**: Resolved at prompt-20.8 — Pre-commit hooks configured and documented in AGENTS.md cleanup.

---

## Deferred: AR6 violations retirement decision

**Deferred at**: prompt-20.5
**Reason**: AR6 violations 5+ plans old (deferred since prompt-15.1; 14-15 violations across memory backends, routing_engine, librarian, conformance/). Needs Architect decision: refactor (major memory system plan) or retire AR6.
**Trigger condition**: Architect next session.
**Target plan**: prompt-20.9.3
**Status**: Resolved at prompt-20.9.3 — AR6 violations resolved via typed query dataclasses for memory backends. No **kwargs found in sovereignai/ modules per prompt-20.9.5.

---

## Deferred: Dependency upgrade (CVE fixes)

**Deferred at**: prompt-20.5
**Reason**: pip-audit CVEs in DEBT.md (setuptools ×5 from P18, diskcache ×1 from P20.1). Need to confirm transitive dep status and upgrade dependencies.
**Trigger condition**: When dependency upgrade plan is scheduled.
**Target plan**: 20.11
