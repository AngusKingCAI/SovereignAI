# Scripts/Rules/Templates/RULE_TEMPLATE.py
# Standard rule implementation template
# Copy this file and rename it to RULE-XX.py
# id: RULE-ID, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Standardized rule template, agent: all, persona: governance
"""RULE-ID: Standardized rule template."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Standardized rule evaluation function.
    
    REQUIRED STRUCTURE:
    1. Always check target_tools first
    2. Always extract standardized message
    3. Only implement the checks your rule needs (based on YAML params)
    4. Always return {"decision": "allow|deny", "rule_id": str, "reason": str}
    
    Args:
        rule: Rule metadata dictionary
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool
        params: Rule-specific parameters from check.params
    
    Returns:
        dict: {decision: allow|deny, rule_id: str, reason: str}
    """
    rule_id = rule["id"]
    
    # REQUIRED: Check if tool is in target tools
    target_tools = params.get("target_tools", [])
    if target_tools and tool_name not in target_tools:
        return {"decision": "allow", "rule_id": rule_id}
    
    # REQUIRED: Get standardized message
    message = params.get("message", f"violation of rule {rule_id} requires explicit user confirmation")
    
    # OPTIONAL: Extract common fields based on your rule's needs
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content", "")
    command = tool_input.get("command", "")
    
    # OPTIONAL: Implement only the checks your rule needs
    # Include only the sections that match your YAML params
    
    # Check patterns (for command-based rules like SHR-01)
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
    
    # Check forbidden patterns (for path-based rules like SHR-04)
    forbidden = params.get("forbidden", [])
    if forbidden:
        normalized_path = file_path.replace("\\", "/")
        for pattern in forbidden:
            if re.search(pattern, normalized_path):
                return {
                    "decision": "deny",
                    "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                    "rule_id": rule_id
                }
    
    # Check encoding (for encoding rules like SHR-02)
    check_encoding = params.get("check_encoding", False)
    if check_encoding:
        # Implement encoding checks here
        pass
    
    # Check frontmatter (for frontmatter rules like SHR-03)
    check_frontmatter = params.get("check_frontmatter", False)
    if check_frontmatter:
        # Implement frontmatter checks here
        pass
    
    return {"decision": "allow", "rule_id": rule_id}
