# Scripts/Rules/Checks/Types/yaml_field.py
# id: yaml_field, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: YAML field check type implementation, agent: all, persona: governance
"""YAML field check type - validates YAML frontmatter."""
import re
import yaml

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Check YAML frontmatter for required fields or field values."""
    if tool_name not in ("write", "edit"):
        return {"decision": "allow", "rule_id": rule["id"]}
    
    content = tool_input.get("content", "")
    file_path = tool_input.get("file_path", "")
    
    # Check if file matches the glob pattern
    file_glob = params.get("file_glob", "")
    if file_glob:
        # Normalize path separators to forward slashes for pattern matching
        normalized_path = file_path.replace("\\", "/")
        # Convert glob to regex pattern
        # Handle ** (match any number of directories including none)
        glob_pattern = file_glob.replace("**", ".*")
        # Handle * (match any characters except /)
        glob_pattern = glob_pattern.replace("*", "[^/]*")
        # Handle ? (match any single character)
        glob_pattern = glob_pattern.replace("?", ".")
        # Anchor to match the filename at the end
        glob_pattern = glob_pattern + "$"
        if not re.search(glob_pattern, normalized_path):
            return {"decision": "allow", "rule_id": rule["id"]}
    
    # Check if file is in scope directories (case-insensitive)
    scope_dirs = params.get("scope_dirs", [])
    in_scope = any(scope_dir.lower() in file_path.lower() for scope_dir in scope_dirs)
    
    # If not in scope, allow (rule doesn't apply)
    if not in_scope:
        return {"decision": "allow", "rule_id": rule["id"]}
    
    # Extract YAML frontmatter (between --- markers)
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            try:
                frontmatter = yaml.safe_load(parts[1])
                if frontmatter is None:
                    frontmatter = {}
                
                # Check for required fields
                required_fields = params.get("required_fields", [])
                for field in required_fields:
                    if field not in frontmatter:
                        return {
                            "decision": "deny",
                            "reason": f"BLOCKED by rule {rule['id']}: missing required YAML field '{field}' requires explicit user confirmation",
                            "rule_id": rule["id"]
                        }
                
                # Check field values if specified
                field_values = params.get("field_values", {})
                for field, expected_value in field_values.items():
                    if frontmatter.get(field) != expected_value:
                        return {
                            "decision": "deny",
                            "reason": f"BLOCKED by rule {rule['id']}: YAML field '{field}' has incorrect value requires explicit user confirmation",
                            "rule_id": rule["id"]
                        }
            except Exception:
                # If YAML parsing fails, deny for safety
                return {
                    "decision": "deny",
                    "reason": f"BLOCKED by rule {rule['id']}: invalid YAML frontmatter requires explicit user confirmation",
                    "rule_id": rule["id"]
                }
    else:
        # File is in scope but has no frontmatter - deny
        return {
            "decision": "deny",
            "reason": f"BLOCKED by rule {rule['id']}: missing required YAML frontmatter requires explicit user confirmation",
            "rule_id": rule["id"]
        }
    
    return {"decision": "allow", "rule_id": rule["id"]}