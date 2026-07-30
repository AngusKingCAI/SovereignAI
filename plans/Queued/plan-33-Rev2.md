Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Lifecycle Manager

S1.1: Create `app/sovereignai/lifecycle/manager.py` — `AgentLifecycleManager`
S1.2: States: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`
S1.3: Startup sequence: EventBus → OptionsBackend → ModelRegistry → Orchestrator → Web Server → TUI (as separate OS processes per P8/AR12)
S1.4: Process spawning: AgentLifecycleManager spawns and monitors Web Server and TUI as subprocesses, not in-process objects
S1.5: Each stage has 30s timeout; failure emits `lifecycle.stage.failed` and defined failure semantics per stage
S1.6: Failure semantics: per-stage policy (retry-once for critical, continue-without for non-critical, abort-startup for core dependencies)
S1.7: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v`

## S2 — Health Check Aggregation

S2.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S2.2: Polls all registered components concurrently via `asyncio.gather`: EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter
S2.3: Per-check timeout: 2s timeout per component health check to prevent stalling
S2.4: Total latency budget: 5s maximum for `/api/v1/health` response aggregation
S2.5: Adapter health per AR15: `health_check()` returns `HEALTHY | DEGRADED | UNHEALTHY`
S2.6: Aggregate: all HEALTHY = system HEALTHY; any DEGRADED = system DEGRADED; any UNHEALTHY = system UNHEALTHY
S2.7: Expose via GET `/api/v1/health` (Plan 31 consumes via HealthAggregator facade, not direct dependencies)
S2.8: Health check response schema: Pydantic DTO shared with Plan 31 to ensure contract consistency
S2.9: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v`

## S3 — Graceful Shutdown

S3.1: SIGTERM/SIGINT handler: use `asyncio.get_running_loop().add_signal_handler()` for asyncio compatibility
S3.2: Set state SHUTTING_DOWN, stop accepting new requests, emit `lifecycle.shutdown.initiated`
S3.3: Drain in-flight: wait for active orchestrator sessions to complete (60s timeout)
S3.4: TUI drain: emit `lifecycle.tui.draining` event before closing TUI so SSE clients receive final event
S3.5: Shutdown sequence with per-stage timeouts (15s each): TUI → Web Server → Orchestrator → ModelRegistry → OptionsBackend → EventBus
S3.6: EventBus subscriber drain: explicit "drain subscribers" step before closing EventBus with configurable timeout
S3.7: Resource cleanup: explicit SQLite database close calls (messaging_audit.db, graph_memory.db) before SIGKILL
S3.8: Force kill: after 120s total, emit `lifecycle.shutdown.forced` and exit
S3.9: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v`

## S4 — DI Composition

S4.1: Create `app/sovereignai/main.py` — compose all core services via DIContainer
S4.2: No hardcoded names per AR4; all resolved from capability graph or DI registry
S4.3: ≤15 constructor args per P11; split into sub-composers if exceeded
S4.4: DI composition ownership: core service wiring owned by this plan; web layer composition owned by Plan 31
S4.5: Lifecycle manager interface: publish state-transition contract usable by API and TUI-facing status path
S4.6: Test: `pytest app/sovereignai/tests/test_main_composition.py -v`

## S5 — Circuit Breaker Integration

S5.1: Worker circuit breaker per AR7: >50 errors in 10s = unload, no auto-restart
S5.2: Orchestrator circuit breaker: CLOSED → OPEN → HALF-OPEN transitions with recovery testing
S5.3: Orchestrator HALF-OPEN: allow N probe requests after timeout to test recovery before fully closing circuit
S5.4: Adapter circuit breaker: CLOSED → OPEN → HALF-OPEN transitions; 3 failed `health_check()` → UNHEALTHY
S5.5: Adapter HALF-OPEN: allow probe health checks after timeout to detect recovery before marking HEALTHY
S5.6: All circuit events logged via TraceEmitter per AR8
S5.7: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v`

## S6 — AR Checks

S6.1: Add `check_lifecycle_no_globals.py` — verify no global state in lifecycle modules
S6.2: Add `check_lifecycle_health_check_coverage.py` — verify all adapters declare health_check
S6.3: Add `check_circuit_breaker_half_open.py` — verify circuit breakers implement HALF-OPEN state
S6.4: Add `check_async_signal_handler.py` — verify signal handling uses loop.add_signal_handler
S6.5: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
