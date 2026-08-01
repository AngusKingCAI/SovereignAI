Depends on: Plan 31 (Web API), Plan 32 (TUI), Plan 24 (Departments), Plan 22 (EventBus)
Vision principles: P1 (Core sacred), P3 (No provider lock-in), P7 (Modular), P11 (Quality), P13 (Strong and robust)
AR rules: AR1, AR4, AR6, AR7, AR8, AR15
OR rules: UOR-1, UOR-2
Open questions resolved: DD-33.1, DD-33.2, DD-33.3, DD-33.4, DD-33.5, DD-33.6, DD-33.7, DD-33.8, DD-33.9
**Revision**: Rev9

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
S1.2: Lifecycle states: `INITIALIZING → HEALTH_CHECKING → READY → DEGRADED → SHUTTING_DOWN → STOPPED`. Recovery: `DEGRADED → READY` (3 consecutive HEALTHY polls). `UNHEALTHY` maps to `DEGRADED` (no separate UNHEALTHY lifecycle state). `ready` field in response: `true` only in READY state; `false` in all other states.
S1.3: Startup sequence (in-process core only): EventBus → OptionsBackend → Orchestrator → ModelRegistry → Route Registration Readiness Check. **ModelRegistry receives `OrchestratorFactory: Callable[[], Orchestrator]`** — factory resolved from DI, called only at first sync invocation (not `__init__`). Signature: `def create_orchestrator() -> Orchestrator`. Registered in DI: `di_container.register(Callable[[],
Orchestrator], factory=lambda: di_container.resolve(Orchestrator))`. Composition test proves no cycle at construction.
S1.4: EventBus is critical stage: failure aborts startup. All other stages: 30s timeout, failure emits `lifecycle.stage.failed` and continues (degraded start). Rationale: all observability/messaging/SSE depends on EventBus; degraded without it not supported in v1.
S1.5: Fallback: if EventBus unavailable at emit time, write to stderr + `platformdirs.user_data_dir("sovereignai") / "logs" / "lifecycle_fallback.log"` (rotating 10MB × 5). On recovery, drain in order. Recovered events may duplicate — consumers must be idempotent.
S1.6: TUI/Web NOT in startup sequence — separate processes per AR12. TUI polls `/api/lifecycle/ready` (Plan 32 S4.4).
S1.7: **Route Registration Readiness Check**: polls Web process via `GET /api/lifecycle/ready` (unauthenticated, see S3.7). **Polling**: interval 2s, timeout 30s. On connection error: retry with backoff (base 1s, max 5s). On timeout: emit `lifecycle.web_not_ready`, continue startup (degraded — Web API unavailable). This is non-blocking; core functions without Web layer. **Note**: Web process is started separately; this check verifies it has registered its routes.
S1.8: Test: `pytest app/sovereignai/tests/test_lifecycle_manager.py -v`

## S2 — Lifecycle Hooks

S2.1: Create `app/sovereignai/lifecycle/hooks.py` — `LifecycleHookRegistry`; DI-injected (not global), owned by LifecycleComposer
S2.2: Phases: `REGISTRATION_OPEN → REGISTRATION_CLOSED → STARTUP_RUNNING → STARTUP_DONE → SHUTDOWN_RUNNING → SHUTDOWN_DONE`. `LifecycleManager.start()` transitions `REGISTRATION_OPEN → CLOSED`. Registering after CLOSED raises `LifecycleError`.
S2.3: Each hook has `critical: bool` (default False). **Critical hook failure**: log + emit `lifecycle.hook.failed` + mark stage FAILED, continue remaining teardown stages, write sentinel before force-kill. **Non-critical hook failure**: log + emit + continue. All failures also emit to stderr fallback.
S2.4: **Canonical hook timeout rules** (supersedes all other hook-timeout statements):
  - Startup hooks: run sequentially in registration order, per-hook 15s timeout.
  - Shutdown hooks: non-critical (max 4) run **concurrently** with shared 15s budget; critical (max 1) runs **sequentially after** non-critical batch with its own 15s timeout. **Total shutdown hook budget: 30s.**
S2.5: **v1 hook cap**: max 5 total shutdown hooks (max 4 non-critical + 1 critical). AR check enforces cap.
S2.6: Plan 34 registers: startup = `MemoryGateway.load()` (non-critical), shutdown = `MemoryGateway.flush()` (critical).
S2.7: Test: `pytest app/sovereignai/tests/test_lifecycle_hooks.py -v`

## S3 — Health Check Aggregation + Lifecycle Ready Endpoint

S3.1: Create `app/sovereignai/lifecycle/health.py` — `HealthAggregator`
S3.2: Polls all components every 5s; cache TTL 5s; response includes `health_cache_age_ms`
S3.3: Polls: EventBus, OptionsBackend, ModelRegistry, Orchestrator, each Adapter
S3.4: Adapter health per AR15: `HEALTHY | DEGRADED | UNHEALTHY`
S3.5: Aggregate: any UNHEALTHY → DEGRADED; any DEGRADED (no UNHEALTHY) → DEGRADED; all HEALTHY for 3 consecutive polls → READY
S3.6: Register `GET /api/health` — sole registrar (Plan 31 does not register this). Response includes subsystem breakdown.
S3.7: Register `GET /api/lifecycle/ready` — **unauthenticated** (no session cookie required; this is a cross-process readiness probe). Returns `LifecycleReadyResponse(ready: bool, server_pid: int, instance_uuid: str)`. **All three fields populated at process start** (`server_pid` = `os.getpid()`, `instance_uuid` = generated at compose-time, `ready` = toggled by lifecycle state). TUI obtains PID/UUID on first connect regardless of `ready` value. `ready: true` only after all startup stages complete.
S3.8: Test: `pytest app/sovereignai/tests/test_lifecycle_health.py -v`

