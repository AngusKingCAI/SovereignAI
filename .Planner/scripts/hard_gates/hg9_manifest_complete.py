#!/usr/bin/env python3
"""
Hard Gate HG-9: Manifest Complete Validation

Validates that Executor Manifest is complete.
Blocks plan delivery if Executor Manifest is incomplete.

Returns exit code 0 (pass) or 1 (fail)
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
    Check that Executor Manifest is complete.
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
    
    # Check for Executor Manifest section
    if 'Executor Manifest' not in content and '## Executor Manifest' not in content:
        issues.append("Missing Executor Manifest section")
    else:
        print("Found Executor Manifest section")
    
    # Check for required manifest components
    required_manifest_components = [
        r'Phases?',
        r'Deliverables?',
        r'Gates?',
        r'Success Criteria?',
        r'Exit Conditions?',
    ]
    
    for component in required_manifest_components:
        if not re.search(component, content, re.IGNORECASE):
            issues.append(f"Missing manifest component: {component}")
    
    # Check for phase definitions
    phase_pattern = r'## Phase\s+\d+'
    phases = re.findall(phase_pattern, content)
    
    if not phases:
        issues.append("No phase definitions found in manifest")
    else:
        print(f"Found {len(phases)} phase definitions")
    
    # Check for deliverable definitions
    deliverable_pattern = r'Deliverable\s*:'
    deliverables = re.findall(deliverable_pattern, content, re.IGNORECASE)
    
    if not deliverables:
        issues.append("No deliverable definitions found in manifest")
    else:
        print(f"Found {len(deliverables)} deliverable definitions")
    
    # Check for gate definitions
    gate_pattern = r'Gate\s*:'
    gates = re.findall(gate_pattern, content, re.IGNORECASE)
    
    if not gates:
        issues.append("No gate definitions found in manifest")
    else:
        print(f"Found {len(gates)} gate definitions")
    
    if issues:
        print(f"❌ Gate HG-9 FAIL: Executor Manifest validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-9 PASS: Executor Manifest is complete")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()