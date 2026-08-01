"""Persistent graph memory for cross-task knowledge storage.

This module provides PersistentGraphMemory which implements file-backed SQLite
storage for entities and relations shared across tasks, with entity deduplication,
merge strategies, and conflict tracking.
"""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

import aiosqlite

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    from sovereignai.options.schema import BehaviorSettings


class PersistentGraphMemory:
    """Cross-task persistent graph memory using SQLite.

    v1: single-process, single-asyncio-loop, aiosqlite (single connection,
    serialized by asyncio.Lock). Multi-process deferred to v2.

    Performance budget: p99 < 500ms at 100k entities / 500k relations.
    """

    def __init__(
        self,
        db_path: Path | str,
        trace: TraceEmitter,
        behavior_settings: BehaviorSettings | None = None,
    ) -> None:
        """Initialize PersistentGraphMemory.

        Args:
            db_path: SQLite database path for graph memory (separate file).
            trace: Trace emitter for logging.
            behavior_settings: Optional behavior settings for configuration.
        """
        self._db_path = db_path
        self._trace = trace
        self._behavior_settings = behavior_settings
        self._connection: aiosqlite.Connection | None = None
        self._lock = asyncio.Lock()
        self._creation_loop: asyncio.AbstractEventLoop | None = None
        self._active_task_id: str | None = None
        self._in_transaction: bool = False
        self._query_cache: dict[str, tuple[datetime, list[dict]]] = {}
        self._cache_ttl = 1.0  # 1 second TTL
        self._max_cache_entries = 100
        self._initialized = False
        self._trace.emit(
            component="PersistentGraphMemory",
            level=TraceLevel.DEBUG,
            message="PersistentGraphMemory initialized",
        )

    async def load(self) -> None:
        """Load and initialize the persistent graph memory.

        Creates database schema if needed. Sets is_ready()=True on completion.
        Registered as non-critical startup hook in Plan 33's HookRegistry.
        """
        if self._initialized:
            return

        # Capture creation loop for loop mismatch detection
        self._creation_loop = asyncio.get_running_loop()

        self._connection = await aiosqlite.connect(str(self._db_path))
        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA busy_timeout=5000")

        await self._initialize_schema()
        await self._create_indexes()

        self._initialized = True
        self._trace.emit(
            component="PersistentGraphMemory",
            level=TraceLevel.INFO,
            message=f"Persistent graph memory loaded from {self._db_path}",
        )

    async def _initialize_schema(self) -> None:
        """Initialize database schema for entities, relations, and conflicts."""
        if self._connection is None:
            return

        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                attributes TEXT,
                timestamp TEXT NOT NULL
            )
        """
        )

        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS relations (
                rowid INTEGER PRIMARY KEY AUTOINCREMENT,
                src_id TEXT NOT NULL,
                dst_id TEXT NOT NULL,
                type TEXT NOT NULL,
                attributes TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (src_id) REFERENCES entities(id),
                FOREIGN KEY (dst_id) REFERENCES entities(id)
            )
        """
        )

        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS merge_conflicts (
                conflict_id TEXT PRIMARY KEY,
                entity_name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                canonical_uuid TEXT NOT NULL,
                candidate_uuids TEXT NOT NULL,
                first_observed_at TEXT NOT NULL,
                resolution_status TEXT NOT NULL DEFAULT 'unresolved'
            )
        """
        )

        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS merge_dedup (
                task_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                dedup_key TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                PRIMARY KEY(task_id, event_type, dedup_key)
            )
        """
        )

        await self._connection.commit()

    async def _create_indexes(self) -> None:
        """Create indexes for efficient querying."""
        if self._connection is None:
            return

        # Entity indexes
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_type_name ON entities(type, name)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)"
        )

        # Relation indexes
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_src_type ON relations(src_id, type)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_dst_type ON relations(dst_id, type)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_relations_type ON relations(type)"
        )

        # Conflict indexes
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_conflicts_observed "
            "ON merge_conflicts(first_observed_at)"
        )

        # Dedup indexes
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_dedup_first_seen ON merge_dedup(first_seen_at)"
        )

        await self._connection.commit()

    async def merge(
        self, task_id: str, entities: list[dict], dedup_key: str
    ) -> None:
        """Merge entities and relations into persistent graph.

        Entity dedup by name+type match. On collision: store both candidate UUIDs
        in merge_conflicts table; newer timestamp wins for entity attributes.
        Canonical entity: UUID with newer timestamp.
        Tiebreaker: identical timestamps → lexicographically smaller UUID wins.

        Args:
            task_id: Task identifier for transaction tracking.
            entities: List of entity/relation dicts to merge.
            dedup_key: Deduplication key for event deduplication.
        """
        # Loop mismatch detection
        current_loop = asyncio.get_running_loop()
        if self._creation_loop is not None and current_loop != self._creation_loop:
            error_msg = (
                f"MemoryGateway created on loop {self._creation_loop}, "
                f"called from loop {current_loop}"
            )
            self._trace.emit(
                component="PersistentGraphMemory",
                level=TraceLevel.WARN,
                message=error_msg,
            )
            raise RuntimeError(error_msg)

        async with self._lock:
            self._active_task_id = task_id
            self._in_transaction = True

            try:
                # Check dedup
                await self._check_dedup(task_id, dedup_key)

                # Merge entities
                for entity in entities:
                    if "src_id" in entity and "dst_id" in entity:
                        # This is a relation
                        await self._merge_relation(entity, task_id)
                    else:
                        # This is an entity
                        await self._merge_entity(entity, task_id)

                # Insert dedup record
                await self._insert_dedup(task_id, dedup_key)

                # Invalidate cache
                self._invalidate_cache()

                if self._connection is not None:
                    await self._connection.commit()
            finally:
                self._active_task_id = None
                self._in_transaction = False

    async def _check_dedup(self, task_id: str, dedup_key: str) -> None:
        """Check if event has already been processed."""
        if self._connection is None:
            return

        cursor = await self._connection.execute(
            """
            SELECT first_seen_at FROM merge_dedup
            WHERE task_id = ? AND dedup_key = ?
        """,
            (task_id, dedup_key),
        )
        row = await cursor.fetchone()

        if row is not None:
            # Event already processed, skip merge
            self._trace.emit(
                component="PersistentGraphMemory",
                level=TraceLevel.DEBUG,
                message=f"Skipping duplicate event for task {task_id} with dedup_key {dedup_key}",
            )
            raise RuntimeError(f"Duplicate event: {dedup_key}")

    async def _insert_dedup(self, task_id: str, dedup_key: str) -> None:
        """Insert dedup record after successful merge."""
        if self._connection is None:
            return

        now = datetime.now(UTC).isoformat()
        await self._connection.execute(
            """
            INSERT OR REPLACE INTO merge_dedup (task_id, event_type, dedup_key, first_seen_at)
            VALUES (?, 'task.completed', ?, ?)
        """,
            (task_id, dedup_key, now),
        )

    async def _merge_entity(self, entity: dict, task_id: str) -> None:
        """Merge a single entity with deduplication."""
        if self._connection is None:
            return

        entity_id = entity.get("id")
        entity_type = entity.get("type")
        entity_name = entity.get("name", "")
        attributes = json.dumps(entity.get("attributes", {}))
        timestamp = datetime.now(UTC).isoformat()

        # Check for existing entity with same name+type
        cursor = await self._connection.execute(
            """
            SELECT id, timestamp FROM entities
            WHERE type = ? AND name = ?
        """,
            (entity_type, entity_name),
        )
        existing = await cursor.fetchone()

        if existing is None:
            # No collision, insert new entity
            await self._connection.execute(
                """
                INSERT INTO entities (id, type, name, attributes, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """,
                (entity_id, entity_type, entity_name, attributes, timestamp),
            )
        else:
            # Collision detected
            existing_id = existing[0] if existing[0] is not None else ""
            existing_timestamp = existing[1] if existing[1] is not None else ""
            
            # Ensure all arguments are strings for _determine_canonical
            safe_entity_id = entity_id if entity_id is not None else ""
            safe_existing_id = existing_id if existing_id is not None else ""
            safe_timestamp = timestamp if timestamp is not None else ""
            safe_existing_timestamp = existing_timestamp if existing_timestamp is not None else ""
            
            canonical_id = self._determine_canonical(
                safe_entity_id, safe_existing_id, safe_timestamp, safe_existing_timestamp
            )

            # Update or insert canonical entity
            if canonical_id == entity_id:
                # New entity is canonical, update attributes
                await self._connection.execute(
                    """
                    UPDATE entities SET attributes = ?, timestamp = ?
                    WHERE id = ?
                """,
                    (attributes, timestamp, canonical_id),
                )
            else:
                # Existing entity is canonical, keep its attributes
                pass

            # Record conflict
            await self._record_conflict(
                entity_name if entity_name is not None else "",
                entity_type if entity_type is not None else "",
                canonical_id,
                entity_id if entity_id is not None else "",
                existing_id if existing_id is not None else "",
            )

            # Retain non-canonical entity in entities table (v1 limitation)
            if canonical_id != entity_id:
                # Insert/update non-canonical entity with original timestamp
                await self._connection.execute(
                    """
                    INSERT OR REPLACE INTO entities (id, type, name, attributes, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (entity_id, entity_type, entity_name, attributes, timestamp),
                )

    async def _merge_relation(self, relation: dict, task_id: str) -> None:
        """Merge a single relation with reattachment to canonical entities."""
        if self._connection is None:
            return

        src_id = relation.get("src_id")
        dst_id = relation.get("dst_id")
        relation_type = relation.get("type")
        attributes = json.dumps(relation.get("attributes", {}))
        timestamp = datetime.now(UTC).isoformat()

        # Get canonical UUIDs for src and dst
        canonical_src = await self._get_canonical_uuid(src_id if src_id else "")
        canonical_dst = await self._get_canonical_uuid(dst_id if dst_id else "")

        # Insert relation with canonical UUIDs
        await self._connection.execute(
            """
            INSERT INTO relations (src_id, dst_id, type, attributes, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (canonical_src, canonical_dst, relation_type, attributes, timestamp),
        )

    async def _get_canonical_uuid(self, entity_id: str) -> str:
        """Get canonical UUID for an entity ID."""
        if self._connection is None:
            return entity_id

        cursor = await self._connection.execute(
            "SELECT type, name FROM entities WHERE id = ?", (entity_id,)
        )
        row = await cursor.fetchone()

        if row is None:
            return entity_id

        entity_type = row[0] if row[0] is not None else ""
        entity_name = row[1] if row[1] is not None else ""

        # Find canonical entity for this name+type
        cursor = await self._connection.execute(
            """
            SELECT id, timestamp FROM entities
            WHERE type = ? AND name = ?
            ORDER BY timestamp DESC, id ASC
            LIMIT 1
        """,
            (entity_type, entity_name),
        )
        canonical_row = await cursor.fetchone()

        if canonical_row is None:
            return entity_id

        canonical_id = canonical_row[0] if canonical_row[0] is not None else ""
        return canonical_id if canonical_id else entity_id

    def _determine_canonical(
        self, new_id: str, existing_id: str, new_timestamp: str, existing_timestamp: str
    ) -> str:
        """Determine canonical UUID based on timestamp and tiebreaker."""
        if new_timestamp > existing_timestamp:
            return new_id
        elif new_timestamp < existing_timestamp:
            return existing_id
        else:
            # Identical timestamps, use lexicographically smaller UUID
            return min(new_id, existing_id) if new_id and existing_id else new_id or existing_id

    async def _record_conflict(
        self,
        entity_name: str,
        entity_type: str,
        canonical_id: str,
        *candidate_ids: str,
    ) -> None:
        """Record merge conflict in conflicts table."""
        if self._connection is None:
            return

        # Use entity name+type as conflict ID for deduplication
        conflict_id = hashlib.sha256(
            f"{entity_type}:{entity_name}".encode()
        ).hexdigest()

        # Include all candidates including canonical
        all_candidates = list(candidate_ids) + [canonical_id]
        candidate_uuids_json = json.dumps(list(set(all_candidates)))
        now = datetime.now(UTC).isoformat()

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO merge_conflicts
            (conflict_id, entity_name, entity_type, canonical_uuid,
             candidate_uuids, first_observed_at, resolution_status)
            VALUES (?, ?, ?, ?, ?, ?, 'unresolved')
        """,
            (
                conflict_id,
                entity_name,
                entity_type,
                canonical_id,
                candidate_uuids_json,
                now,
            ),
        )

    async def rollback(self, task_id: str) -> bool:
        """Rollback in-progress merge for a task.

        Returns True if merge was in-progress and rolled back.
        Returns False if already committed or no transaction.

        v1 limitation: cannot interrupt an in-progress merge() holding the asyncio.Lock.
        Waits for merge completion, then returns False (committed).
        """
        async with self._lock:
            if self._active_task_id == task_id and self._in_transaction:
                # Rollback the transaction
                if self._connection is not None:
                    await self._connection.rollback()
                self._active_task_id = None
                self._in_transaction = False
                self._trace.emit(
                    component="PersistentGraphMemory",
                    level=TraceLevel.INFO,
                    message=f"Rolled back merge for task {task_id}",
                )
                return True
            else:
                # No in-progress transaction for this task
                self._trace.emit(
                    component="PersistentGraphMemory",
                    level=TraceLevel.WARN,
                    message=(
                        f"Rollback for task {task_id} returned False "
                        "(merge already committed or no transaction)"
                    ),
                )
                return False

    async def query(
        self, entity_id: str, depth: int = 2, use_cache: bool = True
    ) -> list[dict]:
        """Query graph memory for entity and related nodes up to specified depth.

        Args:
            entity_id: Starting entity ID for query.
            depth: Maximum traversal depth (default: 2).
            use_cache: Whether to use query cache (default: True).

        Returns:
            List of dicts containing entity information and relations.
        """
        # Generate cache key
        cache_key = self._generate_cache_key("query", {"entity_id": entity_id, "depth": depth})

        # Check cache
        if use_cache:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

        if self._connection is None:
            return []

        # Execute query
        cursor = await self._connection.execute(
            """
            WITH RECURSIVE graph_traversal AS (
                -- Base case: starting entity
                SELECT
                    e.id,
                    e.type,
                    e.name,
                    e.attributes,
                    0 as depth_level,
                    NULL as relation_type,
                    NULL as source_id
                FROM entities e
                WHERE e.id = ?

                UNION ALL

                -- Recursive case: traverse relations
                SELECT
                    e.id,
                    e.type,
                    e.name,
                    e.attributes,
                    gt.depth_level + 1,
                    r.type as relation_type,
                    r.src_id as source_id
                FROM relations r
                JOIN entities e ON r.dst_id = e.id
                JOIN graph_traversal gt ON r.src_id = gt.id
                WHERE gt.depth_level < ?
            )
            SELECT * FROM graph_traversal
        """,
            (entity_id, depth),
        )

        rows = await cursor.fetchall()

        # Convert to list of dicts
        results = []
        for row in rows:
            attributes = None
            if row[3]:
                with contextlib.suppress(json.JSONDecodeError):
                    attributes = json.loads(row[3])

            results.append(
                {
                    "id": row[0],
                    "type": row[1],
                    "name": row[2],
                    "attributes": attributes,
                    "depth": row[4],
                    "relation_type": row[5],
                    "source_id": row[6],
                }
            )

        # Cache result
        if use_cache:
            self._add_to_cache(cache_key, results)

        return results

    def _generate_cache_key(self, query_type: str, params: dict) -> str:
        """Generate cache key from query type and parameters."""
        key_data = json.dumps([query_type, *sorted(params.items())], sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> list[dict] | None:
        """Get result from cache if still valid."""
        if cache_key not in self._query_cache:
            return None

        timestamp, result = self._query_cache[cache_key]
        age = (datetime.now(UTC) - timestamp).total_seconds()

        if age > self._cache_ttl:
            del self._query_cache[cache_key]
            return None

        return result

    def _add_to_cache(self, cache_key: str, result: list[dict]) -> None:
        """Add result to cache with eviction if needed."""
        # Evict oldest entries if cache is full
        if len(self._query_cache) >= self._max_cache_entries:
            oldest_key = min(self._query_cache.keys(), key=lambda k: self._query_cache[k][0])
            del self._query_cache[oldest_key]

        self._query_cache[cache_key] = (datetime.now(UTC), result)

    def _invalidate_cache(self) -> None:
        """Invalidate entire cache after write operations."""
        self._query_cache.clear()

    async def get_conflicts(
        self, offset: int = 0, limit: int = 500
    ) -> list[dict]:
        """Get merge conflicts sorted by first_observed_at descending.

        Args:
            offset: Pagination offset.
            limit: Maximum number of results (max 500).

        Returns:
            List of conflict dicts.
        """
        if self._connection is None:
            return []

        limit = min(limit, 500)

        cursor = await self._connection.execute(
            """
            SELECT
                conflict_id,
                entity_name,
                entity_type,
                canonical_uuid,
                candidate_uuids,
                first_observed_at,
                resolution_status
            FROM merge_conflicts
            ORDER BY first_observed_at DESC
            LIMIT ? OFFSET ?
        """,
            (limit, offset),
        )

        rows = await cursor.fetchall()

        results = []
        for row in rows:
            candidate_uuids = json.loads(row[4]) if row[4] else []
            results.append(
                {
                    "conflict_id": row[0],
                    "entity_name": row[1],
                    "entity_type": row[2],
                    "canonical_uuid": row[3],
                    "candidate_uuids": candidate_uuids,
                    "first_observed_at": row[5],
                    "resolution_status": row[6],
                }
            )

        return results

    async def flush(self) -> None:
        """Flush pending writes and close connection.

        Registered as critical shutdown hook in Plan 33's HookRegistry.
        Sets is_ready()=False on completion.
        """
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

        self._initialized = False
        self._trace.emit(
            component="PersistentGraphMemory",
            level=TraceLevel.INFO,
            message="Persistent graph memory flushed",
        )

    def is_ready(self) -> bool:
        """Check if persistent graph memory is ready for operations."""
        return self._initialized and self._connection is not None
