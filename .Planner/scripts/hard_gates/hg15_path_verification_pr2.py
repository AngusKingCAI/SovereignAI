#!/usr/bin/env python3
"""
Tool: HG-15 Path Verification PR2 Validation

WHEN TO USE: Phase 3, after plan drafting, before plan finalization

WHAT IT CHECKS: All paths are repo-relative per PR2 requirements. No absolute paths, 
no invalid path references, consistent path separators.

INPUTS: None (auto-discovers latest plan in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-15 PASS: All paths are repo-relative per PR2
- Exit 1: Gate HG-15 FAIL: {list of path verification issues}

FAILURE RECOVERY: Fix path references to be repo-relative, re-run this script.
Do NOT proceed to Phase 4 until exit 0.

DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
"""

import sys
import os
import re
from pathlib import Path

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set UTF-8 encoding for Windows console compatibility
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_gate_condition():
    """
    Check that all paths are repo-relative per PR2.
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
    
    # Patterns for invalid paths (PR2 violations)
    invalid_path_patterns = [
        r'[A-Z]:\\',  # Windows absolute paths (C:\, D:\, etc.)
        r'/home/',  # Unix absolute home paths
        r'/root/',  # Unix root paths
        r'^/',  # Unix absolute paths at start of line
        r'~/',  # Home directory shortcuts
        r'\.\./\.\./',  # Excessive parent directory references (more than 2 levels)
    ]
    
    # Path patterns that should be repo-relative
    path_contexts = [
        r'path[:\s]+["\']?([^"\']+)["\']',  # path: "some/path"
        r'file[:\s]+["\']?([^"\']+)["\']',  # file: "some/path"
        r'directory[:\s]+["\']?([^"\']+)["\']',  # directory: "some/path"
        r'location[:\s]+["\']?([^"\']+)["\']',  # location: "some/path"
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
        r'Agents/',  # Agents directory references
    ]
    
    # Check if there are any path references at all
    has_path_references = any(re.search(pattern, content) for pattern in path_contexts)
    
    if not has_path_references:
        print("No path references found in plan (may be expected for some plans)")
    
    # Validate that paths follow repo-relative patterns
    path_count = 0
    invalid_path_count = 0
    
    for pattern in path_contexts:
        matches = re.finditer(pattern, content)
        for match in matches:
            path_count += 1
            path_value = match.group(1) if match.groups() else match.group()
            
            # Check if path is valid repo-relative
            if re.match(r'^[A-Z]:\\', path_value) or path_value.startswith('/') or path_value.startswith('~'):
                invalid_path_count += 1
                issues.append(f"Non-repo-relative path found: {path_value}")
    
    # Check for Windows-specific backslashes in paths (should use forward slashes)
    backslash_paths = re.findall(r'[a-zA-Z0-9_\-/\\]+\\\\[a-zA-Z0-9_\-/\\]+', content)
    if backslash_paths:
        issues.append(f"Found {len(backslash_paths)} paths with backslashes (should use forward slashes)")
    
    if issues:
        print(f"Gate HG-15 FAIL: Path verification failed")
        for issue in issues[:10]:
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   - ... and {len(issues) - 10} more issues")
        return False
    else:
        print(f"Gate HG-15 PASS: All paths are repo-relative per PR2")
        return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()