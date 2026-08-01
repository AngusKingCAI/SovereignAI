Depends on: Plan 17
Vision principles: P2 (everything pluggable), P8 (UIs separate processes), P4 (local-first)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-17 on origin)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR69 (Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/), commit before coding

## S1 — Models catalog + tok/s estimation (server-side canonical)
- S1.1: Create sovereignai/shared/model_catalog.py — ModelCatalog class. Constructor: database_registry, trace. Method list_models(filters: ModelFilter) -> list[ModelEntry] aggregates from all registered DatabaseProviders. Filter: search (substring), category, vram_fit_max_mb, quant_level_min (accepts q2/q3/q4/q5/q6/q8/fp16; keeps models with quant ≥ specified, e.g. q4 keeps q4/q5/q6/q8/fp16).
- S1.2: Create sovereignai/shared/tok_sampler.py — `estimate_tok_s(model: ModelEntry, hw: HardwareSnapshot) -> float | None`. Guard: `if not model.file_size_bytes: return None`. Formula: `bandwidth_bytes_per_s / model.file_size_bytes * 0.65`. (file_size_bytes already encodes quantization — do NOT multiply by active_bytes_per_param; that double-counts.) bandwidth_bytes_per_s: lookup GPU memory type via GPU_MEMORY_TYPE_MAP (defined in hardware_probe.py, imported here), convert peak GB/s to bytes/s (1 GB/s = 1e9 bytes/s). Return None if hw has no GPUs or bandwidth unknown.
- S1.3: Create sovereignai/shared/types.py addition: `ModelFilter` dataclass (search: str | None, category: str | None, vram_fit_max_mb: int | None, quant_level_min: str | None), `HardwareSnapshot` dataclass (cpu_percent, ram_percent, ram_used_gb, ram_total_gb, ram_available_gb, memory_bandwidth_gbps, disks: list[DiskUsage], gpus: list[GpuInfo]), `GpuInfo` dataclass (name, vram_total_mb, vram_used_mb, utilization_percent, memory_type: str | None).
- S1.4: Run /verify on each. Add tests/test_model_catalog.py and tests/test_tok_sampler.py with synthetic entries + snapshots. Include worked-example test: known input → known output (pins formula dimensionally). Verify q4 vs fp16 ratio is ~4x (not 16x). Include test: file_size_bytes=0 returns None (no ZeroDivisionError).

## S2 — Hardware probe extension (multi-GPU, live sampling)
- S2.1: Edit sovereignai/shared/hardware_probe.py — add `sample() -> HardwareSnapshot`. Uses psutil for CPU/RAM/disk (ram_available_gb via psutil.virtual_memory().available). Uses pynvml for NVIDIA GPUs.
- S2.2: Guard pynvml import in try/except. If unavailable: gpus=[] and trace WARN "pynvml unavailable — GPU detection skipped".
- S2.3: In sovereignai/shared/hardware_probe.py, add `GPU_MEMORY_TYPE_MAP: dict[str, str]` keyed by GPU name substrings (e.g. "RTX 4090": "GDDR6X", "RTX 3080": "GDDR6X", "RTX 4060": "GDDR6", "A100": "HBM2", default: None). Add `MEMORY_BANDWIDTH_GBPS: dict[str, int]` (GDDR6=768, GDDR6X=1008, HBM2=2000, DDR5=480, default=512). Export both from hardware_probe.py for import by tok_sampler.py. Lookup: find first matching substring in gpu.name → memory_type → bandwidth. Document as best-effort placeholder; DEBT.md entry for PCI-ID-based lookup post-Plan-19.
- S2.4: Add txt/requirements.txt: `psutil>=5.9`, `pynvml>=11.5`.
- S2.5: Run /verify. Extend tests/test_hardware_probe.py with sample() coverage and multi-GPU mock fixtures (OR58 real-shape).
- S2.6: Add DEBT.md entry: "GPU bandwidth lookup is substring-based placeholder — replace with PCI-ID lookup post-Plan-19."

## S3 — Capability API hardware methods (OR69 compliance)
- S3.1: Edit sovereignai/shared/capability_api.py — add `sample_hardware() -> HardwareSnapshot` (calls HardwareProbe.sample()) and `stream_hardware() -> AsyncGenerator[HardwareSnapshot, None]` (yields sample() every 1s). These are the only hardware access path for web/.
- S3.2: Add tests/test_capability_api_hardware.py covering sample_hardware() returns HardwareSnapshot; stream_hardware() yields at 1Hz.

## S4 — Models panel UI (server-side tok/s)
WILL edit UI elements:
- web/templates/index.html: replace `<section id="panel-models">` with: filter bar (search, category dropdown, VRAM-fit checkbox, quant-level dropdown), sortable table (Org, Family, Version, Quant, Size, VRAM, Tok/s [estimated], Source), empty-state div.
- web/static/app.js: add `loadModelsPanel()` fetching /api/models (includes tok_s_estimated field) + /api/hardware, renders rows, applies VRAM badge class, wires column sort. Display tok/s verbatim from server with "~" prefix and "(estimated)" tooltip; render "—" when tok_s_estimated is None. No client-side tok/s computation.
- web/static/styles.css: `.models-table`, `.vram-badge-vram` (green), `.vram-badge-cpu-offload` (amber #CC8400 AA), `.vram-badge-disk` (blue), `.vram-badge-na` (grey), `.empty-state`. Drop "VRAM+RAM" badge — use "CPU-offload" instead.
- web/main.py: add `GET /api/models` accepting query params (search, category, vram_fit, quant_level) -> list[ModelEntryDTO]. Server computes tok_s_estimated via tok_sampler.estimate_tok_s() using capability_api.sample_hardware() (NOT direct HardwareProbe import — OR69). Add `GET /api/hardware` calling capability_api.sample_hardware(); add `GET /api/hardware/stream` SSE calling capability_api.stream_hardware().
- web/schemas.py: add `ModelEntryDTO` (includes tok_s_estimated: float | None), `GpuInfoDTO`, `HardwareSnapshotDTO`, `DiskUsageDTO`.
- S4.1: Edit each file per WILL list. Run /verify after each.
- S4.2: Add tests/test_models_panel.py covering: GET /api/models returns 200 with tok_s_estimated populated; VRAM badge logic (VRAM if vram_required_mb ≤ max(gpus[].vram_total_mb) * 0.9; CPU-offload if ≤ ram_available_gb * 1024 * 0.9; Disk if fits free disk; N/A otherwise); empty-state when no models; tok_s_estimated None when no GPU; DTO shape has tok_s_estimated: float | None.
- S4.3: Add tests/test_hardware_panel.py covering: SSE stream returns 200 and emits JSON frames; multi-GPU DTO; disk enumeration; generator terminates on disconnect.

## Closing
- Run /close (full suite, coverage ≥90% per OR43, all AR checks, browser smoke test on Models + Hardware panels with screenshots to logs/screenshots/prompt-18/, spec_match.py, commit, tag prompt-18, push).
