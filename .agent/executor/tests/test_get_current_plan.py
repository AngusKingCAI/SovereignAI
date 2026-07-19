"""Tests for get_current_plan.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def plan_script() -> Path:
    return Path(__file__).parent.parent / "scripts" / "get_current_plan.py"


def test_get_current_plan_usage(plan_script: Path) -> None:
    """Test script rejects extra arguments."""
    result = subprocess.run(
        [sys.executable, str(plan_script), "extra_arg"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "Usage" in result.stderr


def test_get_current_plan_no_plans(plan_script: Path, tmp_path: Path) -> None:
    """Test with no plan files available."""
    # Script now accepts REPO_ROOT environment variable, so we can test with isolated environment
    # Create minimal test structure in tmp_path
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    # Create .agent/shared directory with PLANS.md
    shared_dir = test_repo / ".agent" / "shared"
    shared_dir.mkdir(parents=True)

    # Create PLANS.md with no active plan and empty recent completed
    plans_md = shared_dir / "PLANS.md"
    plans_md.write_text("""# PLANS.md

## Active Plan

None.

## Recent Completed

| Prompt | Description | Tests | Date |
|--------|-------------|-------|------|
| prompt-test | Test | 100 | 2026-07-19 |
""")

    # Run script with REPO_ROOT environment variable
    import os
    env = os.environ.copy()
    env["REPO_ROOT"] = str(test_repo)

    result = subprocess.run(
        [sys.executable, str(plan_script)],
        capture_output=True,
        text=True,
        env=env
    )
    # Should fail because plan file doesn't exist
    assert result.returncode != 0
    assert "No active plan or recent history found" in result.stderr
