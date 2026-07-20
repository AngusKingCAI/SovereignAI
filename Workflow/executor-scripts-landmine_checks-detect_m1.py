#!/usr/bin/env python3
"""
Landmine M1 Detection: Dual import paths break protocol isinstance

Checks for app.sovereignai.* imports in files under app/sovereignai/.
All source files in app/sovereignai/ must use sovereignai.* imports
(matches installed package name).
"""

import re
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Get repository root using git rev-parse."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        # Fallback to current directory if not in git repo
        return Path.cwd()


def detect_m1_dual_imports() -> int:
    """Check for app.sovereignai.* imports in app/sovereignai/ files."""
    repo_root = get_repo_root()
    sovereignai_dir = repo_root / "app" / "sovereignai"

    if not sovereignai_dir.exists():
        print(f"ERROR: {sovereignai_dir} does not exist")
        return 1

    # Pattern to match app.sovereignai imports
    pattern = re.compile(r'from app\.sovereignai\b|import app\.sovereignai\b')

    violations = []

    for py_file in sovereignai_dir.rglob("*.py"):
        # Skip __pycache__ and test files
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, encoding='utf-8') as f:
                content = f.read()

            # Check each line for the pattern
            for line_num, line in enumerate(content.split('\n'), 1):
                if pattern.search(line):
                    violations.append((py_file.relative_to(repo_root), line_num, line.strip()))
        except Exception as e:
            print(f"WARNING: Could not read {py_file}: {e}")

    if violations:
        print("M1 LANDMINE DETECTED: Dual import paths found in app/sovereignai/")
        print("All source files in app/sovereignai/ must use sovereignai.* imports")
        print("Use .agent/executor/scripts/fix_import_paths.py to standardize")
        print()
        for file_path, line_num, line in violations:
            print(f"  {file_path}:{line_num}: {line}")
        return 1
    else:
        print("M1 check passed: No dual import paths found")
        return 0


if __name__ == "__main__":
    sys.exit(detect_m1_dual_imports())
