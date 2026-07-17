from __future__ import annotations

from app.databases.base import DatabaseProvider, ModelEntry
from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import TraceLevel


class DatabaseRegistry:
    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._providers: dict[str, DatabaseProvider] = {}
        self._trace.emit(
            component="DatabaseRegistry",
            level=TraceLevel.INFO,
            message="DatabaseRegistry initialized",
        )

    def register(self, name: str, provider: DatabaseProvider) -> None:
        self._providers[name] = provider

    def list_databases(self) -> list[str]:
        return list(self._providers.keys())

    def get_database(self, name: str) -> DatabaseProvider:
        return self._providers[name]

    def find_model(self, model_id: str) -> tuple[str, ModelEntry] | None:
        for db_name, provider in self._providers.items():
            for model in provider.list_models():
                if f"{model.org}/{model.family}" == model_id:
                    return db_name, model
        return None
