"""Tests for check_ar7_allowlist.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def allowlist_script():
    return Path(__file__).parent.parent / "scripts" / "ar_checks" / "check_ar7_allowlist.py"


def test_check_ar7_allowlist_usage(allowlist_script):
    """Test script runs successfully without arguments (full check)."""
    result = subprocess.run(
        [sys.executable, str(allowlist_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "AR7 allowlist check passed" in result.stdout



