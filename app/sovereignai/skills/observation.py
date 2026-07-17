from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolCallErrorObservation:
    error_type: str
    message: str
    suggestion: str
    retryable: bool

    def to_prompt_str(self) -> str:
        return f"Error: {self.error_type} - {self.message}\nSuggestion: {self.suggestion}"
