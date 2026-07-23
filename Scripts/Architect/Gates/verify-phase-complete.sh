#!/bin/bash

# Simple working verification script without jq dependency

PHASE=$1

echo "=========================================="
echo "Simple Phase Gate Verification"
echo "=========================================="
echo "Phase: $PHASE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

if [ -z "$PHASE" ]; then
    echo "Error: No phase number provided"
    exit 1
fi

if ! [[ "$PHASE" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid phase number"
    exit 1
fi

# Get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Source simple state functions
source "$SCRIPT_DIR/gate-core/simple-state.sh"

# Check if phase 0
if [ "$PHASE" -eq 0 ]; then
    echo "Phase 0 is the starting phase"
    
    if ! state_file_exists "0"; then
        echo "Creating initial Phase 0 state file..."
        create_simple_state_file "0" "Repository Foundation" "architect-approved" "null"
    else
        echo "Phase 0 state file exists"
    fi
    
    echo "Phase 0 verification passed"
    exit 0
fi

# For other phases, check previous phase
PREVIOUS_PHASE=$((PHASE - 1))
echo "Checking previous phase: $PREVIOUS_PHASE"

if ! state_file_exists "$PREVIOUS_PHASE"; then
    echo "Error: Previous phase $PREVIOUS_PHASE state file not found"
    exit 1
fi

# Check if previous phase is completed
if ! is_phase_completed "$PREVIOUS_PHASE"; then
    echo "Error: Phase $PREVIOUS_PHASE is not completed"
    exit 1
fi

echo "Phase $PREVIOUS_PHASE is completed"
echo "Phase $PHASE may proceed"
echo "=========================================="
echo "Verification PASSED"
echo "=========================================="

exit 0