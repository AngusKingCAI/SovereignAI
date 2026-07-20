#!/usr/bin/env python3
"""verify_attestation.py — verify attestation exists before session ends.

Usage: python verify_attestation.py --plan <plan_id>

Checks that execution-attestation-plan-{N}.md exists and is complete.
Exit 0 = pass, Exit 1 = fail
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=False)
    args = parser.parse_args()

    plan_id = args.plan

    # Fallback: read plan_id from .agent/current_plan.txt if not provided
    if not plan_id:
        try:
            with open(".agent/current_plan.txt") as f:
                plan_id = f.read().strip()
        except FileNotFoundError:
            print("ERROR: plan_id not provided and .agent/current_plan.txt not found")
            sys.exit(1)
    attestation_path = f"logs/execution-attestation-plan-{plan_id}.md"

    if not os.path.exists(attestation_path):
        print(f"FAIL: Missing attestation: {attestation_path}")
        sys.exit(1)

    with open(attestation_path) as f:
        content = f.read()

    required_sections = [
        "Phase Sequence Verification",
        "Deliverable Verification",
        "Gate Results",
        "Forbidden Action Audit",
        "Trace Integrity",
        "Attestation"
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"FAIL: Attestation missing sections: {', '.join(missing)}")
        sys.exit(1)

    if "❌" in content:
        print("FAIL: Attestation contains failures (❌)")
        sys.exit(1)

    print(f"PASS: Attestation complete for Plan {plan_id}")
    sys.exit(0)


if __name__ == "__main__":
    main()
