#!/bin/bash

# Query Script for Phase Gate System
# Inspects current state of phases

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use current working directory as project root (scripts are run from project root)
PROJECT_ROOT="$(pwd)"

# Source core functions (using absolute paths)
GATE_CORE_DIR="$SCRIPT_DIR/gate-core"
source "$GATE_CORE_DIR/hash-functions.sh"
source "$GATE_CORE_DIR/state-file.sh"
source "$GATE_CORE_DIR/chain-verification.sh"
source "$GATE_CORE_DIR/audit-logging.sh"

# Usage information
usage() {
    echo "Usage: $0 <phase_number>"
    echo "Queries and displays the state of a specific phase"
    echo ""
    echo "Exit codes:"
    echo "  0 - State found and valid"
    echo "  1 - State not found"
    echo "  2 - State invalid/tampered"
    echo ""
    echo "Example:"
    echo "  $0 0  # Query Phase 0 state"
    echo "  $0 1  # Query Phase 1 state"
}

# Check arguments
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

PHASE="$1"

# Validate phase number
if ! [[ "$PHASE" =~ ^[0-9]+$ ]]; then
    echo "Error: Phase number must be a non-negative integer"
    usage
    exit 1
fi

echo "=========================================="
echo "Phase Gate State Query"
echo "=========================================="
echo "Querying Phase: $PHASE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Check if state file exists
if ! state_file_exists "$PHASE"; then
    echo "State not found: Phase $PHASE has no state file"
    echo "Phase $PHASE may not have been started yet"
    exit 1
fi

# Read state file
echo "Reading state file..."
state_json=$(read_state_file "$PHASE")

# Display state information
echo ""
echo "Phase Information:"
echo "  Phase: $(echo "$state_json" | jq -r '.phase')"
echo "  Name: $(echo "$state_json" | jq -r '.phase_name')"
echo "  Timestamp: $(echo "$state_json" | jq -r '.timestamp')"
echo ""

echo "Completion Status:"
completion_hash=$(echo "$state_json" | jq -r '.completion_hash')
if [ "$completion_hash" = "null" ] || [ -z "$completion_hash" ]; then
    echo "  Status: NOT COMPLETED"
    echo "  Completion Hash: None"
else
    echo "  Status: COMPLETED"
    echo "  Completion Hash: $completion_hash"
fi
echo ""

echo "Authorization:"
completion_signature=$(echo "$state_json" | jq -r '.completion_signature')
echo "  Signature: $completion_signature"
echo ""

echo "Chain Information:"
previous_hash=$(echo "$state_json" | jq -r '.previous_phase_hash')
if [ "$previous_hash" = "null" ]; then
    echo "  Previous Phase: None (starting phase)"
else
    echo "  Previous Phase Hash: $previous_hash"
fi

state_hash=$(echo "$state_json" | jq -r '.state_hash')
echo "  Current State Hash: $state_hash"
echo ""

echo "State Files:"
state_files=$(echo "$state_json" | jq -r '.state_files[]')
if [ -z "$state_files" ]; then
    echo "  No state files recorded"
else
    echo "$state_files" | while read -r file; do
        echo "  - $file"
    done
fi
echo ""

echo "Metadata:"
metadata=$(echo "$state_json" | jq -r '.metadata')
echo "$metadata" | jq -r 'to_entries | .[] | "  \(.key): \(.value)"'
echo ""

# Verify state integrity
echo "Verifying state integrity..."
if validate_state_file "$PHASE" "$state_json"; then
    echo "  ✓ State file structure valid"
else
    echo "  ✗ State file structure invalid"
    exit 2
fi

# Verify hash if completed
if [ "$completion_hash" != "null" ] && [ -n "$completion_hash" ]; then
    echo "Verifying completion hash..."
    current_files=()
    while IFS= read -r file; do
        file_path="$PROJECT_ROOT/$file"
        if [ -f "$file_path" ]; then
            current_files+=("$file_path")
        fi
    done <<< "$state_files"
    
    if [ ${#current_files[@]} -gt 0 ]; then
        current_hash=$(generate_multi_file_hash "${current_files[@]}")
        if [ "$current_hash" = "$completion_hash" ]; then
            echo "  ✓ Hash verification passed"
        else
            echo "  ✗ Hash verification FAILED"
            echo "    Expected: $completion_hash"
            echo "    Current:  $current_hash"
            exit 2
        fi
    fi
fi

echo "=========================================="
echo "✓ State Query Complete"
echo "=========================================="

exit 0