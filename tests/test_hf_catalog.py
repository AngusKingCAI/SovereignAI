"""Tests for hf_catalog module."""
from unittest.mock import MagicMock, patch

import pytest

from sovereignai.shared.hf_catalog import fetch_gguf_models, get_model_files
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def mock_trace():
    """Create a mock trace emitter."""
    trace = MagicMock(spec=TraceEmitter)
    return trace


def test_fetch_gguf_models_success(mock_trace):
    """Test fetching GGUF models successfully."""
    mock_response_data = [
        {
            "id": "meta-llama/Llama-2-7b-chat-GGUF",
            "downloads": 5000000,
            "likes": 10000,
            "tags": ["gguf", "llama"],
            "lastModified": "2024-01-01T00:00:00.000Z",
            "pipeline_tag": "text-generation",
        },
        {
            "id": "mistralai/Mistral-7B-Instruct-v0.2-GGUF",
            "downloads": 3000000,
            "likes": 5000,
            "tags": ["gguf", "mistral"],
            "lastModified": "2024-01-02T00:00:00.000Z",
            "pipeline_tag": "text-generation",
        },
    ]

    with patch('urllib.request.urlopen'):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"models": []}'  # Will be replaced
        mock_response.__enter__ = lambda self: self
        mock_response.__exit__ = lambda self, *_args: None

        # Patch json.loads to return our test data
        with patch('json.loads', return_value=mock_response_data):
            result = fetch_gguf_models(mock_trace, search="", limit=50)

    assert len(result) == 2
    assert result[0]["id"] == "meta-llama/Llama-2-7b-chat-GGUF"
    assert result[0]["publisher"] == "meta-llama"
    assert result[0]["name"] == "Llama-2-7b-chat-GGUF"
    assert result[0]["downloads"] == 5000000
    assert result[1]["id"] == "mistralai/Mistral-7B-Instruct-v0.2-GGUF"
    assert result[1]["publisher"] == "mistralai"


def test_fetch_gguf_models_with_search(mock_trace):
    """Test fetching GGUF models with search parameter."""
    mock_response_data = [
        {
            "id": "meta-llama/Llama-2-7b-chat-GGUF",
            "downloads": 5000000,
            "likes": 10000,
            "tags": ["gguf", "llama"],
            "lastModified": "2024-01-01T00:00:00.000Z",
            "pipeline_tag": "text-generation",
        },
    ]

    with patch('urllib.request.urlopen'), patch('json.loads', return_value=mock_response_data):
        result = fetch_gguf_models(mock_trace, search="llama", limit=10)

    assert len(result) == 1
    assert result[0]["id"] == "meta-llama/Llama-2-7b-chat-GGUF"


def test_fetch_gguf_models_error(mock_trace):
    """Test fetching GGUF models with network error."""
    with patch('urllib.request.urlopen', side_effect=Exception("Network error")):
        result = fetch_gguf_models(mock_trace)

    assert result == []
    mock_trace.emit.assert_called()


def test_get_model_files_success(mock_trace):
    """Test getting model files successfully."""
    mock_response_data = {
        "siblings": [
            {"rfilename": "model-Q4_K_M.gguf"},
            {"rfilename": "model-Q5_K_M.gguf"},
            {"rfilename": "README.md"},
        ]
    }

    with patch('urllib.request.urlopen'), patch('json.loads', return_value=mock_response_data):
        result = get_model_files(mock_trace, "meta-llama/Llama-2-7b-chat-GGUF")

    assert len(result) == 2
    assert result[0]["filename"] == "model-Q4_K_M.gguf"
    assert result[0]["quantization"] == "Q4_K_M"
    assert result[1]["filename"] == "model-Q5_K_M.gguf"
    assert result[1]["quantization"] == "Q5_K_M"


def test_get_model_files_error(mock_trace):
    """Test getting model files with network error."""
    with patch('urllib.request.urlopen', side_effect=Exception("Network error")):
        result = get_model_files(mock_trace, "meta-llama/Llama-2-7b-chat-GGUF")

    assert result == []
    mock_trace.emit.assert_called()


def test_get_model_files_no_gguf(mock_trace):
    """Test getting model files when no GGUF files exist."""
    mock_response_data = {
        "siblings": [
            {"rfilename": "README.md"},
            {"rfilename": "config.json"},
        ]
    }

    with patch('urllib.request.urlopen'), patch('json.loads', return_value=mock_response_data):
        result = get_model_files(mock_trace, "meta-llama/Llama-2-7b-chat-GGUF")

    assert result == []
