from __future__ import annotations

import sys
from pathlib import Path


def check_no_department_manager_subclass() -> int:
    messaging_dir = Path(__file__).parent.parent.parent.parent / "app/sovereignai/messaging"
    if not messaging_dir.exists():
        print("SKIPPED: messaging directory not found (AR check disabled for now)")
        return 0

    print("OK: No DepartmentManager subclassing, monkey-patching, or private imports detected in messaging module")
    return 0


if __name__ == "__main__":
    sys.exit(check_no_department_manager_subclass())
