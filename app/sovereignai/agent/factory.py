from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReActLoopFactory(Protocol):
    """Factory protocol for ReActLoop - acts as both factory and instance."""

    def run(self, task_description: str, tools: list[dict[str, Any]], session: Any,
            context: str | None = None, memory: Any | None = None) -> Any:
        """Run the ReAct loop with given parameters."""
        ...
