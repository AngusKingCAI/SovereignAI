Depends on: prompt-20.9.3
Vision principles: 1 (local-first), 7 (privacy)
Open questions resolved: none

## WILL edit
- `sovereignai/shared/routing_engine.py` — add health_check caching
- `sovereignai/shared/capability_graph.py` — fix Any import (AR compliance)
- `adapters/external/ollama_adapter/adapter.py` — add timeout parameter, GenerationTimeoutError, fix imports
- `adapters/external/llama_cpp_adapter/adapter.py` — add timeout parameter, GenerationTimeoutError, fix imports
- `tests/test_ollama_adapter.py` — add timeout tests
- `tests/test_llama_cpp_adapter.py` — add timeout tests
- `scripts/ar_checks/no_context_bags.py` — fix stderr output
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `prompts/plan-20.9.4-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- TUI panels, hardware probe, memory backends (handled in 20.9.1-3). Security Guard (new feature, not debt). 
- Unintended files in diff: documents/plan-17-report.md, logs/execution-log-prompt-20.9.3.md, txt/.secrets.baseline (these are pre-existing or cleanup artifacts, not plan scope).
If scope expands, STOP.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify items this plan resolves.
S0.3: Add rules and landmines to AGENTS.md and LANDMINES.md
S0.4: Update PLANS.md with new plan entry
S0.5: Begin Phase 1.

## S1 — Routing Engine Caching

S1.1: Add `health_check_cache: TTLCache` to `RoutingEngine`
S1.2: Cache health_check results for 30 seconds
S1.3: Add cache invalidation on adapter state change
S1.4: Fix `sovereignai/shared/capability_graph.py` Any import (ruff compliance)

S1.5: Commit: `git add -A && git commit -m "perf: health_check caching in RoutingEngine"` (includes capability_graph.py fix)

S1.6: Commit: `git add -A && git commit -m "fix: add trace.emit to RoutingEngine.__init__ per AR22"`

## S2 — Generate Timeout

S2.1: Add `timeout_seconds: float = 30.0` parameter to adapter `generate()` methods
S2.2: Implement timeout using `threading.Timer` (cross-platform)
S2.3: Add tests for timeout behavior

S2.4: Commit: `git add -A && git commit -m "feat: generate() timeout parameter"`

## S3 — Update DEBT.md

S3.1: Mark resolved:
- health_check caching in RoutingEngine → Resolved at prompt-20.9.4
- generate() timeout → Resolved at prompt-20.9.4
- generate() timeout implementation → Resolved at prompt-20.9.4

S3.2: Commit: `git add -A && git commit -m "docs: mark security/arch DEBT items resolved"`

S3.3: Commit: `git add -A && git commit -m "fix: add trace.emit to RoutingEngine.__init__ per AR22"`

## S4 — /close

S4.1: Run `/close`.
