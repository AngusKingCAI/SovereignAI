#!/usr/bin/env python3
"""Cross-reference check for OR/AR rule citations. Replaces scan/SKILL.md Step 5.5."""

import re
import sys
from pathlib import Path


def extract_rule_numbers(file_path: Path) -> set[str]:
    """Extract all OR and AR rule numbers from a file."""
    if not file_path.exists():
        return set()

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # Find all OR\d+ and AR\d+ patterns (uppercase only, followed by digits)
    matches = re.findall(r'\b(?:OR|AR)\d+\b', content)
    return set(matches)


def extract_defined_rules(agents_path: Path) -> set[str]:
    """Extract rule numbers defined in ARCHITECTURE.md (must be at start of line)."""
    architecture_path = agents_path.parent / '.agent' / 'shared' / 'ARCHITECTURE.md'
    
    if not architecture_path.exists():
        print(f"WARNING: {architecture_path} not found, no AR rules defined", file=sys.stderr)
        return set()

    with open(architecture_path, encoding='utf-8') as f:
        content = f.read()

    # Only match rules at start of line (e.g., "AR1. Owner ↔ Orchestrator")
    matches = re.findall(r'^((?:OR|AR)\d+)\.', content, re.MULTILINE)
    return set(matches)


def is_historical_section(content: str, line_num: int, file_name: str) -> bool:
    """Check if a line is in a historical/disclaimer section."""
    lines = content.split('\n')

    # Check for disclaimer markers before this line
    for i in range(max(0, line_num - 10), line_num):
        if 'historical' in lines[i].lower() or 'disclaimer' in lines[i].lower():
            return True

    # File-specific exemptions
    if file_name == 'PLANS.md':
        # Check if in "Completed Prompts" table
        for i in range(max(0, line_num - 20), line_num):
            if 'completed prompts' in lines[i].lower():
                return True

    return file_name == 'CHANGELOG.md'


def extract_cited_rules_with_exemptions(file_path: Path) -> set[str]:
    """Extract cited rule numbers, excluding historical sections."""
    if not file_path.exists():
        return set()

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    cited_rules = set()
    lines = content.split('\n')

    for line_num, line in enumerate(lines):
        if is_historical_section(content, line_num, file_path.name):
            continue

        matches = re.findall(r'\b(?:OR|AR)\d+\b', line)
        cited_rules.update(matches)

    return cited_rules


def main():
    repo_root = Path(__file__).parent.parent.parent.parent

    agents_path = repo_root / 'AGENTS.md'

    # Files to check for citations
    check_files = [
        repo_root / '.agent' / 'shared' / 'PLANS.md',
        repo_root / '.agent' / 'shared' / 'DEBT.md',
        repo_root / '.agent' / 'shared' / 'DECISIONS.md',
        repo_root / '.agent' / 'architect' / 'AI_HANDOFF.md',
    ]

    # Extract defined AR rules from ARCHITECTURE.md
    defined_rules = extract_defined_rules(agents_path)
    
    # Extract defined OR rules from skills
    skills_dir = repo_root / '.devin' / 'skills'
    if skills_dir.exists():
        for skill_file in skills_dir.glob('*/SKILL.md'):
            with open(skill_file, encoding='utf-8') as f:
                content = f.read()
            # Match OR rules at start of line in skill files
            or_matches = re.findall(r'^(OR\d+)\.', content, re.MULTILINE)
            defined_rules.update(or_matches)

    # Extract cited rules from all files
    cited_rules = set()
    for file_path in check_files:
        cited_rules.update(extract_cited_rules_with_exemptions(file_path))

    # Find undefined citations
    undefined = cited_rules - defined_rules

    if undefined:
        print(f"ERROR: Undefined rule citations found: {sorted(undefined)}", file=sys.stderr)
        print(f"Defined: {sorted(defined_rules)}, Cited: {sorted(cited_rules)}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"OK: All {len(cited_rules)} cited rules are defined in AGENTS.md")
        sys.exit(0)


if __name__ == '__main__':
    main()
