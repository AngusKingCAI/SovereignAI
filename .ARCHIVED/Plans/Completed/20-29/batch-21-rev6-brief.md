# Batch 21 Rev 6 Brief

## 1. Context

**Baseline**: 497 tests, 0 ruff, 0 mypy, 89% coverage (prompt-20.9.9).
**Latest tag**: prompt-20.9.9 (2026-07-03).
**Active plan**: None — awaiting Batch 21 delivery.
**Repo**: Python v1, Windows-only. 14 principles + 66 ORs + 47 landmines.
**Key existing types**: Event(channel, correlation_id, timestamp), Channel=NewType(str), ComponentManifest, DIContainer(register_singleton, register_factory, retrieve), CapabilityGraph(register(manifest), list_all_components).
**FastAPI lifespan**: EXISTS in web/main.py (lines 44-53) — calls build_container() + container.start().

## 2. Plans in this batch

| Plan | Title | Depends on | Vision principles |
|---|---|---|---|
| 21 | Skill Framework Foundation | prompt-20.9.9 | P1, P2, P5, P11 |
| 22 | ReAct Agent Capability | Plan 21 | P1, P2, P5, P9, P11 |
| 23 | Typed Event System + Hardware SSE | prompt-20.9.9 | P7, P9, P13 |
| 24 | Department Manager + Coding Infrastructure | Plan 22, Plan 23 | P1, P2, P5, P7, P9 |

## 3. Decisions proposed

**DD-23.1** (Proposed): Circuit breaker on per-handler errors. Rule: >50 errors/10s = unsubscribe handler. Rejected alternative: process-level circuit breaker (too coarse). Consequence: one bad handler doesn't kill the bus.
**DD-24.1** (Proposed): SymbolMap uses tree-sitter-python (pre-compiled wheels) with DEGRADED fallback. Rule: wrap import in try/except; health_check returns DEGRADED. Rejected alternative: regex fallback (false confidence). Consequence: Windows install always works; no C compiler needed.

## 4. Decisions carried forward

DD-20.10.1 (Bounded queues), DD-20.10.2 (Circuit breaker pattern), DD-21.7.1 (One worker per task), DD-21.9.1 (Search/replace + line hint), DD-21.10.1 (No embeddings). Pointers in DECISIONS.md.

## 5. Questions for Round Table

Q-24.1: Does DIContainer.register_factory() support callable retrieval? Existing container has register_factory but plan assumes container.retrieve(SymbolMapFactory) returns a callable.
Q-24.2: Does CapabilityGraph.register() accept ComponentManifest for skill registration? Existing API takes manifest + instance; Plan 21 S7 needs skill_id→manifest resolution.

## 6. Open questions resolved

None in this batch.

## 7. Risks flagged

- **R-21.1**: Existing CapabilityGraph (183 lines) has ComponentManifest-based API. Plan 21 Rev 5 proposed incompatible dict-based registry (S0.5) — REMOVED in Rev 6. Risk: existing register() may not support skill discovery patterns.
- **R-23.1**: EventBus.start()/stop() merged into existing FastAPI lifespan. Risk: lifespan failure breaks existing startup sequence.
- **R-23.2**: Drop-newest queue policy may starve slow handlers. Risk: handler never catches up.
- **R-24.1**: SymbolMapFactory via DIContainer.register_factory(). Risk: container.retrieve() may not return callable.
- **Landmine pre-screen**: L69 (untracked deletion) — plans use commit workflow. L54 (ContentSwitcher) — no Textual imports. L52 (TEST_MODE) — no env hooks. All OK.

## 8. Coverage target

Plan 21: 12 tests. Plan 22: 7 tests. Plan 23: 7 tests. Plan 24: 9 tests. Batch target: +35 tests → 532 total. Floor: 90% coverage per OR43.

## 9. Round Table protocol reminder

Per GR14: this is a diff-summary prompt (Rev 6). Panelists review CHANGED sections only. Settled findings listed — do not re-litigate (GR10). Each finding needs concrete scenario + evidence. Sign as **Panelist**: <name/model>.

## 10. Superseded decisions

DD-21.1.10 (Proposed in Rev 3): CapabilityGraph as simple dict registry. Superseded by using existing CapabilityGraph with ComponentManifest. Replaced by: existing D2 (hand-rolled DI + CapabilityGraph).
