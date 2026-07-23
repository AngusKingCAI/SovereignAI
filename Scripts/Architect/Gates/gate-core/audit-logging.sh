#!/bin/bash

# Audit Logging for Phase Gate System
# Comprehensive logging of all gate operations

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use current working directory as project root (scripts are run from project root)
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Audit log file
AUDIT_LOG="$LOGS_DIR/audit-trail.log"

# Initialize audit log if it doesn't exist
init_audit_log() {
    if [ ! -f "$AUDIT_LOG" ]; then
        echo "# Phase Gate Audit Trail" > "$AUDIT_LOG"
        echo "# Started: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$AUDIT_LOG"
        echo "# Format: [timestamp] operation target details" >> "$AUDIT_LOG"
        echo "" >> "$AUDIT_LOG"
    fi
}

# Log gate operation
log_operation() {
    local operation="$1"
    local target="$2"
    local details="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    init_audit_log
    echo "[$timestamp] $operation $target $details" >> "$AUDIT_LOG"
}

# Log verification attempt
log_verification() {
    local phase="$1"
    local result="$2"
    local details="$3"
    
    log_operation "VERIFY" "phase-$phase" "result=$result $details"
}

# Log completion recording
log_completion() {
    local phase="$1"
    local hash="$2"
    local signature="$3"
    
    log_operation "COMPLETE" "phase-$phase" "hash=$hash signature=$signature"
}

# Log chain verification
log_chain_verification() {
    local start_phase="$1"
    local end_phase="$2"
    local result="$3"
    
    log_operation "CHAIN_VERIFY" "phase-$start_phase-to-$end_phase" "result=$result"
}

# Log tampering detection
log_tampering() {
    local phase="$1"
    local expected_hash="$2"
    local actual_hash="$3"
    
    log_operation "TAMPERING_DETECTED" "phase-$phase" "expected=$expected_hash actual=$actual_hash"
}

# Get recent audit entries
get_recent_audit() {
    local count="${1:-10}"
    
    if [ -f "$AUDIT_LOG" ]; then
        tail -n "$count" "$AUDIT_LOG"
    else
        echo "Audit log not found"
    fi
}

# Get audit entries for specific phase
get_phase_audit() {
    local phase="$1"
    
    if [ -f "$AUDIT_LOG" ]; then
        grep "phase-$phase" "$AUDIT_LOG" || echo "No audit entries found for phase $phase"
    else
        echo "Audit log not found"
    fi
}

# Export functions for use in other scripts
export -f init_audit_log
export -f log_operation
export -f log_verification
export -f log_completion
export -f log_chain_verification
export -f log_tampering
export -f get_recent_audit
export -f get_phase_audit