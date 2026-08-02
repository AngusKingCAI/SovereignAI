Depends on: prompt-13 (batch ordering)
Vision principles: P3 (memory is modular), P13 (learning), Q13 (improvement)
Open questions resolved: Q13 (fully — learning is a worker, not core)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-13 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full. Note the governance rules added in prompts 10.1–10.3 (these apply to this plan's execution and close):
- OR71 (run workflow commands verbatim — re-read `close.md` fresh, do not paraphrase)
- OR75/OR80/OR83 (`git add -A` for ALL commits — no explicit `git add <file>` lists; after every `git add -A`, run `git status -s` to verify staging is clean)
- OR76 (no premature tags — verify `git tag --list prompt-14` is empty before creating)
- OR77 (coverage mandatory at `/close` — STOP if >5% drop from baseline; current baseline: 94%, floor: 89%)
- OR78 (bandit reconciliation — update PLANS.md Low count at every `/close` where tests were added)
- OR82 (never `git mv` — use `mv` + `git add -A` + verify `git ls-files`)

S0.3 — Add new rules (revised from Rev2 per Round Table re-review):
- **OR63**: The Education department is a first-class organizational unit. Source: Plan 14.
- **OR64** (revised): Model improvement tasks run asynchronously via the CapabilityAPI. Fine-tuning acquires a process-wide GPU lock (`threading.Lock`) before starting. **The lock protects against in-process GPU consumers only** (the Teacher worker itself). Cross-process GPU contention with Ollama (a separate process) is NOT handled in v1 — if the user fine-tunes while Ollama is running, Ollama may fail with CUDA OOM. This is a documented known limitation (see DEBT.md). Source: Plan 14 Rev3 (N3).
- **OR65** (revised): The Teacher worker gracefully degrades if GPU/dependencies are unavailable. Heavy ML imports are deferred inside method bodies. Per Rev5 F12: the `health_check()` method uses `importlib.util.find_spec()` FIRST for a fast availability check (no import side effects, ~1ms), then imports the top-level module inside a `try/except` block ONLY if `find_spec` succeeds — this catches both `ImportError` (missing package) and `OSError` (missing CUDA DLLs) without the multi-second import cost on every startup. Source: Plan 14 Rev3 (N17) + Rev5 (F12).
- **OR69**: The self-correction skill subscribes to `TaskStateChanged` events, filters out events where `component == "self_correction"`, and limits to 1 invocation per `task_id` via a `_recently_analyzed` set. When the set's guard triggers (duplicate event), emit a DEBUG trace (not silent). Source: Plan 14 Rev2 (F-1) + Rev3 (N14).
- **OR70**: `curate_dataset()` requires `consent: bool` parameter. PII filter + 30-day retention. Source: Plan 14 Rev2 (F-9).

Commit: `docs: add OR63-OR65, OR69-OR70 for prompt-14`

---

## Plan Body

### S1a — Create sovereignai/shared/hardware_probe.py

(Unchanged from Rev2 — `HardwareProbe` with `has_nvidia_gpu()`, `get_vram_mb()`, `has_cuda_via_torch()`.)

### S1b — Create workers/education/teacher_worker.py

(Revised per Rev6 F12 — health_check uses find_spec FIRST (fast, ~1ms), then imports module ONLY if find_spec succeeds. This catches both ImportError and OSError without the multi-second import cost on every startup.)

```python
"""Teacher worker — performs model improvement tasks (QLoRA fine-tuning, evaluation)."""
import importlib
import importlib.util
import os
import threading
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.capability_api import CapabilityAPI

# Process-wide GPU lock (per Rev3 N3 — in-process only; does NOT protect against Ollama)
_GPU_LOCK = threading.Lock()

class TeacherWorker:
    """Perform model improvement: QLoRA fine-tuning, evaluation, dataset curation."""

    def __init__(self, capability_api, trace, hardware_probe):
        """Create a Teacher worker with GPU and dependency awareness."""
        self._capability_api = capability_api
        self._trace = trace
        self._hardware_probe = hardware_probe
        self._cancel_requested = False  # Rev8: initialize in __init__, not finetune()

    def health_check(self) -> bool:
        """Check if GPU and QLoRA dependencies are available.

        Per Rev6 F12: uses find_spec() FIRST (fast, ~1ms, no import side effects),
        then imports the module ONLY if find_spec succeeds. This catches both
        ImportError (missing package) and OSError (missing CUDA DLLs) without
        the multi-second import cost on every startup.
        """
        required = ["torch", "peft", "transformers", "trl", "bitsandbytes", "accelerate", "datasets"]
        for pkg in required:
            # F12: find_spec first — fast check, no import side effects
            if importlib.util.find_spec(pkg) is None:
                self._trace.emit(
                    component="teacher",
                    level=TraceLevel.WARN,
                    message=f"QLoRA dependency '{pkg}' not installed. Install with: pip install sovereignai[education]",
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
                    message=f"QLoRA dependency '{pkg}' found but broken ({type(e).__name__}): {e}. Install with: pip install sovereignai[education]",
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
        """Fine-tune a model using QLoRA. Acquires in-process GPU lock. Returns model path.

        Per Rev3 N3: the GPU lock is in-process only. It does NOT prevent Ollama
        (a separate process) from using the GPU concurrently. If the user fine-tunes
        while Ollama is running, Ollama may fail with CUDA OOM. This is a known v1 limitation.
        """
        import torch
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from trl import SFTTrainer
        import datasets

        if not _GPU_LOCK.acquire(timeout=10):
            raise RuntimeError("GPU lock timeout — another in-process GPU task is running. Retry later.")
        try:
            self._trace.emit(component="teacher", level=TraceLevel.INFO,
                             message=f"Acquired in-process GPU lock; starting QLoRA fine-tune of {base_model}")

            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            model = AutoModelForCausalLM.from_pretrained(
                base_model, quantization_config=bnb_config,
                device_map="auto", torch_dtype=torch.bfloat16,
            )
            tokenizer = AutoTokenizer.from_pretrained(base_model)
            lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM")
            model = get_peft_model(prepare_model_for_kbit_training(model), lora_config)
            train_dataset = datasets.Dataset.from_list(dataset)
            trainer = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=train_dataset, dataset_text_field="prompt")

            # Cancellation support (per Rev2 F-53)
            self._cancel_requested = False
            for step in range(trainer.max_steps or 1000):
                if self._cancel_requested:
                    self._trace.emit(component="teacher", level=TraceLevel.WARN, message="Fine-tune cancelled by user")
                    break
                trainer.train_step()  # Hypothetical API — actual trainer API may differ
                if step % 100 == 0:
                    self._trace.emit(component="teacher", level=TraceLevel.INFO, message=f"Training step {step}")

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
        """Request cancellation of an in-progress fine-tune."""
        self._cancel_requested = True

    def evaluate(self, model_path: str, dataset: list) -> dict:
        """Evaluate a model. Returns {'loss': float, 'perplexity': float} only (no accuracy — per F-33)."""
        # ... implementation ...

    def curate_dataset(self, trace_ids: list[str], criteria: dict, consent: bool) -> list:
        """Extract training examples from episodic memory. Requires explicit consent.

        Per Rev2 OR70: consent=False returns empty list with WARN.
        PII filter (regex: email/phone/SSN/credit-card) + 30-day retention.
        """
        if not consent:
            self._trace.emit(component="teacher", level=TraceLevel.WARN,
                             message="curate_dataset called with consent=False; returning empty dataset")
            return []
        # ... query episodic memory, filter by date + PII, return list of {"prompt": str, "completion": str} ...

    def _enforce_model_size_limit(self) -> None:
        """Evict oldest fine-tuned models if total size exceeds 50GB (per Rev2 F-44)."""
        models_dir = os.path.expanduser("~/.sovereignai/models")
        if not os.path.isdir(models_dir):
            return
        # ... list models, sum sizes, evict oldest by created_at if >50GB ...

    def _register_model(self, name: str, path: str, dataset: list) -> None:
        """Register a fine-tuned model in the model registry (per Rev2 F-43)."""
        # ... write to ~/.sovereignai/model_registry.json ...
```

### S2 — Create workers/education/manifest.toml

(Unchanged from Rev2 — multiline literal strings for schemas. Add `core = false` field per Plan 12 Rev3 N10.)

```toml
[component]
component_id = "teacher_worker"
name = "Teacher Worker"
version = "0.1.0"
author = "user"
content_hash = "<computed at /close per OR48>"
department = "education"
core = false

# ... capabilities with multiline literal string schemas (unchanged from Rev2) ...
```

### S3 — Create skills/official/self_correction/skill.py

(Revised per Rev3 N14 — emit DEBUG trace when recursion guard triggers.)

```python
"""Self-correction skill — analyzes traces and updates procedural memory."""
import threading
from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel, TaskState, TaskStateChanged

class SelfCorrectionSkill:
    """Analyze completed tasks and update procedural memory with learned patterns."""

    COMPONENT_NAME = "self_correction"

    def __init__(self, librarian: Librarian, trace: TraceEmitter) -> None:
        self._librarian = librarian
        self._trace = trace
        self._recently_analyzed: set[str] = set()
        self._lock = threading.Lock()

    def on_task_state_changed(self, event: TaskStateChanged) -> None:
        """Handle a task state change. Filters own events + deduplicates per task_id."""
        if event.new_state not in (TaskState.COMPLETE, TaskState.FAILED):
            return
        task_id_str = str(event.task_id)
        with self._lock:
            if task_id_str in self._recently_analyzed:
                # Rev3 N14: emit DEBUG trace (not silent)
                self._trace.emit(
                    component=self.COMPONENT_NAME,
                    level=TraceLevel.DEBUG,
                    message=f"Skipping already-analyzed task {task_id_str} (recursion guard)",
                )
                return
            self._recently_analyzed.add(task_id_str)
        try:
            self.analyze_task(task_id_str)
        finally:
            with self._lock:
                self._recently_analyzed.discard(task_id_str)

    def analyze_task(self, task_id: str) -> dict:
        """Read trace events, extract patterns, update procedural memory.
        Filters out self_correction's own emissions (per OR69)."""
        traces = self._librarian.query("trace", {
            "task_id": task_id,
            "exclude_component": self.COMPONENT_NAME,
        })
        patterns = self._extract_patterns(traces)
        for pattern in patterns:
            self.update_procedural_memory(pattern, confidence=pattern.get("confidence", 0.5))
        for pattern in patterns:
            if pattern.get("type") == "routing_failure" and pattern.get("confidence", 0) > 0.8:
                self._recommend_retraining(pattern)
        return {"patterns_found": len(patterns), "memory_updated": len(patterns) > 0}

    def update_procedural_memory(self, pattern: dict, confidence: float) -> bool:
        """Store a learned pattern. Returns True on success, False if lock timed out (per Rev3 N8)."""
        try:
            record_id = self._librarian.store("procedural", data=pattern, metadata={"confidence": confidence})
            return record_id is not None
        except Exception as e:
            # N8: procedural memory lock may time out — log and continue
            self._trace.emit(
                component=self.COMPONENT_NAME,
                level=TraceLevel.WARN,
                message=f"Failed to update procedural memory: {e}",
            )
            return False

    def _recommend_retraining(self, pattern: dict) -> None:
        """Emit a retraining recommendation trace (per Rev2 F-45)."""
        self._trace.emit(
            component=self.COMPONENT_NAME,
            level=TraceLevel.INFO,
            message=f"Retraining recommended: high-confidence routing failure (confidence={pattern.get('confidence')})",
        )

    def _extract_patterns(self, traces: list) -> list:
        """Extract learned patterns from trace events."""
        return []
```

### S4 — Create skills/official/self_correction/manifest.toml

(Unchanged from Rev2 — add `core = false` per Plan 12 Rev3 N10.)

### S5 — Dataset curation logic

(Unchanged from Rev2 — consent gate, PII filter, 30-day retention.)

### S6 — QLoRA fine-tuning implementation

(See S1b above — includes cancellation flag, progress traces, model registry, size-limit enforcement.)

### S7 — Update main.py composition root

(Unchanged from Rev2 — create `__init__.py` files, register HardwareProbe, Teacher, SelfCorrection, wire self-correction to TaskStateChanged. Add `--dev` flag passthrough per Plan 13 Rev3.)

### S8 — Update web UI for Education department

(Unchanged from Rev2 — Education section inside Hardware panel; edit index.html, app.js, styles.css.)

### S9 — Tests

(Updated per Rev3.)

- `tests/test_teacher_worker.py`: Test `health_check()` with **broken imports (N17)**, graceful degradation, `curate_dataset()` consent gate, PII filter, retention.
- `tests/test_self_correction_skill.py`: Test `analyze_task()`, **recursion guard emits DEBUG trace (N14)**, **procedural memory lock timeout handled gracefully (N8)**.
- `tests/test_qlora_integration.py`: Mock deps, test `finetune()` logic, **GPU lock acquired/released (N3 — in-process scope documented)**, `os.path.expanduser()`.
- `tests/test_education_department.py`: End-to-end.
- `tests/test_gpu_lock.py`: Test in-process mutual exclusion.
- `tests/test_model_registry.py`: Test registration, eviction, rollback.

---

## STOP Conditions

- If Teacher worker constructor exceeds 15 arguments, STOP.
- If QLoRA dependencies fail to install via `[education]` extras, STOP only if `health_check()` fails to return False gracefully.
- If self-correction skill blocks task completion >2s per task, STOP.
- If self-correction feedback loop is detected in tests, STOP.
- If PII filter fails to strip a known PII pattern, STOP.
- If `health_check()` returns True when a required package is broken (N17), STOP.
- If coverage drops below 89% (5% drop from 94% baseline), STOP (per OR77).
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/shared/hardware_probe.py`
- `sovereignai/workers/__init__.py`
- `sovereignai/workers/education/__init__.py`
- `sovereignai/workers/education/teacher_worker.py`
- `sovereignai/workers/education/manifest.toml`
- `sovereignai/skills/__init__.py`
- `sovereignai/skills/official/__init__.py`
- `sovereignai/skills/official/self_correction/__init__.py`
- `sovereignai/skills/official/self_correction/skill.py`
- `sovereignai/skills/official/self_correction/manifest.toml`
- `tests/test_teacher_worker.py`
- `tests/test_self_correction_skill.py`
- `tests/test_qlora_integration.py`
- `tests/test_education_department.py`
- `tests/test_gpu_lock.py`
- `tests/test_model_registry.py`

## Files WILL Edit

- `sovereignai/main.py` (extend build_container; add `--dev` flag passthrough)
- `web/templates/index.html`
- `web/static/app.js`
- `web/static/styles.css`
- `pyproject.toml` (add `[education]` extras)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` except new `hardware_probe.py`
- `txt/requirements.txt`
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-14`. Queue Scan 15 in PLANS.md next-5-queue.

## Adjudication summary (Rev2 → Rev3)

New findings addressed: N3 (GPU lock scoped to in-process; Ollama claim removed; DEBT.md entry), N14 (DEBUG trace on recursion guard), N15 (trace batching — DEBT.md entry), N17 (health_check imports modules, not just find_spec).

DEBT.md additions: cross-process GPU lock (N3); batched/background trace inserts (N15); procedural memory consumer wiring (F-18 from Rev2); separate sovereignai-education package (F-21 from Rev2); full PII filter (F-9 from Rev2); full model versioning/rollback (F-43 from Rev2); dedicated task-state ledger (N22 from Plan 11).
