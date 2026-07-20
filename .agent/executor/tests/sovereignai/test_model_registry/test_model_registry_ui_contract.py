from pathlib import Path

import pytest
from sovereignai.model_registry.database import initialize_database
from sovereignai.model_registry.ui_contract import (
    FamilyNode,
    ModelDetailResponse,
    ModelNode,
    ModelTreeResponse,
    ProviderNode,
    VersionNode,
    build_model_tree,
    get_model_detail,
)


@pytest.fixture
def test_db(tmp_path: Path) -> Path:  # type: ignore[no-untyped-def]
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
            '{"function_calling": true}',
        ),
    )

    conn.commit()
    conn.close()

    return db_path


def test_provider_node() -> None:
    """Test ProviderNode model."""
    node = ProviderNode(
        id="openai",
        name="OpenAI",
        is_enabled=True,
        model_count=10,
        last_sync_at="2024-04-09T10:00:00",
        sync_status="fresh",
    )

    assert node.id == "openai"
    assert node.name == "OpenAI"
    assert node.is_enabled is True
    assert node.model_count == 10


def test_family_node() -> None:
    """Test FamilyNode model."""
    node = FamilyNode(
        id="gpt-4",
        provider_id="openai",
        name="GPT-4",
        description="GPT-4 family",
        model_count=5,
    )

    assert node.id == "gpt-4"
    assert node.provider_id == "openai"
    assert node.model_count == 5


def test_model_node() -> None:
    """Test ModelNode model."""
    node = ModelNode(
        id="gpt-4-turbo",
        family_id="gpt-4",
        name="GPT-4 Turbo",
        version_count=3,
    )

    assert node.id == "gpt-4-turbo"
    assert node.family_id == "gpt-4"
    assert node.version_count == 3


def test_version_node() -> None:
    """Test VersionNode model."""
    node = VersionNode(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        version_string="2024-04-09",
        release_date="2024-04-09",
        is_latest=True,
        context_window=128000,
        supports_vision=True,
        supports_tools=True,
    )

    assert node.id == "gpt-4-turbo-2024-04-09"
    assert node.is_latest is True
    assert node.context_window == 128000


def test_model_tree_response() -> None:
    """Test ModelTreeResponse model."""
    response = ModelTreeResponse(
        providers=[
            ProviderNode(
                id="openai",
                name="OpenAI",
                is_enabled=True,
                model_count=10,
                last_sync_at="2024-04-09T10:00:00",
                sync_status="fresh",
            )
        ]
    )

    assert len(response.providers) == 1
    assert response.providers[0].id == "openai"


def test_model_detail_response() -> None:
    """Test ModelDetailResponse model."""
    response = ModelDetailResponse(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        family_id="gpt-4",
        provider_id="openai",
        version_string="2024-04-09",
        release_date="2024-04-09",
        is_latest=True,
        context_window=128000,
        supports_vision=True,
        supports_tools=True,
        capabilities={"function_calling": True},
        pricing=None,
    )

    assert response.id == "gpt-4-turbo-2024-04-09"
    assert response.capabilities == {"function_calling": True}
    assert response.pricing is None


def test_build_model_tree(test_db) -> None:  # type: ignore[no-untyped-def]
    """Test building model tree from database."""
    conn = initialize_database(test_db)

    tree = build_model_tree(conn)

    assert len(tree.providers) == 1
    assert tree.providers[0].id == "openai"
    assert tree.providers[0].name == "OpenAI"
    assert tree.providers[0].model_count == 1

    conn.close()


def test_build_model_tree_empty(test_db) -> None:  # type: ignore[no-untyped-def]
    """Test building model tree with no data."""
    db_path = test_db.parent / "empty.db"
    conn = initialize_database(db_path)

    tree = build_model_tree(conn)

    assert len(tree.providers) == 0

    conn.close()


def test_get_model_detail(test_db) -> None:  # type: ignore[no-untyped-def]
    """Test getting model detail from database."""
    conn = initialize_database(test_db)

    detail = get_model_detail(conn, "gpt-4-turbo-2024-04-09")

    assert detail is not None
    assert detail.id == "gpt-4-turbo-2024-04-09"
    assert detail.model_id == "gpt-4-turbo"
    assert detail.family_id == "openai-gpt4"
    assert detail.provider_id == "openai"
    assert detail.context_window == 128000
    assert detail.supports_vision is True
    assert detail.supports_tools is True
    assert detail.capabilities == {"function_calling": True}

    conn.close()


def test_get_model_detail_not_found(test_db) -> None:  # type: ignore[no-untyped-def]
    """Test getting model detail for non-existent version."""
    conn = initialize_database(test_db)

    detail = get_model_detail(conn, "nonexistent")

    assert detail is None

    conn.close()


def test_model_tree_serialization() -> None:
    """Test ModelTreeResponse serialization."""
    response = ModelTreeResponse(
        providers=[
            ProviderNode(
                id="openai",
                name="OpenAI",
                is_enabled=True,
                model_count=10,
                last_sync_at="2024-04-09T10:00:00",
                sync_status="fresh",
            )
        ]
    )

    data = response.model_dump()
    assert data["providers"][0]["id"] == "openai"


def test_model_detail_serialization() -> None:
    """Test ModelDetailResponse serialization."""
    response = ModelDetailResponse(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        family_id="gpt-4",
        provider_id="openai",
        version_string="2024-04-09",
        release_date="2024-04-09",
        is_latest=True,
        context_window=128000,
        supports_vision=True,
        supports_tools=True,
        capabilities={"function_calling": True},
    )

    data = response.model_dump()
    assert data["id"] == "gpt-4-turbo-2024-04-09"
    assert data["capabilities"] == {"function_calling": True}
