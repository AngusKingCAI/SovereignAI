# SovereignAI — Round Table Prompt v1.0 (Design Review)

**⚠️ HISTORICAL DOCUMENT — Uses pre-v1.4 GR numbering. Current GR rules in .agent/architect/AI_HANDOFF.md Section 3.**

**Date**: 2026-07-03
**Type**: Full prompt (first pass per GR14)
**Material**: `SovereignAI_Consolidated_Design_v1.0.md` (~485KB, ~9,000 lines — full text of 25 source documents) + `SovereignAI_Design_Review_Brief_v1.0.md`

---

## 1. Roles

You are a panelist in a Round Table review of a consolidated design document for **SovereignAI**, a local-first modular AI assistant. Your job is to **find issues, not fixes**. Assume failure. Require a concrete scenario for every finding. Do not propose implementations — propose failure modes.

**Sign every response**: `**Panelist**: <your name/model>`

**Your verdict must be one of**:
- **Pass** — no blocking issues, design is sound
- **Conditional** — issues found but addressable before plan drafting
- **Block** — CRITICAL issues that must be fixed before any plan can be drafted

**Verdict requires majority of assigned panelists** (GR13). Conditional/block verdicts need Architect reasoning (GR4).

---

## 2. Material

### 2.1 Primary material
- **`SovereignAI_Consolidated_Design_v1.0.md`** — ~485KB, ~9,000 lines. Contains the FULL TEXT of 25 source documents concatenated. Nothing has been cut or summarized — every document is reproduced in full. Documents are:

**Process & Governance (Documents 1–7):**
1. AI_HANDOFF.md — Process guide (Architect workflow, Round Table, batch process, plan template)
2. AGENTS.md — 30 AR rules + 27 OR rules, OR1–OR27 (post-20.8 purge)
3. LANDMINES.md — 27 active landmines, L5–L68 (gaps from 20.8 archive of 35 entries; L64 archived, OR45 renumbered out)
4. DECISIONS.md — 7 existing DDs (D1–D7 + D6-Correction)
5. DEBT.md — 6 active deferred items
6. PLANS.md — Baseline 471 tests, 89% coverage, completed prompts, queue
7. CHANGELOG.md — Per-plan change log

**Principles & Department Specs (Documents 8–13):**
8. principles.md — 14 core principles + workflow principles (authority)
9. SovereignAI_Orchestrator_Spec.md — Orchestrator department spec
10. SovereignAI_Coding_Department_Spec.md — Coding department spec
11. SovereignAI_Research_Department_Spec.md — Research department spec
12. SovereignAI_Education_Department_Spec.md — Education department spec
13. SovereignAI_Library_Department_Spec.md — Library department spec

**Design Documents (Documents 14–24):**
14. SovereignAI_Skill_Agent_System_Design_v1.0.md (12 design decisions)
15. SovereignAI_Cross_Department_Messaging_Design_v1.0.md (DD-20.10.4–11)
16. SovereignAI_Worker_Spawning_Design_v1.0.md (DD-21.0.1)
17. SovereignAI_LLM_Function_Calling_Design_v1.0.md (DD-21.3.1)
18. SovereignAI_Hardware_SSE_Streaming_Design_v1.0.md (DD-21.5.1)
19. SovereignAI_Department_Manager_Architecture_Design_v1.0.md (DD-21.7.1)
20. SovereignAI_Diff_Based_Editing_Design_v1.0.md (DD-21.9.1)
21. SovereignAI_Codebase_Indexing_Design_v1.0.md (DD-21.10.1)
22. SovereignAI_Graph_Memory_Backend_Design_v1.0.md (DD-21.12.1)
23. SovereignAI_Models_Panel_Drill_Down_Design_v1.0.md (DD-21.13.1)
24. SovereignAI_Options_Panel_Persistence_Design_v1.0.md (DD-21.15.1)

**Index (Document 25):**
25. SovereignAI_Design_Document_Index.md — navigation, plan queue, open questions

### 2.2 Supporting material
- **`SovereignAI_Design_Review_Brief_v1.0.md`** — index, dependencies, open questions, risks, plan queue

(Note: principles.md, AGENTS.md, LANDMINES.md, DECISIONS.md, DEBT.md, PLANS.md, and CHANGELOG.md are listed above as Documents 2–8 inside the consolidated file — they are NOT separate files to consult. The only separate supporting file is the Brief.)

### 2.3 Review dimensions

