from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import TraceLevel, WorkingQuery

if TYPE_CHECKING:
    pass


class WorkingMemoryBackend:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        # Map task_id -> list of working memory records
        self._store: dict[str, list[dict]] = {}

    def store(self, data: dict, metadata: dict | None = None) -> str:
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

    def query(self, query: WorkingQuery) -> list[dict]:
        results = []

        # Map context_id to task_id for compatibility
        for task_id, records in self._store.items():
            if task_id != query.context_id:
                continue

            for record in records:
                results.append(record)

        # Limit results to max_items
        if len(results) > query.max_items:
            results = results[:query.max_items]

        self._trace.emit(
            component="working_memory",
            level=TraceLevel.DEBUG,
            message=f"Query returned {len(results)} working memory records",
        )
        return results

    def delete(self, record_id: str) -> bool:
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
        if task_id in self._store:
            count = len(self._store[task_id])
            del self._store[task_id]
            self._trace.emit(
                component="working_memory",
                level=TraceLevel.DEBUG,
                message=f"Cleaned up {count} working memory records for task {task_id}",
            )
