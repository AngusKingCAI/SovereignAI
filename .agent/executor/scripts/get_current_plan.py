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
    prompts_dir = repo_root / 'prompts'

    if not prompts_dir.exists():
        print(f"ERROR: {prompts_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Find all plan-{N}-Rev*.md files in prompts/ (active plans only)
    plan_files = list(prompts_dir.glob('plan-*-Rev*.md'))

    if not plan_files:
        print(
            "ERROR: No active plan files found in prompts/ "
            "matching pattern plan-*-Rev*.md",
            file=sys.stderr,
        )
        sys.exit(1)

    # Sort by plan number numerically (lowest first), then by revision number (highest first)
    def extract_plan_info(filepath):
        """Extract plan number and revision from filename for proper sorting."""
        match = re.search(r'plan-(\d+(?:\.\d+)*)-rev(\d+)', filepath.name, re.IGNORECASE)
        if match:
            # Convert to tuple for proper numeric comparison (plan_parts, revision)
            plan_parts = match.group(1).split('.')
            plan_tuple = tuple(int(p) for p in plan_parts)
            revision = int(match.group(2))
            # Negate revision so higher revisions sort first
            return (plan_tuple, -revision)
        return ((0, 0), 0)

    plan_files.sort(key=extract_plan_info)

    # Return the first one (lowest plan number, then highest revision)
    current_plan = plan_files[0]
    print(current_plan)
    sys.exit(0)


if __name__ == '__main__':
    main()
