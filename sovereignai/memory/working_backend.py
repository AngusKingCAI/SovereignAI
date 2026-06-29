"""Working memory backend for in-process task-scoped data.

Per OR87: Working memory is in-process only — no persistence to disk.
Cleanup is triggered when tasks reach terminal states (COMPLETE/FAILED).
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

if TYPE_CHECKING:
    pass


class WorkingMemoryBackend:
    """In-process backend for working memory — stores task-scoped transient data.

    Per OR87: Working memory is in-process only. No persistence to disk.
    Data is stored in memory and cleaned up when tasks reach terminal states.
    """

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a working memory backend with an in-memory data store.

        Args:
            trace: Trace emitter for logging operations and errors.
        """
        self._trace = trace
        # Map task_id -> list of working memory records
        self._store: dict[str, list[dict]] = {}

    def store(self, data: dict, metadata: dict | None = None) -> str:
        """Store a working memory record and return the generated record id.

        Args:
            data: Working memory fields. Must contain: task_id (str), key (str),
                value (any serializable type).
            metadata: Optional metadata dict (not used by working backend).

        Returns:
            The generated record id (UUID string).
        """
        record_id = str(uuid.uuid4())
        task_id = data["task_id"]
        key = data["key"]
        value = data["value"]

        if task_id not in self._store:
            self._store[task_id] = []

        record = {
            "id": record_id,
            "task_id": task_id,
            "key": key,
            "value": value,
        }
        self._store[task_id].append(record)

        self._trace.emit(
            component="working_memory",
            level=TraceLevel.DEBUG,
            message=f"Stored working memory record {record_id} for task {task_id}",
        )
        return record_id

    def query(self, query: dict) -> list[dict]:
        """Query working memory records matching the specified criteria and filters.

        Args:
            query: Query parameters. Supported keys:
                - task_id: Filter by task ID (str)
                - key: Filter by key name (str)

        Returns:
            List of matching working memory records.
        """
        results = []

        for task_id, records in self._store.items():
            if "task_id" in query and task_id != query["task_id"]:
                continue

            for record in records:
                if "key" in query and record.get("key") != query["key"]:
                    continue
                results.append(record)

        self._trace.emit(
            component="working_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} working memory records",
        )
        return results

    def delete(self, record_id: str) -> bool:
        """Delete a working memory record by its unique identifier string.

        Args:
            record_id: The id of the record to delete.

        Returns:
            True if the record was deleted, False if not found.
        """
        for task_id, records in self._store.items():
            for i, record in enumerate(records):
                if record.get("id") == record_id:
                    records.pop(i)
                    if not records:
                        del self._store[task_id]
                    self._trace.emit(
                        component="working_memory",
                        level=TraceLevel.DEBUG,
                        message=f"Deleted working memory record {record_id}",
                    )
                    return True
        return False

    def cleanup(self, task_id: str) -> None:
        """Remove all working memory records for a given task identifier.

        Called when a task reaches a terminal state (COMPLETE or FAILED).

        Args:
            task_id: The task ID to clean up.
        """
        if task_id in self._store:
            count = len(self._store[task_id])
            del self._store[task_id]
            self._trace.emit(
                component="working_memory",
                level=TraceLevel.DEBUG,
                message=f"Cleaned up {count} working memory records for task {task_id}",
            )
