Depends on: prompt-13
Vision principles: P3 (memory is modular), P13 (learning), Q13 (improvement)
Open questions resolved: Q13 (fully — learning is a worker, not core)

---

## S0 — Opening

S0.1 — Run `/open`. Verify prompt-13 tag exists on origin. Confirm working copy is clean and on `main`.

S0.2 — Read `AGENTS.md` in full.

S0.3 — Add new rules:
- **OR63**: The Education department is a first-class organizational unit. It has its own worker (Teacher) and skills (self-correction, dataset curation). It is NOT a special case — it registers via the CapabilityGraph like any other department. Source: Plan 14.
- **OR64**: Model improvement tasks (QLoRA fine-tuning, evaluation) are heavy-weight operations that run asynchronously. They are dispatched as tasks via the CapabilityAPI, not run synchronously in the request handler. The web UI shows progress via task state polling. Source: Plan 14.
- **OR65**: The Teacher worker gracefully degrades if GPU/dependencies are unavailable. It registers with DEGRADED status and emits a WARN trace. The UI shows "Teacher: unavailable — install GPU dependencies" instead of failing silently. Source: Plan 14.

Commit: `docs: add OR63-OR65 for prompt-14`

---

## Plan Body

### S1 — Create workers/education/teacher_worker.py

The Teacher worker performs model improvement tasks.

**Constructor** (≤15 args per AR5):
```python
def __init__(
    self,
    capability_api: CapabilityAPI,
    trace: TraceEmitter,
    hardware_probe: HardwareProbe,  # From Plan 7
) -> None:
```

**Capabilities** (declared in manifest):
- `model_finetune` — Fine-tune a model using QLoRA
- `model_evaluate` — Evaluate model performance on a dataset
- `dataset_curate` — Curate a training dataset from traces

**Methods**:
- `health_check() -> bool`: Check if GPU and dependencies are available.
- `finetune(base_model: str, dataset: list, output_name: str) -> str`: Run QLoRA fine-tuning. Return path to fine-tuned model.
- `evaluate(model_path: str, dataset: list) -> dict`: Return metrics (loss, accuracy, perplexity).
- `curate_dataset(trace_ids: list[str], criteria: dict) -> list`: Extract training examples from episodic memory.

**Graceful degradation**:
```python
def health_check(self) -> bool:
    try:
        import torch
        import peft
        import transformers
        return torch.cuda.is_available()
    except ImportError:
        self.trace.emit(TraceLevel.WARN, "teacher", "QLoRA dependencies not installed. Install with: pip install sovereignai[education]")
        return False
```

### S2 — Create workers/education/manifest.toml

```toml
[component]
id = "teacher_worker"
name = "Teacher Worker"
version = "0.1.0"
author = "user"
department = "education"

[[capabilities]]
category = "worker"
name = "model_finetune"
description = "Fine-tune a local model using QLoRA"
input_schema = "{ "base_model": "string", "dataset": [{"prompt":"string","completion":"string"}], "output_name": "string" }"
output_schema = "{ "model_path": "string", "metrics": {"loss":"float","epochs":"int"} }"
priority = 100

[[capabilities]]
category = "worker"
name = "model_evaluate"
description = "Evaluate model performance"
input_schema = "{ "model_path": "string", "dataset": [{"prompt":"string","completion":"string"}] }"
output_schema = "{ "perplexity": "float", "accuracy": "float" }"
priority = 100

[[capabilities]]
category = "worker"
name = "dataset_curate"
description = "Curate training dataset from traces"
input_schema = "{ "trace_ids": ["string"], "criteria": {"min_quality":"float","task_types":["string"]} }"
output_schema = "{ "dataset": [{"prompt":"string","completion":"string"}], "count": "int" }"
priority = 100
```

### S3 — Create skills/official/self_correction/skill.py

The self-correction skill analyzes traces and updates procedural memory.

**Purpose**: Lightweight, runs frequently (after every task completion), updates procedural memory with learned patterns.

**Constructor**:
```python
def __init__(
    self,
    librarian: Librarian,  # From Plan 11
    trace: TraceEmitter,
) -> None:
```

**Methods**:
- `analyze_task(task_id: str) -> dict`: Read trace events for task, extract routing decisions, outcomes.
- `update_procedural_memory(pattern: dict, confidence: float) -> bool`: Store pattern in procedural memory via Librarian.
- `prune_low_confidence(threshold: float = 0.3) -> int`: Remove procedural memory entries below threshold.

