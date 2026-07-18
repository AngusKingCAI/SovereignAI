from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sovereignai.main import build_container
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.types import HardwareSnapshot
from app.web.main import app


@pytest.fixture
def client() -> TestClient:
    from app.web.main import app
    container = build_container()
    app.state.container = container
    return TestClient(app)


@pytest.fixture
def container(client: TestClient) -> Any:
    return client.app.state.container  # type: ignore[attr-defined]


@pytest.mark.skip(reason="Hardware panel tests require full web stack - skipped per S7.4")
def test_hardware_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/api/hardware")
    assert response.status_code == 401


@pytest.mark.skip(reason="Hardware panel tests require full web stack - skipped per S7.4")
def test_hardware_endpoint_returns_snapshot(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    response = client.get("/api/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data
    assert "ram_percent" in data
    assert "disks" in data
    assert "gpus" in data
    assert isinstance(data["disks"], list)
    assert isinstance(data["gpus"], list)


@pytest.mark.skip(reason="Hardware panel tests require full web stack - skipped per S7.4")
def test_hardware_stream_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/api/hardware/stream")
    assert response.status_code == 401


@pytest.mark.timeout(5)
@pytest.mark.skip(reason="Hardware panel tests require full web stack - skipped per S7.4")
def test_hardware_stream_endpoint_sse(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    # Mock stream_hardware to return a finite generator
    async def mock_stream_hardware(self: CapabilityAPI) -> AsyncGenerator[HardwareSnapshot, None]:
        yield self.sample_hardware()

    with patch.object(
        CapabilityAPI, "stream_hardware", mock_stream_hardware
    ), client.stream("GET", "/api/hardware/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        first_line = next(response.iter_lines())
        assert first_line is not None
        assert len(first_line) > 0


@pytest.mark.timeout(10)
@pytest.mark.skip(reason="Hardware panel tests require full web stack - skipped per S7.4")
def test_hardware_stream_sse_multiple_events(client: TestClient, container: Any) -> None:
    from sovereignai.shared.auth import AuthMiddleware
    from sovereignai.shared.capability_api import CapabilityAPI

    auth = container.retrieve(AuthMiddleware)
    auth.register_user("testuser", "testpass")
    session = auth.login("testuser", "testpass")

    client.cookies.set("session_id", session.token)

    # Mock stream_hardware to yield multiple snapshots
    async def mock_stream_hardware(self: CapabilityAPI) -> AsyncGenerator[HardwareSnapshot, None]:
        for _ in range(3):
            yield self.sample_hardware()
            await asyncio.sleep(0.1)

    with patch.object(
        CapabilityAPI, "stream_hardware", mock_stream_hardware
    ), client.stream("GET", "/api/hardware/stream") as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
                if len(lines) >= 3:
                    break

        assert len(lines) >= 1
        assert all(line is not None for line in lines)
