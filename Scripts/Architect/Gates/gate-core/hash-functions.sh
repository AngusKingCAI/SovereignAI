#!/bin/bash

# Hash Functions for Phase Gate System
# Core cryptographic operations for state verification

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Use current working directory as project root (scripts are run from project root)
PROJECT_ROOT="$(pwd)"
LOGS_DIR="$PROJECT_ROOT/Logs/Architect/Gates"

# Ensure logs directory exists
mkdir -p "$LOGS_DIR"

# Generate SHA-256 hash of a file
generate_file_hash() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi
    sha256sum "$file" | awk '{print $1}'
}

# Generate SHA-256 hash of a string
generate_string_hash() {
    local string="$1"
    echo -n "$string" | sha256sum | awk '{print $1}'
}

# Generate hash of directory contents (recursive)
generate_directory_hash() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "Error: Directory not found: $dir" >&2
        return 1
    fi
    
    # Find all files, sort them, and generate combined hash
    find "$dir" -type f -exec sha256sum {} + | sort | sha256sum | awk '{print $1}'
}

# Generate hash of multiple files
generate_multi_file_hash() {
    local files=("$@")
    
    if [ ${#files[@]} -eq 0 ]; then
        echo "Error: No files provided" >&2
        return 1
    fi
    
    # Check all files exist
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "Error: File not found: $file" >&2
            return 1
        fi
    done
    
    # Generate combined hash
    sha256sum "${files[@]}" | sort | sha256sum | awk '{print $1}'
}

# Verify hash matches expected value
verify_hash() {
    local file="$1"
    local expected_hash="$2"
    
    local actual_hash=$(generate_file_hash "$file")
    
    if [ "$actual_hash" = "$expected_hash" ]; then
        echo "Hash verification passed for: $file"
        return 0
    else
        echo "Hash verification FAILED for: $file" >&2
        echo "Expected: $expected_hash" >&2
        echo "Actual:   $actual_hash" >&2
        return 1
    fi
}

# Log hash operation
log_hash_operation() {
    local operation="$1"
    local target="$2"
    local hash="$3"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    echo "[$timestamp] $operation: $target -> $hash" >> "$LOGS_DIR/audit-trail.log"
}

# Export functions for use in other scripts
export -f generate_file_hash
export -f generate_string_hash
export -f generate_directory_hash
export -f generate_multi_file_hash
export -f verify_hash
export -f log_hash_operation