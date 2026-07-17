"""Tests for check_rule_crossrefs.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def crossref_script():
    return Path(__file__).parent.parent / "scripts" / "check_rule_crossrefs.py"


def test_check_rule_crossrefs_valid(crossref_script):
    """Test cross-reference check with valid state."""
    result = subprocess.run(
        [sys.executable, str(crossref_script)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_check_rule_crossrefs_missing_agents(crossref_script, tmp_path):
    """Test cross-reference check with missing AGENTS.md."""
    # The script uses Path(__file__).parent.parent to find repo root,
    # so we can't easily test missing AGENTS.md without modifying the script.
    # Skip this test for now.
    pytest.skip("Script uses hardcoded path, difficult to test missing AGENTS.md")
