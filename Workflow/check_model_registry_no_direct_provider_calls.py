#!/usr/bin/env python3
"""
AR check: Verify all provider access goes through SyncService.

This check ensures that provider API calls are only made through the
ModelSyncService.sync_provider() method, not directly by other components.
"""

import sys
from pathlib import Path


def check_no_direct_provider_calls() -> int:
    """Check that no direct provider API calls exist outside of sync.py."""
    model_registry_dir = Path("app/sovereignai/model_registry")

    violations = []

    # Files that should NOT make direct provider API calls
    restricted_files = [
        "api.py",
        "offline.py",
        "database.py",
        "schema.py",
        "ui_contract.py",
    ]

    for file_path in model_registry_dir.glob("*.py"):
        if file_path.name in restricted_files:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for common provider API patterns
            suspicious_patterns = [
                "openai.",
                "requests.get",
                "httpx.get",
                "aiohttp.",
                "provider.api",
                "client.chat.completions",
                "ollama.generate",
            ]

            for pattern in suspicious_patterns:
                if pattern in content.lower():
                    violations.append(
                        f"{file_path.name}: Found potential direct provider call pattern: {pattern}"
                    )

    if violations:
        print("VIOLATIONS:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("PASS: No direct provider API calls found in restricted files")
    return 0


if __name__ == "__main__":
    sys.exit(check_no_direct_provider_calls())
