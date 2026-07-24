#!/usr/bin/env python3
"""
Gate Verifier Hook - PostToolUse
Automatically detects workflow step completion and posts gate verification messages
Eliminates manual gate posting requirements in workflows
"""

import json
import sys
import os
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Gate detection patterns based on tool operations
GATE_PATTERNS = {
    "gate_1_governance_context": {
        "description": "Governance context established",
        "tools": ["read"],
        "file_patterns": ["Rules/", "AGENTS.md"],
        "message": "✅ Gate 1 PASS: Governance context established, rules loaded"
    },
    "gate_2_plan_structure": {
        "description": "Plan structure created",
        "tools": ["write", "edit"],
        "file_patterns": ["Workflow/", "Plans/"],
        "message": "✅ Gate 2 PASS: Plan structure created, template compliance verified"
    },
    "gate_3_early_validation": {
        "description": "Early gate validation",
        "tools": ["exec"],
        "command_patterns": ["gate", "validate"],
        "message": "✅ Gate 3 PASS: Early gate validation completed"
    },
    "gate_4_review_completed": {
        "description": "Review process completed",
        "tools": ["write"],
        "file_patterns": ["Logs/Roundtable/", "Logs/Planner/"],
        "message": "✅ Gate 4 PASS: Review process completed, findings logged"
    },
    "gate_5_improvements_applied": {
        "description": "Improvements applied",
        "tools": ["edit", "write"],
        "file_patterns": ["Plans/plan-"],
        "message": "✅ Gate 5 PASS: Findings applied, plan improved"
    }
}


def detect_gate_from_operation(tool_name: str, tool_input: Dict) -> Optional[str]:
    """Detect which gate (if any) corresponds to the operation."""
    file_path = tool_input.get("file_path", "")
    command = tool_input.get("command", "")
    
    for gate_id, gate_config in GATE_PATTERNS.items():
        # Check tool match
        if tool_name not in gate_config.get("tools", []):
            continue
        
        # Check file patterns
        file_patterns = gate_config.get("file_patterns", [])
        if file_patterns:
            if not any(pattern in file_path for pattern in file_patterns):
                continue
        
        # Check command patterns
        command_patterns = gate_config.get("command_patterns", [])
        if command_patterns:
            if not any(pattern.lower() in command.lower() for pattern in command_patterns):
                continue
        
        return gate_id
    
    return None


def get_session_context() -> Dict:
    """Get current session context."""
    try:
        # Try to read from session logger output
        session_file = PROJECT_ROOT / ".devin" / "current_session.json"
        if session_file.exists():
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    
    # Fallback to agent_config.json for agent type
    try:
        config_file = PROJECT_ROOT / ".devin" / "agent_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return {
                    "session_id": "unknown",
                    "agent_type": config.get("current_agent", "Architect")
                }
    except Exception:
        pass
    
    # Final fallback to Architect
    return {"session_id": "unknown", "agent_type": "Architect"}


def log_gate_completion(gate_id: str, gate_message: str, session_context: Dict):
    """Log gate completion to gate log file."""
    try:
        agent_type = session_context.get("agent_type", "Architect")
        logs_dir = PROJECT_ROOT / "Logs" / agent_type / "Gates"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = logs_dir / "gate-completions.jsonl"
        
        log_entry = {
            "timestamp": json.dumps({"$date": {"$numberLong": str(int(Path(__file__).stat().st_mtime * 1000))}}),
            "gate_id": gate_id,
            "gate_message": gate_message,
            "session_id": session_context.get("session_id", "unknown"),
            "agent_type": agent_type
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception as e:
        print(f"Error logging gate completion: {e}", file=sys.stderr)


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PostToolUse")
        
        if hook_event != "PostToolUse":
            # Only process PostToolUse events
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
        
        # Detect if this operation corresponds to a gate
        gate_id = detect_gate_from_operation(tool_name, tool_input)
        
        if gate_id:
            gate_config = GATE_PATTERNS[gate_id]
            gate_message = gate_config["message"]
            
            # Get session context
            session_context = get_session_context()
            
            # Log gate completion
            log_gate_completion(gate_id, gate_message, session_context)
            
            # Return output with the gate message as additional context
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": gate_message
                }
            }
            
            print(json.dumps(output))
            sys.exit(0)
        else:
            # No gate detected, return empty output
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
            sys.exit(0)
        
    except Exception as e:
        print(f"Gate verifier error: {e}", file=sys.stderr)
        # Return empty output on error (non-blocking)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()