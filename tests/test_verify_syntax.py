"""Tests for verify_syntax.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def verify_script():
    return Path(__file__).parent.parent / "scripts" / "verify_syntax.py"


def test_verify_syntax_python_valid(verify_script):
    """Test valid Python file."""
    result = subprocess.run(
        [sys.executable, str(verify_script), __file__],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_verify_syntax_python_invalid(verify_script, tmp_path):
    """Test invalid Python file."""
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def broken(\n")

    result = subprocess.run(
        [sys.executable, str(verify_script), str(invalid_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FAIL" in result.stderr


def test_verify_syntax_json_valid(verify_script, tmp_path):
    """Test valid JSON file."""
    json_file = tmp_path / "valid.json"
    json_file.write_text('{"key": "value"}')

    result = subprocess.run(
        [sys.executable, str(verify_script), str(json_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_verify_syntax_json_invalid(verify_script, tmp_path):
    """Test invalid JSON file."""
    json_file = tmp_path / "invalid.json"
    json_file.write_text('{"key": invalid}')

    result = subprocess.run(
        [sys.executable, str(verify_script), str(json_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "FAIL" in result.stderr


def test_verify_syntax_markdown_skipped(verify_script, tmp_path):
    """Test markdown files are skipped."""
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test")

    result = subprocess.run(
        [sys.executable, str(verify_script), str(md_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "skipped" in result.stdout


def test_verify_syntax_nonexistent(verify_script):
    """Test nonexistent file."""
    result = subprocess.run(
        [sys.executable, str(verify_script), "nonexistent.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr
