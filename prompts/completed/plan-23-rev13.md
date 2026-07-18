Depends on: prompt-21, Plan 22 (Typed EventBus — introduces EventBus.start/stop/is_started that TraceEmitterWrapper depends on)
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P9 (observability), P11 (DI only)
Open questions resolved: Q-23.1 through Q-23.5

S0.5 research: Single-call structured output + bounded retry (max 3 attempts) gives best reliability for local 7B models. Token-budget history prevents context overflow. ReAct loop as CapabilityGraph-registered module preserves P1. Temperature cooling: default → 0.1 → 0.0.

## S0 — Opening

S0.0 — Not resuming. Skip.
S0.1 — Run /open. Verify `prompt-21` and `prompt-22` tags. Working copy clean.
S0.2 — Read AGENTS.md.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant.
S0.5 — Verified: `DIContainer` uses `dict[type[Any], ...]` for both `_instances` and `_factories` (P23-E). Protocol classes are hashable types and work as factory keys; `retrieve(Protocol)` invokes factory and returns instance. S10 dual-registration pattern is sound.

## Plan Body

### S1 — Create TraceEmitterWrapper in app/sovereignai/observability/trace_emitter.py
- NEW class (not subclass of existing TraceEmitter). Wraps TraceEmitter from prompt-20.9.9.
- Constructor: `__init__(self, event_bus: EventBus, inner: TraceEmitter)`.
- `emit_event(event_name: str, payload: dict, level: TraceLevel = TraceLevel.INFO) -> None`. Prefixes with "trace." if not already starting with "trace." (case-insensitive).
- When `event_bus.is_started` (Plan 22 S4): construct `Event(channel=prefixed_name, payload=payload, trace_level=level)`, call `event_bus.publish(event)`.
- When not started: route to `inner.emit(component='trace', level=level, message=...)`.
- Wire as singleton in `build_container()`.

### S2 — Create ReActLoop in app/sovereignai/agent/react.py
- Standalone Agent capability (not core, per P1). Registered in CapabilityGraph.
- Constructor: `__init__(self, config: ReActConfig, skill_runner: ISkillRunner, session_registry: ToolSessionRegistry, emitter: TraceEmitterWrapper)`.
- On construction: `self._session_key = uuid.uuid4().hex`. Register: `session_registry.register(self._session_key, skill_runner)`.
- State: `self._pending_tool_calls = asyncio.Queue()` (instance-scoped, NOT class attribute).
- `run(task_description, tools, session, context=None, memory=None) -> AgentResult`, `step(history) -> ToolCall | FinalAnswer`.
- `context` from CodingManager (Plan 24 S2). If not None, include "[Symbol Context]" section.
- `memory` from CodingManager. GraphMemory Protocol (S2.3). If not None, call `memory.query()` for "[Graph Context]".
- Emit trace per step via TraceEmitterWrapper. `TraceLevel.CRITICAL` for terminal/error/completed.

### S2.1 — Create ToolSessionRegistry in app/sovereignai/agent/tool_session.py
- `register(tool_id, runner)`: if registered with DIFFERENT runner, raise `ValueError`. Same pair: no-op.
- `close(tool_id)`: removes entry, does NOT call `runner.close()` (singleton). Idempotent.
- `close_all()`: iterate COPY, `close(tool_id)` each, clear dict. Reserved for shutdown.
- Wire in `main.py build_container()` as singleton.

### S2.2 — Create agent types in app/sovereignai/agent/types.py
- `AgentErrorObservation`: Pydantic BaseModel. `error_type: str`, `message: str`, `last_response: str | None`, `failure_reasons: list[str]`, `retryable: bool = False`.
- `FinalAnswer`: `content: str`. `AgentResult`: `status: Literal["success", "error"]`, `output: str | None`, `error: AgentErrorObservation | None`, `trace: list[str]`.

### S2.3 — Create GraphMemory Protocol in app/sovereignai/agent/protocols.py (P23-A)
- `@runtime_checkable` REQUIRED for runtime isinstance() checks.
- Protocol class `GraphMemory` with method `query(entity_id: str, depth: int = 2) -> list[dict]`.
- **Locked contract (P23-A)**: Plan 24 S5 `TaskGraphCache.query` signature MUST be exactly `query(entity_id: str, depth: int = 2) -> list[dict]`. Plan 24 S5 already specifies this exact signature. Any deviation in Plan 24 requires Plan 23 Protocol update.
- Plan 24 S9 MUST include named test `test_task_graph_cache_satisfies_graph_memory_protocol` that asserts `isinstance(TaskGraphCache(), GraphMemory)`.

### S3 — Create structured prompt template in app/sovereignai/agent/prompts.py
- System prompt: THOUGHT / ACTION / OBSERVATION format.
- Tool definitions injected as compact schema summaries from SkillManifest.
- `[Symbol Context]` if context. `[Graph Context]` if memory.
- Same trace emission as S2.

### S4 — Create ReActConfig and TokenBudgetHistory
- `ReActConfig`: Pydantic in `app/sovereignai/agent/config.py`. `max_context_tokens: int = 8192`.
- `TokenBudgetHistory` in `app/sovereignai/agent/history.py`: compress to fit budget. `to_messages(budget)` guarantees system prompt + task description + last 2 turns preserved (even if exceeds budget; warn if below minimum).
- If pinned minimum exceeds `adapter.max_context_tokens`: raise `TokenBudgetExceededError` immediately. Error message: "Task description too large for model context window. Options: (1) reduce task scope, (2) increase `ReActConfig.max_context_tokens`, (3) switch to larger model."
- Methods: `add_turn(role, content)`, `to_messages(budget)`.

