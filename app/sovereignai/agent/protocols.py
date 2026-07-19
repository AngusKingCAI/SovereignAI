from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class GraphMemory(Protocol):

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        ...
