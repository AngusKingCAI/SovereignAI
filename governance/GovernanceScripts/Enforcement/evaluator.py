# Governance/GovernanceScripts/Enforcement/evaluator.py
# Frontmatter: id: evaluator, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Rule evaluator module, agent: all, persona: governance
#!/usr/bin/env python3
"""
Rule evaluator module — provides the core evaluation logic used by
the PDP hook, test runner, and drift detection.
"""
import re
import yaml
import jsonschema

# Registry of check type evaluators - these are the implemented check types
EVALUATORS = {
    "deny_command": "evaluate_rule",
    "path_pattern": "evaluate_rule",
    "require_field": "evaluate_rule",
    "regex": "evaluate_rule",
    "yaml_field": "evaluate_rule",
    "json_schema": "evaluate_rule",
    "custom_function": "evaluate_rule",
}

def evaluate_rule(rule: dict, tool_call: dict) -> dict:
    """Evaluate a single Policy Card against a tool call.
    Returns: {decision: allow|deny, reason: str, rule_id: str}
    
    This function is imported by:
    - Governance/GovernanceScripts/Enforcement/pre_tool_pdp.py (runtime enforcement)
    - Governance/GovernanceScripts/Validation/run_rule_tests.py (test runner)
    - Governance/Audit/drift_detection.py (drift detection)
    """
    check = rule.get("check", {})
    check_type = check.get("type")
    params = check.get("params", {})
    
    # Extract the relevant input from the tool call
    # Devin CLI's tool call structure uses "tool" and "input" keys
    tool_name = tool_call.get("tool", tool_call.get("tool_name", ""))
    tool_input = tool_call.get("input", tool_call.get("tool_input", {}))
    
    if check_type == "deny_command":
        # Check if the command matches any deny pattern
        command = tool_input.get("command", "")
        for pattern in params.get("patterns", []):
            if re.search(pattern["regex"], command):
                return {
                    "decision": "deny",
                    "reason": pattern.get("reason", f"Blocked by rule {rule['id']}"),
                    "rule_id": rule["id"]
                }
        return {"decision": "allow", "rule_id": rule["id"]}
    
    elif check_type == "path_pattern":
        # Check if file path matches forbidden pattern
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
    
    elif check_type == "require_field":
        # Check if a required YAML field is present (for write operations)
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
    
    elif check_type == "regex":
        # Generic regex match against tool input
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
    
    elif check_type == "yaml_field":
        # Check YAML frontmatter for required fields or field values
        if tool_name in ("write", "edit"):
            content = tool_input.get("content", "")
            file_path = tool_input.get("file_path", "")
            
            # Check if file matches the file_glob pattern
            file_glob = params.get("file_glob", "")
            if file_glob:
                import fnmatch
                # Normalize file path for glob matching
                normalized_path = file_path.replace("\\", "/")
                if not fnmatch.fnmatch(normalized_path, file_glob):
                    return {"decision": "allow", "rule_id": rule["id"]}
            
            # Check if file is in scope directories
            scope_dirs = params.get("scope_dirs", [])
            in_scope = False
            for scope_dir in scope_dirs:
                if scope_dir in file_path:
                    in_scope = True
                    break
            
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
    
    elif check_type == "json_schema":
        # Validate tool input against a JSON Schema
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
    
    elif check_type == "custom_function":
        # Call a custom Python function for complex checks
        function_name = params.get("function", "")
        try:
            # Import the function module
            if "." in function_name:
                module_path, func_name = function_name.rsplit(".", 1)
                # Handle different import patterns
                if module_path == "Checks":
                    # For "Checks.function_name", import the submodule directly
                    module = __import__(f"Checks.{func_name}", fromlist=[func_name])
                else:
                    # For "module.submodule.function", import from full path
                    module = __import__(module_path, fromlist=[func_name])
            else:
                # Simple function name - try importing from Checks
                module = __import__(f"Checks.{function_name}", fromlist=[function_name])
                func_name = function_name
            
            # Get the actual function from the module
            custom_func = getattr(module, func_name)
            
            # Call the function with tool_call and params
            result = custom_func(tool_call, params)
            if result.get("deny"):
                return {
                    "decision": "deny",
                    "reason": result.get("reason", f"Custom function check failed (rule {rule['id']})"),
                    "rule_id": rule["id"]
                }
            return {"decision": "allow", "rule_id": rule["id"]}
        except Exception as e:
            # If custom function fails, log but allow (fail-open for custom functions)
            return {"decision": "allow", "rule_id": rule["id"], "note": f"custom function error: {e}"}
    
    # Unknown check type — deny for safety
    return {"decision": "deny", "rule_id": rule["id"], "reason": f"BLOCKED by rule {rule['id']}: unknown check type requires explicit user confirmation"}