Review each DD against:

1. **Principle fit** — Does the DD align with the stated principles? Are there principle violations not flagged?
2. **Internal consistency** — Do DDs contradict each other? Are dependencies correctly mapped?
3. **Codebase delta accuracy** — Does the DD correctly describe what exists vs what's new? (Key codebase facts in the Worker Spawning and Hardware SSE design docs — verified against actual repo code this session.)
4. **AR6 (typed, no context bags)** — Are there `Any`, `dict[str, Any]`, or untyped boundaries?
5. **AR8 (trace side effects)** — Does every side-effectful function emit a trace?
6. **P5 (no speculative contracts)** — Is there infrastructure built before the use case arrives?
7. **P9 (no silent failures)** — Are there failure modes that succeed silently?
8. **P13 (fail gracefully)** — Are there failure modes that hang or cascade?
9. **Concurrency safety** — Are there race conditions, deadlocks, or ordering violations?
10. **Shutdown semantics** — Are drain, sentinel, and timeout behaviors correct?

### 2.4 Risks to verify/refute

- **DD-20.10.7 async delivery**: race condition in worker pool creation? per-handler FIFO guarantee? shutdown liveness?
- **DD-20.10.8 all events persist**: Librarian FIFO backpressure to EventBus? storage growth rate? breaker interaction?
- **DD-20.10.9 versioning**: frozen class enforcement via AST — what if class is renamed? what if frozen set is lost on restart?
- **DD-21.0.1 ThreadPoolExecutor**: GIL impact on sync adapters? cancellation semantics? shutdown blocking?
- **DD-21.3.1 retry**: retry prompt injection of error — could malicious error message manipulate LLM? infinite retry loop?
- **DD-21.7.1 deterministic manager**: validation stage assumes test runner exists — what if no tests? what if Worker claims success but did nothing?
- **DD-21.9.1 search/replace**: ambiguous match disambiguation — what if search_hint is wrong? what if file changed between read and edit (ReAct multi-turn)?
- **DD-21.10.1 codebase index**: tree-sitter on malformed Python? PageRank convergence on disconnected graphs? cache invalidation on file move?
- **DD-21.12.1 graph memory**: recursive CTE performance on large graphs? cycle detection string matching — what if node names contain commas?
- **DD-21.13.1 models panel**: DatabaseProvider contract change — what if existing HF/Ollama providers don't update? sync job crashes mid-way — transaction rollback?
- **DD-21.15.1 options**: Pydantic validation on read — what if stored JSON is from older version with removed fields? schema migration path?

### 2.5 Settled findings (do not re-litigate per GR10)

- **P9 over silent discard**: User directive "log everything is a principle." Selective persistence (DD-20.10.8 Option D) is rejected. Do not re-propose.
- **Async vs sync adapters**: Existing adapters (Ollama, llama.cpp) are SYNC. Do not re-propose asyncio (DD-21.0.1 Option B) without new evidence.
- **EventBus is typed**: Existing EventBus uses frozen dataclass `Event`, not untyped dicts. Do not re-propose wrapper/inheritance (DD-20.10.10 Options B/C) without new evidence.
- **`stream_hardware()` exists**: CapabilityAPI already has `async def stream_hardware()`. Do not re-propose reinvention (DD-21.5.1).
- **OR78 repeal**: User directive in 20.9.2. DD-20.10.0 ratifies. Do not re-propose restoration without new evidence.
- **Round Table bypass for design docs**: DD-misc-1 ratifies User preference. This document IS the Round Table review.
- **L64/OR45 stale citation**: Resolved in Brief §7. L64 archived in 20.8, OR45 renumbered out. Quota-interrupt concern now covered by OR26. Do not re-flag.

---

## 3. Answer Format

For each finding:

```
### Finding F-{N}: {title}

**Severity**: CRITICAL | HIGH | MEDIUM | LOW

**DD affected**: {DD-ID}

**Evidence**:
{concrete scenario — code path, input, or condition that triggers the failure}

**Failure mode**:
{what breaks — data loss, silent corruption, hang, crash, security issue}

**Fix direction** (not implementation):
{suggested approach — 1-2 sentences}

**Panelist**: {name/model}
```

### 3.1 Other concerns

List any concerns that don't rise to finding-level severity but warrant note.

### 3.2 Clean pass

If you find no CRITICAL or HIGH issues, state explicitly:
```
**Clean pass** — no blocking issues found.

**Panelist**: {name/model}
**Verdict**: Pass
```

