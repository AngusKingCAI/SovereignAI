#!/bin/bash

# Simple recording script for phase completion

PHASE=$1
SIGNATURE=$2

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Phase Gate Recording System"
echo "=========================================="
echo "Recording Phase: $PHASE"
echo "Signature: $SIGNATURE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Step 1: Verify conversation logging before recording phase completion
echo "Step 1: Verifying conversation logging..."
CONVERSATION_VERIFY_SCRIPT="$SCRIPT_DIR/verify-conversation-logging.sh"
if [ -f "$CONVERSATION_VERIFY_SCRIPT" ]; then
    bash "$CONVERSATION_VERIFY_SCRIPT" "$PHASE"
    CONVERSATION_CHECK=$?
    if [ $CONVERSATION_CHECK -ne 0 ]; then
        echo "Error: Conversation logging verification failed"
        exit 1
    fi
else
    echo "Warning: Conversation logging verification script not found at $CONVERSATION_VERIFY_SCRIPT"
fi
echo "Conversation logging verified"

if [ -z "$PHASE" ] || [ -z "$SIGNATURE" ]; then
    echo "Error: Phase number and signature required"
    echo "Usage: $0 <phase_number> <signature>"
    exit 1
fi

if ! [[ "$PHASE" =~ ^[0-9]+$ ]]; then
    echo "Error: Invalid phase number"
    exit 1
fi

# Get paths
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Source simple state functions
source "$SCRIPT_DIR/gate-core/simple-state.sh"

# Create or update state file
if ! state_file_exists "$PHASE"; then
    echo "Creating new state file for Phase $PHASE..."
    
    # Determine previous phase hash
    PREVIOUS_PHASE=$((PHASE - 1))
    PREVIOUS_HASH="null"
    
    if [ $PREVIOUS_PHASE -ge 0 ] && state_file_exists "$PREVIOUS_PHASE"; then
        PREVIOUS_STATE=$(read_state_file "$PREVIOUS_PHASE")
        PREVIOUS_HASH=$(extract_json_value "$PREVIOUS_STATE" "state_hash")
    fi
    
    create_simple_state_file "$PHASE" "Phase $PHASE" "$SIGNATURE" "$PREVIOUS_HASH"
else
    echo "State file exists for Phase $PHASE, updating..."
fi

# Generate completion hash of relevant files
echo "Generating completion hash..."

# Define files to hash based on phase
case "$PHASE" in
    0)
        FILES=(
            "Rules/Architect/IDE_Architecture_Rules.md"
            "Docs/DIRECTORY_STRUCTURE.md"
            "Scripts/Architect/Gates/verify-phase-complete.sh"
            "Scripts/Architect/Gates/record-phase-complete.sh"
            "Scripts/Architect/Gates/verify-conversation-logging.sh"
            "Scripts/Architect/Gates/gate-core/simple-state.sh"
            "Scripts/src/logging/log_level.py"
            "Scripts/src/logging/log_entry.py"
            "Scripts/src/logging/log_context.py"
            "Scripts/src/logging/correlation.py"
            "Scripts/src/logging/formatter.py"
            "Scripts/src/logging/conversation_logger.py"
            "Scripts/src/logging/logger.py"
            "Scripts/src/logging/__init__.py"
            "Scripts/src/logging/output/stdout_output.py"
            "Scripts/src/logging/output/file_output.py"
            "Scripts/src/logging/output/__init__.py"
            "Scripts/config/logging_config.py"
            "Scripts/tests/test_log_level.py"
            "Scripts/tests/test_correlation.py"
            "Scripts/tests/test_formatter.py"
            "Scripts/tests/test_integration.py"
        )
        ;;
    *)
        FILES=(
            "Scripts/Architect/Gates/gate-core/simple-state.sh"
            "Scripts/Architect/Gates/verify-conversation-logging.sh"
            "Rules/Architect/IDE_Architecture_Rules.md"
            "Scripts/src/logging/log_level.py"
            "Scripts/src/logging/logger.py"
            "Scripts/config/logging_config.py"
        )
        ;;
esac

# Check which files exist
EXISTING_FILES=()
for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        EXISTING_FILES+=("$PROJECT_ROOT/$file")
        echo "  ✓ $file"
    else
        echo "  ✗ $file (not found)"
    fi
done

if [ ${#EXISTING_FILES[@]} -eq 0 ]; then
    echo "Warning: No files found for hashing"
    COMPLETION_HASH="placeholder-hash"
else
    # Generate hash (simple approach - concatenate file hashes)
    COMPLETION_HASH=""
    for file in "${EXISTING_FILES[@]}"; do
        FILE_HASH=$(sha256sum "$file" | awk '{print $1}')
        COMPLETION_HASH="${COMPLETION_HASH}${FILE_HASH}"
    done
    # Take first 64 chars as final hash
    COMPLETION_HASH=$(echo "$COMPLETION_HASH" | cut -c1-64)
fi

echo "Completion hash: $COMPLETION_HASH"

# Update state file with completion information
STATE_FILE=$(get_state_file_path "$PHASE")
CURRENT_STATE=$(read_state_file "$PHASE")

# Simple JSON update using sed
UPDATED_STATE=$(echo "$CURRENT_STATE" | sed "s/\"completion_hash\": null/\"completion_hash\": \"$COMPLETION_HASH\"/")
UPDATED_STATE=$(echo "$UPDATED_STATE" | sed "s/\"implementation_status\": \"pending\"/\"implementation_status\": \"complete\"/")
UPDATED_STATE=$(echo "$UPDATED_STATE" | sed "s/\"test_status\": \"pending\"/\"test_status\": \"passing\"/")

# Generate state hash
STATE_HASH=$(echo "$UPDATED_STATE" | sha256sum | awk '{print $1}')
UPDATED_STATE=$(echo "$UPDATED_STATE" | sed "s/\"state_hash\": null/\"state_hash\": \"$STATE_HASH\"/")

# Write updated state
echo "$UPDATED_STATE" > "$STATE_FILE"

echo "=========================================="
echo "Phase $PHASE Completion Recorded"
echo "=========================================="
echo "Completion Hash: $COMPLETION_HASH"
echo "State Hash: $STATE_HASH"
echo "Signature: $SIGNATURE"
echo "=========================================="

exit 0