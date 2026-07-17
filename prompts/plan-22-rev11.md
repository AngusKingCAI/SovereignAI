Depends on: Plan 21
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P9 (observability), P11 (DI only)
Open questions resolved: Q-22.1 (ReActLoopFactory as Protocol), Q-22.2 (UUID session keys), Q-22.3 (TraceEmitterWrapper level parameter), Q-22.4 (ISkillRunner singleton close safety), Q-22.5 (GraphMemory Protocol, no forward import)

S0.4 best practices: Single-call structured output with Pydantic validation + bounded retry (max 3 total attempts) gives best reliability/speed tradeoff for local 7B models. Token-budget history prevents context window overflow. ReAct loop as CapabilityGraph-registered module preserves P1. Temperature cooling strategy: default → 0.1 → 0.0 with schema-reminder prefix on final attempt.

## S0 — Opening

S0.1 — Run /open. Verify Plan 21 tag exists on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — No new rules for this plan.

## Plan Body

### S0.5 — Create TraceEmitterWrapper in sovereignai/observability/trace_emitter.py
- NEW class (not subclass of existing TraceEmitter). Wraps existing TraceEmitter from prompt-20.9.9.
- Constructor takes event_bus: EventBus and inner: TraceEmitter (existing).
- Method: emit_event(event_name: str, payload: dict, level: TraceLevel = TraceLevel.INFO) -> None. Prefixes event_name with "trace." ONLY if event_name does not already start with "trace." (case-insensitive: check event_name.lower()).
- When EventBus is started (event_bus.is_started is True): construct Event(channel=prefixed_name, payload=payload, trace_level=level) and call event_bus.publish(event). The trace_level field on Event carries the level for downstream critical-event routing.
- When EventBus is not started: route to inner.emit(component='trace', level=level, message=f"{prefixed_name}: {json.dumps(payload)}") directly. Existing TraceEmitter signature (component, level, message) is unchanged.
- Wire as singleton in build_container(). Inject EventBus and existing TraceEmitter into constructor.

### S1 — Create ReActLoop in sovereignai/agent/react.py
- Standalone Agent capability (not core, per P1). Registered in CapabilityGraph.
- Constructor: __init__(self, config: ReActConfig, skill_runner: ISkillRunner, session_registry: ToolSessionRegistry, emitter: TraceEmitterWrapper).
- On construction, generate self._session_key = uuid.uuid4().hex. Register the injected skill_runner in session_registry under this key: session_registry.register(self._session_key, skill_runner). UUID ensures GC-independent uniqueness.
- State: self._pending_tool_calls = asyncio.Queue() (instance-scoped, NOT class attribute).
- Methods: run(task_description: str, tools: list[SkillManifest], session: SkillSession, context: dict | None = None, memory: GraphMemory | None = None) -> AgentResult, step(history: list[Turn]) -> ToolCall | FinalAnswer.
- The context parameter receives symbol context from CodingManager (Plan 24 S2). If context is not None, include it in the system prompt under a "[Symbol Context]" section. If None, omit the section.
- The memory parameter receives a GraphMemory-compatible object from CodingManager (Plan 24 S2). GraphMemory is a Protocol defined in sovereignai/agent/protocols.py with method query(entity_id: str, depth: int = 2) -> list[dict]. If memory is not None, call memory.query() with seed entities derived from task_description to build "[Graph Context]" section. If None, omit.
- Emits trace event per step via injected TraceEmitterWrapper. Callers use unprefixed names: "react.step_completed", "react.tool_called", etc. emit_event() handles prefixing. Pass TraceLevel.CRITICAL for terminal/error/completed events.

### S1.1 — Create ToolSessionRegistry in sovereignai/agent/tool_session.py
- Methods: register(tool_id: str, runner: ISkillRunner), close(tool_id: str), close_all().
- Stores dict[str, ISkillRunner].
- register(tool_id, runner): if tool_id already registered with a DIFFERENT runner, raise ValueError("tool_id already registered"). If same (tool_id, runner) pair, no-op (idempotent). This prevents silent shadowing.
- close(tool_id) removes the entry from dict but does NOT call runner.close(). ISkillRunner is a singleton; per-task cleanup removes registry entry only. Returns without error if tool_id not found (idempotent).
- close_all() iterates a COPY of registered items, calls close(tool_id) for each, then clears the dict. Reserved for app shutdown only.
- Wire in main.py build_container() as singleton.

