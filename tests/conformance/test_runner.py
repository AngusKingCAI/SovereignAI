"""Tests for conformance runner."""
from unittest.mock import MagicMock

from sovereignai.conformance.runner import ConformanceRunner
from sovereignai.shared.trace_emitter import TraceEmitter


def test_runner_init():
    """Test ConformanceRunner initialization."""
    trace = TraceEmitter()
    runner = ConformanceRunner(trace)
    assert runner is not None


def test_runner_check_first_party_no_tests():
    """Test checking conformance for first-party component with no tests."""
    trace = TraceEmitter()
    runner = ConformanceRunner(trace)
    result = runner.check(
        component_id="test_component",
        content_hash="abc123",
        capability_class="TestCapability",
        instance=MagicMock(),
        is_first_party=True,
    )
    assert result is False  # Should fail-closed for first-party with no tests


def test_runner_check_third_party_no_tests():
    """Test checking conformance for third-party component with no tests."""
    trace = TraceEmitter()
    runner = ConformanceRunner(trace)
    result = runner.check(
        component_id="test_component",
        content_hash="abc123",
        capability_class="TestCapability",
        instance=MagicMock(),
        is_first_party=False,
    )
    assert result is True  # Should fail-open for third-party with no tests


def test_runner_cache():
    """Test that conformance results are cached."""
    trace = TraceEmitter()
    runner = ConformanceRunner(trace)
    runner.check(
        component_id="test_component",
        content_hash="abc123",
        capability_class="TestCapability",
        instance=MagicMock(),
        is_first_party=False,
    )
    # Second call should use cache
    result = runner.check(
        component_id="test_component",
        content_hash="abc123",
        capability_class="TestCapability",
        instance=MagicMock(),
        is_first_party=False,
    )
    assert result is True
