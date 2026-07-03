# SovereignAI -- Design Document Index

**Date**: 2026-07-03  
**Status**: Living index -- updated as new documents are ratified

---

## Document Registry

| # | Document | DDs Covered | Status | Depends On |
|---|----------|-------------|--------|------------|
| 1 | `SovereignAI_Skill_Agent_System_Design_v1.0.md` | DD-1 through DD-12 | Approved | ../PRINCIPLES.md, ../AGENTS.md, ../DECISIONS.md |
| 2 | `SovereignAI_Cross_Department_Messaging_Design_v1.0.md` | DD-20.10.4 through DD-20.10.11 | Approved | Doc #1 |
| 3 | `SovereignAI_LLM_Function_Calling_Design_v1.0.md` | DD-21.3.1 | Approved | Doc #1 |
| 4 | `SovereignAI_Diff_Based_Editing_Design_v1.0.md` | DD-21.9.1 | Approved | Doc #1 |
| 5 | `SovereignAI_Worker_Spawning_Design_v1.0.md` | DD-21.0.1 | Approved | Doc #1 |
| 6 | `SovereignAI_Codebase_Indexing_Design_v1.0.md` | DD-21.10.1 | Approved | Doc #1 |
| 7 | `SovereignAI_Hardware_SSE_Streaming_Design_v1.0.md` | DD-21.5.1 | Approved | Doc #1, Doc #2 |

---

## Decision Cross-Reference

| DD-ID | Topic | Document | Section |
|-------|-------|----------|---------|
| DD-1 | Hybrid manifest (manifest + code) | Doc #1 | Section 2 |
| DD-2 | Pydantic schemas with auto-generated summary | Doc #1 | Section 2 |
| DD-3 | In-process execution default | Doc #1 | Section 2 |
| DD-4 | Hybrid tool parser (JSON primary, XML fallback) | Doc #1 | Section 2 |
| DD-5 | Session-scoped state | Doc #1 | Section 2 |
| DD-6 | Structured error handling | Doc #1 | Section 2 |
| DD-7 | ReAct as meta-skill | Doc #1 | Section 2 |
| DD-8 | Manifest format locked | Doc #1 | Section 2 |
| DD-9 | Initial skills | Doc #1 | Section 2 |
| DD-10 | Hybrid registration | Doc #1 | Section 2 |
| DD-11 | Structured prompts at Worker level | Doc #1 | Section 2 |
| DD-12 | Token-budget history | Doc #1 | Section 2 |
| DD-20.10.1 | Bounded trace queue | Doc #2 | Section 6.2 |
| DD-20.10.2 | Circuit breaker | Doc #2 | Section 6.2 |
| DD-20.10.3 | Async delivery | Doc #2 | Section 6.1 |
| DD-20.10.4 | Event schema base | Doc #2 | Section 2 |
| DD-20.10.5 | Event type registry | Doc #2 | Section 4 |
| DD-20.10.6 | Consumer registration | Doc #2 | Section 4 |
| DD-20.10.7 | Delivery (fan-out, FIFO, priority, breaker) | Doc #2 | Section 6 |
| DD-20.10.8 | Persistence (all events) | Doc #2 | Section 7 |
| DD-20.10.9 | Versioning (C+B) | Doc #2 | Section 5 |
| DD-20.10.10 | Integration (extend EventBus) | Doc #2 | Section 8 |
| DD-20.10.11 | Plan scope (two plans) | Doc #2 | Section 2 |
| DD-21.0.1 | Worker spawning (thread pool) | Doc #5 | Section 2 |
| DD-21.3.1 | Tool call generation (single-call + retry) | Doc #3 | Section 2 |
| DD-21.5.1 | Hardware SSE streaming | Doc #7 | Section 2 |
| DD-21.9.1 | Diff-based editing (search/replace + hint) | Doc #4 | Section 2 |
| DD-21.10.1 | Codebase indexing (symbol map) | Doc #6 | Section 2 |

---

## Implementation Plan Queue

