# PLANS.md — SovereignAI Project State

**Last updated**: 2026-07-03 (prompt-20.9.6)

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
**Plan 15.1**: Baseline → 320 tests. Delta: 0 — see CHANGELOG prompt-15.1.
**Plan 16**: Baseline → 332 tests. Delta: +12 — see CHANGELOG prompt-16.
**Plan 17**: Baseline → 362 tests. Delta: +30 — see CHANGELOG prompt-17.
**Plan 18**: Baseline → 391 tests. Delta: +29 — see CHANGELOG prompt-18.
**Plan 19**: Baseline → 407 tests. Delta: +16 — see CHANGELOG prompt-19.
**Plan 20**: Baseline → 407 tests. Delta: 0 — see CHANGELOG prompt-20.
**Plan 20.1**: Baseline → 455 tests. Delta: +48 — see CHANGELOG prompt-20.1.
**Plan 20.2**: Baseline → 455 tests. Delta: 0 — see CHANGELOG prompt-20.2.
**Plan 20.3**: Baseline → 455 tests. Delta: 0 — see CHANGELOG prompt-20.3.
**Plan 20.4**: Baseline → 456 tests. Delta: +1 — see CHANGELOG prompt-20.4.
**Plan 20.5**: Baseline → 359 tests. Delta: -97 — see CHANGELOG prompt-20.5 (spec_match, TUI AR7, pynvml tests deferred).
**Plan 20.6**: Baseline → 458 tests. Delta: +99 — see CHANGELOG prompt-20.6 (TUI tests added, deferred tests re-enabled).
**Plan 20.7.1**: Baseline → 466 tests. Delta: +8 — see CHANGELOG prompt-20.7.1 (test_ar_checks.py decimal plan number fix).
**Plan 20.7.2**: Baseline → 466 tests. Delta: 0 — see CHANGELOG prompt-20.7.2 (AR-check scripts + skills integration, no test changes).
**Plan 20.7.3**: Baseline → 464 tests. Delta: -2 — see CHANGELOG prompt-20.7.3 (removed pynvml tests, test count correction).
**Plan 20.9**: Baseline → 480 tests. Delta: +16 — see CHANGELOG prompt-20.9 (workflow optimization scripts + tests).
**Plan 20.9.1**: Baseline → 480 tests. Delta: 0 — see CHANGELOG prompt-20.9.1 (TUI AR7 compliance refactoring, scoped tests only).
**Plan 20.9.2**: Baseline → 59 tests. Delta: -405 — see CHANGELOG prompt-20.9.2 (hardware probe refactor, scoped tests only).
**Plan 20.9.3**: Baseline → 464 tests. Delta: +405 — see CHANGELOG prompt-20.9.3 (typed memory queries, AR6 fixes).
**Plan 20.9.4**: Baseline → 468 tests. Delta: +4 — see CHANGELOG prompt-20.9.4 (health_check caching, generate() timeout).
**Plan 20.9.5**: Baseline → 472 tests. Delta: +4 — see CHANGELOG prompt-20.9.5 (AR-check caching + test).
**Plan 20.9.6**: Baseline → 480 tests. Delta: +8 — see CHANGELOG prompt-20.9.6 (bounded queue implementation + tests).
**Plan 20.9.5**: Baseline → 471 tests. Delta: +3 — see CHANGELOG prompt-20.9.5 (AR6 context bag cleanup, AR-check caching).

---

## Test Baseline

**Current**: 479 tests (Plan 20.9.6 `/close`)
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
| **Bandit** | 0 findings | Plan 11 | 2 nosec B608 for SQL injection warnings (parameterized queries). 8 low/medium pre-existing. |
| **pip-audit** | 1 CVE in diskcache | Plan 20.9.4 | diskcache CVE-2025-69872 (pre-existing, documented in DEBT.md) |
| **Vulture** | 0 findings | Plan 1 | High-confidence (≥80) only |
| **detect-secrets** | pass | Plan 1 | Baseline established prompt-0 |
| **pre-commit** | pass | Plan 1 | Hooks configured at prompt-0 |
| **Coverage** | 89% | Plan 20.9.4 | Scoped tests only (routing_engine, adapters). Target: 90% floor. Coverage measured at every /close per OR43. |

---

## Completed Prompts

