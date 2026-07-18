from __future__ import annotations

import pytest
from sovereignai.skills.observation import ToolCall, ToolCallErrorObservation
from sovereignai.skills.parser import ToolCallParser


def test_json_parsing() -> None:
    parser = ToolCallParser()
    text = '{"name": "test_tool", "arguments": {"arg1": "value1"}}'
    result = parser.parse(text)

    assert isinstance(result, ToolCall)
    assert result.name == "test_tool"
    assert result.arguments == {"arg1": "value1"}


def test_pluggable_format() -> None:
    parser = ToolCallParser()

    def custom_parser(text: str) -> ToolCall | ToolCallErrorObservation:
        return ToolCall(name="custom", arguments={"source": "custom"})

    parser.register_format("custom", custom_parser)

    result = parser.parse("custom format")
    assert isinstance(result, ToolCall)
    assert result.name == "custom"


def test_duplicate_format_name_rejection() -> None:
    parser = ToolCallParser()

    with pytest.raises(ValueError, match="already registered"):
        parser.register_format("json", lambda x: ToolCall(name="dup", arguments={}))


def test_malformed_xml_rejection() -> None:
    parser = ToolCallParser()
    text = "<invalid>xml"
    result = parser.parse(text)

    assert isinstance(result, ToolCallErrorObservation)
    # The parser tries JSON first (fails with json_decode_error), then XML (fails with xml_parse_error)
    # Returns the first error from JSON parsing
    assert result.error_type == "json_decode_error"
    assert result.retryable is True


def test_invalid_json() -> None:
    parser = ToolCallParser()
    text = '{"invalid": json}'
    result = parser.parse(text)

    assert isinstance(result, ToolCallErrorObservation)
    # The parser tries JSON first (fails with json_decode_error), then XML (fails with xml_parse_error)
    # Returns the first error from JSON parsing
    assert result.error_type == "json_decode_error"
    assert result.retryable is True


def test_missing_name_field() -> None:
    parser = ToolCallParser()
    text = '{"arguments": {}}'
    result = parser.parse(text)

    assert isinstance(result, ToolCallErrorObservation)
    # The parser tries JSON first, which returns missing_field error
    assert result.error_type == "missing_field"
