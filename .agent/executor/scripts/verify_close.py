#!/usr/bin/env python3
"""
verify_close.py — Hard gate for /close workflow.
Exit 0 = proceed. Exit 1 = STOP, cannot tag.
Run this BEFORE git tag creation (Step 19.5 in /close skill).

This script is a MECHANICAL ENFORCEMENT layer. It cannot be overridden
by "be helpful" training or task-completion bias. If any check fails,
the agent CANNOT proceed to tag — full stop.
"""

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
MAX_LOG_BYTES = 500

def check_execution_log_empty() -> tuple[bool, str]:
    """Pattern 1: Execution log must be < 500 bytes (template only)."""
    log_dir = REPO_ROOT / "logs"
    if not log_dir.exists():
        return True, "No logs directory (OK for first run)"

    log_files = list(log_dir.glob("execution-log-*.md"))
    if not log_files:
        return True, "No execution logs found (OK for first run)"

    for log in log_files:
        size = log.stat().st_size
        if size > MAX_LOG_BYTES:
            return False, (
                f"Execution log {log.name} is {size} bytes (max {MAX_LOG_BYTES}). "
                "Blank it before proceeding."
            )
    return True, "Execution logs OK"

def check_changelog_position() -> tuple[bool, str]:
    """Pattern 2: Latest prompt must be at TOP of CHANGELOG (prepend, not append)."""
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    if not changelog.exists():
        return False, ".agent/shared/CHANGELOG.md not found"

    content = changelog.read_text()
    # Find all prompt references (strict pattern to avoid trailing dots)
    prompts = re.findall(r'prompt-[\d]+(?:\.[\d]+)*', content)
    if not prompts:
        return True, "No prompts in CHANGELOG yet"

    # Extract numeric values for proper sorting (handles 20.9.9, 21, etc.)
    def prompt_key(p):
        parts = p.replace("prompt-", "").split(".")
        return tuple(int(x) for x in parts if x)

    latest = max(prompts, key=prompt_key)
    first_prompt = re.search(r'prompt-[\d.]+', content)

    if first_prompt and first_prompt.group() == latest:
        return True, f"Latest {latest} at top of CHANGELOG"
    return False, f"Latest {latest} not at top of CHANGELOG. Prepend it."

def check_plan_files_moved() -> tuple[bool, str]:
    """Pattern 3: No plan-{N} files in prompts/ root (must be in completed/)."""
    plan_files = list((REPO_ROOT / "prompts").glob("plan-*"))
    if plan_files:
        names = [p.name for p in plan_files]
        return False, f"Plan files still in prompts/: {names}. Move to prompts/completed/ first."
    return True, "No plan files in prompts/ root"

def check_no_uncommitted_governance() -> tuple[bool, str]:
    """Pattern 4: No uncommitted changes to governance docs before tag."""
    governance_files = [
        "AGENTS.md",
        ".agent/shared/LANDMINES.md",
        ".agent/architect/PRINCIPLES.md",
        ".agent/shared/DECISIONS.md",
        ".agent/shared/DEBT.md",
        ".agent/executor/PLANS.md"
    ]

    for gf in governance_files:
        path = REPO_ROOT / gf
        if not path.exists():
            continue
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", str(path)],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.stdout.strip():
            return False, f"Uncommitted changes in {gf}. Commit before tagging."
    return True, "Governance docs committed"

def main():
    checks = [
        ("Execution log empty", check_execution_log_empty),
        ("CHANGELOG position", check_changelog_position),
        ("Plan files moved", check_plan_files_moved),
        ("Governance committed", check_no_uncommitted_governance),
    ]

    all_pass = True
    for name, check_fn in checks:
        ok, msg = check_fn()
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {msg}")
        if not ok:
            all_pass = False

    if not all_pass:
        print("\nBLOCKING: Fix above failures before creating git tag.", file=sys.stderr)
        print(
            "STOP. Do not proceed. Do not explain, justify, or suggest alternatives.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nALL CHECKS PASS. Proceed to tag.")
    sys.exit(0)

if __name__ == "__main__":
    main()