> **Note**: Rule numbers in historical rows refer to the numbering scheme active at that time.

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
| prompt-20.9 | `prompt-20.9` | Workflow optimization scripts and token reduction | 480 | 0 | 0 | 2026-07-02 |
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
| prompt-15.1 | `prompt-15.1` | Fix Critical Issues from Log Scan — test mode, memory backends, production guards | 320 | 0 | 0 | 2026-06-29 |
| prompt-19 | `prompt-19` | llama.cpp Adapter, Routing Engine Failover, First-Run Experience | 407 | 0 | 0 | 2026-07-01 |
| prompt-20 | `prompt-20` | pynvml Deprecation Fix, HfApi Direction Parameter Removal | 407 | 0 | 0 | 2026-07-01 |
| prompt-20.1 | `prompt-20.1` | Coverage Improvement, TeacherWorker Removal, Scan Infrastructure Fix | 455 | 0 | 0 | 2026-07-01 |
| prompt-20.2 | `prompt-20.2` | Governance Patch: spec_match.py allowlist, TUI AR7, OR51-OR53 | 455 | 0 | 0 | 2026-07-02 |
| prompt-20.3 | `prompt-20.3` | Governance Patch: Crash Recovery, OR57-OR60, L46-L49 | 455 | 0 | 0 | 2026-07-02 |
| prompt-20.4 | `prompt-20.4` | Governance Patch: OR61-OR66, L50-L55, TUI AR7 fix | 456 | 0 | 0 | 2026-07-02 |
| prompt-20.5 | `prompt-20.5` | Governance Patch: pynvml removal, spec_match.py TUI paths, OR67-OR68 | 359 | 0 | 0 | 2026-07-02 |
| prompt-20.6 | `prompt-20.6` | TUI Panel Loading Fix — ContentSwitcher, Refresh buttons, TUI tests | 458 | 0 | 0 | 2026-07-02 |
| prompt-20.7.1 | `prompt-20.7.1` | AGENTS.md Conciseness Pass + New Rules — GR18, OR75/OR77/OR79/OR80/OR81, L60-L66 | 466 | 0 | 0 | 2026-07-02 |
| prompt-20.7.2 | `prompt-20.7.2` | AR-Check Scripts + Skills Integration — check_dependencies.py, check_plan_immutability.py, check_rule_conciseness.py, /open and /close skill updates | 466 | 0 | 0 | 2026-07-02 |
| prompt-20.7.3 | `prompt-20.7.3` | 20.6 Rollback + sailogs/ Implementation + Test Mocks — FileTraceSubscriber, sailogs/, test_file_trace_subscriber.py, 30s timeout, HFDatabaseProvider mocks, S8 rollbacks, pynvml removal | 464 | 0 | 0 | 2026-07-02 |
| prompt-20.9.3 | `prompt-20.9.3` | Typed Memory Queries — Add typed query dataclasses to memory backends per AR6 | 464 | 0 | 0 | 2026-07-03 |
| prompt-20.9.4 | `prompt-20.9.4` | Performance Improvements — health_check caching, generate() timeout | 468 | 0 | 0 | 2026-07-03 |
| prompt-20.9.5 | `prompt-20.9.5` | AR6 Context Bag Cleanup + AR-Check Caching | 471 | 0 | 0 | 2026-07-03 |

---

## Active Plan

Plan 20.9.5 — AR6 Context Bag Cleanup + AR-Check Caching

---

## Next-5-Prompt Queue

| Slot | Plan | Description | Depends on | Status |
|---|---|---|---|---|
| 1 | Plan 21 | UI overhaul — 10 panels (deferred per user request) | Plan 20 | ⏳ Pending |
| 2 | Plan 22 | Future plan | Plan 21 | ⏳ Pending |
| 3 | Plan 23 | Future plan | Plan 22 | ⏳ Pending |
| 4 | Plan 24 | Future plan | Plan 23 | ⏳ Pending |
| 5 | Plan 25 | Future plan | Plan 24 | ⏳ Pending |

---

## Open Questions

Tracked solely in `principles.md` (SSOT) — do not duplicate the full table here, and do not log resolutions in this file. `principles.md` strikes resolved questions and notes the resolving plan; that's the only place this happens now.

**Snapshot** (refreshed at each scan, per `scan.md` step 4 — may lag the vision doc by up to one batch): 5 open (Q1, Q2, Q8, Q13, Q31), 6 resolved (Q3, Q4, Q9, Q14, Q26, Q32 — see `principles.md` for resolving plans).

---

## Key Document Cross-References

| Document | Contains |
|---|---|
| `AGENTS.md` | Always-on AR + OR rules |
| `AI_HANDOFF.md` | Static process guide, plan template, Round Table process |
| `principles.md` | Canonical vision, 14 principles, success criteria, open questions |
| `LANDMINES.md` | Known failure patterns (L1–L9, L11, L12, L17 inherited; L24+ SovereignAI) |
| `DECISIONS.md` | Architectural decisions record |
| `DEBT.md` | Deferred items register |
| `.devin/skills/open/SKILL.md` | Opening workflow skill |
| `.devin/skills/verify/SKILL.md` | Per-edit verification skill |
| `.devin/skills/close/SKILL.md` | Closing workflow skill |
| `.devin/skills/scan/SKILL.md` | Scan workflow skill |

**Numbering policy** (per OR46): Rule and landmine numbers are frozen — never renumbered. Gaps from retired slots are documented in AGENTS.md's "Retired slots" block. New rules continue from OR66; new landmines from L47.

---

## How to Update

1. **After every plan**: Add row to Completed Prompts. Move active plan out of queue; promote next to Active.
2. **Baseline changes**: Update Test Baseline using the generated count (`pytest --collect-only -q`), not a hand-summed breakdown. Update Static Analysis Baseline with new counts and source plan.
3. **Reconciliation note**: Add a one-line delta to Baseline Reconciliation Notes: `**Plan N**: Baseline → X tests. Delta: ±Y — see CHANGELOG prompt-N.` The "why" goes in CHANGELOG only — don't duplicate it here.
4. **Open question resolved**: Do NOT edit this file's Open Questions section beyond the snapshot count. Strike the question and note the resolving plan in `principles.md` only — that's the sole place resolutions are recorded. Refresh the snapshot count here at the next scan (per `scan.md` step 4).
5. **Edit tool only** — never `sed`, `Set-Content`, or shell redirection (OR7).
