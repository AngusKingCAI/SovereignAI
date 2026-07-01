# SovereignAI — Education Department: Implementation Specification

**Document Type:** Deep Implementation Spec  
**Author:** Angus / Claude (design pass)  
**Audience:** GLM (implementing agent) + Round Table review  
**Status:** Draft v2 — amended to integrate Research Department upstream dependency  
**Date:** 2026-06-29  
**Depends on:** `SovereignAI_Architecture_Decisions.md`, `principles.md`, `models-panel-spec.md`, `SovereignAI_Research_Department_Spec.md`
**Note on direction:** this is a genuine runtime dependency, not a documentation cross-reference — the Education Manager cannot start Stage 1 without a completed Research Brief (§7.1 of the Research spec; Stage 0 below). This is the asymmetric half of the Research↔Education relationship; see the Research spec's header note for why Research's own reference to Education does not run the other way.

---

## 0. Purpose

This document specifies the **Education Department** — SovereignAI's internal capability for creating **slim, hyper-specialized expert models** from larger base models. Using techniques including QLoRA fine-tuning, model pruning, and knowledge distillation, the department produces purpose-built models (a Python Coder Model, a Legal Analyst Model, a Medical Triage Model, etc.) that run efficiently on local hardware and slot directly into the existing Models panel as first-class citizens alongside downloaded models.

The core value proposition: instead of routing every coding task through a large 70B generalist, the user can deploy a 3–7B model that has been specifically trained on Python, runs on less VRAM, responds faster, and produces higher quality outputs for that narrow domain.

---

## 1. Company Metaphor Placement

Following the SovereignAI company structure:

| Entity | Role in Education Department |
|--------|------------------------------|
| **Owner (User)** | Decides which expert models to create; approves training runs; accepts or rejects finished models |
| **Orchestrator (CEO)** | Receives the order ("create a Python Coder model"), structures it into a training job specification |
| **Education Manager** | Permanent department head. Owns the training pipeline end-to-end. Coordinates Dataset Workers, Training Workers, Evaluation Workers, and Export Workers |
| **Research Manager** | Upstream dependency. Receives a Domain Brief request from the Education Manager, runs the full Research pipeline, and delivers a completed `education_domain_brief_v1.toml` before Stage 1 begins |
| **Dataset Workers** | Consume the Research Department's Domain Brief to pull recommended datasets; clean, format, and synthesize training data. Do **not** perform their own dataset discovery or base model evaluation — that belongs to Research |
| **Training Workers** | Execute fine-tuning jobs (QLoRA via Unsloth/Axolotl), write checkpoints to SSD |
| **Evaluation Workers** | Run benchmarks on candidate models, generate quality reports |
| **Export Workers** | Merge LoRA adapters into base model, quantize, export to GGUF, register with Ollama |
| **Librarian** | Provides training data from memory backends (Qdrant embeddings, Postgres chat history, Obsidian docs) as raw inputs to Dataset Workers |
| **Security Guard** | Audits training data provenance, flags suspicious inputs, verifies GGUF checksums |

The Education Department is a **permanent department** (not task-spawned). It maintains its own state: a registry of training jobs, completed models, and evaluation reports. It surfaces in the Workers panel under a dedicated "Education" section.

---

## 2. What the Department Produces

Each output is called an **Expert Model**. An Expert Model is:

- A GGUF file on disk, sized appropriately for the target hardware tier
- A `Modelfile` so Ollama can serve it immediately
- A manifest (`expert-model.toml`) declaring the domain, base model lineage, training dataset hash, benchmark scores, and VRAM requirement
- A LoRA adapter archive (kept separately so the user can re-merge onto a newer base model later without retraining)

Expert Models are registered in the Models panel under a new provider tab: **[Education]**, where they appear alongside downloaded Ollama/HuggingFace models. They can be set as the default model for a specific SovereignAI department (e.g., "Python Coder Model" set as default for the Coding Department).

---

## 3. The Three Core Techniques

### 3.1 QLoRA Fine-Tuning (Primary Technique)

**What it is:** QLoRA (Quantized Low-Rank Adaptation) combines two ideas. First, the base model's weights are loaded in 4-bit NF4 (NormalFloat 4) precision — this cuts VRAM consumption by approximately 75% compared to standard 16-bit loading. Second, small "adapter" matrices (called LoRA adapters) are added between transformer layers. Only these adapter matrices are trained; the frozen base weights are never updated. The result: a 7B model that would require ~14GB of VRAM to fine-tune in full precision can instead be fine-tuned with ~8GB.

**Why QLoRA over full fine-tuning:**
- Full fine-tuning a 7B model requires 100–120GB of VRAM (roughly $50,000 of H100s for a single run). QLoRA does the same job on a single RTX 4090 (24GB) in hours.
- LoRA adapters are typically 10–100MB. The base model on disk is unchanged. Multiple expert adapters can be stored and swapped without storing multiple full copies of the base model.
- Quality loss is small: QLoRA achieves approximately 80–90% of full fine-tuning quality — acceptable for domain-specialized models where the goal is deeper expertise in a narrow area, not general-purpose supremacy.

**How it works technically:**

```
Base Model Weights (Frozen, 4-bit NF4)
         ↓
[Input] → W_frozen (4-bit) + (A × B × α/r) → [Output]
                              ↑
                     LoRA Adapters (trainable, bf16)
                     A: (d × r), B: (r × d)
                     r = rank (controls adapter capacity)
                     α = scaling factor
```

During the forward pass, the 4-bit frozen weights are temporarily dequantized to bfloat16 for computation. Gradients flow only through the LoRA adapter matrices — never into the frozen base. At the end of training, the adapters (A and B matrices) encode everything the model learned.

