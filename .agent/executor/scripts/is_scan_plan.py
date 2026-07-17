#!/usr/bin/env python3
"""Determine if current plan is a scan plan (plan number % 5 == 0)."""

import sys
from pathlib import Path


def is_scan_plan(plan_file: str) -> bool:
    """Return True if plan number is divisible by 5."""
    try:
        # Extract plan number from filename like "plan-21-rev11.md"
        filename = Path(plan_file).name
        # Handle both "plan-N-revM.md" and "plan-N.md" formats
        if filename.startswith("plan-"):
            parts = filename.replace(".md", "").split("-")
            # plan-N-revM -> ["plan", "N", "revM"]
            # plan-N -> ["plan", "N"]
            if len(parts) >= 2 and parts[1].isdigit():
                plan_number = int(parts[1])
                return plan_number % 5 == 0
    except (ValueError, IndexError):
        pass
    return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: is_scan_plan.py <plan-file>", file=sys.stderr)
        sys.exit(1)

    plan_file = sys.argv[1]
    if is_scan_plan(plan_file):
        print("true")
    else:
        print("false")
