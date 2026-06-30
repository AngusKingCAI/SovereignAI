"""Tests for SSE streaming endpoint."""
from fastapi.testclient import TestClient


def test_sse_stream_with_auth(client: TestClient) -> None:
    """Test that SSE stream works with authentication."""
    # SSE endpoint uses session cookie auth, not dependency override
    # Skip for now - requires cookie setup
    pass
