# SovereignAI — Design Review Brief v1.0

**Date**: 2026-07-03
**Batch**: Design review (not plan review)
**Material**: `SovereignAI_Consolidated_Design_v1.0.md` (full text of 25 source documents, ~485KB, ~9,000 lines)

---

## 1. Context

- **Baseline**: 471 tests, 0 skipped, 89% coverage (Plan 20.9.5 `/close`)
- **Repo state**: tag `prompt-20.9.5` on origin, latest commit `58e67da`
- **Governance**: AGENTS.md 5,993 chars (30 AR + 27 OR rules, OR1–OR27), LANDMINES.md 27 active entries (L5–L68, gaps from 20.8 archive of 35 entries), DECISIONS.md 7 DDs (D1–D7 + D6-Correction)
- **Active DEBT**: 6 items (Snyk auth, diskcache CVE, first-run UI, setuptools CVEs, pip-audit CVEs, TraceEmitter bounded queue)
- **Open governance issues**: OR78 repeal unratified (DD-20.10.0); spec_match ALLOWLIST growth unaudited
- **Design docs reviewed**: 25 source documents (process guide + 6 governance files + principles + 5 department specs + 11 design docs + index) = 22 DDs total
- **Round Table bypass**: Design docs bypassed RT per User preference (DD-misc-1); this IS the RT review
- **Consolidated document**: `SovereignAI_Consolidated_Design_v1.0.md` — ~485KB, ~9,000 lines, full text of all 25 sources, nothing cut

## 2. DDs in this batch

| DD-ID | Title | Depends on | Principles |
|---|---|---|---|
| DD-20.10.0 | OR78 repeal ratification | None | Process |
| DD-20.10.1 | Trace queue circuit breaker | None | P9/P13/P7 |
| DD-20.10.2 | Sentinel-based drain exit | DD-20.10.1 | P9/P13 |
| DD-20.10.3 | Queue strategy taxonomy | DD-20.10.1 | P9/P13/P7 |
| DD-20.10.4 | Event schema base (8 fields) | None | P9/AR8/AR23 |
| DD-20.10.5 | Event type registry (explicit) | DD-20.10.4 | P1/P5/D2/D4 |
| DD-20.10.6 | Consumer registration (signature-validated) | DD-20.10.5 | D2/D4/P1/AR6 |
| DD-20.10.7 | Fan-out delivery (async + breaker) | DD-20.10.6 | P9/P13/AR8 |
| DD-20.10.8 | All events persist via Librarian | DD-20.10.7 | P4/P9/AR2 |
| DD-20.10.9 | Versioning + major-bump escape | DD-20.10.4 | P4/P5/AR6/AR17 |
| DD-20.10.10 | EventBus integration (extend in place) | DD-20.10.4–9 | P5 |
| DD-20.10.11 | Plan scope (event system) | All 20.10.x | Process |
| DD-21.0.1 | Worker spawning (ThreadPoolExecutor) | None | P4/P5/P13/AR7 |
| DD-21.3.1 | Tool call generation (single-call + retry) | None | P2/P3/P5/AR6 |
| DD-21.5.1 | Hardware SSE (wraps stream_hardware) | None | P8/AR13/AR24 |
| DD-21.7.1 | Department manager (deterministic + 1 ReAct) | DD-21.0.1/21.3.1/21.10.1 | P5/AR1/P13 |
| DD-21.9.1 | Diff editing (search/replace + hint) | DD-21.3.1 | P3/P5/P9/P13/AR8 |
| DD-21.10.1 | Codebase indexing (symbol map) | None | P3/P4/P5/AR6/AR8 |
| DD-21.12.1 | Graph memory (SQLite EAV + CTE) | None | P4/P5/AR6/AR19/AR21 |
| DD-21.13.1 | Models panel drill-down (4-table) | DD-21.5.1/21.15.1 | P4/P5/AR6/AR21/AR25/AR26 |
| DD-21.15.1 | Options persistence (SQLite + Pydantic) | None | P4/P5/AR6/AR21/AR8 |
| DD-misc-1 | RT bypass for design docs | None | Process |

