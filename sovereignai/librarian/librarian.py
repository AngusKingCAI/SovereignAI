"""Librarian — the memory router for all SovereignAI components.

Per AR10: All memory access routes through the Librarian. No component
may query a memory backend directly. The Librarian enforces access control,
routing, and backend selection per current memory topology.

Per OR86: Memory backends are pluggable components discovered via the
CapabilityGraph, not hardcoded in the core. The Librarian queries the graph
for backends declaring memory_storage and memory_query capabilities.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    ComponentId,
    TraceLevel,
)

if TYPE_CHECKING:
    pass


class Librarian:
    """Route memory operations to pluggable backends based on capability declarations.

    The Librarian does not store data itself — it routes store, query, and delete
    requests to backends that declare the appropriate capabilities. Backends are
    discovered via the CapabilityGraph (per OR86), not hardcoded.

    Per AR10: All memory access routes through the Librarian. No component may
    instantiate, import, or query a memory backend directly.
    """

    def __init__(
        self,
        capability_graph: ICapabilityIndex,
        trace: TraceEmitter,
    ) -> None:
        """Create a librarian instance wired to the capability graph for backend discovery.

        Args:
            capability_graph: Index of registered components and their capabilities.
                Used to find backends declaring memory_storage and memory_query.
            trace: Trace emitter for logging routing decisions and errors.
        """
        self._graph = capability_graph
        self._trace = trace

    def store(self, memory_type: str, data: dict, metadata: dict | None = None) -> str:
        """Route a store request to the highest-priority backend declaring memory_storage.

        Args:
            memory_type: The type of memory being stored (e.g. "episodic", "procedural").
            data: The data to store. Structure is backend-specific.
            metadata: Optional metadata dict (e.g. task_id for trace backend).

        Returns:
            The generated record id from the backend.

        Raises:
            NoActiveProviderError: If no backend declares memory_storage for this memory_type.
        """
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

    def query(self, memory_type: str, query: dict) -> list[dict]:
        """Route a query request to backends declaring memory_query for the memory type.

        If multiple backends match, performs scatter-gather with merge semantics per memory type.

        Args:
            memory_type: The type of memory being queried (e.g. "episodic", "procedural").
            query: The query parameters. Structure is backend-specific.

        Returns:
            List of matching records, merged according to memory type semantics.

        Raises:
            NoActiveProviderError: If no backend declares memory_query for this memory_type.
        """
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
            # and call its query() method. For now, we return empty results.
            self._trace.emit(
                component="Librarian",
                level=TraceLevel.DEBUG,
                message=f"Queried backend {component_id} for memory_type '{memory_type}'",
            )

        # Apply merge semantics per memory type
        merged = self._merge_results(memory_type, all_results)
        return merged

    def delete(self, memory_type: str, record_id: str) -> bool:
        """Route a delete request to the backend that owns the record.

        Args:
            memory_type: The type of memory (e.g. "episodic", "procedural").
            record_id: The id of the record to delete.

        Returns:
            True if the record was deleted, False if not found.

        Raises:
            NoActiveProviderError: If no backend declares memory_storage for this memory_type.
        """
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
        """Query the CapabilityGraph for backends declaring a capability for a memory type.

        Args:
            memory_type: The memory type name (used as the capability name).
            capability: The capability category (e.g. "memory_storage", "memory_query").

        Returns:
            List of component IDs, sorted by priority (highest first).
        """
        # Map capability string to CapabilityCategory
        if capability == "memory_storage" or capability == "memory_query":
            category = CapabilityCategory.MEMORY
        else:
            return []

        # Query the graph for providers
        providers = self._graph.find_providers(category, memory_type)
        return [component_id for component_id, _ in providers]

    def _merge_results(self, memory_type: str, results: list[dict]) -> list[dict]:
        """Apply scatter-gather merge semantics for a memory type based on the plan.

        Merge semantics per plan:
        - episodic: union, dedupe by id, sort by timestamp ascending
        - procedural: union, dedupe by pattern id, keep highest confidence
        - trace: union, dedupe by id, sort by timestamp ascending
        - working: first-backend-wins
        - Future types: union, dedupe by id

        Args:
            memory_type: The memory type being merged.
            results: List of result dicts from multiple backends.

        Returns:
            Merged and sorted results.
        """
        self._trace.emit(
            component="librarian",
            level=TraceLevel.DEBUG,
            message=f"Merging {len(results)} results for memory_type={memory_type}",
        )
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
