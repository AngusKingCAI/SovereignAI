#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path


def main():
    # Get repo root from git to handle different script locations
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, cwd=Path(__file__).parent,
    )
    repo_root = (
        Path(result.stdout.strip()) if result.returncode == 0
        else Path(__file__).parent.parent.parent.parent.parent
    )
    agents_md = repo_root / "AGENTS.md"
    principles_md = repo_root / ".agent" / "architect" / "PRINCIPLES.md"

    if not agents_md.exists():
        print(f"Error: {agents_md} not found", file=sys.stderr)
        sys.exit(1)

    errors = []

    # Check AR/OR rules in AGENTS.md
    with open(agents_md, encoding="utf-8") as f:
        lines = f.readlines()

    rule_pattern = re.compile(r"^(AR\d+|OR\d+|UOR-\d+|VOR-\d+|OOR-\d+|COR-\d+)\. \[Mandatory\]")

    i = 0
    while i < len(lines):
        match = rule_pattern.match(lines[i])
        if match:
            rule_id = match.group(1)
            rule_start = i

            i += 1
            line_count = 1

            while i < len(lines) and not rule_pattern.match(lines[i]):
                if lines[i].strip() and not lines[i].strip().startswith("---"):
                    line_count += 1
                i += 1

            if line_count > 2:
                errors.append(f"{rule_id}: {line_count} lines (max 2)")

            rule_text = lines[rule_start].strip()
            char_count = len(rule_text) - len(rule_id) - 2
            if char_count > 600:
                errors.append(f"{rule_id}: {char_count} chars (hard limit 600)")
            elif char_count > 400:
                pass  # Remove advisory output
        else:
            i += 1

    # Check GR rules in PRINCIPLES.md (GR1-GR15)
    if principles_md.exists():
        with open(principles_md, encoding="utf-8") as f:
            lines = f.readlines()

        gr_pattern = re.compile(r"^(GR\d+)\.\s+")

        i = 0
        while i < len(lines):
            match = gr_pattern.match(lines[i])
            if match:
                rule_id = match.group(1)
                rule_start = i

                i += 1
                line_count = 1

                while i < len(lines) and not gr_pattern.match(lines[i]):
                    if lines[i].strip() and not lines[i].strip().startswith("---"):
                        line_count += 1
                    i += 1

                if line_count > 2:
                    errors.append(f"{rule_id}: {line_count} lines (max 2)")

                rule_text = lines[rule_start].strip()
                char_count = len(rule_text) - len(rule_id) - 2
                if char_count > 600:
                    errors.append(f"{rule_id}: {char_count} chars (hard limit 600)")
                elif char_count > 400:
                    pass  # Remove advisory output
            else:
                i += 1

    if errors:
        print("Rules exceed conciseness limits:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
