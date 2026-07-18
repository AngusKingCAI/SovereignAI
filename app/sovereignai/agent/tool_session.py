from __future__ import annotations

from typing import Any


class ToolSessionRegistry:
    """Registry for tool session tracking with sync close per P23-Claude-async-mismatch."""

    def __init__(self) -> None:
        self._sessions: dict[str, Any] = {}

    def register(self, tool_id: str, runner: Any) -> None:
        """Register a tool session. Raises ValueError if tool_id already
        registered with different runner.
        """
        if tool_id in self._sessions:
            existing_runner = self._sessions[tool_id]
            if existing_runner is not runner:
                raise ValueError(
                    f"Tool {tool_id} already registered with different runner. "
                    f"Existing: {existing_runner}, New: {runner}"
                )
            # Same pair: no-op
            return
        self._sessions[tool_id] = runner

    def close(self, tool_id: str) -> None:
        """Remove tool session entry. Does NOT call runner.close() (singleton).
        Idempotent. Sync method.
        """
        if tool_id in self._sessions:
            del self._sessions[tool_id]
        # Idempotent: no error if not found

    def close_all(self) -> None:
        """Close all tool sessions by iterating over a copy. Reserved for shutdown."""
        for tool_id in list(self._sessions.keys()):
            self.close(tool_id)
        self._sessions.clear()
