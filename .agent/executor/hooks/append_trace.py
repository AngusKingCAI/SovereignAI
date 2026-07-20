#!/usr/bin/env python3
"""append_trace.py — append action to execution trace with integrity hashing.

Usage:
  python append_trace.py --skill <skill_name> --plan <plan_id>
  python append_trace.py --action file_edit --file <path> --plan <plan_id>
  python append_trace.py --action file_write --file <path> --plan <plan_id>
  python append_trace.py --action file_delete --file <path> --plan <plan_id>

Appends a structured JSON line to .agent/executor/traces/trace-plan-{N}.jsonl
with cryptographic chain for tamper detection and schema versioning for migration.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import UTC, datetime

TRACE_SCHEMA_VERSION = "1.0"


def get_previous_entry_hash(trace_path: str) -> str:
    """Get the entry_hash of the last entry in the trace file."""
    if not os.path.exists(trace_path):
        return ""  # No previous entry for first entry
    
    try:
        with open(trace_path, "r") as f:
            lines = f.readlines()
        
        if not lines:
            return ""
        
        # Get the last non-empty line
        last_line = None
        for line in reversed(lines):
            if line.strip():
                last_line = line.strip()
                break
        
        if not last_line:
            return ""
        
        entry = json.loads(last_line)
        return entry.get("entry_hash", "")
    except (json.JSONDecodeError, IOError):
        return ""


def compute_entry_hash(entry: dict) -> str:
    """Compute SHA256 hash of entry excluding the entry_hash field itself."""
    # Create a copy without entry_hash to avoid self-reference
    entry_copy = entry.copy()
    entry_copy.pop("entry_hash", None)
    
    # Convert to JSON string with sorted keys for consistency
    entry_str = json.dumps(entry_copy, sort_keys=True)
    
    return hashlib.sha256(entry_str.encode()).hexdigest()


def add_integrity_fields(entry: dict, prev_hash: str) -> dict:
    """Add integrity fields to trace entry."""
    entry["schema_version"] = TRACE_SCHEMA_VERSION
    entry["prev_hash"] = prev_hash
    
    # Compute hash of entry (will be updated after this assignment)
    entry_hash = compute_entry_hash(entry)
    entry["entry_hash"] = entry_hash
    
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", help="Skill name (for skill_invoke action)")
    parser.add_argument("--plan", required=False)
    parser.add_argument("--action", choices=["skill", "file_write", "file_edit", "file_delete"],
                       help="Action type")
    parser.add_argument("--file", help="File path (for file actions)")
    args = parser.parse_args()

    plan_id = args.plan

    # Fallback: read plan_id from .agent/current_plan.txt if not provided
    if not plan_id:
        try:
            with open(".agent/current_plan.txt") as f:
                plan_id = f.read().strip()
        except FileNotFoundError:
            print("ERROR: plan_id not provided and .agent/current_plan.txt not found")
            sys.exit(1)

    trace_dir = ".agent/executor/traces"
    os.makedirs(trace_dir, exist_ok=True)

    trace_path = f"{trace_dir}/trace-plan-{plan_id}.jsonl"

    # Get previous entry hash for chain integrity
    prev_hash = get_previous_entry_hash(trace_path)

    # Build entry based on action type
    if args.skill and not args.action:
        # Legacy mode: skill invocation
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "plan_id": plan_id,
            "action": "skill_invoke",
            "skill": args.skill,
            "result": "invoked"
        }
        print(f"TRACE: {args.skill} logged to {trace_path}")
    elif args.action:
        # New mode: file action
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "plan_id": plan_id,
            "action": args.action,
            "file": args.file,
            "result": "completed"
        }
        print(f"TRACE: {args.action} on {args.file} logged to {trace_path}")
    else:
        print("ERROR: Must specify --skill or --action")
        sys.exit(1)

    # Add integrity fields (schema_version, prev_hash, entry_hash)
    entry = add_integrity_fields(entry, prev_hash)

    with open(trace_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
