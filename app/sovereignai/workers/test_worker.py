from __future__ import annotations

from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.shared.capability_graph import CapabilityGraph
from sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


class TestWorker:
    def __init__(
        self,
        working_memory: WorkingMemoryBackend,
        capability_graph: CapabilityGraph,
        trace: TraceEmitter,
    ) -> None:
        self._working_memory = working_memory
        self._capability_graph = capability_graph
        self._trace = trace
        self._trace.emit(
            component="TestWorker",
            level=TraceLevel.INFO,
            message="TestWorker initialized",
        )

    def process_task(self, task_id: str) -> str:
        prompt = self._working_memory.query({"task_id": task_id, "key": "prompt"})  # type: ignore
        if not prompt:
            self._trace.emit(
                component="TestWorker",
                level=TraceLevel.ERROR,
                message=f"No prompt found for task {task_id}",
            )
            return "error: no prompt"

        prompt_text = prompt[0]["value"]
        self._trace.emit(
            component="TestWorker",
            level=TraceLevel.INFO,
            message=f"Processing task {task_id} with prompt: {prompt_text[:50]}...",
        )

        try:
            adapters = self._capability_graph.adapters_by_capability("model_inference")
            if adapters:
                adapter_meta = adapters[0]
                adapter = self._capability_graph.get_adapter(adapter_meta.component_id)
                if adapter and hasattr(adapter, "generate"):
                    result = adapter.generate(prompt_text)
                    self._working_memory.store(
                        {"task_id": task_id, "key": "result", "value": result}
                    )
                    self._working_memory.store(
                        {"task_id": task_id, "key": "status", "value": "complete"}
                    )
                    self._trace.emit(
                        component="TestWorker",
                        level=TraceLevel.INFO,
                        message=f"Completed task {task_id}",
                    )
                    return str(result)
        except Exception as e:
            self._trace.emit(
                component="TestWorker",
                level=TraceLevel.ERROR,
                message=f"Failed to process task {task_id}: {e}",
            )
            self._working_memory.store(
                {"task_id": task_id, "key": "status", "value": "failed"}
            )

        return "error: no adapter available"
