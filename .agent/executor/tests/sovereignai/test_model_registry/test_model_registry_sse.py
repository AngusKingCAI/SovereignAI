from datetime import datetime

from sovereignai.model_registry.events import SyncCompletedEvent


def test_sync_completed_event_success() -> None:
    event = SyncCompletedEvent(
        status="success",
        provider_id="openai",
        timestamp=datetime(2024, 4, 9, 10, 0, 0),
        models_count=10,
    )

    assert event.status == "success"
    assert event.provider_id == "openai"
    assert event.models_count == 10
    assert event.error_class is None


def test_sync_completed_event_failed() -> None:
    event = SyncCompletedEvent(
        status="failed",
        provider_id="openai",
        timestamp=datetime(2024, 4, 9, 10, 0, 0),
        error_class="ProviderAuthError",
    )

    assert event.status == "failed"
    assert event.provider_id == "openai"
    assert event.error_class == "ProviderAuthError"
    assert event.models_count is None


def test_sync_completed_event_serialization() -> None:
    event = SyncCompletedEvent(
        status="success",
        provider_id="openai",
        timestamp=datetime(2024, 4, 9, 10, 0, 0),
        models_count=10,
    )

    data = event.model_dump()
    assert data["status"] == "success"
    assert data["provider_id"] == "openai"
    assert data["models_count"] == 10


def test_sync_completed_event_from_dict() -> None:
    data = {
        "status": "success",
        "provider_id": "openai",
        "timestamp": "2024-04-09T10:00:00",
        "models_count": 10,
    }

    event = SyncCompletedEvent.model_validate(data)
    assert event.status == "success"
    assert event.provider_id == "openai"
    assert event.models_count == 10
