#!/usr/bin/env python3
"""Get the current plan file. Replaces close/SKILL.md Step 0 ls -v | tail -n 1 pattern."""

import re
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) != 1:
        print("Usage: get_current_plan.py", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent.parent
    plans_md = repo_root / '.agent' / 'shared' / 'PLANS.md'

    if not plans_md.exists():
        print(f"ERROR: {plans_md} not found", file=sys.stderr)
        sys.exit(1)

    # Read PLANS.md to get the active plan from the "Active Plan" section
    with open(plans_md, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find the "Active Plan" section - handle both table format and plain text format
    active_plan_match = re.search(
        r'## Active Plan\s*\n+(.+?)(?:\n+##|\Z)',
        content,
        re.DOTALL,
    )

    if not active_plan_match:
        print("ERROR: Could not find Active Plan section in PLANS.md", file=sys.stderr)
        sys.exit(1)

    active_plan = active_plan_match.group(1).strip()
    if active_plan == 'None' or active_plan == '':
        print("No active plan set in PLANS.md", file=sys.stderr)
        sys.exit(1)

    # If it's a table row, extract the plan name
    if '|' in active_plan:
        # Try to extract from table format
        parts = active_plan.split('|')
        for part in parts:
            if 'plan-' in part:
                active_plan = part.strip()
                break

    # Convert to full path
    if not active_plan.startswith('prompts/'):
        active_plan = f"prompts/{active_plan}"
    # Add .md extension if not present
    if not active_plan.endswith('.md'):
        active_plan = f"{active_plan}.md"
    active_plan_path = repo_root / active_plan
    if active_plan_path.exists():
        print(active_plan_path)
        sys.exit(0)
    else:
        print(f"ERROR: Active plan file not found: {active_plan_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
