#!/usr/bin/env python3
"""
Executor manifest validation hook for PreToolUse.
Validates executor manifest sections using deterministic parsing.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_executor_manifest(file_path):
    """Validate executor manifest sections using deterministic parsing."""
    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        return False, f"Could not read plan file: {e}"
    
    # Look for manifest sections
    manifest_patterns = [
        r'## Executor Manifest',
        r'## Manifest',
        r'### Manifest'
    ]
    
    manifest_found = False
    for pattern in manifest_patterns:
        if re.search(pattern, content):
            manifest_found = True
            break
    
    if not manifest_found:
        return True, "No manifest section found - validation not required"
    
    # Extract manifest content
    manifest_content = ""
    for pattern in manifest_patterns:
        match = re.search(pattern, content)
        if match:
            start_pos = match.start()
            # Find the next section header
            next_section = re.search(r'\n## ', content[start_pos + 2:])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = len(content)
            manifest_content = content[start_pos:end_pos]
            break
    
    if not manifest_content:
        return True, "Manifest section is empty - validation passed"
    
    # Check for required manifest subsections
    required_manifest_fields = [
        "required_tools",
        "dependencies",
        "permissions",
        "constraints"
    ]
    
    missing_fields = []
    for field in required_manifest_fields:
        if field.lower() not in manifest_content.lower():
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Manifest missing required fields: {missing_fields}"
    
    # Check for proper markdown formatting in manifest
    if not re.search(r'### \w+', manifest_content):
        return False, "Manifest should use proper markdown subsection formatting"
    
    return True, "Executor manifest validation passed"

def main():
    """Main executor manifest validation logic."""
    verbosity = get_verbosity()
    show_hook_header("Executor Manifest Validation", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except:
        env_vars = {}
    
    # Extract file path from tool input
    tool_input = env_vars.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    
    if not file_path:
        show_hook_result("No file path provided, allowing operation", success=True, verbosity=verbosity)
        return 0
    
    # Check if this is a plan file (manifests are typically in plans)
    file_path = Path(file_path)
    if 'Plan' not in file_path.name and 'plan' not in file_path.name.lower():
        show_hook_result(f"File {file_path.name} is not a plan file, skipping manifest validation", success=True, verbosity=verbosity)
        return 0
    
    # Validate executor manifest
    allowed, message = validate_executor_manifest(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Executor manifest validation failed - operation blocked", verbosity)
        show_hook_error_details(f"Executor manifest validation failed - operation blocked", verbosity)
        # Return permission decision to block
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": message
            }
        }
        print(json.dumps(output, indent=2))
        return 2  # Block the operation
    
    show_hook_result("Executor manifest validation passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in executor manifest validation: {e}", file=sys.stderr)
        sys.exit(1)
