#!/usr/bin/env python3
"""append_trace.py — append skill invocation to execution trace.

Usage: python append_trace.py --skill <skill_name> --plan <plan_id>

Appends a structured JSON line to .agent/executor/traces/trace-plan-{N}.jsonl
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", required=True)
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()

    plan_id = args.plan
    skill_name = args.skill

    trace_dir = ".agent/executor/traces"
    os.makedirs(trace_dir, exist_ok=True)

    trace_path = f"{trace_dir}/trace-plan-{plan_id}.jsonl"

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plan_id": plan_id,
        "action": "skill_invoke",
        "skill": skill_name,
        "result": "invoked"
    }

    with open(trace_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"TRACE: {skill_name} logged to {trace_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
