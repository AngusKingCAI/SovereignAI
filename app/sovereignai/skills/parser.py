from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import defusedxml.ElementTree as ElementTree

from app.sovereignai.skills.observation import ToolCall, ToolCallErrorObservation


class ToolCallParser:
    def __init__(self) -> None:
        self._formats: dict[str, Callable[[str], ToolCall | ToolCallErrorObservation]] = {}
        self._register_default_formats()

    def _register_default_formats(self) -> None:
        self.register_format("json", self._parse_json)
        self.register_format("xml", self._parse_xml)

    def register_format(
        self,
        name: str,
        parser_func: Callable[[str], ToolCall | ToolCallErrorObservation],
    ) -> None:
        if name in self._formats:
            raise ValueError(f"Format '{name}' already registered")
        self._formats[name] = parser_func

    def parse(self, text: str) -> ToolCall | ToolCallErrorObservation:
        for _format_name, parser in self._formats.items():
            result = parser(text)
            if isinstance(result, ToolCall):
                return result

        return ToolCallErrorObservation(
            error_type="parse_error",
            message="Failed to parse tool call with any registered format",
            suggestion="Ensure tool call uses valid JSON or XML format",
            retryable=True,
        )

    def _parse_json(self, text: str) -> ToolCall | ToolCallErrorObservation:
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                return ToolCallErrorObservation(
                    error_type="invalid_json",
                    message="JSON must be an object",
                    suggestion="Use JSON object format",
                    retryable=True,
                )

            name = data.get("name")
            arguments = data.get("arguments", {})

            if not name:
                return ToolCallErrorObservation(
                    error_type="missing_field",
                    message="Missing 'name' field in JSON",
                    suggestion="Include 'name' field with tool name",
                    retryable=True,
                )

            return ToolCall(name=name, arguments=arguments)
        except json.JSONDecodeError:
            return ToolCallErrorObservation(
                error_type="json_decode_error",
                message="Invalid JSON format",
                suggestion="Use valid JSON format",
                retryable=True,
            )

    def _parse_xml(self, text: str) -> ToolCall | ToolCallErrorObservation:
        try:
            root = ElementTree.fromstring(text)
            if root.tag != "tool_call":
                return ToolCallErrorObservation(
                    error_type="invalid_xml",
                    message="XML root must be tool_call",
                    suggestion="Use tool_call as root element",
                    retryable=True,
                )

            name = root.get("name")
            if not name:
                return ToolCallErrorObservation(
                    error_type="missing_attribute",
                    message="Missing 'name' attribute on tool_call",
                    suggestion="Include 'name' attribute on tool_call",
                    retryable=True,
                )

            arguments: dict[str, Any] = {}
            for child in root:
                if child.tag == "arguments":
                    for arg in child:
                        arguments[arg.tag] = arg.text

            return ToolCall(name=name, arguments=arguments)
        except ElementTree.ParseError:
            return ToolCallErrorObservation(
                error_type="xml_parse_error",
                message="Invalid XML format",
                suggestion="Use valid XML format",
                retryable=True,
            )
