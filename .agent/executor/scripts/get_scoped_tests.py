#!/usr/bin/env python3
"""
Determine which test suite to run based on modified files.

Usage:
    python get_scoped_tests.py [architect|sovereignai|all]

Returns:
    Exit code 0 with test path(s) on stdout
"""

import subprocess
import sys
from pathlib import Path


def get_architect_test_paths() -> list[str]:
    """Return test paths for architect/executor system."""
    return [".agent/executor/tests/test_*.py"]


def get_sovereignai_test_paths() -> list[str]:
    """Return test paths for sovereignai application code."""
    return [
        ".agent/executor/tests/app_tests/",
        ".agent/executor/tests/sovereignai/",
        ".agent/executor/tests/conformance/",
        ".agent/executor/tests/contracts/",
        ".agent/executor/tests/property/"
    ]


def get_all_test_paths() -> list[str]:
    """Return all test paths."""
    return [".agent/executor/tests/"]


def determine_test_scope() -> str:
    """Analyze git changes to determine test scope."""
    try:
        # Check if this is a fix plan (COR-1: test-fix plans run full suite)
        # Use get_current_plan.py to get current plan
        get_current_plan_script = Path(__file__).parent / "get_current_plan.py"
        if get_current_plan_script.exists():
            result = subprocess.run(
                ["python", str(get_current_plan_script)],
                capture_output=True,
                text=True,
                check=True
            )
            current_plan = result.stdout.strip()
            if "plan-fix" in current_plan or "plan-workflow-fix" in current_plan:
                return "all"  # Fix plans always run full suite

        result = subprocess.run(
            ["git", "log", "--name-only", "-1", "--pretty=format:"],
            capture_output=True,
            text=True,
            check=True
        )
        changed_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Check if only test files changed
        test_only_changed = all(
            f.startswith(".agent/executor/tests/") or f == ""
            for f in changed_files
        )

        # Check if any architect/executor files changed
        architect_changed = any(
            f.startswith(".agent/") or f.startswith(".devin/")
            for f in changed_files
        )

        # Check if any sovereignai files changed
        sovereignai_changed = any(
            f.startswith("app/") or f.startswith("app/sovereignai/")
            for f in changed_files
        )

        if test_only_changed:
            return "all"  # Test-only changes run full suite
        elif architect_changed and sovereignai_changed:
            return "all"
        elif architect_changed:
            return "architect"
        elif sovereignai_changed:
            return "sovereignai"
        else:
            return "all"  # Default to all if no changes detected
    except Exception:
        return "all"  # Default to all on error


def main() -> int:
    scope = sys.argv[1] if len(sys.argv) > 1 else determine_test_scope()

    if scope == "architect":
        paths = get_architect_test_paths()
    elif scope == "sovereignai":
        paths = get_sovereignai_test_paths()
    else:  # all
        paths = get_all_test_paths()

    for path in paths:
        print(path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
