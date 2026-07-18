from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_check_event_frozen_script_exists() -> None:
    script_path = (
        Path(__file__).parent.parent.parent
        / "scripts"
        / "ar_checks"
        / "check_event_frozen.py"
    )
    assert script_path.exists()


def test_check_event_frozen_passes() -> None:
    script_path = (
        Path(__file__).parent.parent.parent
        / "scripts"
        / "ar_checks"
        / "check_event_frozen.py"
    )
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stdout}\n{result.stderr}"
