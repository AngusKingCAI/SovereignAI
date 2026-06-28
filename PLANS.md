# PLANS.md — SovereignAI Project State

**Last updated**: 2026-06-28 (prompt-5)

Dynamic state: baselines, completed prompts, next-5-queue. SSOT for test counts, static analysis baselines, and active prompt. Executor updates at every `/close`. Architect reads at every session start. Do not duplicate into other documents.

---

## Baseline Reconciliation Notes

**Plan 1**: First code plan. Established baseline at 22 tests. Delta: 0.
**Plan 2**: Discovery layer. Baseline → 40 tests. Delta: +3 (manifest_parser has 8 vs expected 6; added test_parse_missing_capability_field_raises and test_parse_invalid_priority_raises per Findings 2 and 12).
**Plan 3**: Execution layer. Baseline → 75 tests. Delta: +6 (task_state_machine has 11 vs expected 8; added test_get_state_unknown_returns_none, test_list_tasks_returns_insertion_order, test_transition_unknown_task_raises_unknown_task_error).
**Plan 4**: Interface layer. Baseline → 107 tests. Delta: +32 (8 auth + 9 capability_api + 5 ar7 + 3 relay_placeholder + 7 composition_root).
**Plan 5**: Scan 5. Baseline → 106 tests. Delta: -1 (added test_register_equal_priority_stable_sort and test_register_cleanup_old_capabilities_on_reregistration to capability_graph, but net count decreased by 1 due to test skip changes).

---

## Test Baseline

**Current**: 106 tests (Plan 5 `/close` — Scan 5)
Breakdown: 6 event_bus + 6 trace_emitter + 6 di_container + 21 composition_root + 8 manifest_parser + 7 capability_graph + 7 lifecycle_manager + 5 routing_engine + 11 task_state_machine + 6 dag_validator + 8 auth + 9 capability_api + 5 ar7 + 3 relay_placeholder.
**Tolerance**: ±5 tests. If count at plan start differs from baseline, update this entry and note the delta in CHANGELOG.

---

## Static Analysis Baseline

**Established**: Plan 1 `/close`

| Tool | Baseline | Source | Notes |
|---|---|---|---|
| **Ruff** | 0 errors | Plan 1 | D100/D104 excluded per pyproject.toml |
| **Mypy (file-scoped)** | 0 errors | Plan 1 | File-scoped per OR2 |
| **Bandit** | 49 Low (B101) | Plan 1 | All test assertions; filter `>> Issue: [B` per OR4 |
| **pip-audit** | 0 CVEs | Plan 1 | Scans txt/requirements.txt only per OR39 (file empty — no runtime deps) |
| **Vulture** | 0 findings | Plan 1 | High-confidence (≥80) only |
| **detect-secrets** | pass | Plan 1 | Baseline established prompt-0 |
| **pre-commit** | pass | Plan 1 | Hooks configured at prompt-0 |
| **Coverage** | 96% | Plan 5 | 568 statements, 22 missed. Gaps: main.py (smoke), capability_api.py (error paths), lifecycle_manager.py (error paths), manifest_parser.py (error path), types.py (unused error classes) |

---

## Completed Prompts

| Prompt | Tag | Description | Tests | Ruff | Mypy | Date |
|---|---|---|---|---|---|---|
| prompt-0 | `prompt-0` | Bootstrap — governance docs only, no code | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.1 | `prompt-0.1` | Post-execution cleanup — OR40-OR43, L24-L27, workflow fixes | N/A | N/A | N/A | 2026-06-28 |
| prompt-0.2 | `prompt-0.2` | Environment + doc drift — OR44-OR45, L28-L29, venv setup, ruff config fix | N/A | 0 | N/A | 2026-06-28 |
| prompt-0.3 | `prompt-0.3` | Venv path + repo hygiene — OR46, L30, absolute venv paths in workflows | N/A | 0 | N/A | 2026-06-28 |
| prompt-0.4 | `prompt-0.4` | Mypy filtering + kill bash at start — OR47, L31, /open kill orphans, /close mypy .py filter | N/A | 0 | N/A | 2026-06-28 |
| prompt-1 | `prompt-1` | Core scaffold — Event Bus, TraceEmitter, DI container, Composition Root | 22 | 0 | 0 | 2026-06-28 |
| prompt-2 | `prompt-2` | Discovery layer — manifest parser, capability graph, ICapabilityIndex | 40 | 0 | 0 | 2026-06-28 |
| prompt-3 | `prompt-3` | Execution layer — routing, lifecycle, task state machine, DAG validator | 75 | 0 | 0 | 2026-06-28 |
| prompt-4 | `prompt-4` | Interface layer — Auth middleware, Capability API, Relay placeholder, Q26 audit | 107 | 0 | 0 | 2026-06-28 |
| prompt-5 | `prompt-5` | Scan 5 — mechanical verification scan | 106 | 0 | 0 | 2026-06-28 |

