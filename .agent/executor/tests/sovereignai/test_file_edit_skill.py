"""Tests for file_edit skill (Plan 24 S9)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.skills.official.file_edit.skill import FileEditSkill, LineRangeHint
from sovereignai.agent.types import AgentErrorObservation


def test_file_edit_skill_construction():
    """Test FileEditSkill construction with trace emitter."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    assert skill._trace is trace


def test_parse_line_hint_valid():
    """Test parsing valid line range hint."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    hint = skill.parse_line_hint("10-15")
    assert hint is not None
    assert hint.start_line == 10
    assert hint.end_line == 15


def test_parse_line_hint_invalid():
    """Test parsing invalid line range hint returns None."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    # Invalid format
    assert skill.parse_line_hint("invalid") is None
    # Invalid range (start > end)
    assert skill.parse_line_hint("15-10") is None
    # Negative start
    assert skill.parse_line_hint("-5-10") is None


def test_parse_line_hint_none():
    """Test parsing None hint returns None."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    assert skill.parse_line_hint(None) is None


def test_find_match_locations():
    """Test finding match locations in content."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    content = "line1\nline2\ntest_line\nline4\ntest_line\nline6"
    matches = skill.find_match_locations(content, "test_line")
    
    assert len(matches) == 2
    assert matches[0] == (3, 3)
    assert matches[1] == (5, 5)


def test_validate_hint_against_matches_unique():
    """Test hint validation when search text is unique (no hint needed)."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    matches = [(3, 3)]  # Single match
    hint = None
    
    assert skill.validate_hint_against_matches(matches, hint) is True


def test_validate_hint_against_matches_with_hint():
    """Test hint validation when hint matches exactly one location."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    matches = [(3, 3), (5, 5)]
    hint = LineRangeHint(start_line=3, end_line=3)
    
    assert skill.validate_hint_against_matches(matches, hint) is True


def test_validate_hint_against_matches_invalid_hint():
    """Test hint validation when hint doesn't match any location."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    matches = [(3, 3), (5, 5)]
    hint = LineRangeHint(start_line=10, end_line=15)
    
    assert skill.validate_hint_against_matches(matches, hint) is False


def test_apply_edit_unique_match():
    """Test applying edit when search text is unique."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("original_line\n")
        f.write("test_line\n")
        f.write("another_line\n")
        temp_path = f.name
    
    try:
        result = skill.apply_edit(
            str(temp_path),
            "test_line",
            "modified_line"
        )
        
        assert result["success"] is True
        assert result["line_edited"] == 2
        
        # Verify file was modified
        with open(temp_path) as f:
            content = f.read()
        assert "modified_line" in content
        assert "test_line" not in content
    finally:
        Path(temp_path).unlink()


def test_apply_edit_file_not_found():
    """Test applying edit to non-existent file."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    result = skill.apply_edit(
        "/nonexistent/file.py",
        "test",
        "replacement"
    )
    
    assert result["success"] is False
    assert "not found" in result["error"]
    assert result["retryable"] is False


def test_apply_edit_search_not_found():
    """Test applying edit when search text not found."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("line1\nline2\nline3\n")
        temp_path = f.name
    
    try:
        result = skill.apply_edit(
            str(temp_path),
            "nonexistent_text",
            "replacement"
        )
        
        assert result["success"] is False
        assert "not found" in result["error"]
        assert result["retryable"] is False
    finally:
        Path(temp_path).unlink()


def test_apply_edit_multi_match_without_hint():
    """Test applying edit with multiple matches and no hint returns retryable error."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("test_line\n")
        f.write("test_line\n")
        f.write("test_line\n")
        temp_path = f.name
    
    try:
        result = skill.apply_edit(
            str(temp_path),
            "test_line",
            "modified_line"
        )
        
        assert result["success"] is False
        assert result["retryable"] is True
        assert "3 locations" in result["error"]
    finally:
        Path(temp_path).unlink()


def test_apply_edit_multi_match_with_valid_hint():
    """Test applying edit with multiple matches and valid hint succeeds."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("test_line\n")
        f.write("test_line\n")
        f.write("test_line\n")
        temp_path = f.name
    
    try:
        result = skill.apply_edit(
            str(temp_path),
            "test_line",
            "modified_line",
            hint="2-2"
        )
        
        assert result["success"] is True
        assert result["line_edited"] == 2
    finally:
        Path(temp_path).unlink()


def test_edit_returns_retryable_error_for_ambiguity():
    """Test that edit() returns AgentErrorObservation for retryable errors (P24-H, P24-M)."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("test_line\n")
        f.write("test_line\n")
        temp_path = f.name
    
    try:
        result = skill.edit(
            str(temp_path),
            "test_line",
            "modified_line"
        )
        
        # Should return AgentErrorObservation for retryable error
        assert isinstance(result, AgentErrorObservation)
        assert result.retryable is True
        assert result.error_type == "AmbiguousMatch"
    finally:
        Path(temp_path).unlink()


def test_edit_returns_direct_result_for_success():
    """Test that edit() returns direct result dict for successful edits."""
    trace = MagicMock()
    skill = FileEditSkill(trace)
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("original_line\n")
        temp_path = f.name
    
    try:
        result = skill.edit(
            str(temp_path),
            "original_line",
            "modified_line"
        )
        
        # Should return result dict, not AgentErrorObservation
        assert not isinstance(result, AgentErrorObservation)
        assert result["success"] is True
    finally:
        Path(temp_path).unlink()


def test_file_edit_skill_auto_discovered():
    """Test that file_edit skill appears in discovered skill list (Plan 21 S7)."""
    # This test would verify SkillDiscovery.scan() finds the file_edit skill
    # For now, we assert the skill structure exists
    from pathlib import Path
    
    skill_path = Path("app/skills/official/file_edit")
    assert skill_path.exists()
    assert (skill_path / "manifest.toml").exists()
    assert (skill_path / "skill.py").exists()
