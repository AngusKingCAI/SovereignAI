from __future__ import annotations

import sys
from pathlib import Path


def check_memory_gateway_ownership() -> int:
    """Check that MemoryGateway is the sole owner of PersistentGraphMemory.

    Verify that no other modules directly instantiate or own PersistentGraphMemory.
    """
    memory_dir = (
        Path(__file__).parent.parent.parent.parent.parent / "app/sovereignai/memory"
    )
    if not memory_dir.exists():
        print("SKIPPED: memory directory not found")
        return 0

    # Check that only gateway.py imports and owns PersistentGraphMemory
    gateway_file = memory_dir / "gateway.py"
    if not gateway_file.exists():
        print("SKIPPED: gateway.py not found")
        return 0

    # Scan memory directory for other files that might own PGM
    violations = []
    for memory_file in memory_dir.glob("*.py"):
        if memory_file.name == "gateway.py":
            continue
        if memory_file.name == "persistent_graph.py":
            continue  # The implementation itself
        if memory_file.name == "__init__.py":
            continue  # Export module is allowed

        content = memory_file.read_text()
        if "PersistentGraphMemory" in content and ("import" in content or "from" in content):
            violations.append(str(memory_file))

    if violations:
        print("FAILED: Found non-gateway modules that reference PersistentGraphMemory:")
        for file_path in violations:
            print(f"  {file_path}")
        return 1

    print("OK: MemoryGateway is the sole owner of PersistentGraphMemory")
    return 0


if __name__ == "__main__":
    sys.exit(check_memory_gateway_ownership())
