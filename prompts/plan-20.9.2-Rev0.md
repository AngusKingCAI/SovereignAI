Depends on: prompt-20.9.1
Vision principles: 3 (hardware-aware), 6 (efficiency)
Open questions resolved: none

## Clarifications (from S0.9)

1. **nvidia_ml_py3 dependency**: Remove from web layer too. Delete `web/hardware_probe.py` and have web layer consume hardware data exclusively through `CapabilityAPI.sample_hardware()` / `CapabilityAPI.stream_hardware()`. This satisfies AR12 and AR27.

2. **AdapterCapability enum**: Future use only. Add to `sovereignai/shared/types.py` for adapter manifests to declare static capabilities, but don't wire it into hardware probe system. Hardware probe answers "what hardware exists"; AdapterCapability answers "what can this adapter do."

3. **PCI-ID database scope**: Common GPUs only (RTX 20/30/40 series, GTX 16 series, common mobile variants). Keep it small, maintainable, and testable per "wire as you go" principle.

4. **Coverage target scope**: GPU paths only (nvidia-smi subprocess, nvidia-ml-py calls, WMI fallback). Focus on GPU detection paths without inflating scope.

## WILL edit
- `sovereignai/shared/hardware_probe.py` — refactor GPU detection
- `web/hardware_probe.py` — DELETE (web layer to use CapabilityAPI only)
- `tests/test_hardware_probe.py` — add GPU tests, remove pynvml skip stubs
- `sovereignai/shared/types.py` — add AdapterCapability enum (future use)
- `txt/requirements.txt` — remove nvidia_ml_py3
- `DEBT.md` — mark resolved items
- `CHANGELOG.md` — append per OR73
- `PLANS.md` — update baseline
- `prompts/plan-20.9.2-Rev0.md` — move to completed/ at /close

## WILL NOT edit
- TUI panels (handled in 20.9.1), core orchestrator. If scope expands, STOP.

## S0 — Opening

S0.1: Run `/open`. Read `AGENTS.md` in full.
S0.2: Read `DEBT.md`. Identify items this plan resolves.
S0.3: No new rules.
S0.4: Begin Phase 1.

## S1 — Remove nvidia_ml_py3 Dependency

S1.1: Remove `nvidia_ml_py3` from `txt/requirements.txt`
S1.2: Delete pynvml fallback code from `sovereignai/shared/hardware_probe.py`
S1.3: Keep Windows WMI and Linux `/proc` fallbacks
S1.4: Delete `web/hardware_probe.py` (web layer to use CapabilityAPI.sample_hardware() / stream_hardware() only)
S1.5: Commit: `git add -A && git commit -m "refactor: remove nvidia_ml_py3 dependency and web/hardware_probe.py"`

## S2 — Add AdapterCapability Enum

S2.1: Add to `sovereignai/shared/types.py` (future use for adapter manifests):
```python
class AdapterCapability(Enum):
    GPU_COMPUTE = "gpu_compute"
    GPU_MEMORY = "gpu_memory"
    CPU_INFERENCE = "cpu_inference"
    QUANTIZATION = "quantization"
```

S2.2: Commit: `git add -A && git commit -m "feat: add AdapterCapability enum for future adapter capability declarations"`

## S3 — Refactor GPU Detection

S3.1: Replace substring-based GPU bandwidth lookup with PCI-ID database lookup
S3.2: Add `gpu_bandwidth_db.json` with common GPU PCI ID → bandwidth mappings (RTX 20/30/40 series, GTX 16 series, common mobile variants)
S3.3: Update `hardware_probe.py` to use PCI-ID lookup first, fallback to substring
S3.4: Commit: `git add -A && git commit -m "refactor: PCI-ID based GPU bandwidth lookup"`

## S4 — GPU Testing Infrastructure

S4.1: Delete `pytest.skip("pynvml support removed")` stubs from `test_hardware_probe.py`
S4.2: Add mock nvidia-smi for Windows testing
S4.3: Add mock `/proc/driver/nvidia/gpus/` for Linux testing
S4.4: Add mock PCI-ID database for bandwidth tests
S4.5: Target ≥90% coverage on GPU detection paths only (nvidia-smi subprocess, nvidia-ml-py calls, WMI fallback)

S4.6: Commit: `git add -A && git commit -m "test: GPU testing infrastructure with mocks"`

## S5 — Update DEBT.md

S5.1: Mark resolved:
- web/hardware_probe.py nvidia_ml_py3 dependency → Resolved at prompt-20.9.2 (web/hardware_probe.py deleted, web layer uses CapabilityAPI only)
- GPU bandwidth lookup is substring-based placeholder → Resolved at prompt-20.9.2
- hardware_probe.py GPU path coverage gap → Resolved at prompt-20.9.2
- GPU testing infrastructure → Resolved at prompt-20.9.2
- pynvml test refactoring after S3.5 → Resolved at prompt-20.9.2
- AdapterCapability enum for GPU capability probing → Resolved at prompt-20.9.2

S5.2: Commit: `git add -A && git commit -m "docs: mark hardware DEBT items resolved"`

## S6 — /close

S6.1: Run `/close`.
