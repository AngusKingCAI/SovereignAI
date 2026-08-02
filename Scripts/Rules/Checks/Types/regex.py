# Scripts/Rules/Checks/Types/regex.py
# id: regex, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Regex check type implementation, agent: all, persona: governance
"""Regex check type - generic regex matching."""
import re

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Generic regex match against tool input."""
    scope = params.get("scope", "all")
    if scope == "file_content":
        input_string = tool_input.get("content", "") or tool_input.get("file_path", "") or str(tool_input)
    else:
        input_string = tool_input.get("command", "") or tool_input.get("content", "") or str(tool_input)
    pattern = params.get("pattern", "")
    if re.search(pattern, input_string):
        return {
            "decision": "deny",
            "reason": f"BLOCKED by rule {rule['id']}: prohibited pattern match requires explicit user confirmation",
            "rule_id": rule["id"]
        }
    return {"decision": "allow", "rule_id": rule["id"]}