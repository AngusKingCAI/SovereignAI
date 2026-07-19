#!/usr/bin/env python3
"""
Landmine M1 Detection: Dual import paths break protocol isinstance

Wrapper for check_import_paths.py that provides landmine output format.
Checks for app.sovereignai.* imports in files under app/sovereignai/.
All source files in app/sovereignai/ must use sovereignai.* imports
(matches installed package name).
"""

import subprocess
import sys
from pathlib import Path


def check_m1_import_paths() -> int:
    """Run check_import_paths.py and return exit code."""
    # Get repo root from git to handle different script locations
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    repo_root = (
        Path(result.stdout.strip()) if result.returncode == 0
        else Path(__file__).parent.parent.parent.parent.parent
    )
    check_script = repo_root / ".agent" / "executor" / "scripts" / "check_import_paths.py"

    if not check_script.exists():
        print(f"ERROR: {check_script} not found")
        return 1

    result = subprocess.run(
        [sys.executable, str(check_script)],
        capture_output=True,
        text=True,
        cwd=repo_root,
    )

    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(check_m1_import_paths())
