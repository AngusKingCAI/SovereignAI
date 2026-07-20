#!/usr/bin/env python3
"""
AR check: Verify all adapter modules in adapters/ register into ADAPTER_REGISTRY.

This check ensures that all provider adapter modules are properly registered
in the ADAPTER_REGISTRY in adapters/__init__.py.
"""

import re
import sys
from pathlib import Path


def get_adapter_files() -> list:
    """Get all adapter module files in adapters/ directory."""
    adapters_dir = Path("app/sovereignai/model_registry/adapters")

    if not adapters_dir.exists():
        return []

    return list(adapters_dir.glob("*.py"))


def get_registered_adapters() -> set:
    """Parse adapters/__init__.py to extract registered adapter IDs."""
    init_file = Path("app/sovereignai/model_registry/adapters/__init__.py")

    if not init_file.exists():
        return set()

    with open(init_file, encoding="utf-8") as f:
        content = f.read()

    # Simple regex-based approach
    pattern = r'"([^"]+)":\s*.*Adapter\(\)'
    matches = re.findall(pattern, content)

    registered = set(matches)

    return registered


def check_adapter_registry() -> int:
    """Check that all adapter modules are registered."""
    adapter_files = get_adapter_files()
    registered = get_registered_adapters()

    # Expected adapter names based on file names
    expected_adapters = {
        f.stem for f in adapter_files if f.stem != "__init__"
    }

    violations = []

    for expected in expected_adapters:
        if expected not in registered:
            violations.append(
                f"Adapter module '{expected}.py' exists but is not registered in ADAPTER_REGISTRY"
            )

    # Check for registered adapters without corresponding files
    for adapter_id in registered:
        if f"{adapter_id}.py" not in [f.name for f in adapter_files]:
            violations.append(
                f"Adapter '{adapter_id}' is registered but no corresponding module file exists"
            )

    if violations:
        print("VIOLATIONS:")
        for violation in violations:
            print(f"  - {violation}")
        return 1

    print("PASS: All adapter modules are properly registered")
    return 0


if __name__ == "__main__":
    sys.exit(check_adapter_registry())
