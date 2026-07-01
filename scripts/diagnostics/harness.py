from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sovereignai.main import build_container
from sovereignai.memory.trace_backend import TraceMemoryBackend
from sovereignai.memory.working_backend import WorkingMemoryBackend
from sovereignai.orchestrator.dispatcher import MessageDispatcher
from sovereignai.shared.trace_emitter import TraceEmitter

if TYPE_CHECKING:
    from sovereignai.shared.container import DIContainer


class HarnessResult:
    def __init__(self, stage: str, status: str, details: str):
        self.stage = stage
        self.status = status
        self.details = details

    def __str__(self) -> str:
        return f"[{self.status}] {self.stage} ({self.details})"


class DiagnosticHarness:
    def __init__(self) -> None:
        self._container: DIContainer | None = None
        self._trace: TraceEmitter | None = None
        self._correlation_id = str(uuid.uuid4())
        self._results: list[HarnessResult] = []

    def _log_result(self, stage: str, status: str, details: str) -> None:
        result = HarnessResult(stage, status, details)
        self._results.append(result)
        print(result)

    def run_all(self) -> list[HarnessResult]:
        self._stage1_start_ai_service()
        self._stage2_download_model()
        self._stage3_load_model_and_generate()
        self._stage4_test_memory_backends()
        self._stage5_test_message_dispatcher()
        self._stage6_test_trace_memory()
        return self._results

    def _stage1_start_ai_service(self) -> None:
        stage = "Stage 1: Start AI Service"
        try:
            from adapters.external.ollama_adapter.adapter import OllamaAdapter

            ollama = OllamaAdapter(trace=TraceEmitter())
            if ollama.health_check():
                self._log_result(stage, "PASS", "Ollama healthy")
                return
        except Exception:
            pass

        try:
            from adapters.external.llama_cpp_adapter.adapter import LlamaCppAdapter
            from sovereignai.shared.hardware_probe import HardwareProbe

            probe = HardwareProbe()
            llama = LlamaCppAdapter(
                trace=TraceEmitter(),
                hardware_probe=probe,
                model_path_resolver=lambda x: Path("models") / x,
                database_registry=None,  # type: ignore[arg-type]
            )
            health = llama.health_check()
            if health.healthy:
                self._log_result(stage, "PASS", f"LlamaCpp healthy: {health.detail}")
                return
            else:
                self._log_result(stage, "SKIP", f"LlamaCpp not healthy: {health.detail}")
                return
        except Exception as exc:
            self._log_result(stage, "FAIL", f"Both services unavailable: {exc}")

    def _stage2_download_model(self) -> None:
        stage = "Stage 2: Download Model"
        try:
            from adapters.external.ollama_adapter.adapter import OllamaAdapter

            ollama = OllamaAdapter(trace=TraceEmitter())
            if ollama.health_check():
                try:
                    import ollama as ollama_client

                    ollama_client.pull("tinyllama")
                    self._log_result(stage, "PASS", "Downloaded tinyllama via Ollama")
                    return
                except Exception as exc:
                    self._log_result(stage, "SKIP", f"Download failed: {exc}")
                    return
        except Exception:
            pass

        try:
            models_dir = Path("models")
            if models_dir.exists():
                gguf_files = list(models_dir.glob("**/*.gguf"))
                if gguf_files:
                    self._log_result(stage, "PASS", f"Found {len(gguf_files)} GGUF models")
                    return
            self._log_result(stage, "SKIP", "No GGUF models found in models/")
        except Exception as exc:
            self._log_result(stage, "FAIL", f"Model check failed: {exc}")

    def _stage3_load_model_and_generate(self) -> None:
        stage = "Stage 3: Load Model + Generate"
        try:
            from adapters.external.ollama_adapter.adapter import OllamaAdapter

            self._container = build_container(dev_mode=True)
            self._trace = self._container.retrieve(TraceEmitter)

            ollama = OllamaAdapter(trace=self._trace)
            if ollama.health_check():
                response = ollama.generate("What is 2+2?", model="tinyllama")
                if response and len(response) > 0:
                    self._log_result(stage, "PASS", f"Generated {len(response)} chars")
                    return
                else:
                    self._log_result(stage, "FAIL", "Empty response from Ollama")
                    return
        except Exception as exc:
            self._log_result(stage, "FAIL", f"Generation failed: {exc}")

    def _stage4_test_memory_backends(self) -> None:
        stage = "Stage 4: Test Memory Backends"
        try:
            if not self._container:
                self._container = build_container(dev_mode=True)
                self._trace = self._container.retrieve(TraceEmitter)

            working = self._container.retrieve(WorkingMemoryBackend)
            task_id = str(uuid.uuid4())

            working.store(
                data={"task_id": task_id, "key": "test_key", "value": "test_value"},
                metadata={"correlation_id": self._correlation_id},
            )

            results = working.query({"task_id": task_id, "key": "test_key"})
            if results and len(results) > 0:
                self._log_result(
                    stage, "PASS",
                    f"WorkingMemory: stored and retrieved {len(results)} records"
                )
            else:
                self._log_result(stage, "FAIL", "WorkingMemory query returned no results")
        except Exception as exc:
            self._log_result(stage, "FAIL", f"Memory backend test failed: {exc}")

    def _stage5_test_message_dispatcher(self) -> None:
        stage = "Stage 5: Test MessageDispatcher"
        try:
            if not self._container:
                self._container = build_container(dev_mode=True)
                self._trace = self._container.retrieve(TraceEmitter)

            dispatcher = self._container.retrieve(MessageDispatcher)
            if dispatcher:
                self._log_result(stage, "PASS", "MessageDispatcher instantiated")
            else:
                self._log_result(stage, "FAIL", "MessageDispatcher not found in container")
        except Exception as exc:
            self._log_result(stage, "FAIL", f"MessageDispatcher test failed: {exc}")

    def _stage6_test_trace_memory(self) -> None:
        stage = "Stage 6: Test Trace Memory"
        try:
            if not self._container:
                self._container = build_container(dev_mode=True)
                self._trace = self._container.retrieve(TraceEmitter)

            trace_backend = self._container.retrieve(TraceMemoryBackend)

            trace_backend.store(
                data={
                    "component": "harness",
                    "level": "info",
                    "message": "Test trace event",
                    "correlation_id": self._correlation_id,
                },
                metadata={"test": True},
            )

            self._log_result(stage, "PASS", "TraceMemory: stored test event")
        except Exception as exc:
            self._log_result(stage, "FAIL", f"Trace memory test failed: {exc}")