**Key hyperparameters and recommended starting values:**

| Parameter | Recommended Default | Notes |
|-----------|--------------------|----|
| `lora_r` (rank) | 16 | Increase to 32–64 for large domain shifts. r=8 for simple formatting tasks |
| `lora_alpha` | 32 (= 2×r) | Controls adapter influence. Raise to 3×r if adaptation is too slow |
| `lora_dropout` | 0.05 | Light regularization |
| `target_modules` | `all-linear` | Targets all attention + MLP linear layers. Broader = more expressive |
| `learning_rate` | 2e-4 | Cosine decay with warmup |
| `quantization` | NF4 (4-bit), double quant | Standard for QLoRA |
| `compute_dtype` | bfloat16 | Training precision for adapters |
| `batch_size` | 4 | With gradient accumulation steps = 4 (effective batch = 16) |
| `num_epochs` | 2–5 | Watch validation loss; stop at inflection point |
| `max_seq_length` | 2048–4096 | Domain-dependent |

**Three QLoRA innovations to implement:**
1. **NF4 quantization** — 4-bit NormalFloat data type, information-theoretically optimal for normally distributed neural network weights
2. **Double quantization** — the quantization constants themselves are quantized, saving an additional ~0.4 bits/parameter
3. **Paged optimizers** — optimizer states (AdamW momentum, variance) page to CPU RAM during memory spikes, preventing OOM crashes

### 3.2 Model Pruning (Secondary / Post-Training Technique)

Pruning removes parameters from an already-trained or fine-tuned model that contribute little to output quality. The goal is to reduce model size and inference cost beyond what quantization alone achieves.

**Three categories of pruning:**

**Structured Pruning** removes entire components — attention heads, MLP layers, or transformer blocks. This produces an architecturally smaller model that is immediately hardware-efficient (no special runtime needed). Disadvantages: tends to cause more quality degradation; usually requires short re-fine-tuning (LoRA recovery pass) after pruning.

*Relevant tool: LLM-Pruner (gradient-based structured pruning + LoRA recovery). ShortGPT (layer removal by Block Influence score).*

**Unstructured Pruning** zeroes out individual weights based on magnitude or importance criteria. The resulting model has the same architecture but with many zero weights (sparsity). Research shows unstructured pruning (Wanda, Magnitude pruning) can match unpruned models at 50–60% sparsity, and can sometimes even improve performance. Disadvantage: requires sparsity-aware hardware or software for actual speedup.

*Relevant tools: SparseGPT (one-shot, no retraining needed), Wanda (weight magnitude × input activation norm).*

**Semi-Structured Pruning (N:M sparsity)** enforces that exactly N of every M consecutive weights are zero. NVIDIA's Ampere architecture (RTX 30xx, A100) natively accelerates 2:4 sparsity (2 zeros per 4 weights), providing real inference speedup without specialized hardware.

**Recommended pruning strategy for the Education Department:**

For most Expert Models, pruning is applied **after** QLoRA fine-tuning as a final compression step:

1. Fine-tune the base model with QLoRA to create a domain-specialized adapter.
2. Merge the adapter into the base model to produce a full-precision merged model.
3. Apply structured pruning (10–30% of layers removed) using a small domain-relevant calibration dataset.
4. Run a short LoRA recovery pass (1–2 epochs) on pruned model.
5. Quantize the result to GGUF Q4_K_M for deployment.

This pipeline can reduce a 7B model to effective ~3–4B parameter density while retaining the specialized knowledge.

### 3.3 Knowledge Distillation (Teacher→Student Transfer)

Knowledge distillation uses a large "teacher" model to train a smaller "student" model. The student does not just learn from the raw training labels — it learns from the teacher's soft probability distributions over outputs (the "dark knowledge"), which carry richer information than hard labels alone.

**Three distillation methods available to the Education Department:**

**Response Distillation (Black-Box):** The teacher generates instruction-response pairs. The student fine-tunes on these synthetic outputs. This is the most practical approach — it requires no access to the teacher's internal activations, only its API or local inference. Workflow: run a capable frontier or local model (Llama 4, Qwen, etc.) to generate thousands of expert-quality Q&A pairs in the target domain; use these as the student model's training data.

**Chain-of-Thought (CoT) Distillation:** The teacher generates step-by-step reasoning traces alongside final answers. The student learns to produce the same reasoning style. Research ("Distilling Step-by-Step") shows a 770M-parameter student trained on CoT rationales can outperform few-shot prompted 540B models on target tasks. The Education Department should prefer CoT generation for reasoning-heavy domains (coding, math, logic).

**Logit-Level Distillation (White-Box):** The student is trained to minimize KL divergence between its output logits and the teacher's — not just to predict the correct token, but to match the teacher's entire probability distribution. This requires access to the teacher's logits during training (i.e., both models must be running simultaneously). More computationally intensive, but extracts more information per training example. Suitable for distilling smaller versions of locally-hosted teachers.

**Recommended distillation strategy:**

For Expert Model creation, the most pragmatic approach is **Response Distillation + CoT** using a locally-hosted capable model (e.g., a 70B Qwen or Llama running on the user's hardware) as teacher. This avoids licensing complications from frontier API providers (OpenAI's terms prohibit training competing models from outputs) and keeps data fully local-first.

---

## 4. End-to-End Training Pipeline

The pipeline has seven stages. Each stage maps to one or more Workers. All stages are tracked as tasks in the Tasks panel with full status, history, and logs.

