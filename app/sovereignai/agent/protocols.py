from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class GraphMemory(Protocol):
    """Protocol for graph memory queries. Locked contract for Plan 24 TaskGraphCache."""

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        """Query graph memory for entity and related nodes up to specified depth."""
        ...
