#!/usr/bin/env python3
"""
AR check: Verify database.py implements transaction safety.

This check ensures that database.py uses commit patterns for transaction safety.
"""

import sys
from pathlib import Path


def check_transaction_safety() -> int:
    """Check that database operations use transactions."""
    database_file = Path("app/sovereignai/model_registry/database.py")

    if not database_file.exists():
        print("SKIP: database.py not found")
        return 0

    with open(database_file, encoding="utf-8") as f:
        content = f.read()

    violations = []

    # Check that transaction patterns are present
    if "conn.commit()" not in content:
        violations.append("database.py should use conn.commit() for transaction safety")

    # Check for WAL mode (indicates proper transaction handling)
    if "PRAGMA journal_mode=WAL" not in content:
        violations.append("database.py should enable WAL mode for better concurrency")

    if violations:
        print("VIOLATIONS:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("PASS: Database implements transaction safety")
    return 0


if __name__ == "__main__":
    sys.exit(check_transaction_safety())
