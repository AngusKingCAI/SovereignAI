from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel


class StructuredOutputExhaustedError(Exception):

    def __init__(self, last_raw: str, failure_reasons: list[str]) -> None:
        self.last_raw = last_raw
        self.failure_reasons = failure_reasons
        super().__init__(
            f"Structured output extraction failed after 3 attempts. "
            f"Reasons: {failure_reasons}. Last raw: {last_raw[:200]}..."
        )


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


class FinalAnswer(BaseModel):
    content: str


class SingleCallStructuredOutput:

    def __init__(self, emitter: Any) -> None:
        self._emitter = emitter

    def extract(
        self,
        raw_response: str,
        schema_type: Literal["tool_call", "final_answer"],
    ) -> ToolCall | FinalAnswer:
        """Extract structured output from raw LLM response with bounded retry."""
        failure_reasons: list[str] = []

        # Attempt 1: default temperature
        try:
            return self._attempt_extraction(raw_response, schema_type)
        except Exception as e:
            failure_reasons.append(f"Attempt 1 (default temp): {e}")

        # Attempt 2: temperature 0.1
        try:
            return self._attempt_extraction(raw_response, schema_type, temperature=0.1)
        except Exception as e:
            failure_reasons.append(f"Attempt 2 (temp 0.1): {e}")

        # Attempt 3: temperature 0.0 + schema reminder
        try:
            return self._attempt_extraction(
                raw_response, schema_type, temperature=0.0, schema_reminder=True
            )
        except Exception as e:
            failure_reasons.append(f"Attempt 3 (temp 0.0 + schema): {e}")

        # All attempts failed - emit trace and raise
        from sovereignai.shared.types import TraceLevel

        self._emitter.emit_event(
            event_name="react.structured_output_exhausted",
            payload={
                "failure_reasons": failure_reasons,
                "last_raw_length": len(raw_response),
            },
            level=TraceLevel.ERROR,
        )

        raise StructuredOutputExhaustedError(
            last_raw=raw_response,
            failure_reasons=failure_reasons,
        )

    def _attempt_extraction(
        self,
        raw_response: str,
        schema_type: Literal["tool_call", "final_answer"],
        temperature: float = 0.7,
        schema_reminder: bool = False,
    ) -> ToolCall | FinalAnswer:
        """Attempt extraction with specified parameters."""
        # This is a placeholder - actual implementation would call LLM with temperature
        # and parse response according to schema
        if schema_type == "final_answer":
            if "final answer:" in raw_response.lower():
                content = raw_response.split("final answer:")[-1].strip()
                return FinalAnswer(content=content)
            raise ValueError("No FinalAnswer pattern found in response")
        else:
            # ToolCall extraction logic - more flexible pattern matching
            if "action:" in raw_response.lower():
                # Find the action line
                lines = raw_response.split("\n")
                action_line = None
                action_index = -1
                for i, line in enumerate(lines):
                    if "action:" in line.lower():
                        action_line = line.split(":", 1)[1].strip()
                        action_index = i
                        break

                if action_line and action_index >= 0:
                    # Try to parse name
                    parts = action_line.split(None, 1)  # Split on first whitespace
                    if parts:
                        name = parts[0].strip()
                        # Look for arguments in next lines
                        args = {}
                        if (
                            action_index + 1 < len(lines)
                            and "arguments:" in lines[action_index + 1].lower()
                        ):
                            args_line = lines[action_index + 1].split(":", 1)[1].strip()
                            # Simple JSON-like parsing
                            if args_line.startswith("{") and args_line.endswith("}"):
                                try:
                                    import json
                                    args = json.loads(args_line)
                                except json.JSONDecodeError:
                                    args = {"raw": args_line}
                        return ToolCall(name=name, arguments=args)
            raise ValueError("No ToolCall pattern found in response")
