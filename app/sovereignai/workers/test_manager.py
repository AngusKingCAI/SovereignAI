from __future__ import annotations

from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class TestManager:
    def __init__(self, working_memory: WorkingMemoryBackend, trace: TraceEmitter) -> None:
        self._working_memory = working_memory
        self._trace = trace
        self._trace.emit(
            component="TestManager",
            level=TraceLevel.INFO,
            message="TestManager initialized",
        )

    def receive_prompt(self, prompt: str) -> str:
        task_id = f"test-task-{hash(prompt)}"
        self._working_memory.store(
            {"task_id": task_id, "key": "prompt", "value": prompt}
        )
        self._working_memory.store(
            {"task_id": task_id, "key": "status", "value": "assigned"}
        )
        self._trace.emit(
            component="TestManager",
            level=TraceLevel.INFO,
            message=f"Received prompt, assigned task {task_id}",
        )
        return task_id

    def approve_result(self, task_id: str) -> bool:
        result = self._working_memory.query({"task_id": task_id, "key": "result"})
        if result:
            self._working_memory.store(
                {"task_id": task_id, "key": "status", "value": "approved"}
            )
            self._trace.emit(
                component="TestManager",
                level=TraceLevel.INFO,
                message=f"Approved result for task {task_id}",
            )
            return True
        return False

    def get_task_status(self, task_id: str) -> str:
        status = self._working_memory.query({"task_id": task_id, "key": "status"})
        if status:
            value = status[0]["value"]
            return str(value) if value is not None else "unknown"
        return "unknown"
