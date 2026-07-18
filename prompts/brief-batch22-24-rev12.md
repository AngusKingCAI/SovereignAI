# Brief — Batch 22-24 Rev 12

## 1. Context

Baseline 531 tests (prompt-plan-fix-1-Rev1, 2026-07-18). Renumbering: old Plan 22 (ReActLoop) ↔ old Plan 23 (Typed EventBus) swapped so execution order matches numerical order. Plans aligned with workflow-fix-2 through plan-fix-1-Rev1 changes (S0.0-S0.5 template, landmine M1-M4 compliance, rule rename to UOR/VOR/OOR/COR/SOR, `asyncio.timeout()`, env-based `pytest.skip`).

## 2. Plans in this batch

| # | Title | Depends on | Vision principles |
|---|-------|-----------|-------------------|
| 22 | Typed EventBus (was old 23) | prompt-20.9.9 | P7, P9, P13 |
| 23 | ReActLoop (was old 22) | prompt-21, Plan 22 | P1, P2, P5, P9, P11 |
| 24 | Departments | Plan 22, Plan 23 | P1, P2, P5, P7, P9 |

## 3. Decisions proposed

- DD-22.1: AR7 circuit-breaker extended to EventBus handlers; key=(handler_id, event_type); Librarian system-critical (no auto-unsubscribe)
- DD-22.11.1: Critical overflow emits at ERROR level (not CRITICAL) to avoid feedback loop
- DD-22.11.2: Pre-start critical events protected in separate buffer (maxsize=10000)
- DD-22.11.3: Critical overflow = best-effort with SQLite fallback, not guaranteed
- DD-22.11.7: Pre-start non-critical buffer overflow = drop-oldest with dropped_count
- DD-22.11.9: Critical overflow emission MUST use __publish_internal() with trace_level=ERROR
- DD-22.11.10: Librarian replay task lifecycle (child of drain task)
- DD-23.11.1: ReActLoopFactory Protocol + concrete ReActLoop key, both unconditionally registered
- DD-23.11.3: GraphMemory Protocol with @runtime_checkable
- DD-24.11.1: execute_task try/finally for graph_memory.close()
- DD-24.11.2: TaskGraphCache.close() idempotent via _closed flag
- DD-24.11.3: ctx=None warning logged BEFORE worker spawn
- DD-24.11.4: Latency test warmup + 5-run median, all timings in failure output

## 4. Decisions carried forward

DD-20.10.8, DD-21.7.1, DD-21.9.1, DD-21.10.1, DD-21.12.1 — see `.agent/shared/DECISIONS.md` (pending verification; see Q-RT.1, Q-RT.2).

## 5. Questions for Round Table

- Q-RT.1: Are DD-21.7.1, DD-21.9.1, DD-21.10.1, DD-21.12.1 actually in Plan 21 text? If not, remove citations.
- Q-RT.2: Does Librarian (`app/sovereignai/librarian/librarian.py`) have `handle_event` method? If not, defer Plan 22 S5.
- Q-RT.3: Plans at 121/135/128 lines exceed ≤120 limit. Acceptable or trim?
- Q-RT.4: EventBus constructor breaking change (Plan 22 S1) — any call sites beyond `app/sovereignai/main.py:37`?
- Q-RT.5: Does `ar_checks/run_all.py` auto-discover new scripts, or need explicit registration for `check_event_registration.py`, `check_event_frozen.py`?

## 6. Open questions resolved

Q-22.1 through Q-22.6 (EventBus four-state, critical routing, lifespan ordering, _publish_internal, pre-start buffers). Q-23.1 through Q-23.5 (ReActLoopFactory Protocol, UUID session keys, TraceEmitterWrapper level, ISkillRunner close, GraphMemory Protocol). Q-24.1 through Q-24.4 (DIContainer factory, GraphMemoryBackend wiring, build_context return, ephemeral scope).

## 7. Risks flagged

- R1: Renumbering confusion (old "Plan 22" references in completed plans/logs mean ReActLoop, not new Typed EventBus). Mitigated by clear `Depends on:` headers.
- R2: 4 DD-21.x.x citations in Plan 24 unverified (Q-RT.1).
- R3: DD-20.10.8 reference in Plan 22 S5 unverified; Plan 20.10 may not have shipped (Q-RT.2).
- R4: Plan 22 S1 breaking change to EventBus constructor — verify no other call sites (Q-RT.4).
- R5: ~13 new DD-IDs need propagation to DECISIONS.md at /close step 12 per GR6.
- R6: Plan 23 S2.3 GraphMemory Protocol claim "Plan 24's TaskGraphCache satisfies this Protocol structurally" unverifiable until Plan 24 lands.
- R7: Plan 22 S4 `__publish_internal()` name mangling may not resolve in nested drain task closures.
- R8: Plan 22 S5 `librarian_overflow.sqlite` hardcoded path may collide across test fixtures.
- R9: Plan 24 S4 tree-sitter silently degrades if package not installed; verify `health_check()` loudness.
- Landmine pre-screen: M1-M4 addressed in each plan's S10/S11. M5 addressed in Plan 24 S4 (env-based skip).

## 8. Coverage target

≥90% per plan. Test files in `.agent/executor/tests/sovereignai/` per landmine M4. Plan 22: ~6 test files. Plan 23: ~9 test files. Plan 24: ~9 test files.

## 9. Round Table protocol reminder

Full first-pass prompt per GR10. Severity: CRITICAL/HIGH block; MEDIUM address or document; LOW Architect discretion. Majority verdict per plan (Pass/Conditional/Block) before delivery (GR9). Conditional/block needs GR3 reasoning. No host paths (GR4). Sign every response: `**Panelist**: <name/model>`. Find issues, not fixes.

## 10. Superseded decisions

DD-21.12.1 ("SQLite already required") — superseded by factual correction: `sqlite3` is Python stdlib, no requirements.txt entry needed. No new DD-ID (correction, not architectural change).
