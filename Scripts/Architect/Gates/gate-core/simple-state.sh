#!/bin/bash

# Simple state file operations without jq dependency
# Uses grep and basic string operations for JSON parsing

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

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

# Extract JSON value using grep and sed
extract_json_value() {
    local json="$1"
    local key="$2"
    echo "$json" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed 's/.*"\([^"]*\)"$/\1/'
}

# Check if phase is completed
is_phase_completed() {
    local phase="$1"
    local state_json=$(read_state_file "$phase")
    
    local completion_hash=$(extract_json_value "$state_json" "completion_hash")
    
    if [ "$completion_hash" = "null" ] || [ -z "$completion_hash" ]; then
        return 1
    fi
    
    return 0
}

# Create simple state file
create_simple_state_file() {
    local phase="$1"
    local phase_name="$2"
    local completion_signature="$3"
    local previous_phase_hash="$4"
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local state_file=$(get_state_file_path "$phase")
    
    cat > "$state_file" << EOF
{
  "phase": "$phase",
  "phase_name": "$phase_name",
  "completion_hash": null,
  "state_hash": null,
  "timestamp": "$timestamp",
  "completion_signature": "$completion_signature",
  "previous_phase_hash": $previous_phase_hash,
  "state_files": [],
  "metadata": {
    "specification_status": "pending",
    "implementation_status": "pending",
    "test_status": "pending"
  }
}
EOF
    
    echo "Created state file for phase $phase"
}

# Export functions
export -f get_state_file_path
export -f state_file_exists
export -f read_state_file
export -f extract_json_value
export -f is_phase_completed
export -f create_simple_state_file