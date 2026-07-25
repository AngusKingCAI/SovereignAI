#!/usr/bin/env python3
"""
Disabled tool permission check - allows all operations
"""
import json
import sys

def main():
    """Always allow operations."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse"}}))
    sys.exit(0)

if __name__ == "__main__":
    main()