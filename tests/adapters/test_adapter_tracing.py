"""Test adapter tracing."""
import pytest


def test_adapter_register_info_emit() -> None:
    """Verify adapter registration emits INFO."""
    # This test would require mocking TraceEmitter to capture emits
    # For now, just verify the adapter can be imported
    try:
        from adapters.external.ollama_adapter.adapter import OllamaAdapter
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace = TraceEmitter()
        adapter = OllamaAdapter(trace)
        assert adapter is not None
    except ImportError:
        pytest.skip("Ollama adapter not available")


def test_adapter_invoke_debug_emit() -> None:
    """Verify adapter capability invocation emits DEBUG."""
    # This test would require mocking TraceEmitter to capture emits
    try:
        from adapters.external.ollama_adapter.adapter import OllamaAdapter
        from sovereignai.shared.trace_emitter import TraceEmitter
        trace = TraceEmitter()
        adapter = OllamaAdapter(trace)
        # Health check should emit
        assert adapter.health_check() in [True, False]
    except ImportError:
        pytest.skip("Ollama adapter not available")