| Plan | Scope | Depends On | DDs Applied | Document |
|------|-------|------------|-------------|----------|
| 20.10.1 | Typed Event Foundation | None | DD-20.10.4/5/6/9/10 | Doc #2 |
| 20.10.2 | Delivery Hardening + Persistence | 20.10.1 | DD-20.10.7/8 | Doc #2 |
| 20.10.3 | Trace Queue Hardening | None | DD-20.10.1/2/3 | Doc #2 |
| 21.0 | Worker Spawning | None | DD-21.0.1 | Doc #5 |
| 21.1 | Skill framework core | None | DD-1/2/3/8/10 | Doc #1 |
| 21.2 | Initial skills | 21.1 | DD-9 | Doc #1 |
| 21.3 | ReAct meta-skill | 21.1, 21.2 | DD-21.3.1, DD-4/5/6/7/11/12 | Doc #1, Doc #3 |
| 21.4 | Web skills | 21.1 | DD-9 | Doc #1 |
| 21.5 | UI integration | 21.1 | DD-10 | Doc #1 |
| 21.5.1 | Hardware SSE streaming | None | DD-21.5.1 | Doc #7 |
| 21.6 | MCP server integration | 21.1, 21.5 | DD-3 | Doc #1 |
| 21.7 | Shell execution + sandbox | 21.6 | DD-3 | Doc #1 |
| 21.8 | Git operations skill | 21.7 | DD-3 | Doc #1 |
| 21.9 | Diff-based editing | 21.8 | DD-21.9.1 | Doc #4 |
| 21.10 | Codebase indexing | None | DD-21.10.1 | Doc #6 |

---

## Open Questions (All Documents)

| ID | Question | Status | Raised In |
|----|----------|--------|-----------|
| Q-20.10.5 | Can old frozen classes ever be removed? | Deferred | Doc #2 |
| Q-20.10.6 | Event replay time-travel support? | Deferred | Doc #2 |
| Q-20.10.7 | Encryption-at-rest for sensitive payloads? | Deferred | Doc #2 |
| Q-21.0.1 | Priority queues for WorkerPool? | Deferred | Doc #5 |
| Q-21.0.2 | Pre-warmed workers? | Deferred | Doc #5 |
| Q-21.0.3 | WorkerPool metrics exposure? | Deferred | Doc #5 |
| Q-21.3.1 | Parallel tool calls support? | Deferred | Doc #3 |
| Q-21.3.2 | Streaming generation partial JSON parse? | Deferred | Doc #3 |
| Q-21.3.3 | Security Guard audit every tool call? | Deferred | Doc #3 |
| Q-21.5.1 | Hardware telemetry to episodic memory? | Deferred | Doc #7 |
| Q-21.5.2 | Thermal data in HardwareSnapshot? | Deferred | Doc #7 |
| Q-21.5.3 | Web endpoint filtering (CPU/GPU only)? | Deferred | Doc #7 |
| Q-21.9.1 | Multi-file edits in single response? | Deferred | Doc #4 |
| Q-21.9.2 | Hunk-based git diffs support? | Deferred | Doc #4 |
| Q-21.9.3 | AST-aware structural editing? | Deferred to v2+ | Doc #4 |
| Q-21.10.1 | Incremental updates vs full rebuild? | Deferred | Doc #6 |
| Q-21.10.2 | When to add semantic embeddings? | Deferred to v2+ | Doc #6 |
| Q-21.10.3 | Include docstrings/comments in index? | Deferred | Doc #6 |

---

## Gap Status

| Gap # | Topic | Status | Document |
|-------|-------|--------|----------|
| #2 | Tool Layer | Partially designed | Doc #1 |
| #3 | ReAct Agent Loop | Designed | Doc #1 |
| #4 | LLM Function Calling | Designed | Doc #3 |
| #5 | Context/Repo Indexing | Designed | Doc #6 |
| #6 | Diff-Based Editing | Designed | Doc #4 |
| #7 | Department Managers | Not yet designed | -- |
| #8 | Cross-Department Messaging | Designed | Doc #2 |
| #9 | Worker Spawning | Designed | Doc #5 |
| #10 | Codebase Index | Designed | Doc #6 |
| #11 | Security Guard | Deferred per P10 | -- |
| #12 | Graph Memory Backend | Not yet designed | -- |
| #13 | Models Panel Drill-Down | Not yet designed | -- |
| #14 | Hardware Panel SSE | Designed | Doc #7 |
| #15 | Options Panel Persistence | Not yet designed | -- |

---

*End of index.*
