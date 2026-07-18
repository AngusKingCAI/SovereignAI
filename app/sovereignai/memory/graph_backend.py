"""Task graph cache using SQLite adjacency tables with recursive CTE queries.

This module provides a graph memory backend for per-task ephemeral storage
of entities and relations, using SQLite with recursive CTEs for graph traversal.
"""
from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class GraphMemory(Protocol):
    """Protocol for graph memory queries. Locked contract for Plan 24 TaskGraphCache."""

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        """Query graph memory for entity and related nodes up to specified depth."""
        ...


class TaskGraphCache(GraphMemory):
    """Per-task ephemeral graph memory using SQLite adjacency tables.

    This implements the GraphMemory protocol (P23-A) with a locked signature:
    query(entity_id: str, depth: int = 2) -> list[dict]

    Uses SQLite adjacency tables with recursive CTEs for graph traversal.
    Default :memory: mode for per-task ephemeral storage. File-backed mode
    available via db_path parameter for configurability.
    """

    def __init__(self, db_path: Path | str = ":memory:") -> None:
        """Initialize TaskGraphCache.

        Args:
            db_path: SQLite database path. Default :memory: for per-task ephemeral.
                     File-backed mode for configurability (caller supplies path).
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._closed = False
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize SQLite database with adjacency tables."""
        if self._closed:
            return

        self._connection = sqlite3.connect(self._db_path)
        self._connection.row_factory = sqlite3.Row

        # Create adjacency tables
        cursor = self._connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                attributes TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS relations (
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                relation TEXT NOT NULL,
                FOREIGN KEY (source) REFERENCES entities(id),
                FOREIGN KEY (target) REFERENCES entities(id)
            )
        """
        )

        # Create indexes for efficient querying
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target)"
        )

        self._connection.commit()

    def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        attributes: dict[str, Any] | None = None,
    ) -> None:
        """Add an entity to the graph.

        Args:
            entity_id: Unique identifier for the entity.
            entity_type: Type/category of the entity.
            attributes: Optional dictionary of entity attributes.
        """
        if self._closed or self._connection is None:
            return

        import json

        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO entities (id, type, attributes) VALUES (?, ?, ?)",
            (entity_id, entity_type, json.dumps(attributes) if attributes else None),
        )
        self._connection.commit()

    def add_relation(self, source: str, target: str, relation: str) -> None:
        """Add a relation between two entities.

        Args:
            source: Source entity ID.
            target: Target entity ID.
            relation: Type of relation.
        """
        if self._closed or self._connection is None:
            return

        cursor = self._connection.cursor()
        cursor.execute(
            "INSERT INTO relations (source, target, relation) VALUES (?, ?, ?)",
            (source, target, relation),
        )
        self._connection.commit()

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        """Query graph memory for entity and related nodes up to specified depth.

        Locked signature per P23-A contract. Uses recursive CTE for graph traversal.
        Return type list[dict] matches GraphMemory Protocol exactly.

        Args:
            entity_id: Starting entity ID for query.
            depth: Maximum traversal depth (default: 2).

        Returns:
            List of dicts containing entity information and relations.
        """
        if self._closed or self._connection is None:
            return []

        cursor = self._connection.cursor()

        # Use recursive CTE to traverse graph up to specified depth
        query = """
            WITH RECURSIVE graph_traversal AS (
                -- Base case: starting entity
                SELECT
                    e.id,
                    e.type,
                    e.attributes,
                    0 as depth_level,
                    NULL as relation,
                    NULL as source_id
                FROM entities e
                WHERE e.id = ?

                UNION ALL

                -- Recursive case: traverse relations
                SELECT
                    e.id,
                    e.type,
                    e.attributes,
                    gt.depth_level + 1,
                    r.relation,
                    r.source
                FROM relations r
                JOIN entities e ON r.target = e.id
                JOIN graph_traversal gt ON r.source = gt.id
                WHERE gt.depth_level < ?
            )
            SELECT * FROM graph_traversal
        """

        cursor.execute(query, (entity_id, depth))
        rows = cursor.fetchall()

        # Convert to list of dicts
        import json

        results = []
        for row in rows:
            attributes = None
            if row["attributes"]:
                with contextlib.suppress(json.JSONDecodeError):
                    attributes = json.loads(row["attributes"])

            results.append(
                {
                    "id": row["id"],
                    "type": row["type"],
                    "attributes": attributes,
                    "depth": row["depth_level"],
                    "relation": row["relation"],
                    "source_id": row["source_id"],
                }
            )

        return results

    def close(self) -> None:
        """Close SQLite connection. Idempotent via _closed flag (DD-24.11.2)."""
        if self._closed:
            return

        if self._connection is not None:
            self._connection.close()
            self._connection = None

        self._closed = True

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.close()
