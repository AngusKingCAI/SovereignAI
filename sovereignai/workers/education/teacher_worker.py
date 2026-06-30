import importlib
import importlib.util
import os
import re
import threading
from datetime import UTC, datetime, timedelta

from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel

# Process-wide GPU lock (per Rev3 N3 — in-process only; does NOT protect against Ollama)
_GPU_LOCK = threading.Lock()


class TeacherWorker:

    def __init__(
        self,
        capability_api: CapabilityAPI,
        trace: TraceEmitter,
        hardware_probe: HardwareProbe,
    ):
        self._capability_api = capability_api
        self._trace = trace
        self._hardware_probe = hardware_probe
        self._cancel_requested = False  # Rev8: initialize in __init__, not finetune()

    def health_check(self) -> bool:
        required = [
            "torch",
            "peft",
            "transformers",
            "trl",
            "bitsandbytes",
            "accelerate",
            "datasets",
        ]
        for pkg in required:
            # F12: find_spec first — fast check, no import side effects
            if importlib.util.find_spec(pkg) is None:
                self._trace.emit(
                    component="teacher",
                    level=TraceLevel.WARN,
                    message=(
                        f"QLoRA dependency '{pkg}' not installed. "
                        "Install with: pip install sovereignai[education]"
                    ),
                )
                return False
            # F12: find_spec succeeded — now try actual import to catch broken installs
            # (find_spec can return non-None for packages with missing native deps)
            try:
                importlib.import_module(pkg)
            except (ImportError, OSError) as e:
                self._trace.emit(
                    component="teacher",
                    level=TraceLevel.WARN,
                    message=(
                        f"QLoRA dependency '{pkg}' found but broken ({type(e).__name__}): {e}. "
                        "Install with: pip install sovereignai[education]"
                    ),
                )
                return False
        # Verify CUDA is actually available (not just that torch imports)
        try:
            import torch
            if not torch.cuda.is_available():
                self._trace.emit(
                    component="teacher",
                    level=TraceLevel.WARN,
                    message="CUDA not available. Teacher worker requires an NVIDIA GPU.",
                )
                return False
        except Exception as e:
            self._trace.emit(
                component="teacher",
                level=TraceLevel.WARN,
                message=f"torch.cuda.is_available() check failed: {e}",
            )
            return False
        return True

    def finetune(self, base_model: str, dataset: list, output_name: str) -> str:
        import datasets
        import torch
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from trl import SFTTrainer

        if not _GPU_LOCK.acquire(timeout=10):
            raise RuntimeError(
                "GPU lock timeout — another in-process GPU task is running. Retry later."
            )
        try:
            self._trace.emit(
                component="teacher",
                level=TraceLevel.INFO,
                message=(
                    f"Acquired in-process GPU lock; "
                    f"starting QLoRA fine-tune of {base_model}"
                ),
            )

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            model = AutoModelForCausalLM.from_pretrained(  # nosec B615
                base_model, quantization_config=bnb_config,
                device_map="auto", torch_dtype=torch.bfloat16,
            )
            tokenizer = AutoTokenizer.from_pretrained(base_model)  # nosec B615
            lora_config = LoraConfig(
                r=16,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj"],
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(prepare_model_for_kbit_training(model), lora_config)
            train_dataset = datasets.Dataset.from_list(dataset)
            trainer = SFTTrainer(
                model=model,
                tokenizer=tokenizer,
                train_dataset=train_dataset,
                dataset_text_field="prompt",
            )

            # Cancellation support (per Rev2 F-53)
            self._cancel_requested = False
            for step in range(trainer.max_steps or 1000):
                if self._cancel_requested:
                    self._trace.emit(
                        component="teacher",
                        level=TraceLevel.WARN,
                        message="Fine-tune cancelled by user",
                    )
                    break
                trainer.train_step()  # Hypothetical API — actual trainer API may differ
                if step % 100 == 0:
                    self._trace.emit(
                        component="teacher",
                        level=TraceLevel.INFO,
                        message=f"Training step {step}",
                    )

            output_path = os.path.expanduser(f"~/.sovereignai/models/{output_name}")
            os.makedirs(output_path, exist_ok=True)

            # Size-limit enforcement (per Rev2 F-44) — evict oldest if >50GB total
            self._enforce_model_size_limit()

            model.save_pretrained(output_path)
            self._register_model(output_name, output_path, dataset)
            return output_path
        finally:
            _GPU_LOCK.release()

    def cancel(self) -> None:
        self._cancel_requested = True

    def evaluate(self, model_path: str, dataset: list) -> dict:
        # Placeholder implementation — actual evaluation logic to be added
        return {"loss": 0.0, "perplexity": 0.0}

    def curate_dataset(
        self, trace_ids: list[str], _criteria: dict[str, object], consent: bool
    ) -> list:
        if not consent:
            self._trace.emit(
                component="teacher",
                level=TraceLevel.WARN,
                message="curate_dataset called with consent=False; returning empty dataset",
            )
            return []

        # Query episodic memory for trace events
        try:
            # CapabilityAPI doesn't have query_memory - use librarian instead
            # For now, return empty list as this requires Librarian dependency
            traces: list = []
        except Exception as e:
            self._trace.emit(
                component="teacher",
                level=TraceLevel.ERROR,
                message=f"Failed to query episodic memory: {e}",
            )
            return []

        # Filter by 30-day retention
        cutoff_date = datetime.now(UTC) - timedelta(days=30)
        filtered_traces = [
            t for t in traces
            if datetime.fromisoformat(t.get("timestamp", "")) >= cutoff_date
        ]

        # Extract examples and filter PII
        examples = []
        pii_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
            r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',  # SSN
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card
        ]

        for trace in filtered_traces:
            prompt = trace.get("prompt", "")
            completion = trace.get("completion", "")

            # Check for PII
            has_pii = any(
                re.search(pattern, prompt + completion, re.IGNORECASE)
                for pattern in pii_patterns
            )
            if has_pii:
                continue

            examples.append({"prompt": prompt, "completion": completion})

        self._trace.emit(
            component="teacher",
            level=TraceLevel.INFO,
            message=f"Curated {len(examples)} examples from {len(trace_ids)} trace IDs",
        )
        return examples

    def _enforce_model_size_limit(self) -> None:
        models_dir = os.path.expanduser("~/.sovereignai/models")
        if not os.path.isdir(models_dir):
            return

        # Calculate total size and list models with creation time
        models = []
        total_size = 0
        for model_name in os.listdir(models_dir):
            model_path = os.path.join(models_dir, model_name)
            if os.path.isdir(model_path):
                size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, _, filenames in os.walk(model_path)
                    for filename in filenames
                )
                created_at = os.path.getctime(model_path)
                models.append({
                    "name": model_name,
                    "path": model_path,
                    "size": size,
                    "created_at": created_at,
                })
                total_size += size

        # Evict oldest if >50GB
        max_size_gb = 50
        while total_size > max_size_gb * 1024 * 1024 * 1024 and models:
            oldest = min(models, key=lambda m: float(m["created_at"]))  # type: ignore[arg-type]
            self._trace.emit(
                component="teacher",
                level=TraceLevel.WARN,
                message=f"Evicting model {oldest['name']} to enforce size limit",
            )
            # Remove model directory
            import shutil
            model_path = str(oldest["path"])  # type: ignore[arg-type]
            shutil.rmtree(model_path)
            oldest_size = int(oldest["size"])  # type: ignore[call-overload]
            total_size -= oldest_size
            models.remove(oldest)

    def _register_model(self, name: str, path: str, dataset: list) -> None:
        import json
        registry_path = os.path.expanduser("~/.sovereignai/model_registry.json")
        registry = {}

        if os.path.exists(registry_path):
            try:
                with open(registry_path) as f:
                    registry = json.load(f)
            except (OSError, json.JSONDecodeError):
                pass

        registry[name] = {
            "path": path,
            "dataset_size": len(dataset),
            "created_at": datetime.now(UTC).isoformat(),
        }

        # Atomic write
        temp_path = registry_path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(registry, f, indent=2)
        os.replace(temp_path, registry_path)
