Depends on: prompt-21, Plan 22 (Typed EventBus — introduces EventBus.start/stop/is_started that TraceEmitterWrapper depends on)
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P9 (observability), P11 (DI only)
Open questions resolved: Q-23.1 (ReActLoopFactory as Protocol), Q-23.2 (UUID session keys), Q-23.3 (TraceEmitterWrapper level parameter), Q-23.4 (ISkillRunner singleton close safety), Q-23.5 (GraphMemory Protocol, no forward import)

S0.5 research: Single-call structured output with Pydantic validation + bounded retry (max 3 total attempts) gives best reliability/speed tradeoff for local 7B models. Token-budget history prevents context window overflow. ReAct loop as CapabilityGraph-registered module preserves P1. Temperature cooling strategy: default → 0.1 → 0.0 with schema-reminder prefix on final attempt.

## S0 — Opening

S0.0 — Not resuming (second plan in queue). Skip resume check.
S0.1 — Run /open. Verify `prompt-21` and `prompt-22` tags exist on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — Check `.agent/executor/suggestions/` per OOR-1. At drafting: empty.
S0.4 — Check `.agent/shared/DEBT.md`. At drafting: no items relevant. Note: S2.3 GraphEntity TypedDict is optional — if deferred, add DEBT.md entry at /close.
S0.5 — Research findings documented in plan header above.

## Plan Body

### S1 — Create TraceEmitterWrapper in app/sovereignai/observability/trace_emitter.py
- NEW class (not subclass of existing TraceEmitter). Wraps existing TraceEmitter from prompt-20.9.9.
- Constructor: `__init__(self, event_bus: EventBus, inner: TraceEmitter)`.
- Method: `emit_event(event_name: str, payload: dict, level: TraceLevel = TraceLevel.INFO) -> None`. Prefixes `event_name` with "trace." ONLY if not already starting with "trace." (case-insensitive).
- When `event_bus.is_started` is True: construct `Event(channel=prefixed_name, payload=payload, trace_level=level)` and call `event_bus.publish(event)`.
- When EventBus not started: route to `inner.emit(component='trace', level=level, message=f"{prefixed_name}: {json.dumps(payload)}")`. Existing TraceEmitter signature unchanged.
- Wire as singleton in `build_container()`. Inject EventBus and existing TraceEmitter.

### S2 — Create ReActLoop in app/sovereignai/agent/react.py
- Standalone Agent capability (not core, per P1). Registered in CapabilityGraph.
- Constructor: `__init__(self, config: ReActConfig, skill_runner: ISkillRunner, session_registry: ToolSessionRegistry, emitter: TraceEmitterWrapper)`.
- On construction: `self._session_key = uuid.uuid4().hex`. Register injected skill_runner: `session_registry.register(self._session_key, skill_runner)`. UUID ensures GC-independent uniqueness.
- State: `self._pending_tool_calls = asyncio.Queue()` (instance-scoped, NOT class attribute).
- Methods: `run(task_description: str, tools: list[SkillManifest], session: SkillSession, context: dict | None = None, memory: GraphMemory | None = None) -> AgentResult`, `step(history: list[Turn]) -> ToolCall | FinalAnswer`.
- `context` parameter receives symbol context from CodingManager (Plan 24 S2). If not None, include in system prompt under "[Symbol Context]" section.
- `memory` parameter receives GraphMemory-compatible object from CodingManager. GraphMemory is Protocol in `app/sovereignai/agent/protocols.py` with method `query(entity_id: str, depth: int = 2) -> list[dict]`. If not None, call `memory.query()` with seed entities from task_description for "[Graph Context]" section.
- Emits trace event per step via injected TraceEmitterWrapper. Callers use unprefixed names: "react.step_completed", "react.tool_called". `emit_event()` handles prefixing. Pass `TraceLevel.CRITICAL` for terminal/error/completed events.

### S2.1 — Create ToolSessionRegistry in app/sovereignai/agent/tool_session.py
- Methods: `register(tool_id: str, runner: ISkillRunner)`, `close(tool_id: str)`, `close_all()`.
- Stores `dict[str, ISkillRunner]`.
- `register(tool_id, runner)`: if tool_id registered with DIFFERENT runner, raise `ValueError("tool_id already registered")`. If same pair, no-op (idempotent).
- `close(tool_id)`: removes entry from dict, does NOT call `runner.close()`. ISkillRunner is singleton. Returns without error if tool_id not found (idempotent).
- `close_all()`: iterate COPY of registered items, call `close(tool_id)` for each, clear dict. Reserved for app shutdown.
- Wire in `main.py build_container()` as singleton.

