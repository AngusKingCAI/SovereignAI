#!/usr/bin/env python3
"""preflight_check.py — verify all required compliance files exist before plan execution.

Usage: python preflight_check.py --plan <plan_id>

Checks:
1. verify_execution.py exists
2. ATTESTATION_TEMPLATE.md exists
3. check_manifest.py exists
4. append_trace.py exists
5. verify_attestation.py exists
6. .agent/executor/traces/ directory exists (creates if missing)
7. .agent/executor/hooks/ directory exists (creates if missing)
8. Plan file exists and has Executor Manifest

Exit 0 = PASS, Exit 1 = FAIL
"""

import argparse
import os
import sys

REQUIRED_FILES = [
    ".agent/executor/scripts/verify_execution.py",
    ".agent/executor/ATTESTATION_TEMPLATE.md",
    ".agent/executor/hooks/check_manifest.py",
    ".agent/executor/hooks/append_trace.py",
    ".agent/executor/hooks/verify_attestation.py",
]

REQUIRED_DIRS = [
    ".agent/executor/traces",
    ".agent/executor/hooks",
    ".agent/executor/scripts",
]


def check_plan_manifest(plan_id: str) -> tuple[bool, str | None]:
    """Check plan file has Executor Manifest."""
    # Look for plan files with revision suffixes (e.g., plan-28-Rev5.md)
    import glob

    # First try in plans/ directory (active plans)
    plan_pattern = f"plans/plan-{plan_id}*.md"
    plan_files = glob.glob(plan_pattern)

    # If not found, try in plans/completed/ subdirectories
    if not plan_files:
        for subdir in ['0-9', '10-19', '20-29', '30-39', 'Misc']:
            plan_pattern = f"plans/completed/{subdir}/plan-{plan_id}*.md"
            plan_files = glob.glob(plan_pattern)
            if plan_files:
                break

    if not plan_files:
        return False, f"Plan file not found: plan-{plan_id}*.md"

    # Sort by revision number if present, otherwise use the file name
    def extract_revision(filename: str) -> int:
        # Extract revision number from filename like plan-28-Rev5.md
        import re
        match = re.search(r'Rev(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0

    plan_files.sort(key=extract_revision, reverse=True)
    plan_path = plan_files[0]  # Use highest revision

    with open(plan_path) as f:
        content = f.read()

    if "## Executor Manifest" not in content:
        return False, f"Plan {plan_id} missing Executor Manifest (GR13)"

    return True, None


def main() -> bool:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()

    errors = []
    warnings = []

    print(f"[PREFLIGHT] Plan {args.plan}")
    print()

    # Check required files
    for req_file in REQUIRED_FILES:
        if os.path.exists(req_file):
            print(f"  [OK] {req_file}")
        else:
            errors.append(f"Missing required file: {req_file}")
            print(f"  [FAIL] {req_file}")

    # Check/create required directories
    for req_dir in REQUIRED_DIRS:
        if os.path.exists(req_dir):
            print(f"  [OK] {req_dir}/")
        else:
            os.makedirs(req_dir, exist_ok=True)
            warnings.append(f"Created missing directory: {req_dir}")
            print(f"  [WARN] {req_dir}/ (created)")

    # Check plan manifest
    ok, err = check_plan_manifest(args.plan)
    if ok:
        print(f"  [OK] Plan {args.plan} has Executor Manifest")
    else:
        if err:
            errors.append(err)
        print(f"  [FAIL] {err}")

    print()
    if errors:
        print(f"FAIL: {len(errors)} critical issues found")
        for e in errors:
            print(f"  [FAIL] {e}")
        if warnings:
            for w in warnings:
                print(f"  [WARN] {w}")
        return False
    else:
        print("PASS: All preflight checks passed")
        if warnings:
            for w in warnings:
                print(f"  [WARN] {w}")
        return True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
