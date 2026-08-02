# Scripts/Rules/Checks/Types/custom_function.py
# id: custom_function, version: 1.0.0, owner: SovereignAI, updated: 2026-08-02, purpose: Custom function check type implementation, agent: all, persona: governance
"""Custom function check type - calls external Python functions."""

def evaluate(rule: dict, tool_name: str, tool_input: dict, params: dict) -> dict:
    """Call a custom Python function for complex checks."""
    function_name = params.get("function", "")
    try:
        # Simple function name - import from Checks module
        module = __import__(f"Checks.{function_name}", fromlist=[function_name])
        custom_func = getattr(module, function_name)
        
        # Call the function with tool_call and params
        tool_call = {"tool": tool_name, "input": tool_input}
        result = custom_func(tool_call, params)
        if result.get("deny"):
            return {
                "decision": "deny",
                "reason": result.get("reason", f"Custom function check failed (rule {rule['id']})"),
                "rule_id": rule["id"]
            }
        return {"decision": "allow", "rule_id": rule["id"]}
    except Exception as e:
        # If custom function fails, deny for safety to ensure issues are visible
        return {
            "decision": "deny",
            "rule_id": rule["id"],
            "reason": f"Custom function import error for {function_name}: {str(e)}"
        }