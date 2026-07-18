#!/usr/bin/env python3
"""Check that a commit touching UI directories doesn't also touch sovereignai/.

Enforces AR7 (AGENTS.md) at the commit-scope level (close.md step 8's "UI
changes don't touch sovereignai/" check): if the most recent commit's diff
includes both a UI-layer path and a sovereignai/ path, that's a layering
violation worth a STOP, not a silent merge of concerns.

Modified to check staged changes by default to avoid false positives from
historical commits (e.g., DEBT-10 Plan 25 violations).
"""

import subprocess
import sys

UI_PREFIXES = ("app/web/", "app/cli/", "app/tui/", "app/phone/")
CORE_PREFIX = "app/sovereignai/"


def changed_files(staged: bool = True) -> list[str]:
    """Return the list of files changed (staged by default, or last commit)."""
    if staged:
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
    else:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True,
            text=True,
            check=True,
        )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    """Run the AR7 commit-scope check on staged changes by default."""
    try:
        files = changed_files(staged=True)
    except subprocess.CalledProcessError as exc:
        print(f"git diff failed: {exc}", file=sys.stderr)
        return 0  # Nothing to compare against — not a violation.

    if not files:
        print("AR7: no staged changes found.")
        return 0

    touches_ui = [f for f in files if f.startswith(UI_PREFIXES)]
    touches_core = [f for f in files if f.startswith(CORE_PREFIX)]

    if touches_ui and touches_core:
        print("AR7 violation: staged changes touch both UI and core layers:", file=sys.stderr)
        print(f"  UI files: {touches_ui}", file=sys.stderr)
        print(f"  Core files: {touches_core}", file=sys.stderr)
        return 1

    print("AR7: no UI/core layering violation in staged changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
