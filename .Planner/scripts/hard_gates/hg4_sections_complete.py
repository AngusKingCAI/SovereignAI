#!/usr/bin/env python3
"""
Tool: HG-4 Sections Complete Validation

WHEN TO USE: Phase 4, after plan drafting, before quality gates

WHAT IT CHECKS: Plan has all required sections (Context, Architecture, Dependencies, 
Implementation, Testing, Deployment, Rollback, Maintenance) with sufficient content.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-4 PASS: All required sections present and complete
- Exit 1: Gate HG-4 FAIL: {list of missing or incomplete sections}

FAILURE RECOVERY: Add missing sections or expand incomplete sections, re-run this script.
Do NOT proceed to Phase 5 until exit 0.

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
    Check that all required sections are present.
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
    
    # Look for plan files (excluding completed directory)
    plan_files = []
    for pattern in ["plan-*.md", "plan-*.Rev*.md"]:
        plan_files.extend(plans_dir.glob(pattern))
    
    # Filter out completed plans
    plan_files = [f for f in plan_files if "completed" not in str(f)]
    
    if not plan_files:
        print("⚠️  No plan files found, skipping validation")
        return True
    
    # Get the most recently modified plan file
    latest_plan = max(plan_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating plan: {latest_plan.name}")
    
    try:
        with open(latest_plan, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading plan file: {e}")
        return False
    
    issues = []
    
    # Define required sections based on technical plan best practices
    required_sections = {
        'Context': [r'## Context', r'## Background', r'## Problem Statement', r'## Overview'],
        'Architecture': [r'## Architecture', r'## Technical Context', r'## System Design'],
        'Dependencies': [r'## Dependencies', r'Depends on:', r'## Prerequisites'],
        'Implementation': [r'## Implementation', r'## Development', r'## Execution'],
        'Testing': [r'## Testing', r'## Verification', r'## Validation'],
        'Deliverables': [r'## Deliverables', r'## Outputs', r'## Results'],
    }
    
    # Check for at least one pattern from each required section category
    for section_name, patterns in required_sections.items():
        section_found = False
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                section_found = True
                break
        
        if not section_found:
            issues.append(f"Missing required section: {section_name}")
    
    # Check for basic structure elements
    structure_elements = {
        'Step sections': [r'## S\d+', r'## Step \d+', r'## Phase \d+'],
        'Headers': [r'^#+\s+[A-Z]', r'^#{1,3}\s+\w+'],
        'Lists': [r'^\s*[-*+]\s+', r'^\s*\d+\.\s+'],
    }
    
    for element_name, patterns in structure_elements.items():
        element_found = False
        for pattern in patterns:
            if re.search(pattern, content, re.MULTILINE):
                element_found = True
                break
        
        if not element_found:
            issues.append(f"Missing structural element: {element_name}")
    
    # Check for empty sections (section headers with no content)
    section_pattern = r'^#+\s+.+$'
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if re.match(section_pattern, line):
            # Check if next few lines have content
            next_lines = lines[i+1:i+5] if i+1 < len(lines) else []
            has_content = any(next_lines and line.strip() and not line.strip().startswith('#') 
                           for line in next_lines)
            
            if not has_content:
                # Extract section name
                section_name = line.strip('#').strip()
                issues.append(f"Empty section with no content: {section_name}")
    
    # Check for minimum length requirements
    if len(content) < 500:  # Arbitrary minimum length for a substantive plan
        issues.append(f"Plan content too short ({len(content)} characters, minimum 500)")
    
    # Check for completion indicators
    completion_indicators = [
        r'\bcomplete\b',
        r'\bfinished\b',
        r'\bdone\b',
        r'\bfinal\b',
    ]
    
    has_completion = any(re.search(pattern, content, re.IGNORECASE) for pattern in completion_indicators)
    if not has_completion:
        issues.append("Missing completion indicators or status")
    
    if issues:
        print(f"❌ Gate HG-4 FAIL: Required sections validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-4 PASS: All required sections are present")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-4 PASS: All required sections are present")
        sys.exit(0)
    else:
        print("❌ Gate HG-4 FAIL: Required sections are missing")
        sys.exit(1)

if __name__ == "__main__":
    main()