#!/usr/bin/env python3
"""Run only failing tests from previous pytest run for faster iteration."""

import subprocess
import sys
from pathlib import Path


def get_failing_tests() -> list[str]:
    """Extract failing test IDs from .pytest_failures.txt cache."""
    cache_file = Path(".pytest_failures.txt")
    if not cache_file.exists():
        return []

    content = cache_file.read_text(encoding="utf-8")
    if not content.strip():
        return []

    return [line.strip() for line in content.strip().split("\n") if line.strip()]


def cache_failing_tests(test_ids: list[str]) -> None:
    """Cache failing test IDs to .pytest_failures.txt."""
    cache_file = Path(".pytest_failures.txt")
    cache_file.write_text("\n".join(test_ids), encoding="utf-8")


def run_pytest_and_capture_failures(test_path: str, timeout: int = 300) -> tuple[int, list[str]]:
    """Run pytest and capture failing test IDs."""
    cmd = ["pytest", test_path, "-v", "--tb=line", f"--timeout={timeout}"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout + 10
    )

    # Parse output for FAILED lines
    failing_tests = []
    for line in result.stdout.split("\n"):
        if "FAILED" in line and "::" in line:
            # Extract test ID from line like ".agent/executor/tests/test_foo.py::test_bar FAILED"
            parts = line.split()
            for part in parts:
                if "::" in part:
                    failing_tests.append(part)
                    break

    return result.returncode, failing_tests


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: run_failing_tests.py <test_path> [--full]", file=sys.stderr)
        return 1

    test_path = sys.argv[1]
    force_full = "--full" in sys.argv

    # If --full flag, skip cache and run full suite
    if force_full:
        print("Running full test suite (--full flag)")
        returncode, failing = run_pytest_and_capture_failures(test_path)
        cache_failing_tests(failing)
        return returncode

    # Check for cached failures
    failing_tests = get_failing_tests()

    if not failing_tests:
        print("No cached failures found, running full suite")
        returncode, failing = run_pytest_and_capture_failures(test_path)
        cache_failing_tests(failing)
        return returncode

    print(f"Running {len(failing_tests)} failing tests from cache")
    failing_tests_str = " ".join(failing_tests)
    cmd = ["pytest", failing_tests_str, "-v", "--tb=line", "--timeout=300"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=310
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    # If all tests pass, clear cache
    if result.returncode == 0:
        print("All failing tests now pass - clearing cache")
        Path(".pytest_failures.txt").unlink(missing_ok=True)
        return 0

    # Otherwise, update cache with still-failing tests
    still_failing = []
    for line in result.stdout.split("\n"):
        if "FAILED" in line and "::" in line:
            parts = line.split()
            for part in parts:
                if "::" in part:
                    still_failing.append(part)
                    break

    cache_failing_tests(still_failing)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
