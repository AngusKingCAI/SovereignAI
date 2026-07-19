import pytest
from pydantic import ValidationError
from sovereignai.options.schema import APIKey, BehaviorSettings, DisplaySettings


def test_api_key_creation() -> None:
    api_key = APIKey(provider="openai", key="sk-test-123")
    assert api_key.provider == "openai"
    assert api_key.key == "sk-test-123"


def test_api_key_default() -> None:
    api_key = APIKey(provider="openai")
    assert api_key.provider == "openai"
    assert api_key.key == ""


def test_display_settings_defaults() -> None:
    settings = DisplaySettings()
    assert settings.theme == "dark"
    assert settings.font_size == 14
    assert settings.panel_layout == "default"
    assert settings.language == "en"


def test_display_settings_custom() -> None:
    settings = DisplaySettings(theme="light", font_size=16, panel_layout="compact", language="fr")
    assert settings.theme == "light"
    assert settings.font_size == 16
    assert settings.panel_layout == "compact"
    assert settings.language == "fr"


def test_display_settings_font_size_validation() -> None:
    with pytest.raises(ValidationError):
        DisplaySettings(font_size=7)  # Below minimum

    with pytest.raises(ValidationError):
        DisplaySettings(font_size=33)  # Above maximum


def test_behavior_settings_defaults() -> None:
    settings = BehaviorSettings()
    assert settings.auto_save is True
    assert settings.confirm_destructive is True
    assert settings.default_department == "research"
    assert settings.max_iterations == 10
    assert settings.conversation_retention_days == 7
    assert settings.model_sync_interval_hours == 24
    assert settings.enabled_providers is None
    assert settings.sync_error_retention_days == 30


def test_behavior_settings_custom() -> None:
    settings = BehaviorSettings(
        auto_save=False,
        confirm_destructive=False,
        default_department="coding",
        max_iterations=20,
        conversation_retention_days=14,
        model_sync_interval_hours=12,
        enabled_providers=["openai", "ollama"],
        sync_error_retention_days=60
    )
    assert settings.auto_save is False
    assert settings.confirm_destructive is False
    assert settings.default_department == "coding"
    assert settings.max_iterations == 20
    assert settings.conversation_retention_days == 14
    assert settings.model_sync_interval_hours == 12
    assert settings.enabled_providers == ["openai", "ollama"]
    assert settings.sync_error_retention_days == 60


def test_behavior_settings_max_iterations_validation() -> None:
    with pytest.raises(ValidationError):
        BehaviorSettings(max_iterations=0)  # Below minimum

    with pytest.raises(ValidationError):
        BehaviorSettings(max_iterations=101)  # Above maximum


def test_behavior_settings_retention_days_validation() -> None:
    with pytest.raises(ValidationError):
        BehaviorSettings(conversation_retention_days=0)  # Below minimum

    with pytest.raises(ValidationError):
        BehaviorSettings(conversation_retention_days=366)  # Above maximum


def test_behavior_settings_sync_interval_validation() -> None:
    with pytest.raises(ValidationError):
        BehaviorSettings(model_sync_interval_hours=0)  # Below minimum

    with pytest.raises(ValidationError):
        BehaviorSettings(model_sync_interval_hours=169)  # Above maximum


def test_behavior_settings_enabled_providers_empty() -> None:
    settings = BehaviorSettings(enabled_providers=[])
    assert settings.enabled_providers is None  # Empty list converted to None


def test_behavior_settings_enabled_providers_none() -> None:
    settings = BehaviorSettings(enabled_providers=None)
    assert settings.enabled_providers is None


def test_behavior_settings_sync_error_retention_validation() -> None:
    with pytest.raises(ValidationError):
        BehaviorSettings(sync_error_retention_days=0)  # Below minimum

    with pytest.raises(ValidationError):
        BehaviorSettings(sync_error_retention_days=366)  # Above maximum


def test_api_key_serialization() -> None:
    api_key = APIKey(provider="openai", key="sk-test-123")
    data = api_key.model_dump()
    assert data["provider"] == "openai"
    assert data["key"] == "sk-test-123"


def test_display_settings_serialization() -> None:
    settings = DisplaySettings(theme="light", font_size=16)
    data = settings.model_dump()
    assert data["theme"] == "light"
    assert data["font_size"] == 16


def test_behavior_settings_serialization() -> None:
    settings = BehaviorSettings(max_iterations=20, enabled_providers=["openai"])
    data = settings.model_dump()
    assert data["max_iterations"] == 20
    assert data["enabled_providers"] == ["openai"]


def test_display_settings_from_dict() -> None:
    data = {"theme": "light", "font_size": 16, "panel_layout": "compact", "language": "fr"}
    settings = DisplaySettings.model_validate(data)
    assert settings.theme == "light"
    assert settings.font_size == 16


def test_behavior_settings_from_dict() -> None:
    data = {
        "auto_save": False,
        "max_iterations": 20,
        "enabled_providers": ["openai", "ollama"]
    }
    settings = BehaviorSettings.model_validate(data)
    assert settings.auto_save is False
    assert settings.max_iterations == 20
    assert settings.enabled_providers == ["openai", "ollama"]
