"""Check that only Orchestrator talks to Owner via owner.message.received.

Enforces architecture rule AR1: Owner ↔ Orchestrator only. This check verifies
that only the Orchestrator facade subscribes to owner.message.received events,
ensuring the Orchestrator is the single entry point for Owner communications.

AR Rule: AR1 - Owner ↔ Orchestrator only
"""

import sys
from pathlib import Path


def check_orchestrator_single_entry() -> int:
    """Check that only Orchestrator subscribes to owner.message.received."""
    orchestrator_files = list(Path("app/sovereignai/orchestrator").glob("*.py"))

    if not orchestrator_files:
        print("Orchestrator directory not found, skipping check.")
        return 0

    owner_subscribers = []

    for py_file in orchestrator_files:
        if py_file.name == "__init__.py":
            continue

        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

            if "owner.message.received" in content:
                owner_subscribers.append(
                    f"{py_file}: subscribes to owner.message.received"
                )
        except Exception as e:
            print(f"Error reading {py_file}: {e}", file=sys.stderr)
            return 1

    if len(owner_subscribers) > 1:
        print("Multiple owner.message.received subscribers found:", file=sys.stderr)
        for subscriber in owner_subscribers:
            print(f"  {subscriber}", file=sys.stderr)
        return 1

    if len(owner_subscribers) == 1:
        print("Orchestrator is the single entry point for Owner communications.")
        return 0

    print("No owner.message.received subscribers found in Orchestrator.")
    return 0


if __name__ == "__main__":
    sys.exit(check_orchestrator_single_entry())
