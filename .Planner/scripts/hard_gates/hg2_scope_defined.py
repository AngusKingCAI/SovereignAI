#!/usr/bin/env python3
"""
Hard Gate HG-2: Scope Defined Validation

Validates that scope boundaries are clearly defined with explicit boundaries.
Blocks plan creation if scope boundaries are undefined.

Returns exit code 0 (pass) or 1 (fail)
"""

import sys
import os
import re
from pathlib import Path

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gate_condition():
    """
    Check that scope boundaries are clearly defined.
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
    
    # Check for scope indicators
    scope_indicators = [
        r'\bin scope\b',
        r'\bout of scope\b',
        r'\bscope\b.*\bboundar',
        r'\bwhat this plan does\b',
        r'\bwhat this plan does not do\b',
        r'\blocked scope\b',
        r'\bscope adjudication\b'
    ]
    
    scope_found = False
    for pattern in scope_indicators:
        if re.search(pattern, content, re.IGNORECASE):
            scope_found = True
            break
    
    if not scope_found:
        issues.append("No clear scope boundaries defined")
    
    # Check for in-scope/out-of-scope delineation
    if not re.search(r'\bin[- ]scope\b', content, re.IGNORECASE):
        issues.append("Missing in-scope delineation")
    
    if not re.search(r'\bout[- ]scope\b', content, re.IGNORECASE):
        issues.append("Missing out-of-scope delineation")
    
    # Check for what's NOT included (good scope practice)
    if not re.search(r'\bwhat this plan does not\b', content, re.IGNORECASE):
        issues.append("Missing statement of what plan does not do")
    
    # Check for open questions section (indicates scope boundaries)
    if not re.search(r'\bopen questions?\b', content, re.IGNORECASE):
        issues.append("Missing open questions section (helps define scope)")
    
    if issues:
        print(f"❌ Gate HG-2 FAIL: Scope boundaries validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-2 PASS: Scope boundaries are clearly defined")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()