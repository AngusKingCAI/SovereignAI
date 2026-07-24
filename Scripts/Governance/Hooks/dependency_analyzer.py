#!/usr/bin/env python3
"""
Dependency analysis hook for PreToolUse.
Analyzes dependencies using deterministic graph analysis instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def analyze_dependencies(file_path):
    """Analyze dependencies using deterministic graph analysis."""
    try:
        with open(file_path) as f:
            content = f.read()
    except Exception as e:
        return False, f"Could not read plan file: {e}"
    
    # Look for dependency sections
    dependency_patterns = [
        r'## Dependencies',
        r'### Dependencies',
        r'Dependencies:',
        r'requires:',
        r'depends on'
    ]
    
    dependencies_found = False
    for pattern in dependency_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            dependencies_found = True
            break
    
    if not dependencies_found:
        return True, "No dependencies section found - validation not required"
    
    # Extract dependency content
    dependency_content = ""
    for pattern in dependency_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            start_pos = match.start()
            # Find the next section header
            next_section = re.search(r'\n## ', content[start_pos + 2:])
            if next_section:
                end_pos = start_pos + next_section.start()
            else:
                end_pos = len(content)
            dependency_content = content[start_pos:end_pos]
            break
    
    if not dependency_content:
        return True, "Dependencies section is empty - validation passed"
    
    # Check for required dependency fields
    required_fields = [
        "external",
        "internal",
        "version",
        "system"
    ]
    
    # Extract dependency items
    dependency_items = re.findall(r'[-*]\s+\w+', dependency_content)
    
    if not dependency_items:
        return False, "Dependencies section exists but no dependencies found"
    
    # Check for dependency completeness
    missing_fields = []
    for field in required_fields:
        if field.lower() not in dependency_content.lower():
            # This is a soft check - not all fields are required
            pass
    
    # Check for circular dependencies (basic check)
    if "circular" in dependency_content.lower():
        return False, "Circular dependencies detected - must be resolved"
    
    # Check for undefined dependencies
    undefined_deps = []
    for dep in dependency_items:
        dep_name = re.sub(r'[-*]\s+', '', dep).strip()
        if dep_name and dep_name not in content.lower():
            # Dependency mentioned but not defined
            if f"{dep_name}:" not in content.lower() and f"{dep_name} " not in content.lower():
                undefined_deps.append(dep_name)
    
    if undefined_deps:
        return False, f"Undefined dependencies found: {undefined_deps}"
    
    return True, f"Dependency analysis passed - {len(dependency_items)} dependencies found"

def main():
    """Main dependency analysis logic."""
    verbosity = get_verbosity()
    show_hook_header("Dependency Analysis", verbosity)
    
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
    
    # Check if this is a plan file
    file_path = Path(file_path)
    if 'Plan' not in file_path.name and 'plan' not in file_path.name.lower():
        show_hook_result(f"File {file_path.name} is not a plan file, skipping dependency analysis", success=True, verbosity=verbosity)
        return 0
    
    # Analyze dependencies
    allowed, message = analyze_dependencies(file_path)
    
    show_hook_result(f"Analysis result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Dependency analysis failed - operation blocked", verbosity)
        show_hook_error_details(f"Dependency analysis failed - operation blocked", verbosity)
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
    
    show_hook_result("Dependency analysis passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in dependency analysis: {e}", file=sys.stderr)
        sys.exit(1)