## 3. Decisions proposed (GR6/GR8)

- **DD-20.10.0**: OR78 repeal — rule: ratify removal; rejected: restore check (re-introduces 20.7.3 STOPs); consequence: L50 updated to "superseded"
- **DD-20.10.1**: Trace breaker — rule: high/low watermark + aggregate events; rejected: silent discard (P9 viol), per-drop trace (amplification); consequence: producers handle deferred flag
- **DD-20.10.2**: Sentinel — rule: identity-checked DRAIN_SHUTDOWN, breaker bypass; rejected: None/string/enum/Event; consequence: shutdown liveness guaranteed
- **DD-20.10.3**: Strategy taxonomy — rule: trace=breaker, worker=block, drop forbidden; rejected: unbounded block; consequence: TraceEmitter never blocks callers
- **DD-20.10.4**: Event schema — rule: 8 fields, no task_id/memory_scope; rejected: dict payload, task_id, memory_scope; consequence: 5 callsites update
- **DD-20.10.5**: Registry — rule: explicit register() in main.py; rejected: central/types.py, manifest, auto-discover; consequence: check_event_registration.py enforces
- **DD-20.10.6**: Subscribe — rule: inspect.signature validation + subscribe_all tier; rejected: @on_event decorator, auto-wire; consequence: OR29 proposed
- **DD-20.10.7**: Delivery — rule: per-handler FIFO + breaker, one thread per handler; rejected: point-to-point, hybrid, channel; consequence: ~60 threads acceptable
- **DD-20.10.8**: Persistence — rule: ALL events persist via Librarian subscribe_all; rejected: selective ClassVar (User rejected); consequence: 64KB cap, TTL deferred
- **DD-20.10.9**: Versioning — rule: forward-compat (C) + major bump (B); rejected: no versioning, per-event migration; consequence: OR28 proposed, check_event_frozen.py
- **DD-20.10.10**: Integration — rule: extend in place, 5 callsites; rejected: wrapper, inheritance, parallel; consequence: atomic migration, no coexistence
- **DD-20.10.11**: Plan scope — rule: 2 event plans + 1 trace plan; rejected: single plan (too large), 4 plans (too granular); consequence: see plan queue
- **DD-21.0.1**: Workers — rule: ThreadPoolExecutor max 4, sync; rejected: asyncio (adapters sync), process pool, hybrid; consequence: no adapter rewrites
- **DD-21.3.1**: Tool calls — rule: single-call + Pydantic + retry; rejected: native (P3), two-step (P3-soft), hybrid (P5); consequence: adapter interface unchanged
- **DD-21.5.1**: Hardware SSE — rule: wrap stream_hardware(); rejected: EventBus (6GB/year), polling, reinvent; consequence: ~15 lines web endpoint
- **DD-21.7.1**: Manager — rule: deterministic + 1 ReAct Worker; rejected: LLM planner, router, hybrid (conflates Worker/Tool), state machine; consequence: supersede path to multi-Worker
- **DD-21.9.1**: Diff editing — rule: search/replace + optional hint; rejected: naive A, whole-file, sed, adaptive, line-range (silent corruption); consequence: ~150 lines parser
- **DD-21.10.1**: Codebase index — rule: symbol map + tree-sitter + hand-rolled PageRank; rejected: embeddings (P3), hybrid, file tree, networkx; consequence: 2 new deps
- **DD-21.12.1**: Graph memory — rule: SQLite EAV + recursive CTE + cycle detection; rejected: NetworkX, Kuzu, hybrid, JSON blob; consequence: GraphQuery in Librarian match
- **DD-21.13.1**: Models panel — rule: 4-table per existing spec; rejected: adjacency list, materialized path; consequence: DatabaseProvider contract extends
- **DD-21.15.1**: Options — rule: SQLite + Pydantic-validated; rejected: JSON blob Any (AR6), TOML, env vars, hybrid; consequence: ~150 lines
- **DD-misc-1**: RT bypass — rule: design docs bypass RT, plans don't; rejected: force RT on design docs; consequence: this document IS the RT review

