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
    # Script now accepts repo_root parameter, so we can test with isolated environment
    # Create minimal test structure in tmp_path
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Create .agent/shared directory with required files
    shared_dir = test_repo / ".agent" / "shared"
    shared_dir.mkdir(parents=True)

    # Create minimal ARCHITECTURE.md and OR_RULES.md
    (shared_dir / "ARCHITECTURE.md").write_text("# Test\n\n## AR Rules\n\nAR1. Test rule\n")
    (shared_dir / "OR_RULES.md").write_text("# Test\n\n### UOR-1\nTest rule\n")

    # Run script with REPO_ROOT environment variable
    import os
    env = os.environ.copy()
    env['REPO_ROOT'] = str(test_repo)

    result = subprocess.run(
        [sys.executable, str(crossref_script)],
        capture_output=True,
        text=True,
        env=env
    )
    # Script should find files from test_repo
    assert result.returncode == 0
