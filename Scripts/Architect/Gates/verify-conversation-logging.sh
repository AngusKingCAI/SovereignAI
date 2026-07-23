#!/bin/bash

# Gate 5: Verify conversation logging before session completion
# This ensures maximum observability by requiring conversation audit trails

PHASE=$1

echo "=========================================="
echo "Conversation Logging Verification"
echo "=========================================="
echo "Phase: $PHASE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

if [ -z "$PHASE" ]; then
    echo "Error: No phase number provided"
    exit 1
fi

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
CONVERSATIONS_DIR="$PROJECT_ROOT/Logs/Architect/Conversations"

# Check if conversations directory exists
if [ ! -d "$CONVERSATIONS_DIR" ]; then
    echo "Error: Conversations directory not found: $CONVERSATIONS_DIR"
    exit 1
fi

# Check if there are any conversation log files
if ls "$CONVERSATIONS_DIR"/*.json 1> /dev/null 2>&1; then
    echo "Conversation log files found"
else
    echo "Error: No conversation log files found in $CONVERSATIONS_DIR"
    exit 1
fi

# Check the most recent conversation file
LATEST_FILE=$(ls -t "$CONVERSATIONS_DIR"/*.json 2>/dev/null | head -1)

echo "Latest conversation file: $LATEST_FILE"

# Verify conversation log structure
SESSION_ID=$(grep -o '"session_id": "[^"]*"' "$LATEST_FILE" | sed 's/.*"\([^"]*\)".*/\1/')
TRACE_ID=$(grep -o '"trace_id": "[^"]*"' "$LATEST_FILE" | sed 's/.*"\([^"]*\)".*/\1/')
MESSAGE_COUNT=$(grep -o '"role":' "$LATEST_FILE" | wc -l)
SUMMARY=$(grep -o '"summary": "[^"]*"' "$LATEST_FILE" | sed 's/.*"\([^"]*\)".*/\1/')

echo "Session ID: $SESSION_ID"
echo "Trace ID: $TRACE_ID"
echo "Message count: $MESSAGE_COUNT"
echo "Summary: $SUMMARY"

# Validate conversation log structure
if [ -z "$SESSION_ID" ]; then
    echo "Error: Session ID not found in conversation log"
    exit 1
fi

if [ -z "$TRACE_ID" ]; then
    echo "Error: Trace ID not found in conversation log"
    exit 1
fi

if [ "$MESSAGE_COUNT" -lt 2 ]; then
    echo "Error: Conversation log must contain at least 2 messages (user + assistant)"
    exit 1
fi

if [ -z "$SUMMARY" ]; then
    echo "Error: Conversation summary not found in conversation log"
    exit 1
fi

echo "=========================================="
echo "Conversation Logging Verification PASSED"
echo "=========================================="
echo "Conversation audit trail verified successfully"
echo "Session: $SESSION_ID"
echo "Trace: $TRACE_ID"
echo "Messages: $MESSAGE_COUNT"
echo "=========================================="

exit 0