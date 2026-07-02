from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    ComponentId,
    EpisodicQuery,
    ProceduralQuery,
    TraceLevel,
    TraceQuery,
    WorkingQuery,
)

if TYPE_CHECKING:
    pass


class Librarian:

    def __init__(
        self,
        capability_graph: ICapabilityIndex,
        trace: TraceEmitter,
    ) -> None:
        self._graph = capability_graph
        self._trace = trace

    def store(self, memory_type: str, data: dict, metadata: dict | None = None) -> str:
        from sovereignai.shared.types import NoActiveProviderError

        providers = self._route(memory_type, "memory_storage")
        if not providers:
            self._trace.emit(
                component="Librarian",
                level=TraceLevel.ERROR,
                message=f"No backend declares memory_storage for memory_type '{memory_type}'",
            )
            raise NoActiveProviderError(
                f"No backend declares memory_storage for memory_type '{memory_type}'"
            )

        # Route to highest-priority provider
        component_id = providers[0]
        # In a full implementation, we would retrieve the backend instance from the DI container
        # and call its store() method. For now, we return a placeholder record id.
        record_id = str(uuid.uuid4())
        self._trace.emit(
            component="Librarian",
            level=TraceLevel.DEBUG,
            message=f"Routed store for memory_type '{memory_type}' to backend {component_id}",
        )
        return record_id

    def query(
        self,
        memory_type: str,
        query: EpisodicQuery | ProceduralQuery | WorkingQuery | TraceQuery,
    ) -> list[dict]:
        from sovereignai.shared.types import NoActiveProviderError

        providers = self._route(memory_type, "memory_query")
        if not providers:
            self._trace.emit(
                component="Librarian",
                level=TraceLevel.ERROR,
                message=f"No backend declares memory_query for memory_type '{memory_type}'",
            )
            raise NoActiveProviderError(
                f"No backend declares memory_query for memory_type '{memory_type}'"
            )

        # Scatter-gather: query all backends and merge results
        all_results: list[dict] = []
        for component_id in providers:
            # In a full implementation, we would retrieve the backend instance from the DI container
            # and call its query() method with the typed query. For now, we return empty results.
            self._trace.emit(
                component="Librarian",
                level=TraceLevel.DEBUG,
                message=f"Queried backend {component_id} for memory_type '{memory_type}' with typed query",  # noqa: E501
            )

        # Apply merge semantics per memory type
        merged = self._merge_results(memory_type, all_results)
        return merged

    def delete(self, memory_type: str, record_id: str) -> bool:
        from sovereignai.shared.types import NoActiveProviderError

        providers = self._route(memory_type, "memory_storage")
        if not providers:
            self._trace.emit(
                component="Librarian",
                level=TraceLevel.ERROR,
                message=f"No backend declares memory_storage for memory_type '{memory_type}'",
            )
            raise NoActiveProviderError(
                f"No backend declares memory_storage for memory_type '{memory_type}'"
            )

        # Route to the backend that owns the record
        # In a full implementation, we would query backends to find which one owns the record
        component_id = providers[0]
        self._trace.emit(
            component="Librarian",
            level=TraceLevel.DEBUG,
            message=f"Routed delete for record {record_id} to backend {component_id}",
        )
        return True

    def _route(self, memory_type: str, capability: str) -> list[ComponentId]:
        # Map capability string to CapabilityCategory
        if capability == "memory_storage" or capability == "memory_query":
            category = CapabilityCategory.MEMORY
        else:
            return []

        # Query the graph for providers
        providers = self._graph.find_providers(category, memory_type)
        return [component_id for component_id, _ in providers]

    def _merge_results(self, memory_type: str, results: list[dict]) -> list[dict]:
        if memory_type == "working":
            # First-backend-wins: return first backend's results only
            return [results[0]] if results else []

        # Default merge: union, dedupe by id
        seen_ids = set()
        merged = []
        for result in results:
            if "id" in result:
                if result["id"] not in seen_ids:
                    seen_ids.add(result["id"])
                    merged.append(result)
            else:
                # No id field, include as-is
                merged.append(result)

        # Sort by timestamp for episodic and trace
        if memory_type in ("episodic", "trace"):
            merged.sort(key=lambda x: x.get("timestamp", 0))

        return merged
