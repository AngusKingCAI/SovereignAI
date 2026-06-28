"""Tests for OllamaAdapter."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from adapters.external.ollama_adapter.adapter import OllamaAdapter
from sovereignai.shared.trace_emitter import TraceEmitter


@pytest.fixture
def trace() -> TraceEmitter:
    """Create a trace emitter for testing."""
    return TraceEmitter()


@pytest.fixture
def adapter(trace: TraceEmitter) -> OllamaAdapter:
    """Create an Ollama adapter for testing."""
    return OllamaAdapter(trace=trace)


def test_health_check_success(trace: TraceEmitter) -> None:
    """Test health check when Ollama is running."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.return_value = []
        adapter = OllamaAdapter(trace=trace)
        assert adapter.health_check() is True


def test_health_check_failure(trace: TraceEmitter) -> None:
    """Test health check when Ollama is not running."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.side_effect = Exception("Ollama not running")
        adapter = OllamaAdapter(trace=trace)
        assert adapter.health_check() is False


def test_generate_success(trace: TraceEmitter) -> None:
    """Test successful text generation."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.return_value = []  # Health check passes
        adapter = OllamaAdapter(trace=trace)

    with patch("adapters.external.ollama_adapter.adapter.ollama.generate") as mock_generate:
        mock_generate.return_value = {"response": "Generated text"}
        result = adapter.generate("test prompt")
        assert result == "Generated text"


def test_generate_failure(trace: TraceEmitter) -> None:
    """Test text generation when Ollama is not healthy."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.side_effect = Exception("Ollama not running")
        adapter = OllamaAdapter(trace=trace)

    with pytest.raises(RuntimeError, match="not healthy"):
        adapter.generate("test prompt")


def test_generate_exception(trace: TraceEmitter) -> None:
    """Test text generation when Ollama raises an exception."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.return_value = []  # Health check passes
        adapter = OllamaAdapter(trace=trace)

    with patch("adapters.external.ollama_adapter.adapter.ollama.generate") as mock_generate:
        mock_generate.side_effect = Exception("Generation failed")

        with pytest.raises(RuntimeError, match="Generation failed"):
            adapter.generate("test prompt")


def test_chat_success(trace: TraceEmitter) -> None:
    """Test successful chat completion."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.return_value = []  # Health check passes
        adapter = OllamaAdapter(trace=trace)

    with patch("adapters.external.ollama_adapter.adapter.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"role": "assistant", "content": "Chat response"}}
        result = adapter.chat([{"role": "user", "content": "Hello"}])
        assert result["role"] == "assistant"
        assert result["content"] == "Chat response"


def test_chat_failure(trace: TraceEmitter) -> None:
    """Test chat completion when Ollama is not healthy."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.side_effect = Exception("Ollama not running")
        adapter = OllamaAdapter(trace=trace)

    with pytest.raises(RuntimeError, match="not healthy"):
        adapter.chat([{"role": "user", "content": "Hello"}])


def test_chat_exception(trace: TraceEmitter) -> None:
    """Test chat completion when Ollama raises an exception."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.return_value = []  # Health check passes
        adapter = OllamaAdapter(trace=trace)

    with patch("adapters.external.ollama_adapter.adapter.ollama.chat") as mock_chat:
        mock_chat.side_effect = Exception("Chat failed")

        with pytest.raises(RuntimeError, match="Chat failed"):
            adapter.chat([{"role": "user", "content": "Hello"}])


def test_degraded_registration_on_init(trace: TraceEmitter) -> None:
    """Test that adapter is registered as DEGRADED when health check fails."""
    with patch("adapters.external.ollama_adapter.adapter.ollama.list") as mock_list:
        mock_list.side_effect = Exception("Ollama not running")
        adapter = OllamaAdapter(trace=trace)

        assert adapter.health_check() is False

        # Check that a WARN trace was emitted
        events = trace.get_events()
        assert any("DEGRADED" in event.message for event in events)
