# PLANS.md — SovereignAI Project State

Dynamic state only. SSOT for baselines, active plan, queue, blockers.
Full history: `.agent/shared/CHANGELOG.md`.

---

## Current Baseline

| Metric | Value | Source Plan |
|--------|-------|-------------|
| Tests | 891 passed, 52 skipped | reorganization-fix |
| ruff | 0 | reorganization-fix |
| mypy | 37 pre-existing (not blocking) | reorganization-fix |

## Active Plan

| Plan | Rev | Status | Start Date |
|------|-----|--------|------------|
| batch-governance | — | Completed | 2026-07-21 |

## Queue

| Slot | Plan | Status | Depends On |
|------|------|--------|------------|
| 1 | — | — | — |
| 2 | — | — | — |
| 3 | — | — | — |
| 4 | — | — | — |
| 5 | — | — | — |

## STOPs / Blockers

None.

## Compliance State

| Check | Status | Last Verified |
|-------|--------|---------------|
| Executor Manifest present (GR13) | ✅ | reorganization-fix |
| Execution attestation produced | ✅ | reorganization-fix |
| verify_execution.py PASS | ✅ | reorganization-fix |
| Trace file complete | ✅ | reorganization-fix |

## Recent History (last 5)

| Plan | Rev | Date | Note |
|------|-----|------|------|
| batch-governance | — | 2026-07-21 | ✅ Completed: Add batch governance plan and batch RT score document support (v1.6) |
| reorganization-fix | — | 2026-07-20 | ✅ Completed: Post-reorganization cleanup, removed stale files, fixed script runners |
| Plan 30 | Rev 2 | 2026-07-20 | ✅ Completed: Scan fix: AR check paths, SOR-1/M7/M8 added, range review 26-29 |
| Plan 29 | Rev 5 | 2026-07-20 | Model registry with provider sync, offline mode, SSE updates, and API layer |
| Plan 28 | Rev 5 | 2026-07-19 | Options Panel persistence with encryption, migrations, and EventBus integration |
| workflow-fix | Rev 1 | 2026-07-19 | Fixed 9 critical/high/medium compliance system issues |
| Plan 27 | Rev 5 | 2026-07-19 | Cross-department messaging with InterDepartmentBus, security, and integration |
| Plan 26 | Rev 5 | 2026-07-19 | Orchestrator component with IntentClassifier, DepartmentRouter, ConversationState, and EventBus integration |
| Plan 25.5 | Rev 1 | 2026-07-19 | Test infrastructure fixes |
| Plan 25.4 | Rev 1 | 2026-07-19 | 643 passed, 52 skipped |
