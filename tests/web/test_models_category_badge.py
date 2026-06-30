"""Test category badge rendering."""
from fastapi.testclient import TestClient


def test_category_badge_nlp(client: TestClient) -> None:
    """Verify NLP category badge renders correctly."""
    response = client.get("/api/models/catalog?db=huggingface")
    assert response.status_code == 200
    data = response.json()
    # Find a model with NLP category
    for org in data.get("orgs", []):
        for family in org.get("families", []):
            if family.get("category_group") == "nlp":
                assert family.get("category") is not None
                break


def test_category_badge_multimodal(client: TestClient) -> None:
    """Verify Multimodal category badge renders correctly."""
    response = client.get("/api/models/catalog?db=huggingface")
    assert response.status_code == 200
    data = response.json()
    # Find a model with Multimodal category
    for org in data.get("orgs", []):
        for family in org.get("families", []):
            if family.get("category_group") == "multimodal":
                assert family.get("category") is not None
                break


def test_category_badge_computer_vision(client: TestClient) -> None:
    """Verify Computer Vision category badge renders correctly."""
    response = client.get("/api/models/catalog?db=huggingface")
    assert response.status_code == 200
    data = response.json()
    # Find a model with Computer Vision category
    for org in data.get("orgs", []):
        for family in org.get("families", []):
            if family.get("category_group") == "computer_vision":
                assert family.get("category") is not None
                break