### S2.2 — Create agent types in app/sovereignai/agent/types.py
- `AgentErrorObservation`: Pydantic BaseModel with `error_type: str`, `message: str`, `last_response: str | None`, `failure_reasons: list[str]`, `retryable: bool = False`.
- `FinalAnswer`: Pydantic BaseModel with `content: str`.
- `AgentResult`: Pydantic BaseModel with `status: Literal["success", "error"]`, `output: str | None`, `error: AgentErrorObservation | None`, `trace: list[str]`.

### S2.3 — Create GraphMemory Protocol in app/sovereignai/agent/protocols.py
- `@runtime_checkable` decorator REQUIRED for runtime isinstance() checks in tests.
- Protocol class `GraphMemory` with method `query(entity_id: str, depth: int = 2) -> list[dict]`.
- ReActLoop imports this Protocol for type hints. No dependency on Plan 24's concrete implementation.
- Plan 24's TaskGraphCache satisfies this Protocol structurally (claim verified when Plan 24 lands — if Plan 24's API differs, Protocol must be updated).
- Optional: Define `GraphEntity` TypedDict with `id: str`, `type: str`, `attributes: dict[str, Any]`. Change return type to `list[GraphEntity]` for stronger type safety. If deferred, add DEBT.md entry at /close.

### S3 — Create structured prompt template in app/sovereignai/agent/prompts.py
- System prompt: THOUGHT / ACTION / OBSERVATION format.
- Tool definitions injected as compact schema summaries from SkillManifest.
- If `context` provided, append "[Symbol Context]" section with ranked symbols.
- If `memory` provided, append "[Graph Context]" section with relevant graph entities from `memory.query()`.
- Uses same trace emission as S2 — no additional emit call per step.

### S4 — Create ReActConfig and TokenBudgetHistory in app/sovereignai/agent/history.py and app/sovereignai/agent/config.py
- `ReActConfig`: Pydantic model in `app/sovereignai/agent/config.py`. Fields: `max_context_tokens: int = 8192`.
- `TokenBudgetHistory`: Compress conversation to fit token budget. Never exceed budget unless minimum pinned context cannot fit.
- `to_messages(budget)` guarantees at minimum: system prompt + task description + last 2 turns preserved, even if exceeds budget. If budget below minimum, log warning and use minimum.
- If pinned minimum exceeds adapter's advertised `max_context_tokens` (default 8192, configurable via ReActConfig), raise `TokenBudgetExceededError` immediately. Comparison uses `min(ReActConfig.max_context_tokens, adapter_reported_max_context_tokens)` if adapter advertises limit; otherwise config default. Error message: "Task description too large for model context window. Options: (1) reduce task scope, (2) set ReActConfig.max_context_tokens to a higher value (if model supports it), or (3) switch to a larger model."
- Methods: `add_turn(role, content)`, `to_messages(budget)`.

### S5 — Create SingleCallStructuredOutput in app/sovereignai/agent/structured_output.py
- Pydantic model for LLM response: `ToolCall | FinalAnswer`.
- Validation with bounded retry: max 3 total attempts (1 initial + 2 retries).
- Attempt 1: default temperature. Attempt 2: temperature 0.1. Attempt 3: temperature 0.0 with schema-reminder prefix.
- After 3 consecutive validation failures, raise `StructuredOutputExhaustedError` containing last raw LLM response and all failure reasons. Emit trace event via injected TraceEmitterWrapper before raising (`level=TraceLevel.CRITICAL`). ReActLoop catches and produces `AgentErrorObservation` propagated to caller, not a crash.
- Works with any backend supporting structured output (Ollama, vLLM, llama.cpp).

### S6 — Integrate ReActLoop with ISkillRunner
- ReActLoop delegates tool execution to ISkillRunner via injected `skill_runner`.
- Converts `SkillResult` to `Observation`: `Observation(role='tool', content=result.output, tool_call_id=...)`. If `result.error` set, convert to `ToolErrorObservation`.
- `ToolErrorObservation` fed back as next observation.
- Safety bounds: `max_iterations=50`, `max_consecutive_errors=5`, `max_execution_time=600s` (enforced via `asyncio.timeout()` — Python 3.11+ required per pyproject.toml).
- On `run()` completion (success or error): call `session_registry.close(self._session_key)`. Does NOT call `runner.close()` — ISkillRunner is singleton.
- On `StructuredOutputExhaustedError`: (1) drain `_pending_tool_calls` queue, (2) emit `trace.react.structured_output_exhausted` via TraceEmitterWrapper with `session_key` in payload (`level=TraceLevel.CRITICAL`), (3) call `session_registry.close(self._session_key)`. Do NOT call `close_all()`.
- On `TokenBudgetExceededError`: ReActLoop catches at loop start, converts to `AgentErrorObservation` (no cleanup needed — no resources acquired), returns without calling LLM.

