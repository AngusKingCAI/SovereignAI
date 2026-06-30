"""Test hierarchical models catalog endpoint."""
from fastapi.testclient import TestClient


def test_hierarchical_catalog_structure(client: TestClient) -> None:
    """Verify endpoint returns correct hierarchical structure."""
    response = client.get("/api/models/catalog?db=huggingface")
    assert response.status_code == 200
    data = response.json()
    assert "orgs" in data
    assert isinstance(data["orgs"], list)


def test_lazy_loading_org_level(client: TestClient) -> None:
    """Verify lazy loading works at org level."""
    response = client.get("/api/models/catalog?db=huggingface")
    assert response.status_code == 200
    data = response.json()
    # Should return org list without families
    assert all("families" not in org for org in data["orgs"])


def test_lazy_loading_family_level(client: TestClient) -> None:
    """Verify lazy loading works at family level."""
    response = client.get("/api/models/catalog?db=huggingface&org=google")
    assert response.status_code == 200
    data = response.json()
    # Should return families for the specified org
    assert "families" in data or len(data["orgs"]) == 0