---

## Active Plan

None — awaiting next plan.

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | Scan 5 | First scan — verify baselines, fix accumulated issues | Plans 1–4 | ⏳ Pending |
| 2 | TBD | Future plan | TBD | ⏳ Pending |
| 3 | TBD | Future plan | TBD | ⏳ Pending |
| 4 | TBD | Future plan | TBD | ⏳ Pending |
| 5 | TBD | Future plan | TBD | ⏳ Pending |

---

## Open Questions Outstanding

| Q# | Question | Target plan |
|---|---|---|
| Q1 | Adapter contract — manifest format and interface contract | Plan 2 |
| Q2 | Skill discovery and registration — directory scan + manifest | Plan 2 |
| ~~Q3~~ | ~~Memory abstraction — capability-based backend routing~~ | ~~Resolved Plan 3 (interface defined; impl deferred to DEBT)~~ |
| ~~Q4~~ | ~~Core routing between adapters without knowing them~~ | ~~Resolved Plan 3 (capability-based via ICapabilityIndex + LifecycleManager)~~ |
| Q8 | Adapter/skill/memory versioning — semver + capability negotiation | Plan 2 |
| ~~Q9~~ | ~~Test strategy~~ | ~~Resolved Plan 1~~ |
| Q13 | Learning and improvement — retrospective trace skill | Deferred post Plan 4 |
| ~~Q14~~ | ~~Persistence story — crash recovery via trace replay~~ | ~~Resolved Plan 3 (in-memory only; durable backends deferred)~~ |
| Q31 | Packaging and distribution — Windows-first, PyInstaller vs native | Deferred post Plan 4 |
| ~~Q32~~ | ~~Debt register format~~ | ~~Resolved Plan 1 (DEBT.md scaffold)~~ |
| ~~Q26~~ | ~~Single file instantiates all core components explicitly~~ | ~~Resolved Plan 4 (main.py build_container() — no runtime magic)~~ |

---

## Key Document Cross-References

| Document | Contains |
|---|---|
| `AGENTS.md` | Always-on AR + OR rules |
| `AI_HANDOFF.md` | Static process guide, plan template, Round Table process |
| `project-vision-Rev5.md` | Canonical vision, 14 principles, success criteria, open questions |
| `LANDMINES.md` | Known failure patterns (L1–L9, L11, L12, L17 inherited; L24+ SovereignAI) |
| `DECISIONS.md` | Architectural decisions record |
| `DEBT.md` | Deferred items register |
| `.devin/workflows/open.md` | Opening workflow |
| `.devin/workflows/verify.md` | Per-edit verification |
| `.devin/workflows/close.md` | Closing workflow |
| `.devin/workflows/scan.md` | Scan workflow |

---

## How to Update

1. **After every plan**: Add row to Completed Prompts. Move active plan out of queue; promote next to Active.
2. **Baseline changes**: Update Test Baseline or Static Analysis Baseline with new counts, source plan, and delta reason.
3. **Reconciliation note**: Add entry to Baseline Reconciliation Notes: `**Plan N**: <what changed, why, delta>`.
4. **Open question resolved**: Strike from Open Questions table; note resolving plan. Update `project-vision-Rev5.md` too.
5. **Edit tool only** — never `sed`, `Set-Content`, or shell redirection (OR7).
