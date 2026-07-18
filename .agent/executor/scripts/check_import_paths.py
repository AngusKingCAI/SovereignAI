#!/usr/bin/env python3
"""
Detection script: scan app/sovereignai/**/*.py for app.sovereignai imports.
Fails if any dual import paths are found.

Usage: python check_import_paths.py
"""

import re
import sys
from pathlib import Path


def check_imports():
    """Scan for app.sovereignai imports in sovereignai package."""
    sovereignai_dir = Path('app/sovereignai')
    if not sovereignai_dir.exists():
        print(f"Directory not found: {sovereignai_dir}")
        return 1

    violations = []
    pattern = re.compile(r'(from app\.sovereignai|import app\.sovereignai)')

    for py_file in sovereignai_dir.rglob('*.py'):
        content = py_file.read_text()
        if pattern.search(content):
            violations.append(str(py_file))

    if violations:
        print("ERROR: Found app.sovereignai imports in sovereignai package:")
        for violation in violations:
            print(f"  - {violation}")
        print("\nAll files in app/sovereignai/ must use sovereignai.* imports (no app. prefix)")
        return 1

    print("OK: No app.sovereignai imports found in sovereignai package")
    return 0


if __name__ == '__main__':
    sys.exit(check_imports())
