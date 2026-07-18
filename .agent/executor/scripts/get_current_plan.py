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

    # Read PLANS.md to get the most recently completed plan
    with open(plans_md, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Find the "Recent Completed" section and extract the first (most recent) plan
    # Look for the table header, separator, then first data row
    recent_completed_match = re.search(
        r'## Recent Completed.*?\n\|.*?\n\|[-|\s]+\n\|\s*(.+?)\s*\|',
        content,
        re.DOTALL,
    )

    if not recent_completed_match:
        print("ERROR: Could not find Recent Completed section in PLANS.md", file=sys.stderr)
        sys.exit(1)

    recent_plan = recent_completed_match.group(1).strip()
    if not recent_plan:
        print("No recent plan found in PLANS.md", file=sys.stderr)
        sys.exit(1)

    # Remove "prompt-" prefix if present (PLANS.md uses prompt- but files don't)
    if recent_plan.startswith('prompt-'):
        recent_plan = recent_plan[7:]  # Remove "prompt-" prefix

    # Convert to full path
    if not recent_plan.startswith('prompts/completed/'):
        recent_plan = f"prompts/completed/{recent_plan}"
    # Add .md extension if not present
    if not recent_plan.endswith('.md'):
        recent_plan = f"{recent_plan}.md"
    recent_plan_path = repo_root / recent_plan
    if recent_plan_path.exists():
        print(recent_plan_path)
        sys.exit(0)
    else:
        print(f"ERROR: Recent plan file not found: {recent_plan_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
