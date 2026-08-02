# Brief — Batch 21 Rev 10

## 1. Scope
Plans 21–24: Skill Framework → ReAct Agent → Typed Events → Departments.

## 2. Dependencies
Plan 21 depends on prompt-20.9.9.
Plan 22 depends on Plan 21.
Plan 23 depends on prompt-20.9.9.
Plan 24 depends on Plan 22 + Plan 23.
Binary: if any plan STOPs, all downstream plans STOP.

## 3. Vision Principles
P1 (core sacred), P2 (pluggable), P5 (wire as you go), P7 (modular), P9 (observability), P11 (DI only), P13 (strong and robust).

## 4. Open Questions Resolved
Q-21.1: CapabilityCategory.SKILL enum added.
Q-21.2: skill_id used directly in find_providers().
Q-21.3: ComponentManifest metadata backward compat verified via kwarg check.
Q-22.1: ReActLoopFactory as Protocol with concrete fallback.
Q-22.2: UUID session keys.
Q-22.3: TraceEmitterWrapper level parameter propagates to EventBus.
Q-22.4: ISkillRunner singleton close lifecycle documented.
Q-22.5: GraphMemory Protocol in Plan 22, no forward import.
Q-23.1: Critical events use reserved queue, not direct dispatch.
Q-23.2: queue.dropped aggregated per handler per second.
Q-23.3: Lifespan ordering fixed (handlers → bus.start → container.start).
Q-23.4: _publish_internal defined with runtime guards.
Q-23.5: Three-state EventBus (INIT/RUNNING/STOPPING/STOPPED).
Q-23.6: Pre-start buffer overflow = drop-oldest + warning.
Q-24.1: DIContainer factory semantics (retrieve returns instance).
Q-24.2: GraphMemoryBackend renamed TaskGraphCache, ephemeral.
Q-24.3: build_context returns dict | None.
Q-24.4: Ephemeral graph memory scope documented.

## 5. Key Decisions (DD-IDs)
DD-21.10.1: ComponentManifest kwarg verification before metadata addition.
DD-22.10.1: ReActLoopFactory Protocol primary + concrete fallback.
DD-22.10.2: TraceEmitterWrapper constructs Event with trace_level=level.
DD-22.10.3: GraphMemory Protocol in sovereignai/agent/protocols.py.
DD-22.10.4: Singleton close lifecycle documented; cleanup ordering fixed.
DD-23.10.1: Three-state EventBus replaces _started/_stopping booleans.
DD-23.10.2: Lifespan: handlers register → bus.start() → container.start().
DD-23.10.3: Critical events use reserved bounded queue (size=100).
DD-23.10.4: __publish_internal with name mangling + runtime guards.
DD-23.10.5: event_bus.is_started property exposed.
DD-23.10.6: Pre-start buffer overflow = drop-oldest + warning.
DD-24.10.1: build_context() returns dict | None.
DD-24.10.2: TaskGraphCache ephemeral with close() method.
DD-24.10.3: Latency test: warmup + 3-run median.
DD-24.10.4: Runtime guard: try/except ImportError.

## 6. Landmines
BLOCKING: None identified in Rev 10 screening.

## 7. Risks to Verify
R-21.10.1: Does kwarg verification catch all positional ComponentManifest usages?
R-22.10.1: Does GraphMemory Protocol satisfy mypy strict mode?
R-22.10.2: Does ReActLoopFactory concrete fallback work when Protocol rejected?
R-23.10.1: Does three-state state machine prevent all race conditions?
R-23.10.2: Does reserved critical queue (size=100) overflow under extreme load?
R-23.10.3: Does __publish_internal prevent misuse by non-drain callers?
R-24.10.1: Does TaskGraphCache.close() in finally block always execute?
R-24.10.2: Does warmup + 3-run median eliminate CI flakiness?

## 8. Test Strategy
Unit tests per plan file. Integration test (test_department_full_cycle) runtime-guarded. Latency test marked @pytest.mark.slow. All tests include auth rejection without cookie.

## 9. Delivery Target
C:/SovereignAI/prompts/plan-{21,22,23,24}-rev10.md

## 10. Revision History
Rev 1–6: Initial drafts + Round Table cycles.
Rev 7: CRITICAL/HIGH fixes from Rev 6 (register_factory pattern, Worker spawn, critical-event exemption).
Rev 8: CRITICAL/HIGH fixes from Rev 7 (SKILL enum, Protocol class, UUID keys, 5s timeout, GraphMemoryBackend wiring).
Rev 9: CRITICAL/HIGH fixes from Rev 8 (lifespan order, critical-event routing, _publish_internal, SymbolContext type).
Rev 10: CRITICAL/HIGH fixes from Rev 9 (three-state bus, reserved critical queue, GraphMemory Protocol, TaskGraphCache, latency test methodology).
