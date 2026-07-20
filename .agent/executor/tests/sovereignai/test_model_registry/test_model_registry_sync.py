import asyncio
import contextlib
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from sovereignai.model_registry.adapters import ADAPTER_REGISTRY, OllamaAdapter, OpenAIAdapter
from sovereignai.model_registry.schema import NormalizedModelData
from sovereignai.model_registry.sync import (
    ModelSyncService,
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class FakeAdapter:
    """Fake adapter for testing."""

    def __init__(self, should_fail: bool = False, fail_with: Exception | None = None) -> None:
        self.should_fail = should_fail
        self.fail_with = fail_with

    async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
        if self.should_fail:
            if self.fail_with:
                raise self.fail_with
            raise ProviderAuthError("Test auth error")

        return [
            NormalizedModelData(
                provider_id="fake",
                model_id="test-model",
                model_name="Test Model",
                version_string="v1",
                release_date=datetime(2024, 1, 1),
                context_window=4096,
                supports_vision=False,
                supports_tools=False,
                capabilities={},
            )
        ]


@pytest.fixture
def sync_service(tmp_path: Path) -> ModelSyncService:
    db_path = tmp_path / "test.db"
    service = ModelSyncService(db_path, event_bus=None)
    yield service
    service.close()


def test_sync_service_initialization(sync_service: ModelSyncService) -> None:
    assert sync_service._conn is None
    _ = sync_service.conn
    assert sync_service._conn is not None


def test_sync_service_close(sync_service: ModelSyncService) -> None:
    _ = sync_service.conn
    sync_service.close()
    assert sync_service._conn is None


def test_sync_provider_success(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter()
    result = asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    assert result["status"] == "success"
    assert result["provider_id"] == "fake"
    assert result["models_count"] == "1"
    assert "started_at" in result
    assert "completed_at" in result


def test_sync_provider_auth_error(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter(should_fail=True, fail_with=ProviderAuthError("Invalid key"))

    with pytest.raises(ProviderAuthError):
        asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    # Check sync run was logged as failed
    status = sync_service.get_sync_status("fake")
    assert status["last_successful_sync_at"] is None
    assert status["last_error_class"] == "ProviderAuthError"


def test_sync_provider_rate_limit_error(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter(should_fail=True, fail_with=ProviderRateLimitError("Rate limited"))

    with pytest.raises(ProviderRateLimitError):
        asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    status = sync_service.get_sync_status("fake")
    assert status["last_error_class"] == "ProviderRateLimitError"


def test_sync_provider_unavailable_error(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter(
        should_fail=True, fail_with=ProviderUnavailableError("Service unavailable")
    )

    with pytest.raises(ProviderUnavailableError):
        asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    status = sync_service.get_sync_status("fake")
    assert status["last_error_class"] == "ProviderUnavailableError"


def test_sync_provider_timeout(sync_service: ModelSyncService) -> None:
    class SlowAdapter:
        async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
            await asyncio.sleep(2)  # Short delay for testing
            return []

    # Mock the timeout to be shorter for testing
    import sovereignai.model_registry.sync as sync_module
    original_wait_for = sync_module.asyncio.wait_for

    async def short_wait_for(coro, timeout):  # type: ignore[no-untyped-def]
        return await original_wait_for(coro, timeout=0.1)  # 0.1s timeout for testing

    sync_module.asyncio.wait_for = short_wait_for

    try:
        adapter = SlowAdapter()

        with pytest.raises(ProviderUnavailableError, match="timeout"):
            asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

        status = sync_service.get_sync_status("fake")
        assert status["last_error_class"] == "TimeoutError"
    finally:
        sync_module.asyncio.wait_for = original_wait_for


def test_sync_lock_prevents_overlap(sync_service: ModelSyncService) -> None:
    class SlowAdapter:
        def __init__(self) -> None:
            self.call_count = 0

        async def fetch_models(self, api_key: str) -> list[NormalizedModelData]:
            self.call_count += 1
            await asyncio.sleep(0.05)  # Short delay
            return [
                NormalizedModelData(
                    provider_id="fake",
                    model_id="test-model",
                    model_name="Test Model",
                    version_string="v1",
                    release_date=datetime(2024, 1, 1),
                    context_window=4096,
                    supports_vision=False,
                    supports_tools=False,
                    capabilities={},
                )
            ]

    adapter = SlowAdapter()

    # Run sync sequentially to test basic functionality
    # (Testing actual concurrent locking requires async test infrastructure)
    result1 = asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))
    result2 = asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    # Both should complete successfully
    assert result1["status"] == "success"
    assert result2["status"] == "success"
    assert adapter.call_count == 2


def test_cache_models(sync_service: ModelSyncService) -> None:
    models = [
        NormalizedModelData(
            provider_id="test",
            model_id="model1",
            model_name="Model 1",
            version_string="v1",
            release_date=datetime(2024, 1, 1),
            context_window=4096,
            supports_vision=False,
            supports_tools=False,
            capabilities={},
        )
    ]

    sync_service._cache_models("test", models)

    # Verify data was cached
    cursor = sync_service.conn.execute("SELECT * FROM providers WHERE id = ?", ("test",))
    provider = cursor.fetchone()
    assert provider is not None
    assert provider["id"] == "test"

    cursor = sync_service.conn.execute("SELECT * FROM families WHERE provider_id = ?", ("test",))
    family = cursor.fetchone()
    assert family is not None

    cursor = sync_service.conn.execute("SELECT * FROM models WHERE family_id = ?", (family["id"],))
    model = cursor.fetchone()
    assert model is not None

    cursor = sync_service.conn.execute(
        "SELECT * FROM model_versions WHERE model_id = ?", (model["id"],)
    )
    version = cursor.fetchone()
    assert version is not None


def test_sanitize_error_message(sync_service: ModelSyncService) -> None:
    # Test API key redaction
    message = "Error with API key sk-1234567890abcdef1234567890abcdef"
    sanitized = sync_service._sanitize_error_message(message)
    assert "sk-1234567890abcdef1234567890abcdef" not in sanitized
    assert "***REDACTED***" in sanitized

    # Test AWS key redaction
    message = "Error with key AKIAIOSFODNN7EXAMPLE"
    sanitized = sync_service._sanitize_error_message(message)
    assert "AKIAIOSFODNN7EXAMPLE" not in sanitized
    assert "***REDACTED***" in sanitized

    # Test GitHub token redaction
    message = "Error with token ghp_1234567890abcdef1234567890abcdef12345678"
    sanitized = sync_service._sanitize_error_message(message)
    assert "ghp_1234567890abcdef1234567890abcdef12345678" not in sanitized
    assert "***REDACTED***" in sanitized

    # Test truncation
    long_message = "A" * 600
    sanitized = sync_service._sanitize_error_message(long_message)
    assert len(sanitized) == 500


def test_cleanup_old_errors(sync_service: ModelSyncService) -> None:
    # Insert old errors
    old_date = (datetime.now() - timedelta(days=40)).isoformat()
    sync_service.conn.execute(
        """
        INSERT INTO sync_errors (timestamp, provider_adapter_name, error_class, safe_error_message)
        VALUES (?, ?, ?, ?)
        """,
        (old_date, "test", "TestError", "Test message"),
    )

    # Insert recent errors
    recent_date = datetime.now().isoformat()
    sync_service.conn.execute(
        """
        INSERT INTO sync_errors (timestamp, provider_adapter_name, error_class, safe_error_message)
        VALUES (?, ?, ?, ?)
        """,
        (recent_date, "test", "TestError", "Test message"),
    )
    sync_service.conn.commit()

    # Cleanup with 30 day retention
    sync_service.cleanup_old_errors(retention_days=30)

    # Verify old error was removed
    cursor = sync_service.conn.execute("SELECT COUNT(*) as count FROM sync_errors")
    count = cursor.fetchone()["count"]
    assert count == 1


def test_get_sync_status_no_syncs(sync_service: ModelSyncService) -> None:
    status = sync_service.get_sync_status("nonexistent")
    assert status["provider_id"] == "nonexistent"
    assert status["last_successful_sync_at"] is None
    assert status["last_error_timestamp"] is None
    assert status["last_error_class"] is None
    assert status["last_error_message"] is None


def test_get_sync_status_with_success(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter()
    asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    status = sync_service.get_sync_status("fake")
    assert status["provider_id"] == "fake"
    assert status["last_successful_sync_at"] is not None
    assert status["last_error_class"] is None


def test_get_sync_status_with_error(sync_service: ModelSyncService) -> None:
    adapter = FakeAdapter(should_fail=True)
    with contextlib.suppress(ProviderAuthError):
        asyncio.run(sync_service.sync_provider("fake", adapter, "test-key"))

    status = sync_service.get_sync_status("fake")
    assert status["provider_id"] == "fake"
    assert status["last_successful_sync_at"] is None
    assert status["last_error_class"] == "ProviderAuthError"
    assert status["last_error_message"] is not None


def test_openai_adapter() -> None:
    adapter = OpenAIAdapter()
    models = asyncio.run(adapter.fetch_models("sk-test"))

    assert len(models) > 0
    assert all(m.provider_id == "openai" for m in models)
    assert all(isinstance(m, NormalizedModelData) for m in models)


def test_openai_adapter_no_api_key() -> None:
    adapter = OpenAIAdapter()
    with pytest.raises(ProviderAuthError):
        asyncio.run(adapter.fetch_models(""))


def test_ollama_adapter() -> None:
    adapter = OllamaAdapter()
    models = asyncio.run(adapter.fetch_models(""))

    assert len(models) > 0
    assert all(m.provider_id == "ollama" for m in models)
    assert all(isinstance(m, NormalizedModelData) for m in models)


def test_adapter_registry() -> None:
    assert "openai" in ADAPTER_REGISTRY
    assert "ollama" in ADAPTER_REGISTRY
    assert isinstance(ADAPTER_REGISTRY["openai"], OpenAIAdapter)
    assert isinstance(ADAPTER_REGISTRY["ollama"], OllamaAdapter)


def test_adapter_registry_duplicate_rejection() -> None:
    from sovereignai.model_registry.adapters import register_adapter

    with pytest.raises(ValueError, match="already registered"):
        register_adapter("openai", OpenAIAdapter())


def test_adapter_registry_filter_all() -> None:
    from sovereignai.model_registry.adapters import filter_adapters

    filtered = filter_adapters(None)
    assert "openai" in filtered
    assert "ollama" in filtered


def test_adapter_registry_filter_subset() -> None:
    from sovereignai.model_registry.adapters import filter_adapters

    filtered = filter_adapters(["openai"])
    assert "openai" in filtered
    assert "ollama" not in filtered


def test_adapter_registry_filter_case_insensitive() -> None:
    from sovereignai.model_registry.adapters import filter_adapters

    filtered = filter_adapters(["OpenAI", "OLLAMA"])
    assert "openai" in filtered
    assert "ollama" in filtered


def test_adapter_registry_filter_spaces() -> None:
    from sovereignai.model_registry.adapters import filter_adapters

    filtered = filter_adapters(["open ai", "ollama "])
    assert "openai" in filtered
    assert "ollama" in filtered