### 3.3 Verdict

End your response with:
```
**Panelist**: {name/model}
**Verdict**: Pass | Conditional | Block
**Findings**: {count} CRITICAL, {count} HIGH, {count} MEDIUM, {count} LOW
```

---

## 4. Scope boundaries

### 4.1 In scope
- All 22 DDs across the 25 source documents
- Cross-DD consistency and dependencies
- Codebase delta accuracy (verified facts in Worker Spawning and Hardware SSE docs)
- Principle alignment
- Open questions (16 total) — panelists may answer or defer
- Proposed new rules (OR28, OR29) and AR-check scripts
- Blockers list — are all CRITICAL/HIGH from earlier reviews addressed?

### 4.2 Out of scope
- Plan drafting (plans come after design ratification — plan numbers are tentative: 21-24, 26-29, etc. with scans at 25/30/35)
- Implementation details beyond what's in the DDs
- Style/formatting of the consolidated document
- Web research sources (applied as best-practices; not reviewable)

### 4.3 Severity rubric (per AI_HANDOFF)
- **CRITICAL**: Data loss, security, irreversible damage. Blocks.
- **HIGH**: Executor STOP, test failure, broken build. Blocks.
- **MEDIUM**: Degraded functionality, tech debt. Address or document.
- **LOW**: Style, naming. Architect discretion.

---

## 5. Specific questions for panelists

In addition to free-form findings, please address:

1. **DD-20.10.7 per-handler FIFO**: Is one-thread-per-handler the right model, or should there be a bounded worker pool with per-handler queues? What's the failure mode if handler count exceeds thread limit?

2. **DD-20.10.8 all events persist**: At 100 events/sec average (trace + business), that's ~3B events/year. Is 64KB cap + deferred TTL sufficient bounding, or does this need explicit storage budget now?

3. **DD-21.7.1 validation stage**: The Manager runs deterministic validation (e.g., tests) after Worker returns. What if the task has no test command? What if validation itself fails (test runner crashes)? Is the failure mode P9-compliant?

4. **DD-21.9.1 search/replace in ReAct multi-turn**: After Turn 2's edit, the file changes. Turn 3's search block was composed from Turn 1's observation. Is this the same drift problem as line-range (E), or does content-based matching actually solve it? What if the file was edited by another process between turns?

5. **DD-21.12.1 recursive CTE cycle detection**: The `path` column uses comma-separated strings. What if a node ID contains a comma? What if the graph has 10K+ nodes — is string matching performant?

6. **DD-21.13.1 DatabaseProvider contract change**: Extending `health_check()` return type is a breaking change to existing HF/Ollama providers. How should this migration be sequenced? What if a provider doesn't update?

7. **Cross-DD: EventBus + WorkerPool + Librarian**: Three subsystems with circuit breakers (DD-20.10.7, DD-21.0.1, DD-20.10.8). Is there a cascading failure mode where one breaker trips another? E.g., Librarian breaker trips → events stop persisting → does EventBus breaker trip?

8. **Process: 3 consecutive design questions had factual errors about codebase**. Is the design process itself sound, or does it need a mandatory "read existing code before designing" step? Should this be a new OR rule?

9. **Plan queue sequencing**: Plans 21-24 (batch 1) cover event system + trace queue + worker spawning. Are these the right first 4 plans, or should skill framework (Plan 26) come first since the event system has no consumers until skills exist?

10. **Department specs vs design docs**: The 5 department specs (Documents 9–13) predate this design session. Do they conflict with any of the 22 DDs? Are there assumptions in the specs that the DDs invalidate?

---

## 6. Delivery notes

- Findings without evidence auto-dropped (per AI_HANDOFF Round Table section)
- Architect will explicitly accept/reject every finding with reasoning (GR4)
- On clean pass, Architect posts panelist scorecard inline (GR16)
- User may force-stop Round Table at any time
- Each rev brings new evidence — no re-litigating settled findings (GR10)

---

## 7. Read order (per Design Document Index)

1. `SovereignAI_Design_Review_Brief_v1.0.md` — brief (start here)
2. This prompt — review dimensions, risks, settled findings
3. `SovereignAI_Consolidated_Design_v1.0.md` — all 25 documents in full
4. Individual design docs (Documents 14–24) for deep dives
5. principles.md (Document 8) + AGENTS.md (Document 2) for principle/rule lookup

---

*End of prompt.*
