"""Integration tests for the Web UI — load real manifests, test real endpoints.

These tests catch bugs that unit tests with mocks miss:
- Manifest format mismatch (Bug 1: [component] table vs flat)
- Dispatch route signature mismatch (Bug 2: wrong kwarg names)
- First-run API 401 handling (Bug 3: HTTPException in middleware → 500)
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def container_no_users() -> Generator:
    """Provide a real container with no registered users (first-run state)."""
    from sovereignai.main import build_container
    from web.main import app

    container = build_container()
    app.state.container = container
    yield container


@pytest.fixture
def client_no_users(_container_no_users: Any) -> TestClient:
    """Provide a TestClient with no registered users (first-run state)."""
    from web.main import app
    return TestClient(app)


@pytest.fixture
def client_authenticated() -> TestClient:
    """Provide a TestClient with a registered and logged-in user."""
    from sovereignai.main import build_container
    from web.main import app

    container = build_container()
    app.state.container = container

    client = TestClient(app)
    # Register via API (first-run setup)
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200, f"Register failed: {response.text}"
    # Login via API to get session cookie
    response = client.post(
        "/api/auth/login",
        json={"username": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    assert "session_id" in response.cookies, "No session cookie set"

    # Manually set the cookie for subsequent requests
    client.cookies.set("session_id", response.cookies["session_id"])
    return client


class TestManifestLoading:
    """Bug 1: manifests must load correctly (table format unwrap)."""

    def test_real_manifests_parse(self) -> None:
        """Verify the actual manifest files in skills/ and adapters/ parse without error."""
        from sovereignai.shared.manifest_parser import parse_manifest

        manifest_paths = [
            Path("skills/user/websearch_skill/manifest.toml"),
            Path("adapters/external/ollama_adapter/manifest.toml"),
        ]
        for mp in manifest_paths:
            manifest = parse_manifest(mp)
            assert manifest.component_id is not None, f"{mp} has no component_id"
            assert manifest.version is not None, f"{mp} has no version"
            assert len(manifest.provides) >= 1, f"{mp} has no capabilities"

    def test_build_container_registers_components(self) -> None:
        """Verify build_container() registers the real manifests in the capability graph."""
        from sovereignai.main import build_container
        from sovereignai.shared.capability_graph import ICapabilityIndex

        container = build_container()
        idx = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
        components = idx.list_all_components()
        component_ids = {str(c.component_id) for c in components}

        assert "websearch_skill" in component_ids, "websearch_skill not registered"
        assert "ollama_adapter" in component_ids, "ollama_adapter not registered"

    def test_flat_format_still_works(self) -> None:
        """Verify flat-format manifests (used by existing tests) still parse after the unwrap fix.

        This ensures backward compatibility with test fixtures that use flat format.
        """
        from sovereignai.shared.manifest_parser import parse_manifest

        manifest_file = Path("test_flat_manifest.toml")
        manifest_file.write_text(
            'component_id = "TestAdapter"\n'
            'version = "1.0.0"\n'
            'author = "test"\n'
            'content_hash = "sha256:abc"\n\n'
            '[[provides]]\n'
            'category = "model_inference"\n'
            'name = "text_generation"\n'
            'version = "1.0.0"\n'
            'priority = 10\n'
        )
        try:
            manifest = parse_manifest(manifest_file)
            assert manifest.component_id == "TestAdapter"
            assert len(manifest.provides) == 1
        finally:
            manifest_file.unlink()


class TestDispatchRoute:
    """Bug 2: /api/dispatch must use correct submit_task kwarg names."""

    def test_dispatch_returns_task_id(self, client_authenticated: TestClient) -> None:
        """Verify dispatch returns a task_id (not a 500 from wrong kwargs)."""
        response = client_authenticated.post(
            "/api/dispatch",
            json={"message": "test message"},
        )
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )
        data = response.json()
        assert "task_id" in data, f"Response missing task_id: {data}"
        assert "state" in data, f"Response missing state: {data}"


class TestFirstRunAuthHandling:
    """Bug 3: unauthenticated API requests must return 401, not 500."""

    def test_api_capabilities_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify API endpoints return 401 (not 500) when no users are registered."""
        response = client_no_users.get("/api/capabilities")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data, f"Response missing detail: {data}"

    def test_api_workers_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify /api/workers returns 401 (not 500) on first run."""
        response = client_no_users.get("/api/workers")
        assert response.status_code == 401

    def test_api_tasks_returns_401_on_first_run(self, client_no_users: TestClient) -> None:
        """Verify /api/tasks returns 401 (not 500) on first run."""
        response = client_no_users.get("/api/tasks")
        assert response.status_code == 401

    def test_authenticated_capabilities_returns_200(self, client_authenticated: TestClient) -> None:
        """Verify /api/capabilities returns 200 (with content) after login."""
        response = client_authenticated.get("/api/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # After Bug 1 fix, there should be at least 2 capabilities (web_search + ollama)
        assert len(data) >= 2, f"Expected >=2 capabilities, got {len(data)}: {data}"
