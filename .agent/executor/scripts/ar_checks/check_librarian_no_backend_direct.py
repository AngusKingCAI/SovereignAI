from __future__ import annotations

import sys
from pathlib import Path


def check_librarian_no_backend_direct() -> int:
    """Check that workers don't directly import memory backends.

    Workers MUST query Librarian, not memory backends directly.
    """
    workers_dir = (
        Path(__file__).parent.parent.parent.parent.parent / "app/sovereignai/workers"
    )
    if not workers_dir.exists():
        print("SKIPPED: workers directory not found")
        return 0

    # Check for direct imports of memory backends
    forbidden_imports = [
        "from sovereignai.memory.persistent_graph import",
        "from sovereignai.memory.gateway import",
        "import sovereignai.memory.persistent_graph",
        "import sovereignai.memory.gateway",
    ]

    violations = []
    for worker_file in workers_dir.rglob("*.py"):
        content = worker_file.read_text()
        for forbidden in forbidden_imports:
            if forbidden in content:
                violations.append((str(worker_file), forbidden))

    if violations:
        print("FAILED: Found direct memory backend imports in workers:")
        for file_path, import_stmt in violations:
            print(f"  {file_path}: {import_stmt}")
        return 1

    print("OK: No direct memory backend imports found in workers")
    return 0


if __name__ == "__main__":
    sys.exit(check_librarian_no_backend_direct())
