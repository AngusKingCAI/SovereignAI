Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3, DD-33.4, DD-33.5, DD-33.6
**Revision**: Rev2

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full
S0.3: Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.4: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Lifecycle Manager

S1.1: Create `app/sovereignai/lifecycle/manager.py` — `AgentLifecycleManager`
S1.2: States: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`
S1.3: Startup sequence (in-process core only): EventBus → OptionsBackend → ModelRegistry → Orchestrator → Web Server
S1.4: EventBus is critical stage: failure aborts startup entirely (not degraded). All other stages: 30s timeout, failure emits `lifecycle.stage.failed` and continues (degraded start)
S1.5: `lifecycle.stage.failed` fallback: if EventBus down, write to stderr + rotating file (`logs/lifecycle_fallback.log`)
S1.6: TUI is NOT in startup sequence — it is a separate process per AR12. TUI polls `/api/lifecycle/ready` before connecting
S1.7: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v`

## S2 — Lifecycle Hooks

S2.1: Create `app/sovereignai/lifecycle/hooks.py` — `LifecycleHookRegistry`
S2.2: Components register startup hooks (called in registration order) and shutdown hooks (called in reverse registration order)
S2.3: Plan 34 registers: startup hook = `PersistentGraphMemory.load()`, shutdown hook = `PersistentGraphMemory.flush()`
S2.4: Test: `pytest app/sovereignai/tests/test_lifecycle_hooks.py -v`

## S3 — Health Check Aggregation

S3.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S3.2: Background-cached polling: polls all registered components every 5s in background task; `/api/health` returns cached results <1s old
S3.3: Polls: EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter
S3.4: Adapter health per AR15: `health_check()` returns `HEALTHY | DEGRADED | UNHEALTHY`
S3.5: Aggregate: any UNHEALTHY = system UNHEALTHY; any DEGRADED (and no UNHEALTHY) = system DEGRADED; all HEALTHY = system HEALTHY
S3.6: Register `GET /api/health` route with real backend; Plan 31 stub replaced
S3.7: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v`

## S4 — Graceful Shutdown

S4.1: SIGTERM/SIGINT handler: set state SHUTTING_DOWN, stop accepting new requests
S4.2: Drain in-flight: active sessions = has in-flight message or pending clarification; 60s timeout
S4.3: Shutdown sequence (in-process core only): Web Server → Orchestrator → ModelRegistry → OptionsBackend → EventBus; per-stage timeout 20s
S4.4: TUI is NOT in shutdown sequence — it monitors SSE `lifecycle.shutting_down` event and exits client-side
S4.5: Force kill: after 120s total, emit `lifecycle.shutdown.forced` and exit
S4.6: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v`

## S5 — DI Composition

S5.1: Create `app/sovereignai/main.py` — compose all core services via DIContainer
S5.2: No hardcoded names per AR4; all resolved from capability graph or DI registry
S5.3: Sub-composers: `CoreServicesComposer` (EventBus, OptionsBackend, ModelRegistry), `OrchestratorComposer` (Orchestrator, InterDepartmentBus), `AdapterComposer` (adapter registry), `LifecycleComposer` (LifecycleManager, HealthAggregator, HookRegistry)
S5.4: ≤15 constructor args per P11 per sub-composer; add AR check `test_max_constructor_args.py`
S5.5: Test: `pytest app/sovereignai/tests/test_main_composition.py -v`

## S6 — Circuit Breaker Integration

S6.1: Worker circuit breaker per AR7: >50 errors in 10s = unload; error = unhandled exception in message handler or adapter response
S6.2: Orchestrator circuit breaker: >10 consecutive message failures in 60s window = state → DEGRADED; reset on 1 success within window
S6.3: Adapter circuit breaker: `health_check()` fails 3x = mark UNHEALTHY; recovery: 60s cooldown, half-open probe, 3 consecutive HEALTHY polls → close breaker
S6.4: All circuit events logged via TraceEmitter per AR8; TraceEmitter has stderr fallback if EventBus unavailable
S6.5: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v`

## S7 — AR Checks

S7.1: Add `check_lifecycle_no_globals.py` — verify no global state in lifecycle modules
S7.2: Add `check_lifecycle_health_check_coverage.py` — verify all adapters declare health_check
S7.3: Add `check_max_constructor_args.py` — verify no constructor exceeds 15 args
S7.4: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
