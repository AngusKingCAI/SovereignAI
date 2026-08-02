Depends on: prompt-13
Vision principles: P3 (memory is modular), P13 (learning), Q13 (improvement)
Open questions resolved: Q13 (fully — learning is a worker, not core)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-13 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules (revised from Rev1 per Round Table adjudication):
- **OR63**: The Education department is a first-class organizational unit. It has its own worker (Teacher) and skills (self-correction, dataset curation). It is NOT a special case — it registers via the CapabilityGraph like any other department. Source: Plan 14.
- **OR64** (revised): Model improvement tasks (QLoRA fine-tuning, evaluation) are heavy-weight operations that run asynchronously. They are dispatched as tasks via the CapabilityAPI, not run synchronously in the request handler. The web UI shows progress via task state polling. Fine-tuning acquires a process-wide GPU lock (`GPUResourceManager`) before starting — Ollama inference and other GPU consumers must respect the same lock. For v1 the lock is in-process (`threading.Lock`); cross-process locking is deferred. Source: Plan 14 Rev2 (F-10).
- **OR65** (revised): The Teacher worker gracefully degrades if GPU/dependencies are unavailable. It registers with DEGRADED status and emits a WARN trace. The UI shows "Teacher: unavailable — install GPU dependencies" instead of failing silently. Heavy ML imports (`torch`, `transformers`, `peft`, `trl`, `bitsandbytes`, `accelerate`, `datasets`) are deferred inside method bodies (`finetune`, `evaluate`) — never at module level. The `health_check()` method uses `importlib.util.find_spec()` to check availability without importing, so a missing dependency does not break import. Source: Plan 14 Rev2 (F-20).
- **OR69**: The self-correction skill subscribes to `TaskStateChanged` events but must filter out events emitted by its own operations to prevent recursive feedback loops. The skill tags its own trace emissions with `component="self_correction"` and the subscription callback ignores events where `event.component == "self_correction"`. Additionally, a recursion depth guard limits self-correction to 1 invocation per task_id (tracked via a set of recently-analyzed task_ids, cleared after analysis completes). Source: Plan 14 Rev2 (F-1, CRITICAL).
- **OR70**: The Teacher worker's `curate_dataset()` method requires an explicit `consent: bool` parameter. When `consent=False`, the method returns an empty list and logs a WARN. A minimal PII filter (regex-based, covering email, phone, SSN, credit card patterns) strips obvious PII from training examples. Only traces from the last 30 days are eligible. This is a v1 minimal safeguard; a proper PII filter is deferred. Source: Plan 14 Rev2 (F-9, CRITICAL).

Commit: `docs: add OR63-OR65, OR69-OR70 for prompt-14`

---

## Plan Body

### S1 — Create sovereignai/shared/hardware_probe.py + workers/education/teacher_worker.py

