from datetime import datetime

from sovereignai.model_registry.schema import (
    Model,
    ModelFamily,
    ModelVersion,
    NormalizedModelData,
    Provider,
)


def test_provider_creation() -> None:
    provider = Provider(
        id="openai",
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        auth_type="bearer_token"
    )
    assert provider.id == "openai"
    assert provider.name == "OpenAI"
    assert provider.api_base_url == "https://api.openai.com/v1"
    assert provider.auth_type == "bearer_token"
    assert provider.is_enabled is True


def test_provider_defaults() -> None:
    provider = Provider(
        id="openai",
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        auth_type="bearer_token"
    )
    assert provider.is_enabled is True


def test_provider_disabled() -> None:
    provider = Provider(
        id="openai",
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        auth_type="bearer_token",
        is_enabled=False
    )
    assert provider.is_enabled is False


def test_model_family_creation() -> None:
    family = ModelFamily(
        id="gpt-4",
        provider_id="openai",
        name="GPT-4",
        description="GPT-4 family of models"
    )
    assert family.id == "gpt-4"
    assert family.provider_id == "openai"
    assert family.name == "GPT-4"
    assert family.description == "GPT-4 family of models"


def test_model_family_defaults() -> None:
    family = ModelFamily(
        id="gpt-4",
        provider_id="openai",
        name="GPT-4"
    )
    assert family.description == ""


def test_model_creation() -> None:
    model = Model(
        id="gpt-4-turbo",
        family_id="gpt-4",
        name="GPT-4 Turbo"
    )
    assert model.id == "gpt-4-turbo"
    assert model.family_id == "gpt-4"
    assert model.name == "GPT-4 Turbo"


def test_model_version_creation() -> None:
    version = ModelVersion(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        version_string="2024-04-09",
        release_date=datetime(2024, 4, 9),
        is_latest=True,
        context_window=128000,
        supports_vision=True,
        supports_tools=True,
        capabilities={"function_calling": True, "json_mode": True}
    )
    assert version.id == "gpt-4-turbo-2024-04-09"
    assert version.model_id == "gpt-4-turbo"
    assert version.version_string == "2024-04-09"
    assert version.release_date == datetime(2024, 4, 9)
    assert version.is_latest is True
    assert version.context_window == 128000
    assert version.supports_vision is True
    assert version.supports_tools is True
    assert version.capabilities == {"function_calling": True, "json_mode": True}


def test_model_version_defaults() -> None:
    version = ModelVersion(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        version_string="2024-04-09"
    )
    assert version.release_date is None
    assert version.is_latest is False
    assert version.context_window is None
    assert version.supports_vision is False
    assert version.supports_tools is False
    assert version.capabilities == {}


def test_normalized_model_data_creation() -> None:
    data = NormalizedModelData(
        provider_id="openai",
        model_id="gpt-4-turbo",
        model_name="GPT-4 Turbo",
        version_string="2024-04-09",
        release_date=datetime(2024, 4, 9),
        context_window=128000,
        supports_vision=True,
        supports_tools=True,
        capabilities={"function_calling": True}
    )
    assert data.provider_id == "openai"
    assert data.model_id == "gpt-4-turbo"
    assert data.model_name == "GPT-4 Turbo"
    assert data.version_string == "2024-04-09"
    assert data.release_date == datetime(2024, 4, 9)
    assert data.context_window == 128000
    assert data.supports_vision is True
    assert data.supports_tools is True
    assert data.capabilities == {"function_calling": True}


def test_normalized_model_data_defaults() -> None:
    data = NormalizedModelData(
        provider_id="openai",
        model_id="gpt-4-turbo",
        model_name="GPT-4 Turbo",
        version_string="2024-04-09"
    )
    assert data.release_date is None
    assert data.context_window is None
    assert data.supports_vision is False
    assert data.supports_tools is False
    assert data.capabilities == {}


def test_provider_serialization() -> None:
    provider = Provider(
        id="openai",
        name="OpenAI",
        api_base_url="https://api.openai.com/v1",
        auth_type="bearer_token"
    )
    data = provider.model_dump()
    assert data["id"] == "openai"
    assert data["name"] == "OpenAI"
    assert data["api_base_url"] == "https://api.openai.com/v1"
    assert data["auth_type"] == "bearer_token"


def test_model_version_serialization() -> None:
    version = ModelVersion(
        id="gpt-4-turbo-2024-04-09",
        model_id="gpt-4-turbo",
        version_string="2024-04-09",
        context_window=128000
    )
    data = version.model_dump()
    assert data["id"] == "gpt-4-turbo-2024-04-09"
    assert data["context_window"] == 128000


def test_normalized_model_data_serialization() -> None:
    data = NormalizedModelData(
        provider_id="openai",
        model_id="gpt-4-turbo",
        model_name="GPT-4 Turbo",
        version_string="2024-04-09"
    )
    serialized = data.model_dump()
    assert serialized["provider_id"] == "openai"
    assert serialized["model_id"] == "gpt-4-turbo"


def test_provider_from_dict() -> None:
    data = {
        "id": "openai",
        "name": "OpenAI",
        "api_base_url": "https://api.openai.com/v1",
        "auth_type": "bearer_token",
        "is_enabled": False
    }
    provider = Provider.model_validate(data)
    assert provider.id == "openai"
    assert provider.is_enabled is False


def test_model_version_from_dict() -> None:
    data = {
        "id": "gpt-4-turbo-2024-04-09",
        "model_id": "gpt-4-turbo",
        "version_string": "2024-04-09",
        "context_window": 128000,
        "supports_vision": True
    }
    version = ModelVersion.model_validate(data)
    assert version.context_window == 128000
    assert version.supports_vision is True


def test_normalized_model_data_from_dict() -> None:
    data = {
        "provider_id": "openai",
        "model_id": "gpt-4-turbo",
        "model_name": "GPT-4 Turbo",
        "version_string": "2024-04-09",
        "supports_tools": True
    }
    normalized = NormalizedModelData.model_validate(data)
    assert normalized.provider_id == "openai"
    assert normalized.supports_tools is True
