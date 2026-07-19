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
        repo_root = Path(env_root) if env_root else Path(__file__).parent.parent.parent.parent

    # Get current plan from PLANS.md (SSOT for active plan and recent history)
    plans_file = repo_root / '.agent' / 'shared' / 'PLANS.md'

    if not plans_file.exists():
        print(f"ERROR: {plans_file} not found", file=sys.stderr)
        sys.exit(1)

    with open(plans_file, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Parse the Active Plan section first
    active_plan_match = re.search(r'## Active Plan\s*\| (.*?) \| (.*?) \|', content, re.MULTILINE)
    if active_plan_match:
        plan_name = active_plan_match.group(1).strip()
        plan_rev = active_plan_match.group(2).strip()
        if plan_name and plan_name != '—':
            # Convert "Plan 25.4" + "Rev 1" to "plan-25.4-Rev1" format
            plan_file_name = plan_name.lower().replace(' ', '-')
            plan_file_name = plan_file_name.replace('plan', 'plan')
            if plan_rev and plan_rev != '—':
                # Convert "Rev 1" to "Rev1" (remove space)
                plan_rev_formatted = plan_rev.replace(' ', '')
                plan_file_name = f"{plan_file_name}-{plan_rev_formatted}"

            # Look for the plan file in prompts/
            plan_path = repo_root / 'prompts' / f'{plan_file_name}.md'
            if plan_path.exists():
                print(plan_path)
                sys.exit(0)

            # Try prompts/completed/
            plan_path = repo_root / 'prompts' / 'completed' / f'{plan_file_name}.md'
            if plan_path.exists():
                print(plan_path)
                sys.exit(0)

    # If no active plan, check Recent History for most recent completed plan
    recent_history_section = re.search(r'## Recent History.*?\n((?:\|.*?\n)+)', content, re.DOTALL)
    if recent_history_section:
        recent_table = recent_history_section.group(1)
        # Get the first row after the header row (skip the header row itself)
        lines = recent_table.split('\n')
        for line in lines:
            if line.startswith('|') and '------' in line:
                # This is the separator row, skip it
                continue
            if line.startswith('|') and line.strip():
                parts = line.split('|')
                # Skip header row: it has "Plan" and "Rev" as column headers
                if len(parts) >= 3 and parts[1].strip() == 'Plan' and parts[2].strip() == 'Rev':
                    continue
                # This is a data row
                if len(parts) >= 3:
                    plan_name = parts[1].strip()
                    plan_rev = parts[2].strip()
                    if plan_name and plan_name != '—':
                        # Convert "Plan 25.4" + "Rev 1" to "plan-25.4-Rev1" format
                        plan_file_name = plan_name.lower().replace(' ', '-')
                        plan_file_name = plan_file_name.replace('plan', 'plan')
                        if plan_rev and plan_rev != '—':
                            # Convert "Rev 1" to "Rev1" (remove space)
                            plan_rev_formatted = plan_rev.replace(' ', '')
                            plan_file_name = f"{plan_file_name}-{plan_rev_formatted}"

                        # Look for the plan file in prompts/completed/
                        plan_path = repo_root / 'prompts' / 'completed' / f'{plan_file_name}.md'
                        if plan_path.exists():
                            print(plan_path)
                            sys.exit(0)
                        else:
                            print(f"ERROR: Plan file not found: {plan_path}", file=sys.stderr)
                            sys.exit(1)

    print("ERROR: No active plan or recent history found in PLANS.md", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
