# PLANS.md — SovereignAI Project State

**Last updated**: 2026-06-28 (prompt-0.2)

This document tracks the dynamic state of the SovereignAI project: baselines, completed prompts, and the next-5-prompt queue. It is the canonical source for test counts, static analysis baselines, and which prompt is currently active. The Executor updates this document at every `/close`. The Architect reads it at every session start. Do not duplicate content from this file into other documents — this is the SSOT for baselines and queue state.

---

## Baseline Reconciliation Notes

*No code plans executed yet (prompt-0 and prompt-0.1 were docs-only). Test and static-analysis baselines will be established at Plan 1 `/close` and recorded here. Each entry follows this format:*

*`**Plan N**: <what changed, why, delta, tolerance note>`*

---

## Test Baseline

**Current baseline**: Not yet established — set at Plan 1 `/close` (S_close step: full pytest run)

**Tolerance**: ±5 tests (variance acceptable due to parameterised fixtures and environment variation)

**Delta tracking**: If test count at the start of a plan differs from baseline, update this entry and note the change in CHANGELOG.

---

## Static Analysis Baseline

**Status**: Not yet established — all tool baselines set at Plan 1 `/close`

| Tool | Baseline | Source | Notes |
|---|---|---|---|
| **Ruff** | TBD | Plan 1 `/close` | 0 errors expected on fresh scaffold |
| **Mypy (file-scoped)** | TBD | Plan 1 `/close` | File-scoped per OR2 — not full repo |
| **Bandit** | TBD | Plan 1 `/close` | Count per OR4 (filter: `>> Issue: [B`) |
| **pip-audit** | TBD | Plan 1 `/close` | CVE count across all packages |
| **Vulture** | TBD | Plan 1 `/close` | High-confidence findings only |
| **detect-secrets** | TBD | Plan 1 `/close` | Baseline established with `.secrets.baseline` |
| **pre-commit** | TBD | Plan 1 | Hooks configured at scaffold |

---

## Completed Prompts

| Prompt | Tag | Description | Tests | Ruff | Mypy | Date |
|---|---|---|---|---|---|---|
| prompt-0 | `prompt-0` | Bootstrap commit — governance docs only, no code | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.1 | `prompt-0.1` | Post-execution cleanup — OR40-OR43, L24-L27, workflow fixes, repo hygiene | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.2 | `prompt-0.2` | Environment + doc drift cleanup — OR44-OR45, L28-L29, venv setup, ruff config fix | N/A | 0 | N/A | 2026-06-28 |

*Plans 1–4 rows will be added here at each `/close`.*

---

## Active Plan

**Plan 1** — awaiting execution.

Plan 1 file: prompts/plan-1.md (to be created by Architect, copied by User)

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | Plan 1 | Core scaffold — project layout, event bus, TraceEmitter, DI container, Composition Root | prompt-0 | ▶️ Active |
| 2 | Plan 2 | Capability graph, manifest parser, routing engine | Plan 1 | ⏳ Pending Plan 1 |
| 3 | Plan 3 | Lifecycle manager, task state machine, DAG validator | Plan 2 | ⏳ Pending Plan 2 |
| 4 | Plan 4 | Auth middleware, Capability API, Relay server stub | Plan 3 | ⏳ Pending Plan 3 |
| 5 | Scan 5 | First scan — verify baselines, fix accumulated issues | Plans 1–4 | ⏳ Pending Plans 1–4 |

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
| Q9 | Test strategy — conformance, contract, property-based | Plan 1 |
| Q13 | Learning and improvement — retrospective trace skill (not core) | Deferred (post Plan 4) |
| Q14 | Persistence story — many stores, crash recovery via trace replay | Plan 3 |
| Q31 | Packaging and distribution — Windows-first, PyInstaller vs native | Deferred (post Plan 4) |
| Q32 | Debt register format — where it lives, who maintains it, trigger conditions | Plan 1 (DEBT.md scaffold) |

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
