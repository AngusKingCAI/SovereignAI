#!/usr/bin/env python3
"""
Hard Gate HG-7: Compliance Lines Present Validation

Validates that all compliance lines are present in the plan.
Blocks plan delivery if compliance lines are missing.

Returns exit code 0 (pass) or 1 (fail)
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check that all compliance lines are present.
    Returns True if gate passes, False otherwise.
    """
    # Find the most recent plan file
    plans_dir = Path("Plans")
    if not plans_dir.exists():
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