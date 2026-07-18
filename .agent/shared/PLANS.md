# PLANS.md — SovereignAI Project State

Dynamic state only. SSOT for baselines, queue, scan schedule.

---

## Current Baseline

| Metric | Value | Plan |
|--------|-------|------|
| Tests | 497 | 20.9.9 |
| ruff | 0 | 20.9.9 |
| mypy | 0 | 20.9.9 |

## Trend (last 5 plans)

| Plan | Tests | Delta | Note |
|------|-------|-------|------|
| 20.9.9 | 497 | +5 | Documentation hygiene |
| 20.9.8 | 492 | +7 | Correlation ID typing |
| 20.9.7 | 485 | +8 | TUI Memory Panel AR7 |
| 20.9.6 | 480 | +8 | BoundedTraceQueue |
| 20.9.5 | 471 | +9 | AR6 context bag cleanup |

## Active Plan

plan-fix-2-Rev1

## Next in Queue

| Slot | Plan | Status |
|------|------|--------|
| 1 | Plan 22 | ⏳ Pending |
| 2 | Plan 23 | ⏳ Pending |
| 3 | Plan 24 | ⏳ Pending |
| 4 | Plan 25 | ⏳ Pending |
| 5 | Plan 26 | ⏳ Pending |

## Recent Completed (last 10)

| Prompt | Description | Tests | Date |
|--------|-------------|-------|------|
| prompt-plan-fix-1-Rev1 | Plan Fix 1 - Import Path Standardization, ToolCallParser Error Types, SkillManifest Fixes, Test Reorganization | 531 | 2026-07-18 |
| prompt-workflow-fix-6 | Workflow Fix 6 - Test path mismatches, AR check script paths, OR rules, timeout fix | 531 | 2026-07-18 |
| prompt-workflow-fix-5 | Workflow Fix 5 - STOP definition, get_current_plan.py fix, verify_close.py Rev suffix handling | N/A | 2026-07-18 |
| prompt-workflow-fix-3 | Workflow Fix 3 - AR check script paths and verify_close.py logic | N/A | 2026-07-18 |
| workflow-fix-2 | Workflow Fix 2 - OR rules, AR21, execution log handling | N/A | 2026-07-18 |
| workflow-fix | Fix Governance Workflow Inconsistencies | N/A | 2026-07-18 |
| 20.9.9 | Documentation Hygiene + Document Hygiene Tests | 497 | 2026-07-03 |
| 20.9.8 | Correlation ID Typing + VersionNegotiator Disable | 492 | 2026-07-03 |
| 20.9.7 | TUI Memory Panel AR7 Compliance via CapabilityAPI | 485 | 2026-07-03 |
| 20.9.6 | BoundedTraceQueue Implementation | 480 | 2026-07-03 |
| 20.9.4 | Performance Improvements — health_check caching, generate() timeout | 468 | 2026-07-03 |
| 20.9.3 | Typed Memory Queries — Add typed query dataclasses | 464 | 2026-07-03 |
| 20.9.2 | Hardware Probe Refactoring - GPU Detection and Dependency Cleanup | 59 | 2026-07-03 |
| 20.9.1 | TUI AR7 Compliance: Capability API Extension and Panel Refactoring | 480 | 2026-07-02 |
| 20.8 | AGENTS.md + LANDMINES.md Cleanup and Restructure | N/A | 2026-07-02 |
| 20.9.4 | Performance Improvements — health_check caching, generate() timeout | 468 | 2026-07-03 |
| 20.9.3 | Typed Memory Queries — Add typed query dataclasses | 464 | 2026-07-03 |
| 20.9.2 | Hardware probe cleanup | 59 | 2026-07-03 |
| 20.9.1 | TUI AR7 compliance — 13 scoped tests | 480 | 2026-07-02 |
| 20.9 | Workflow optimization | 480 | 2026-07-02 |

## Scan History

| Scan | Date | Result |
|------|------|--------|
| 20 | 2026-07-02 | Pass |
| 15 | 2026-06-29 | Pass |
| 10 | 2026-06-29 | Pass |
| 5 | 2026-06-28 | Pass |

## STOPs / Blockers

None.
