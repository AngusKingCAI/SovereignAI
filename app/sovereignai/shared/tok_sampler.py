from __future__ import annotations

from app.sovereignai.shared.hardware_probe import (
    MEMORY_BANDWIDTH_GBPS,
)
from app.sovereignai.shared.types import HardwareSnapshot, ModelEntry


def estimate_tok_s(model: ModelEntry, hw: HardwareSnapshot) -> float | None:
    if not model.file_size_bytes:
        return None

    if not hw.gpus:
        return None

    max_bandwidth_bytes_per_s = 0.0
    for gpu in hw.gpus:
        memory_type = gpu.memory_type
        if memory_type is None:
            continue

        bandwidth_gbps = float(MEMORY_BANDWIDTH_GBPS.get(memory_type, 512))
        bandwidth_bytes_per_s = bandwidth_gbps * 1e9
        if bandwidth_bytes_per_s > max_bandwidth_bytes_per_s:
            max_bandwidth_bytes_per_s = bandwidth_bytes_per_s

    if max_bandwidth_bytes_per_s == 0:
        return None

    tok_s = max_bandwidth_bytes_per_s / model.file_size_bytes * 0.65
    return tok_s