```
Stage 0: Research Brief (Research Department)
       ↓  produces: education_domain_brief_v1.toml
Stage 1: Domain Specification
       ↓
Stage 2: Dataset Construction
       ↓
Stage 3: QLoRA Fine-Tuning
       ↓
Stage 4: Evaluation & Quality Gate
       ↓
Stage 5: Pruning & Compression (optional)
       ↓
Stage 6: Export, Registration & Deployment
```

### Stage 0: Research Brief (Research Department Handoff)

**Actor:** Education Manager → Research Manager (cross-department event bus message)

The Education Manager cannot begin a training job without a completed Domain Brief from the Research Department. This is a **hard dependency** — not advisory. The rationale: dataset selection, base model choice, and benchmark identification all require research that the Education Department does not perform itself. Starting without a brief means making those choices arbitrarily, which produces lower-quality Expert Models and duplicates effort the Research Department is designed to do.

**How the handoff works:**

The Education Manager publishes a `ResearchBriefRequest` event to the event bus when a new training job is initiated:

```python
ResearchBriefRequest(
    requested_by   = "education_manager",
    job_id         = "python-coder-v1",
    domain         = "Python Software Engineering",
    description    = "Expert Python developer: idiomatic code, testing, debugging, PEP compliance",
    output_schema  = "education_domain_brief_v1",
    depth          = "standard",
    urgency        = "normal"
)
```

The Research Manager picks this up, runs the full research pipeline (Source Discovery → Deep Retrieval → Evaluation → Fact-Checking → Synthesis), and publishes a `ResearchBriefComplete` event when finished:

```python
ResearchBriefComplete(
    brief_id        = "brief-20260629-001",
    job_id          = "python-coder-v1",
    deliverable_path = "research/deliverables/brief-20260629-001.toml",
    confidence      = 0.88
)
```

The Education Manager reads the delivered `education_domain_brief_v1.toml` and uses it to pre-populate Stage 1 (Domain Specification). The training job record in the Education Registry stores the `brief_id` permanently — so the provenance chain from final Expert Model back to the research that informed it is always intact.

**Override:** The Owner can bypass Stage 0 with an explicit `skip_research: true` flag on the training job (recorded in the job manifest). This is logged as a conscious decision, not a silent shortcut. Useful when the Owner already has domain knowledge and wants to specify datasets and base model manually.

**Timeout behaviour:** If the Research Department does not complete the brief within a configurable timeout (default: 30 minutes for `standard` depth), the Education Manager escalates a warning to the CEO for Owner awareness. The job remains in `AWAITING_BRIEF` state — it does not proceed and does not silently time out.

**What the Domain Brief provides to Stage 1:**

| Brief Field | Stage 1 Consumption |
|-------------|-------------------|
| `base_model.recommended_model` | Pre-fills the base model selection in `training-job.toml`. Owner can override. |
| `base_model.vram_qlora_estimate_gb` | Used by hardware_check.py to validate the job fits on available VRAM before anything runs |
| `datasets.recommended[]` | Pre-fills the dataset list for Stage 2 Dataset Workers. Workers pull from this list rather than discovering independently |
| `datasets.gaps` | Flags whether synthetic data generation is needed to fill coverage gaps, and how significant those gaps are |
| `benchmarks.primary` + `benchmarks.secondary` | Configures the Evaluation Worker's benchmark suite in Stage 4 |
| `open_questions[]` | Surfaced to the Owner during Stage 1 review — any unresolved issues (e.g., unclear dataset licenses) that need a decision before training starts |

### Stage 1: Domain Specification

The Owner (or CEO, on behalf of the Owner) reviews the Domain Brief delivered by the Research Department and confirms or overrides its recommendations. The Education Manager pre-populates the `training-job.toml` from the brief; the Owner's role here is **review and approval**, not discovery.

Specifically, the Owner confirms or overrides:

- **Target domain** — the domain description from the brief (e.g., "Python developer", "legal contract analyst"). Usually accepted as-is; the Owner may narrow or expand the scope.
- **Base model** — the Research Department's recommended base model is pre-filled (e.g., `Qwen/Qwen2.5-Coder-7B`). The Owner can override this with any model from the Models panel, but the brief's rationale and license notes are displayed alongside the recommendation to inform the decision.
- **Hardware tier** — determined automatically from the Hardware panel and the brief's `vram_qlora_estimate_gb`; Owner confirms.
- **Quality bar** — minimum benchmark improvement over base model to accept the result. Benchmark names are pre-filled from the brief's `benchmarks.primary` field.
- **Open questions** — any items flagged by Research (e.g., unclear dataset licenses) must be resolved or explicitly deferred before the job is confirmed.

This produces a `training-job.toml` manifest:

```toml
[job]
id = "python-coder-v1"
domain = "Python Software Engineering"
description = "Expert Python developer: idiomatic code, testing, debugging, PEP compliance"
research_brief_id = "brief-20260629-001"   # set by Education Manager from Stage 0 handoff
skip_research = false                        # true = Owner override, bypasses Stage 0

[base]
provider = "ollama"
model = "qwen3"
tag = "7b"
identifier = "ollama:qwen3:7b"

[training]
technique = "qlora"
lora_r = 16
lora_alpha = 32
target_modules = "all-linear"
max_seq_length = 4096
num_epochs = 3
learning_rate = "2e-4"

[hardware]
max_vram_gb = 24
training_backend = "unsloth"

[quality_gate]
min_humaneval_pass_at_1_delta = 0.05  # must improve base by 5 percentage points
max_mmlu_delta = -0.03                # general capability must not drop more than 3%

[output]
gguf_quantization = "q4_k_m"
register_in_models_panel = true
set_as_coding_dept_default = false
```

### Stage 2: Dataset Construction

