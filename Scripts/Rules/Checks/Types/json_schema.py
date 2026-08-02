# Scripts/Rules/Checks/Types/json_schema.py
# id: json_schema, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: JSON Schema check type implementation, agent: all, persona: governance
"""JSON Schema check type - validates against JSON Schema."""

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Validate tool input against a JSON Schema."""
    # This check type requires jsonschema to be installed
    try:
        import jsonschema
    except ImportError:
        return {
            "decision": "deny",
            "reason": f"BLOCKED by rule {rule['id']}: jsonschema library not installed",
            "rule_id": rule["id"]
        }
    
    schema = params.get("schema", {})
    try:
        jsonschema.validate(tool_input, schema)
        return {"decision": "allow", "rule_id": rule["id"]}
    except jsonschema.ValidationError as e:
        return {
            "decision": "deny",
            "reason": f"BLOCKED by rule {rule['id']}: JSON Schema validation failed requires explicit user confirmation",
            "rule_id": rule["id"]
        }