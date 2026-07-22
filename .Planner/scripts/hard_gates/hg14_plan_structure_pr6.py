#!/usr/bin/env python3
"""
Hard Gate HG-14: Plan Structure PR6 Validation

Validates that plan structure follows PR6 requirements.
Blocks plan delivery if structure violates PR6.
Returns exit code 0 (pass) or 1 (fail)
"""

import sys
import os
import re
from pathlib import Path

def check_gate_condition():
    """
    Check that plan structure follows PR6 requirements.
    Returns True if gate passes, False otherwise.
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
        return False
    
    issues = []
    
    # Check for PR6 compliance: Standard structure (header, manifest, phases, deliverables)
    required_structure_elements = {
        'Header': [r'# Plan', r'## Vision', r'## Principles', r'## Overview'],
        'Manifest': [r'## Executor Manifest', r'## Manifest', r'Manifest:'],
        'Phases': [r'## Phase', r'## Step', r'## Implementation'],
        'Deliverables': [r'Deliverable', r'## Output', r'## Result'],
    }
    
    for element_name, patterns in required_structure_elements.items():
        element_found = False
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                element_found = True
                break
        
        if not element_found:
            issues.append(f"Missing required structure element: {element_name}")
    
    # Check for section ordering (PR6 requires proper ordering)
    section_order = ['#', '##', '###']
    lines = content.split('\n')
    
    # Validate section hierarchy
    header_levels = []
    for line in lines:
        match = re.match(r'^(#+)\s+', line)
        if match:
            level = len(match.group(1))
            header_levels.append(level)
    
    # Check for invalid header level jumps (e.g., from # to ###)
    for i in range(1, len(header_levels)):
        if header_levels[i] - header_levels[i-1] > 1:
            issues.append(f"Invalid header level jump at line {i+1}")
    
    # Check for proper section ordering (no major violations)
    if header_levels and header_levels[0] != 1:
        issues.append("Plan must start with a main title (#)")
    
    # Check for PR rule references
    pr_references = re.findall(r'PR\d+', content)
    if not pr_references:
        issues.append("Missing PR rule references (PR1-PR16)")
    
    # Check for compliance lines
    compliance_lines = re.findall(r'✅.*PASS', content)
    if not compliance_lines:
        issues.append("Missing compliance indicators")
    
    if issues:
        print(f"Gate HG-14 FAIL: Plan structure validation failed")
        for issue in issues[:10]:
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   - ... and {len(issues) - 10} more issues")
        return False
    else:
        print(f"Gate HG-14 PASS: Plan structure follows PR6 requirements")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()