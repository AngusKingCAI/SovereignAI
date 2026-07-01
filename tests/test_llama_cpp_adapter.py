from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from adapters.external.llama_cpp_adapter.adapter import LlamaCppAdapter
from databases.base import ModelNotFoundError
from sovereignai.shared.types import AdapterHealth


@pytest.fixture
def mock_trace():
    trace = MagicMock()
    trace.emit = MagicMock()
    return trace


@pytest.fixture
def mock_hardware_probe():
    probe = MagicMock()
    probe.sample = MagicMock()
    return probe


@pytest.fixture
def mock_database_registry():
    registry = MagicMock()
    registry.find_model = MagicMock()
    return registry


@pytest.fixture
def mock_model_path_resolver():
    resolver = MagicMock()
    return resolver


@pytest.fixture
def adapter(mock_trace, mock_hardware_probe, mock_database_registry, mock_model_path_resolver):
    return LlamaCppAdapter(
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
        model_path_resolver=mock_model_path_resolver,
        database_registry=mock_database_registry,
        requested_n_gpu_layers=0,
    )


def test_model_not_found_error(adapter, mock_database_registry, mock_trace):
    mock_database_registry.find_model.return_value = None

    with pytest.raises(ModelNotFoundError):
        adapter.load_model("unknown/model")

    error_calls = [call for call in mock_trace.emit.call_args_list if "ERROR" in str(call)]
    assert any("Unknown model_id" in str(call) for call in error_calls)




def test_health_check_import_failure():
    mock_trace = MagicMock()
    mock_hardware_probe = MagicMock()
    mock_database_registry = MagicMock()
    mock_model_path_resolver = MagicMock()

    adapter = LlamaCppAdapter(
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
        model_path_resolver=mock_model_path_resolver,
        database_registry=mock_database_registry,
        requested_n_gpu_layers=0,
    )

    import sys
    sys.modules["llama_cpp"] = None
    try:
        health = adapter.health_check()
        assert health.healthy is False
        assert "llama-cpp-python not installed" in health.detail
    finally:
        if "llama_cpp" in sys.modules:
            del sys.modules["llama_cpp"]


def test_health_check_gpu_offload_failure():
    mock_trace = MagicMock()
    mock_hardware_probe = MagicMock()
    mock_database_registry = MagicMock()
    mock_model_path_resolver = MagicMock()

    adapter = LlamaCppAdapter(
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
        model_path_resolver=mock_model_path_resolver,
        database_registry=mock_database_registry,
        requested_n_gpu_layers=10,
    )

    mock_llama_cpp = MagicMock()
    mock_llama_cpp.llama_supports_gpu_offload.return_value = False

    import sys
    sys.modules["llama_cpp"] = mock_llama_cpp
    try:
        health = adapter.health_check()
        assert health.healthy is False
        assert "GPU offload not supported" in health.detail
    finally:
        if "llama_cpp" in sys.modules:
            del sys.modules["llama_cpp"]


def test_health_check_cpu_only_healthy():
    mock_trace = MagicMock()
    mock_hardware_probe = MagicMock()
    mock_database_registry = MagicMock()
    mock_model_path_resolver = MagicMock()

    adapter = LlamaCppAdapter(
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
        model_path_resolver=mock_model_path_resolver,
        database_registry=mock_database_registry,
        requested_n_gpu_layers=0,
    )

    mock_llama_cpp = MagicMock()

    import sys
    sys.modules["llama_cpp"] = mock_llama_cpp
    try:
        health = adapter.health_check()
        assert health.healthy is True
        assert health.detail == "OK"
    finally:
        if "llama_cpp" in sys.modules:
            del sys.modules["llama_cpp"]


def test_health_check_gpu_probe_absent_cpu_mode():
    mock_trace = MagicMock()
    mock_hardware_probe = MagicMock()
    mock_database_registry = MagicMock()
    mock_model_path_resolver = MagicMock()

    adapter = LlamaCppAdapter(
        trace=mock_trace,
        hardware_probe=mock_hardware_probe,
        model_path_resolver=mock_model_path_resolver,
        database_registry=mock_database_registry,
        requested_n_gpu_layers=10,
    )

    mock_llama_cpp = MagicMock()
    del mock_llama_cpp.llama_supports_gpu_offload

    import sys
    sys.modules["llama_cpp"] = mock_llama_cpp
    try:
        health = adapter.health_check()
        assert health.healthy is False
        assert "predates GPU offload probe" in health.detail
    finally:
        if "llama_cpp" in sys.modules:
            del sys.modules["llama_cpp"]


def test_adapter_health_dataclass():
    health = AdapterHealth(healthy=True, detail="OK")
    assert health.healthy is True
    assert health.detail == "OK"

    health2 = AdapterHealth(healthy=False, detail="Error")
    assert health2.healthy is False
    assert health2.detail == "Error"