### S1.2 — Create agent types in sovereignai/agent/types.py
- AgentErrorObservation: Pydantic BaseModel with error_type: str, message: str, last_response: str | None, failure_reasons: list[str], retryable: bool = False.
- FinalAnswer: Pydantic BaseModel with content: str.
- AgentResult: Pydantic BaseModel with status: Literal["success", "error"], output: str | None, error: AgentErrorObservation | None, trace: list[str].

### S1.3 — Create GraphMemory Protocol in sovereignai/agent/protocols.py
- @runtime_checkable decorator REQUIRED for runtime isinstance() checks in tests.
- Protocol class GraphMemory with method query(entity_id: str, depth: int = 2) -> list[dict].
- ReActLoop imports this Protocol for type hints. No dependency on Plan 24's concrete implementation.
- Plan 24's TaskGraphCache satisfies this Protocol structurally.
- Optional: Define GraphEntity TypedDict with id: str, type: str, attributes: dict[str, Any] fields. Change return type to list[GraphEntity] for stronger type safety. If deferred, add DEBT.md entry.

### S2 — Create structured prompt template in sovereignai/agent/prompts.py
- System prompt: THOUGHT / ACTION / OBSERVATION format.
- Tool definitions injected as compact schema summaries from SkillManifest.
- If context parameter is provided (Plan 24 S2), append "[Symbol Context]" section with ranked symbols.
- If memory parameter is provided, append "[Graph Context]" section with relevant graph entities from memory.query().
- Uses the same trace emission described in S1 — no additional emit call per step.

### S3 — Create ReActConfig and TokenBudgetHistory in sovereignai/agent/history.py
- ReActConfig: Pydantic model in sovereignai/agent/config.py. Fields: max_context_tokens: int = 8192.
- TokenBudgetHistory: Compress conversation to fit token budget. Never exceed budget unless minimum pinned context cannot fit.
- to_messages(budget) guarantees at minimum the system prompt + task description + last 2 turns are preserved, even if that exceeds budget. If budget is below this minimum, log warning and use minimum.
- If pinned minimum exceeds adapter's advertised max_context_tokens (default 8192, configurable via ReActConfig), raise TokenBudgetExceededError immediately — do not call LLM. Comparison uses min(ReActConfig.max_context_tokens, adapter_reported_max_context_tokens) if adapter advertises a limit; otherwise uses config default. Error message: "Task description too large for model context window. Options: (1) reduce task scope, (2) set ReActConfig.max_context_tokens to a higher value (if model supports it), or (3) switch to a larger model."
- add_turn(role, content), to_messages(budget) methods.

### S4 — Create SingleCallStructuredOutput in sovereignai/agent/structured_output.py
- Pydantic model for LLM response: ToolCall | FinalAnswer.
- Validation with bounded retry: max 3 total attempts (1 initial + 2 retries).
- Attempt 1: default temperature.
- Attempt 2: temperature 0.1.
- Attempt 3: temperature 0.0 with schema-reminder prefix injected into system prompt.
- After 3 consecutive validation failures, raise StructuredOutputExhaustedError containing the last raw LLM response and all failure reasons. Emits trace event via injected TraceEmitterWrapper before raising (pass level=TraceLevel.CRITICAL). ReActLoop catches this and produces AgentErrorObservation propagated to caller, not a crash.
- Works with any backend supporting structured output (Ollama, vLLM, llama.cpp).

