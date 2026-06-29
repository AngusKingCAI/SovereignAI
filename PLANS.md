# PLANS.md — SovereignAI Project State

**Last updated**: 2026-06-29 (prompt-10.4)

Dynamic state: baselines, completed prompts, next-5-queue. SSOT for test counts, static analysis baselines, and active prompt. Executor updates at every `/close`. Architect reads at every session start. Do not duplicate into other documents.

---

## Baseline Reconciliation Notes

Full explanations live in `CHANGELOG.md` (one entry per plan) — this section tracks only the running delta, per OR17. Going forward, write one line per plan (`**Plan N**: Baseline → X tests. Delta: ±Y — see CHANGELOG prompt-N.`); do not restate the per-test reasoning here.

**Plan 1**: Baseline → 22 tests. Delta: 0.
**Plan 2**: Baseline → 40 tests. Delta: +3 — see CHANGELOG prompt-2.
**Plan 3**: Baseline → 75 tests. Delta: +6 — see CHANGELOG prompt-3.
**Plan 4**: Baseline → 107 tests. Delta: +32 — see CHANGELOG prompt-4.
**Plan 5**: Baseline → 106 tests. Delta: -1 — see CHANGELOG prompt-5.
**Plan 6**: Baseline → 117 tests. Delta: +11 — see CHANGELOG prompt-6.
**Plan 7**: Baseline → 149 tests. Delta: +32 — see CHANGELOG prompt-7.
**Plan 8**: Baseline → 158 tests. Delta: +9 — see CHANGELOG prompt-8.
**Plan 9**: Baseline → 169 tests. Delta: +11 — see CHANGELOG prompt-9.
**Plan 10**: Baseline → 169 tests. Delta: 0 — see CHANGELOG prompt-10.
**Plan 10.1**: Baseline → 169 tests. Delta: 0 — see CHANGELOG prompt-10.1.
**Plan 10.2**: Baseline → 169 tests. Delta: 0 — governance patch, no test changes.
**Plan 10.3**: Baseline → 169 tests. Delta: 0 — governance condensation patch, no test changes.
**Plan 10.4**: Baseline → 177 tests. Delta: +8 — see CHANGELOG prompt-10.4.

---

## Test Baseline

