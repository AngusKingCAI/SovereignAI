#!/usr/bin/env python3
"""OR73 enforcement: CHANGELOG prepend discipline.

Usage: check_changelog.py <plan_number>
Example: check_changelog.py 20.5

Checks:
  1. CHANGELOG.md exists and starts with `# CHANGELOG\n\n## prompt-N — `
     (the newest entry matches the plan number passed as argv[1]).
  2. The newest entry is immediately below the `# CHANGELOG` header
     (no orphan content between).
  3. The newest entry has ≥1 bullet point (`- ` line) before the next
     `## ` header or EOF.
  4. No `## prompt-M` entry appears ABOVE the newest entry
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
    if lines[1] != "":
        print("ERROR: Second line should be blank", file=sys.stderr)
        return 1
    if not lines[2].startswith(f"## prompt-{plan_number}"):
        print(f"ERROR: Third line does not start with '## prompt-{plan_number}'", file=sys.stderr)
        print(f"Actual: {lines[2][:80]}", file=sys.stderr)
        return 1

    # Check 2: No orphan content between header and newest entry (already covered by check 1)

    # Check 3: Newest entry has ≥1 bullet point before next header or EOF
    bullet_count = 0

    for line in lines[3:]:  # Start after the header line
        if line.startswith("- "):
            bullet_count += 1
        elif line.startswith("## "):
            break

    if bullet_count == 0:
        print(f"ERROR: Entry for prompt-{plan_number} has no bullet points", file=sys.stderr)
        return 1

    # Check 4: No prompt-M entry above newest entry (already covered by check 1)

    print(f"OR73: CHANGELOG entry for prompt-{plan_number} is correctly formatted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
