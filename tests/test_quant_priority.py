from __future__ import annotations

from sovereignai.shared.quant_priority import QUANT_PRIORITY, select_best_quant


def test_quant_priority_order() -> None:
    assert QUANT_PRIORITY == [
        "q4_K_M",
        "q4_K_S",
        "q5_K_M",
        "q5_K_S",
        "q6_K",
        "q8_0",
    ]


def test_select_best_quant() -> None:
    available = ["q8_0", "q4_K_M", "q5_K_S"]
    assert select_best_quant(available) == "q4_K_M"


def test_select_best_quant_partial_match() -> None:
    available = ["q5_K_S", "q6_K"]
    assert select_best_quant(available) == "q5_K_S"


def test_select_best_quant_no_match() -> None:
    available = ["q2_K", "f16"]
    assert select_best_quant(available) is None


def test_select_best_quant_empty() -> None:
    assert select_best_quant([]) is None


def test_select_best_quant_q6_k() -> None:
    available = ["q6_K"]
    assert select_best_quant(available) == "q6_K"
