"""Tests for check_rule_crossrefs_doc.py script."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.fixture
def check_script():
    return Path(__file__).parent.parent / "scripts" / "ar_checks" / "check_rule_crossrefs_doc.py"


def test_check_rule_crossrefs_doc_usage(check_script):
    """Test script runs successfully without arguments."""
    result = subprocess.run(
        [sys.executable, str(check_script)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
