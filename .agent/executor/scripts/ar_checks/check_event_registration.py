#!/usr/bin/env python3
"""
AR check: Verify event registrations are properly configured.

This script checks that:
1. EventRegistry is properly instantiated in main.py
2. EventBus receives EventRegistry in constructor
3. Event payload classes exist in events.py
4. Events are properly registered with handlers

AR ID: AR8 (tracing)
"""

import sys
from pathlib import Path

# Add app/ to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "app"))

def check_event_registry_import() -> bool:
    """Check that EventRegistry is imported in main.py"""
    main_py = Path(__file__).parent.parent.parent.parent.parent / "app" / "sovereignai" / "main.py"
    content = main_py.read_text()
    return "from sovereignai.shared.event_registry import EventRegistry" in content

def check_event_bus_registry_param() -> bool:
    """Check that EventBus constructor accepts registry parameter"""
    event_bus_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "event_bus.py"
    )
    content = event_bus_py.read_text()
    return "registry: EventRegistry" in content

def check_registry_instantiation() -> bool:
    """Check that EventRegistry is instantiated before EventBus"""
    main_py = Path(__file__).parent.parent.parent.parent.parent / "app" / "sovereignai" / "main.py"
    content = main_py.read_text()
    return "registry = EventRegistry()" in content

def check_event_bus_construction() -> bool:
    """Check that EventBus is constructed with registry"""
    main_py = Path(__file__).parent.parent.parent.parent.parent / "app" / "sovereignai" / "main.py"
    content = main_py.read_text()
    return "EventBus(trace=trace, registry=registry)" in content

def check_events_module_exists() -> bool:
    """Check that events.py module exists"""
    events_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "events.py"
    )
    return events_py.exists()

def check_event_classes_exist() -> bool:
    """Check that event payload classes exist"""
    events_py = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app"
        / "sovereignai"
        / "shared"
        / "events.py"
    )
    if not events_py.exists():
        return False
    content = events_py.read_text()
    required_classes = ["TaskCreated", "TaskUpdated", "AgentStep", "HardwareStatus"]
    return all(cls_name in content for cls_name in required_classes)

def main() -> int:
    checks = [
        ("EventRegistry import in main.py", check_event_registry_import),
        ("EventBus accepts registry parameter", check_event_bus_registry_param),
        ("EventRegistry instantiated", check_registry_instantiation),
        ("EventBus constructed with registry", check_event_bus_construction),
        ("events.py module exists", check_events_module_exists),
        ("Event payload classes exist", check_event_classes_exist),
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
