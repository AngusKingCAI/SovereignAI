#!/usr/bin/env python3
"""
PreToolUse Hook: Plan Write Validation

Runs before any write/edit operation to plan files.
Validates against hard gates to prevent invalid plan modifications.
If gates fail, blocks the write operation (exit code 2).
"""

import sys
import json
import os
import re
from pathlib import Path

def main():
    # Read hook input from stdin
    try:
        hook_input = json.loads(sys.stdin.read())
    except:
        # If no input, allow operation
        sys.exit(0)
    
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    
    # Only validate write/edit operations
    if tool_name not in ["write", "edit"]:
        sys.exit(0)
    
    # Check if operation is on plan files
    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)
    
    # Convert to Path and check if it's a plan file
    path_obj = Path(file_path)
    
    # Check if file is in plans directory or has plan-like name
    is_plan_file = (
        "plans" in path_obj.parts or 
        "plan" in path_obj.name.lower() or
        path_obj.name.startswith("plan-")
    )
    
    if not is_plan_file:
        sys.exit(0)
    
    print(f"PreToolUse Hook: Validating plan file write: {path_obj.name}")
    
    # Validate against relevant hard gates for plan files
    # HG-7: Compliance lines present
    # HG-8: Paths valid
    # HG-9: Manifest complete
    # HG-14: Plan structure
    # HG-15: Path requirements (repo-relative)
    # HG-18: Spec approval
    
    # For now, we'll do basic validation
    # In production, this would call the actual hard gate scripts
    
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading plan file: {e}")
        sys.exit(2)  # Block operation if file cannot be read
    
    # Basic validation checks
    validation_passed = True
    validation_errors = []
    
    # Check for compliance lines (HG-7)
    has_compliance_lines = "Gate PASS" in content or "Gate PLAN-" in content
    if not has_compliance_lines and len(content) > 100:  # Only check if file has content
        validation_errors.append("HG-7: Missing compliance lines")
        validation_passed = False
    
    # Check for path validation (HG-8, HG-15) - basic check
    # Note: We check for problematic absolute path patterns
    absolute_path_patterns = [
        r'/[a-zA-Z]/',  # Unix absolute paths
        r'[A-Z]:\\',     # Windows absolute paths
    ]
    
    for pattern in absolute_path_patterns:
        matches = re.findall(pattern, content)
        if matches:
            validation_errors.append(f"HG-8/HG-15: Found absolute path(s): {matches[:3]}")
            validation_passed = False
    
    # Check for manifest completeness (HG-9)
    manifest_pattern = r"## Executor Manifest"
    if not re.search(manifest_pattern, content, re.IGNORECASE):
        validation_errors.append("HG-9: Missing Executor Manifest section")
        validation_passed = False
    else:
        # Check for basic manifest components
        manifest_section = re.search(r"## Executor Manifest.*?(?=##|$)", content, re.DOTALL | re.IGNORECASE)
        if manifest_section:
            manifest_content = manifest_section.group(0)
            required_manifest_items = ["phases", "deliverables", "gates"]
            for item in required_manifest_items:
                if item.lower() not in manifest_content.lower():
                    validation_errors.append(f"HG-9: Missing manifest component: {item}")
                    validation_passed = False
    
    # Check for plan structure (HG-14)
    required_sections = [
        r"# Plan: .+",
        r"## Vision Principles",
        r"## PR Rules Reference",
        r"## Executor Manifest",
    ]
    
    for section in required_sections:
        if not re.search(section, content, re.MULTILINE):
            validation_errors.append(f"HG-14: Missing required section: {section}")
            validation_passed = False
    
    # Check for spec approval (HG-18)
    spec_approval_pattern = r"Gate PLAN-2\.5 PASS.*spec approved"
    if not re.search(spec_approval_pattern, content, re.IGNORECASE):
        validation_errors.append("HG-18: Missing spec approval compliance line (Phase 2.5)")
        validation_passed = False
    
    if validation_passed:
        print(f"PreToolUse Hook: Plan file validation passed")
        sys.exit(0)  # Allow operation
    else:
        print(f"PreToolUse Hook: Plan file validation failed")
        for error in validation_errors:
            print(f"   - {error}")
        print(f"Blocking write operation to prevent invalid plan modification")
        sys.exit(2)  # Block operation

if __name__ == "__main__":
    main()