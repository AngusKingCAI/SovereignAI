"""Pytest configuration and shared fixtures."""
import os
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

import web.main

# Set test mode BEFORE any imports that trigger build_container
os.environ["SOVEREIGNAI_TEST_MODE"] = "1"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app with auth bypass."""
    # Set dependency override before creating the client
    web.main.app.dependency_overrides[web.main.get_current_user] = (
        lambda request: MagicMock(username="test")
    )
    client = TestClient(web.main.app)
    yield client
    # Clean up
    web.main.app.dependency_overrides.clear()


@pytest.fixture
def fresh_auth() -> Any:
    """Provide a fresh AuthMiddleware with no persisted users.

    Tests that need to register users should use this fixture instead of
    retrieving AuthMiddleware from the container (which has persisted users).
    """
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.trace_emitter import TraceEmitter
    trace = TraceEmitter()
    auth = AuthMiddleware(trace=trace)
    # Clear any loaded users to ensure a fresh slate for tests
    auth._password_hashes.clear()
    auth._salts.clear()
    return auth
