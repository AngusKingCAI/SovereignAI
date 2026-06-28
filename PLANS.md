# PLANS.md — SovereignAI Project State

**Last updated**: 2026-06-28 (prompt-1)

This document tracks the dynamic state of the SovereignAI project: baselines, completed prompts, and the next-5-prompt queue. It is the canonical source for test counts, static analysis baselines, and which prompt is currently active. The Executor updates this document at every `/close`. The Architect reads it at every session start. Do not duplicate content from this file into other documents — this is the SSOT for baselines and queue state.

---

## Baseline Reconciliation Notes

**Plan 1**: First code plan — established test baseline at 23 tests and static analysis baselines for all tools. Delta from expected: +1 test (di_container thread-safety test added per Finding 3).

---

## Test Baseline

**Current baseline**: 23 tests (Plan 1 `/close`). Breakdown: 6 event_bus + 6 trace_emitter + 6 di_container + 5 composition_root.

**Tolerance**: ±5 tests (variance acceptable due to parameterised fixtures and environment variation)

**Delta tracking**: If test count at the start of a plan differs from baseline, update this entry and note the change in CHANGELOG.

---

## Static Analysis Baseline

**Status**: Established at Plan 1 `/close`

| Tool | Baseline | Source | Notes |
|---|---|---|---|
| **Ruff** | 0 errors | Plan 1 `/close` | Fresh scaffold — D100/D104 excluded per pyproject.toml |
| **Mypy (file-scoped)** | 0 errors | Plan 1 `/close` | File-scoped per OR2 — Plan 1 files: shared/types.py, event_bus.py, trace_emitter.py, container.py, main.py + tests |
| **Bandit** | 49 Low (B101: assert_used) | Plan 1 `/close` | Count per OR4 (filter: `>> Issue: [B`) — all test assertions, expected |
| **pip-audit** | 0 CVEs | Plan 1 `/close` | Scanned txt/requirements.txt only per OR39 — file remains empty (no runtime deps per Rev2 Finding 5; Rev3 confirms no stale references) |
| **Vulture** | 0 findings | Plan 1 `/close` | High-confidence (≥80) only |
| **detect-secrets** | pass | Plan 1 `/close` | Baseline established prompt-0; unchanged |
| **pre-commit** | pass | Plan 1 | Hooks configured at prompt-0 scaffold |

---

## Completed Prompts

| Prompt | Tag | Description | Tests | Ruff | Mypy | Date |
|---|---|---|---|---|---|---|
| prompt-0 | `prompt-0` | Bootstrap commit — governance docs only, no code | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.1 | `prompt-0.1` | Post-execution cleanup — OR40-OR43, L24-L27, workflow fixes, repo hygiene | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.2 | `prompt-0.2` | Environment + doc drift cleanup — OR44-OR45, L28-L29, venv setup, ruff config fix | N/A | 0 | N/A | 2026-06-28 |
| prompt-0.3 | `prompt-0.3` | Venv path + repo hygiene cleanup — OR46, L30, workflow files use absolute venv paths | N/A | 0 | N/A | 2026-06-28 |
| prompt-0.4 | `prompt-0.4` | Mypy filtering + kill bash at start — OR47, L31, /open step 1 kill orphans, /close step 3 mypy .py filter, /close step 21 stronger language | N/A | 0 | N/A | 2026-06-28 |
| prompt-1 | `prompt-1` | Core scaffold — Event Bus, TraceEmitter, DI container, Composition Root, test baseline | 22 | 0 | 0 | 2026-06-28 |

*Plans 2–4 rows will be added here at each `/close`.*

---

## Active Plan

**Plan 2** — awaiting execution.

Plan 2 file: prompts/plan-2-Rev3.md

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | Plan 2 | Capability graph, manifest parser, routing engine | Plan 1 | ▶️ Active |
| 2 | Plan 3 | Lifecycle manager, task state machine, DAG validator | Plan 2 | ⏳ Pending Plan 2 |
| 3 | Plan 4 | Auth middleware, Capability API, Relay server stub | Plan 3 | ⏳ Pending Plan 3 |
| 4 | Scan 5 | First scan — verify baselines, fix accumulated issues | Plans 1–4 | ⏳ Pending Plans 1–4 |
| 5 | TBD | Future plan | TBD | ⏳ Pending |

---

## Open Questions Outstanding

The following open questions from `project-vision-Rev5.md` remain unresolved. Plans resolve them as they proceed — cross off here and update the vision doc when resolved.

| Q# | Question | Target plan |
|---|---|---|
| Q1 | Adapter contract — manifest format and interface contract | Plan 2 |
| Q2 | Skill discovery and registration — directory scan + manifest | Plan 2 |
| Q3 | Memory abstraction — capability-based backend routing | Plan 3 |
| Q4 | Core routing between adapters without knowing them | Plan 2 |
| Q8 | Adapter/skill/memory versioning — semantic versioning + capability negotiation | Plan 2 |
| ~~Q9~~ | ~~Test strategy — conformance, contract, property-based~~ | ~~Resolved at Plan 1~~ |
| Q13 | Learning and improvement — retrospective trace skill (not core) | Deferred (post Plan 4) |
| Q14 | Persistence story — many stores, crash recovery via trace replay | Plan 3 |
| Q31 | Packaging and distribution — Windows-first, PyInstaller vs native | Deferred (post Plan 4) |
| ~~Q32~~ | ~~Debt register format — where it lives, who maintains it, trigger conditions~~ | ~~Resolved at Plan 1 (DEBT.md scaffold)~~ |

---

## Key Document Cross-References

- **Architecture and operational rules** → `AGENTS.md` (always-on; every file edit must comply)
- **Static process guide, plan template, Round Table process** → `AI_HANDOFF.md`
- **Canonical vision, 14 principles, success criteria, open questions** → `project-vision-Rev5.md`
- **Known failure patterns** → `LANDMINES.md` (append-only; L1–L9, L11, L12, L17 inherited from sovereign-ai predecessor; L24+ SovereignAI-specific)
- **Architectural decisions record** → `DECISIONS.md`
- **Deferred items register** → `DEBT.md`
- **Opening workflow** → `.devin/workflows/open.md`
- **Per-edit verification** → `.devin/workflows/verify.md`
- **Closing workflow** → `.devin/workflows/close.md`
- **Scan workflow** → `.devin/workflows/scan.md`

---

## How to Update This Document

1. **After every plan**: Add a row to the Completed Prompts table (append to bottom). Move the active plan out of the queue. Promote the next plan to Active.
2. **At baseline changes**: Update Test Baseline or Static Analysis Baseline with new counts, source plan, and reason for delta.
3. **When a baseline reconciliation note is needed**: Add a new entry to the Baseline Reconciliation Notes section in the format: `**Plan N**: <what changed, why, delta, tolerance note>`.
4. **When an open question is resolved**: Strike it from the Open Questions table and note the resolving plan. Update `project-vision-Rev5.md` to cross it off there too.
5. **Edit tool only** — never `sed`, `Set-Content`, or shell redirection on this file (OR7).

---

*Maintained by: Executor (at `/close`). Architect reads but does not edit directly.*
