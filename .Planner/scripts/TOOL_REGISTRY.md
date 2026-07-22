# Tool Registry

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Registry of all hard gate scripts with standardized tool descriptions per Anthropic best practices. Agents read this file at Phase 0 to know what tools are available and when to use them.

## Tool Registry

| Tool ID | Tool Name | Trigger Phase | Trigger Condition | Inputs | Outputs | Failure Recovery |
|---------|-----------|---------------|-------------------|--------|---------|------------------|
| HG-1 | Requirements Complete Validation | Phase 1 | After requirements assessment, before plan drafting | None (auto-discovers latest plan) | Exit 0: requirements complete, Exit 1: specific issues | Fix listed issues, re-run, don't proceed to Phase 2 |
| HG-2 | Scope Defined Validation | Phase 1 | After requirements assessment, before plan drafting | None (auto-discovers latest plan) | Exit 0: scope defined, Exit 1: scope issues | Add scope section, re-run, don't proceed to Phase 2 |
| HG-3 | Dependencies Feasible Validation | Phase 1 | After requirements assessment, before plan drafting | None (auto-discovers latest plan) | Exit 0: dependencies feasible, Exit 1: dependency issues | Fix dependency issues, re-run, don't proceed to Phase 2 |
| HG-14 | Plan Structure PR6 Validation | Phase 2 | After plan structure design, before plan drafting | None (auto-discovers latest plan) | Exit 0: structure follows PR6, Exit 1: structure issues | Fix structure issues, re-run, don't proceed to Phase 3 |
| HG-15 | Path Verification PR2 Validation | Phase 3 | After plan drafting, before plan finalization | None (auto-discovers latest plan) | Exit 0: paths repo-relative, Exit 1: path issues | Fix path references, re-run, don't proceed to Phase 4 |
| HG-4 | Sections Complete Validation | Phase 4 | After plan drafting, before quality gates | None (auto-discovers latest plan) | Exit 0: sections complete, Exit 1: missing sections | Add/expand sections, re-run, don't proceed to Phase 5 |
| HG-5 | Language Clear Validation | Phase 4 | After plan drafting, before quality gates | None (auto-discovers latest plan) | Exit 0: language clear, Exit 1: clarity issues | Improve language, re-run, don't proceed to Phase 5 |
| HG-6 | Landmines Screened Validation | Phase 4 | After plan drafting, before quality gates | None (auto-discovers latest plan) | Exit 0: no landmines, Exit 1: landmines detected | Address landmines, re-run, don't proceed to Phase 5 |
| HG-7 | Compliance Lines Present Validation | Phase 5 | After plan finalization, before Round Table | None (auto-discovers latest plan) | Exit 0: compliance lines present, Exit 1: missing lines | Add compliance lines, re-run, don't proceed to Phase 6 |
| HG-8 | Paths Valid Validation | Phase 5 | After plan finalization, before Round Table | None (auto-discovers latest plan) | Exit 0: paths valid, Exit 1: path issues | Fix path references, re-run, don't proceed to Phase 6 |
| HG-9 | Manifest Complete Validation | Phase 5 | After plan finalization, before Round Table | None (auto-discovers latest plan) | Exit 0: manifest complete, Exit 1: missing components | Complete manifest, re-run, don't proceed to Phase 6 |
| HG-10 | Critical Findings Addressed Validation | Phase 6 | After Round Table review, before plan delivery | None (queries Round Table database) | Exit 0: CRITICAL findings addressed, Exit 1: unaddressed findings | Address findings, update database, re-run, don't deliver plan |
| HG-11 | High Findings Addressed Validation | Phase 6 | After Round Table review, before plan delivery | None (queries Round Table database) | Exit 0: HIGH findings addressed, Exit 1: unaddressed findings | Address findings, update database, re-run, don't deliver plan |
| HG-12 | No Blocking Landmines Validation | Phase 6 | After Round Table review, before plan delivery | None (queries Round Table database) | Exit 0: no blocking landmines, Exit 1: blocking landmines | Address landmines, re-run, don't deliver plan |
| HG-13 | Manifest Present Validation | Phase 6 | After Round Table review, before plan delivery | None (auto-discovers latest plan) | Exit 0: manifest present, Exit 1: manifest missing | Add manifest section, re-run, don't deliver plan |

## Phase Gate Mapping

| Phase | Hard Gates | Blocking? |
|-------|------------|-----------|
| Phase 0 | None | N/A (deliberately un-gated) |
| Phase 1 | HG-1, HG-2, HG-3 | Yes |
| Phase 2 | HG-14 | Yes |
| Phase 3 | HG-15 | Yes |
| Phase 4 | HG-4, HG-5, HG-6 | Yes |
| Phase 5 | HG-7, HG-8, HG-9 | Yes |
| Phase 6 | HG-10, HG-11, HG-12, HG-13 | Yes |

## Tool Distinction Notes

- **HG-9 vs HG-13**: HG-9 checks Executor Manifest completeness (all components present), HG-13 checks Executor Manifest existence (section exists). This distinction prevents false positives.
- **HG-7 vs HG-8**: HG-7 checks compliance indicators presence, HG-8 checks path validity. Both run in Phase 5 but check different aspects.
- **HG-10 vs HG-11**: HG-10 checks CRITICAL findings, HG-11 checks HIGH findings. Both query Round Table database but with different severity filters.

## Tool Testing

Per Anthropic best practices, each tool should be tested against 5 different plan states:
1. Valid plan (should pass)
2. Missing requirements (HG-1 should fail)
3. Missing scope (HG-2 should fail)
4. Circular dependencies (HG-3 should fail)
5. Missing compliance lines (HG-7 should fail)

## Tool Usage

Agents can invoke individual gates directly:
```bash
python .Planner/scripts/hard_gates/hg1_requirements_complete.py
```

Or run all gates for a phase:
```bash
python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1
```

## Dependencies

- **Common Dependencies**: All gates require `plans/` directory with at least one plan-*.md file
- **Database Gates** (HG-10, HG-11, HG-12): Require Round Table database with findings data
- **Pattern Library** (HG-6): Requires PATTERN_LIBRARY.md for governance landmine definitions

## Compliance

All tools follow the standardized tool description format per PR20 (Tool Description Standard) from PLANNER_RULES.md. This ensures agents have clear guidance on when and how to use each tool.