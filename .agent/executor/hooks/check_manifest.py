#!/usr/bin/env python3
"""check_manifest.py — verify file write is in-scope for current plan phase.

Usage: python check_manifest.py --file <file_path> --plan <plan_id>

Blocks writes to:
- Governance files (always)
- Files outside current phase deliverables (if manifest loaded)

Exit 0 = allow, Exit 1 = block
"""

import argparse
import os
import re
import sys


def load_manifest(plan_id):
    """Load Executor Manifest from plan file."""
    plan_path = f"prompts/plan-{plan_id}.md"
    if not os.path.exists(plan_path):
        return None

    with open(plan_path) as f:
        content = f.read()

    match = re.search(r"## Executor Manifest\n(.*?)(?=\n## |\Z)", content, re.DOTALL)
    if not match:
        return None

    manifest_text = match.group(1)
    deliverables = []

    for line in manifest_text.split("\n"):
        line = line.strip()
        if line.startswith("- S") and ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                file_part = parts[1].strip()
                file_match = re.search(r"`([^`]+)`", file_part)
                if file_match:
                    deliverables.append(file_match.group(1))
                else:
                    first_word = file_part.split()[0]
                    if "." in first_word:
                        deliverables.append(first_word)

    return {"deliverables": deliverables}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--plan", required=False)
    args = parser.parse_args()

    file_path = args.file
    plan_id = args.plan

    # Fallback: read plan_id from .agent/current_plan.txt if not provided
    if not plan_id:
        try:
            with open(".agent/current_plan.txt") as f:
                plan_id = f.read().strip()
        except FileNotFoundError:
            print("ERROR: plan_id not provided and .agent/current_plan.txt not found")
            sys.exit(1)

    # Always block governance files and architect directory
    gov_patterns = [
        ".agent/executor/ARCHITECTURE.md",
        ".agent/executor/OR_RULES.md",
        "PRINCIPLES.md",
        ".agent/architect/AI_HANDOFF.md",
        ".agent/shared/LANDMINES.md",
        ".agent/architect/",
    ]

    for gov in gov_patterns:
        if file_path.startswith(gov) or file_path.endswith(gov) or gov in file_path:
            print(f"BLOCK: Governance file write prohibited: {file_path}")
            sys.exit(1)

    # Load manifest and check scope
    manifest = load_manifest(plan_id)
    if manifest:
        allowed_prefixes = [
            ".agent/executor/traces/",
            ".agent/executor/scripts/",
            ".agent/executor/hooks/",
            "logs/",
            "tests/",
            ".agent/executor/tests/",
        ]

        is_allowed = False
        for d in manifest["deliverables"]:
            if file_path == d or file_path.endswith(d):
                is_allowed = True
                break

        for prefix in allowed_prefixes:
            if file_path.startswith(prefix):
                is_allowed = True
                break

        if file_path.startswith("app/"):
            is_allowed = True

        if not is_allowed:
            # Intentional: out-of-scope files allowed with warning to support exploratory work
            print(f"WARN: File {file_path} not in manifest deliverables for plan {plan_id}")

    print(f"ALLOW: {file_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
