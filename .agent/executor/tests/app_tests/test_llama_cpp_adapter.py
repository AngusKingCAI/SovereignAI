from __future__ import annotations

import os
import time
from unittest.mock import MagicMock, patch

import pytest
from sovereignai.shared.types import AdapterHealth

from app.adapters.external.llama_cpp_adapter.adapter import GenerationTimeoutError, LlamaCppAdapter
from app.databases.base import ModelNotFoundError


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
    if not os.environ.get('SOVEREIGNAI_FULL_STACK_TESTS'):
        pytest.skip("Set SOVEREIGNAI_FULL_STACK_TESTS=1 to run full stack integration tests")
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


def test_generate_timeout(adapter, mock_database_registry, mock_model_path_resolver, mock_trace):
    import sys
    mock_llama_cpp = MagicMock()
    mock_llm = MagicMock()
    mock_llm.create_completion = MagicMock()
    def slow_completion(*args, **kwargs):
        time.sleep(5)
        return {"choices": [{"text": "Generated text"}]}
    mock_llm.create_completion.side_effect = slow_completion
    mock_llama_cpp.Llama = MagicMock(return_value=mock_llm)
    sys.modules["llama_cpp"] = mock_llama_cpp

    with patch.object(adapter, 'load_model'):
        adapter._llm = mock_llm
        try:
            with pytest.raises(GenerationTimeoutError, match='exceeded timeout'):
                adapter.generate("test/model", "test prompt", 100, 0.7, timeout_seconds=0.1)
        finally:
            if "llama_cpp" in sys.modules:
                del sys.modules["llama_cpp"]


def test_generate_no_timeout(adapter, mock_database_registry, mock_model_path_resolver, mock_trace):
    import sys
    mock_llama_cpp = MagicMock()
    mock_llm = MagicMock()
    mock_llm.create_completion = MagicMock(return_value={"choices": [{"text": "Generated text"}]})
    mock_llama_cpp.Llama = MagicMock(return_value=mock_llm)
    sys.modules["llama_cpp"] = mock_llama_cpp

    with patch.object(adapter, 'load_model'):
        adapter._llm = mock_llm
        try:
            result = adapter.generate("test/model", "test prompt", 100, 0.7, timeout_seconds=30.0)
            assert result == "Generated text"
        finally:
            if "llama_cpp" in sys.modules:
                del sys.modules["llama_cpp"]
