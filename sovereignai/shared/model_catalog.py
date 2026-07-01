from __future__ import annotations

from databases.base import ModelEntry
from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ModelFilter, TraceLevel

QUANT_PRIORITY = {
    "q2": 0,
    "q3": 1,
    "q4": 2,
    "q5": 3,
    "q6": 4,
    "q8": 5,
    "fp16": 6,
}


class ModelCatalog:
    def __init__(self, database_registry: DatabaseRegistry, trace: TraceEmitter) -> None:
        self._registry = database_registry
        self._trace = trace
        self._trace.emit(
            component="ModelCatalog",
            level=TraceLevel.INFO,
            message="ModelCatalog initialized",
        )

    def list_models(self, filters: ModelFilter) -> list[ModelEntry]:
        all_models: list[ModelEntry] = []
        for db_name in self._registry.list_databases():
            provider = self._registry.get_database(db_name)
            all_models.extend(provider.list_models())

        filtered: list[ModelEntry] = []
        for model in all_models:
            if filters.search is not None:
                search_lower = filters.search.lower()
                model_id = f"{model.org}/{model.family}".lower()
                if search_lower not in model_id:
                    continue

            if filters.category is not None:
                if model.category != filters.category:
                    continue

            if filters.vram_fit_max_mb is not None:
                if model.vram_required_mb > filters.vram_fit_max_mb:
                    continue

            if filters.quant_level_min is not None:
                min_priority = QUANT_PRIORITY.get(filters.quant_level_min, 999)
                model_priority = QUANT_PRIORITY.get(model.quant, 999)
                if model_priority < min_priority:
                    continue

            filtered.append(model)

        self._trace.emit(
            component="ModelCatalog",
            level=TraceLevel.DEBUG,
            message=f"Filtered {len(all_models)} models to {len(filtered)}",
        )
        return filtered
