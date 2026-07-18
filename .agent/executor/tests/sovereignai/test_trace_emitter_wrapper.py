"""Tests for TraceEmitterWrapper (Plan 23 S9)."""

from unittest.mock import MagicMock

import pytest
from sovereignai.observability.trace_emitter import TraceEmitterWrapper
from sovereignai.shared.types import TraceLevel


@pytest.fixture
def mock_event_bus():
    bus = MagicMock()
    bus.is_started = False
    return bus


@pytest.fixture
def mock_trace_emitter():
    emitter = MagicMock()
    return emitter


@pytest.fixture
def wrapper(mock_event_bus, mock_trace_emitter):
    return TraceEmitterWrapper(event_bus=mock_event_bus, inner=mock_trace_emitter)


def test_prefix_added(wrapper, mock_event_bus, mock_trace_emitter):
    """Test that 'trace.' prefix is added if not present."""
    wrapper.emit_event("test_event", {"key": "value"}, TraceLevel.INFO)

    # When not started, should route to inner emitter
    mock_trace_emitter.emit.assert_called_once()
    call_args = mock_trace_emitter.emit.call_args
    assert "trace.test_event" in call_args[1]["message"]


def test_no_double_prefix(wrapper, mock_event_bus, mock_trace_emitter):
    """Test that 'trace.' is not added if already present (case-insensitive)."""
    wrapper.emit_event("TRACE.test_event", {"key": "value"}, TraceLevel.INFO)

    mock_trace_emitter.emit.assert_called_once()
    call_args = mock_trace_emitter.emit.call_args
    assert "TRACE.test_event" in call_args[1]["message"]


def test_fallback_when_not_started(wrapper, mock_event_bus, mock_trace_emitter):
    """Test fallback to inner emitter when EventBus not started."""
    mock_event_bus.is_started = False
    wrapper.emit_event("test_event", {"key": "value"}, TraceLevel.INFO)

    mock_trace_emitter.emit.assert_called_once()
    mock_event_bus.publish.assert_not_called()


def test_wrapper_construction():
    """Test that wrapper can be constructed with required dependencies."""
    bus = MagicMock()
    bus.is_started = False
    emitter = MagicMock()
    wrapper = TraceEmitterWrapper(event_bus=bus, inner=emitter)
    assert wrapper is not None


def test_emit_with_different_levels(wrapper, mock_event_bus, mock_trace_emitter):
    """Test that different trace levels are handled."""
    mock_event_bus.is_started = False
    wrapper.emit_event("test", {}, TraceLevel.DEBUG)
    wrapper.emit_event("test", {}, TraceLevel.ERROR)
    wrapper.emit_event("test", {}, TraceLevel.WARN)

    assert mock_trace_emitter.emit.call_count == 3
