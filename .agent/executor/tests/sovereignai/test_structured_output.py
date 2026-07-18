"""Tests for SingleCallStructuredOutput (Plan 23 S9)."""

import pytest
from unittest.mock import MagicMock

from sovereignai.agent.structured_output import (
    SingleCallStructuredOutput,
    StructuredOutputExhaustedError,
    ToolCall,
    FinalAnswer,
)


@pytest.fixture
def mock_emitter():
    emitter = MagicMock()
    return emitter


@pytest.fixture
def extractor(mock_emitter):
    return SingleCallStructuredOutput(emitter=mock_emitter)


def test_extract_final_answer(extractor):
    """Test extracting FinalAnswer from response."""
    response = "final answer: The result is 42"
    result = extractor.extract(response, schema_type="final_answer")

    assert isinstance(result, FinalAnswer)
    assert result.content == "The result is 42"


def test_extract_tool_call(extractor):
    """Test extracting ToolCall from response."""
    response = "Action: calculator\nArguments: {\"operation\": \"add\", \"a\": 1, \"b\": 2}"
    result = extractor.extract(response, schema_type="tool_call")

    assert isinstance(result, ToolCall)
    assert result.name == "calculator"
    assert "operation" in result.arguments


def test_validation_failure_retry(extractor):
    """Test that extraction retries on validation failure."""
    # Mock the internal attempt method to fail first time, succeed second
    call_count = [0]

    def mock_attempt(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            raise ValueError("First attempt failed")
        return FinalAnswer(content="Success")

    extractor._attempt_extraction = mock_attempt

    result = extractor.extract("test", schema_type="final_answer")
    assert isinstance(result, FinalAnswer)
    assert call_count[0] == 2  # Retried once


def test_max_3_attempts(extractor, mock_emitter):
    """Test that extraction fails after max 3 attempts."""
    call_count = [0]

    def mock_attempt(*args, **kwargs):
        call_count[0] += 1
        raise ValueError(f"Attempt {call_count[0]} failed")

    extractor._attempt_extraction = mock_attempt

    with pytest.raises(StructuredOutputExhaustedError) as exc_info:
        extractor.extract("test", schema_type="final_answer")

    assert call_count[0] == 3  # Max attempts reached
    assert len(exc_info.value.failure_reasons) == 3


def test_exhausted_emits_error_trace(extractor, mock_emitter):
    """Test that exhausted error emits ERROR trace."""
    def mock_attempt(*args, **kwargs):
        raise ValueError("Failed")

    extractor._attempt_extraction = mock_attempt

    with pytest.raises(StructuredOutputExhaustedError):
        extractor.extract("test", schema_type="final_answer")

    # Verify ERROR trace was emitted
    mock_emitter.emit_event.assert_called()
    call_args = mock_emitter.emit_event.call_args
    assert call_args[1]["level"] == "error"  # TraceLevel.ERROR
    assert "structured_output_exhausted" in call_args[1]["event_name"]


def test_cooling_temperature_strategy(extractor):
    """Test that temperature cooling strategy is applied (Plan 23 S5)."""
    temperatures = []

    def mock_attempt(raw, schema_type, temperature=0.7, schema_reminder=False):
        temperatures.append(temperature)
        raise ValueError("Failed")

    extractor._attempt_extraction = mock_attempt

    with pytest.raises(StructuredOutputExhaustedError):
        extractor.extract("test", schema_type="final_answer")

    # Should see default -> 0.1 -> 0.0
    assert temperatures[0] == 0.7  # Default
    assert temperatures[1] == 0.1  # Cooled
    assert temperatures[2] == 0.0  # Coldest
