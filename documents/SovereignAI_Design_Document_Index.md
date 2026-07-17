# SovereignAI — Design Document Index

**Status**: Living document
**Date**: 2026-07-03 (synced with consolidated package v1.0)
**Author**: Architect

---

## Purpose

This index catalogs all design documents in the SovereignAI project. It is the navigation entry point for Architects, Executors, and Round Table panelists.

**SSOT principle**: Each design decision lives in ONE document. This index points to documents, never duplicates their content.

**Package note (this session)**: For Round Table review, all 25 source documents below have been consolidated into a single file — `SovereignAI_Consolidated_Design_v1.0.md` (~485KB, ~9,000 lines). Governance files (Category A), department specs (Category B), and design docs (Category C) are NOT separate uploads for this review round — they are Documents 1–25 inside the consolidated file. The "Location" column below shows where each document lives in the repo for ongoing reference; for THIS review, panelists read them inline in the consolidated file.

---

## Document Categories

### A. Process & Governance (always-on)
These documents define HOW we work, not WHAT we build.

| Document | Location (repo) | Doc # in consolidated | Responsibility |
|---|---|---|---|
| `AI_HANDOFF.md` | repo root | 1 | Process guide — Architect workflow, Round Table, batch process, plan template |
| `AGENTS.md` | repo root | 2 | 30 AR rules + 27 OR rules, OR1–OR27 (post-20.8 purge) |
| `LANDMINES.md` | repo root | 3 | 27 active failure patterns (L5–L68, gaps from 20.8 archive of 35 entries; L64 archived, OR45 renumbered out) |
| `DECISIONS.md` | repo root | 4 | Architectural decisions record (D1–D7 + D6-Correction) |
| `DEBT.md` | repo root | 5 | Deferred items register |
| `PLANS.md` | repo root | 6 | Dynamic state, baselines, queue |
| `CHANGELOG.md` | repo root | 7 | Per-plan change log |
| `.devin/skills/*/SKILL.md` | `.devin/skills/` | not in consolidated | Workflow skills (open, close, verify, scan) — excluded from this review; not design content |

### B. Architecture & Department Specs
These documents specify WHAT to build at the system and department level.

| Document | Location (repo) | Doc # in consolidated | Status |
|---|---|---|---|
| `principles.md` | `documents/` | 8 | 14 core principles + workflow principles (authority) |
| `SovereignAI_Orchestrator_Spec.md` | `documents/` | 9 | Draft v1 |
| `SovereignAI_Coding_Department_Spec.md` | `documents/` | 10 | Draft v1 |
| `SovereignAI_Research_Department_Spec.md` | `documents/` | 11 | Draft v1 |
| `SovereignAI_Education_Department_Spec.md` | `documents/` | 12 | Draft v2 |
| `SovereignAI_Library_Department_Spec.md` | `documents/` | 13 | Draft v1 |
| `SovereignAI_Architecture_Decisions.md` | `documents/` | **excluded** | Historical (pre-DECISIONS.md) — superseded by Document 4 (DECISIONS.md). Deliberately excluded from this review round; cited here for traceability. |
| `models-panel-spec.md` | `documents/` | **excluded** | Draft — partially superseded by Plan 17. Deliberately excluded from consolidated; DD-21.13.1 (Models Panel Drill-Down design, Document 23) reproduces the relevant §3 schema inline. Cited here for traceability. |
| `project-vision-Rev5.md` | `documents/` | **excluded** | Historical reference only — founding vision, not active design. Deliberately excluded from this review round. |

**Exclusion confirmation**: The three "excluded" entries above are intentionally omitted from the 25-document consolidated file, not oversights. `SovereignAI_Architecture_Decisions.md` is superseded by DECISIONS.md (Document 4). `models-panel-spec.md`'s relevant content is reproduced in DD-21.13.1 (Document 23). `project-vision-Rev5.md` is historical founding vision, not active design under review.

### C. Design Documents (this session)
These documents specify HOW to build specific subsystems. Each contains Design Decisions (DDs) for Round Table ratification.

