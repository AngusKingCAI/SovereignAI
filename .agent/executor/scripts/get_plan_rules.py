#!/usr/bin/env python3
"""Extract only the rules referenced in current plan.

Loads only relevant rules instead of entire ruleset.
Reduces context by 40-60%.

Usage: python get_plan_rules.py
"""
import json
import re
import sys
from pathlib import Path


def get_plan_rules(plan_file):
    """Extract AR/OR rule IDs mentioned in plan header."""
    with open(plan_file) as f:
        content = f.read()

    # Look for rule references in header (first 1500 chars typically)
    header = content[:1500]
    rules = set()

    for match in re.finditer(r'\b(AR\d+|UOR-\d+|VOR-\d+|COR-\d+|SOR-\d+)\b', header):
        rules.add(match.group(1))

    return sorted(rules)


def get_current_plan(repo_root: Path) -> Path | None:
    """Get current plan file using same logic as get_current_plan.py."""
    plans_file = repo_root / '.agent' / 'shared' / 'PLANS.md'

    if not plans_file.exists():
        return None

    with open(plans_file, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Parse the Active Plan section first
    active_plan_match = re.search(
        r'## Active Plan.*?\n\|.*?\n\| (.*?) \| (.*?) \|', content, re.DOTALL
    )
    if active_plan_match:
        plan_name = active_plan_match.group(1).strip()
        plan_rev = active_plan_match.group(2).strip()
        if plan_name and plan_name != '—':
            # Convert "Plan 25.4" + "Rev 1" to "plan-25.4-Rev1" format
            plan_file_name = plan_name.lower().replace(' ', '-')
            if plan_rev and plan_rev != '—':
                plan_rev_formatted = plan_rev.replace(' ', '')
                plan_file_name = f"{plan_file_name}-{plan_rev_formatted}"

            # Look for the plan file in plans/
            plan_path = repo_root / 'plans' / f'{plan_file_name}.md'
            if plan_path.exists():
                return plan_path

            # Try plans/completed/ with subdirectories
            completed_dir = repo_root / 'plans' / 'completed'
            plan_path = completed_dir / f'{plan_file_name}.md'
            if plan_path.exists():
                return plan_path

            for subdir in ['0-9', '10-19', '20-29', '30-39', 'Misc']:
                plan_path = completed_dir / subdir / f'{plan_file_name}.md'
                if plan_path.exists():
                    return plan_path

    return None


def main():
    repo_root = Path.cwd()

    # Get current plan using same logic as get_current_plan.py
    plan_file = get_current_plan(repo_root)
    if not plan_file:
        # No current plan, return empty
        print("[]")
        return 0

    rules = get_plan_rules(plan_file)
    print(json.dumps(rules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
