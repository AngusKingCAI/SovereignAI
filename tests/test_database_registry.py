from __future__ import annotations

from databases.base import DatabaseProvider, DatabaseStatus
from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ModelEntry


class MockDatabaseProvider(DatabaseProvider):
    def __init__(self, name: str) -> None:
        self.name = name

    def list_models(self) -> list[ModelEntry]:
        return []

    def download_model(self, _model_id: str) -> None:
        pass

    def update_model(self, _model_id: str) -> None:
        pass

    def uninstall_model(self, _model_id: str) -> None:
        pass

    def health_check(self) -> DatabaseStatus:
        return DatabaseStatus(installed=True, version="1.0", size_bytes=1000)


def test_register_and_retrieve() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    provider = MockDatabaseProvider("test_db")
    registry.register("test_db", provider)
    assert registry.get_database("test_db") is provider


def test_list_databases() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    registry.register("db1", MockDatabaseProvider("db1"))
    registry.register("db2", MockDatabaseProvider("db2"))
    assert set(registry.list_databases()) == {"db1", "db2"}


def test_find_model() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)

    class TestProvider(DatabaseProvider):
        name = "test_db"

        def list_models(self) -> list[ModelEntry]:
            return [
                ModelEntry(
                    org="org1",
                    family="model1",
                    version="1.0",
                    quant="q4_K_M",
                    file_size_bytes=1000,
                    vram_required_mb=1000,
                    num_layers=32,
                    category="llm",
                    source_db="test_db",
                )
            ]

        def download_model(self, _model_id: str) -> None:
            pass

        def update_model(self, _model_id: str) -> None:
            pass

        def uninstall_model(self, _model_id: str) -> None:
            pass

        def health_check(self) -> DatabaseStatus:
            return DatabaseStatus(installed=True, version="1.0", size_bytes=1000)

    registry.register("test_db", TestProvider())
    result = registry.find_model("org1/model1")
    assert result is not None
    assert result[0] == "test_db"
    assert result[1].family == "model1"


def test_find_model_not_found() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    registry.register("db1", MockDatabaseProvider("db1"))
    assert registry.find_model("nonexistent/model") is None