The Dataset Worker builds the training corpus using the recommended datasets from the Research Department's Domain Brief. **Dataset Workers do not perform independent dataset discovery or evaluation** — that work was done in Stage 0. Their role is to pull, clean, synthesize, and format the datasets the brief identified.

It operates in three sub-phases:

**Phase A: Seed Collection.** Pull the datasets listed in the Domain Brief's `datasets.recommended[]` field:

- **From the Domain Brief's ranked dataset list:** Workers iterate through recommended datasets in rank order, pulling from HuggingFace Hub, GitHub, or other identified sources as specified in the brief.
- **From Memory panel (Librarian):** User's own documents, code files, and past chat history relevant to the domain — queried via the Librarian using the domain tags from the brief.
- **Gap check:** If the Domain Brief's `datasets.gaps` field flags a coverage gap (e.g., "no Python debugging dataset found"), the Education Manager marks Phase B (Synthetic Generation) as required rather than optional for this job.

**Phase B: Synthetic Data Generation (Self-Instruct).** A locally-hosted teacher model (configurable — defaults to the largest model available in the Models panel) generates:

1. A seed set of 150–200 hand-curated instruction-response examples
2. The teacher expands these into 5,000–20,000 new instruction-response pairs via Self-Instruct
3. Chain-of-Thought reasoning is requested explicitly: the teacher is prompted to "think step by step" and include its reasoning trace in the response
4. For coding domains, the teacher generates working, executable code with inline comments explaining choices

Generated data is validated programmatically (Python: actually executable; JSON: parseable; etc.) before inclusion.

**Phase C: Cleaning and Formatting.** All collected data is:

