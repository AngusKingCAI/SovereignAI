#!/usr/bin/env python3
"""OR73 enforcement: CHANGELOG append discipline.

Usage: check_changelog.py <plan_number>
Example: check_changelog.py 20.5

Checks:
  1. CHANGELOG.md exists and ends with `## prompt-N — `
     (the newest entry matches the plan number passed as argv[1]).
  2. The newest entry is at the end of the file (no orphan content after).
  3. The newest entry has ≥1 bullet point (`- ` line) before EOF.
  4. No `## prompt-M` entry appears AFTER the newest entry
     (would indicate an out-of-order append).
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

    # Check 1: File ends with header and newest entry matches plan number
    # Check line by line to handle various dash characters
    lines = content.splitlines()
    if len(lines) < 3:
        print("ERROR: CHANGELOG.md has insufficient lines", file=sys.stderr)
        return 1
    if lines[0] != "# CHANGELOG":
        print("ERROR: CHANGELOG.md does not start with '# CHANGELOG'", file=sys.stderr)
        return 1
    
    # Find the last entry (should be at the end)
    last_entry_line = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith("## prompt-"):
            last_entry_line = i
            break
    
    if last_entry_line is None:
        print("ERROR: No prompt entry found in CHANGELOG.md", file=sys.stderr)
        return 1
    
    if not lines[last_entry_line].startswith(f"## prompt-{plan_number}"):
        print(f"ERROR: Last entry does not start with '## prompt-{plan_number}'", file=sys.stderr)
        print(f"Actual: {lines[last_entry_line][:80]}", file=sys.stderr)
        return 1

    # Check 2: No orphan content after newest entry
    if last_entry_line < len(lines) - 1:
        print(f"ERROR: Orphan content after prompt-{plan_number} entry (lines {last_entry_line + 1} to {len(lines)})", file=sys.stderr)
        return 1

    # Check 3: Newest entry has ≥1 bullet point before EOF
    bullet_count = 0
    for line in lines[last_entry_line:]:
        if line.startswith("- "):
            bullet_count += 1

    if bullet_count == 0:
        print(f"ERROR: Entry for prompt-{plan_number} has no bullet points", file=sys.stderr)
        return 1

    # Check 4: No prompt-M entry after newest entry (already covered by check 2)

    print(f"OR73: CHANGELOG entry for prompt-{plan_number} is correctly formatted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
