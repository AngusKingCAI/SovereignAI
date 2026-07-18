#!/usr/bin/env python3
"""
Migrate legacy OR IDs to new naming scheme.

Mapping:
- OR17 → UOR-1 (Deliverables Ship in Full)
- OR19 → UOR-2 (Test/Static Analysis Failures)
- OR29 → COR-1 (Test-Fix Plans Run Full Suite)
- OR48 → [RETIRED]
- OR61 → [RETIRED]
- OR63 → UOR-3 (diskcache CVE Monitoring)
- OR65 → [RETIRED]
"""

import re
from pathlib import Path

# Mapping of legacy OR IDs to new IDs
LEGACY_TO_NEW = {
    "OR17": "UOR-1",
    "OR19": "UOR-2",
    "OR29": "COR-1",
    "OR48": "[RETIRED]",
    "OR61": "[RETIRED]",
    "OR63": "UOR-3",
    "OR65": "[RETIRED]",
}

# Files to process
TARGET_FILES = [
    "CHANGELOG.md",
    "DEBT.md",
    "DECISIONS.md",
]


def find_target_files(repo_root: Path) -> list[Path]:
    """Find all target files to process."""
    files = []

    # Add specific shared files
    for filename in TARGET_FILES:
        path = repo_root / ".agent" / "shared" / filename
        if path.exists():
            files.append(path)

    # Add all SKILL.md files
    for skill_dir in (repo_root / ".devin" / "skills").glob("*"):
        skill_file = skill_dir / "SKILL.md"
        if skill_file.exists():
            files.append(skill_file)

    # Add all plan files
    for plan_file in (repo_root / "prompts").glob("*.md"):
        files.append(plan_file)

    # Add all log files
    for log_file in (repo_root / "logs").glob("*.md"):
        files.append(log_file)

    return sorted(files)


def migrate_file(file_path: Path) -> dict:
    """Migrate OR IDs in a single file."""
    content = file_path.read_text(encoding="utf-8")
    original_content = content

    changes = []
    retired_mentions = []

    for legacy_id, new_id in LEGACY_TO_NEW.items():
        pattern = r"\b" + re.escape(legacy_id) + r"\b"

        if new_id == "[RETIRED]":
            # Count retired mentions but don't replace
            matches = re.findall(pattern, content)
            if matches:
                retired_mentions.append(legacy_id)
        else:
            # Replace with new ID
            new_content = re.sub(pattern, new_id, content)
            if new_content != content:
                changes.append((legacy_id, new_id, len(re.findall(pattern, original_content))))
                content = new_content

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")

    parent = file_path.parents[2] if len(file_path.parents) >= 3 else file_path
    return {
        "file": str(file_path.relative_to(parent)),
        "changes": changes,
        "retired_mentions": retired_mentions,
        "modified": content != original_content,
    }


def main():
    repo_root = Path(__file__).parent.parent.parent.parent

    files = find_target_files(repo_root)

    print(f"Found {len(files)} target files to process")
    print()

    all_results = []
    for file_path in files:
        result = migrate_file(file_path)
        all_results.append(result)

        if result["changes"]:
            print(f"Modified: {result['file']}")
            for legacy, new, count in result["changes"]:
                print(f"  {legacy} -> {new} ({count} occurrences)")

        if result["retired_mentions"]:
            print(f"Retired IDs in {result['file']}: {', '.join(result['retired_mentions'])}")

        if result["changes"] or result["retired_mentions"]:
            print()

    # Summary
    modified_files = [r for r in all_results if r["modified"]]
    retired_files = [r for r in all_results if r["retired_mentions"]]

    print("Summary:")
    print(f"  Modified files: {len(modified_files)}")
    print(f"  Files with retired IDs: {len(retired_files)}")

    if retired_files:
        print()
        print("Files with retired OR IDs (manual review needed):")
        for result in retired_files:
            print(f"  {result['file']}: {', '.join(result['retired_mentions'])}")


if __name__ == "__main__":
    main()
