#!/usr/bin/env python3
"""Check that a commit touching UI directories doesn't also touch sovereignai/.

Enforces AR7 (AGENTS.md) at the commit-scope level (close.md step 8's "UI
changes don't touch sovereignai/" check): if the most recent commit's diff
includes both a UI-layer path and a sovereignai/ path, that's a layering
violation worth a STOP, not a silent merge of concerns.
"""

import subprocess
import sys

UI_PREFIXES = ("web/", "cli/", "tui/", "phone/")
CORE_PREFIX = "sovereignai/"
# Exception: sovereignai/main.py can be touched when adding a new UI that needs DI registration
# This is a one-time setup cost; subsequent UI changes should not touch core.
CORE_EXCEPTION = "sovereignai/main.py"


def changed_files(ref: str = "HEAD~1") -> list[str]:
    """Return the list of files changed between ref and HEAD via git diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", ref],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    """Run the AR7 commit-scope check comparing the current commit against HEAD~1."""
    try:
        files = changed_files()
    except subprocess.CalledProcessError as exc:
        print(f"git diff failed (likely first commit, no HEAD~1): {exc}", file=sys.stderr)
        return 0  # Nothing to compare against — not a violation.

    touches_ui = [f for f in files if f.startswith(UI_PREFIXES)]
    touches_core = [f for f in files if f.startswith(CORE_PREFIX) and f != CORE_EXCEPTION]

    if touches_ui and touches_core:
        print("AR7 violation: commit touches both UI and core layers:", file=sys.stderr)
        print(f"  UI files: {touches_ui}", file=sys.stderr)
        print(f"  Core files: {touches_core}", file=sys.stderr)
        return 1

    print("AR7: no UI/core layering violation in this commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
