"""Tests for run_all_landmine_checks.py script."""

from pathlib import Path

import pytest


@pytest.fixture
def check_script():
    return Path(__file__).parent.parent / "scripts" / "landmine_checks" / "run_all_landmine_checks.py"


def test_run_all_landmine_checks_exists(check_script):
    """Test script exists and is executable."""
    assert check_script.exists()
    assert check_script.is_file()
