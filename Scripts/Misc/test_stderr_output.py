#!/usr/bin/env python3
"""
Test script that writes to stderr for user messages
while stdout can be used for data
"""
import sys
from datetime import datetime

# Write user message to stderr
print("=== STDERR MESSAGE (should appear in terminal) ===", file=sys.stderr)
print(f"Timestamp: {datetime.now().isoformat()}", file=sys.stderr)
print("This is a user message via stderr", file=sys.stderr)
print("=== END STDERR MESSAGE ===", file=sys.stderr)

# Write data to stdout (if needed)
print("This is data output via stdout")