Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3, DD-33.4, DD-33.5, DD-33.6, DD-33.7, DD-33.8, DD-33.9
**Revision**: Rev13

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
S1.2: Lifecycle states: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`. Recovery: DEGRADED → READY (3 consecutive HEALTHY). UNHEALTHY → DEGRADED; HEALTHY 3x → READY. No separate UNHEALTHY state.
S1.3: Startup sequence (in-process core): EventBus → OptionsBackend → Orchestrator → ModelRegistry → Route Registration Readiness Check. ModelRegistry receives `OrchestratorFactory` (callable returning Orchestrator). **Explicit contract**: ModelRegistry MUST NOT call factory during `__init__`; first sync is the only permitted invocation point. Composition test proves no cycle at construction. Startup stages execute after DI composition; MemoryGateway.load() runs as startup hook per S2.6 (within 15s timeout), after Route Readiness Check completes or times out.
S1.4: EventBus is critical: failure aborts startup. All other stages: 30s timeout, failure emits `lifecycle.stage.failed` and continues (degraded start). **Rationale**: EventBus critical — all observability, messaging, SSE depend on it. Degraded start without EventBus unsupported in v1.
S1.5: Stage failure fallback: if EventBus unavailable, write to stderr + `platformdirs.user_data_dir("sovereignai") / "logs" / "lifecycle_fallback.log"` (rotating 10MB × 5). On EventBus recovery: read fallback log tail, emit each entry as `lifecycle.stage.recovered`, truncate file.
S1.6: TUI NOT in startup — separate process per AR12. TUI polls `/api/lifecycle/ready` before connecting.
S1.7: **Route Registration Readiness Check**: polls `GET /api/lifecycle/ready` (Plan 31 mounts via Web bridge; Plan 33 supplies backend service). Does not start Web process. Web process is operator-started (separate per AR12); Plan 33 does not launch Web. Poll interval: 2s. **Behavior**: TCP refused/DNS failure (Web not deployed) = log once, skip, proceed (non-blocking). Connection success + `ready: false` = counts toward 30s timeout (Web alive but not ready). Connection success + `ready: true` = success. Log progress every 10s. On timeout: continue startup degraded.
S1.8: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v` — `test_startup_sequence_order`, `test_model_registry_factory_not_called_in_init`, `test_eventbus_failure_aborts_startup`, `test_readiness_false_counts_toward_timeout`, `test_readiness_timeout_degraded_start`

## S2 — Lifecycle Hooks

S2.1: Create `app/sovereignai/lifecycle/hooks.py` — `LifecycleHookRegistry`; DI-injected, owned by LifecycleComposer
S2.2: Phases: `REGISTRATION_OPEN → REGISTRATION_CLOSED → STARTUP_RUNNING → STARTUP_DONE → SHUTDOWN_RUNNING → SHUTDOWN_DONE`. Gate: `LifecycleManager.start()` transitions `REGISTRATION_OPEN → CLOSED`. Registering after `CLOSED` raises `LifecycleError`.
S2.3: Hook failure behavior: **Critical SHUTDOWN hook failure**: log + emit `lifecycle.hook.failed` + mark stage FAILED, continue remaining teardown stages within timeouts, write sentinel before force-kill. **Non-critical hook failure** (startup or shutdown): log + emit + continue next hook. **Critical STARTUP hook failure**: emit `lifecycle.hook.failed`; abort startup with `LifecycleError` raised out of `LifecycleManager.run_startup()`. Caller (S5.1 step 6) catches: degraded-start permitted only if all critical startup hooks passed. Non-critical startup hook failure: log + emit + continue. All hook failures emit to stderr fallback and EventBus if available.
S2.4: **Canonical hook timeout rules** (supersedes all other refs): per-startup hook 15s each (sequential); per-shutdown: non-critical concurrent 15s shared + critical sequential 15s = 30s total. **Implementation**: `asyncio.wait_for(coro, 15)`; `TimeoutError` caught and counted as hook failure per S2.3. Cross-ref: S4.3 force-kill budget accounts for 30s.
S2.5: **v1 hook cap**: max 5 total startup hooks (critical + non-critical combined). Max 5 total shutdown hooks (4 non-critical + 1 critical). AR check `check_max_shutdown_hooks.py` enforces both caps.
S2.6: Plan 34 registers: startup hook = `MemoryGateway.load()` (critical=False — system starts without memory, routes return 503 until loaded), shutdown hook = `MemoryGateway.flush()` (critical=True). **Load timeout**: if `load()` exceeds 15s hook timeout, log WARN, emit `lifecycle.memory_load_timeout`, continue with memory disabled. `MemoryGateway.is_ready() -> bool`: True after `load()` completes, False after `flush()` or if load not yet completed.
S2.7: Test: `pytest app/sovereignai/tests/test_lifecycle_hooks.py -v` — `test_critical_startup_hook_failure_aborts`, `test_non_critical_startup_hook_failure_continues`, `test_shutdown_hook_concurrent_timeout`, `test_max_5_startup_hooks_enforced`, `test_max_5_shutdown_hooks_enforced`

