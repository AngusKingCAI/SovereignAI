from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AgentErrorObservation:
    """Error observation from agent execution."""
    error_type: str
    message: str
    last_response: str | None = None
    failure_reasons: list[str] = field(default_factory=list)
    retryable: bool = False


@dataclass
class FinalAnswer:
    """Final answer from agent reasoning."""
    content: str


@dataclass
class AgentResult:
    """Result of agent execution."""
    status: Literal["success", "error"]
    output: str | None = None
    error: AgentErrorObservation | None = None
    trace: list[str] = field(default_factory=list)
