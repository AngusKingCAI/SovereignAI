#!/usr/bin/env python3
"""
Hard Gate HG-8: Paths Valid Validation

Validates that all paths are repo-relative and valid.
Blocks plan delivery if paths are invalid or non-repo-relative.

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
    Check that all paths are repo-relative and valid.
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
    
    # Patterns for invalid paths
    invalid_path_patterns = [
        r'[A-Z]:\\',  # Windows absolute paths (C:\, D:\, etc.)
        r'/home/',  # Unix absolute home paths
        r'/root/',  # Unix root paths
        r'^/',  # Unix absolute paths at start of line
        r'~/',  # Home directory shortcuts
        r'\.\./',  # Parent directory references (allow in some contexts)
    ]
    
    # Path patterns that should be repo-relative
    path_contexts = [
        r'path[:\s]+["\']?([^"\']+)["\']?',  # path: "some/path"
        r'file[:\s]+["\']?([^"\']+)["\']?',  # file: "some/path"
        r'directory[:\s]+["\']?([^"\']+)["\']?',  # directory: "some/path"
        r'location[:\s]+["\']?([^"\']+)["\']?',  # location: "some/path"
        r'["\']([a-zA-Z0-9_\-./\\]+)["\']',  # paths in quotes
    ]
    
    # Check for invalid paths
    for pattern in invalid_path_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            issues.append(f"Found invalid path pattern: {match.group()} at position {match.start()}")
    
    # Check for absolute paths in common contexts
    absolute_path_patterns = [
        r'(?:path|file|directory|location)\s*[:=]\s*["\']?(?:[A-Z]:\\|/|~)',  # Windows/Unix absolute paths
        r'(?:cd|chdir)\s+["\']?(?:[A-Z]:\\|/|~)',  # cd commands with absolute paths
    ]
    
    for pattern in absolute_path_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            issues.append(f"Found absolute path: {match.group()} at position {match.start()}")
    
    # Check for proper repo-relative path patterns
    valid_relative_patterns = [
        r'\.\./',  # Allowed parent directory references
        r'\./',  # Current directory references
        r'[a-zA-Z0-9_\-]+/',  # Relative directory references
        r'sovereignai/',  # Project root references
        r'\.Planner/',  # Planner directory references
        r'\.Executor/',  # Executor directory references
    ]
    
    # Check if there are any path references at all
    has_path_references = any(re.search(pattern, content) for pattern in path_contexts)
    
    if not has_path_references:
        print("⚠️  No path references found in plan (may be expected for some plans)")
    
    if issues:
        print(f"❌ Gate HG-8 FAIL: Path validation failed")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ Gate HG-8 PASS: All paths are repo-relative and valid")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()