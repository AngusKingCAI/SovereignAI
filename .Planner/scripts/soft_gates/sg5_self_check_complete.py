#!/usr/bin/env python3
"""
Soft Gate SG-5: Self-Check Complete

Warns if Phase 6.0 self-check compliance line is missing.
This is a non-blocking gate that alerts to skipped self-check.
Returns exit code 0 (always passes) but outputs warning if violated.
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check that Phase 6.0 self-check compliance line is present.
    Returns True if gate passes, False otherwise (but always returns exit code 0).
    """
    # Find the most recent plan file (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["Plans", "plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("Plans directory not found, skipping validation")
        return True
    
    # Look for plan files (excluding completed directory)
    plan_files = []
    for pattern in ["plan-*.md", "plan-*.Rev*.md"]:
        plan_files.extend(plans_dir.glob(pattern))
    
    # Filter out completed plans
    plan_files = [f for f in plan_files if "completed" not in str(f)]
    
    if not plan_files:
        print("No plan files found, skipping validation")
        return True
    
    # Get the most recently modified plan file
    latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating plan: {latest_plan.name}")
    
    try:
        with open(latest_plan, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading plan file: {e}")
        return True
    
    # Check for Phase 6.0 compliance line
    phase_6_0_pattern = r"Gate PLAN-6\.0 PASS:"
    if not re.search(phase_6_0_pattern, content):
        print(f"Gate SG-5 WARN: Phase 6.0 self-check compliance line missing")
        print(f"   - Missing: Gate PLAN-6.0 PASS: Self-check complete, {{N}} findings self-fixed, {{N}} deferred to Round Table")
        print(f"   - Recommendation: Run Phase 6.0 self-check before Round Table to catch self-identifiable issues")
        return False
    else:
        print(f"Gate SG-5 PASS: Phase 6.0 self-check compliance line present")
        return True

def main():
    # Always return exit code 0 (soft gate never blocks)
    check_gate_condition()
    sys.exit(0)

if __name__ == "__main__":
    main()