### S5 — Create SingleCallStructuredOutput in app/sovereignai/agent/structured_output.py
- Pydantic model: `ToolCall | FinalAnswer`.
- Bounded retry: max 3 attempts (1 initial + 2 retries). Attempt 1: default temp. Attempt 2: temp 0.1. Attempt 3: temp 0.0 + schema-reminder prefix.
- After 3 failures: raise `StructuredOutputExhaustedError` with last raw response + failure reasons. Emit trace via TraceEmitterWrapper (`level=TraceLevel.CRITICAL`) before raising. ReActLoop catches → `AgentErrorObservation` to caller.

### S6 — Integrate ReActLoop with ISkillRunner (P23-B, P23-C, P23-G)
- Delegate tool execution to `skill_runner`. Convert `SkillResult` → `Observation`. If `result.error`: `ToolErrorObservation`.
- **`run()` body wrapped in `try: ... finally: await session_registry.close(self._session_key)` (P23-B)**. Specific handlers (`StructuredOutputExhaustedError`, normal completion, `TokenBudgetExceededError`) inside `try`. `finally` guarantees cleanup for ANY exception including unhandled.
- **`asyncio.timeout(600)` wraps the `try/finally` block (P23-C)**: on `TimeoutError`, `finally` still fires `session_registry.close(self._session_key)`. ReActLoop catches `TimeoutError`, converts to `AgentErrorObservation(retryable=False)`.
- Safety bounds: `max_iterations=50`, `max_consecutive_errors=5`, `max_execution_time=600s` (Python 3.11+ per pyproject.toml).
- On `StructuredOutputExhaustedError` (P23-G): (1) **log each pending `ToolCall` payload at WARNING level with `session_key`** before draining, (2) drain `_pending_tool_calls`, (3) emit `trace.react.structured_output_exhausted` (`level=TraceLevel.CRITICAL`), (4) `session_registry.close(self._session_key)`. Do NOT call `close_all()`.
- On `TokenBudgetExceededError`: catch at loop start, convert to `AgentErrorObservation` (no cleanup needed — no resources acquired), return without calling LLM.

### S7 — Create web endpoints in app/web/main.py
- `/api/agent/tasks` POST → `AgentTaskResponseDTO`. `/api/agent/tasks/{task_id}` GET → status + trace. `/api/agent/tasks/{task_id}/stream` GET → SSE; session cookie auth; 403 unauthenticated.
- Web UI consumer for agent SSE deferred (DEBT.md entry at /close). TUI tasks panel (S8) consumes stream.
- DTOs in `app/web/schemas.py`: `AgentTaskSubmitDTO`, `AgentTaskResponseDTO`, `AgentStepDTO`.

### S8 — Update TUI tasks panel in app/tui/panels/tasks.py (P23-F)
- WILL edit: `tasks.py` — agent task indicator, reasoning trace display. WILL NOT edit: other panels.
- **Cookie auth (P23-F)**: TUI `tasks.py` MUST include session cookie in SSE request headers. If TUI framework cannot attach cookie, defer stream consumption and add DEBT.md entry instead of shipping a broken panel.
- Follow `compose()` → `on_mount()` → `_load_data()` pattern.

### S9 — Tests in .agent/executor/tests/sovereignai/
- `test_react_loop.py`: step reasoning, max iteration bound, **`test_session_close_on_unhandled_exception` (P23-B)**, **`test_session_close_on_timeout` (P23-C)**.
- `test_structured_output.py`: validation + retry, max 3 attempts, exhausted returns typed error, cooling_temperature_strategy.
- `test_token_budget.py`: budget enforcement, truncation order, retention, `budget_exceeded_error_on_impossible_minimum`.
- `test_agent_integration.py`: end-to-end with mock LLM.
- `test_react_concurrency.py`: two concurrent ReActLoop instances, retry counters per-instance, `test_error_cleans_up_resources`, `test_duplicate_registration_raises`, `test_session_key_is_uuid`.
- `test_agent_api.py`: endpoint auth, task submission, SSE stream auth rejection.
- `test_trace_emitter_wrapper.py`: prefix, no double-prefix, fallback when not started, level parameter, CRITICAL constructs Event.
- `test_react_loop_factory_protocol_registration`: Protocol key + concrete key both work (DD-23.11.1). **`test_retrieve_protocol_returns_instance` (P23-E)**.
- `test_graph_memory_protocol`: duck-typed object satisfies Protocol (`@runtime_checkable`, DD-23.11.3). **`test_pending_tool_calls_logged_before_drain` (P23-G)**.

### S10 — Wire in app/sovereignai/main.py build_container()
- Register ReActLoop as FACTORY under capability name 'agent.react'.
- Define `ReActLoopFactory` as Protocol class: `class ReActLoopFactory(Protocol): def __call__(self) -> ReActLoop: ...`
- UNCONDITIONAL dual registration (DD-23.11.1): `container.register_factory(ReActLoopFactory, factory)` + `container.register_factory(ReActLoop, factory)`. No try/except.
- Retrieve: `loop = container.retrieve(ReActLoopFactory)` returns instance directly.
- Inject ReActConfig, ToolSessionRegistry, ISkillRunner, TraceEmitterWrapper. Register in CapabilityGraph.

### S11 — Landmine compliance
- M1: `sovereignai.*` imports. M2: update `WEB_MAIN_ALLOWED_IMPORTS` + `TUI_ALLOWED_IMPORTS` for `app/web/main.py` + `app/tui/panels/tasks.py`. M3: update `spec_match.py` ALLOWLIST for `app/sovereignai/{agent,observability}/`. M4: tests in `tests/sovereignai/`.

### S12 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-23.11.1, DD-23.11.3 to `.agent/shared/DECISIONS.md` as Proposed.
