# scripts/enforcement/pre_tool_pdp.py
#!/usr/bin/env python3
"""
Policy Decision Point for Devin CLI PreToolUse hook.
Evaluates every tool call against binding Policy Cards.
"""
import sys
import json
import yaml
import os
from pathlib import Path
from datetime import datetime

# Import the evaluator module for the core evaluation logic
sys.path.insert(0, str(Path(__file__).parent.parent))
from enforcement.evaluator import evaluate_rule

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
POLICY_CARDS_DIR = PROJECT_ROOT / "governance" / "policy-cards"
AUDIT_LOG = PROJECT_ROOT / ".audit" / "violations.jsonl"

def load_active_agent(tool_call: dict = None):
    """Determine the active agent from session state or tool call context.
    
    In a single-agent deployment, this returns a fixed agent (configurable via ACTIVE_AGENT env var).
    In a multi-agent deployment, this would resolve agent identity from:
    - The session_id in the tool call payload (Devin CLI provides this)
    - A session state store (e.g., Redis, file-based state)
    - Or agent-specific environment variables per subprocess
    
    Current implementation: Single-agent mode with environment variable fallback.
    """
    # If tool_call contains session_id, in a real implementation we would:
    # 1. Look up session state in a state store
    # 2. Return the agent associated with that session
    # For now, we use environment variable configuration
    return os.environ.get("ACTIVE_AGENT", "architect")

def load_binding_rules(agent: str):
    """Load all binding-severity Policy Cards for the active agent.
    
    Note: This function re-reads and re-parses YAML files on every call.
    In a production deployment with many rules, consider adding:
    - An in-memory cache with mtime-based invalidation
    - Or a long-lived daemon process that reloads on SIGHUP
    
    Current implementation: No caching (simple, correct, slower with many rules).
    """
    rules = []
    # Load shared rules (apply to all agents)
    shared_dir = POLICY_CARDS_DIR / "shared"
    if shared_dir.exists():
        for card_file in sorted(shared_dir.glob("*.yaml")):  # Sort for deterministic order
            card = yaml.safe_load(card_file.read_text())
            if card.get("severity") == "blocking" and card.get("agent") in ("all", agent):
                rules.append(card)
    # Load agent-specific rules
    agent_dir = POLICY_CARDS_DIR / agent
    if agent_dir.exists():
        for card_file in sorted(agent_dir.glob("*.yaml")):  # Sort for deterministic order
            card = yaml.safe_load(card_file.read_text())
            if card.get("severity") == "blocking":
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

def main():
    """Main PDP entry point — reads tool call from stdin, returns decision."""
    try:
        stdin_data = sys.stdin.read()
        tool_call = json.loads(stdin_data)
        # Normalize tool call structure to use "tool" and "input" keys
        if "tool_name" in tool_call and "tool" not in tool_call:
            tool_call["tool"] = tool_call["tool_name"]
        if "tool_input" in tool_call and "input" not in tool_call:
            tool_call["input"] = tool_call["tool_input"]
    except (json.JSONDecodeError, ValueError) as e:
        # Check if any safety-tier rules are active
        agent = load_active_agent()
        rules = load_binding_rules(agent)
        has_safety_rules = any(rule.get("tier") == "safety" for rule in rules)
        
        if has_safety_rules:
            # Fail-closed for safety rules: deny on malformed input
            error_output = {
                "hookSpecificOutput": {
                    "additionalContext": f"⛔ BLOCKED: PDP failed to parse stdin (safety-tier rules active). "
                                         f"Error: {e}. The tool call was denied to prevent potential safety violations."
                }
            }
            print(json.dumps(error_output))
            sys.exit(2)  # exit code 2 = deny
        else:
            # Fail-open for non-safety rules: allow but log
            print(json.dumps({"decision": "allow", "error": f"stdin parse failed: {e}"}))
            sys.exit(0)
    
    agent = load_active_agent()
    rules = load_binding_rules(agent)
    
    # Evaluate every binding rule — any deny means deny
    # Wrap in try/except to catch evaluation errors
    try:
        for rule in rules:
            result = evaluate_rule(rule, tool_call)
            log_decision(tool_call, result)
            if result["decision"] == "deny":
                # Output the deny decision as additionalContext
                output = {
                    "hookSpecificOutput": {
                        "additionalContext": f"⛔ BLOCKED by rule {result['rule_id']}: {result['reason']}\n"
                                             f"The tool call was denied by the Policy Decision Point. "
                                             f"Modify your approach and try again."
                    }
                }
                print(json.dumps(output))
                sys.exit(2)  # exit code 2 = deny the tool call
    except Exception as e:
        # Evaluation error: check if safety rules are active
        has_safety_rules = any(rule.get("tier") == "safety" for rule in rules)
        if has_safety_rules:
            # Fail-closed for safety rules
            error_output = {
                "hookSpecificOutput": {
                    "additionalContext": f"⛔ BLOCKED: PDP evaluation error (safety-tier rules active). "
                                         f"Error: {e}. The tool call was denied to prevent potential safety violations."
                }
            }
            print(json.dumps(error_output))
            sys.exit(2)
        else:
            # Fail-open for non-safety rules
            print(json.dumps({"decision": "allow", "error": f"evaluation error: {e}"}))
            sys.exit(0)
    
    # All rules passed — allow
    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
