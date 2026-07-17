"""Tests for check_ar7_allowlist.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def allowlist_script():
    return Path(__file__).parent.parent / "scripts" / "check_ar7_allowlist.py"


def test_check_ar7_allowlist_usage(allowlist_script):
    """Test script usage error."""
    result = subprocess.run(
        [sys.executable, str(allowlist_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Usage" in result.stderr


def test_check_ar7_allowlist_nonexistent(allowlist_script):
    """Test with nonexistent file."""
    result = subprocess.run(
        [sys.executable, str(allowlist_script), "HEAD", "nonexistent.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr
