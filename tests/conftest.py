"""Pytest configuration and shared fixtures."""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import web.main


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app with auth bypass."""
    # Set dependency override before creating the client
    web.main.app.dependency_overrides[web.main.get_current_user] = (
        lambda request: MagicMock(username="test")
    )
    client = TestClient(web.main.app)
    yield client
    # Clean up
    web.main.app.dependency_overrides.clear()
