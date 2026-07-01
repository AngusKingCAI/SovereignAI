from __future__ import annotations

QUANT_PRIORITY: list[str] = [
    "q4_K_M",
    "q4_K_S",
    "q5_K_M",
    "q5_K_S",
    "q6_K",
    "q8_0",
]


def select_best_quant(available: list[str]) -> str | None:
    for quant in QUANT_PRIORITY:
        if quant in available:
            return quant
    return None
