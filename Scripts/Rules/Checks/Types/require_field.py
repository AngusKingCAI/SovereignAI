# Scripts/Rules/Checks/Types/require_field.py
# id: require_field, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Require field check type implementation, agent: all, persona: governance
"""Require field check type - checks for required fields in content."""

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Check if a required YAML field is present (for write operations)."""
    if tool_name in ("write", "edit"):
        content = tool_input.get("content", "")
        required_fields = params.get("fields", [])
        for field in required_fields:
            if f"{field}:" not in content[:500]:  # check frontmatter only
                return {
                    "decision": "deny",
                    "reason": f"BLOCKED by rule {rule['id']}: missing required frontmatter field '{field}' requires explicit user confirmation",
                    "rule_id": rule["id"]
                }
    return {"decision": "allow", "rule_id": rule["id"]}