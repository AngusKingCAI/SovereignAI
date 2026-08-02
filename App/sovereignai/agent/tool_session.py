from __future__ import annotations

from typing import Any


class ToolSessionRegistry:

    def __init__(self) -> None:
        self._sessions: dict[str, Any] = {}

    def register(self, tool_id: str, runner: Any) -> None:
        if tool_id in self._sessions:
            existing_runner = self._sessions[tool_id]
            if existing_runner is not runner:
                raise ValueError(
                    f"Tool {tool_id} already registered with different runner. "
                    f"Existing: {existing_runner}, New: {runner}"
                )
            return
        self._sessions[tool_id] = runner

    def close(self, tool_id: str) -> None:
        if tool_id in self._sessions:
            del self._sessions[tool_id]

    def close_all(self) -> None:
        for tool_id in list(self._sessions.keys()):
            self.close(tool_id)
        self._sessions.clear()
