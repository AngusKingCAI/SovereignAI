#!/usr/bin/env python3
"""Get the current plan file. Replaces close/SKILL.md Step 0 ls -v | tail -n 1 pattern."""

import sys
from pathlib import Path


def main():
    if len(sys.argv) != 1:
        print("Usage: get_current_plan.py", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    prompts_dir = repo_root / 'prompts'

    if not prompts_dir.exists():
        print(f"ERROR: {prompts_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Find all plan-{N}-Rev*.md files
    plan_files = sorted(prompts_dir.glob('plan-*-Rev*.md'))

    if not plan_files:
        print("ERROR: No plan files found matching pattern plan-*-Rev*.md", file=sys.stderr)
        sys.exit(1)

    # Return the last one (highest version)
    current_plan = plan_files[-1]
    print(current_plan)
    sys.exit(0)


if __name__ == '__main__':
    main()
