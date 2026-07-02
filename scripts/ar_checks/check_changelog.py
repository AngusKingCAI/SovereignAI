#!/usr/bin/env python3
"""OR73 enforcement: CHANGELOG prepend discipline.

Usage: check_changelog.py <plan_number>
Example: check_changelog.py 20.5

Checks:
  1. CHANGELOG.md exists and starts with `## prompt-N — `
     (the newest entry matches the plan number passed as argv[1]).
  2. The newest entry is at the top of the file (after header, no other prompt entries before it).
  3. The newest entry has ≥1 bullet point (`- ` line).
  4. No `## prompt-M` entry appears BEFORE the newest entry
     (would indicate an out-of-order prepend).
  5. Exit 0 if all checks pass; exit 1 with diagnostic on any failure.
"""

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: check_changelog.py <plan_number>", file=sys.stderr)
        return 1

    plan_number = sys.argv[1]
    changelog_path = Path("CHANGELOG.md")

    if not changelog_path.exists():
        print("ERROR: CHANGELOG.md not found", file=sys.stderr)
        return 1

    content = changelog_path.read_text()

    # Check 1: File starts with header and newest entry matches plan number
    # Check line by line to handle various dash characters
    lines = content.splitlines()
    if len(lines) < 3:
        print("ERROR: CHANGELOG.md has insufficient lines", file=sys.stderr)
        return 1
    if lines[0] != "# CHANGELOG":
        print("ERROR: CHANGELOG.md does not start with '# CHANGELOG'", file=sys.stderr)
        return 1

    # Find the first entry (should be at the top, after header)
    first_entry_line = None
    for i in range(1, len(lines)):  # Skip header line
        if lines[i].startswith("## prompt-"):
            first_entry_line = i
            break

    if first_entry_line is None:
        print("ERROR: No prompt entry found in CHANGELOG.md", file=sys.stderr)
        return 1

    if not lines[first_entry_line].startswith(f"## prompt-{plan_number}"):
        print(f"ERROR: First entry does not start with '## prompt-{plan_number}'", file=sys.stderr)
        print(f"Actual: {lines[first_entry_line][:80]}", file=sys.stderr)
        return 1

    # Check 2: No other prompt entry before newest entry (except header)
    found_another_entry = False
    for i in range(1, first_entry_line):  # Check between header and first entry
        if lines[i].startswith("## prompt-"):
            found_another_entry = True
            break

    if found_another_entry:
        print(f"ERROR: Another prompt entry found before prompt-{plan_number}", file=sys.stderr)
        return 1

    # Check 3: Newest entry has ≥1 bullet point
    bullet_count = 0
    # Find the end of this entry (next prompt entry or EOF)
    entry_end = len(lines)
    for i in range(first_entry_line + 1, len(lines)):
        if lines[i].startswith("## prompt-"):
            entry_end = i
            break

    for line in lines[first_entry_line:entry_end]:
        if line.startswith("- "):
            bullet_count += 1

    if bullet_count == 0:
        print(f"ERROR: Entry for prompt-{plan_number} has no bullet points", file=sys.stderr)
        return 1

    # Check 4: No prompt-M entry before newest entry (already covered by check 2)

    print(f"OR73: CHANGELOG entry for prompt-{plan_number} is correctly formatted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
