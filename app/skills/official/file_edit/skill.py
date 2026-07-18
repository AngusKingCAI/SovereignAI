"""File edit skill with search/replace and optional line-range hint.

This skill provides diff-based editing with search/replace operations
and optional line-range hints for disambiguation when search text
matches multiple locations.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.sovereignai.agent.types import AgentErrorObservation
from app.sovereignai.shared.trace_emitter import TraceEmitter, TraceLevel


@dataclass
class LineRangeHint:
    start_line: int
    end_line: int


class FileEditSkill:
    """File edit skill with search/replace and optional line-range hint."""

    def __init__(self, trace: TraceEmitter) -> None:
        """Create a file edit skill.

        Args:
            trace: Trace emitter for logging edit operations.
        """
        self._trace = trace

    def parse_line_hint(self, hint: str | None) -> LineRangeHint | None:
        """Parse line range hint from string.

        Args:
            hint: String in format "start-end" or None.

        Returns:
            LineRangeHint if valid, None otherwise.
        """
        if hint is None:
            return None

        try:
            if "-" in hint:
                start_str, end_str = hint.split("-")
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start <= end and start >= 1:
                    return LineRangeHint(start_line=start, end_line=end)
        except (ValueError, AttributeError):
            pass

        return None

    def find_match_locations(self, content: str, search_text: str) -> list[tuple[int, int]]:
        """Find all locations where search_text appears in content.

        Args:
            content: File content to search.
            search_text: Text to search for.

        Returns:
            List of (start_line, end_line) tuples for each match.
        """
        matches = []
        lines = content.split("\n")

        for i, line in enumerate(lines, start=1):
            if search_text in line:
                matches.append((i, i))

        return matches

    def validate_hint_against_matches(
        self,
        matches: list[tuple[int, int]],
        hint: LineRangeHint | None,
    ) -> bool:
        """Validate that hint matches exactly one location.

        Args:
            matches: List of match locations.
            hint: Line range hint to validate.

        Returns:
            True if hint matches exactly one location, False otherwise.
        """
        if hint is None:
            return len(matches) == 1

        matching_in_range = [
            (start, end)
            for start, end in matches
            if hint.start_line <= start <= hint.end_line
        ]

        return len(matching_in_range) == 1

    def apply_edit(
        self,
        file_path: str,
        search_text: str,
        replace_text: str,
        hint: str | None = None,
    ) -> dict[str, Any]:
        """Apply search/replace edit to file.

        Args:
            file_path: Path to file to edit.
            search_text: Text to search for.
            replace_text: Text to replace with.
            hint: Optional line range hint for disambiguation.

        Returns:
            Dict with success status and result or error information.
        """
        path = Path(file_path)

        if not path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}",
                "retryable": False,
            }

        content = path.read_text()

        matches = self.find_match_locations(content, search_text)

        if not matches:
            return {
                "success": False,
                "error": f"Search text not found: {search_text}",
                "retryable": False,
            }

        line_hint = self.parse_line_hint(hint)

        if len(matches) > 1 and not self.validate_hint_against_matches(matches, line_hint):
            return {
                "success": False,
                "error": (
                    f"Search text matches {len(matches)} locations. "
                    f"Provide line-range hint for disambiguation."
                ),
                "retryable": True,
            }

        if line_hint and len(matches) > 1:
            match_start, match_end = line_hint.start_line, line_hint.end_line
        else:
            match_start, match_end = matches[0]

        lines = content.split("\n")
        for i in range(match_start - 1, match_end):
            if i < len(lines):
                lines[i] = lines[i].replace(search_text, replace_text, 1)
                break

        new_content = "\n".join(lines)
        path.write_text(new_content)

        self._trace.emit(
            component="FileEditSkill",
            level=TraceLevel.INFO,
            message=f"Successfully edited {file_path} (line {match_start})",
        )

        return {
            "success": True,
            "file_edited": file_path,
            "line_edited": match_start,
        }

    def edit(
        self,
        file_path: str,
        search_text: str,
        replace_text: str,
        hint: str | None = None,
    ) -> Any:
        """Main entry point for skill invocation.

        Args:
            file_path: Path to file to edit.
            search_text: Text to search for.
            replace_text: Text to replace with.
            hint: Optional line range hint for disambiguation.

        Returns:
            Result dict or AgentErrorObservation for retryable errors.
        """
        result = self.apply_edit(file_path, search_text, replace_text, hint)

        if not result["success"] and result.get("retryable"):
            return AgentErrorObservation(
                error_type="ambiguous_match",
                message=result["error"],
                retryable=True,
            )

        return result