**Integration with TaskStateMachine**: Subscribe to task completion events. On COMPLETE or FAILED, call `analyze_task()`.

### S4 — Create skills/official/self_correction/manifest.toml

```toml
[component]
id = "self_correction_skill"
name = "Self-Correction"
version = "0.1.0"
author = "user"

[[capabilities]]
category = "skill"
name = "self_correction"
description = "Analyze traces and update procedural memory with learned patterns"
input_schema = "{ "task_id": "string" }"
output_schema = "{ "patterns_found": "int", "memory_updated": "bool" }"
priority = 50
```

### S5 — Create dataset curation logic

The Teacher worker's `curate_dataset()` method:

1. Query episodic memory for traces matching criteria (task types, quality threshold).
2. Extract (prompt, completion) pairs from successful task traces.
3. Filter out low-quality examples (errors, timeouts, user cancellations).
4. Return curated dataset as list of dicts.

### S6 — Create QLoRA fine-tuning implementation

The Teacher worker's `finetune()` method:

```python
def finetune(self, base_model: str, dataset: list, output_name: str) -> str:
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from trl import SFTTrainer

    # Load base model (from Ollama registry or local path)
    model = AutoModelForCausalLM.from_pretrained(base_model, load_in_4bit=True)
    tokenizer = AutoTokenizer.from_pretrained(base_model)

    # QLoRA config
    lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
    model = get_peft_model(prepare_model_for_kbit_training(model), lora_config)

    # Train
    trainer = SFTTrainer(model=model, tokenizer=tokenizer, train_dataset=dataset)
    trainer.train()

    # Save
    output_path = f"~/.sovereignai/models/{output_name}"
    model.save_pretrained(output_path)
    return output_path
```

**Note**: This is a simplified sketch. The actual implementation handles error cases, progress reporting, and cancellation.

### S7 — Update main.py composition root

Register Education department components:
```python
# 15. Teacher Worker
from workers.education.teacher_worker import TeacherWorker
teacher = TeacherWorker(
    capability_api=container.retrieve(CapabilityAPI),
    trace=trace,
    hardware_probe=container.retrieve(HardwareProbe),
)
container.register_singleton(TeacherWorker, teacher)

# 16. Self-Correction Skill
from skills.official.self_correction.skill import SelfCorrectionSkill
self_correction = SelfCorrectionSkill(
    librarian=container.retrieve(Librarian),
    trace=trace,
)
container.register_singleton(SelfCorrectionSkill, self_correction)
```

### S8 — Update web UI for Education department

Add to the 9-panel sidebar (Plan 8):
- **Education** panel (replaces one of the placeholder panels or adds as 10th)
- Shows: Teacher worker status, available models, training jobs, dataset quality metrics
- Allows: Submit fine-tuning job, view progress, download fine-tuned model

### S9 — Tests

- `tests/test_teacher_worker.py`: Test health_check, graceful degradation, dataset curation.
- `tests/test_self_correction_skill.py`: Test analyze_task, update_procedural_memory, prune.
- `tests/test_qlora_integration.py`: Mock torch/peft/transformers, test finetune logic without actual GPU.
- `tests/test_education_department.py`: Test end-to-end: task completion → self-correction → procedural memory update.

---

## STOP Conditions

- If Teacher worker constructor exceeds 15 arguments, STOP.
- If QLoRA dependencies fail to install (optional), STOP only if graceful degradation fails.
- If self-correction skill blocks task completion (runs synchronously), STOP.
- If any test fails, STOP.

---

## Files WILL Create

- `workers/education/teacher_worker.py`
- `workers/education/__init__.py`
- `workers/education/manifest.toml`
- `skills/official/self_correction/skill.py`
- `skills/official/self_correction/manifest.toml`
- `tests/test_teacher_worker.py`
- `tests/test_self_correction_skill.py`
- `tests/test_qlora_integration.py`
- `tests/test_education_department.py`

## Files WILL Edit

- `sovereignai/main.py` (extend build_container)
- `web/templates/index.html` (add Education panel)
- `web/static/app.js` (add Education panel loader)
- `pyproject.toml` (add optional `[education]` extras)
- `txt/requirements.txt` (add optional education deps)

## Files WILL NOT Edit

- Any file in `sovereignai/shared/` (core is sacred per P1)
- `AGENTS.md` (except S0.3)

---

## Closing

Run `/close`. Tag: `prompt-14`. Queue Scan 15 in PLANS.md next-5-queue.
