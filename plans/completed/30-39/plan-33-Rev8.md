Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3, DD-33.4, DD-33.5, DD-33.6, DD-33.7, DD-33.8, DD-33.9
**Revision**: Rev8

## Executor Manifest

**Plan**: 33
**Phases**: 7 (S0–S7)
**Deliverables**:
| Phase | Deliverable | Verification |
|-------|-------------|--------------|
| S1 | `app/sovereignai/lifecycle/manager.py` — `AgentLifecycleManager` | `pytest app/sovereignai/tests/test_lifecycle_manager.py -v` passes |
| S2 | `app/sovereignai/lifecycle/hooks.py` — `LifecycleHookRegistry` | `pytest app/sovereignai/tests/test_lifecycle_hooks.py -v` passes |
| S3 | `app/sovereignai/lifecycle/health.py` — `HealthAggregator` + `/api/health` + `/api/lifecycle/ready` | `pytest app/sovereignai/tests/test_lifecycle_health.py -v` passes |
| S4 | Graceful shutdown with SIGTERM/SIGINT + sentinel | `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v` passes |
| S5 | `app/sovereignai/main.py` — DI composition | `pytest app/sovereignai/tests/test_main_composition.py -v` passes |
| S6 | Circuit breaker integration | `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v` passes |
| S7 | AR check scripts + document hygiene | `pytest .agent/executor/tests/test_document_hygiene.py -v` passes |

**Coverage target**: ≥90%
**Forbidden actions**: Do not modify `AI_HANDOFF.md`, `AGENTS.md`, `PRINCIPLES.md`, `OR_RULES.md`, `PLANS.md`, `DEBT.md`.
**Commit message**: `feat(lifecycle): add agent lifecycle manager with health checks, graceful shutdown, and circuit breakers`

## S0 — Opening

S0.1: Run `/open`
S0.2: Read `AGENTS.md` in full. Read plan header AR rules from `.agent/executor/ARCHITECTURE.md`. Read plan header OR rules from `.agent/executor/OR_RULES.md`.
S0.3: Check `.agent/shared/DEBT.md` for deferred items.

## S1 — Lifecycle Manager

S1.1: Create `app/sovereignai/lifecycle/manager.py` — `AgentLifecycleManager`
S1.2: Lifecycle states: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`. Recovery: `DEGRADED → READY` (3 consecutive HEALTHY polls). Health status `UNHEALTHY` maps to lifecycle `DEGRADED`; health `HEALTHY` after 3 consecutive → `READY`. Health transitions trigger lifecycle transitions. No separate UNHEALTHY lifecycle state.
S1.3: Startup sequence (in-process core): EventBus → OptionsBackend → Orchestrator → ModelRegistry → Route Registration Readiness Check; ModelRegistry receives an `OrchestratorFactory` (callable returning Orchestrator). Factory called only at first sync invocation, not during `__init__`. Add composition test proving no cycle at construction.
S1.4: EventBus is critical stage: failure aborts startup. All other stages: 30s timeout, failure emits `lifecycle.stage.failed` and continues (degraded start). **Rationale**: EventBus is critical because all observability, messaging, and SSE infrastructure depends on it. Degraded start without EventBus is not supported in v1.
S1.5: Stage failure fallback: for non-EventBus stage failures, if EventBus is unavailable at emit time, write to stderr + `platformdirs.user_data_dir("sovereignai") / "logs" / "lifecycle_fallback.log"` (rotating, 10MB × 5). On EventBus recovery, drain fallback log in order.
S1.6: TUI is NOT in startup sequence — separate process per AR12. TUI polls `/api/lifecycle/ready` before connecting
S1.7: **Route Registration Readiness Check**: monitors web process via `GET /api/lifecycle/ready`; does not start the web process (that's Plan 31 `app/web/main.py`). This is a readiness dependency check, not a process launch.
S1.8: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v`

## S2 — Lifecycle Hooks

S2.1: Create `app/sovereignai/lifecycle/hooks.py` — `LifecycleHookRegistry`; DI-injected (not global), owned by LifecycleComposer
S2.2: Phases: `REGISTRATION_OPEN → REGISTRATION_CLOSED → STARTUP_RUNNING → STARTUP_DONE → SHUTDOWN_RUNNING → SHUTDOWN_DONE`. Explicit gate: `LifecycleManager.start()` transitions `REGISTRATION_OPEN → CLOSED`. Registering after `CLOSED` raises `LifecycleError`.
S2.3: Hooks registered outside `REGISTRATION_OPEN` raise `LifecycleError`; duplicate registration raises. Each hook has `critical: bool` flag (default False). Critical hook failure: log + emit `lifecycle.hook.failed` + **mark stage as FAILED, continue remaining teardown stages within their timeouts, write sentinel before force-kill**. Non-critical hook failure: log + emit + continue. All hook failures also emit to stderr fallback and EventBus if available.
S2.4: Execution order: startup hooks run in registration order; shutdown hooks run in reverse registration order; each hook has its own timeout (configurable, default 15s).
S2.5: **v1 hook cap**: max 5 total shutdown hooks (critical + non-critical combined). Max 1 critical shutdown hook. Non-critical shutdown hooks run concurrently with shared 15s timeout (not sequential). Force-kill budget accounts for this.
S2.6: Plan 34 registers: startup hook = `MemoryGateway.load()` (critical=False — system starts without memory, routes return 503 until loaded), shutdown hook = `MemoryGateway.flush()` (critical=True — flush failure marks stage FAILED, continues remaining teardown).
S2.7: Test: `pytest app/sovereignai/tests/test_lifecycle_hooks.py -v`

