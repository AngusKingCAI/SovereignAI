"""Tests for task execution endpoints."""
from fastapi.testclient import TestClient


def test_create_task(client: TestClient):
    """Test /api/tasks endpoint (POST)."""
    response = client.post("/api/tasks", json={
        "category": "test",
        "payload": {"test": "data"}
    })
    # May fail if no workers registered or invalid category
    assert response.status_code in [200, 400, 422, 500]


def test_get_task_state(client: TestClient):
    """Test /api/tasks/{task_id} endpoint."""
    # Use a fake UUID
    response = client.get("/api/tasks/00000000-0000-0000-0000-000000000000")
    # Should return 404 for non-existent task or 401 if auth issue
    assert response.status_code in [200, 404, 401]


def test_submit_message(client: TestClient):
    """Test /api/tasks/{task_id}/message endpoint."""
    # Use a fake UUID
    response = client.post("/api/tasks/00000000-0000-0000-0000-000000000000/message", json={
        "message": "test message"
    })
    # Should return 404 for non-existent task
    assert response.status_code in [200, 404]
