# Batch Brief - Batch 7

**Date**: 2026-07-30  
**Review Type**: Internal Round Table  
**Plans in Batch**: Plan 31.Rev2, Plan 32.Rev2, Plan 33.Rev2, Plan 34.Rev2  
**Previous Iterations**: Rev1 (internal round table completed, external round table failed)  
**Batch Revision**: Rev2

---

## Plan Overviews

### Plan 31.Rev2
**Plan File**: Plans/Queued/plan-31-Rev2.md  
**Goal**: Design Web API layer with DTOs, orchestrator/messaging endpoints, auth, SSE, and DI composition  
**Context Summary**: Web API provides HTTP interface for UI processes to consume core capabilities per P8 (UIs are separate processes). This plan creates the API boundary layer that enables TUI and future UIs to interact with the system.  
**Changes Planned**: Web DTOs (Pydantic), orchestrator endpoints (message/status/SSE), messaging endpoints (send/audit/circuits), options/model registry endpoints, session cookie auth with security attributes, CORS restrictions, DI composition in main.py, AR compliance checks  
**Rev2 Changes**: Added API versioning (/api/v1/), cookie security attributes (HttpOnly, Secure, SameSite), SSE security headers, error response DTOs, HealthAggregator facade pattern, clarified DI composition ownership vs Plan 33

### Plan 32.Rev2
**Plan File**: Plans/Queued/plan-32-Rev2.md  
**Goal**: Design TUI web client integration with Web API for all 10 sidebar sections  
**Context Summary**: TUI process connects to Web API per P8 separate processes architecture. This plan wires all TUI panels to consume API endpoints instead of direct core imports, maintaining process separation.  
**Changes Planned**: TUI web client (httpx wrapper), session cookie management with encryption, sidebar panel wiring for all 10 sections (orchestrator, workers, tasks, memory, models, adapters, hardware, logs, options), main screen integration with auto-refresh, cookie auth resolution for DEBT-7, AR compliance checks  
**Rev2 Changes**: Added cookie encryption at rest, cookie validation, SSE reconnection strategy, 401 error handling, DEBT-7 resolution criteria, client abstraction boundary, error handling granularity, offline/degraded mode behavior

### Plan 33.Rev2
**Plan File**: Plans/Queued/plan-33-Rev2.md  
**Goal**: Design agent lifecycle management with health aggregation, graceful shutdown, and circuit breaker integration  
**Context Summary**: System needs robust startup/shutdown sequences, health monitoring, and graceful degradation per P13 (Strong and robust). This plan creates the lifecycle orchestration that manages all core services.  
**Changes Planned**: AgentLifecycleManager with state machine and startup sequence, HealthAggregator for component health polling, graceful shutdown with SIGTERM/SIGINT handling, DI composition in main.py, circuit breaker integration for workers/orchestrator/adapters, AR compliance checks  
**Rev2 Changes**: Added async-correct signal handling (loop.add_signal_handler), HALF-OPEN circuit breaker state, HealthAggregator concurrency model with timeouts, per-stage shutdown timeouts, process spawning clarity (subprocess vs in-process), failure semantics per stage, resource cleanup for SQLite

### Plan 34.Rev2
**Plan File**: Plans/Queued/plan-34-Rev2.md  
**Goal**: Design Librarian event handling, episodic event consumer, and cross-task persistent graph memory  
**Context Summary**: System needs event-driven memory updates and persistent knowledge graph across tasks per P9 (Observability). This plan implements event-driven memory management and persistent knowledge storage.  
**Changes Planned**: Librarian event handler for task lifecycle events, episodic event consumer for orchestrator/messaging events, PersistentGraphMemory with SQLite backing, integration with Librarian and EventBus, API exposure for graph/episodic queries, AR compliance checks  
**Rev2 Changes**: Added consumer idempotency patterns, dead-letter queue for failed events, structured event format (wide events), event sampling strategy, SQLite WAL mode, conflict resolution using ON CONFLICT/UPSERT, indexing strategy, schema registry for event evolution

---

## Cross-Plan Dependencies

**Dependency Analysis**: 
- Plan 31 (Web API) is foundational for Plan 32 (TUI) - TUI depends on API endpoints
- Plan 33 (Lifecycle) orchestrates startup/shutdown of Plan 31 (Web API) and Plan 32 (TUI)
- Plan 34 (Memory Events) integrates with Plan 22 (EventBus) and Plan 24 (Graph Memory) dependencies
- Plan 33 references Plan 31's `/api/health` endpoint for health aggregation
- Plan 34 references Plan 33's lifecycle for persistent graph load/flush

**Sequencing Risks**: 
- Plan 31 must complete before Plan 32 can be implemented (API dependency)
- Plan 33 should be implemented before Plan 34 to ensure lifecycle management is in place
- Plan 34's persistent graph integration depends on Plan 24 (Graph Memory) being available

