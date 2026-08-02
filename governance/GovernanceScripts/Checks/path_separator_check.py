# Governance/GovernanceScripts/Checks/path_separator_check.py
# Frontmatter: id: path_separator_check, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Custom check function for path separator validation, agent: all, persona: governance
"""Custom check function for path separator validation."""
import re

def path_separator_check(tool_call: dict, params: dict) -> dict:
    """Check for backslash characters in file content or paths."""
    tool_name = tool_call.get("tool", "")
    tool_input = tool_call.get("input", {})
    
    # Check file content for backslashes
    content = tool_input.get("content", "")
    file_path = tool_input.get("file_path", "")
    
    # Combine both content and file path for checking
    text_to_check = content + file_path
    
    # Check for backslash characters
    if re.search(r'\\', text_to_check):
        return {
            "deny": True,
            "reason": "BLOCKED by rule SHR-02: backslash path separators require explicit user confirmation"
        }
    
    return {"deny": False}
