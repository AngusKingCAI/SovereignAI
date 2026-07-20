#!/usr/bin/env python3
"""
Run all AR checks for the model registry module.

This script runs all architecture rule checks to ensure the model registry
implementation follows architectural principles.
"""

import subprocess
import sys
from pathlib import Path


def run_check(check_name: str, script_path: Path) -> bool:
    """Run a single AR check and return True if it passes."""
    print(f"\n{'='*60}")
    print(f"Running: {check_name}")
    print(f"{'='*60}")

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    return result.returncode == 0


def main() -> int:
    """Run all AR checks."""
    checks_dir = Path(__file__).parent

    # Define all checks
    checks = [
        (
            "No Direct Provider Calls",
            checks_dir / "check_model_registry_no_direct_provider_calls.py",
        ),
        ("Adapter Registry", checks_dir / "check_model_registry_adapter_registry.py"),
        ("Transaction Safety", checks_dir / "check_model_registry_transaction_safety.py"),
    ]

    results = {}

    for check_name, script_path in checks:
        if not script_path.exists():
            print(f"SKIP: {check_name} - script not found")
            results[check_name] = None
            continue

        passed = run_check(check_name, script_path)
        results[check_name] = passed

    # Summary
    print(f"\n{'='*60}")
    print("AR CHECK SUMMARY")
    print(f"{'='*60}")

    passed_count = sum(1 for v in results.values() if v is True)
    failed_count = sum(1 for v in results.values() if v is False)
    skipped_count = sum(1 for v in results.values() if v is None)

    for check_name, passed in results.items():
        if passed is True:
            print(f"[PASS] {check_name}")
        elif passed is False:
            print(f"[FAIL] {check_name}")
        else:
            print(f"[SKIP] {check_name}")

    print(f"\nTotal: {passed_count} passed, {failed_count} failed, {skipped_count} skipped")

    if failed_count > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
