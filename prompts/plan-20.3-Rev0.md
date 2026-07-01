# Plan 20.3 — Diagnostic Harness (Real End-to-End AI Workflow)

```
Depends on: prompt-20.2
Vision principles: P4 (testability), P9 (observability), P13 (fail gracefully)

Open questions resolved: none
```

---

## S0 — Opening
- **S0.1**: Run `/open`
- **S0.2**: Read `AGENTS.md` in full
- **S0.3**: Add OR71 to AGENTS.md: "Diagnostic harness tests real end-to-end AI workflow with explicit model lifecycle: load → use → unload per stage. Mock tests verify code paths; harness tests verify system functionality." Commit.

---

## S1 — Create `scripts/diagnostics/harness.py`

**S1.1**: Import `build_container()` from `sovereignai.main`

**S1.2**: Stage 1 — Start AI Service
- Try `OllamaAdapter.health_check()`. If not running, try `ollama serve` in background, retry after 5s.
- If still failing, try `LlamaCppAdapter.health_check()`.
- PASS if at least one service healthy, SKIP if both unavailable, FAIL if exception.

**S1.3**: Stage 2 — Download Model
- If Ollama healthy: `ollama pull tinyllama`.
- If LlamaCpp healthy: Verify GGUF in `models/`, prompt to download if missing.
- PASS if model available, SKIP if download fails, FAIL if exception.

**S1.4**: Stage 3 — Orchestrator: Load Model + Create Prompt
- Build container, retrieve `MessageDispatcher`.
- Load model into adapter. Call `dispatch("What is 2+2?")`.
- Verify response non-empty, routing_trace present.
- **Unload model** via adapter `unload()`.
- PASS if real response, FAIL if exception.

**S1.5**: Stage 4 — Orchestrator Saves Prompt for Manager
- Store prompt in `WorkingMemoryBackend` with `task_id`.
- Verify `TraceMemoryBackend` logged the interaction.
- PASS if persisted, FAIL if exception.

**S1.6**: Stage 5 — Manager: Load Model + Read Prompt
- Load model into adapter. Retrieve manager from `CapabilityGraph`.
- Manager reads prompt from `WorkingMemoryBackend`.
- **Unload model** via adapter `unload()`.
- PASS if prompt readable, FAIL if exception.

**S1.7**: Stage 6 — Manager Saves Task for Worker
- Manager creates task, saves to `WorkingMemoryBackend`.
- Verify trace logged.
- PASS if task saved, FAIL if exception.

**S1.8**: Stage 7 — Worker: Load Model + Execute
- Load model into adapter. Retrieve worker from `CapabilityGraph`.
- Worker reads task, calls adapter `generate()` with task prompt.
- **Unload model** via adapter `unload()`.
- PASS if worker generates response, FAIL if exception.

**S1.9**: Stage 8 — Worker Saves Results
- Worker stores result in `WorkingMemoryBackend`.
- Verify trace logged.
- PASS if persisted, FAIL if exception.

**S1.10**: Stage 9 — Manager: Load Model + Check Quality
- Load model into adapter. Manager reads result from `WorkingMemoryBackend`.
- Manager checks quality: verify response contains "4".
- **Unload model** via adapter `unload()`.
- PASS if quality check passes, FAIL if exception or wrong content.

**S1.11**: Stage 10 — Manager Saves Response for Orchestrator
- Manager stores final response in `WorkingMemoryBackend`.
- Verify trace logged.
- PASS if saved, FAIL if exception.

**S1.12**: Stage 11 — Orchestrator: Load Model + Respond to User
- Load model into adapter. Orchestrator reads final response.
- Formats and returns to user.
- **Unload model** via adapter `unload()`.
- PASS if complete response delivered, FAIL if exception.

**S1.13**: Stage 12 — Memory Tracks All Interactions
- Query `TraceMemoryBackend` for events with correlation ID.
- Count: should be ≥ 14 (one per stage).
- Query `EpisodicMemoryBackend` for task episode.
- PASS if all tracked, FAIL if incomplete.

---

## S2 — Create `scripts/diagnostics/run.py`
- **S2.1**: Entry point: `python scripts/diagnostics/run.py [--auto-fix]`
- **S2.2**: Output: `[N/12] Name ... PASS/SKIP/FAIL (details)`
- **S2.3**: Final line: `Result: X PASS, Y FAIL, Z SKIP`
- **S2.4**: With `--auto-fix`: prompt `[Y/n]` for each missing service, install via Devin terminal

---

## S3 — Create `scripts/diagnostics/installers.py`
- **S3.1**: `install_ollama()`: Run `winget install Ollama.Ollama` or download from ollama.com
- **S3.2**: `start_ollama()`: Run `ollama serve` in background subprocess
- **S3.3**: `pull_model(model_name)`: Run `ollama pull {model_name}`
- **S3.4**: `install_llama_cpp()`: Verify `llama-cpp-python` in requirements.txt, pip install if missing

---

## S4 — Test harness
- **S4.1**: Run `python scripts/diagnostics/run.py` on Executor machine
- **S4.2**: Record results in execution log
- **S4.3**: Fix any FAIL before proceeding

---

## S5 — Scan and Close
- **S5.1**: Run `pytest` — must be ≥90%, no failures
- **S5.2**: Run `ruff` — must be 0 errors
- **S5.3**: Run `mypy` on `scripts/diagnostics/` — 0 errors
- **S5.4**: Update `CHANGELOG.md`, `PLANS.md`, `DEBT.md`
- **S5.5**: Run `/verify`, `/close`
