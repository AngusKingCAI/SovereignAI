"""PreToolUse hook test to see if popup decisions work in Devin CLI."""

import sys
import json


def main():
    """Test PreToolUse popup decision capability."""
    try:
        # Read stdin for hook event data
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        
        print(f"[PreToolUse Test] Tool: {tool_name}, Input: {tool_input}", file=sys.stderr)
        
        # Test: Try to return an "ask" decision to see if Devin CLI supports popup
        # Based on research, this might not work in Devin CLI (only supports approve/block)
        # But we want to test it empirically
        
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": "PreToolUse popup test - asking for user decision"
            }
        }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"[PreToolUse Test Error] {str(e)}", file=sys.stderr)
        # If we fail, allow the tool to proceed
        sys.exit(0)


if __name__ == "__main__":
    main()
