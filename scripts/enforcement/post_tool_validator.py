# scripts/enforcement/post_tool_validator.py
#!/usr/bin/env python3
"""
PostToolUse hook - advisory validation for non-blocking rules.
Injects warnings for soft violations without blocking the action.
"""
import json
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"

def load_advisory_rules(agent: str):
    """Load all advisory-severity Policy Cards for the active agent."""
    rules = []
    # Load shared rules
    shared_dir = POLICY_CARDS_DIR / "shared"
    if shared_dir.exists():
        for card_file in sorted(shared_dir.glob("*.yaml")):
            card = yaml.safe_load(card_file.read_text())
            if card.get("severity") == "advisory" and card.get("agent") in ("all", agent):
                rules.append(card)
    # Load agent-specific rules
    agent_dir = POLICY_CARDS_DIR / agent
    if agent_dir.exists():
        for card_file in sorted(agent_dir.glob("*.yaml")):
            card = yaml.safe_load(card_file.read_text())
            if card.get("severity") == "advisory":
                rules.append(card)
    return rules

def main():
    """Main entry point — reads tool call from stdin, returns advisory warnings."""
    try:
        stdin_data = __import__('sys').stdin.read()
        tool_call = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError):
        # Malformed input — don't block post-tool
        print(json.dumps({"decision": "allow"}))
        exit(0)
    
    import os
    agent = os.environ.get("ACTIVE_AGENT", "architect")
    rules = load_advisory_rules(agent)
    
    warnings = []
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from enforcement.evaluator import evaluate_rule
    
    # Normalize tool call structure
    if "tool_name" in tool_call and "tool" not in tool_call:
        tool_call["tool"] = tool_call["tool_name"]
    if "tool_input" in tool_call and "input" not in tool_call:
        tool_call["input"] = tool_call["tool_input"]
    
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
    
    exit(0)

if __name__ == "__main__":
    main()
