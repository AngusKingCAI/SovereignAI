Depends on: Plan 21
Vision principles: P1 (core sacred), P2 (pluggable), P5 (wire as you go), P9 (observability), P11 (DI only)
Open questions resolved: none

S0.4 best practices: Single-call structured output with Pydantic validation + bounded retry (max 3) gives best reliability/speed tradeoff for local 7B models. Token-budget history prevents context window overflow. ReAct loop as CapabilityGraph-registered module preserves P1. Temperature retry strategy: cooling (default → 0.1 → 0.0) with schema-reminder prefix on final attempt — higher temperature reduces schema adherence.

## S0 — Opening

S0.1 — Run /open. Verify Plan 21 tag exists on origin. Working copy clean on main.
S0.2 — Read AGENTS.md in full.
S0.3 — No new rules for this plan.

## Plan Body

### S1 — Create ReActLoop in sovereignai/agent/react.py
- Standalone Agent capability (not core, per P1). Registered in CapabilityGraph.
- Constructor: __init__(self, config: ReActConfig, skill_runner: ISkillRunner, session_registry: ToolSessionRegistry, emitter: TraceEmitter).
- On construction, register the injected skill_runner in session_registry: session_registry.register("default", skill_runner). This ensures cleanup (S5) can close the runner via session_registry.close_all().
- Methods: run(task_description: str, tools: list[SkillManifest], session: SkillSession) -> AgentResult, step(history: list[Turn]) -> ToolCall | FinalAnswer.
- Emits trace event per step via injected TraceEmitter.

### S1.1 — Create ToolSessionRegistry in sovereignai/agent/tool_session.py
- Methods: register(tool_id: str, runner: ISkillRunner), close(tool_id: str), close_all().
- Stores dict[str, ISkillRunner]. close_all() iterates registered runners and calls runner.close() (optional, default no-op per ISkillRunner protocol).
- close(tool_id) closes the registered runner by ID; distinct from ISkillRunner.close() which closes the runner instance itself.
- Wire in main.py build_container() as singleton.

### S1.2 — Create agent types in sovereignai/agent/types.py
- AgentErrorObservation: Pydantic BaseModel with error_type: str, message: str, last_response: str | None, failure_reasons: list[str], retryable: bool = False.
- FinalAnswer: Pydantic BaseModel with content: str.
- AgentResult: Pydantic BaseModel with status: Literal["success", "error"], output: str | None, error: AgentErrorObservation | None, trace: list[str].

### S2 — Create structured prompt template in sovereignai/agent/prompts.py
- System prompt: THOUGHT / ACTION / OBSERVATION format.
- Tool definitions injected as compact schema summaries from SkillManifest.
- Uses the same trace emission described in S1 — no additional emit call per step.

### S3 — Create ReActConfig and TokenBudgetHistory in sovereignai/agent/history.py
- ReActConfig: Pydantic model in sovereignai/agent/config.py. Fields: max_context_tokens: int = 8192.
- TokenBudgetHistory: Compress conversation to fit token budget. Never exceed budget unless minimum pinned context cannot fit.
- to_messages(budget) guarantees at minimum the system prompt + task description + last 2 turns are preserved, even if that exceeds budget. If budget is below this minimum, log warning and use minimum.
- If pinned minimum exceeds adapter's advertised max_context_tokens (default 8192, configurable via ReActConfig), raise TokenBudgetExceededError immediately — do not call LLM. Comparison uses min(ReActConfig.max_context_tokens, adapter_reported_max_context_tokens) if adapter advertises a limit; otherwise uses config default. Error message: "Task description too large for model context window. Options: (1) reduce task scope, (2) set ReActConfig.max_context_tokens to a higher value (if model supports it), or (3) switch to a larger model."
- add_turn(role, content), to_messages(budget) methods.

### S4 — Create SingleCallStructuredOutput in sovereignai/agent/structured_output.py
- Pydantic model for LLM response: ToolCall | FinalAnswer.
- Validation with bounded retry (max 3). Error feedback injected into retry prompt.
- Retry temperature strategy: cooling, not heating. Attempt 1 at default temperature; attempts 2-3 at 0.1 and 0.0. Attempt 3 injects schema-reminder prefix into system prompt.
- After 3 consecutive validation failures, raise StructuredOutputExhaustedError containing the last raw LLM response and all failure reasons. Emits trace event via injected TraceEmitter before raising. ReActLoop catches this and produces AgentErrorObservation propagated to caller, not a crash.
- Works with any backend supporting structured output (Ollama, vLLM, llama.cpp).

### S5 — Integrate ReActLoop with ISkillRunner
- ReActLoop delegates tool execution to ISkillRunner via injected skill_runner.
- Converts SkillResult to Observation: Observation(role='tool', content=result.output, tool_call_id=...). If result.error is set, convert to ToolErrorObservation instead.
- ToolErrorObservation fed back as next observation.
- Safety bounds: max_iterations=50, max_consecutive_errors=5, max_execution_time=600s.
- On StructuredOutputExhaustedError: (1) close tool connections via ToolSessionRegistry.close_all(), (2) drain remaining queue (discard pending tool calls), (3) emit AgentErrorObservation and return. ReActLoop emits trace.react.structured_output_exhausted via injected TraceEmitter before cleanup.
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
- test_structured_output.py: validation + retry, max 3 attempts, exhausted retry returns typed error, cooling_temperature_strategy (verifies temp decreases, not increases).
- test_token_budget.py: budget enforcement, truncation order, task-description retention under truncation, budget_exceeded_error_on_impossible_minimum (verifies loop-level catch + AgentErrorObservation).
- test_agent_integration.py: end-to-end task with mock LLM.
- test_react_concurrency.py: two ReActLoop instances running concurrently with shared LLM backend (mock) do not interfere. Retry counters are per-instance. test_error_cleans_up_resources (verifies close → drain → emit order).
- test_agent_api.py: endpoint auth, task submission, SSE stream auth rejection.

### S9 — Wire in main.py build_container()
- Register ReActLoop in build_container() under capability name 'agent.react'.
- Inject ReActConfig, ToolSessionRegistry, ISkillRunner, TraceEmitter.
- Register in CapabilityGraph.

### S10 — Run /verify after each edit. Run /close.
