#!/usr/bin/env python3
"""Get the current plan file. Replaces close/SKILL.md Step 0 ls -v | tail -n 1 pattern."""

import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 1:
        print("Usage: get_current_plan.py", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent.parent.parent
    plans_md = repo_root / '.agent' / 'shared' / 'PLANS.md'

    if not plans_md.exists():
        print(f"ERROR: {plans_md} not found", file=sys.stderr)
        sys.exit(1)

    # Read PLANS.md to get the active plan from the "Active Plan" section
    content = plans_md.read_text(encoding='utf-8')
    
    # Find the "Active Plan" section
    active_plan_match = re.search(r'## Active Plan.*?\| File \| ([^\n]+) \|', content, re.DOTALL)
    if active_plan_match:
        active_plan = active_plan_match.group(1).strip()
        if active_plan == 'None':
            print("No active plan set in PLANS.md", file=sys.stderr)
            sys.exit(1)
        
        # Convert to full path
        active_plan_path = repo_root / active_plan
        if active_plan_path.exists():
            print(active_plan_path)
            sys.exit(0)
        else:
            print(f"ERROR: Active plan file not found: {active_plan_path}", file=sys.stderr)
            sys.exit(1)
    else:
        print("ERROR: Could not find Active Plan section in PLANS.md", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
