"""Tests for check_component_manifest_kwargs_ast.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def check_script():
    return (
        Path(__file__).parent.parent / "scripts" / "ar_checks" /
        "check_component_manifest_kwargs_ast.py"
    )


def test_check_component_manifest_kwargs_ast_usage(check_script):
    """Test script runs successfully without arguments."""
    result = subprocess.run(
        [sys.executable, str(check_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
