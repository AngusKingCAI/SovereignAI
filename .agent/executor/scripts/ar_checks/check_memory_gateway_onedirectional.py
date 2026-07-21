from __future__ import annotations

import sys
from pathlib import Path


def check_memory_gateway_onedirectional() -> int:
    """Check that MemoryGateway does not import or invoke Orchestrator.

    MemoryGateway should be one-directional: MemoryGateway → Librarian → Orchestrator.
    Gateway should not have any knowledge of or dependencies on Orchestrator.
    """
    gateway_file = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app/sovereignai/memory/gateway.py"
    )
    if not gateway_file.exists():
        print("SKIPPED: gateway.py not found")
        return 0

    content = gateway_file.read_text()

    # Check for any Orchestrator references
    forbidden_patterns = [
        "from sovereignai.orchestrator",
        "import sovereignai.orchestrator",
        "from app.sovereignai.orchestrator",
        "import app.sovereignai.orchestrator",
        "Orchestrator",
        "orchestrator_facade",
    ]

    violations = []
    for pattern in forbidden_patterns:
        if pattern in content:
            violations.append(pattern)

    if violations:
        print("FAILED: MemoryGateway contains Orchestrator references:")
        for pattern in violations:
            print(f"  {pattern}")
        return 1

    print("OK: MemoryGateway does not import or invoke Orchestrator")
    return 0


if __name__ == "__main__":
    sys.exit(check_memory_gateway_onedirectional())
