from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.diagnostics.harness import DiagnosticHarness


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SovereignAI diagnostic harness")
    parser.add_argument(
        "--auto-fix",
        action="store_true",
        help="Prompt to install missing services",
    )
    args = parser.parse_args()

    print("SovereignAI Diagnostic Harness")
    print("=" * 50)
    print()

    harness = DiagnosticHarness()
    results = harness.run_all()

    print()
    print("=" * 50)
    print("Summary:")
    pass_count = sum(1 for r in results if r.status == "PASS")
    fail_count = sum(1 for r in results if r.status == "FAIL")
    skip_count = sum(1 for r in results if r.status == "SKIP")
    print(f"Result: {pass_count} PASS, {fail_count} FAIL, {skip_count} SKIP")

    if args.auto_fix and fail_count > 0:
        print()
        print("Auto-fix mode: Some stages failed.")
        print("Run installers manually if needed:")
        print("  python scripts/diagnostics/installers.py")

    sys.exit(0 if fail_count == 0 else 1)


if __name__ == "__main__":
    main()