### S7 — Create web endpoints in app/web/main.py
- `/api/agent/tasks` POST: submit agent task. Returns `AgentTaskResponseDTO`.
- `/api/agent/tasks/{task_id}` GET: get status + reasoning trace.
- `/api/agent/tasks/{task_id}/stream` GET: SSE streaming reasoning steps. Enforce session cookie auth; reject unauthenticated with 403.
- Web UI consumer for agent SSE deferred — add DEBT.md entry with target plan TBD. TUI tasks panel (S8) consumes the stream.
- DTOs in `app/web/schemas.py`: `AgentTaskSubmitDTO`, `AgentTaskResponseDTO`, `AgentStepDTO`.

### S8 — Update TUI tasks panel in app/tui/panels/tasks.py
- WILL edit: `tasks.py` — add agent task indicator, reasoning trace display.
- WILL NOT edit: other panels.
- Show task type (direct vs agent). Display last reasoning step.
- Follow `compose()` -> `on_mount()` -> `_load_data()` pattern.

### S9 — Create tests in .agent/executor/tests/sovereignai/
- `test_react_loop.py`: step-by-step reasoning, max iteration bound.
- `test_structured_output.py`: validation + retry, max 3 attempts, exhausted retry returns typed error, cooling_temperature_strategy (verifies temp decreases).
- `test_token_budget.py`: budget enforcement, truncation order, task-description retention, budget_exceeded_error_on_impossible_minimum.
- `test_agent_integration.py`: end-to-end task with mock LLM.
- `test_react_concurrency.py`: two ReActLoop instances concurrent with shared LLM backend (mock) do not interfere; retry counters per-instance; `test_error_cleans_up_resources` (drain → emit → close order); `test_duplicate_registration_raises`; `test_session_key_is_uuid`.
- `test_agent_api.py`: endpoint auth, task submission, SSE stream auth rejection.
- `test_trace_emitter_wrapper.py`: emit_event prefixes correctly, no double-prefix, fallback when EventBus not started, level parameter works, CRITICAL-level events construct Event with `trace_level=TraceLevel.CRITICAL`.
- `test_react_loop_factory_protocol_registration`: verifies Protocol class works as DIContainer key; concrete ReActLoop key works. BOTH keys registered unconditionally (DD-23.11.1).
- `test_graph_memory_protocol`: verifies duck-typed GraphMemory object satisfies Protocol at runtime (requires `@runtime_checkable` per DD-23.11.3).

### S10 — Wire in app/sovereignai/main.py build_container()
- Register ReActLoop as FACTORY (not singleton) under capability name 'agent.react'.
- Define `ReActLoopFactory` as Protocol class:
  ```python
  class ReActLoopFactory(Protocol):
      def __call__(self) -> ReActLoop: ...
  ```
- UNCONDITIONAL dual registration (DD-23.11.1): ALWAYS register both keys pointing to same factory lambda:
  ```python
  factory = lambda: ReActLoop(...)
  container.register_factory(ReActLoopFactory, factory)
  container.register_factory(ReActLoop, factory)
  ```
  No try/except, no conditional fallback.
- Retrieve: `loop = container.retrieve(ReActLoopFactory)` — returns instance directly.
- Inject ReActConfig, ToolSessionRegistry, ISkillRunner, TraceEmitterWrapper.
- Register in CapabilityGraph.

### S11 — Landmine compliance
- M1: All imports use `sovereignai.*` package path.
- M2: Update `WEB_MAIN_ALLOWED_IMPORTS` and `TUI_ALLOWED_IMPORTS` in `.agent/executor/tests/sovereignai/test_ar7_no_core_imports_in_ui.py` for new imports in `app/web/main.py` and `app/tui/panels/tasks.py`.
- M3: Update `ALLOWLIST` in `.agent/executor/scripts/ar_checks/spec_match.py` for new paths: `app/sovereignai/agent/`, `app/sovereignai/observability/`.
- M4: All test files in `.agent/executor/tests/sovereignai/`.

### S12 — Run /verify after each edit. Run /close per VOR-2.
- At /close step 12, add DD-23.11.1, DD-23.11.3 to `.agent/shared/DECISIONS.md` as Proposed status.
