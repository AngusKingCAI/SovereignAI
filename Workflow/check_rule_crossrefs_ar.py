#!/usr/bin/env python3
"""AR rule cross-reference check: Verify every AR rule ID has corresponding
check script(s) OR is marked Design-time. Supports rules with multiple scripts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def extract_ar_rules_from_architecture(arch_path: Path) -> dict[str, str]:
    """Extract AR rule IDs and their verification status from ARCHITECTURE.md."""
    content = arch_path.read_text(encoding='utf-8')

    # Find the verification table
    table_pattern = r'\| Rule \| Script \| Status \| Note \|\s*\|.*?\n(\|.*?\n)+'
    table_match = re.search(table_pattern, content, re.MULTILINE)
    if not table_match:
        return {}

    rules: dict[str, str] = {}
    for line in table_match.group(0).split('\n'):
        if line.startswith('|') and not line.startswith('| Rule'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 4:
                rule_id = parts[1]
                status = parts[3]
                if rule_id and rule_id != 'Rule':
                    rules[rule_id] = status

    return rules


def get_existing_check_scripts(scripts_dir: Path) -> set[str]:
    """Get set of existing AR check script filenames."""
    if not scripts_dir.exists():
        return set()

    scripts = set()
    for script_file in scripts_dir.glob('*.py'):
        scripts.add(script_file.stem)

    return scripts


def main() -> int:
    """Check AR rule cross-references."""
    repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    arch_path = repo_root / '.agent' / 'executor' / 'ARCHITECTURE.md'
    scripts_dir = repo_root / '.agent' / 'executor' / 'scripts' / 'ar_checks'

    if not arch_path.exists():
        print(f'ARCHITECTURE.md not found: {arch_path}', file=sys.stderr)
        return 1

    ar_rules = extract_ar_rules_from_architecture(arch_path)
    if not ar_rules:
        print('No AR rules found in ARCHITECTURE.md verification table', file=sys.stderr)
        return 1

    existing_scripts = get_existing_check_scripts(scripts_dir)

    orphaned_rules: list[str] = []

    for rule_id, status in ar_rules.items():
        if status == 'Design-time':
            # Design-time rules don't need check scripts
            continue

        if status == '—' or status == '':
            # Check if there's a corresponding script
            # Map rule IDs to script name(s) — rules can have multiple check scripts
            # AR4 has two scripts: no_hardcoded_component_names.py and check_ar4_allowlist.py
            script_mapping = {
                'AR4': ['no_hardcoded_component_names', 'check_ar4_allowlist'],
                'AR8': ['check_tracing'],
                'AR12': ['ui_does_not_touch_core'],
                'AR15': ['check_component_manifest_kwargs'],
                'P11': ['no_context_bags'],
            }

            expected_scripts = script_mapping.get(rule_id, [])
            missing_scripts = [s for s in expected_scripts if s not in existing_scripts]

            if missing_scripts:
                script_list = ', '.join(f'{s}.py' for s in missing_scripts)
                orphaned_rules.append(f'{rule_id} (missing scripts: {script_list})')

    if orphaned_rules:
        print('Orphaned AR rules (no corresponding check scripts):', file=sys.stderr)
        for rule in orphaned_rules:
            print(f'  {rule}', file=sys.stderr)
        return 1

    print(
        'AR rule cross-reference check passed: All AR rules have '
        'corresponding check scripts or are Design-time'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
