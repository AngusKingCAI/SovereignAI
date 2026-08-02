# Scripts/Rules/Enforcement/evaluator.py
# id: evaluator
# version: 3.0.0
# owner: SovereignAI
# updated: 2026-08-02
# purpose: Unified rule evaluator with hook interface
# agent: all
# persona: governance
#!/usr/bin/env python3
"""
Unified rule evaluator - handles hook interface and rule evaluation.

KISS DESIGN: Each rule has its own Python file with matching name.
Evaluator scans and loads rule-specific implementations dynamically.
Handles both PreToolUse and PostToolUse hook events directly.
"""
import sys
import json
import yaml
import os
import importlib
from pathlib import Path
from datetime import datetime

# Registry of rule evaluators - maps rule IDs to their evaluate functions
_RULE_EVALUATORS = {}

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RULES_DIR = PROJECT_ROOT / "Rules"
AUDIT_LOG = PROJECT_ROOT / "Logs" / "Audit" / "violations.jsonl"

def auto_discover_rules():
    """Auto-discover and load all rule-specific Python modules."""
    rules_dir = Path(__file__).parent.parent
    if rules_dir.exists():
        # Add rules directory to path for imports
        sys.path.insert(0, str(rules_dir))
        
        for module_file in rules_dir.glob("*.py"):
            if module_file.name.startswith("_"):
                continue
            # Skip template files
            if "template" in module_file.name.lower():
                continue
            module_name = module_file.stem
            try:
                module = importlib.import_module(module_name)
                # Register the evaluate function from the module
                if hasattr(module, 'evaluate'):
                    # Use module name as rule ID
                    _RULE_EVALUATORS[module_name] = module.evaluate
            except Exception as e:
                print(f"Warning: Failed to load rule {module_name}: {e}")

# Auto-discover rules on module import
auto_discover_rules()

def load_active_agent():
    """Determine the active agent from environment variable."""
    return os.environ.get("ACTIVE_AGENT", "architect")

def load_rules(agent: str, severity: str = None):
    """Load all Policy Cards for the active agent, optionally filtered by severity."""
    rules = []
    # Load shared rules
    shared_dir = RULES_DIR / "Shared"
    if shared_dir.exists():
        for card_file in sorted(shared_dir.glob("*.yaml")):
            card = yaml.safe_load(card_file.read_text(encoding='utf-8'))
            if card.get("agent") in ("all", agent):
                if severity is None or card.get("severity") == severity:
                    rules.append(card)
    # Load agent-specific rules
    agent_dir = RULES_DIR / agent
    if agent_dir.exists():
        for card_file in sorted(agent_dir.glob("*.yaml")):
            card = yaml.safe_load(card_file.read_text(encoding='utf-8'))
            if severity is None or card.get("severity") == severity:
                rules.append(card)
    return rules

def log_decision(tool_call: dict, result: dict):
    """Log every PDP decision to the audit trail."""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tool": tool_call.get("tool", ""),
        "input_summary": str(tool_call.get("input", ""))[:200],
        "decision": result["decision"],
        "rule_id": result.get("rule_id"),
        "reason": result.get("reason", "")
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def evaluate_rule(rule: dict, tool_call: dict) -> dict:
    """Evaluate a single Policy Card against a tool call.
    Returns: {decision: allow|deny, reason: str, rule_id: str}
    """
    rule_id = rule.get("id", "")
    params = rule.get("check", {}).get("params", {})
    
    # Extract the relevant input from the tool call
    tool_name = tool_call.get("tool", tool_call.get("tool_name", ""))
    tool_input = tool_call.get("input", tool_call.get("tool_input", {}))
    
    # Dispatch to the rule-specific evaluator function
    evaluator_func = _RULE_EVALUATORS.get(rule_id)
    if evaluator_func:
        return evaluator_func(rule, tool_name, tool_input, params)
    else:
        # Unknown rule — deny for safety
        return {
            "decision": "deny",
            "rule_id": rule_id,
            "reason": f"⛔ BLOCKED by rule {rule_id}: unknown rule requires explicit user confirmation"
        }

def main():
    """Main entry point - handles hook interface directly."""
    try:
        stdin_data = sys.stdin.read()
        tool_call = json.loads(stdin_data)
        # Normalize tool call structure
        if "tool_name" in tool_call and "tool" not in tool_call:
            tool_call["tool"] = tool_call["tool_name"]
        if "tool_input" in tool_call and "input" not in tool_call:
            tool_call["input"] = tool_call["tool_input"]
        
        # Determine hook event type from environment
        hook_event = os.environ.get("HOOK_EVENT", "PreToolUse")
        
        # Don't interfere if no tool/input
        if "tool" not in tool_call or "input" not in tool_call:
            sys.exit(0)
    except (json.JSONDecodeError, ValueError) as e:
        # Parse error - check if safety rules are active
        agent = load_active_agent()
        rules = load_rules(agent)
        has_safety_rules = any(rule.get("tier") == "safety" for rule in rules)
        
        if has_safety_rules and hook_event == "PreToolUse":
            # Use user bypass for safety rules on parse error
            error_output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": f"Evaluator failed to parse stdin (safety-tier rules active). Error: {e}. This action requires user confirmation due to safety policy."
                }
            }
            print(json.dumps(error_output))
            sys.exit(0)
        else:
            # Fail-open for non-safety rules or post-tool events
            sys.exit(0)
    
    agent = load_active_agent()
    
    if hook_event == "PreToolUse":
        # Load blocking rules for pre-tool validation
        rules = load_rules(agent, "blocking")
        
        violations = []
        for rule in rules:
            result = evaluate_rule(rule, tool_call)
            log_decision(tool_call, result)
            
            if result["decision"] == "deny":
                violations.append(result)
        
        if violations:
            # Return permissionDecision: "ask" to trigger user bypass dialog
            violation_messages = [f"Rule {v['rule_id']}: {v['reason']}" for v in violations]
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": "\n".join(violation_messages)
                }
            }
            print(json.dumps(output))
            sys.exit(0)
        else:
            # No violations - exit with no output
            sys.exit(0)
    
    elif hook_event == "PostToolUse":
        # Load advisory rules for post-tool validation
        rules = load_rules(agent, "advisory")
        
        warnings = []
        for rule in rules:
            result = evaluate_rule(rule, tool_call)
            if result["decision"] == "deny":
                warnings.append(f"⚠️ Advisory rule {result['rule_id']}: {result['reason']}")
        
        if warnings:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "\n".join(warnings) + "\n"
                }
            }
            print(json.dumps(output))
        else:
            print(json.dumps({"decision": "allow"}))
        
        sys.exit(0)
    
    else:
        # Unknown hook event - fail open
        sys.exit(0)

if __name__ == "__main__":
    main()