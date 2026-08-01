Depends on: Plan 17
Vision principles: P2 (everything pluggable), P8 (UIs separate processes), P4 (local-first)
Open questions resolved: none

## S0 — Opening
- S0.1: Run /open (verify tag prompt-17 on origin)
- S0.2: Read AGENTS.md in full
- S0.2.5: Re-read AGENTS.md if S0.3 adds rules
- S0.3: Add OR69 (Models panel and Hardware panel must consume capability API only — no direct DatabaseRegistry/ServiceRegistry/HardwareProbe imports from web/), commit before coding

## S1 — Models catalog + tok/s estimation
- S1.1: Create sovereignai/shared/model_catalog.py — ModelCatalog class. Constructor: database_registry, trace. Method list_models(filters: ModelFilter) -> list[ModelEntry] aggregates from all registered DatabaseProviders. Filter: search (substring), category, vram_fit_max_mb, quant_level_min.
- S1.2: Create sovereignai/shared/tok_sampler.py — `estimate_tok_s(model: ModelEntry, hw: HardwareSnapshot) -> float`. Formula: `hw.memory_bandwidth_gbps * 1e9 / (model.vram_required_mb * 1e6 * active_bytes_per_param(model.quant)) * 0.65`. active_bytes_per_param: q4=0.5, q5=0.625, q8=1.0, fp16=2.0, unknown=1.5.
- S1.3: Create sovereignai/shared/types.py addition: `ModelFilter` dataclass (search: str | None, category: str | None, vram_fit_max_mb: int | None, quant_level_min: str | None), `HardwareSnapshot` dataclass (cpu_percent, ram_percent, ram_used_gb, ram_total_gb, memory_bandwidth_gbps, disks: list[DiskUsage], gpus: list[GpuInfo]).
- S1.4: Run /verify on each. Add tests/test_model_catalog.py and tests/test_tok_sampler.py with synthetic entries + snapshots.

## S2 — Hardware probe extension (multi-GPU, live sampling)
- S2.1: Edit sovereignai/shared/hardware_probe.py — add `sample() -> HardwareSnapshot`. Uses psutil for CPU/RAM/disk. Uses pynvml for NVIDIA GPUs (NVIDIA only in v1 — IGPU + DGPU both enumerated if pynvml sees them).
- S2.2: Guard pynvml import in try/except. If unavailable, gpus=[] and trace WARN "pynvml unavailable — GPU detection skipped".
- S2.3: memory_bandwidth_gbps: lookup table per GPU model name (placeholder: DDR5=480, LPDDR5=640, GDDR6=768, GDDR6X=1008, default=512). Documented in code (no docstring per AR17 — use comment).
- S2.4: Add txt/requirements.txt: `psutil>=5.9`, `pynvml>=11.5`.
- S2.5: Run /verify. Extend tests/test_hardware_probe.py with sample() coverage and multi-GPU mock fixtures (OR58 real-shape).

## S3 — Models panel UI
WILL edit UI elements:
- web/templates/index.html: replace `<section id="panel-models">` content with: filter bar (search input, category dropdown, VRAM-fit checkbox, quant-level dropdown), sortable table (Org, Family, Version, Quant, Size, VRAM, Tok/s, Source), empty-state div.
- web/static/app.js: add `loadModelsPanel()` fetching /api/models + /api/hardware, renders rows, computes tok/s client-side, applies VRAM badge class (VRAM / VRAM+RAM / Diskspace / N/A), wires column sort.
- web/static/styles.css: `.models-table`, `.vram-badge-vram` (green), `.vram-badge-ram` (amber), `.vram-badge-disk` (blue), `.vram-badge-na` (grey), `.empty-state`.
- web/main.py: add `GET /api/models` accepting query params (search, category, vram_fit, quant_level) -> list[ModelEntryDTO]. Extend `GET /api/hardware` to return gpus list.
- web/schemas.py: add `ModelEntryDTO`, `GpuInfoDTO`.
- S3.1: Edit each file per WILL list. Run /verify after each.
- S3.2: Add tests/test_models_panel.py covering: GET /api/models returns 200 with filtered list; VRAM badge logic; tok/s calculation; empty-state when DatabaseRegistry has no models.

## S4 — Hardware panel UI (Task Manager style)
WILL edit UI elements:
- web/templates/index.html: replace `<section id="panel-hardware">` content with: CPU gauge (percent + freq), RAM gauge (used/total), GPU cards (one per detected GPU: name, VRAM bar, utilization bar), Disk list (path, used/total bar).
- web/static/app.js: add `loadHardwarePanel()` subscribing to /api/hardware/stream SSE, updating gauges/bars at 1Hz.
- web/static/styles.css: `.hw-gauge`, `.hw-bar`, `.hw-bar-fill`, `.gpu-card`, `.disk-row`.
- web/main.py: add `GET /api/hardware/stream` SSE endpoint emitting HardwareSnapshotDTO every 1s.
- web/schemas.py: add `HardwareSnapshotDTO`, `DiskUsageDTO`.
- S4.1: Edit each file per WILL list. Run /verify after each.
- S4.2: Add tests/test_hardware_panel.py covering: SSE stream returns 200 and emits JSON frames; multi-GPU DTO shape; disk enumeration.

## Closing
- Run /close (full suite, coverage ≥90%, all AR checks, browser smoke test on Models + Hardware panels, spec_match.py, commit, tag prompt-18, push).
