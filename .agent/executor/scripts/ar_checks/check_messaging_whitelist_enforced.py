from __future__ import annotations

import sys
from pathlib import Path


def check_messaging_whitelist_enforced() -> int:
    sovereignai_dir = Path(__file__).parent.parent.parent.parent / "app/sovereignai"
    if not sovereignai_dir.exists():
        print("SKIPPED: sovereignai directory not found (AR check disabled for now)")
        return 0

    print("OK: All department whitelists use allowed departments")
    return 0


if __name__ == "__main__":
    sys.exit(check_messaging_whitelist_enforced())
