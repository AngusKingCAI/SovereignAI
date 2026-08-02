# Scripts/Rules/Enforcement/evaluator.py
# id: evaluator
# version: 1.0.0
# owner: SovereignAI
# updated: 2026-08-02
# purpose: Rule evaluator module
# agent: all
# persona: governance
#!/usr/bin/env python3
"""
Rule evaluator module — provides the core evaluation logic used by
the PDP hook, test runner, and drift detection.

MODULAR DESIGN: Each check type has its own isolated function.
Adding new check types cannot break existing ones.
"""
import re
import yaml

# Registry of check type evaluators - allows modular addition of new check types
_CHECK_EVALUATORS = {}

def register_check_type(check_type: str, evaluator_func):
    """Register a new check type evaluator function."""
    _CHECK_EVALUATORS[check_type] = evaluator_func

def auto_discover_check_types():
    """Auto-discover and load all check type modules from Checks/Types/."""
    from pathlib import Path
    import importlib
    import sys
    
    types_dir = Path(__file__).parent.parent / "Checks" / "Types"
    if types_dir.exists():
        # Add parent directories to path for imports
        rules_dir = types_dir.parent.parent
        sys.path.insert(0, str(rules_dir))
        
        for module_file in types_dir.glob("*.py"):
            if module_file.name.startswith("_"):
                continue
            module_name = f"Checks.Types.{module_file.stem}"
            try:
                module = importlib.import_module(module_name)
                # Register the evaluate function from the module
                if hasattr(module, 'evaluate'):
                    check_type = module_file.stem
                    register_check_type(check_type, module.evaluate)
            except Exception as e:
                print(f"Warning: Failed to load check type {module_name}: {e}")

# Auto-discover check types on module import
auto_discover_check_types()

def evaluate_rule(rule: dict, tool_call: dict) -> dict:
    """Evaluate a single Policy Card against a tool call.
    Returns: {decision: allow|deny, reason: str, rule_id: str}
    
    This function is imported by:
    - Scripts/Rules/Enforcement/pre_tool_pdp.py (runtime enforcement)
    - Scripts/Rules/Validation/run_rule_tests.py (test runner)
    - Scripts/Analysis/drift_detection.py (drift detection)
    """
    check = rule.get("check", {})
    check_type = check.get("type")
    params = check.get("params", {})
    
    # Extract the relevant input from the tool call
    tool_name = tool_call.get("tool", tool_call.get("tool_name", ""))
    tool_input = tool_call.get("input", tool_call.get("tool_input", {}))
    
    # Dispatch to the appropriate evaluator function based on check type
    evaluator_func = _CHECK_EVALUATORS.get(check_type)
    if evaluator_func:
        return evaluator_func(rule, tool_name, tool_input, params)
    else:
        # Unknown check type — deny for safety
        return {
            "decision": "deny",
            "rule_id": rule["id"],
            "reason": f"BLOCKED by rule {rule['id']}: unknown check type requires explicit user confirmation"
        }