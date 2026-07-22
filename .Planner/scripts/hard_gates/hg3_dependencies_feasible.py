#!/usr/bin/env python3
"""
Hard Gate HG-3: Dependencies Feasible Validation

Validates that dependencies are technically feasible.
Blocks plan creation if dependencies are infeasible.

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
    Check that dependencies are technically feasible.
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
    
    # Check for dependencies section
    if "Depends on:" not in content and "depends on" not in content.lower() and "dependencies" not in content.lower():
        issues.append("Missing dependencies section or dependencies information")
    
    # Check for circular dependency indicators
    circular_patterns = [
        r'\bcircular\s+dependency\b',
        r'\bcycle\s+detected\b',
        r'\bmutual\s+dependency\b',
        r'\bA\s+depends\s+on\s+B.*B\s+depends\s+on\s+A\b',
    ]
    
    for pattern in circular_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found circular dependency indicator: {pattern}")
    
    # Check for impossible technical requirements
    impossible_patterns = [
        r'\binfinite\s+(loop|process|time)\b',
        r'\bimpossible\s+to\s+(implement|achieve|complete)\b',
        r'\btechnically\s+impossible\b',
        r'\bviolates\s+physics\b',
        r'\bbreaks\s+fundamental\s+laws\b',
    ]
    
    for pattern in impossible_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found impossible technical requirement: {pattern}")
    
    # Check for TBD/TODO in dependencies (indicates incomplete planning)
    dependency_section = re.search(r'(?:Depends on|dependencies|Dependencies)[\s\S]*?(?=##|\Z)', content, re.IGNORECASE)
    if dependency_section:
        dep_text = dependency_section.group(0)
        todo_patterns = [
            r'\bTBD\b',
            r'\bTBA\b',
            r'\bTBC\b',
            r'\bTODO\b(?!\s*:)',
            r'\bto be determined\b',
            r'\bto be announced\b',
        ]
        
        for pattern in todo_patterns:
            if re.search(pattern, dep_text, re.IGNORECASE):
                issues.append(f"Found incomplete dependency planning: {pattern}")
    
    # Check for version conflicts or incompatible requirements
    conflict_patterns = [
        r'\bversion\s+conflict\b',
        r'\bincompatible\s+version\b',
        r'\bmutually\s+exclusive\b',
        r'\bconflicting\s+requirements\b',
    ]
    
    for pattern in conflict_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Found dependency conflict: {pattern}")
    
    if issues:
        print(f"❌ Gate HG-3 FAIL: Dependencies validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-3 PASS: Dependencies are technically feasible")
        return True

def main():
    if check_gate_condition():
        print("✅ Gate HG-3 PASS: Dependencies are technically feasible")
        sys.exit(0)
    else:
        print("❌ Gate HG-3 FAIL: Dependencies are infeasible")
        sys.exit(1)

if __name__ == "__main__":
    main()