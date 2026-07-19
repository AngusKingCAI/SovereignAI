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


def check_plan_manifest(plan_id):
    """Check plan file has Executor Manifest."""
    plan_path = f"prompts/plan-{plan_id}.md"
    if not os.path.exists(plan_path):
        return False, f"Plan file not found: {plan_path}"

    with open(plan_path) as f:
        content = f.read()

    if "## Executor Manifest" not in content:
        return False, f"Plan {plan_id} missing Executor Manifest (GR14)"

    return True, None


def main():
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
            print(f"  ✅ {req_file}")
        else:
            errors.append(f"Missing required file: {req_file}")
            print(f"  ❌ {req_file}")

    # Check/create required directories
    for req_dir in REQUIRED_DIRS:
        if os.path.exists(req_dir):
            print(f"  ✅ {req_dir}/")
        else:
            os.makedirs(req_dir, exist_ok=True)
            warnings.append(f"Created missing directory: {req_dir}")
            print(f"  ⚠️  {req_dir}/ (created)")

    # Check plan manifest
    ok, err = check_plan_manifest(args.plan)
    if ok:
        print(f"  ✅ Plan {args.plan} has Executor Manifest")
    else:
        errors.append(err)
        print(f"  ❌ {err}")

    print()
    if errors:
        print(f"FAIL: {len(errors)} critical issues found")
        for e in errors:
            print(f"  ❌ {e}")
        if warnings:
            for w in warnings:
                print(f"  ⚠️  {w}")
        return False
    else:
        print(f"PASS: All preflight checks passed")
        if warnings:
            for w in warnings:
                print(f"  ⚠️  {w}")
        return True


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
