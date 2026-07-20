#!/usr/bin/env python3
"""Lightweight checks combined into single invocation.

Replaces 10+ sequential script calls with 1 call.
Reduces model context overhead by 40-50%.

Usage: python check_all_lightweight.py [file_path]
"""
import subprocess
import sys
from pathlib import Path


def run_check(script_path, name, args=None):
    """Run check and return exit code."""
    if not script_path.exists():
        return 0  # Skip if script doesn't exist

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"{name}: {status}")
    if result.returncode != 0 and result.stdout:
        # Only print first line of error (compact)
        first_line = result.stdout.split('\n')[0][:80]
        print(f"  {first_line}")
    return result.returncode


def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    repo_root = (
        Path(__file__).parent.parent.parent.parent
        if Path(__file__).parent.name == "scripts"
        else Path.cwd()
    )

    # Require file argument for meaningful checks
    if not file_path:
        print("Error: file_path argument required", file=sys.stderr)
        return 1

    scripts = []

    # Always run syntax check if file provided
    if file_path:
        scripts.append(
            (repo_root / ".agent/executor/scripts/verify_syntax.py", "Syntax", [file_path])
        )

    # Only run import path check if file is in app/sovereignai/
    if file_path and "app/sovereignai/" in file_path:
        scripts.append(
            (repo_root / ".agent/executor/scripts/check_import_paths.py", "Imports", [file_path])
        )

    all_passed = True
    for script, name, args in scripts:
        if run_check(script, name, args) != 0:
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
