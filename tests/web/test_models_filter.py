"""Test models catalog filtering."""
from fastapi.testclient import TestClient


def test_category_filter(client: TestClient) -> None:
    """Verify category filter works."""
    response = client.get("/api/models/catalog?db=huggingface&category=text-generation")
    assert response.status_code == 200
    data = response.json()
    # Verify all returned models match the category
    if data.get("models"):
        for model in data["models"]:
            assert model.get("category") == "text-generation"


def test_vram_fit_filter(client: TestClient) -> None:
    """Verify VRAM fit filter works."""
    response = client.get("/api/models/catalog?db=huggingface&vram_fit=true")
    assert response.status_code == 200
    data = response.json()
    # Verify all returned models fit in VRAM
    if data.get("models"):
        for model in data["models"]:
            assert model.get("vram_badge") == "VRAM"


def test_quant_level_filter(client: TestClient) -> None:
    """Verify quant level filter works."""
    response = client.get("/api/models/catalog?db=huggingface&quant_level=40")
    assert response.status_code == 200
    data = response.json()
    # Verify all returned models match the quant level
    if data.get("models"):
        for model in data["models"]:
            assert model.get("quant_level") == 40


def test_search_filter(client: TestClient) -> None:
    """Verify search filter works."""
    response = client.get("/api/models/catalog?db=huggingface&search=llama")
    assert response.status_code == 200
    data = response.json()
    # Verify all returned models contain the search term
    if data.get("models"):
        for model in data["models"]:
            assert "llama" in model.get("name", "").lower()
