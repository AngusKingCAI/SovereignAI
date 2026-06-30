"""Tests for the hierarchical models catalog endpoint."""
from fastapi.testclient import TestClient


def test_hierarchical_catalog_orgs(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint returns org list at level 1."""
    response = client.get("/api/models/catalog/hierarchical")
    assert response.status_code == 200
    data = response.json()
    assert "orgs" in data
    assert isinstance(data["orgs"], list)


def test_hierarchical_catalog_families(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint returns families at level 2."""
    response = client.get(
        "/api/models/catalog/hierarchical?org=test-org"
    )
    assert response.status_code == 200
    data = response.json()
    assert "families" in data
    assert isinstance(data["families"], list)


def test_hierarchical_catalog_versions(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint returns versions at level 3."""
    response = client.get(
        "/api/models/catalog/hierarchical?org=test-org&family=test-family"
    )
    assert response.status_code == 200
    data = response.json()
    assert "model_versions" in data
    assert isinstance(data["model_versions"], list)


def test_hierarchical_catalog_variants(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint returns quant variants at level 4."""
    response = client.get(
        "/api/models/catalog/hierarchical?org=test-org&family=test-family&model_version=test-version"
    )
    assert response.status_code == 200
    data = response.json()
    assert "quant_variants" in data
    assert isinstance(data["quant_variants"], list)


def test_hierarchical_catalog_sorting(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint supports sorting."""
    response = client.get(
        "/api/models/catalog/hierarchical?org=test-org&family=test-family&model_version=test-version&sort=size&dir=desc"
    )
    assert response.status_code == 200
    data = response.json()
    assert "quant_variants" in data


def test_hierarchical_catalog_file_type_filter(client: TestClient) -> None:
    """Test that the hierarchical catalog endpoint filters by file type."""
    response = client.get(
        "/api/models/catalog/hierarchical?file_type=gguf"
    )
    assert response.status_code == 200
    data = response.json()
    assert "orgs" in data
