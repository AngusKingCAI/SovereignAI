#!/usr/bin/env python3
"""
Test script for PostCompaction hook - prints to chat
"""
import json
import sys
from datetime import datetime

def main():
    # Read stdin data if available
    try:
        if not sys.stdin.isatty():
            stdin_data = sys.stdin.read()
            if stdin_data:
                hook_input = json.loads(stdin_data)
            else:
                hook_input = {}
        else:
            hook_input = {}
    except (json.JSONDecodeError, Exception) as e:
        hook_input = {}
    
    # Get summary if available
    summary = hook_input.get("summary", "No summary available")
    timestamp = datetime.now().isoformat()
    
    # Create output that should appear in chat
    output_message = f"""
=== POST-COMPACTION HOOK FIRED ===
Timestamp: {timestamp}
Summary: {summary}
This message should appear in the chat after compaction.
==================================
"""
    
    # Output JSON with additionalContext to inject into chat
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PostCompaction",
            "additionalContext": output_message
        }
    }
    
    print(json.dumps(result, indent=2))
    
    # Also write to debug file
    with open("C:/SovereignAI/.hook_chat_test.txt", "w") as f:
        f.write(f"Hook fired at: {timestamp}\n")
        f.write(f"Summary: {summary}\n")

if __name__ == "__main__":
    main()