### S5 — Integrate ReActLoop with ISkillRunner
- ReActLoop delegates tool execution to ISkillRunner via injected skill_runner.
- Converts SkillResult to Observation: Observation(role='tool', content=result.output, tool_call_id=...). If result.error is set, convert to ToolErrorObservation instead.
- ToolErrorObservation fed back as next observation.
- Safety bounds: max_iterations=50, max_consecutive_errors=5, max_execution_time=600s (enforced via asyncio.wait_for() wrapping the run() call). Use asyncio.wait_for() for Python <3.11 compatibility; do not use asyncio.timeout.
- On run() completion (success or error): call session_registry.close(self._session_key) to remove only this loop's entry. Does NOT call runner.close() — ISkillRunner is singleton.
- On StructuredOutputExhaustedError: (1) drain _pending_tool_calls queue (discard all items), (2) emit trace.react.structured_output_exhausted via injected TraceEmitterWrapper with session_key in payload (level=TraceLevel.CRITICAL), (3) call session_registry.close(self._session_key) to remove this loop's entry. Do NOT call close_all().
- On TokenBudgetExceededError: ReActLoop catches at loop start, converts to AgentErrorObservation (no cleanup needed since no resources acquired), and returns without calling LLM.

### S6 — Create web endpoints in web/main.py
- /api/agent/tasks POST: submit agent task. Returns AgentTaskResponseDTO.
- /api/agent/tasks/{task_id} GET: get status + reasoning trace.
- /api/agent/tasks/{task_id}/stream GET: SSE streaming reasoning steps. Enforce session cookie auth; reject unauthenticated connections with 403.
- Web UI consumer for agent SSE deferred — add DEBT.md entry with target plan TBD. TUI tasks panel (S7) consumes the stream.
- DTOs in web/schemas.py: AgentTaskSubmitDTO, AgentTaskResponseDTO, AgentStepDTO.

### S7 — Update TUI tasks panel (tui/panels/tasks.py)
- WILL edit: tasks.py — add agent task indicator, reasoning trace display.
- WILL NOT edit: other panels.
- Show task type (direct vs agent). Display last reasoning step.
- Follow compose() -> on_mount() -> _load_data() pattern.

### S8 — Create tests
- test_react_loop.py: step-by-step reasoning, max iteration bound.
- test_structured_output.py: validation + retry, max 3 total attempts (1 initial + 2 retries), exhausted retry returns typed error, cooling_temperature_strategy (verifies temp decreases, not increases).
- test_token_budget.py: budget enforcement, truncation order, task-description retention under truncation, budget_exceeded_error_on_impossible_minimum (verifies loop-level catch + AgentErrorObservation).
- test_agent_integration.py: end-to-end task with mock LLM.
- test_react_concurrency.py: two ReActLoop instances running concurrently with shared LLM backend (mock) do not interfere. Retry counters are per-instance. test_error_cleans_up_resources (verifies drain → emit → close order). test_duplicate_registration_raises (verifies ValueError on different runner, same key). test_session_key_is_uuid (verifies uuid4 format, not id()).
- test_agent_api.py: endpoint auth, task submission, SSE stream auth rejection.
- test_trace_emitter_wrapper.py: verifies emit_event prefixes correctly, no double-prefix, fallback when EventBus not started, level parameter works, CRITICAL-level events construct Event with trace_level=TraceLevel.CRITICAL.
- test_react_loop_factory_protocol_registration: verifies Protocol class works as DIContainer key; also verify concrete ReActLoop key works. BOTH keys registered unconditionally (DD-22.11.1).
- test_graph_memory_protocol: verifies duck-typed GraphMemory object satisfies Protocol at runtime (requires @runtime_checkable per DD-22.11.3).

### S9 — Wire in main.py build_container()
- Register ReActLoop as FACTORY (not singleton) under capability name 'agent.react'.
- Define ReActLoopFactory as Protocol class (not type alias):
  ```python
  class ReActLoopFactory(Protocol):
      def __call__(self) -> ReActLoop: ...
  ```
- UNCONDITIONAL dual registration (DD-22.11.1): ALWAYS register both keys pointing to the same factory lambda:
  ```python
  factory = lambda: ReActLoop(...)
  container.register_factory(ReActLoopFactory, factory)
  container.register_factory(ReActLoop, factory)
  ```
  No try/except, no conditional fallback. Both keys always available.
- Retrieve: loop = container.retrieve(ReActLoopFactory)  # Returns ReActLoop instance directly — no trailing (). DIContainer.retrieve() invokes the factory; returns instance directly.
- Inject ReActConfig, ToolSessionRegistry, ISkillRunner, TraceEmitterWrapper.
- Register in CapabilityGraph.

### S10 — Run /verify after each edit. Run /close.