**Current**: 177 tests (Plan 10.4 `/close`)
Generated via (do not hand-sum a per-suite breakdown — see Plan 5's reconciliation note for what happens when it drifts):
```
.venv/Scripts/python.exe -m pytest tests/ --collect-only -q
```
If a per-suite count is needed for debugging, generate it on demand rather than maintaining it here:
```
.venv/Scripts/python.exe -m pytest tests/ --collect-only -q | grep -oE '^[^:]+\.py' | sort | uniq -c
```
**Tolerance**: ±5 tests. If count at plan start differs from baseline, update this entry and add one line to Baseline Reconciliation Notes (delta only — full reasoning goes in CHANGELOG, not both places).

---

## Static Analysis Baseline

**Established**: Plan 1 `/close`

| Tool | Baseline | Source | Notes |
|---|---|---|---|
| **Ruff** | 0 errors | Plan 1 | D100/D104 excluded per pyproject.toml |
| **Mypy (file-scoped)** | 0 errors | Plan 1 | File-scoped per OR2 |
| **Bandit** | 355 Low (B101) | Plan 10.4 | All test assertions; filter `>> Issue: [B` per OR4. Bandit count reconciled at every /close per OR78. |
| **pip-audit** | 0 CVEs | Plan 1 | Scans txt/requirements.txt only per OR39 (file empty — no runtime deps) |
| **Vulture** | 0 findings | Plan 1 | High-confidence (≥80) only |
| **detect-secrets** | pass | Plan 1 | Baseline established prompt-0 |
| **pre-commit** | pass | Plan 1 | Hooks configured at prompt-0 |
| **Coverage** | 93% | Plan 10 | Dropped from 96% (Plan 5) as codebase grew through Plans 6–10 without proportional test additions. Gaps to address in Plans 11–14: memory backends, versioning, conformance framework, Education department. Target: 90% floor (Plan 13 STOP condition). Coverage measured at every /close per OR77. |

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
| prompt-6 | `prompt-6` | Implement FastAPI Web UI | 117 | 0 | 0 | 2026-06-28 |
| prompt-7 | `prompt-7` | MessageDispatcher, WebSearchSkill, OllamaAdapter, HardwareProbe | 149 | 0 | 0 | 2026-06-29 |
| prompt-8 | `prompt-8` | 9-panel sidebar UI with observability | 158 | 0 | 0 | 2026-06-29 |
| prompt-9 | `prompt-9` | Web Authentication Implementation | 169 | 0 | 0 | 2026-06-29 |
| prompt-10 | `prompt-10` | Scan 10 — mechanical verification scan | 169 | 0 | 0 | 2026-06-29 |
| prompt-10.1 | `prompt-10.1` | Post-Scan-10 Cleanup Patch — OR75, L34-L35, close.md hardening | N/A | N/A | N/A | 2026-06-29 |
| prompt-10.2 | `prompt-10.2` | Governance Patch: Rule Gap Fixes + Premature Tag Cleanup — OR76-OR82, L36-L39 | N/A | N/A | N/A | 2026-06-29 |
| prompt-10.4 | `prompt-10.4` | Web UI Hotfix Patch — 3 bugs (manifest parser, dispatch kwargs, first-run 401) | 177 | 0 | 0 | 2026-06-29 |

---

## Active Plan

**None** — awaiting next plan

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | Plan 11 | Memory layer — Librarian, backends (episodic, procedural, working, trace) | Scan 10 | ⏳ Pending |
| 2 | Plan 12 | Versioning — semver, negotiator, compatibility matrix | Plan 11 | ⏳ Pending |
| 3 | Plan 13 | Test framework — conformance, contract, property-based tests | Plan 12 | ⏳ Pending |
| 4 | Plan 14 | Education department — Teacher worker, self-correction skill | Plan 13 | ⏳ Pending |
| 5 | Scan 15 | Third whole-repo scan | Plan 14 | ⏳ Pending |

---

## Open Questions

Tracked solely in `project-vision-Rev5.md` (SSOT) — do not duplicate the full table here, and do not log resolutions in this file. `project-vision-Rev5.md` strikes resolved questions and notes the resolving plan; that's the only place this happens now.

**Snapshot** (refreshed at each scan, per `scan.md` step 4 — may lag the vision doc by up to one batch): 5 open (Q1, Q2, Q8, Q13, Q31), 6 resolved (Q3, Q4, Q9, Q14, Q26, Q32 — see `project-vision-Rev5.md` for resolving plans).

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

**Numbering policy** (per OR84): Rule and landmine numbers are frozen — never renumbered. Gaps from retired slots are documented in AGENTS.md's "Retired slots" block. New rules continue from OR85; new landmines from L40.

---

## How to Update

1. **After every plan**: Add row to Completed Prompts. Move active plan out of queue; promote next to Active.
2. **Baseline changes**: Update Test Baseline using the generated count (`pytest --collect-only -q`), not a hand-summed breakdown. Update Static Analysis Baseline with new counts and source plan.
3. **Reconciliation note**: Add a one-line delta to Baseline Reconciliation Notes: `**Plan N**: Baseline → X tests. Delta: ±Y — see CHANGELOG prompt-N.` The "why" goes in CHANGELOG only — don't duplicate it here.
4. **Open question resolved**: Do NOT edit this file's Open Questions section beyond the snapshot count. Strike the question and note the resolving plan in `project-vision-Rev5.md` only — that's the sole place resolutions are recorded. Refresh the snapshot count here at the next scan (per `scan.md` step 4).
5. **Edit tool only** — never `sed`, `Set-Content`, or shell redirection (OR7).
