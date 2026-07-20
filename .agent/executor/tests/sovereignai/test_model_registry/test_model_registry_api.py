from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sovereignai.model_registry.api import router
from sovereignai.model_registry.database import initialize_database


@pytest.fixture
def test_db(tmp_path: Path) -> Path:
    """Create a test database with sample data."""
    db_path = tmp_path / "test.db"
    conn = initialize_database(db_path)

    # Insert sample provider
    conn.execute(
        """
        INSERT INTO providers (id, name, api_base_url, auth_type, is_enabled)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("openai", "OpenAI", "https://api.openai.com/v1", "bearer_token", 1),
    )

    # Insert sample family
    conn.execute(
        """
        INSERT INTO families (id, provider_id, name, description)
        VALUES (?, ?, ?, ?)
        """,
        ("openai-gpt4", "openai", "GPT-4", "GPT-4 family"),
    )

    # Insert sample model
    conn.execute(
        """
        INSERT INTO models (id, family_id, name)
        VALUES (?, ?, ?)
        """,
        ("gpt-4-turbo", "openai-gpt4", "GPT-4 Turbo"),
    )

    # Insert sample model version
    conn.execute(
        """
        INSERT INTO model_versions (
            id, model_id, version_string, release_date, is_latest,
            context_window, supports_vision, supports_tools, capabilities
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "gpt-4-turbo-2024-04-09",
            "gpt-4-turbo",
            "2024-04-09",
            "2024-04-09",
            1,
            128000,
            1,
            1,
            "{}",
        ),
    )

    # Insert sync run with recent date to avoid stale status
    recent_time = datetime.now() - timedelta(hours=1)
    conn.execute(
        """
        INSERT INTO sync_runs (provider_id, started_at, completed_at, status, error_class)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("openai", recent_time.isoformat(), recent_time.isoformat(), "SUCCESS", None),
    )

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def client(test_db):  # type: ignore[no-untyped-def]
    """Create a test client with mocked database."""
    from sovereignai.model_registry import api

    # Mock the database connection
    original_get_db = api.get_db_connection

    def mock_get_db():  # type: ignore[no-untyped-def]
        return initialize_database(test_db)

    api.get_db_connection = mock_get_db

    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)

    yield TestClient(app)

    api.get_db_connection = original_get_db


def test_list_providers(client) -> None:  # type: ignore[no-untyped-def]
    """Test listing all providers."""
    response = client.get("/api/models/providers")
    assert response.status_code == 200

    providers = response.json()
    assert len(providers) == 1
    assert providers[0]["id"] == "openai"
    assert providers[0]["name"] == "OpenAI"
    assert providers[0]["is_enabled"] is True
    assert providers[0]["last_sync_at"] is not None
    assert providers[0]["sync_status"] == "fresh"


def test_list_models_no_filters(client) -> None:  # type: ignore[no-untyped-def]
    """Test listing models without filters."""
    response = client.get("/api/models")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 1
    assert models[0]["id"] == "gpt-4-turbo-2024-04-09"
    assert models[0]["name"] == "GPT-4 Turbo"
    assert models[0]["family_id"] == "openai-gpt4"
    assert models[0]["family_name"] == "GPT-4"
    assert models[0]["provider_id"] == "openai"
    assert models[0]["version_string"] == "2024-04-09"
    assert models[0]["context_window"] == 128000
    assert models[0]["supports_vision"] is True
    assert models[0]["supports_tools"] is True


def test_list_models_filter_by_provider(client) -> None:  # type: ignore[no-untyped-def]
    """Test filtering models by provider."""
    response = client.get("/api/models?provider_id=openai")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 1
    assert models[0]["provider_id"] == "openai"


def test_list_models_filter_by_family_name(client) -> None:  # type: ignore[no-untyped-def]
    """Test filtering models by family name."""
    response = client.get("/api/models?family_name=gpt")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 1
    assert "gpt" in models[0]["family_name"].lower()


def test_list_models_filter_by_vision(client) -> None:  # type: ignore[no-untyped-def]
    """Test filtering models by vision support."""
    response = client.get("/api/models?supports_vision=true")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 1
    assert models[0]["supports_vision"] is True


def test_list_models_filter_by_tools(client) -> None:  # type: ignore[no-untyped-def]
    """Test filtering models by tools support."""
    response = client.get("/api/models?supports_tools=true")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 1
    assert models[0]["supports_tools"] is True


def test_list_models_no_results(client) -> None:  # type: ignore[no-untyped-def]
    """Test listing models with filters that yield no results."""
    response = client.get("/api/models?provider_id=nonexistent")
    assert response.status_code == 200

    models = response.json()
    assert len(models) == 0


def test_get_model_by_id(client) -> None:  # type: ignore[no-untyped-def]
    """Test getting a specific model by ID."""
    response = client.get("/api/models/gpt-4-turbo-2024-04-09")
    assert response.status_code == 200

    model = response.json()
    assert model["id"] == "gpt-4-turbo-2024-04-09"
    assert model["name"] == "GPT-4 Turbo"
    assert model["context_window"] == 128000


def test_get_model_not_found(client) -> None:  # type: ignore[no-untyped-def]
    """Test getting a non-existent model."""
    response = client.get("/api/models/nonexistent")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_trigger_sync_success(client) -> None:  # type: ignore[no-untyped-def]
    """Test triggering sync for a valid provider."""
    from sovereignai.model_registry.adapters import ADAPTER_REGISTRY

    # Ensure openai is in registry
    if "openai" not in ADAPTER_REGISTRY:
        pytest.skip("OpenAI adapter not in registry")

    response = client.post(
        "/api/models/sync",
        json={"provider_id": "openai"}
    )
    assert response.status_code == 200

    result = response.json()
    assert result["status"] == "triggered"
    assert result["provider_id"] == "openai"
    assert "sync triggered" in result["message"].lower()


def test_trigger_sync_not_found(client) -> None:  # type: ignore[no-untyped-def]
    """Test triggering sync for a non-existent provider."""
    response = client.post(
        "/api/models/sync",
        json={"provider_id": "nonexistent"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_trigger_sync_case_insensitive(client) -> None:  # type: ignore[no-untyped-def]
    """Test that provider_id is normalized (case insensitive)."""
    from sovereignai.model_registry.adapters import ADAPTER_REGISTRY

    if "openai" not in ADAPTER_REGISTRY:
        pytest.skip("OpenAI adapter not in registry")

    response = client.post(
        "/api/models/sync",
        json={"provider_id": "OpenAI"}
    )
    assert response.status_code == 200

    result = response.json()
    assert result["provider_id"] == "openai"


def test_trigger_sync_spaces_removed(client) -> None:  # type: ignore[no-untyped-def]
    """Test that spaces are removed from provider_id."""
    from sovereignai.model_registry.adapters import ADAPTER_REGISTRY

    if "openai" not in ADAPTER_REGISTRY:
        pytest.skip("OpenAI adapter not in registry")

    response = client.post(
        "/api/models/sync",
        json={"provider_id": "open ai"}
    )
    assert response.status_code == 200

    result = response.json()
    assert result["provider_id"] == "openai"
