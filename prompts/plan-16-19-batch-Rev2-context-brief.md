# Batch Brief — Plans 16-19 (Rev 2)

**Panelist**: _(pending Round Table sign-off)_

## Context
- **Baseline**: prompt-15.1 cleanup pass complete (AR17 no-docstrings, D7 no-OR-refs-in-source, principles.md as 32-line authority).
- **Repo state**: 320 tests, 89% coverage (PLANS.md baseline). 90% floor enforced at every /close.
- **Workflow files**: open=41 lines, close=88, scan=42, verify=21. All flat-format.
- **Active sidebar tabs**: 9 (Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Options). Logs becomes 10th.

## Plans in this batch
| Plan | Title | Depends on | Vision principles |
|---|---|---|---|
| 16 | Foundation + Governance + Logs Panel | Scan 15 | P9, P11, P8 |
| 17 | Provider Framework + HF Database + Ollama Service | 16 | P2, P3, P4, P5 |
| 18 | Models Panel + Hardware Panel + Tok/s + VRAM Badges | 17 | P2, P8, P4 |
| 19 | llama.cpp Adapter (P4 Minimum Viable Local) | 18 | P3, P4, P5 |

**Dependency chain**: linear 16 → 17 → 18 → 19. No parallelism. If Plan N STOPs, all downstream STOPs (binary).

## New rules proposed (OR66-OR70)
- **OR66** (Plan 16): Logs panel consumes `/api/traces` SSE only — no direct TraceEmitter import from web/.
- **OR67** (Plan 17): `databases/` and `services/` are root-level packages, never nested in `sovereignai/`.
- **OR68** (Plan 17): every ServiceProvider and DatabaseProvider exposes `health_check()` returning typed status dataclass.
- **OR69** (Plan 18): Models and Hardware panels consume capability API only.
- **OR70** (Plan 19): every adapter manifest declares `routing_priority` int (ascending sort, lower = higher priority).

## Open questions resolved
**None.** No Q1-Q34 resolutions in this batch. (Snapshot per PLANS.md: 5 open — Q1, Q2, Q8, Q13, Q31.)

## Key design decisions (per session-context-plans-16-19.md)
1. Logs as 10th sidebar tab (user explicit).
2. `databases/` and `services/` root-level packages — P5 fix (core provides registries only).
3. P4 minimum viable local = 2 adapters (Ollama + llama.cpp).
4. Models panel: 4-level dropdown, tok/s runtime-computed, VRAM badges, empty-DB state.
5. Options panel: 3 tabs (Model Services / Model Databases / Authentication), 3-button rows per provider.
6. Hardware panel: Task Manager style, multi-GPU detection (IGPU + DGPU), live SSE sampling at 1Hz.

## Risks flagged for Round Table
- **R1**: llama.cpp native lib on Windows may require CUDA toolkit — first-run UX must handle missing deps gracefully (typed AdapterUnavailableError, not crash).
- **R2**: HF scraping rate limits — Plan 17 S2.3 caches 1hr. May be too aggressive for power users; too short for offline use.
- **R3**: Tok/s formula (bandwidth ÷ active bytes × 0.65) is a heuristic — empirical validation deferred to post-Plan-19.
- **R4**: OR70 routing_priority ordering — Ollama=10 (preferred), llama.cpp=20 (failover). Confirm intent.
- **R5**: spec_match.py governance/test file exemption (Plan 16 S1.3) — verify allowlist doesn't permit scope creep through test files.

## Coverage target
≥90% at every /close (per workflow principles). Current baseline 89% — Plan 16 must lift to ≥90%.

## Round Table protocol
Runs until clean pass (no unaddressed CRITICAL/HIGH). Each rev brings new evidence — no re-litigating settled findings. Severity: CRITICAL/HIGH block; MEDIUM address or document; LOW architect discretion. Items without evidence auto-dropped.

## Settled findings (do not re-litigate)
- AR17 (no docstrings) — settled prompt-cleanup.
- D7 (no OR refs in source code) — settled prompt-cleanup.
- principles.md as authority (replaces project-vision-Rev5.md) — settled this session.
- Logs as 10th sidebar tab — user explicit.
- 120-line plan cap — settled this session.
- Reverted 18.x saga — clean rebuild from prompt-15.1.