| Document | Location (repo) | Doc # in consolidated | DDs | Status |
|---|---|---|---|---|
| `SovereignAI_Skill_Agent_System_Design_v1.0.md` | design_docs/ | 14 | (12 decisions in §2) | Draft v1.0 |
| `SovereignAI_Cross_Department_Messaging_Design_v1.0.md` | design_docs/ | 15 | DD-20.10.4–11 | Draft v1.0 |
| `SovereignAI_Worker_Spawning_Design_v1.0.md` | design_docs/ | 16 | DD-21.0.1 | Draft v1.0 |
| `SovereignAI_LLM_Function_Calling_Design_v1.0.md` | design_docs/ | 17 | DD-21.3.1 | Draft v1.0 |
| `SovereignAI_Hardware_SSE_Streaming_Design_v1.0.md` | design_docs/ | 18 | DD-21.5.1 | Draft v1.0 |
| `SovereignAI_Department_Manager_Architecture_Design_v1.0.md` | design_docs/ | 19 | DD-21.7.1 | Draft v1.0 |
| `SovereignAI_Diff_Based_Editing_Design_v1.0.md` | design_docs/ | 20 | DD-21.9.1 | Draft v1.0 |
| `SovereignAI_Codebase_Indexing_Design_v1.0.md` | design_docs/ | 21 | DD-21.10.1 | Draft v1.0 |
| `SovereignAI_Graph_Memory_Backend_Design_v1.0.md` | design_docs/ | 22 | DD-21.12.1 | Draft v1.0 |
| `SovereignAI_Models_Panel_Drill_Down_Design_v1.0.md` | design_docs/ | 23 | DD-21.13.1 | Draft v1.0 |
| `SovereignAI_Options_Panel_Persistence_Design_v1.0.md` | design_docs/ | 24 | DD-21.15.1 | Draft v1.0 |

### D. Review Artifacts (this session)
These documents are produced for Round Table review of the design docs. All three live in `download/` as standalone files.

| Document | Location | Purpose |
|---|---|---|
| `SovereignAI_Design_Review_Brief_v1.0.md` | download/ | Brief per AI_HANDOFF Brief Format — index, dependencies, open questions, risks, plan queue |
| `SovereignAI_Round_Table_Prompt_v1.0.md` | download/ | Full prompt per GR14 — review dimensions, risks, settled findings, specific questions, read order (§7) |
| `SovereignAI_Consolidated_Design_v1.0.md` | download/ | All 25 source documents (governance + specs + design docs + this index) in one file (~485KB, ~9,000 lines). Nothing cut or summarized. |

---

## Design Decision (DD) Index

