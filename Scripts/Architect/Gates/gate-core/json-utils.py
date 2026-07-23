#!/usr/bin/env python3
"""
JSON utilities for Phase Gate System
Python alternative to jq for JSON processing
"""

import json
import sys

def read_json_file(file_path):
    """Read and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        return None

def write_json_file(file_path, data):
    """Write data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing JSON file: {e}", file=sys.stderr)
        return False

def get_json_value(data, key):
    """Get value from JSON data by key"""
    if isinstance(data, dict):
        return data.get(key)
    return None

def set_json_value(data, key, value):
    """Set value in JSON data"""
    if isinstance(data, dict):
        data[key] = value
        return data
    return data

def validate_json(data):
    """Validate JSON structure"""
    if not isinstance(data, dict):
        return False, "Not a JSON object"
    return True, "Valid JSON"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: json-utils.py <command> [args...]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "read":
        if len(sys.argv) < 3:
            print("Usage: json-utils.py read <file>")
            sys.exit(1)
        data = read_json_file(sys.argv[2])
        if data:
            print(json.dumps(data, indent=2))
    
    elif command == "get":
        if len(sys.argv) < 4:
            print("Usage: json-utils.py get <file> <key>")
            sys.exit(1)
        data = read_json_file(sys.argv[2])
        if data:
            value = get_json_value(data, sys.argv[3])
            print(value if value is not None else "null")
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Usage: json-utils.py validate <file>")
            sys.exit(1)
        data = read_json_file(sys.argv[2])
        if data:
            valid, message = validate_json(data)
            print(f"Valid: {valid} - {message}")
            sys.exit(0 if valid else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)