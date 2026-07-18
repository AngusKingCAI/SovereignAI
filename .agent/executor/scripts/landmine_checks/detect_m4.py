#!/usr/bin/env python3
"""
Landmine M4 Detection: Test directory structure for namespace collisions

Checks for test directory names that shadow installed package names,
which creates namespace package collisions that break isinstance()
on all dataclasses/protocols.
"""

import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get repository root using git rev-parse."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # Fallback to current directory if not in git repo
        return Path.cwd()


def detect_m4_namespace_collisions() -> int:
    """Check for test directory names that shadow installed package names."""
    repo_root = get_repo_root()
    test_dir = repo_root / ".agent" / "executor" / "tests"

    if not test_dir.exists():
        print(f"ERROR: {test_dir} does not exist")
        return 1

    # Known package names to check against
    # Based on installed packages and src structure
    package_names = {
        "sovereignai",  # Main package
        # Add other package names as needed
    }

    violations = []

    # Check immediate subdirectories of tests/
    for item in test_dir.iterdir():
        if item.is_dir() and item.name in package_names:
            violations.append(item.name)

    if violations:
        print("M4 LANDMINE DETECTED: Test directory shadows installed package name")
        print("Test directory names must not match installed package names")
        print("This creates namespace package collisions that break isinstance()")
        print()
        for name in violations:
            print(f"  Collision: tests/{name}/ shadows package '{name}'")
        print()
        print("Fix: Rename test directory to non-conflicting name (e.g., app_tests)")
        print("      Update pyproject.toml testpaths accordingly")
        return 1
    else:
        print("M4 check passed: No namespace collisions detected")
        return 0


if __name__ == "__main__":
    sys.exit(detect_m4_namespace_collisions())
