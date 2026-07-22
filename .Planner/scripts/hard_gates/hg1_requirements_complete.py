#!/usr/bin/env python3
"""
Hard Gate HG-1: Requirements Complete Validation

Validates that requirements are complete and unambiguous.
Blocks plan creation if requirements are incomplete or ambiguous.

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
    Check that requirements are complete and unambiguous.
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
    
    # Check for key requirement indicators
    issues = []
    
    # Check for dependencies section
    if "Depends on:" not in content and "depends on" not in content.lower():
        issues.append("Missing dependencies information")
    
    # Check for vision principles
    if "Vision principles:" not in content and "vision principles" not in content.lower():
        issues.append("Missing vision principles")
    
    # Check for architectural context or context section
    if "Architectural Context" not in content and "Context" not in content:
        issues.append("Missing architectural context or context section")
    
    # Check for vague terms
    vague_patterns = [
        r'\bTBD\b',
        r'\bto be determined\b',
        r'\bTBA\b',
        r'\bto be announced\b',
        r'\bTBC\b',
        r'\bto be confirmed\b',
        r'\bTODO\b(?!\s*:)',  # Allow TODO: but not standalone TODO
        r'\bfuture work\b',
        r'\blater\b(?!\s*phase)',  # Allow "later phase" but not standalone "later"
    ]
    
    for pattern in vague_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found vague term: {pattern}")
    
    # Check for specific step sections (S1, S2, etc.)
    if not re.search(r'## S\d+\s*—', content):
        issues.append("Missing specific step sections (S1, S2, etc.)")
    
    # Check for compliance lines
    if not re.search(r'✅', content):
        issues.append("Missing compliance indicators")
    
    if issues:
        print(f"❌ Gate HG-1 FAIL: Requirements validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-1 PASS: Requirements are complete and unambiguous")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()