## 4. Decisions carried forward (GR9)

Existing DDs in DECISIONS.md (D1–D7 + D6-Correction) — pointer only, not duplicated. Key ones referenced:
- D2 (hand-rolled DI, no magic) — underpins DD-20.10.5/6
- D4 (explicit wiring in main.py) — underpins DD-20.10.5/6, DD-21.0.1
- D6 (no docstrings, AR11) — underpins all example code

## 5. Questions for Round Table (GR15)

- Q-20.10.1: Trip-count gauge on trace breaker?
- Q-20.10.2: Sentinel bypass of breaker? (proposed Accepted)
- Q-20.10.3: Per-handler breaker threshold (50/10s)?
- Q-20.10.4: 64KB episodic payload cap right size?
- Q-20.10.5: Old frozen class removal policy?
- Q-20.10.6: Time-travel replay?
- Q-20.10.7: Encryption-at-rest for events?
- Q-21.0.1: max_workers=4 right size?
- Q-21.3.1: MAX_RETRIES=3 right count?
- Q-21.5.1: Heartbeat now or defer?
- Q-21.7.1: When to promote F → multi-Worker?
- Q-21.9.1: Fuzzy matching threshold?
- Q-21.10.1: Symbol map cache persistent?
- Q-21.12.1: When to add networkx?
- Q-21.13.1: DatabaseProvider contract change handling?
- Q-21.15.1: Settings registry mechanism?

## 6. Open questions resolved (GR2)

- "How should dropped queue items be handled?" → DD-20.10.1 (breaker)
- "What sentinel for drain exit?" → DD-20.10.2 (identity-checked)
- "What should block strategy do?" → DD-20.10.3 (timeout fallthrough to breaker)
- "Event schema base?" → DD-20.10.4 (8 fields, Option B)
- "Event type registry?" → DD-20.10.5 (Option D-refined, explicit)
- "Consumer registration?" → DD-20.10.6 (Option C, signature-validated)
- "Delivery model?" → DD-20.10.7 (Option B, fan-out with refinements)
- "Persistence?" → DD-20.10.8 (Option C, all events — User directive)
- "Versioning?" → DD-20.10.9 (Option C+B)
- "EventBus integration?" → DD-20.10.10 (Option A, extend in place)
- "Plan scope?" → DD-20.10.11 (Option B refined, 2 plans + trace plan)
- "Worker spawning?" → DD-21.0.1 (Option A, ThreadPoolExecutor)
- "Tool call generation?" → DD-21.3.1 (Option E, single-call + retry)
- "Hardware SSE?" → DD-21.5.1 (Option A, wrap existing)
- "Department manager?" → DD-21.7.1 (Option F, deterministic + 1 ReAct)
- "Diff editing?" → DD-21.9.1 (Option A+, search/replace + hint)
- "Codebase indexing?" → DD-21.10.1 (Option B, symbol map)
- "Graph memory?" → DD-21.12.1 (Option B, SQLite EAV)
- "Models panel?" → DD-21.13.1 (existing spec, 4-table)
- "Options persistence?" → DD-21.15.1 (Option E, SQLite + Pydantic)

## 7. Risks flagged (GR12)

