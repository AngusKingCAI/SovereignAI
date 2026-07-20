#!/usr/bin/env python3
"""Plan rule reference validator: Validate that AR/OR rules referenced in plan exist.

Usage: python check_plan_rule_refs.py --plan <plan_id>

Validates that AR and OR rule IDs referenced in plan header actually exist in
ARCHITECTURE.md and OR_RULES.md. Prevents plans from referencing retired/superseded rules.

Exit 0 = all references valid, Exit 1 = invalid references found.
"""

import json
import re
import sys
from pathlib import Path


def extract_defined_rules(repo_root: Path) -> set[str]:
    """Extract rule numbers defined in ARCHITECTURE.md and OR_RULES.md."""
    defined_rules = set()

    # Extract AR rules from ARCHITECTURE.md
    architecture_path = repo_root / '.agent' / 'executor' / 'ARCHITECTURE.md'
    if architecture_path.exists():
        with open(architecture_path, encoding='utf-8') as f:
            content = f.read()
        # Match rules at start of line (e.g., "AR1. Owner ↔ Orchestrator")
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
    or_rules_path = repo_root / '.agent' / 'executor' / 'OR_RULES.md'
    if or_rules_path.exists():
        with open(or_rules_path, encoding='utf-8') as f:
            content = f.read()
        # Match new naming convention: UOR-1, VOR-1, OOR-1, COR-1, SOR-1
        or_matches = re.findall(r'^### (UOR|VOR|OOR|COR|SOR)-(\d+)', content, re.MULTILINE)
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


def extract_plan_rule_references(plan_file: Path) -> set[str]:
    """Extract AR/OR rule IDs referenced in plan header."""
    if not plan_file.exists():
        return set()

    with open(plan_file) as f:
        content = f.read()

    # Look for rule references in header (first 1500 chars typically)
    header = content[:1500]
    rules = set()

    for match in re.finditer(r'\b(AR\d+|UOR-\d+|VOR-\d+|COR-\d+|SOR-\d+)\b', header):
        rules.add(match.group(1))

    return rules


def validate_plan_rule_refs(plan_id: str, repo_root: Path | None = None) -> tuple[bool, str]:
    """Validate that rule references in plan exist in governance files.
    
    Returns (is_valid, message) - False if invalid references found.
    """
    if repo_root is None:
        repo_root = Path.cwd()

    # Find plan file
    plan_pattern = f"plan-{plan_id}*.md"
    plan_files = list((repo_root / 'plans').glob(plan_pattern))
    
    if not plan_files:
        # Try in completed/ subdirectories
        completed_dir = repo_root / 'plans' / 'completed'
        for subdir in ['0-9', '10-19', '20-29', '30-39', 'Misc']:
            subdir_path = completed_dir / subdir
            if subdir_path.exists():
                plan_files = list(subdir_path.glob(plan_pattern))
                if plan_files:
                    break
    
    if not plan_files:
        return False, f"Plan file not found: plan-{plan_id}*.md"
    
    # Sort by revision number if present
    def extract_revision(filename: Path) -> int:
        match = re.search(r'Rev(\d+)', str(filename))
        if match:
            return int(match.group(1))
        return 0
    
    plan_files.sort(key=extract_revision, reverse=True)
    plan_path = plan_files[0]

    # Extract rule references from plan
    plan_rules = extract_plan_rule_references(plan_path)
    
    if not plan_rules:
        return True, "No rule references found in plan (validation skipped)"

    # Extract defined rules from governance files
    defined_rules = extract_defined_rules(repo_root)
    
    # Find undefined references
    undefined_refs = plan_rules - defined_rules
    
    if undefined_refs:
        undefined_list = sorted(undefined_refs)
        return False, f"Invalid rule references in plan: {undefined_list}. These rules do not exist in ARCHITECTURE.md or OR_RULES.md."
    
    return True, f"All {len(plan_rules)} rule references are valid"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, help="Plan ID to validate")
    args = parser.parse_args()

    is_valid, message = validate_plan_rule_refs(args.plan)
    
    if is_valid:
        print(f"PASS: {message}")
        return 0
    else:
        print(f"FAIL: {message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())