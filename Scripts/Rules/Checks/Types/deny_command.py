# Scripts/Rules/Checks/Types/deny_command.py
# id: deny_command, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Deny command check type implementation, agent: all, persona: governance
"""Deny command check type - blocks dangerous shell commands."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Check if the command matches any deny pattern."""
    command = tool_input.get("command", "")
    
    # Check if command is in scope-based exemption directories
    scope_dirs = params.get("scope_dirs", [])
    if scope_dirs:
        # Normalize path separators in the full command
        normalized_command = command.replace("\\", "/")
        # Check if any scope directory is in the command
        if any(scope_dir.lower() in normalized_command.lower() for scope_dir in scope_dirs):
            return {"decision": "allow", "rule_id": rule["id"]}
    
    for pattern in params.get("patterns", []):
        if re.search(pattern["regex"], command):
            return {
                "decision": "deny",
                "reason": pattern.get("reason", f"Blocked by rule {rule['id']}"),
                "rule_id": rule["id"]
            }
    return {"decision": "allow", "rule_id": rule["id"]}