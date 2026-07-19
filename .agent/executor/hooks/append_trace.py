#!/usr/bin/env python3
"""append_trace.py — append action to execution trace.

Usage:
  python append_trace.py --skill <skill_name> --plan <plan_id>
  python append_trace.py --action file_edit --file <path> --plan <plan_id>
  python append_trace.py --action file_write --file <path> --plan <plan_id>
  python append_trace.py --action file_delete --file <path> --plan <plan_id>

Appends a structured JSON line to .agent/executor/traces/trace-plan-{N}.jsonl
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


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

    # Build entry based on action type
    if args.skill and not args.action:
        # Legacy mode: skill invocation
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": plan_id,
            "action": "skill_invoke",
            "skill": args.skill,
            "result": "invoked"
        }
        print(f"TRACE: {args.skill} logged to {trace_path}")
    elif args.action:
        # New mode: file action
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "plan_id": plan_id,
            "action": args.action,
            "file": args.file,
            "result": "completed"
        }
        print(f"TRACE: {args.action} on {args.file} logged to {trace_path}")
    else:
        print("ERROR: Must specify --skill or --action")
        sys.exit(1)

    with open(trace_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
