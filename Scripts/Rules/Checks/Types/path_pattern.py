# Scripts/Rules/Checks/Types/path_pattern.py
# id: path_pattern, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Path pattern check type implementation, agent: all, persona: governance
"""Path pattern check type - blocks/allows file paths based on patterns."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Check if file path matches forbidden pattern."""
    file_path = tool_input.get("file_path", "")
    # Normalize path separators to forward slashes for pattern matching
    normalized_path = file_path.replace("\\", "/")
    
    for pattern in params.get("forbidden", []):
        if re.search(pattern, normalized_path):
            return {
                "decision": "deny",
                "reason": f"BLOCKED by rule {rule['id']}: file placement violation requires explicit user confirmation",
                "rule_id": rule["id"]
            }
    return {"decision": "allow", "rule_id": rule["id"]}