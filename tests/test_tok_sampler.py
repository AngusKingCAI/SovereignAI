from __future__ import annotations

from sovereignai.shared.hardware_probe import GPU_MEMORY_TYPE_MAP, MEMORY_BANDWIDTH_GBPS
from sovereignai.shared.tok_sampler import estimate_tok_s
from sovereignai.shared.types import GpuInfo, HardwareSnapshot, ModelEntry


def test_estimate_tok_s_with_gpu() -> None:
    model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=4_800_000_000,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=1008,
        disks=[],
        gpus=[
            GpuInfo(
                name="RTX 4090",
                vram_total_mb=24576,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type="GDDR6X",
            )
        ],
    )

    result = estimate_tok_s(model, hw)
    assert result is not None
    expected = (1008 * 1e9) / 4_800_000_000 * 0.65
    assert abs(result - expected) < 0.1


def test_estimate_tok_s_no_gpu() -> None:
    model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=4_800_000_000,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=512,
        disks=[],
        gpus=[],
    )

    result = estimate_tok_s(model, hw)
    assert result is None


def test_estimate_tok_s_zero_file_size() -> None:
    model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=0,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=1008,
        disks=[],
        gpus=[
            GpuInfo(
                name="RTX 4090",
                vram_total_mb=24576,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type="GDDR6X",
            )
        ],
    )

    result = estimate_tok_s(model, hw)
    assert result is None


def test_estimate_tok_s_q4_vs_fp16_ratio() -> None:
    q4_model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=4_800_000_000,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    fp16_model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="fp16",
        file_size_bytes=16_000_000_000,
        vram_required_mb=16000,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=1008,
        disks=[],
        gpus=[
            GpuInfo(
                name="RTX 4090",
                vram_total_mb=24576,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type="GDDR6X",
            )
        ],
    )

    q4_result = estimate_tok_s(q4_model, hw)
    fp16_result = estimate_tok_s(fp16_model, hw)

    assert q4_result is not None
    assert fp16_result is not None
    ratio = q4_result / fp16_result
    assert 3.0 < ratio < 5.0


def test_estimate_tok_s_multi_gpu_max_bandwidth() -> None:
    model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=4_800_000_000,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=2000,
        disks=[],
        gpus=[
            GpuInfo(
                name="RTX 4060",
                vram_total_mb=8192,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type="GDDR6",
            ),
            GpuInfo(
                name="A100",
                vram_total_mb=81920,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type="HBM2",
            ),
        ],
    )

    result = estimate_tok_s(model, hw)
    assert result is not None
    expected = (2000 * 1e9) / 4_800_000_000 * 0.65
    assert abs(result - expected) < 0.1


def test_estimate_tok_s_gpu_unknown_memory_type() -> None:
    model = ModelEntry(
        org="meta",
        family="llama-3-8b",
        version="instruct",
        quant="q4",
        file_size_bytes=4_800_000_000,
        vram_required_mb=4800,
        num_layers=32,
        category="llm",
        source_db="huggingface",
    )

    hw = HardwareSnapshot(
        cpu_percent=10.0,
        ram_percent=50.0,
        ram_used_gb=8.0,
        ram_total_gb=16.0,
        ram_available_gb=8.0,
        memory_bandwidth_gbps=512,
        disks=[],
        gpus=[
            GpuInfo(
                name="Unknown GPU",
                vram_total_mb=8192,
                vram_used_mb=0,
                utilization_percent=0.0,
                memory_type=None,
            )
        ],
    )

    result = estimate_tok_s(model, hw)
    assert result is None
