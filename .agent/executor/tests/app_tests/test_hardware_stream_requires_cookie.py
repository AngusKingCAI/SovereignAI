from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from app.web.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_hardware_stream_requires_cookie(client: TestClient) -> None:
    if not os.environ.get("SOVEREIGNAI_FULL_STACK_TESTS"):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")

    response = client.get("/api/hardware/stream")
    assert response.status_code == 401
