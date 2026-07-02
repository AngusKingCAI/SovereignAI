#!/usr/bin/env python3
"""Get the current plan file. Replaces close/SKILL.md Step 0 ls -v | tail -n 1 pattern."""

import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 1:
        print("Usage: get_current_plan.py", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).parent.parent
    prompts_dir = repo_root / 'prompts'
    completed_dir = prompts_dir / 'completed'

    if not prompts_dir.exists():
        print(f"ERROR: {prompts_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Find all plan-{N}-Rev*.md files in prompts/ (active plans)
    plan_files = list(prompts_dir.glob('plan-*-Rev*.md'))

    # If no active plans, look in completed/ (for /close skill)
    if not plan_files and completed_dir.exists():
        plan_files = list(completed_dir.glob('plan-*-Rev*.md'))

    if not plan_files:
        print("ERROR: No plan files found matching pattern plan-*-Rev*.md", file=sys.stderr)
        sys.exit(1)

    # Sort by plan number numerically, not alphabetically
    def extract_plan_number(filepath):
        """Extract plan number from filename for numeric sorting."""
        match = re.search(r'plan-(\d+(?:\.\d+)*)', filepath.name)
        if match:
            # Convert to tuple for proper numeric comparison (major, minor)
            parts = match.group(1).split('.')
            return tuple(int(p) for p in parts)
        return (0, 0)

    plan_files.sort(key=extract_plan_number)

    # Return the last one (highest plan number)
    current_plan = plan_files[-1]
    print(current_plan)
    sys.exit(0)


if __name__ == '__main__':
    main()
