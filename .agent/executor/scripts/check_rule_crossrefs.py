#!/usr/bin/env python3
"""Cross-reference check for OR/AR rule citations. Replaces scan/SKILL.md Step 5.5."""

import os
import re
import sys
from pathlib import Path


def extract_rule_numbers(file_path: Path) -> set[str]:
    """Extract all OR and AR rule numbers from a file."""
    if not file_path.exists():
        return set()

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    # Find all patterns: AR\d+, UOR-\d+, VOR-\d+, OOR-\d+, COR-\d+
    matches = re.findall(r'\b(?:AR|UOR|VOR|OOR|COR)-?\d+\b', content)
    return set(matches)


def extract_defined_rules(agents_path: Path) -> set[str]:
    """Extract rule numbers defined in ARCHITECTURE.md and OR_RULES.md."""
    defined_rules = set()

    # Extract AR rules from ARCHITECTURE.md
    architecture_path = agents_path.parent / '.agent' / 'executor' / 'ARCHITECTURE.md'
    if architecture_path.exists():
        with open(architecture_path, encoding='utf-8') as f:
            content = f.read()
        # Only match rules at start of line (e.g., "AR1. Owner ↔ Orchestrator")
        # Also match reserved rules (e.g., "AR16-AR20. Reserved.")
        ar_matches = re.findall(r'^AR\d+\.|^AR\d+-AR\d+\.', content, re.MULTILINE)
        # Extract individual AR numbers from ranges like "AR16-AR20"
        for match in ar_matches:
            if '-' in match:
                # Handle range like "AR16-AR20"
                start, end = re.findall(r'AR(\d+)', match)
                for i in range(int(start), int(end) + 1):
                    defined_rules.add(f"AR{i}")
            else:
                # Extract just the AR number (remove period)
                ar_num = re.match(r'AR(\d+)\.', match)
                if ar_num:
                    defined_rules.add(f"AR{ar_num.group(1)}")
    else:
        print(f"WARNING: {architecture_path} not found, no AR rules defined", file=sys.stderr)

    # Extract OR rules from OR_RULES.md (new naming convention)
    or_rules_path = agents_path.parent / '.agent' / 'executor' / 'OR_RULES.md'
    if or_rules_path.exists():
        with open(or_rules_path, encoding='utf-8') as f:
            content = f.read()
        # Match new naming convention: UOR-1, VOR-1, OOR-1, COR-1
        or_matches = re.findall(r'^### (UOR|VOR|OOR|COR)-(\d+)', content, re.MULTILINE)
        # Convert to expected format for citations
        for prefix, num in or_matches:
            defined_rules.add(f"{prefix}-{num}")
        
        # Also extract retired rules from the Retired Rules table
        # Table format: | Legacy ID | New ID | Status | Notes |
        retired_matches = re.findall(r'^\| ([A-Z]+-\d+) \|', content, re.MULTILINE)
        for retired_id in retired_matches:
            defined_rules.add(retired_id)
    else:
        print(f"WARNING: {or_rules_path} not found, no OR rules defined", file=sys.stderr)

    return defined_rules


def is_historical_section(content: str, line_num: int, file_name: str, file_path: Path) -> bool:
    """Check if a line is in a historical/disclaimer section."""
    lines = content.split('\n')

    # Exempt all log files - they are historical execution logs
    if 'logs' in str(file_path):
        return True

    # Exempt all completed plans - they are historical plans
    if 'completed' in str(file_path):
        return True

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

    return False


def extract_cited_rules_with_exemptions(file_path: Path) -> set[str]:
    """Extract cited rule numbers, excluding historical sections."""
    if not file_path.exists():
        return set()

    # Skip CHANGELOG.md entirely - it documents historical state
    if file_path.name == 'CHANGELOG.md':
        return set()

    with open(file_path, encoding='utf-8') as f:
        content = f.read()

    cited_rules = set()
    lines = content.split('\n')

    for line_num, line in enumerate(lines):
        if is_historical_section(content, line_num, file_path.name, file_path):
            continue

        # Match new naming convention: UOR-1, VOR-1, etc. and old OR\d+, AR\d+
        matches = re.findall(r'\b(?:AR|UOR|VOR|OOR|COR)-?\d+\b', line)
        cited_rules.update(matches)

    return cited_rules


def main(repo_root: Path | None = None):
    if repo_root is None:
        # Check for REPO_ROOT environment variable first
        env_root = os.environ.get('REPO_ROOT')
        if env_root:
            repo_root = Path(env_root)
        else:
            repo_root = Path(__file__).parent.parent.parent.parent

    agents_path = repo_root / 'AGENTS.md'

    # Files to check for citations
    check_files = [
        repo_root / 'AGENTS.md',
        repo_root / '.agent' / 'shared' / 'PLANS.md',
        repo_root / '.agent' / 'shared' / 'DEBT.md',
        repo_root / '.agent' / 'architect' / 'AI_HANDOFF.md',
    ]

    # Add all skill files
    for skill_dir in (repo_root / '.devin' / 'skills').glob('*'):
        skill_file = skill_dir / 'SKILL.md'
        if skill_file.exists():
            check_files.append(skill_file)

    # Add all plan files
    for plan_file in (repo_root / 'prompts').glob('*.md'):
        check_files.append(plan_file)

    # Add all executor scripts
    for script_file in (repo_root / '.agent' / 'executor' / 'scripts').glob('**/*.py'):
        check_files.append(script_file)

    # Extract defined rules from ARCHITECTURE.md and OR_RULES.md
    defined_rules = extract_defined_rules(agents_path)

    # Extract cited rules from all files
    cited_rules = set()
    for file_path in check_files:
        cited_rules.update(extract_cited_rules_with_exemptions(file_path))

    # Find undefined citations
    undefined = cited_rules - defined_rules

    if undefined:
        print(f"ERROR: Undefined rule citations found: {sorted(undefined)}", file=sys.stderr)
        print(f"Defined: {sorted(defined_rules)}, Cited: {sorted(cited_rules)}", file=sys.stderr)
        return 1
    else:
        print(f"OK: All {len(cited_rules)} cited rules are defined")
        return 0


if __name__ == '__main__':
    main()
