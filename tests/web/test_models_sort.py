"""Test models catalog sorting."""
from fastapi.testclient import TestClient


def test_sort_by_name_ascending(client: TestClient) -> None:
    """Verify name column sorts ascending."""
    response = client.get("/api/models/catalog?db=huggingface&sort=name&dir=asc")
    assert response.status_code == 200
    data = response.json()
    # Verify models are sorted by name ascending
    if data.get("models"):
        names = [m.get("name", "") for m in data["models"]]
        assert names == sorted(names)


def test_sort_by_name_descending(client: TestClient) -> None:
    """Verify name column sorts descending."""
    response = client.get("/api/models/catalog?db=huggingface&sort=name&dir=desc")
    assert response.status_code == 200
    data = response.json()
    # Verify models are sorted by name descending
    if data.get("models"):
        names = [m.get("name", "") for m in data["models"]]
        assert names == sorted(names, reverse=True)


def test_sort_by_size_ascending(client: TestClient) -> None:
    """Verify size column sorts ascending."""
    response = client.get("/api/models/catalog?db=huggingface&sort=size&dir=asc")
    assert response.status_code == 200
    data = response.json()
    # Verify models are sorted by size ascending
    if data.get("models"):
        sizes = [m.get("size_gb", 0) for m in data["models"]]
        assert sizes == sorted(sizes)


def test_sort_by_size_descending(client: TestClient) -> None:
    """Verify size column sorts descending."""
    response = client.get("/api/models/catalog?db=huggingface&sort=size&dir=desc")
    assert response.status_code == 200
    data = response.json()
    # Verify models are sorted by size descending
    if data.get("models"):
        sizes = [m.get("size_gb", 0) for m in data["models"]]
        assert sizes == sorted(sizes, reverse=True)
