#!/bin/bash

# Chain Verification for Phase Gate System
# Verifies hash chain integrity across phases

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use current working directory as project root (scripts are run from project root)
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Source hash functions and state file functions
source "$SCRIPT_DIR/hash-functions.sh"
source "$SCRIPT_DIR/state-file.sh"

# Verify hash chain from phase 0 to given phase
verify_chain_integrity() {
    local target_phase="$1"
    
    echo "Verifying hash chain from phase 0 to phase $target_phase..."
    
    # Start from phase 0
    local current_phase=0
    local previous_state_hash=null
    
    while [ $current_phase -le $target_phase ]; do
        echo "Checking phase $current_phase..."
        
        # Check if state file exists
        if ! state_file_exists "$current_phase"; then
            echo "Error: State file missing for phase $current_phase" >&2
            return 3
        fi
        
        # Read state file
        local state_json=$(read_state_file "$current_phase")
        
        # Extract state hash
        local state_hash=$(echo "$state_json" | jq -r '.state_hash')
        
        # Verify previous phase hash matches
        local expected_previous_hash=$(echo "$state_json" | jq -r '.previous_phase_hash')
        
        if [ "$current_phase" -eq 0 ]; then
            # Phase 0 should have null previous hash
            if [ "$expected_previous_hash" != "null" ]; then
                echo "Error: Phase 0 should have null previous_phase_hash, got: $expected_previous_hash" >&2
                return 3
            fi
        else
            # Verify chain continuity
            if [ "$expected_previous_hash" != "$previous_state_hash" ]; then
                echo "Error: Hash chain broken at phase $current_phase" >&2
                echo "Expected previous hash: $previous_state_hash" >&2
                echo "Actual previous hash: $expected_previous_hash" >&2
                return 3
            fi
        fi
        
        # Update previous state hash for next iteration
        previous_state_hash="$state_hash"
        
        echo "Phase $current_phase: state_hash=$state_hash, chain OK"
        
        current_phase=$((current_phase + 1))
    done
    
    echo "Hash chain verification passed from phase 0 to phase $target_phase"
    return 0
}

# Verify single phase completion
verify_phase_completion() {
    local phase="$1"
    
    echo "Verifying completion of phase $phase..."
    
    # Check if state file exists
    if ! state_file_exists "$phase"; then
        echo "Error: Phase $phase not started - no state file found" >&2
        return 1
    fi
    
    # Read state file
    local state_json=$(read_state_file "$phase")
    
    # Check completion hash
    local completion_hash=$(echo "$state_json" | jq -r '.completion_hash')
    if [ "$completion_hash" = "null" ] || [ -z "$completion_hash" ]; then
        echo "Error: Phase $phase not completed - no completion hash" >&2
        return 1
    fi
    
    # Check completion signature
    local completion_signature=$(echo "$state_json" | jq -r '.completion_signature')
    if [ "$completion_signature" = "null" ] || [ -z "$completion_signature" ]; then
        echo "Error: Phase $phase not authorized - no completion signature" >&2
        return 4
    fi
    
    # Verify state files hash matches completion hash
    local state_files=$(echo "$state_json" | jq -r '.state_files[]')
    if [ -n "$state_files" ]; then
        local current_hash=$(generate_multi_file_hash $state_files)
        if [ "$current_hash" != "$completion_hash" ]; then
            echo "Error: Phase $phase state files have been modified" >&2
            echo "Expected hash: $completion_hash" >&2
            echo "Current hash: $current_hash" >&2
            return 2
        fi
    fi
    
    echo "Phase $phase completion verified: hash=$completion_hash, signature=$completion_signature"
    return 0
}

# Link phases in chain (call when phase N completes)
link_phase_chain() {
    local current_phase="$1"
    local previous_phase=$((current_phase - 1))
    
    if [ $previous_phase -lt 0 ]; then
        echo "Phase 0 has no previous phase to link"
        return 0
    fi
    
    echo "Linking phase $current_phase to phase $previous_phase..."
    
    # Get previous phase state hash
    if ! state_file_exists "$previous_phase"; then
        echo "Error: Previous phase $previous_phase state file not found" >&2
        return 3
    fi
    
    local previous_state_json=$(read_state_file "$previous_phase")
    local previous_state_hash=$(echo "$previous_state_json" | jq -r '.state_hash')
    
    # Update current phase state file with previous phase hash
    local current_state_json=$(read_state_file "$current_phase")
    local updated_json=$(echo "$current_state_json" | jq --arg hash "$previous_state_hash" '.previous_phase_hash = $hash')
    
    # Recalculate state hash after update
    local new_state_hash=$(echo "$updated_json" | generate_string_hash)
    updated_json=$(echo "$updated_json" | jq --arg hash "$new_state_hash" '.state_hash = $hash')
    
    # Write updated state file
    write_state_file "$current_phase" "$updated_json"
    
    echo "Phase $current_phase linked to phase $previous_phase (hash: $previous_state_hash)"
    return 0
}

# Export functions for use in other scripts
export -f verify_chain_integrity
export -f verify_phase_completion
export -f link_phase_chain