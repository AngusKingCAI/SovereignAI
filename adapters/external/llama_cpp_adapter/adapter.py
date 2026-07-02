from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from databases.base import ModelNotFoundError
from sovereignai.shared.quant_priority import select_best_quant
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import AdapterHealth, AdapterUnavailableError, TraceLevel

if TYPE_CHECKING:
    from sovereignai.shared.database_registry import DatabaseRegistry
    from sovereignai.shared.hardware_probe import HardwareProbe


class GenerationTimeoutError(Exception):
    pass


class LlamaCppAdapter:
    def __init__(
        self,
        trace: TraceEmitter,
        hardware_probe: HardwareProbe,
        model_path_resolver: Callable[[str], Path],
        database_registry: DatabaseRegistry,
        requested_n_gpu_layers: int = 0,
    ) -> None:
        self._trace = trace
        self._hardware_probe = hardware_probe
        self._model_path_resolver = model_path_resolver
        self._database_registry = database_registry
        self._requested_n_gpu_layers = requested_n_gpu_layers
        self._llm: Any = None
        self._loaded_model_id: str | None = None

    def load_model(self, model_id: str) -> None:
        if self._llm is not None and self._loaded_model_id == model_id:
            return

        if self._llm is not None:
            del self._llm
            self._llm = None
            self._loaded_model_id = None
            import gc

            gc.collect()

        match = self._database_registry.find_model(model_id)
        if match is None:
            self._trace.emit(
                component="llama_cpp_adapter",
                level=TraceLevel.ERROR,
                message=f"Unknown model_id: {model_id}",
            )
            raise ModelNotFoundError(model_id)

        _, model = match

        model_dir = self._model_path_resolver(model_id)

        model_info_path = model_dir / "model_info.json"
        gguf_path: Path | None = None

        import json

        try:
            with model_info_path.open() as f:
                model_info = json.load(f)

            if (
                model_info.get("model_id") == model_id
                and model_info.get("filename", "").endswith(".gguf")
            ):
                gguf_path = model_dir / model_info["filename"]
            else:
                gguf_path = None
        except (FileNotFoundError, json.JSONDecodeError):
            gguf_path = None

        if gguf_path is None:
            gguf_files = list(model_dir.glob("*.gguf"))
            if not gguf_files:
                raise AdapterUnavailableError(f"No GGUF files found in {model_dir}")

            quants = [  # noqa: E501
                gguf_file.stem.split("-")[-1]
                for gguf_file in gguf_files
                if "-" in gguf_file.stem
            ]
            best_quant = select_best_quant(quants)
            if best_quant:
                for gguf_file in gguf_files:
                    if f"-{best_quant}" in gguf_file.stem:
                        gguf_path = gguf_file
                        break
            if gguf_path is None:
                gguf_path = gguf_files[0]

        try:
            with gguf_path.open("rb") as gguf_file_handle:
                buf = gguf_file_handle.read(8)
        except OSError as exc:
            raise AdapterUnavailableError("Invalid or unreadable GGUF file") from exc

        if len(buf) < 8:
            raise AdapterUnavailableError("Truncated GGUF header")

        if buf[:4] != b"GGUF":
            raise AdapterUnavailableError("Invalid GGUF file (bad magic)")

        version = int.from_bytes(buf[4:8], "little", signed=False)
        if version < 2:
            raise AdapterUnavailableError(f"Unsupported GGUF version {version} (v1 deprecated)")

        gpus = self._hardware_probe.sample().gpus
        if not gpus:
            n_gpu_layers = 0
            self._trace.emit(
                component="llama_cpp_adapter",
                level=TraceLevel.WARN,
                message="No GPU — CPU mode",
            )
        else:
            vram_budget_mb = max(g.vram_total_mb for g in gpus)
            if not model.vram_required_mb or not model.num_layers:
                n_gpu_layers = 0
                self._trace.emit(
                    component="llama_cpp_adapter",
                    level=TraceLevel.WARN,
                    message="incomplete model metadata, CPU mode",
                )
            else:
                n_gpu_layers = min(
                    model.num_layers,
                    vram_budget_mb * model.num_layers // max(1, model.vram_required_mb),
                )

        self._trace.emit(
            component="llama_cpp_adapter",
            level=TraceLevel.INFO,
            message=f"Loading model {model_id} with {n_gpu_layers} GPU layers",
        )

        try:
            import llama_cpp

            self._llm = llama_cpp.Llama(model_path=str(gguf_path), n_gpu_layers=n_gpu_layers)
            self._loaded_model_id = model_id
            self._trace.emit(
                component="llama_cpp_adapter",
                level=TraceLevel.INFO,
                message=f"Model {model_id} loaded successfully",
            )
        except Exception as exc:
            self._trace.emit(
                component="llama_cpp_adapter",
                level=TraceLevel.ERROR,
                message=f"Failed to load model {model_id}: {exc}",
            )
            raise AdapterUnavailableError(f"Failed to load model: {exc}") from exc

    def generate(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int,
        temperature: float,
        timeout_seconds: float = 30.0,
    ) -> str:
        self._trace.emit(  # noqa: E501
            component="llama_cpp_adapter",
            level=TraceLevel.DEBUG,
            message=(
                f"generate() called with model_id={model_id}, "
                f"max_tokens={max_tokens}, temperature={temperature}"
            )
        )
        self.load_model(model_id)

        result: str | None = None
        error: Exception | None = None
        timeout_event = threading.Event()

        def _generate() -> None:
            nonlocal result, error
            try:
                completion = self._llm.create_completion(
                    prompt, max_tokens=max_tokens, temperature=temperature
                )
                result = str(completion["choices"][0]["text"])  # type: ignore[index]
            except Exception as exc:
                error = exc
            finally:
                timeout_event.set()

        thread = threading.Thread(target=_generate, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if not timeout_event.is_set():
            raise GenerationTimeoutError(
                f"Generation exceeded timeout of {timeout_seconds} seconds"
            )

        if error is not None:
            self._trace.emit(
                component="llama_cpp_adapter",
                level=TraceLevel.ERROR,
                message=f"Generation failed: {error}",
            )
            raise AdapterUnavailableError(str(error)) from error

        if result is None:
            raise AdapterUnavailableError("llama.cpp generation returned None")

        return result

    def health_check(self) -> AdapterHealth:
        try:
            import llama_cpp
        except ImportError:
            return AdapterHealth(healthy=False, detail="llama-cpp-python not installed")

        if self._requested_n_gpu_layers > 0:
            if hasattr(llama_cpp, "llama_supports_gpu_offload"):
                if not llama_cpp.llama_supports_gpu_offload():
                    return AdapterHealth(
                        healthy=False,
                        detail="GPU offload not supported in this build",
                    )
            else:
                return AdapterHealth(
                    healthy=False,
                    detail="llama-cpp build predates GPU offload probe",
                )

        return AdapterHealth(healthy=True, detail="OK")