| DD-ID | Title | Document (Doc #) | Status |
|---|---|---|---|
| DD-20.10.0 | OR78 repeal ratification | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.1 | Trace queue circuit breaker | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.2 | Sentinel-based drain exit | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.3 | Queue strategy taxonomy | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.4 | Event schema base (8 fields) | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.5 | Event type registry (explicit) | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.6 | Consumer registration (signature-validated) | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.7 | Fan-out delivery (async + breaker) | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.8 | All events persist via Librarian | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.9 | Versioning + major-bump escape | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.10 | EventBus integration (extend in place) | 15 (Cross-Dept Messaging) | Proposed |
| DD-20.10.11 | Plan scope (event system) | 15 (Cross-Dept Messaging) | Proposed |
| DD-21.0.1 | Worker spawning (ThreadPoolExecutor) | 16 (Worker Spawning) | Proposed |
| DD-21.3.1 | Tool call generation (single-call + retry) | 17 (LLM Function Calling) | Proposed |
| DD-21.5.1 | Hardware SSE (wraps stream_hardware) | 18 (Hardware SSE) | Proposed |
| DD-21.7.1 | Department manager (deterministic + 1 ReAct) | 19 (Dept Manager) | Proposed |
| DD-21.9.1 | Diff editing (search/replace + hint) | 20 (Diff-Based Editing) | Proposed |
| DD-21.10.1 | Codebase indexing (symbol map) | 21 (Codebase Indexing) | Proposed |
| DD-21.12.1 | Graph memory (SQLite EAV + CTE) | 22 (Graph Memory) | Proposed |
| DD-21.13.1 | Models panel drill-down (4-table) | 23 (Models Panel) | Proposed |
| DD-21.15.1 | Options persistence (SQLite + Pydantic) | 24 (Options Persistence) | Proposed |
| DD-misc-1 | RT bypass for design docs | (process) | Proposed |

---

## Plan Queue (Tentative — Not Yet Numbered)

Plans will be numbered sequentially starting at 21. Scans occur every 5 plans (25, 30, 35...). Plan numbers are NOT final until plans are drafted.

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

**Batch composition** (per AI_HANDOFF "4 plans per batch"):
- **Batch 1**: Plans 21-24 (event system + trace queue + worker spawning)
- **Batch 2**: Plans 26-29 (skill framework + initial skills + ReAct + codebase index)
- **Batch 3**: Plans 31-34 (file_edit + coding manager + graph memory + options)
- **Batch 4**: Plans 36-37+ (hardware SSE + models panel + future)

Scans at Plans 25, 30, 35, 40... per AI_HANDOFF "Scan every 5 plans."

---

## Open Questions Index

| Q-ID | Question | Source DD |
|---|---|---|
| Q-20.10.1 | Trip-count gauge on trace breaker? | DD-20.10.1 |
| Q-20.10.2 | Sentinel bypass of breaker? | DD-20.10.2 |
| Q-20.10.3 | Per-handler breaker threshold? | DD-20.10.7 |
| Q-20.10.4 | 64KB episodic payload cap right size? | DD-20.10.8 |
| Q-20.10.5 | Old frozen class removal policy? | DD-20.10.9 |
| Q-20.10.6 | Time-travel replay? | DD-20.10.9 |
| Q-20.10.7 | Encryption-at-rest for events? | DD-20.10.8 |
| Q-21.0.1 | max_workers=4 right size? | DD-21.0.1 |
| Q-21.3.1 | MAX_RETRIES=3 right count? | DD-21.3.1 |
| Q-21.5.1 | Heartbeat now or defer? | DD-21.5.1 |
| Q-21.7.1 | When to promote F → multi-Worker? | DD-21.7.1 |
| Q-21.9.1 | Fuzzy matching threshold? | DD-21.9.1 |
| Q-21.10.1 | Symbol map cache persistent? | DD-21.10.1 |
| Q-21.12.1 | When to add networkx? | DD-21.12.1 |
| Q-21.13.1 | DatabaseProvider contract change handling? | DD-21.13.1 |
| Q-21.15.1 | Settings registry mechanism? | DD-21.15.1 |

---

## Proposed New Rules

| Rule | Text | Enforced by |
|---|---|---|
| OR28 | Event payload classes with version marked frozen in EventRegistry must not be edited. Edits = STOP. | `check_event_frozen.py` |
| OR29 | Every Pydantic BaseModel subclass with `event_type: ClassVar[str]` must be registered in main.py. | `check_event_registration.py` |

---

## Read Order

**Note**: The canonical read order for Round Table panelists is maintained in `SovereignAI_Round_Table_Prompt_v1.0.md` §7 to avoid drift between two copies of the same list. The summaries below point to that source of truth and add context for non-panelist roles.

### For a Round Table panelist
**See `SovereignAI_Round_Table_Prompt_v1.0.md` §7 for the canonical 5-step read order.** Summary: Brief → Prompt → Consolidated doc (all 25 documents inline) → individual design docs for deep dives → principles.md (Document 8) + AGENTS.md (Document 2) for principle/rule lookup. All governance content is already inside the consolidated file — do NOT look for AGENTS.md, LANDMINES.md, DECISIONS.md, DEBT.md, PLANS.md, or CHANGELOG.md as separate uploads.

### For a new Architect (start of session, ongoing work — not this review round)
1. `AI_HANDOFF.md` (Document 1 in consolidated, or repo root) — process guide
2. `principles.md` (Document 8, or `documents/`) — 14 principles
3. `PLANS.md` (Document 6, or repo root) — current state, baselines
4. `LANDMINES.md` (Document 3, or repo root) — failure patterns
5. `DECISIONS.md` (Document 4, or repo root) — architectural decisions
6. `DEBT.md` (Document 5, or repo root) — deferred items
7. This index — navigation
8. Design docs (Category C, Documents 14–24) as needed for the current batch

For ongoing work (not this review), these are read from the repo directly — the consolidated file is a review-round artifact, not the working state.

### For an Executor (S0.2 of a plan)
1. `AGENTS.md` (Document 2 in consolidated, or repo root) — all rules (consult `LANDMINES.md` / Document 3 if ambiguous)
2. The specific plan file
3. The design doc(s) the plan implements (Category C, Documents 14–24)

---

## Document Lifecycle

1. **Draft**: Author writes document, marks "Draft — prepared for Round Table review"
2. **Round Table**: Panelists review, Architect applies findings (GR4)
3. **Ratified**: On clean pass, DDs migrate to `DECISIONS.md` as Accepted
4. **Implemented**: Plans derived from ratified DDs are executed
5. **Historical**: After implementation, design docs become reference (not updated unless superseded)

**Supersede don't delete** (GR7): When a DD is superseded, it moves to a "Superseded" subsection with a pointer to the replacement. Never deleted.

---

*End of index.*