- **L50/L68**: Plan file mutation — DD-20.10.0 ratifies OR78 removal
- **L22/L48**: AR check self-modification — new check scripts must not be edited in same commit as core
- **L48**: spec_match ALLOWLIST growth — audit per plan
- **L49**: AR7 allowlist expansion — TUI_PANELS_ALLOWED_IMPORTS removed in 20.9.1
- **L45**: Stray files — OR23 scan in /close
- **L39**: Pre-existing test failures — OR19
- **L67**: Plan split without /open + /close
- **L68**: Plan split with content modification
- **Process**: 3 consecutive design questions had factual errors about codebase — verify before proposing
- **Stale citation corrected (this rev)**: Brief v1.0 erroneously cited "L64: Quota interrupt — OR45". L64 was added in 20.7.3 then archived in 20.8's LANDMINES purge (now at `archive/LANDMINES-ARCHIVE.md:209`). OR45 was renumbered out in 20.8's AGENTS.md purge — OR rules now run OR1–OR27. The quota-interrupt-without-re-read concern is covered by OR26 ("Follow skill workflows systematically. Never skip steps"). Also corrected: "18 active landmines" was the post-20.8 count; actual count is now 27 (9 added in 20.9.x: L67, L68, and others restored).

## 8. Coverage target

N/A — this is a design review, not a plan review. Coverage targets apply per-plan at `/close`.

## 9. Round Table protocol reminder

- Find issues, not fixes (GR3)
- Assume failure, require concrete scenario
- Sign `**Panelist**: <name/model>` (GR3)
- Severity + Evidence + Fix per finding (GR14)
- No re-litigating settled findings (GR10)
- Items without evidence auto-dropped
- Majority of panelists must return verdict (GR13)
- Conditional/block verdicts need Architect GR4 reasoning

## 10. Superseded decisions (GR7)

None — no existing DDs in DECISIONS.md are superseded by this batch. DD-20.10.0 ratifies a prior user directive (OR78 repeal) but does not supersede a DD.

---

## Plan Queue (Tentative — Not Yet Numbered)

Plans will be numbered sequentially starting at 21. Scans at 25, 30, 35, 40... per AI_HANDOFF "Scan every 5 plans."

| Plan # | Scope | Depends On | Batch |
|---|---|---|---|
| Plan 21 | Event system foundation (typed events, registry, versioning, OR28/OR29) | None | 1 |
| Plan 22 | Event delivery hardening + persistence (async, breaker, Librarian) | Plan 21 | 1 |
| Plan 23 | Trace queue hardening (circuit breaker, sentinel, strategy) | None | 1 |
| Plan 24 | Worker spawning (ThreadPoolExecutor, WorkerPool) | None | 1 |
| **Plan 25** | **SCAN** | — | — |
| Plan 26 | Skill framework core (manifest, SkillRunner, registration) | None | 2 |
| Plan 27 | Initial skills (file_read, file_write, file_search, web_search, web_fetch) | Plan 26 | 2 |
| Plan 28 | ReAct meta-skill (loop, ToolCallParser, session) | Plan 26, Plan 27 | 2 |
| Plan 29 | Codebase indexing service (symbol map, tree-sitter, PageRank) | None | 2 |
| **Plan 30** | **SCAN** | — | — |
| Plan 31 | file_edit skill (diff-based editing, A+ parser) | Plan 26 | 3 |
| Plan 32 | Coding Department Manager (deterministic pipeline) | Plan 28, Plan 29 | 3 |
| Plan 33 | Graph memory backend (SQLite EAV + recursive CTE) | None | 3 |
| Plan 34 | Options panel persistence (OptionsBackend + settings classes) | None | 3 |
| **Plan 35** | **SCAN** | — | — |
| Plan 36 | Hardware SSE streaming (wraps stream_hardware) | None | 4 |
| Plan 37 | Models panel drill-down (4-table schema + sync + SSE + UI) | Plan 36, Plan 34 | 4 |
| Plan 38+ | Web skills, UI integration, MCP, shell, git (future) | TBD | 4+ |

---

*Brief — 80 lines target exceeded due to volume (22 DDs across 25 documents). Per GR11, briefs ≤80 lines; this is a design review brief covering 22 DDs across 6 subsystems, not a standard 4-plan batch brief. Architect discretion applied.*
