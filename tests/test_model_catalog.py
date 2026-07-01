from __future__ import annotations

from unittest.mock import Mock

from databases.base import DatabaseProvider, ModelEntry
from sovereignai.shared.database_registry import DatabaseRegistry
from sovereignai.shared.model_catalog import ModelCatalog
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import ModelFilter


def test_list_models_no_filters() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="mistral",
            family="mistral-7b",
            version="v0.1",
            quant="q4",
            file_size_bytes=4_200_000_000,
            vram_required_mb=4200,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(ModelFilter())
    assert len(result) == 2


def test_list_models_search_filter() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="mistral",
            family="mistral-7b",
            version="v0.1",
            quant="q4",
            file_size_bytes=4_200_000_000,
            vram_required_mb=4200,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(ModelFilter(search="llama"))
    assert len(result) == 1
    assert result[0].family == "llama-3-8b"


def test_list_models_category_filter() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="stability",
            family="sdxl",
            version="1.0",
            quant="fp16",
            file_size_bytes=6_900_000_000,
            vram_required_mb=6900,
            num_layers=32,
            category="image",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(ModelFilter(category="llm"))
    assert len(result) == 1
    assert result[0].category == "llm"


def test_list_models_vram_filter() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="meta",
            family="llama-3-70b",
            version="instruct",
            quant="q4",
            file_size_bytes=40_000_000_000,
            vram_required_mb=40000,
            num_layers=80,
            category="llm",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(ModelFilter(vram_fit_max_mb=8000))
    assert len(result) == 1
    assert result[0].family == "llama-3-8b"


def test_list_models_quant_filter() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q2",
            file_size_bytes=2_400_000_000,
            vram_required_mb=2400,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="fp16",
            file_size_bytes=16_000_000_000,
            vram_required_mb=16000,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(ModelFilter(quant_level_min="q4"))
    assert len(result) == 2
    assert all(m.quant in ("q4", "fp16") for m in result)


def test_list_models_combined_filters() -> None:
    trace = TraceEmitter()
    registry = DatabaseRegistry(trace)
    catalog = ModelCatalog(registry, trace)

    mock_provider = Mock(spec=DatabaseProvider)
    mock_provider.list_models.return_value = [
        ModelEntry(
            org="meta",
            family="llama-3-8b",
            version="instruct",
            quant="q4",
            file_size_bytes=4_800_000_000,
            vram_required_mb=4800,
            num_layers=32,
            category="llm",
            source_db="huggingface",
        ),
        ModelEntry(
            org="meta",
            family="llama-3-70b",
            version="instruct",
            quant="q4",
            file_size_bytes=40_000_000_000,
            vram_required_mb=40000,
            num_layers=80,
            category="llm",
            source_db="huggingface",
        ),
    ]
    registry.register("hf", mock_provider)

    result = catalog.list_models(
        ModelFilter(search="llama", vram_fit_max_mb=8000, quant_level_min="q4")
    )
    assert len(result) == 1
    assert result[0].family == "llama-3-8b"
