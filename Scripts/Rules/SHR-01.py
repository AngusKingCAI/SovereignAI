# Scripts/Rules/SHR-01.py
# id: SHR-01, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Safety commands rule implementation, agent: all, persona: governance
"""SHR-01: Safety commands - blocks dangerous shell commands."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Standardized rule evaluation function."""
    rule_id = rule["id"]
    
    # Check if tool is in target tools (if specified)
    target_tools = params.get("target_tools", [])
    if target_tools and tool_name not in target_tools:
        return {"decision": "allow", "rule_id": rule_id}
    
    # Get standardized message
    message = params.get("message", f"violation of rule {rule_id} requires explicit user confirmation")
    
    # Extract command field
    command = tool_input.get("command", "")
    
    # Normalize path separators in command
    normalized_command = command.replace("\\", "/")
    
    # Check scope directories (if specified)
    scope_dirs = params.get("scope_dirs", [])
    if scope_dirs:
        in_scope = any(scope_dir.lower() in normalized_command.lower() for scope_dir in scope_dirs)
        if in_scope:
            return {"decision": "allow", "rule_id": rule_id}
    
    # Check patterns with reasons (if specified)
    patterns = params.get("patterns", [])
    for pattern_config in patterns:
        pattern = pattern_config.get("regex", "")
        reason = pattern_config.get("reason", message)
        if re.search(pattern, command):
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: {reason}",
                "rule_id": rule_id
            }
    
    return {"decision": "allow", "rule_id": rule_id}