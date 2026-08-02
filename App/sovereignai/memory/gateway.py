"""Memory gateway for unified access to memory backends.

This module provides MemoryGateway which is the sole owner of PersistentGraphMemory
and provides a unified interface for memory operations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    from sovereignai.memory.persistent_graph import PersistentGraphMemory


class MemoryGateway:
    """Gateway for unified access to memory backends.

    Sole owner of PersistentGraphMemory. Provides unified interface for
    memory operations with query caching and lifecycle management.
    """

    def __init__(
        self,
        persistent_graph: PersistentGraphMemory | None = None,
        trace: TraceEmitter | None = None,
    ) -> None:
        """Initialize MemoryGateway.

        Args:
            persistent_graph: PersistentGraphMemory instance (owned exclusively).
            trace: Trace emitter for logging.
        """
        self._persistent_graph = persistent_graph
        self._trace = trace or TraceEmitter()
        self._trace.emit(
            component="MemoryGateway",
            level=TraceLevel.DEBUG,
            message="MemoryGateway initialized",
        )

    async def load(self) -> None:
        """Load memory backends.

        Registered as non-critical startup hook in Plan 33's HookRegistry.
        Sets is_ready()=True on completion.
        """
        if self._persistent_graph is not None:
            await self._persistent_graph.load()
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.INFO,
                message="MemoryGateway loaded",
            )

    async def flush(self) -> None:
        """Flush memory backends.

        Registered as critical shutdown hook in Plan 33's HookRegistry.
        Sets is_ready()=False on completion.
        """
        if self._persistent_graph is not None:
            await self._persistent_graph.flush()
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.INFO,
                message="MemoryGateway flushed",
            )

    async def merge(self, task_id: str, entities: list[dict], dedup_key: str) -> None:
        """Merge entities into persistent graph memory.

        Args:
            task_id: Task identifier.
            entities: List of entity/relation dicts to merge.
            dedup_key: Deduplication key for event deduplication.
        """
        if self._persistent_graph is None:
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.WARN,
                message="PersistentGraphMemory not available, skipping merge",
            )
            return

        await self._persistent_graph.merge(task_id, entities, dedup_key)

    async def rollback(self, task_id: str) -> bool:
        """Rollback in-progress merge for a task.

        Args:
            task_id: Task identifier.

        Returns:
            True if rollback succeeded, False otherwise.
        """
        if self._persistent_graph is None:
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.WARN,
                message="PersistentGraphMemory not available, skipping rollback",
            )
            return False

        result = await self._persistent_graph.rollback(task_id)
        return result if result is not None else False

    async def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        """Query persistent graph memory.

        Args:
            entity_id: Starting entity ID.
            depth: Maximum traversal depth.

        Returns:
            List of entity/relation dicts.
        """
        if self._persistent_graph is None:
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.WARN,
                message="PersistentGraphMemory not available, returning empty results",
            )
            return []

        result = await self._persistent_graph.query(entity_id, depth)
        return result if result is not None else []

    async def get_conflicts(
        self, offset: int = 0, limit: int = 500
    ) -> list[dict]:
        """Get merge conflicts from persistent graph.

        Args:
            offset: Pagination offset.
            limit: Maximum number of results.

        Returns:
            List of conflict dicts.
        """
        if self._persistent_graph is None:
            self._trace.emit(
                component="MemoryGateway",
                level=TraceLevel.WARN,
                message="PersistentGraphMemory not available, returning empty conflicts",
            )
            return []

        result = await self._persistent_graph.get_conflicts(offset, limit)
        return result if result is not None else []

    def is_ready(self) -> bool:
        """Check if memory gateway is ready for operations."""
        if self._persistent_graph is None:
            return False
        return self._persistent_graph.is_ready() if self._persistent_graph is not None else False