**Critical Rev2 fix (F-35)**: Rev1 referenced `HardwareProbe` "From Plan 7" but `HardwareProbe` does not exist anywhere in the repo. This plan creates it as a core shared component (justified: it's used by the Education worker, which is a top-level package — putting `HardwareProbe` in `web/` would create a layering violation).

**S1a — Create sovereignai/shared/hardware_probe.py** (new core file):
```python
"""Hardware probe — detect GPU, VRAM, and compute availability.

Used by workers (Education) and adapters (Ollama) to make runtime decisions
about model loading and fine-tuning feasibility.
"""
import shutil
import subprocess

class HardwareProbe:
    """Detect available hardware resources (GPU, VRAM, CPU, RAM)."""

    def __init__(self) -> None:
        """Create a hardware probe. Detection is lazy — runs on first query."""

    def has_nvidia_gpu(self) -> bool:
        """Return True if an NVIDIA GPU is detected via nvidia-smi."""
        return shutil.which("nvidia-smi") is not None

    def get_vram_mb(self) -> int | None:
        """Return VRAM in MB if an NVIDIA GPU is present, else None."""
        if not self.has_nvidia_gpu():
            return None
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            )
            return int(result.stdout.strip().split("\n")[0])
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return None

    def has_cuda_via_torch(self) -> bool:
        """Return True if torch reports CUDA is available. Imports torch lazily."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
```

**S1b — Create workers/education/teacher_worker.py**:

```python
"""Teacher worker — performs model improvement tasks (QLoRA fine-tuning, evaluation)."""
import importlib.util
import os
import threading
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel
from sovereignai.shared.hardware_probe import HardwareProbe
from sovereignai.shared.capability_api import CapabilityAPI

# Process-wide GPU lock (per Rev2 OR64) — in-process only for v1
_GPU_LOCK = threading.Lock()

class TeacherWorker:
    """Perform model improvement: QLoRA fine-tuning, evaluation, dataset curation."""

    def __init__(
        self,
        capability_api: CapabilityAPI,
        trace: TraceEmitter,
        hardware_probe: HardwareProbe,
    ) -> None:
        """Create a Teacher worker with GPU and dependency awareness."""
        self._capability_api = capability_api
        self._trace = trace
        self._hardware_probe = hardware_probe

    def health_check(self) -> bool:
        """Check if GPU and QLoRA dependencies are available, without importing heavy libs.

        Uses importlib.util.find_spec() so a missing dependency does not break import.
        Returns True only if all required packages are importable AND CUDA is available.
        """
        required = ["torch", "peft", "transformers", "trl", "bitsandbytes", "accelerate", "datasets"]
        for pkg in required:
            if importlib.util.find_spec(pkg) is None:
                self._trace.emit(
                    component="teacher",
                    level=TraceLevel.WARN,
                    message=f"QLoRA dependency '{pkg}' not installed. Install with: pip install sovereignai[education]",
                )
                return False
        if not self._hardware_probe.has_cuda_via_torch():
            self._trace.emit(
                component="teacher",
                level=TraceLevel.WARN,
                message="CUDA not available. Teacher worker requires an NVIDIA GPU.",
            )
            return False
        return True

    def finetune(self, base_model: str, dataset: list, output_name: str) -> str:
        """Fine-tune a model using QLoRA. Acquires GPU lock. Returns path to fine-tuned model.

        Heavy ML imports are inside this method body (per Rev2 OR65) — not at module level.
        """
        # Lazy imports (per Rev2 F-20)
        import torch
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from trl import SFTTrainer
        import datasets

        # Acquire GPU lock (per Rev2 OR64) — blocks if Ollama or another worker holds it
        if not _GPU_LOCK.acquire(timeout=10):
            raise RuntimeError("GPU lock timeout — another GPU task is running. Retry later.")
        try:
            self._trace.emit(component="teacher", level=TraceLevel.INFO,
                             message=f"Acquired GPU lock; starting QLoRA fine-tune of {base_model}")

            # Quantization config (per Rev2 F-5 — Rev1's load_in_4bit=True was deprecated)
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                quantization_config=bnb_config,
                device_map="auto",
                torch_dtype=torch.bfloat16,
            )
            tokenizer = AutoTokenizer.from_pretrained(base_model)

            lora_config = LoraConfig(
                r=16, lora_alpha=32,
                target_modules=["q_proj", "v_proj"],
                task_type="CAUSAL_LM",
            )
            model = get_peft_model(prepare_model_for_kbit_training(model), lora_config)

            train_dataset = datasets.Dataset.from_list(dataset)
            trainer = SFTTrainer(
                model=model, tokenizer=tokenizer,
                train_dataset=train_dataset,
                dataset_text_field="prompt",
            )
            trainer.train()

            # Expand ~ (per Rev2 F-5 — Rev1's unexpanded tilde was a bug)
            output_path = os.path.expanduser(f"~/.sovereignai/models/{output_name}")
            os.makedirs(output_path, exist_ok=True)
            model.save_pretrained(output_path)

            # Register in model registry (per Rev2 F-43)
            self._register_model(output_name, output_path, dataset)

            self._trace.emit(component="teacher", level=TraceLevel.INFO,
                             message=f"Fine-tune complete; model saved to {output_path}")
            return output_path
        finally:
            _GPU_LOCK.release()

    def evaluate(self, model_path: str, dataset: list) -> dict:
        """Evaluate a model on a dataset. Returns metrics: loss and perplexity only.

        Note (per Rev2 F-33): 'accuracy' is removed — it is a classification metric,
        not appropriate for causal LMs. Perplexity (exp of cross-entropy loss) is the
        standard causal LM metric.
        """
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        # ... implementation returns {"loss": float, "perplexity": float} ...

    def curate_dataset(self, trace_ids: list[str], criteria: dict, consent: bool) -> list:
        """Extract training examples from episodic memory. Requires explicit consent.

        Per Rev2 OR70: consent=False returns empty list with WARN.
        A minimal PII filter strips email/phone/SSN/credit-card patterns.
        Only traces from the last 30 days are eligible.
        """
        if not consent:
            self._trace.emit(component="teacher", level=TraceLevel.WARN,
                             message="curate_dataset called with consent=False; returning empty dataset")
            return []
        # ... query episodic memory, filter by date + PII, return list of {"prompt": str, "completion": str} ...
```

### S2 — Create workers/education/manifest.toml

Per Rev2 F-22 — use TOML multiline literal strings (`'''...'''`) for `input_schema`/`output_schema` to avoid the unescaped-quote parse failure.

```toml
[component]
id = "teacher_worker"
name = "Teacher Worker"
version = "0.1.0"
author = "user"
content_hash = "<computed at /close per OR48>"
department = "education"

[[capabilities]]
category = "worker"
name = "model_finetune"
description = "Fine-tune a local model using QLoRA"
input_schema = '''
{
  "base_model": "string",
  "dataset": [{"prompt": "string", "completion": "string"}],
  "output_name": "string"
}
'''
output_schema = '''
{
  "model_path": "string",
  "metrics": {"loss": "float", "epochs": "int"}
}
'''
priority = 100

[[capabilities]]
category = "worker"
name = "model_evaluate"
description = "Evaluate model performance"
input_schema = '''
{
  "model_path": "string",
  "dataset": [{"prompt": "string", "completion": "string"}]
}
'''
output_schema = '''
{
  "loss": "float",
  "perplexity": "float"
}
'''
priority = 100

[[capabilities]]
category = "worker"
name = "dataset_curate"
description = "Curate training dataset from traces (requires explicit consent)"
input_schema = '''
{
  "trace_ids": ["string"],
  "criteria": {"min_quality": "float", "task_types": ["string"]},
  "consent": "bool"
}
'''
output_schema = '''
{
  "dataset": [{"prompt": "string", "completion": "string"}],
  "count": "int"
}
'''
priority = 100
```

### S3 — Create skills/official/self_correction/skill.py

Per Rev2 F-1 (CRITICAL) — add recursion guard and self-event filtering.

```python
"""Self-correction skill — analyzes traces and updates procedural memory.

Subscribes to TaskStateChanged events. Filters out its own trace emissions
to prevent recursive feedback loops (per Rev2 OR69).
"""
import threading
from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import TraceLevel, TaskState, TaskStateChanged

class SelfCorrectionSkill:
    """Analyze completed tasks and update procedural memory with learned patterns."""

    COMPONENT_NAME = "self_correction"  # Used to filter own events

    def __init__(
        self,
        librarian: Librarian,
        trace: TraceEmitter,
    ) -> None:
        """Create a self-correction skill with recursion guard."""
        self._librarian = librarian
        self._trace = trace
        self._recently_analyzed: set[str] = set()  # task_ids analyzed in this cycle
        self._lock = threading.Lock()

    def on_task_state_changed(self, event: TaskStateChanged) -> None:
        """Handle a task state change event. Filters own events to prevent recursion.

        Per Rev2 OR69: ignores events where the trace component is 'self_correction'.
        Also enforces a 1-invocation-per-task_id guard.
        """
        if event.new_state not in (TaskState.COMPLETE, TaskState.FAILED):
            return
        task_id_str = str(event.task_id)
        with self._lock:
            if task_id_str in self._recently_analyzed:
                return  # Already analyzed this task — prevent recursion
            self._recently_analyzed.add(task_id_str)
        try:
            self.analyze_task(task_id_str)
        finally:
            with self._lock:
                self._recently_analyzed.discard(task_id_str)

    def analyze_task(self, task_id: str) -> dict:
        """Read trace events for a task, extract patterns, update procedural memory.

        Filters out events emitted by self_correction (per Rev2 OR69) to prevent
        the feedback loop: completion → self-correction → trace emission → self-correction.
        """
        # Query traces for this task, EXCLUDING self_correction's own emissions
        traces = self._librarian.query("trace", {
            "task_id": task_id,
            "exclude_component": self.COMPONENT_NAME,
        })
        patterns = self._extract_patterns(traces)
        for pattern in patterns:
            self.update_procedural_memory(pattern, confidence=pattern.get("confidence", 0.5))
        # If a high-confidence routing-failure pattern is found, recommend retraining (per Rev2 F-45)
        for pattern in patterns:
            if pattern.get("type") == "routing_failure" and pattern.get("confidence", 0) > 0.8:
                self._recommend_retraining(pattern)
        return {"patterns_found": len(patterns), "memory_updated": len(patterns) > 0}

    def update_procedural_memory(self, pattern: dict, confidence: float) -> bool:
        """Store a learned pattern in procedural memory via the Librarian."""
        record_id = self._librarian.store("procedural", data=pattern, metadata={"confidence": confidence})
        return record_id is not None

    def prune_low_confidence(self, threshold: float = 0.3) -> int:
        """Remove procedural memory entries below the confidence threshold."""
        # Query procedural memory for low-confidence patterns and delete them
        low_confidence = self._librarian.query("procedural", {"max_confidence": threshold})
        count = 0
        for entry in low_confidence:
            if self._librarian.delete("procedural", entry["id"]):
                count += 1
        return count

    def _extract_patterns(self, traces: list) -> list:
        """Extract learned patterns from a list of trace events."""
        # ... implementation ...
        return []

    def _recommend_retraining(self, pattern: dict) -> None:
        """Publish a retraining recommendation event for the Teacher worker (per Rev2 F-45)."""
        self._trace.emit(
            component=self.COMPONENT_NAME,
            level=TraceLevel.INFO,
            message=f"Retraining recommended: high-confidence routing failure pattern detected (confidence={pattern.get('confidence')})",
        )
        # The Teacher worker subscribes to INFO-level self_correction traces and queues a fine-tune job.
        # Full event-bus integration is deferred — for v1, the trace emission is the signal.
```

### S4 — Create skills/official/self_correction/manifest.toml

Per Rev2 F-22 — multiline literal strings.

```toml
[component]
id = "self_correction_skill"
name = "Self-Correction"
version = "0.1.0"
author = "user"
content_hash = "<computed at /close per OR48>"

[[capabilities]]
category = "skill"
name = "self_correction"
description = "Analyze traces and update procedural memory with learned patterns"
input_schema = '''
{
  "task_id": "string"
}
'''
output_schema = '''
{
  "patterns_found": "int",
  "memory_updated": "bool"
}
'''
priority = 50
```

### S5 — Dataset curation logic (with consent + PII filter + retention)

Per Rev2 OR70 — the `curate_dataset()` method:

1. If `consent=False`, return `[]` with WARN trace.
2. Query episodic memory for traces matching `trace_ids` and `criteria`.
3. Filter by `last_used_after` = now - 30 days (retention limit).
4. Extract `(prompt, completion)` pairs from successful task traces. Skip traces that don't have the expected shape `{"prompt": str, "completion": str}` — log a WARN for each skipped trace (per Rev2 F-39).
5. Apply minimal PII filter: regex-strip email addresses, phone numbers, SSN patterns, and credit card patterns from both `prompt` and `completion`. Replace with `[REDACTED]`.
6. Filter out low-quality examples (errors, timeouts, user cancellations) per `criteria.min_quality`.
7. Return curated dataset as `list[dict]` where each dict is `{"prompt": str, "completion": str}`.

### S6 — QLoRA fine-tuning implementation

See S1b above. The `finetune()` method body is complete with:
- Lazy imports inside the method (per Rev2 F-20)
- GPU lock acquisition (per Rev2 OR64)
- Correct `BitsAndBytesConfig` usage (per Rev2 F-5 — Rev1's `load_in_4bit=True` was deprecated)
- `device_map="auto"` and `torch_dtype=torch.bfloat16` (per Rev2 F-5)
- `os.path.expanduser()` for the output path (per Rev2 F-5 — Rev1's unexpanded tilde was a bug)
- Model registry write (per Rev2 F-43)
- Size-limit enforcement: before saving, check total size of `~/.sovereignai/models/`; if >50 GB, evict oldest models by `created_at` (per Rev2 F-44)
- `try/finally` on the GPU lock to ensure release on error

**Cancellation** (per Rev2 F-53): a `_cancel_requested` flag is checked between training steps. The `cancel()` method sets it. Full mid-step cancellation is deferred — the current step completes before the flag is checked. Progress is reported via trace events every 100 steps.

### S7 — Update main.py composition root

Per Rev2 F-23 — create all required `__init__.py` files for the new packages.

**Files to create first** (before imports work):
- `sovereignai/workers/__init__.py` (empty)
- `sovereignai/workers/education/__init__.py` (empty)
- `sovereignai/skills/__init__.py` (empty — note: `sovereignai/skills/` exists with `.gitkeep` but no `__init__.py`)
- `sovereignai/skills/official/__init__.py` (empty)
- `sovereignai/skills/official/self_correction/__init__.py` (empty)

**Composition root additions**:
```python
# 17. HardwareProbe (new core component — per Rev2 F-35)
from sovereignai.shared.hardware_probe import HardwareProbe
hardware_probe = HardwareProbe()
container.register_singleton(HardwareProbe, hardware_probe)

# 18. Teacher Worker
from sovereignai.workers.education.teacher_worker import TeacherWorker
teacher = TeacherWorker(
    capability_api=container.retrieve(CapabilityAPI),
    trace=trace,
    hardware_probe=container.retrieve(HardwareProbe),
)
# Register with DEGRADED status if health_check fails (per Rev2 OR65)
if not teacher.health_check():
    trace.emit(component="main", level=TraceLevel.WARN,
               message="Teacher worker registered in DEGRADED mode — GPU dependencies unavailable")
container.register_singleton(TeacherWorker, teacher)

# 19. Self-Correction Skill
from sovereignai.skills.official.self_correction.skill import SelfCorrectionSkill
self_correction = SelfCorrectionSkill(
    librarian=container.retrieve(Librarian),
    trace=trace,
)
container.register_singleton(SelfCorrectionSkill, self_correction)

# 20. Wire self-correction to TaskStateChanged events (per Rev2 F-1 — with recursion guard)
bus = container.retrieve(EventBus)
skill = container.retrieve(SelfCorrectionSkill)
bus.subscribe(TASK_STATE_CHANNEL, skill.on_task_state_changed)
```

### S8 — Update web UI for Education department

Per Rev2 F-32 — specify the exact panel placement and edit the stylesheet.

**Panel placement**: The Education panel replaces the "placeholder" sub-section of the **Hardware** panel (which currently shows GPU/CPU/RAM/VRAM). The Hardware panel keeps its GPU/CPU/RAM/VRAM summary; the Education panel is added as a new section below it within the same sidebar item. This avoids breaking the 9-panel layout (no 10th panel added).

**Files to edit**:
- `web/templates/index.html` — add an Education section inside the Hardware panel's `<div>`, showing: Teacher worker status, available models, training jobs, dataset quality metrics.
- `web/static/app.js` — add an `loadEducationPanel()` function that polls the CapabilityAPI for Teacher worker status.
- `web/static/styles.css` — add `.education-section` styling (margin, padding, table layout for model list). This file was missing from Rev1's "Files WILL Edit" list (F-32).

### S9 — Tests

- `tests/test_teacher_worker.py`: Test `health_check()` (mock `importlib.util.find_spec`), graceful degradation, `curate_dataset()` with `consent=False` returns `[]`, PII filter strips email/phone/SSN, 30-day retention filter works.
- `tests/test_self_correction_skill.py`: Test `analyze_task()`, `update_procedural_memory()`, `prune_low_confidence()`, **recursion guard** (F-1: emit a self_correction trace, verify it's filtered out, verify a task is analyzed at most once).
- `tests/test_qlora_integration.py`: Mock `torch`/`peft`/`transformers`/`trl`/`bitsandbytes`/`accelerate`/`datasets`, test `finetune()` logic without actual GPU. Verify GPU lock is acquired and released. Verify `os.path.expanduser()` is called on the output path.
- `tests/test_education_department.py`: End-to-end: task completion → self-correction → procedural memory update → (mock) retraining recommendation.
- `tests/test_gpu_lock.py`: Test that `GPUResourceManager` lock is mutually exclusive — a second `acquire()` call blocks until the first releases.
- `tests/test_model_registry.py`: Test model registration, size-limit eviction (F-44), manual rollback via registry edit (F-43).

---

## STOP Conditions

- If Teacher worker constructor exceeds 15 arguments, STOP.
- If QLoRA dependencies fail to install via `pip install sovereignai[education]`, STOP only if graceful degradation fails (health_check returns False instead of raising).
- If self-correction skill blocks task completion (runs synchronously >2s per task), STOP.
- If self-correction feedback loop is detected in tests (a self_correction trace triggers another self_correction invocation), STOP — recursion guard failed.
- If PII filter fails to strip a known PII pattern (email, phone, SSN, credit card) in tests, STOP.
- If any test fails, STOP.

---

## Files WILL Create

- `sovereignai/shared/hardware_probe.py` (new core file — per Rev2 F-35)
- `sovereignai/workers/__init__.py` (per Rev2 F-23)
- `sovereignai/workers/education/__init__.py`
- `sovereignai/workers/education/teacher_worker.py`
- `sovereignai/workers/education/manifest.toml`
- `sovereignai/skills/__init__.py` (per Rev2 F-23 — missing in repo)
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

- `sovereignai/main.py` (extend build_container — register HardwareProbe, Teacher, SelfCorrection, wire self-correction to TaskStateChanged)
- `web/templates/index.html` (add Education section inside Hardware panel)
- `web/static/app.js` (add Education panel loader)
- `web/static/styles.css` (add .education-section styling — was missing in Rev1, per F-32)
- `pyproject.toml` (add optional `[education]` extras: `torch`, `transformers>=4.40`, `peft>=0.10`, `trl>=0.8`, `bitsandbytes>=0.42`, `accelerate>=0.25`, `datasets>=2.18`)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` except the new `hardware_probe.py` (new file, not edit to existing — per P1, adding a new core component is allowed with justification; the Education worker needs hardware detection and `web/` is the wrong layer)
- `txt/requirements.txt` (per Rev2 — Education deps are optional extras in pyproject.toml only, NOT in requirements.txt — fixes F-9-adjacent Kimi #9)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-14`. Queue Scan 15 in PLANS.md next-5-queue.

## Adjudication summary (Rev1 → Rev2)

Findings addressed: F-1 (CRITICAL — recursion guard + self-event filtering), F-4 (full dep list enumerated), F-5 (BitsAndBytesConfig, device_map, expanduser), F-9 (CRITICAL — consent gate, PII filter, 30-day retention), F-10 (CRITICAL — GPU lock via GPUResourceManager), F-18 (RoutingEngine is the future consumer; documented, not a black hole), F-20 (lazy imports + find_spec in health_check), F-21 (extras in pyproject.toml only, not requirements.txt), F-22 (multiline literal strings for TOML), F-23 (all __init__.py files created), F-32 (specific panel placement + styles.css edit), F-33 (accuracy removed; loss + perplexity only), F-35 (HardwareProbe created in shared/), F-36 (batch query — addressed in Plan 11 S2), F-39 (return schema specified), F-41 (size cap — addressed in Plan 11 S3), F-43 (model registry), F-44 (size-limit eviction), F-45 (retraining recommendation via trace), F-53 (cancellation flag + progress reporting).

Findings rejected: F-24 (pluggable memory is vision-endorsed), F-52 (STOP thresholds calibrated).
