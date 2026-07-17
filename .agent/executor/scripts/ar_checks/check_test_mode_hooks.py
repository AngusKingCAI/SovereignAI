#!/usr/bin/env python3
"""L52 enforcement: Scan production code for TEST_MODE env hooks.

Scans sovereignai/, databases/, services/, adapters/, web/ for env-var branching
patterns like os.environ.get(...TEST_MODE...), if os.getenv(...TEST...), etc.
Exit≠0 if found in any non-test file.
"""

import re
import sys
from pathlib import Path

# Production code directories (exclude tests/)
PRODUCTION_DIRS = [
    "sovereignai/",
    "databases/",
    "services/",
    "adapters/",
    "web/",
]

# Patterns to detect TEST_MODE env hooks
PATTERNS = [
    r'os\.environ\.get\([^)]*[Tt][Ee][Ss][Tt][^)]*\)',
    r'os\.getenv\([^)]*[Tt][Ee][Ss][Tt][^)]*\)',
    r'if\s+_test_mode',
    r'if\s+test_mode',
    r'TEST_MODE\s*==',
    r'TEST_MODE\s*!=',
]


def scan_file(file_path: Path) -> list[str]:
    """Scan a single file for TEST_MODE patterns."""
    matches = []
    try:
        content = file_path.read_text()
        for pattern in PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.splitlines()[line_num - 1].strip()
                matches.append(f"{file_path}:{line_num}: {line_content}")
    except Exception:
        pass
    return matches


def main() -> int:
    """Scan production code for TEST_MODE env hooks."""
    all_matches = []

    for prod_dir in PRODUCTION_DIRS:
        dir_path = Path(prod_dir)
        if not dir_path.exists():
            continue

        for py_file in dir_path.rglob("*.py"):
            # Skip test files
            if "test" in py_file.name or py_file.parent.name == "tests":
                continue
            matches = scan_file(py_file)
            all_matches.extend(matches)

    if all_matches:
        print("L52 violation: Production code contains TEST_MODE env hooks:", file=sys.stderr)
        for match in all_matches:
            print(f"  {match}", file=sys.stderr)
        return 1

    print("L52: no TEST_MODE env hooks in production code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
