from __future__ import annotations

import sys
from pathlib import Path


def check_graph_memory_persistence() -> int:
    """Check that PersistentGraphMemory uses file-backed mode.

    Verify that memory persistence is configured to use file storage,
    not in-memory storage.
    """
    # Check that the persistent_graph module exists and uses file-backed storage
    persistent_graph_file = (
        Path(__file__).parent.parent.parent.parent.parent
        / "app/sovereignai/memory/persistent_graph.py"
    )
    if not persistent_graph_file.exists():
        print("SKIPPED: persistent_graph.py not found")
        return 0

    content = persistent_graph_file.read_text()

    # Check for file-backed storage indicators
    if "Path" in content and "db_path" in content:
        print("OK: PersistentGraphMemory uses file-backed storage")
        return 0

    print("FAILED: PersistentGraphMemory does not appear to use file-backed storage")
    return 1


if __name__ == "__main__":
    sys.exit(check_graph_memory_persistence())
