#!/bin/bash

# State File Operations for Phase Gate System
# Handles reading, writing, and validation of state files

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use current working directory as project root (scripts are run from project root)
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Source hash functions
source "$SCRIPT_DIR/hash-functions.sh"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Get state file path for a phase
get_state_file_path() {
    local phase="$1"
    echo "$LOGS_DIR/phase-$phase-state.json"
}

# Check if state file exists
state_file_exists() {
    local phase="$1"
    local state_file=$(get_state_file_path "$phase")
    [ -f "$state_file" ]
}

# Read state file
read_state_file() {
    local phase="$1"
    local state_file=$(get_state_file_path "$phase")
    
    if [ ! -f "$state_file" ]; then
        echo "Error: State file not found for phase $phase: $state_file" >&2
        return 1
    fi
    
    cat "$state_file"
}

# Write state file
write_state_file() {
    local phase="$1"
    local state_json="$2"
    local state_file=$(get_state_file_path "$phase")
    
    # Create backup if file exists
    if [ -f "$state_file" ]; then
        cp "$state_file" "$state_file.backup"
    fi
    
    # Write new state
    echo "$state_json" > "$state_file"
    
    # Log the write operation
    local state_hash=$(echo "$state_json" | generate_string_hash)
    log_hash_operation "WRITE_STATE" "phase-$phase" "$state_hash"
    
    return 0
}

# Validate state file structure
validate_state_file() {
    local phase="$1"
    local state_json="$2"
    
    # Check if valid JSON using Python
    if ! python "$SCRIPT_DIR/gate-core/json-utils.py" validate "$state_file"; then
        echo "Error: Invalid JSON in state file for phase $phase" >&2
        return 1
    fi
    
    return 0
}

# Create initial state file for a phase
create_state_file() {
    local phase="$1"
    local phase_name="$2"
    local completion_signature="$3"
    local previous_phase_hash="$4"
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local state_file=$(get_state_file_path "$phase")
    
    # Build state JSON
    local state_json=$(jq -n \
        --arg phase "$phase" \
        --arg phase_name "$phase_name" \
        --arg timestamp "$timestamp" \
        --arg completion_signature "$completion_signature" \
        --arg previous_phase_hash "${previous_phase_hash:-null}" \
        '{
            phase: $phase,
            phase_name: $phase_name,
            completion_hash: null,
            state_hash: null,
            timestamp: $timestamp,
            completion_signature: $completion_signature,
            previous_phase_hash: $previous_phase_hash,
            state_files: [],
            metadata: {
                specification_status: "pending",
                implementation_status: "pending",
                test_status: "pending"
            }
        }')
    
    # Validate and write
    if validate_state_file "$phase" "$state_json"; then
        write_state_file "$phase" "$state_json"
        echo "Created initial state file for phase $phase"
        return 0
    else
        echo "Error: Failed to create state file for phase $phase" >&2
        return 1
    fi
}

# Update state file with completion information
update_state_completion() {
    local phase="$1"
    local completion_hash="$2"
    local state_files_json="$3"
    local metadata_json="$4"
    
    local state_json=$(read_state_file "$phase")
    
    # Update state file with completion information
    local updated_json=$(echo "$state_json" | jq \
        --arg completion_hash "$completion_hash" \
        --argjson state_files "$state_files_json" \
        --argjson metadata "$metadata_json" \
        '.completion_hash = $completion_hash |
         .state_files = $state_files |
         .metadata = $metadata')
    
    # Generate state hash of the updated JSON
    local state_hash=$(echo "$updated_json" | generate_string_hash)
    
    # Add state hash to the JSON
    updated_json=$(echo "$updated_json" | jq --arg state_hash "$state_hash" '.state_hash = $state_hash')
    
    # Validate and write
    if validate_state_file "$phase" "$updated_json"; then
        write_state_file "$phase" "$updated_json"
        echo "Updated state file for phase $phase with completion hash: $completion_hash"
        return 0
    else
        echo "Error: Failed to update state file for phase $phase" >&2
        return 1
    fi
}

# Export functions for use in other scripts
export -f get_state_file_path
export -f state_file_exists
export -f read_state_file
export -f write_state_file
export -f validate_state_file
export -f create_state_file
export -f update_state_completion