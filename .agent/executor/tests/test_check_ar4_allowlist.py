"""Tests for check_ar4_allowlist.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def allowlist_script():
    return Path(__file__).parent.parent / "scripts" / "check_ar4_allowlist.py"


def test_check_ar4_allowlist_usage(allowlist_script):
    """Test script requires two arguments: commit and file path."""
    result = subprocess.run(
        [sys.executable, str(allowlist_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Usage:" in result.stderr


def test_check_ar4_allowlist_nonexistent_file(allowlist_script):
    """Test script fails gracefully on nonexistent file."""
    result = subprocess.run(
        [sys.executable, str(allowlist_script), "HEAD", "nonexistent.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "not found" in result.stderr
