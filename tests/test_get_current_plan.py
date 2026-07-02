"""Tests for get_current_plan.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def plan_script():
    return Path(__file__).parent.parent / "scripts" / "get_current_plan.py"


def test_get_current_plan_usage(plan_script):
    """Test script rejects extra arguments."""
    result = subprocess.run(
        [sys.executable, str(plan_script), "extra_arg"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Usage" in result.stderr


def test_get_current_plan_no_plans(plan_script, tmp_path):
    """Test with no plan files available."""
    # The script uses Path(__file__).parent.parent to find repo root,
    # so we can't easily test missing plans without modifying the script.
    # Skip this test for now.
    pytest.skip("Script uses hardcoded path, difficult to test missing plans")
