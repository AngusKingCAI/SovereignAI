# PLANS.md — SovereignAI Project State

**Last updated**: 2026-06-30 (prompt-18.3)

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
**Plan 10.5**: Baseline → 183 tests. Delta: +6 — see CHANGELOG prompt-10.5.
**Plan 12**: Baseline → 271 tests. Delta: +88 — see CHANGELOG prompt-12.
**Plan 13**: Baseline → 288 tests. Delta: +17 — see CHANGELOG prompt-13.
**Plan 14**: Baseline → 320 tests. Delta: +32 — see CHANGELOG prompt-14.
**Plan 15**: Baseline → 320 tests. Delta: 0 — see CHANGELOG prompt-15.
**Plan 16**: Baseline → 332 tests. Delta: +12 — see CHANGELOG prompt-16.
**Plan 17**: Baseline → 352 tests. Delta: +20 — see CHANGELOG prompt-17.
**Plan 17.1**: Baseline → 352 tests. Delta: 0 — hotfix, no test changes.
**Plan 17.2**: Baseline → 352 tests. Delta: 0 — hotfix, no test changes.
**Plan 17.3**: Baseline → 352 tests. Delta: 0 — hotfix, no test changes.
**Plan 17.4**: Baseline → 342 tests. Delta: -10 — see CHANGELOG prompt-17.4.
**Plan 17.5**: Baseline → 342 tests. Delta: 0 — see CHANGELOG prompt-17.5.
**Plan 17.6**: Baseline → 342 tests. Delta: 0 — see CHANGELOG prompt-17.6.
**Plan 17.7**: Baseline → 352 tests. Delta: +10 — see CHANGELOG prompt-17.7.
**Plan 18.0**: Baseline → 355 tests. Delta: +3 — see CHANGELOG prompt-18.0.
**Plan 18.1**: Baseline → 363 tests. Delta: +8 — see CHANGELOG prompt-18.1.
**Plan 18.1.1**: Baseline → 363 tests. Delta: 0 — hotfix, no test changes.
**Plan 18.2**: Baseline → 418 tests. Delta: +55 — see CHANGELOG prompt-18.2.
**Plan 18.3**: Baseline → 502 tests. Delta: +84 — see CHANGELOG prompt-18.3.

---

## Test Baseline

**Current**: 502 tests (Plan 18.3 `/close`)
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
| **Ruff** | 34 findings (line length, whitespace) | Plan 18.3 | Deferred to next prompt |
| **Mypy (file-scoped)** | 6 pre-existing errors | Plan 18.3 | config_loader.py, sovereignai/main.py, service.py — deferred |
| **Bandit** | 2 pre-existing (B310, B608) | Plan 18.3 | Ollama service urllib, web/main.py SQL — deferred |
| **pip-audit** | 0 CVEs | Plan 18.3 | Clean |
| **Vulture** | 0 findings | Plan 18.3 | Clean |
| **detect-secrets** | pass | Plan 18.3 | Clean |
| **pre-commit** | pass | Plan 18.3 | Hooks configured |
| **Coverage** | 87% | Plan 18.3 | 89% target deferred to next prompt |

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
| prompt-10.5 | `prompt-10.5` | Web UI Hotfix: /api/tasks 500 + Panel Population | 183 | 0 | 0 | 2026-06-29 |
| prompt-11 | `prompt-11` | Memory layer — Librarian, backends (episodic, procedural, working, trace) | 183 | 0 | 0 | 2026-06-29 |
| prompt-12 | `prompt-12` | Version Negotiation — SemVer, negotiator, compatibility matrix | 271 | 0 | 0 | 2026-06-29 |
| prompt-13 | `prompt-13` | Conformance and Property Testing — framework, contracts, Hypothesis | 288 | 0 | 0 | 2026-06-29 |
| prompt-14 | `prompt-14` | Education Department — Teacher worker, Self-correction skill, QLoRA | 320 | 0 | 0 | 2026-06-29 |
| prompt-15 | `prompt-15` | Scan 15 — mechanical verification scan | 320 | 0 | 0 | 2026-06-29 |
| prompt-16 | `prompt-16` | Fix Log Drawer and Add Orchestrator Thinking | 332 | 0 | 0 | 2026-06-29 |
| prompt-17 | `prompt-17` | Implement Models, Memory, Orchestrator, and Options Panels | 352 | 0 | 0 | 2026-06-29 |
| prompt-17.1 | `prompt-17.1` | Fix model pull to use hf.co/ prefix | 352 | 0 | 0 | 2026-06-29 |
| prompt-17.2 | `prompt-17.2` | Fix Model Pull + Organize HF Catalog by Family | 352 | 0 | 0 | 2026-06-30 |
| prompt-17.3 | `prompt-17.3` | Fix Auth Tests + Resizable Log + Verbose Pull Logging + Close Discipline | 352 | 0 | 0 | 2026-06-30 |
| prompt-17.4 | `prompt-17.4` | Fix Register Page Redirect + Autocomplete Attributes | 342 | 3 pre-existing | 4 pre-existing | 2026-06-30 |
| prompt-17.5 | `prompt-17.5` | Fix Registration Block + Cookie Secure Flag | 342 | 3 pre-existing | 4 pre-existing | 2026-06-30 |
| prompt-17.6 | `prompt-17.6` | Fix Model Pull 500 + Collapsible Family Sections + Load More + Provider Search | 342 | 2 pre-existing | 4 pre-existing | 2026-06-30 |
| prompt-17.7 | `prompt-17.7` | Fix Auth Deletion + Pull Method + Load More + Log Toggle Button | 352 | 0 | 5 pre-existing | 2026-06-30 |
| prompt-18.0 | `prompt-18.0` | Web UI Polish + Download Pipeline Fix | 355 | 0 | 0 | 2026-06-30 |
| prompt-18.1 | `prompt-18.1` | Logs Panel Restructure + Verbose Logging + Model Database + Options Tabs | 363 | 0 | 0 | 2026-06-30 |
| prompt-18.1.1 | `prompt-18.1.1` | Fix Options Tab Click Handler | 363 | 0 | N/A | 2026-06-30 |
| prompt-18.2 | `prompt-18.2` | Models Menu Restructure + Universal Tracing | 418 | 26 line length warnings | 4 pre-existing | 2026-06-30 |
| prompt-18.3 | `prompt-18.3` | UI Status Updates & Tracing Enforcement | 502 | 34 findings | 6 pre-existing | 2026-06-30 |

---

## Active Plan

**None — awaiting next plan**

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | TBD | TBD | TBD | ⏳ Pending |
| 2 | TBD | TBD | TBD | ⏳ Pending |
| 3 | TBD | TBD | TBD | ⏳ Pending |
| 4 | TBD | TBD | TBD | ⏳ Pending |
| 5 | TBD | TBD | TBD | ⏳ Pending |

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
