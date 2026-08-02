# Scripts/Rules/SHR-03.py
# id: SHR-03, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Frontmatter requirements rule implementation, agent: all, persona: governance
"""SHR-03: Frontmatter requirements - ensures governance .md files have proper YAML frontmatter."""
import re
import yaml

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
    content = tool_input.get("content", "")
    
    # Normalize path separators
    normalized_path = file_path.replace("\\", "/")
    
    # Check file glob pattern (if specified)
    file_glob = params.get("file_glob", "")
    if file_glob:
        glob_pattern = file_glob.replace("**", ".*").replace("*", "[^/]*").replace("?", ".") + "$"
        if not re.search(glob_pattern, normalized_path):
            return {"decision": "allow", "rule_id": rule_id}
    
    # Check scope directories (if specified)
    scope_dirs = params.get("scope_dirs", [])
    if scope_dirs:
        in_scope = any(scope_dir.lower() in normalized_path.lower() for scope_dir in scope_dirs)
        if not in_scope:
            return {"decision": "allow", "rule_id": rule_id}
    
    # Check frontmatter (if specified)
    check_frontmatter = params.get("check_frontmatter", False)
    if check_frontmatter:
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 2:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    
                    # Check for required fields
                    required_fields = params.get("required_fields", [])
                    for field in required_fields:
                        if field not in frontmatter:
                            return {
                                "decision": "deny",
                                "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                                "rule_id": rule_id
                            }
                    
                    # Check field values if specified
                    field_values = params.get("field_values", {})
                    for field, expected_value in field_values.items():
                        if frontmatter.get(field) != expected_value:
                            return {
                                "decision": "deny",
                                "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                                "rule_id": rule_id
                            }
                except Exception:
                    return {
                        "decision": "deny",
                        "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                        "rule_id": rule_id
                    }
        else:
            return {
                "decision": "deny",
                "reason": f"⛔ BLOCKED by rule {rule_id}: {message}",
                "rule_id": rule_id
            }
    
    return {"decision": "allow", "rule_id": rule_id}