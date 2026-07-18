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

    # Read PLANS.md to get the current plan
    with open(plans_md, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # First, check for "Active Plan" section
    active_plan_match = re.search(
        r'## Active Plan.*?\n(.*?)(?=\n##|$)',
        content,
        re.DOTALL,
    )

    if active_plan_match:
        active_plan = active_plan_match.group(1).strip()
        if active_plan and active_plan != "None.":
            # Extract plan name from active plan line
            plan_match = re.search(r'prompt-([^\s—]+)', active_plan)
            if plan_match:
                plan_name = plan_match.group(1)
                plan_path = repo_root / 'prompts' / f'{plan_name}.md'
                if plan_path.exists():
                    print(plan_path)
                    sys.exit(0)

    # Fall back to "Recent Completed" section if no active plan
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

    # Convert to full path for completed plans
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
        # Try looking in prompts/ directory (for active plans)
        active_plan_path = repo_root / 'prompts' / recent_plan.replace('prompts/completed/', '')
        if active_plan_path.exists():
            print(active_plan_path)
            sys.exit(0)
        print(f"ERROR: Recent plan file not found: {recent_plan_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
