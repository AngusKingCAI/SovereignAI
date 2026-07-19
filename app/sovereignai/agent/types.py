from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AgentErrorObservation:
    error_type: str
    message: str
    last_response: str | None = None
    failure_reasons: list[str] = field(default_factory=list)
    retryable: bool = False


@dataclass
class FinalAnswer:
    content: str


@dataclass
class AgentResult:
    status: Literal["success", "error"]
    output: str | None = None
    error: AgentErrorObservation | None = None
    trace: list[str] = field(default_factory=list)
