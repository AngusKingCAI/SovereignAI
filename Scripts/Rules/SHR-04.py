# Scripts/Rules/SHR-04.py
# id: SHR-04, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: File placement rule implementation, agent: all, persona: governance
"""SHR-04: File placement - ensures governance files are placed in correct locations."""
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
    
    # Extract common fields
    file_path = tool_input.get("file_path", "")
    
    # Normalize path separators
    normalized_path = file_path.replace("\\", "/")
    
    # Check forbidden patterns (if specified)
    forbidden = params.get("forbidden", [])
    for pattern in forbidden:
        if re.search(pattern, normalized_path):
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                "rule_id": rule_id
            }
    
    return {"decision": "allow", "rule_id": rule_id}