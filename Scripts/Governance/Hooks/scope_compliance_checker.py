#!/usr/bin/env python3
"""
Scope compliance checking hook for PreToolUse.
Validates scope compliance using deterministic rule checking instead of LLM analysis.
"""

import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result, show_hook_error, show_hook_error_details

def validate_scope_compliance(file_path):
    """Validate scope compliance using deterministic rule checking."""
    project_root = Path("C:/SovereignAI")
    
    # Define scope boundaries from configuration
    allowed_directories = {
        "Agents",
        "Rules",
        "Workflow", 
        "Scripts",
        "Logs",
        "Docs"
    }
    
    protected_directories = {
        "App"  # Application code - deferred to Phase 12
    }
    
    restricted_operations = {
        "production_deployment",
        "database_schema_modification",
        "user_interface_development"
    }
    
    file_path = Path(file_path)
    
    # Check if operation is in protected directory
    for protected_dir in protected_directories:
        if protected_dir in str(file_path):
            return False, f"Cannot modify files in {protected_dir}/ directory - deferred to Phase 12"
    
    # Check for restricted operations in file names
    for restricted_op in restricted_operations:
        if restricted_op.replace("_", " ").replace("-", " ") in file_path.name.lower():
            return False, f"File name suggests restricted operation: {restricted_op} - not allowed in current phase"
    
    # Check file content for restricted patterns
    try:
        with open(file_path) as f:
            content = f.read()
        
        # Check for restricted keywords in content
        restricted_keywords = [
            "production deployment",
            "database schema",
            "user interface",
            "UI development"
        ]
        
        for keyword in restricted_keywords:
            if keyword.lower() in content.lower():
                return False, f"File contains restricted operation: {keyword} - deferred to Phase 12"
    except:
        # If we can't read the file, allow it (might be a new file)
        pass
    
    return True, "Scope compliance verification passed"

def main():
    """Main scope compliance checking logic."""
    verbosity = get_verbosity()
    show_hook_header("Scope Compliance Checking", verbosity)
    
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
    
    # Validate scope compliance
    allowed, message = validate_scope_compliance(file_path)
    
    show_hook_result(f"Validation result: {message}", success=allowed, verbosity=verbosity)
    
    if not allowed:
        show_hook_error("Scope compliance check failed - operation blocked", verbosity)
        show_hook_error_details(f"Scope compliance check failed - operation blocked", verbosity)
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
    
    show_hook_result("Scope compliance verification passed", success=True, verbosity=verbosity)
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in scope compliance checking: {e}", file=sys.stderr)
        sys.exit(1)