**Integration Points**: 
- Web API endpoints (Plan 31) consumed by TUI (Plan 32)
- Health aggregation (Plan 33) monitors Web API (Plan 31) and TUI (Plan 32)
- Lifecycle manager (Plan 33) orchestrates startup order of all components
- EventBus (Plan 22 dependency) used by Plan 34 for event handling
- Graph Memory (Plan 24 dependency) used by Plan 34 for persistent storage

**Shared Resources**: 
- EventBus (Plan 22) for event distribution
- Graph Memory backend (Plan 24) for knowledge storage
- DIContainer for service composition across all plans
- TraceEmitter for logging across all plans
- SQLite databases: messaging_audit.db (Plan 31), graph_memory.db (Plan 34)

---

## Author's Confidence by Plan

**Plan 31.Rev2**: High - Plan follows established API patterns with added security attributes and versioning. DEBT-7 resolution criteria clarified. HealthAggregator facade addresses architectural concerns.

**Plan 32.Rev2**: High - TUI integration with added encryption, validation, and reconnection strategy. DEBT-7 resolution criteria provide clear path forward. Client abstraction boundary well-defined.

**Plan 33.Rev2**: High - Lifecycle management with async-correct signal handling, HALF-OPEN circuit state, and process spawning clarity. Addresses all HIGH severity issues from previous review.

**Plan 34.Rev2**: High - Event-driven architecture with idempotency, dead-letter queue, and wide events format. SQLite WAL mode and ON CONFLICT conflict resolution address data integrity concerns.

---

## Named Open Questions by Plan

**Plan 31.Rev2**: None - DD-31.1, DD-31.2, DD-31.3 marked as resolved. Previous security concerns addressed with Rev2 changes.

**Plan 32.Rev2**: DEBT-7 (Cookie Auth Resolution) - Resolution criteria clarified in Rev2. Will test with textual library and document limitation if needed.

**Plan 33.Rev2**: None - DD-33.1, DD-33.2, DD-33.3 marked as resolved. Previous architectural concerns addressed with Rev2 changes.

**Plan 34.Rev2**: None - DD-34.1, DD-34.2, DD-34.3, DD-34.4 marked as resolved. Previous data architecture concerns addressed with Rev2 changes.

---

## Vision Principle Compliance by Plan

**Plan 31.Rev2**: 
- CA-8 (UI Process Separation): ✅ Web API is separate process from core, UIs consume via API
- CA-9 (Observability): ✅ SSE endpoints emit events, all operations logged via TraceEmitter
- CA-10 (Dependency Injection): ✅ Web layer composes via DIContainer, core services via Plan 33
- CA-11 (Strong and Robust): ✅ Graceful degradation, circuit breakers for resilience
- CA-4 (Local-First): ✅ API runs locally, no cloud dependencies

**Plan 32.Rev2**: 
- CA-8 (UI Process Separation): ✅ TUI is separate process, consumes Web API via httpx
- CA-10 (Dependency Injection): ✅ TUIWebClient composed via DI, no hardcoded names
- CA-11 (Strong and Robust): ✅ Degraded badge on API failures, error handling
- CA-4 (Local-First): ✅ TUI connects to local API, no cloud dependencies

**Plan 33.Rev2**: 
- CA-1 (Core is Sacred): ✅ Lifecycle is pluggable component, not core module
- CA-3 (No Provider Lock-in): ✅ Works with any adapter/model, no provider-specific logic
- CA-7 (Modular Over Simple): ✅ Components fail independently, graceful degradation
- CA-10 (Dependency Injection): ✅ Core services compose via DIContainer, ≤15 constructor args
- CA-11 (Strong and Robust): ✅ Fault isolation, automatic recovery, graceful shutdown

**Plan 34.Rev2**: 
- CA-1 (Core is Sacred): ✅ Memory components are pluggable, not core modules
- CA-2 (Everything Pluggable): ✅ Librarian queries memory backends via interfaces
- CA-9 (Observability): ✅ All events logged via TraceEmitter, merge conflicts logged
- CA-10 (Dependency Injection): ✅ Components composed via DI, no global state
- CA-11 (Strong and Robust): ✅ File-backed persistence, conflict resolution, graceful degradation

---

## Review Focus Areas

**Quality Dimensions to Evaluate**:
- Accuracy: Are the technical claims accurate and feasible?
- Completeness: Are all necessary elements included for your domain?
- Clarity: Is the plan clear and unambiguous for your domain?
- Structure: Is the plan well-organized and executable?
- Context: Is sufficient background provided for your domain?