## S3 — Health Check + Lifecycle Ready

S3.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S3.2: Background-cached polling: all registered components every 5s; cache TTL 5s; `/api/health` returns cached <5s old. Includes `health_cache_age_ms`.
S3.3–S3.5: Polls EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter. Adapter health per AR15: `HEALTHY | DEGRADED | UNHEALTHY`. Aggregate: any UNHEALTHY = DEGRADED; any DEGRADED (no UNHEALTHY) = DEGRADED; all HEALTHY → READY (3 consecutive).
S3.6: Register `GET /api/health` — sole registrar (Plan 31 does not register this). **Response: `HealthSnapshot` DTO** per Plan 31 S1.2 canonical names. Subsystem health breakdown included.
S3.7: Register `GET /api/lifecycle/ready` — **unauthenticated** (operational monitoring endpoint). Returns `LifecycleReadyResponse` with `ready: bool`, `server_pid: int`, `instance_uuid: str`. All three fields populated at process start.
S3.7a: **`ready` field state machine**: `process_startup → ready=false` → `all_startup_stages_complete → ready=true` → `SIGTERM_or_SIGINT → ready=false` → `process_exits`. On critical startup failure: `ready` stays `false`, process exits non-zero. During graceful drain, `ready=false` is the first signal TUI/Web sees. **Security note**: `server_pid` exposed for operational monitoring; restrict to internal networks in production.
S3.8: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v` — `test_health_returns_health_snapshot_dto`, `test_ready_false_during_startup`, `test_ready_true_after_stages_complete`, `test_ready_false_on_sigterm`, `test_health_unhealthy_returns_503_envelope`

## S4 — Graceful Shutdown

S4.1: SIGTERM/SIGINT handler: set state SHUTTING_DOWN. **Immediately**: (a) set `ready = false` (S3.7a), (b) emit `lifecycle.shutting_down` via EventBus with `{timestamp, server_pid, instance_uuid, drain_timeout_seconds: 60}`. Hook failures do not prevent this emission. If EventBus unavailable: emit to stderr fallback: `'[LIFECYCLE] shutting_down pid={pid} uuid={uuid}'`.
S4.2: Drain in-flight: 60s timeout. **Drain-time route policy**: `/api/lifecycle/ready` returns `ready: false`; `/api/health` returns cached results; `/api/lifecycle/stream` SSE continues streaming `lifecycle.shutting_down`, new connections rejected 503; `POST /api/auth/logout` and `GET /api/trace/logs` exempt; all other routes return 503 with `Retry-After: 60`.
S4.3: Shutdown sequence (sequential, after drain): Orchestrator (20s) → ModelRegistry (20s) → OptionsBackend (20s) → [emit `lifecycle.stopped`, drain 2s] → EventBus (20s) → HookRegistry (30s). **Force-kill: 190s** = 60s drain + Orchestrator(20s) + ModelRegistry(20s) + OptionsBackend(20s) + EventBus(20s) + HookRegistry(30s) + 20s headroom. `lifecycle.stopped` emitted after core services drained, before EventBus shutdown; 2s post-stopped drain folded into headroom.
S4.4: TUI NOT in shutdown sequence — monitors SSE `/api/lifecycle/stream` and file sentinel; exits client-side.
S4.5: Before force-kill: write sentinel at `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{os.getpid()}.sentinel"` — atomic write, fsync. Sentinel body: `{datetime.now(timezone.utc).isoformat()}\n{instance_uuid}\n`. Format MUST match Plan 32 S4.4 (TUI parser contract). Emit `lifecycle.shutdown.forced` if EventBus available; stderr fallback otherwise. On next startup, cleanup deletes sentinels for PIDs not running. **Corrupted sentinel**: log ERROR, delete file.
S4.6: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v` — `test_sigterm_emits_shutting_down`, `test_sigterm_sets_ready_false`, `test_shutdown_sequence_emits_stopped`, `test_sentinel_cleanup_pid_dead_deletes`, `test_sentinel_cleanup_pid_alive_skips`, `test_sentinel_cleanup_stale_age_deletes`, `test_sentinel_cleanup_malformed_pid_deletes`, `test_drain_logout_exempt`, `test_drain_health_exempt`

## S5 — DI Composition

S5.1: Create `app/sovereignai/main.py` — compose all core services via DIContainer. **7-step instantiation order**: 1. `CoreServicesComposer` → EventBus, OptionsBackend; 2. `OrchestratorComposer` → Orchestrator, InterDepartmentBus; 3. `ModelRegistryComposer` → ModelRegistry (receives `OrchestratorFactory` callable); 4. `AdapterComposer` → adapter registry; 5. `LifecycleComposer` → LifecycleManager, HealthAggregator, HookRegistry; 6. `MemoryComposer` → MemoryGateway (nullable until loaded), PersistentGraphMemory; registers hooks: `MemoryGateway.load()` (non-critical startup), `MemoryGateway.flush()` (critical shutdown); 7. Runtime: `LifecycleManager.start()` triggers startup hooks (after DI composition completes). Orchestrator receives `Optional[MemoryGateway]` via DI. **`MemoryGatewayProvider`**: deferred dependency — memory API returns 503 until `MemoryGateway.load()` completes.
S5.2: No hardcoded names per AR4; all resolved from capability graph or DI registry.
S5.3: Sub-composers: `CoreServicesComposer`, `OrchestratorComposer`, `ModelRegistryComposer`, `AdapterComposer`, `LifecycleComposer`, `MemoryComposer`. MemoryGateway sole owner of PGM per Plan 34 S5.3.
S5.4: ≤15 constructor args per sub-composer/manager/hook class (P11). AR check `test_max_constructor_args.py`.
S5.5: Test: `pytest app/sovereignai/tests/test_main_composition.py -v` — `test_7_step_instantiation_order`, `test_memory_gateway_nullable_at_construction`, `test_memory_api_503_before_load`, `test_concurrent_first_memory_requests`

## S6 — Circuit Breaker Integration

S6.1: Worker circuit breaker per AR7: >50 errors in 10s per worker (`worker_id`) = unload. Error includes timeout (>30s without response). After unload: worker quarantined 60s; dispatch to that worker_id rejected with `worker_unavailable`; after cooldown, re-eligible for load.
S6.2: Orchestrator circuit breaker: 10 consecutive message failures within consecutive-failure-with-60s-gap-reset = DEGRADED. Any success resets the run. If >60s since last failure, run resets. **Success criterion**: `OrchestratorResponse` with `error is None`. Exception, validation error, clarification request, partial-success = all count as failure. Recovery: 60s cooldown, half-open probe, 3 consecutive HEALTHY polls → close.
S6.3: Adapter circuit breaker: `health_check()` fails 3x = UNHEALTHY; recovery: 60s cooldown, half-open probe, 3 consecutive HEALTHY polls → close.
S6.4: All circuit events logged via TraceEmitter per AR8; stderr fallback if EventBus unavailable.
S6.5: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v` — `test_9_failures_1_success_resets`, `test_10_consecutive_60s_trips`, `test_success_criterion_error_is_none`, `test_clarification_request_counts_as_failure`, `test_adapter_health_fail_3x_unhealthy`

## S7 — AR Checks

S7.1: Add `check_lifecycle_no_globals.py` — verify no global state in lifecycle modules
S7.2: Add `check_lifecycle_health_check_coverage.py` — verify all adapters declare health_check
S7.3: Add `check_max_constructor_args.py` — verify each sub-composer/manager/hook `__init__` ≤15 params
S7.4: Add `check_lifecycle_phase_gate.py` — verify no hook registration after `LifecycleManager.start()`
S7.5: Add `check_sentinel_cleanup.py` — verify startup deletes stale sentinels for non-running PIDs
S7.6: Add `check_max_shutdown_hooks.py` — verify max 5 shutdown hooks, max 5 startup hooks
S7.7: Add `check_force_kill_budget.py` — parse constants; assert budget sums correctly
S7.8: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`