## S3 — Health Check Aggregation + Lifecycle Ready Endpoint

S3.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S3.2: Background-cached polling: polls all registered components every 5s; cache TTL 5s; `/api/health` returns cached results <5s old. Response includes `health_cache_age_ms` field.
S3.3: Polls: EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter; includes `health_cache_age_ms`
S3.4: Adapter health per AR15: `health_check()` returns `HEALTHY | DEGRADED | UNHEALTHY`
S3.5: Aggregate: any UNHEALTHY = system UNHEALTHY → lifecycle DEGRADED; any DEGRADED (no UNHEALTHY) = system DEGRADED; all HEALTHY → lifecycle READY (if 3 consecutive)
S3.6: Register `GET /api/health` route with real backend; sole registrar (Plan 31 does not register this). Response includes subsystem health breakdown.
S3.7: Register `GET /api/lifecycle/ready` — returns `LifecycleReadyResponse` with `ready: bool`, `server_pid: int`, `instance_uuid: str`. TUI and Plan 32 sentinel use `server_pid` from this endpoint. `ready: true` only after all startup stages complete.
S3.8: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v`

## S4 — Graceful Shutdown

S4.1: SIGTERM/SIGINT handler: set state SHUTTING_DOWN
S4.2: Drain in-flight: active sessions = has in-flight message or pending clarification; **60s timeout, separate pre-stage**. During drain, server returns HTTP 503 with `Retry-After: 60` for all new requests. Existing in-flight requests continue processing. TCP connections remain open.
S4.3: Shutdown sequence (sequential, after drain completes): Orchestrator (20s) → ModelRegistry (20s) → OptionsBackend (20s) → EventBus (20s) → LifecycleHookRegistry (15s for all non-critical concurrent, plus 15s for critical hook). **Force-kill timeout: 190s** (60s drain + 4×20s stages + 15s hooks + 15s headroom). Per-stage timeout: 20s each. Hook timeout: 15s total (non-critical concurrent + critical sequential).
S4.4: TUI is NOT in shutdown sequence — monitors SSE `/api/lifecycle/stream` and file sentinel; exits client-side
S4.5: Before force-kill: write sentinel file at `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{os.getpid()}.sentinel"` with atomic protocol: `makedirs(path.parent, mode=0o700, exist_ok=True)`; `with open(path, 'w') as f: f.write(f"{timestamp}\n{instance_uuid}\n"); os.fsync(f.fileno())`. Emit `lifecycle.shutdown.forced` to EventBus if available; otherwise stderr fallback. On next startup, cleanup deletes `shutdown.*.sentinel` files for PIDs not running (`os.kill(pid, 0)`) AND matching instance_uuid. Documented v1 limitation: single instance per user.
S4.6: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v`

## S5 — DI Composition

S5.1: Create `app/sovereignai/main.py` — compose all core services via DIContainer
S5.2: No hardcoded names per AR4; all resolved from capability graph or DI registry
S5.3: Sub-composers with file paths:
  - `app/sovereignai/composers/core.py` — `CoreServicesComposer` (EventBus, OptionsBackend, ModelRegistry)
  - `app/sovereignai/composers/orchestrator.py` — `OrchestratorComposer` (Orchestrator, InterDepartmentBus)
  - `app/sovereignai/composers/adapters.py` — `AdapterComposer` (adapter registry)
  - `app/sovereignai/composers/lifecycle.py` — `LifecycleComposer` (LifecycleManager, HealthAggregator, HookRegistry)
  - `app/sovereignai/composers/memory.py` — `MemoryComposer` (MemoryGateway, PersistentGraphMemory)
  MemoryGateway is owned by MemoryComposer and is the **sole owner of PersistentGraphMemory**; both Orchestrator and Librarian receive MemoryGateway via DI. No direct PGM injection outside MemoryComposer. Verifying AR check: see Plan 34 S6.3.
S5.4: ≤15 constructor args per P11 per sub-composer and per manager/hook class; add AR check `test_max_constructor_args.py`
S5.5: Test: `pytest app/sovereignai/tests/test_main_composition.py -v`

## S6 — Circuit Breaker Integration

S6.1: Worker circuit breaker per AR7: >50 errors in 10s per worker (keyed by `worker_id`) = unload. Error = unhandled exception in message handler or adapter response.
S6.2: Orchestrator circuit breaker: >10 consecutive message failures in 60s window = state → DEGRADED. Consecutive = strictly no success between failures; single success resets counter to zero. Window is sliding 60s. Recovery: 60s cooldown, half-open probe, 3 consecutive HEALTHY polls → close breaker.
S6.3: Adapter circuit breaker: `health_check()` fails 3x = mark UNHEALTHY; recovery: 60s cooldown, half-open probe, 3 consecutive HEALTHY polls → close breaker
S6.4: All circuit events logged via TraceEmitter per AR8; TraceEmitter has stderr fallback if EventBus unavailable
S6.5: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v`

## S7 — AR Checks

S7.1: Add `check_lifecycle_no_globals.py` — verify no global state in lifecycle modules
S7.2: Add `check_lifecycle_health_check_coverage.py` — verify all adapters declare health_check
S7.3: Add `check_max_constructor_args.py` — verify each sub-composer and manager/hook class `__init__` parameter count ≤15
S7.4: Add `check_lifecycle_phase_gate.py` — verify no hook registration after `LifecycleManager.start()`
S7.5: Add `check_sentinel_cleanup.py` — verify startup deletes stale sentinel files for non-running PIDs with matching instance_uuid
S7.6: Add `check_max_shutdown_hooks.py` — verify max 5 total shutdown hooks, max 1 critical
S7.7: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`