## S4 — Graceful Shutdown

S4.1: SIGTERM/SIGINT → SHUTTING_DOWN
S4.2: Drain in-flight: 60s timeout (separate pre-stage). HTTP 503 + `Retry-After: 60` for new requests; in-flight requests continue.
S4.3: Shutdown sequence (sequential, after drain): Orchestrator (20s) → ModelRegistry (20s) → OptionsBackend (20s) → EventBus (20s) → LifecycleHookRegistry (30s: 15s non-critical concurrent + 15s critical sequential).
  **Force-kill timeout: 190s** = 60s drain + 80s stages (4×20) + 30s hooks + 20s headroom. AR check verifies: `force_kill_timeout - (drain + stages + hooks) == headroom`.
  **Shutdown order rationale**: Orchestrator first (drains active tasks), then ModelRegistry (flushes model state), then Options (persists config), then EventBus (last — all services depend on it for event emission). Hooks last (may reference any service). Reverse of startup would put EventBus first, but that would break event emission during Orchestrator/ModelRegistry/Options shutdown.
S4.4: TUI/Web NOT in shutdown sequence — monitor SSE sentinel; exit client-side
S4.5: Sentinel file: `platformdirs.user_cache_dir("sovereignai") / f"shutdown.{os.getpid()}.sentinel"`. Content: `timestamp\n{instance_uuid}\n`. Atomic write with `os.fsync`. Emit `lifecycle.shutdown.forced` if EventBus available.
  **Startup cleanup**: delete all `shutdown.*.sentinel` files where extracted PID is not running (`os.kill(pid, 0)` raises ProcessLookupError). **No UUID matching** — v1 is single instance per user; all stale sentinels from dead PIDs are safe to delete. Document: "Multi-instance sentinel isolation deferred to v2."
S4.6: Test: `pytest app/sovereignai/tests/test_lifecycle_shutdown.py -v`

## S5 — DI Composition

S5.1: `app/sovereignai/main.py` — compose all core services via DIContainer. **Instantiation order**:
  1. `LifecycleComposer` → LifecycleManager + HookRegistry
  2. `CoreServicesComposer` → EventBus, OptionsBackend
  3. `OrchestratorComposer` → Orchestrator, InterDepartmentBus (hooks may register here)
  4. `MemoryComposer` → MemoryGateway, PersistentGraphMemory (OrchestratorFactory resolves here)
  5. Call `LifecycleManager.start()` → REGISTRATION_OPEN → CLOSED
  6. Run startup sequence via `LifecycleManager.run_startup()`
  No hardcoded names per AR4.
S5.2: Sub-composers: `app/sovereignai/composers/{core,orchestrator,adapters,lifecycle,memory}.py`
S5.3: MemoryGateway sole owner of PersistentGraphMemory; Orchestrator + Librarian receive MemoryGateway via DI (Optional[MemoryGateway] for Orchestrator — late-bound, nullable until first memory API call).
S5.4: ≤15 constructor args per sub-composer and manager/hook class; AR check `test_max_constructor_args.py`
S5.5: Test: `pytest app/sovereignai/tests/test_main_composition.py -v`

## S6 — Circuit Breaker Integration

S6.1: Worker: >50 errors in 10s per `worker_id` = unload
S6.2: Orchestrator: >10 consecutive failures in 60s = DEGRADED. Consecutive = no success between failures. Recovery: 60s cooldown → half-open → 3 HEALTHY → close.
S6.3: Adapter: `health_check()` fails 3x = UNHEALTHY. Recovery: 60s → half-open → 3 HEALTHY → close.
S6.4: All circuit events via TraceEmitter (stderr fallback if EventBus down)
S6.5: Test: `pytest app/sovereignai/tests/test_lifecycle_circuits.py -v`

## S7 — AR Checks

S7.1: `check_lifecycle_no_globals.py` — no global state in lifecycle modules
S7.2: `check_lifecycle_health_check_coverage.py` — all adapters declare health_check
S7.3: `check_max_constructor_args.py` — each sub-composer/manager/hook `__init__` ≤15 args
S7.4: `check_lifecycle_phase_gate.py` — no hook registration after `start()`
S7.5: `check_sentinel_cleanup.py` — startup deletes stale sentinels for dead PIDs (no UUID condition)
S7.6: `check_max_shutdown_hooks.py` — max 5 total, max 1 critical
S7.7: `check_force_kill_budget.py` — verify `190 - (60 + 80 + 30) == 20`
S7.8: Run `pytest .agent/executor/tests/test_document_hygiene.py -v`

## Closing

Run `/close`