**Domain-Specific Focus**:
- **Security Expert**: Security vulnerabilities, compliance gaps, threat coverage, encryption strategies (cookie auth in Plan 32, CORS in Plan 31, SSE security)
- **Infrastructure Expert**: Scalability, reliability, operational readiness, cost efficiency (lifecycle management in Plan 33, health aggregation, graceful shutdown)
- **Data Architecture Expert**: Data integrity, storage patterns, data flows, governance compliance (persistent graph in Plan 34, event-driven memory, SQLite databases)
- **Application Architecture Expert**: Component boundaries, dependency health, pattern appropriateness, integration design (API design in Plan 31, TUI integration in Plan 32, lifecycle composition in Plan 33)
- **Operations/DevOps Expert**: Deployment safety, monitoring coverage, operational readiness, supportability (health checks in Plan 33, observability in Plan 34, circuit breakers)
- **Business Alignment Expert**: Business value alignment, cost-effectiveness, time-to-market considerations, user impact (UI process separation, system reliability, data persistence)

---

## Quality Rubric Reference

**Scoring**: Use Workflow/Workflow_Reference/Quality_Assessment_Framework.md for dimension-specific evaluation (1-5 scale)  
**Thresholds**: 
- 5 (Excellent): Clean pass
- 4 (Good): Clean pass  
- 3 (Fair): Proceed with rationale
- 2 (Poor): Requires revisions
- 1 (Critical): Block review

---

## Panelist Assignment

**Your Persona**: {Security Expert | Infrastructure Expert | Data Architecture Expert | Application Architecture Expert | Operations/DevOps Expert | Business Alignment Expert}

**Your Focus**: {Specific domain expertise based on persona}

**Plan Assignment**: 
- **Security Expert**: Review Plan 31 (Web API auth/CORS), Plan 32 (cookie auth for SSE)
- **Infrastructure Expert**: Review Plan 33 (lifecycle management, health aggregation, graceful shutdown)
- **Data Architecture Expert**: Review Plan 34 (persistent graph, event-driven memory, SQLite databases)
- **Application Architecture Expert**: Review Plan 31 (API design, DTOs), Plan 32 (TUI integration), Plan 33 (DI composition)
- **Operations/DevOps Expert**: Review Plan 33 (health checks, circuit breakers), Plan 34 (observability, event logging)
- **Business Alignment Expert**: Review Plan 31 (API value), Plan 32 (TUI user experience), Plan 33 (system reliability)

**CRITICAL**: At the start of your review response, you MUST explicitly state:
- For Internal Round Table: "I am reviewing as {Persona}"

This ensures proper logging to the consolidated file:
- Internal: Logs/Planner/Round Table/Internal/Batch7_31-34_Roundtable.md (append per revision, separated by {Agent_Persona})

**Web Search Requirement**: MUST use web search to verify findings against current best practices and research

---

## Iteration Context

**Previous Findings**: Internal round table identified HIGH severity issues (cookie security attributes, SSE headers, circuit breaker HALF-OPEN state) and MEDIUM issues (operational maturity gaps). External round table failed due to inconsistent panelist adherence, but detailed reviews provided additional architectural concerns (DI composition ownership, process boundary clarity, contract-first API design).

**Changes Made**: 
- Plan 31: Added API versioning, cookie security attributes, SSE security headers, error response DTOs, HealthAggregator facade, clarified DI composition ownership
- Plan 32: Added cookie encryption, validation, SSE reconnection, 401 error handling, DEBT-7 resolution criteria, client abstraction
- Plan 33: Added async signal handling, HALF-OPEN circuit state, HealthAggregator concurrency, per-stage timeouts, process spawning clarity, failure semantics, SQLite cleanup
- Plan 34: Added consumer idempotency, dead-letter queue, wide events format, event sampling, SQLite WAL mode, ON CONFLICT conflict resolution, indexing, schema registry

**Convergence Status**: Second iteration - addressing internal/external findings for convergence

---

## Output Format

Provide structured review in JSON format for your assigned plan(s):
```json
{
  "verdict": "PASS|FAIL",
  "dimensions": {
    "accuracy": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "completeness": {"score": 1-5, "notes": "...", "web_sources": []},
    "clarity": {"score": 1-5, "notes": "...", "web_sources": ["https://..."]},
    "structure": {"score": 1-5, "notes": "...", "web_sources": []},
    "context": {"score": 1-5, "notes": "...", "web_sources": []}
  },
  "overall_score": 1-5,
  "issues": [
    {"severity": "CRITICAL|HIGH|MEDIUM|LOW", "dimension": "...", "description": "...", "web_sources": ["https://..."]}
  ],
  "notes": "Overall assessment with rationale"
}
```

---

## Review Guidelines

1. **Use Web Search**: Verify your findings against current best practices and research
2. **Stay in Persona**: Focus on your assigned domain expertise
3. **Be Specific**: Provide concrete, actionable feedback
4. **Cite Sources**: Include web search URLs for verification
5. **Rate Honestly**: Use quality rubric objectively
6. **Consider Execution**: Plan is for manual implementation, ensure clarity
7. **Batch Context**: Consider cross-plan dependencies and integration points
8. **Assigned Plans Only**: Review only the plans assigned to your persona

---

## Review Timeline

**Start Time**: 2026-07-30  
**Expected Completion**: 2026-07-30  
**Panelist Deadline**: Immediate (internal round table)
