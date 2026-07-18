#!/usr/bin/env python3
"""
AR check: Verify Event dataclass is frozen.

This script checks that:
1. Event dataclass has frozen=True decorator
2. Event dataclass has version field
3. Event dataclass has trace_level field
4. Event dataclass has event_type property

AR ID: AR8 (tracing)
"""

import sys
from pathlib import Path

# Add app/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "app"))

def check_event_frozen() -> bool:
    """Check that Event dataclass is frozen"""
    types_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "types.py"
    )
    content = types_py.read_text()
    return "@dataclass(frozen=True)" in content and "class Event:" in content

def check_event_version_field() -> bool:
    """Check that Event has version field"""
    types_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "types.py"
    )
    content = types_py.read_text()
    return "version: int" in content

def check_event_trace_level_field() -> bool:
    """Check that Event has trace_level field"""
    types_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "types.py"
    )
    content = types_py.read_text()
    return "trace_level: TraceLevel" in content

def check_event_type_property() -> bool:
    """Check that Event has event_type property"""
    types_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "types.py"
    )
    content = types_py.read_text()
    return "@property" in content and "def event_type(self) -> str:" in content

def main() -> int:
    checks = [
        ("Event dataclass is frozen", check_event_frozen),
        ("Event has version field", check_event_version_field),
        ("Event has trace_level field", check_event_trace_level_field),
        ("Event has event_type property", check_event_type_property),
    ]

    failed = []
    for name, check in checks:
        if not check():
            failed.append(name)
            print(f"FAIL: {name}")
        else:
            print(f"PASS: {name}")

    if failed:
        print(f"\nFailed checks: {len(failed)}")
        return 1
    print("\nAll checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
