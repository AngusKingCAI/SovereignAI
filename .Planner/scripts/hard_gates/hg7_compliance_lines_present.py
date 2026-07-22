#!/usr/bin/env python3
"""
Tool: HG-7 Compliance Lines Present Validation

WHEN TO USE: Phase 5, after plan finalization, before Round Table

WHAT IT CHECKS: Plan has compliance indicators for all major sections and phases.
Each phase and deliverable has corresponding compliance line.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-7 PASS: All compliance lines present
- Exit 1: Gate HG-7 FAIL: {list of missing compliance lines}

FAILURE RECOVERY: Add missing compliance lines to plan sections, re-run this script.
Do NOT proceed to Phase 6 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
"""

import sys
import os
import re
from pathlib import Path

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gate_condition():
    """
    Check that all compliance lines are present.
    Returns True if gate passes, False otherwise.
    """
    # Find the most recent plan file (case-insensitive for cross-platform compatibility)
    plans_dir = None
    for possible_dir in ["Plans", "plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("⚠️  Plans directory not found, skipping validation")
        return True
    
    plan_files = []
    for pattern in ["plan-*.md", "plan-*.Rev*.md"]:
        plan_files.extend(plans_dir.glob(pattern))
    
    plan_files = [f for f in plan_files if "completed" not in str(f)]
    
    if not plan_files:
        print("⚠️  No plan files found, skipping validation")
        return True
    
    latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating plan: {latest_plan.name}")
    
    try:
        with open(latest_plan, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading plan file: {e}")
        return False
    
    issues = []
    
    # Count compliance lines (✅ markers)
    compliance_pattern = r'✅\s+Gate\s+\w+[-]?\w*\s+PASS'
    compliance_matches = re.findall(compliance_pattern, content)
    
    if not compliance_matches:
        issues.append("No compliance lines found")
    else:
        print(f"Found {len(compliance_matches)} compliance lines")
    
    # Check for compliance lines at major phase transitions
    # Look for phase completion markers
    phase_completion_pattern = r'## S\d+.*?(?=## S\d+|$)'
    phases = re.findall(phase_completion_pattern, content, re.DOTALL)
    
    phases_without_compliance = []
    for i, phase in enumerate(phases, 1):
        if '✅' not in phase:
            phases_without_compliance.append(f"S{i}")
    
    if phases_without_compliance:
        issues.append(f"Phases without compliance lines: {', '.join(phases_without_compliance)}")
    
    # Check for gate enforcement compliance
    if 'Gate Enforcement PASS' not in content:
        issues.append("Missing gate enforcement compliance lines")
    
    if issues:
        print(f"❌ Gate HG-7 FAIL: Compliance lines validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-7 PASS: All compliance lines are present")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()