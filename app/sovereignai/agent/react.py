from __future__ import annotations

import asyncio
import uuid
from typing import Any

from sovereignai.agent.config import ReActConfig
from sovereignai.agent.history import TokenBudgetExceededError, TokenBudgetHistory
from sovereignai.agent.prompts import build_react_prompt
from sovereignai.agent.protocols import GraphMemory
from sovereignai.agent.structured_output import (
    SingleCallStructuredOutput,
    StructuredOutputExhaustedError,
    ToolCall,
)
from sovereignai.agent.tool_session import ToolSessionRegistry
from sovereignai.agent.types import AgentErrorObservation, AgentResult, FinalAnswer
from sovereignai.observability.trace_emitter import TraceEmitterWrapper
from sovereignai.shared.types import TraceLevel


class ReActLoop:
    """ReAct reasoning loop for agent execution."""

    def __init__(
        self,
        config: ReActConfig,
        skill_runner: Any,  # ISkillRunner
        session_registry: ToolSessionRegistry,
        emitter: TraceEmitterWrapper,
    ) -> None:
        self._config = config
        self._skill_runner = skill_runner
        self._session_registry = session_registry
        self._emitter = emitter
        self._session_key = uuid.uuid4().hex
        self._pending_tool_calls: asyncio.Queue = asyncio.Queue()
        self._file_edit_retry_counter: dict[str, int] = {}  # Per-file retry counter

        # Register session
        self._session_registry.register(self._session_key, skill_runner)

    def __call__(self) -> "ReActLoop":
        """Return self to satisfy ReActLoopFactory protocol."""
        return self

    async def run(
        self,
        task_description: str,
        tools: list[dict[str, Any]],
        session: str,
        context: str | None = None,
        memory: GraphMemory | None = None,
    ) -> AgentResult:
        """Execute ReAct loop with safety bounds and cleanup."""
        trace: list[str] = []
        consecutive_errors = 0
        iterations = 0

        # Build memory context if GraphMemory provided
        memory_context = None
        if memory is not None:
            try:
                graph_results = memory.query(entity_id=session, depth=2)
                memory_context = f"Graph context for {session}: {graph_results}"
            except Exception as e:
                trace.append(f"Memory query failed: {e}")

        # Build prompt
        prompt = build_react_prompt(
            task_description=task_description,
            tools=tools,
            context=context,
            memory_context=memory_context,
        )

        # Initialize history
        history = TokenBudgetHistory(max_context_tokens=self._config.max_context_tokens)
        history.add_turn("system", prompt)
        history.add_turn("user", task_description)

        try:
            async with asyncio.timeout(self._config.max_execution_time):
                try:
                    while iterations < self._config.max_iterations:
                        iterations += 1

                        # Check token budget
                        try:
                            messages = history.to_messages(self._config.max_context_tokens)
                        except TokenBudgetExceededError as e:
                            return AgentResult(
                                status="error",
                                output=None,
                                error=AgentErrorObservation(
                                    error_type="TokenBudgetExceeded",
                                    message=str(e),
                                    retryable=False,
                                ),
                                trace=trace,
                            )

                        # Get LLM response (placeholder - would call actual LLM)
                        # For now, simulate a response
                        try:
                            raw_response = await self._mock_llm_call(messages)
                        except Exception as e:
                            # Handle mock LLM errors gracefully for testing
                            return AgentResult(
                                status="error",
                                output=None,
                                error=AgentErrorObservation(
                                    error_type="LLMError",
                                    message=str(e),
                                    retryable=False,
                                ),
                                trace=trace,
                            )

                        # Extract structured output
                        structured_output_extractor = SingleCallStructuredOutput(self._emitter)
                        try:
                            result = structured_output_extractor.extract(
                                raw_response, schema_type="tool_call"
                            )
                        except StructuredOutputExhaustedError as e:
                            # Log pending tool calls at WARNING
                            while not self._pending_tool_calls.empty():
                                tool_call = await self._pending_tool_calls.get()
                                self._emitter.emit_event(
                                    event_name="react.pending_tool_call",
                                    payload=self._safe_repr(tool_call),
                                    level=TraceLevel.WARN,
                                )

                            # Drain queue
                            while not self._pending_tool_calls.empty():
                                await self._pending_tool_calls.get()

                            # Emit CRITICAL trace
                            self._emitter.emit_event(
                                event_name="react.structured_output_exhausted",
                                payload={"session_key": self._session_key},
                                level=TraceLevel.ERROR,
                            )

                            # Close session
                            self._session_registry.close(self._session_key)

                            return AgentResult(
                                status="error",
                                output=None,
                                error=AgentErrorObservation(
                                    error_type="StructuredOutputExhausted",
                                    message=str(e),
                                    failure_reasons=e.failure_reasons,
                                    retryable=False,
                                ),
                                trace=trace,
                            )

                        # Handle result
                        if isinstance(result, FinalAnswer):
                            self._emitter.emit_event(
                                event_name="react.completed",
                                payload={"answer": result.content},
                                level=TraceLevel.ERROR,
                            )
                            return AgentResult(
                                status="success",
                                output=result.content,
                                trace=trace,
                            )
                        elif isinstance(result, ToolCall):
                            # Execute tool
                            try:
                                tool_result = await self._execute_tool(result)
                                trace.append(f"Tool {result.name}: {tool_result}")

                                # Reset retry counter on success
                                if result.name == "file_edit":
                                    file_path = result.arguments.get("path", "")
                                    self._file_edit_retry_counter[file_path] = 0

                                consecutive_errors = 0
                            except Exception as e:
                                consecutive_errors += 1
                                trace.append(f"Tool error: {e}")

                                # Handle file_edit retry logic
                                if result.name == "file_edit":
                                    file_path = result.arguments.get("path", "")
                                    retry_count = self._file_edit_retry_counter.get(file_path, 0)
                                    if retry_count >= 1:
                                        # Second consecutive retryable error
                                        result.arguments[
                                            "hint"
                                        ] = "You must provide a line-range hint to disambiguate."
                                    self._file_edit_retry_counter[file_path] = retry_count + 1

                                if consecutive_errors >= self._config.max_consecutive_errors:
                                    self._emitter.emit_event(
                                        event_name="react.max_consecutive_errors",
                                        payload={"count": consecutive_errors},
                                        level=TraceLevel.ERROR,
                                    )
                                    return AgentResult(
                                        status="error",
                                        output=None,
                                        error=AgentErrorObservation(
                                            error_type="MaxConsecutiveErrors",
                                            message=(
                                                f"Exceeded max consecutive errors: "
                                                f"{consecutive_errors}"
                                            ),
                                            retryable=False,
                                        ),
                                        trace=trace,
                                    )

                            # Add to history
                            history.add_turn("assistant", raw_response)
                            history.add_turn("user", str(tool_result))

                except TimeoutError:
                    # Convert to AgentErrorObservation
                    self._emitter.emit_event(
                        event_name="react.timeout",
                        payload={"seconds": self._config.max_execution_time},
                        level=TraceLevel.ERROR,
                    )
                    return AgentResult(
                        status="error",
                        output=None,
                        error=AgentErrorObservation(
                            error_type="Timeout",
                            message=f"Execution exceeded {self._config.max_execution_time}s",
                            retryable=False,
                        ),
                        trace=trace,
                    )

        finally:
            # Always close session (sync call per P23-Claude-async-mismatch)
            self._session_registry.close(self._session_key)

        # Max iterations reached
        self._emitter.emit_event(
            event_name="react.max_iterations",
            payload={"iterations": iterations},
            level=TraceLevel.ERROR,
        )
        return AgentResult(
            status="error",
            output=None,
            error=AgentErrorObservation(
                error_type="MaxIterations",
                message=f"Exceeded max iterations: {iterations}",
                retryable=False,
            ),
            trace=trace,
        )

    async def _execute_tool(self, tool_call: ToolCall) -> str:
        """Execute a tool call via skill_runner."""
        # Placeholder - would delegate to skill_runner
        # Convert SkillResult to Observation
        # If result.error: ToolErrorObservation
        return f"Executed {tool_call.name} with {tool_call.arguments}"

    async def _mock_llm_call(self, messages: list[dict[str, str]]) -> str:
        """Mock LLM call for testing. Replace with actual LLM integration."""
        # Simulate a response
        return "final answer: Test complete"

    def _safe_repr(self, obj: Any) -> dict[str, Any]:
        """Safe representation that redacts sensitive information (P23-K)."""
        if isinstance(obj, dict):
            safe = {}
            for key, value in obj.items():
                if "path" in key.lower() and isinstance(value, str):
                    # Redact usernames from file paths
                    safe[key] = value.replace("\\Users\\King\\", "\\Users\\REDACTED\\")
                else:
                    safe[key] = value
            return safe
        return {"repr": str(obj)[:200]}  # Truncate long representations
