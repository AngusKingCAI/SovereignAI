#!/usr/bin/env python3
"""Check AR4 main.py exemption allowlist diff. Replaces close/SKILL.md Step 11 awk/grep pipeline."""

import re
import subprocess
import sys
from pathlib import Path


def extract_allowlist(content: str) -> set[str]:
    """Extract WEB_MAIN_ALLOWED_IMPORTS entries from file content."""
    entries = set()
    in_section = False

    for line in content.split('\n'):
        if 'WEB_MAIN_ALLOWED_IMPORTS' in line:
            in_section = True
            continue

        if in_section:
            if line.strip() in {'}', ']', ')', ''}:
                break
            # Extract quoted strings
            matches = re.findall(r'"([^"]+)"', line)
            entries.update(matches)

    return entries


def get_git_file_content(commit: str, file_path: Path) -> str:
    """Get file content from a specific git commit."""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit}:{file_path}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception:
        return ""


def main():
    if len(sys.argv) != 3:
        print("Usage: check_ar4_allowlist.py <previous_commit> <file_path>", file=sys.stderr)
        sys.exit(1)

    previous_commit = sys.argv[1]
    file_path = Path(sys.argv[2])

    if not file_path.exists():
        print(f"ERROR: {file_path} not found", file=sys.stderr)
        sys.exit(1)

    # Get current content
    with open(file_path, encoding='utf-8') as f:
        current_content = f.read()

    # Get previous content
    previous_content = get_git_file_content(previous_commit, file_path)

    if not previous_content:
        print(f"WARNING: Could not get {file_path} from commit {previous_commit}", file=sys.stderr)
        sys.exit(0)

    # Extract allowlists
    previous_entries = extract_allowlist(previous_content)
    current_entries = extract_allowlist(current_content)

    # Find new entries
    new_entries = current_entries - previous_entries

    if new_entries:
        print(f"ERROR: Unapproved AR4 allowlist additions: {sorted(new_entries)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("OK: No unapproved AR4 allowlist additions")
        sys.exit(0)


if __name__ == '__main__':
    main()
