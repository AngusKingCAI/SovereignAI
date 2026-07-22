#!/usr/bin/env python3
"""
Tool: HG-18 Spec Approved Validation

WHEN TO USE: Phase 2.5, after spec generation, before plan drafting

WHAT IT CHECKS: Plan spec has been approved (✅ Gate PLAN-2.5 PASS compliance line present).
Spec includes header, Executor Manifest shell, phase list, deliverable names, gate names.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-18 PASS: Plan spec approved (Phase 2.5 compliance line present)
- Exit 1: Gate HG-18 FAIL: Plan spec not approved (Phase 2.5 compliance line missing)

FAILURE RECOVERY: Generate plan spec first, get spec approval, add compliance line, re-run this script.
Do NOT proceed to Phase 3 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check that plan spec has been approved (Phase 2.5 compliance line present).
    Returns True if gate passes, False otherwise.
    """
    # Find the most recent plan file (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["plans", "Plans", ".Planner/plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("Plans directory not found, skipping validation")
        return True
    
    # Look for plan files
    plan_files = []
    for pattern in ["plan-*.md", "plan_*.md", "*.md"]:
        plan_files.extend(plans_dir.glob(pattern))
    
    # Filter out non-plan files
    plan_files = [f for f in plan_files if "plan" in f.name.lower()]
    
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
        return False
    
    # Check for Phase 2.5 compliance line
    phase_2_5_pattern = r"✅.*Gate.*PLAN-2\.5.*PASS"
    if re.search(phase_2_5_pattern, content, re.IGNORECASE):
        print(f"Gate HG-18 PASS: Plan spec approved (Phase 2.5 compliance line present)")
        return True
    else:
        print(f"Gate HG-18 FAIL: Plan spec not approved (Phase 2.5 compliance line missing)")
        print(f"   Generate plan spec first, get spec approval, add compliance line")
        return False

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()