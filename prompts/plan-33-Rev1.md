Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3
**Revision**: Rev1

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Lifecycle Manager

S1.1: Create `app/sovereignai/lifecycle/manager.py` — `AgentLifecycleManager`
S1.2: States: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`
S1.3: Startup sequence: EventBus → OptionsBackend → ModelRegistry → Orchestrator → Web Server → TUI
S1.4: Each stage has 30s timeout; failure emits `lifecycle.stage.failed` and continues to next stage (degraded start)
S1.5: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v`

## S2 — Health Check Aggregation

S2.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S2.2: Polls all registered components: EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter
S2.3: Adapter health per AR15: `health_check()` returns `HEALTHY | DEGRADED | UNHEALTHY`
S2.4: Aggregate: all HEALTHY = system HEALTHY; any DEGRADED = system DEGRADED; any UNHEALTHY = system UNHEALTHY
S2.5: Expose via GET `/api/health` (already in Plan 31 S4.3; this plan implements the backend)
S2.6: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v`

## S3 — Graceful Shutdown

S3.1: SIGTERM/SIGINT handler: set state SHUTTING_DOWN, stop accepting new requests
S3.2: Drain in-flight: wait for active orchestrator sessions to complete (60s timeout)
S3.3: Shutdown sequence: TUI → Web Server → Orchestrator → ModelRegistry → OptionsBackend → EventBus
S3.4: Force kill: after 120s total, emit `lifecycle.shutdown.forced` and exit
S3.5: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v`

## S4 — DI Composition

S4.1: Create `app/sovereignai/main.py` — compose all core services via DIContainer
S4.2: No hardcoded names per AR4; all resolved from capability graph or DI registry
S4.3: ≤15 constructor args per P11; split into sub-composers if exceeded
S4.4: Test: `pytest app/sovereignai/tests/test_main_composition.py -v`

## S5 — Circuit Breaker Integration

S5.1: Worker circuit breaker per AR7: >50 errors in 10s = unload, no auto-restart
S5.2: Orchestrator circuit breaker: if >10 consecutive message failures, state → DEGRADED
S5.3: Adapter circuit breaker: if `health_check()` fails 3x, mark UNHEALTHY
S5.4: All circuit events logged via TraceEmitter per AR8
S5.5: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v`

## S6 — AR Checks

S6.1: Add `check_lifecycle_no_globals.py` — verify no global state in lifecycle modules
S6.2: Add `check_lifecycle_health_check_coverage.py` — verify all adapters declare health_check
S6.3: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