1. Deduplicated (MinHash LSH on instruction text)
2. Filtered by length (discard too-short or too-long examples relative to `max_seq_length`)
3. Formatted into a consistent instruction template (Alpaca-style or ShareGPT-style, matching the base model's training format)
4. Split into train (90%) / validation (10%) sets
5. Stored as `.jsonl` in `education/datasets/<job_id>/`

**Minimum dataset sizes by domain complexity:**

| Complexity | Examples | Use Case |
|-----------|----------|---------|
| Simple format/style | 500–1,000 | Output formatting, tone |
| Domain specialization | 3,000–10,000 | Python coder, legal analyst |
| Deep reasoning shift | 7,000–20,000 | Math solver, research analyst |

The dataset is hashed (SHA-256) and recorded in the job manifest for reproducibility and the Security Guard's provenance checks.

### Stage 3: QLoRA Fine-Tuning

The Training Worker invokes the training backend. The primary backend is **Unsloth** (single-GPU, maximum VRAM efficiency, fastest iteration). The secondary backend is **Axolotl** (YAML-driven, used for multi-GPU runs or when Unsloth does not support the target base model architecture).

**Unsloth (default — single GPU):**

```python
# Pseudocode — actual implementation is a Worker skill
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = base_model_identifier,
    max_seq_length = config.max_seq_length,
    dtype = None,        # auto-detect bf16/fp16
    load_in_4bit = True, # NF4 quantization
)

model = FastLanguageModel.get_peft_model(
    model,
    r = config.lora_r,
    target_modules = config.target_modules,
    lora_alpha = config.lora_alpha,
    lora_dropout = config.lora_dropout,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 42,
)

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = train_data,
    eval_dataset = val_data,
    dataset_text_field = "text",
    max_seq_length = config.max_seq_length,
    args = training_args,
)

trainer.train()
```

**Training monitoring:** The Training Worker emits real-time events to the SovereignAI event bus: training loss, validation loss, learning rate, GPU utilization, VRAM usage. These are surfaced in the Hardware panel (live GPU stats via `capability_api.sample_hardware()` per OR69) and in a Training sub-view within the Workers panel (loss curves). The Logs panel (10th sidebar tab, consuming `/api/traces` SSE per OR66) shows verbatim training logs.

**Early stopping:** If validation loss increases for more than 3 consecutive checkpoints, the training is paused and the Owner is interrupted with a `choice` interrupt: "Validation loss has risen. Options: (A) Stop and use last best checkpoint, (B) Continue for N more epochs, (C) Abort."

**Checkpointing:** Adapter checkpoints saved every N steps (configurable, default: every epoch) to `education/checkpoints/<job_id>/`. The best checkpoint (lowest validation loss) is marked. Checkpoint files are LoRA adapters only — typically 10–100MB per checkpoint regardless of base model size.

**Axolotl (multi-GPU or pipeline mode):**

When Axolotl is selected as backend, the Training Worker generates a `training.yml` in the Axolotl YAML schema and invokes `axolotl train training.yml`. This enables distributed training with FSDP/DeepSpeed for large base models (>30B parameters) that don't fit on a single GPU even with QLoRA.

### Stage 4: Evaluation & Quality Gate

The Evaluation Worker runs benchmarks on the best checkpoint to determine whether the model passes the quality gate.

**Two-axis evaluation:**

**Axis 1 — Domain Performance:** Task-specific metrics measuring improvement in the target domain.

| Domain | Primary Benchmark | Secondary |
|--------|------------------|-----------|
| Python coding | HumanEval pass@1 | MBPP, EvalPlus |
| General coding | MultiPL-E | SWE-bench |
| Legal | LegalBench | Custom Q&A |
| Math/reasoning | GSM8K, MATH | AIME |
| Research/science | GPQA | SciQ |
| General assistant | MT-Bench | IFEval |

**Axis 2 — General Capability Retention (Catastrophic Forgetting Check):**

Domain fine-tuning risks degrading the model's general capabilities. The Evaluation Worker measures this by running a subset of MMLU (Massive Multitask Language Understanding) and comparing against the base model's known scores:

- MMLU score **must not drop more than the configured `max_mmlu_delta`** (default: 3 percentage points)
- ARC-Challenge (commonsense reasoning) is also measured
- If catastrophic forgetting is detected, the Evaluation Worker flags this and suggests remediation options (mixing general data into training set, reducing epochs, using EWC regularization)

**Passing the quality gate:** Both axes must pass. If either fails, the Evaluation Worker reports failure with diagnostic details (which benchmark failed by how much, overfitting/underfitting signals, suggestions). The Owner is notified and can choose to: accept anyway, trigger re-training with adjusted config, or abort.

**Catastrophic forgetting prevention measures (built in):**

1. **Data mixing:** The Dataset Worker always includes a small proportion (5–15%) of general-purpose instruction data (Alpaca, WildChat) alongside domain data — this anchors the model to general capabilities.
2. **Conservative LoRA rank:** Using r=16 rather than r=64 limits how aggressively the adapter reshapes the base model's behavior.
3. **Regularization:** EWCLoRA (Elastic Weight Consolidation applied to LoRA parameters) is supported as an opt-in for tasks known to cause strong forgetting.
4. **Short training:** Fewer epochs = less forgetting. The Evaluation Worker's early stopping signal catches the inflection point before forgetting begins.

### Stage 5: Pruning & Compression (Optional)

Applied only when:
- The resulting model still exceeds the user's target VRAM budget, **or**
- The Owner explicitly requested maximum compression

**Default pruning recipe for 7B models:**

```
1. Start from: merged 16-bit model (LoRA adapters merged into base)
2. Calibration set: 512 examples from domain dataset (domain-relevant = better pruning decisions)
3. Method: SparseGPT (one-shot unstructured pruning, 2:4 N:M sparsity)
   - Target sparsity: 50% (N:M = 2:4)
   - No retraining required for unstructured up to ~50%
4. Optional follow-up: 1-epoch LoRA recovery pass if quality degraded > threshold
5. Output: sparse 7B model ≈ 40% of original parameter active density
```

**Structured layer pruning (for maximum size reduction):**

When the goal is a model that runs on CPU-only or very limited VRAM (< 8GB):

```
1. Use ShortGPT to compute Block Influence (BI) scores for all transformer layers
2. Remove bottom 20–30% of layers by BI score
3. Run 2-epoch LoRA recovery pass (critical — structured pruning without recovery degrades badly)
4. Result: genuine parameter reduction (e.g., 7B → ~4B real parameter count)
5. Re-run Axis 1 + Axis 2 evaluation on pruned model
```

### Stage 6: Export, Registration & Deployment

**Step 6A: Merge adapters.**

The LoRA adapter matrices (A and B) are merged back into the base model weights. The merge formula: `W_merged = W_base + (A × B) × (alpha / r)`. Unsloth handles 4-bit dequantization automatically before merge. Result: a full-precision merged `.safetensors` model.

**Step 6B: GGUF conversion and quantization.**

The merged model is converted to GGUF format (the binary format used by llama.cpp and Ollama) and quantized for deployment:

```
Quantization levels available (in order of decreasing size):
 - q8_0:    highest quality, ~8GB for 7B model
 - q4_k_m:  recommended default, ~4GB for 7B model, 95%+ quality retention
 - q3_k_m:  aggressive, ~3GB for 7B model, some quality loss
 - q2_k:    minimum viable, ~2.5GB, noticeable degradation
```

Default output: `q4_k_m` unless hardware tier analysis (from Hardware panel) suggests another quantization.

**Step 6C: Ollama Modelfile generation.**

```
FROM ./python-coder-v1-q4_k_m.gguf
SYSTEM You are an expert Python software engineer with deep knowledge of Pythonic idioms,
PEP 8, testing best practices, debugging, and modern Python ecosystem tools.
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
TEMPLATE {{ .Prompt }}
```

**Step 6D: Registration in Models panel.**

The Export Worker calls the catalog API to insert the Expert Model into the `models` table under the `[Education]` provider tab:

```python
{
  "provider": "education",
  "family": "python-expert",
  "name": "Python Coder v1",
  "description": "QLoRA fine-tuned from Qwen3-7B on Python coding corpus",
  "capabilities": ["tools", "code"],
  "base_model": "ollama:qwen3:7b",
  "training_job_id": "python-coder-v1",
  "benchmark_humaneval": 0.68,
  "benchmark_mmlu_delta": -0.01,
  "version_tag": "v1.0",
  "size_bytes": 4200000000,
  "vram_estimate_gb": 5.2,
  "quantization": "Q4_K_M",
  "gguf_path": "education/models/python-coder-v1/python-coder-v1-q4_k_m.gguf",
  "modelfile_path": "education/models/python-coder-v1/Modelfile",
  "adapter_archive_path": "education/adapters/python-coder-v1-lora.tar.gz"
}
```

The model is then loaded into Ollama via `ollama create python-coder-v1 -f Modelfile` and becomes available for immediate use.

**Step 6E: Owner notification.**

The CEO delivers a structured summary to the Owner:

```
Expert Model created: Python Coder v1
Base: Qwen3-7B → Fine-tuned 3 epochs on 8,400 Python examples
HumanEval: 58% → 71% (+13 percentage points)
MMLU delta: -0.8% (within acceptable range)
Size: 4.1GB (Q4_K_M GGUF)
VRAM required: ~5.2GB
Status: Registered in Models panel under [Education] → Python Expert → Python Coder v1
Action: Set as Coding Department default? [Yes / No / Later]
```

---

## 5. Expert Model Taxonomy

The Education Department can produce models across these domains. This list is illustrative, not exhaustive:

### 5.1 Engineering Sub-Domain Models

| Expert Model | Target Base | Key Training Data | Primary Benchmark |
|-------------|-------------|-------------------|-------------------|
| Python Coder | 7B | HumanEval, Stack-Python, GitHub Python repos | HumanEval pass@1 |
| JavaScript/TypeScript Dev | 7B | Stack-JS, TS repos, MDN docs | MultiPL-E JS |
| Bash/Shell Scripter | 3B | Shell scripts, man pages | Custom eval |
| SQL Expert | 3B | Spider dataset, SQL docs, schema examples | Spider accuracy |
| Git & DevOps | 3B | GitHub Actions YAML, Dockerfile corpus | Custom eval |
| Regex & Text Processing | 3B | RegexBuddy data, StackOverflow regex answers | Custom eval |

### 5.2 Research Sub-Domain Models

| Expert Model | Target Base | Key Training Data |
|-------------|-------------|-------------------|
| Scientific Literature Analyst | 7B | PubMed, ArXiv papers, GPQA dataset |
| Data Analyst | 7B | Kaggle notebooks, statsmodels docs, pandas Q&A |
| Academic Writer | 7B | Academic papers, citation formatting, style guides |

### 5.3 Communication Sub-Domain Models

| Expert Model | Target Base | Key Training Data |
|-------------|-------------|-------------------|
| Technical Writer | 3B | ReadTheDocs, API documentation, changelogs |
| Email Composer | 3B | Email datasets, professional correspondence |
| Meeting Summariser | 3B | AMI corpus, meeting transcripts |

### 5.4 Operations Sub-Domain Models

| Expert Model | Target Base | Key Training Data |
|-------------|-------------|-------------------|
| Task Planner | 3B | Planning datasets, structured scheduling Q&A |
| Checklist Generator | 1B | Procedural text, SOPs, technical runbooks |

### 5.5 User-Defined Models

The Owner can specify any domain not in the taxonomy. The CEO prompts for:
- A plain-English domain description
- Any local documents to use as seed data
- Hardware constraints
- Acceptable training time budget

The Dataset Worker then constructs a bespoke corpus using synthetic generation.

---

## 6. Integration with Other SovereignAI Panels

### 6.1 Models Panel

The Models panel gains an **[Education]** tab. This tab reads from the same four-table catalog schema defined in `models-panel-spec.md`, with `provider_id = "education"`. The `integrated` flag is `true` — models in this tab are fully functional, not browse-only.

The drill-down under the Education tab:

```
[Education] tab
  └─ Python Expert (family)
       └─ Python Coder (model)
            └─ v1.0 — Q4_K_M — 4.1GB — ~5.2GB VRAM — HumanEval 71%
            └─ v1.1 — Q4_K_M — 4.3GB — ~5.4GB VRAM — HumanEval 74%
  └─ SQL Expert (family)
       └─ SQL Analyst (model)
            └─ v1.0 — Q3_K_M — 2.8GB — ~3.5GB VRAM — Spider 87%
```

Each version shows: quantization, disk size, VRAM estimate, primary benchmark score, base model lineage, creation date, and training job ID (links to training run record).

New actions in the version detail row (beyond what catalogue models get):

- **Re-train** — opens a new training job using this model's config as starting point
- **Re-merge on new base** — takes the stored LoRA adapter archive and merges it onto a newer version of the base model (without re-training — useful when the user updates their Qwen3 from 7b to a newer release)
- **Unload / Delete** — removes from Ollama and optionally deletes GGUF file

### 6.2 Tasks Panel

All training jobs appear in the Tasks panel. A training job is a long-running scheduled task with the following states:

```
RECEIVED → AWAITING_BRIEF → QUEUED → DATASET_CONSTRUCTION → TRAINING → EVALUATING → EXPORTING → COMPLETE
                                                                             ↓
                                                                        QUALITY_GATE_FAILED
```

`AWAITING_BRIEF` is the state while the Research Department is running Stage 0. If `skip_research: true` is set, this state is skipped and the job moves directly from `RECEIVED` to `QUEUED`.

Training jobs are cancellable (stops at next checkpoint boundary and preserves work done so far).

### 6.3 Hardware Panel

During a training run, the Hardware panel surfaces:
- GPU utilization (should be 90–100% during training; drops signal a pipeline bottleneck)
- VRAM usage (Training Worker reports current usage, peak, and available headroom)
- Temperature and power draw
- Estimated time remaining (computed from tokens-per-second × total tokens)

The Hardware panel also exposes a **VRAM Budget Calculator** sub-section for the Education Department: given a base model and `lora_r`, it estimates peak training VRAM and whether the current hardware can accommodate the job.

### 6.4 Memory Panel

The Librarian routes two types of memory queries from the Education Department:

- **Training data retrieval** — Dataset Workers request "all Python-related documents from Obsidian" or "recent chat messages about coding from Postgres" as seed material for synthetic data generation
- **Benchmark storage** — Evaluation results for each training run are stored in Postgres as structured records and indexed for retrieval (so the CEO can answer "what's our best Python model?" without re-running evals)

### 6.5 Options Panel

New Education-specific settings under a dedicated "Education Department" section:

| Setting | Default | Notes |
|---------|---------|-------|
| Default training backend | Unsloth | Unsloth or Axolotl |
| Default base model for fine-tuning | (largest model currently loaded) | |
| Synthetic data teacher | (largest model in Models panel) | Which model generates synthetic training data |
| Default GGUF quantization | Q4_K_M | |
| General data mixing ratio | 10% | % of non-domain data in training corpus to prevent forgetting |
| Auto-prune if VRAM > threshold | Off | If on, automatically triggers pruning stage when output model exceeds N GB |
| Checkpoint retention | Last 3 | How many checkpoints to keep per job (older deleted) |
| Training run logging | Full | Verbosity level for training logs |

### 6.6 Skills Panel

The Education Department exposes a **Composite Skill** called `create-expert-model` that orchestrates the full six-stage pipeline. This skill is invocable from the CEO's office ("Create a SQL expert model from the Qwen3 3B base") and produces a training job in the Tasks panel.

Individual pipeline stages are exposed as **Atomic Skills**:
- `generate-domain-dataset` — Stage 2 alone
- `run-qlora-training` — Stage 3 alone (takes a pre-built dataset path)
- `evaluate-expert-model` — Stage 4 alone
- `prune-model` — Stage 5 alone
- `export-gguf` — Stage 6 alone

This modularity allows the Owner to run stages independently — e.g., generate and inspect a dataset before committing to the GPU time of a training run.

---

## 7. Hardware Requirements & Tier Planning

Because training is GPU-intensive, the Education Department must be hardware-aware. The following tiers guide job planning:

| Hardware Tier | GPU | VRAM | Max Base Model for QLoRA | Approximate Training Time (7B, 5K examples) |
|---------------|-----|------|--------------------------|----------------------------------------------|
| **Minimum** | RTX 3060 Ti | 8GB | 7B with QLoRA | 4–8 hours |
| **Standard** | RTX 3090 / 4080 | 16–20GB | 13B with QLoRA | 2–4 hours |
| **Recommended** | RTX 4090 / 5090 | 24GB | 30B with QLoRA | 1–3 hours |
| **Extended** | A100 / H100 | 80GB | 70B with QLoRA | 2–6 hours |
| **No GPU** | CPU only | RAM | 1–3B with llama.cpp backend | 12–48 hours (feasible but slow) |

The Hardware panel provides this tier information to the Education Manager, which uses it to:
- Recommend the largest viable base model for the user's hardware
- Warn before starting a job that would exceed available VRAM
- Suggest cloud burst options (RunPod, Lambda Labs) for jobs that exceed local capability

---

## 8. File / Directory Structure on Disk

All Education Department files live under `C:/SovereignAI/education/` (or equivalent):

```
C:/SovereignAI/
  education/
    datasets/
      <job_id>/
        train.jsonl
        val.jsonl
        metadata.json         # source list, SHA-256, row count, dedup stats
    checkpoints/
      <job_id>/
        checkpoint-epoch-1/   # LoRA adapter weights (10–100MB)
        checkpoint-epoch-2/
        checkpoint-best/      # symlink to best checkpoint
    models/
      <job_id>/
        merged-16bit/         # full-precision merged model (large, optional)
        <job_id>-q4_k_m.gguf  # deployment GGUF
        Modelfile             # Ollama Modelfile
    adapters/
      <job_id>-lora.tar.gz    # archived LoRA adapters for re-use
    jobs/
      <job_id>.toml           # training job manifest
    reports/
      <job_id>-eval.json      # benchmark results
    logs/
      <job_id>-training.log
```

---

## 9. Backend Module Layout

```
/backend
  /education
    manager.py               # Education Manager — orchestrates all stages
    job_store.py             # CRUD for training jobs (stored in Postgres/SQLite)
    /dataset
      collector.py           # Stage 2A: pulls from public datasets, GitHub, Memory
      synthesizer.py         # Stage 2B: Self-Instruct synthetic generation via teacher model
      cleaner.py             # Stage 2C: dedup, filter, format, split
      formats.py             # Alpaca / ShareGPT / raw text formatters
    /training
      backend_unsloth.py     # Stage 3: Unsloth training wrapper
      backend_axolotl.py     # Stage 3: Axolotl YAML generation + subprocess launch
      checkpoint_manager.py  # save/load/select best checkpoint
      hardware_check.py      # VRAM estimation and tier detection
    /evaluation
      runner.py              # Stage 4: orchestrates benchmarks
      benchmarks/
        humaneval.py
        mmlu.py
        arc_challenge.py
        custom.py            # pluggable domain-specific eval
      quality_gate.py        # pass/fail logic
      forgetting_detector.py # catastrophic forgetting analysis
    /pruning
      structured.py          # Stage 5: LLM-Pruner / ShortGPT wrapper
      unstructured.py        # Stage 5: SparseGPT / Wanda wrapper
      recovery.py            # post-pruning LoRA recovery pass
    /export
      merger.py              # Stage 6A: LoRA adapter merge
      gguf_converter.py      # Stage 6B: llama.cpp convert_hf_to_gguf.py wrapper
      modelfile_gen.py       # Stage 6C: Ollama Modelfile generation
      catalog_registrar.py   # Stage 6D: Models panel catalog insertion
    api.py                   # REST endpoints consumed by the UI
      # GET  /education/jobs
      # POST /education/jobs            (create new training job)
      # GET  /education/jobs/<id>       (status + logs)
      # POST /education/jobs/<id>/cancel
      # GET  /education/jobs/<id>/eval  (benchmark results)
      # POST /education/jobs/<id>/export (trigger export stage)
      # GET  /education/models          (list all produced Expert Models)
      # POST /education/models/<id>/retrain
      # POST /education/models/<id>/remerge
      # DELETE /education/models/<id>
/frontend
  /components/education/
    EducationPanel.tsx        # main Education sub-view inside Workers panel
    TrainingJobList.tsx       # list of all jobs with status indicators
    TrainingJobDetail.tsx     # live loss curves, hardware stats, Logs panel subscription
    DatasetInspector.tsx      # view sample rows from training/validation sets
    EvaluationReport.tsx      # benchmark results, forgetting analysis, quality gate decision
    CreateJobWizard.tsx       # step-by-step job creation: domain → base model → hardware check → confirm
  /models-panel/
    EducationProviderTab.tsx  # [Education] tab in Models panel (extends existing provider tabs)
```

---

## 10. Security Guard Integration

The Security Guard has audit hooks into the Education Department at the following points:

- **Dataset collection:** Scans downloaded public datasets for data that contains malicious code, biased training signals, or content that would violate the Owner's preferences. Flags flagged rows for Owner review before training begins.
- **Synthetic generation:** Logs all teacher model calls and stores a hash of generated outputs alongside the dataset. Provides provenance chain: "This dataset was generated by model X from seed data Y on date Z."
- **Export:** Verifies the SHA-256 hash of the produced GGUF file and records it in the model manifest. If the file is modified on disk after registration, the Security Guard flags it on next audit.
- **Model loading:** Before any Expert Model is loaded into Ollama for inference, the Security Guard confirms the GGUF hash matches the registered value.

---

## 11. Open Questions for Round Table

1. **Teacher model licensing:** The synthetic data generation phase uses a locally-hosted model as teacher. Should SovereignAI enforce a check against the teacher model's license (some models prohibit using their outputs to train other models)? If so, what is the mechanism — license metadata in the Models panel catalog, or a Security Guard rule?

2. **CPU-only training path:** On hardware with no CUDA GPU, is there a viable training path? llama.cpp supports LoRA fine-tuning via Metal (macOS) and CPU, but quality and speed are substantially degraded. Should the Education Department surface this as a supported (but warned) option, or require a GPU?

3. **Training data from Memory panel:** When pulling the user's own documents and chat history as training data, what privacy controls apply? Should there be an explicit confirmation step before personal data is incorporated into a model that gets shared or merged with external base weights?

4. **Re-merge on base model update:** When the user downloads a new version of a base model (e.g., Qwen3-7B updates), should the system proactively offer to re-merge stored LoRA adapters onto the new base? This is low-cost (no retraining) and would keep Expert Models current.

5. **VRAM during training vs inference:** The system may need to unload all inference models from VRAM before a training job begins, since training requires peak VRAM that may exceed the combined inference budget. Who coordinates this — the Education Manager, the Hardware panel, or the Lifecycle Manager (core)? The Lifecycle Manager is the most architecturally correct answer, but requires a new capability.

6. **Multi-adapter inference:** Instead of merging adapters and exporting to GGUF, some inference engines (vLLM, SGLang) support loading multiple LoRA adapters on top of a single base model and selecting the adapter per-request. This would allow a single base model to serve as Python Coder, SQL Expert, and Legal Analyst simultaneously (with adapter swapping per task). Worth considering for v2 — but requires a different inference backend than Ollama.

7. **Versioning and rollback:** If Expert Model v2 performs worse than v1 on the Owner's real tasks (not just benchmarks), can the Owner roll back to v1? Since v1's GGUF file is preserved, rollback is just re-registering the old model. Confirm this is the intended pattern.

8. **Dataset formats for non-text domains:** For vision-language or audio models (multimodal Expert Models), the dataset format changes substantially. Is multimodal fine-tuning in scope for v1 of the Education Department, or deferred?

9. **Research dependency mode — blocking vs advisory:** Stage 0 is currently a hard blocking dependency: the training job will not proceed without a completed Domain Brief. An alternative is `advisory` mode, where the job proceeds with a warning if Research does not complete in time, and the brief is incorporated retroactively if it arrives before Dataset Construction finishes. Blocking is safer and produces better results; advisory reduces latency for time-sensitive jobs. Should `research_dependency_mode` be a per-job setting (defaulting to `blocking`), or always blocking for v1?

---

## 12. Implementation Order (Suggested)

1. **Directory structure + job_store.py** — scaffolding and data model, including `research_brief_id` and `skip_research` fields and the `AWAITING_BRIEF` state. Confirms schema before any training code is written.
2. **Stage 0 event bus integration** — Education Manager publishes `ResearchBriefRequest` and listens for `ResearchBriefComplete`. Implement with a stub Research Manager response first (returns a hardcoded brief) so the Education pipeline can be developed and tested before the Research Department is fully operational.
3. **hardware_check.py** — VRAM estimation utility, now also consuming `vram_qlora_estimate_gb` from the Domain Brief. Immediately useful and blocks nothing else.
4. **cleaner.py + formats.py** — dataset utilities. Enables testing the pipeline with real data before training infrastructure exists.
5. **backend_unsloth.py (training)** — primary training path. Use a tiny 1B model on a small dataset to validate end-to-end without burning GPU time.
6. **checkpoint_manager.py** — validates that checkpoints can be saved, listed, and loaded.
7. **runner.py + mmlu.py + humaneval.py (evaluation)** — validates the quality gate logic.
8. **merger.py + gguf_converter.py (export)** — validates the GGUF output is valid and can be loaded by Ollama.
9. **catalog_registrar.py** — slots the Expert Model into the Models panel.
10. **EducationPanel.tsx + TrainingJobDetail.tsx** — UI. Wire to live events via existing SSE infrastructure. Include `AWAITING_BRIEF` state display.
11. **synthesizer.py (synthetic data)** — add synthetic generation on top of the working pipeline.
12. **pruning/** — add as optional stage, validate it doesn't break the export path.
13. **backend_axolotl.py** — add as secondary backend for multi-GPU / unsupported architectures.
14. **Security Guard hooks** — add provenance and audit after core pipeline is stable.

---

*End of document.*
