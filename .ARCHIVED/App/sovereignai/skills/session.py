from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class Turn:
    role: str
    content: str
    timestamp: datetime


class SkillSession:
    def __init__(self) -> None:
        self._state: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[Turn]] = {}

    def get(self, correlation_id: str, key: str) -> Any:
        if correlation_id not in self._state:
            return None
        return self._state[correlation_id].get(key)

    def set(
        self,
        correlation_id: str,
        key: str,
        value: str | int | float | bool | list[str] | dict[str, str],
    ) -> None:
        if correlation_id not in self._state:
            self._state[correlation_id] = {}
        self._state[correlation_id][key] = value

    def get_history(self, correlation_id: str) -> list[Turn]:
        return self._history.get(correlation_id, [])

    def add_turn(self, correlation_id: str, role: str, content: str) -> None:
        if correlation_id not in self._history:
            self._history[correlation_id] = []
        self._history[correlation_id].append(
            Turn(role=role, content=content, timestamp=datetime.now(UTC))
        )
