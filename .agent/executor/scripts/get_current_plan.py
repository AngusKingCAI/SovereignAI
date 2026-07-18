#!/usr/bin/env python3
"""Get the current plan file. Replaces close/SKILL.md Step 0 ls -v | tail -n 1 pattern."""

import os
import re
import sys
from pathlib import Path


def main(repo_root: Path | None = None) -> None:
    if len(sys.argv) != 1:
        print("Usage: get_current_plan.py", file=sys.stderr)
        sys.exit(1)

    if repo_root is None:
        # Check for REPO_ROOT environment variable first
        env_root = os.environ.get('REPO_ROOT')
        if env_root:
            repo_root = Path(env_root)
        else:
            repo_root = Path(__file__).parent.parent.parent.parent
    
    # Use CHANGELOG as source of truth (per verify_close.py)
    changelog = repo_root / '.agent' / 'shared' / 'CHANGELOG.md'

    if not changelog.exists():
        print(f"ERROR: {changelog} not found", file=sys.stderr)
        sys.exit(1)

    # Read CHANGELOG to get the current plan
    with open(changelog, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract the first (most recent) plan from the first header
    first_header_match = re.search(r'^## (prompt-[\w-]+)', content, re.MULTILINE)
    if first_header_match:
        current_plan = first_header_match.group(1)  # Keep the full "prompt-22-rev16" format
        # Convert "prompt-22-rev16" to "plan-22-rev16" for file lookup
        current_plan_file = current_plan.replace("prompt-", "plan-")
        
        # Look for the plan file in completed/ first (most recent completed plans), then prompts/ (active)
        plan_path = repo_root / 'prompts' / 'completed' / f'{current_plan_file}.md'
        if plan_path.exists():
            print(plan_path)
            sys.exit(0)
        
        # Try prompts/ (active plans)
        plan_path = repo_root / 'prompts' / f'{current_plan_file}.md'
        if plan_path.exists():
            print(plan_path)
            sys.exit(0)
        
        print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(1)
    
    print("ERROR: No plan found in CHANGELOG", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
