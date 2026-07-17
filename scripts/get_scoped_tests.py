#!/usr/bin/env python3
"""Determine scoped test files based on changed Python files.

For each changed .py file, finds test files that import or reference it.
Returns a list of test file paths to run.
"""

import sys
from pathlib import Path


def get_test_files_for_changed_files(changed_files: list[str]) -> list[str]:
    """Find test files that import or reference changed Python files."""
    test_files = set()

    for changed_file in changed_files:
        file_path = Path(changed_file)
        if file_path.suffix != ".py":
            continue

        # Get module name (e.g., scripts/ar_checks/spec_match.py -> scripts.ar_checks.spec_match)
        module_name = str(file_path.with_suffix("")).replace("/", ".")
        basename = file_path.stem

        # Search test files for references to this module
        tests_dir = Path("tests")
        if not tests_dir.exists():
            continue

        for test_file in tests_dir.rglob("*.py"):
            try:
                content = test_file.read_text(encoding="utf-8")
                # Check if test file imports or references the changed module
                # Look for import statements or qualified names
                module_pattern = (
                    f"from {module_name}" in content
                    or f"import {module_name}" in content
                )
                # Check for basename in test function names or class names
                basename_pattern = (
                    f"test_{basename}" in content
                    or f"Test{basename.capitalize()}" in content
                )
                # Check if test file name contains the basename
                filename_pattern = basename in test_file.name

                if module_pattern or basename_pattern or filename_pattern:
                    test_files.add(str(test_file))
            except Exception:
                # Skip files that can't be read
                continue

    return sorted(test_files)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: get_scoped_tests.py <changed-file1> <changed-file2> ...", file=sys.stderr)
        sys.exit(1)

    changed_files = sys.argv[1:]
    test_files = get_test_files_for_changed_files(changed_files)

    if test_files:
        for test_file in test_files:
            print(test_file)
    else:
        # If no test files found but we had changed .py files, this is a coverage gap
        if any(f.endswith(".py") for f in changed_files):
            print("ERROR: No test files found for changed Python files", file=sys.stderr)
            sys.exit(1)
