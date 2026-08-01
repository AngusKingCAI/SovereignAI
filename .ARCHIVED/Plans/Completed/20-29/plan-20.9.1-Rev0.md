Depends on: prompt-20.8
Vision principles: 9 (capability API), 14 (modularity)
Open questions resolved: none

## WILL edit
- `tui/panels/memory.py` — refactor to CapabilityAPI
- `tui/panels/models.py` — refactor to CapabilityAPI
- `tui/panels/tasks.py` — refactor to CapabilityAPI
- `tui/panels/hardware.py` — refactor to CapabilityAPI
- `tui/panels/options.py` — refactor to CapabilityAPI
- `tui/panels/logs.py` — refactor to CapabilityAPI
- `tui/panels/workers.py` — refactor to CapabilityAPI (discovered during execution)
- `sovereignai/shared/capability_api.py` — add memory/hardware/task/log query methods
- `sovereignai/shared/types.py` — add MemoryBackendInfo and TaskStateSummary
- `sovereignai/main.py` — wire registries and memory backends into CapabilityAPI
- `tests/test_ar7_no_core_imports_in_ui.py` — remove TUI_PANELS_ALLOWED_IMPORTS
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `txt/.secrets.baseline` — updated by detect-secrets scan
- `.devin/workflows/review.md` — skill file updated during execution
- `prompts/plan-20.9.1-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- Core orchestrator, managers, workers, librarian. If scope expands, STOP per OR10.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify items this plan resolves.
S0.3: No new rules.
S0.4: Begin Phase 1.

## S1 — Extend Capability API

S1.1: Add to `sovereignai/shared/types.py`:
- `MemoryBackendInfo` dataclass
- `TaskStateSummary` dataclass

S1.2: Add to `sovereignai/shared/capability_api.py`:
- `query_memory_backends() → list[MemoryBackendInfo]`
- `query_hardware_status() → HardwareSnapshot`
- `query_model_catalog() → list[ModelEntry]`
- `query_task_states() → list[TaskStateSummary]`
- `query_service_registry() → list[tuple[str, ServiceStatus]]`
- `query_logs(correlation_id: str) → list[TraceEvent]`

S1.3: Wire DatabaseRegistry, ServiceRegistry, and memory backends into CapabilityAPI in `sovereignai/main.py`

S1.4: Commit: `git add -A && git commit -m "feat: add TUI query methods to CapabilityAPI"`

S1.5: Fix ServiceStatus circular import using TYPE_CHECKING guard in capability_api.py

S1.6: Commit: `git add -A && git commit -m "fix: use TYPE_CHECKING for ServiceStatus import in capability_api.py"`

## S2 — Refactor TUI Panels

S2.1: `memory.py` — replace `sovereignai.memory.*` imports with CapabilityAPI calls
S2.2: `models.py` — replace `DatabaseRegistry`, `ModelCatalog` with CapabilityAPI
S2.3: `tasks.py` — replace `ITaskStateQuery`, `TaskState` with CapabilityAPI
S2.4: `hardware.py` — replace `HardwareProbe` with CapabilityAPI
S2.5: `options.py` — replace `DatabaseRegistry`, `ServiceRegistry` with CapabilityAPI
S2.6: `logs.py` — replace `TraceEmitter` with CapabilityAPI
S2.7: `workers.py` — replace direct imports with CapabilityAPI (discovered during execution)

S2.8: Commit: `git add -A && git commit -m "refactor: TUI panels use CapabilityAPI only per AR7"`

S2.9: Fix query_service_registry to return service names with status

S2.10: Commit: `git add -A && git commit -m "fix: return service names with status in query_service_registry"`

S2.11: Fix ruff formatting in capability_api.py

S2.12: Commit: `git add -A && git commit -m "fix: ruff formatting in capability_api.py"`

## S3 — Update AR7 Test

S3.1: Remove `TUI_PANELS_ALLOWED_IMPORTS` from `test_ar7_no_core_imports_in_ui.py`
S3.2: All TUI panels must pass strict AR7 — zero exceptions
S3.3: Commit: `git add -A && git commit -m "test: remove TUI panel allowlist exceptions"`

## S4 — First-Run UI (DEFERRED per OR17)

S4.1: DEFERRED - First-run experience UI not implemented per OR17 (deliverables ship in full or defer). Documented in DEBT.md with target plan prompt-20.9.2.

## S5 — Update DEBT.md

S5.1: Mark resolved:
- TUI AR7 compliance after S2.2 revert → Resolved at prompt-20.9.1
- TUI memory.py AR7 compliance → Resolved at prompt-20.9.1

S5.2: Add deferred items:
- First-run experience UI → Deferred at prompt-20.9.1, target plan prompt-20.9.2
- AR6 violations (15 pre-existing) → Deferred at prompt-20.9.1, target plan TBD
- diskcache CVE-2025-69872 → Deferred at prompt-20.9.1, target plan TBD

S5.3: Commit: `git add -A && git commit -m "docs: mark DEBT items resolved at prompt-20.9.1"`

## S6 — /close

S6.1: Run `/close`.
