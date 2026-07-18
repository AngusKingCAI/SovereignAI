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

# Get repo root from git to handle different script locations
result = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True, cwd=Path(__file__).parent
)
REPO_ROOT = Path(result.stdout.strip()) if result.returncode == 0 else Path(__file__).resolve().parent.parent.parent.parent.parent.parent.parent

def check_execution_log_empty() -> tuple[bool, str]:
    """Pattern 1: Execution log should be blank at close (per close/SKILL.md step 11)."""
    logs_dir = REPO_ROOT / "logs"
    if not logs_dir.exists():
        return True, "No logs directory"

    # Find current plan from CHANGELOG or PLANS.md
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    plans_md = REPO_ROOT / ".agent" / "shared" / "PLANS.md"

    current_plan = None

    # Try CHANGELOG first
    if changelog.exists():
        content = changelog.read_text()
        # Look for plan-workflow-fix-{N} pattern in latest entry
        match = re.search(r'plan-workflow-fix-[\d]+', content)
        if match:
            current_plan = match.group()

    # If not found, try PLANS.md
    if not current_plan and plans_md.exists():
        content = plans_md.read_text()
        # Look for active plan marker
        match = re.search(r'\*\*ACTIVE\*\*: plan-workflow-fix-[\d]+', content)
        if match:
            current_plan = match.group().split(": ")[1]

    if not current_plan:
        return True, "No current plan identified - skipping execution log check"

    # Check execution log for current plan only
    execution_log = logs_dir / f"execution-log-{current_plan}.md"
    if not execution_log.exists():
        return True, f"Execution log for {current_plan} not found (not created yet)"

    content = execution_log.read_text().strip()
    # Allow header template only
    header_template = f"# Execution Log: {current_plan}"
    if content.startswith(header_template):
        # Check if there's content beyond the header
        lines_after_header = content.split("---")[0].split("\n")[1:] if "---" in content else []
        # If only header and date/plan info, that's OK (template)
        if len(content) < 200:  # Rough check for template-only content
            return True, f"Execution log for {current_plan} is blank (template only)"

    return False, f"Execution log for {current_plan} not blank (has {len(content)} chars)"

def check_changelog_position() -> tuple[bool, str]:
    """Pattern 2: Latest prompt must be at TOP of CHANGELOG (prepend, not append)."""
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    if not changelog.exists():
        return False, f".agent/shared/CHANGELOG.md not found (REPO_ROOT={REPO_ROOT}, path={changelog})"

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
    """Pattern 3: Only check plans executed in current session (CHANGELOG or PLANS.md)."""
    # Find current plan from CHANGELOG or PLANS.md
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    plans_md = REPO_ROOT / ".agent" / "shared" / "PLANS.md"

    current_plan = None

    # Try CHANGELOG first
    if changelog.exists():
        content = changelog.read_text()
        # Look for plan-workflow-fix-{N} pattern in latest entry
        match = re.search(r'plan-workflow-fix-[\d]+', content)
        if match:
            current_plan = match.group()

    # If not found, try PLANS.md
    if not current_plan and plans_md.exists():
        content = plans_md.read_text()
        # Look for active plan marker
        match = re.search(r'\*\*ACTIVE\*\*: plan-workflow-fix-[\d]+', content)
        if match:
            current_plan = match.group().split(": ")[1]

    if not current_plan:
        return True, "No current plan identified"

    # Check if this specific plan file has been moved to completed/
    plan_file = REPO_ROOT / "prompts" / f"{current_plan}.md"
    completed_file = REPO_ROOT / "prompts" / "completed" / f"{current_plan}.md"

    if plan_file.exists():
        return False, f"Plan file {current_plan}.md still in prompts/ (not moved to completed/)"

    if completed_file.exists():
        return True, f"Plan file {current_plan}.md moved to completed/"

    return True, f"Plan file {current_plan}.md not found (may not be executed yet)"

def check_no_uncommitted_governance() -> tuple[bool, str]:
    """Pattern 4: No uncommitted changes to governance docs before tag."""
    governance_files = [
        "AGENTS.md",
        ".agent/shared/LANDMINES.md",
        ".agent/architect/PRINCIPLES.md",
        ".agent/shared/DECISIONS.md",
        ".agent/shared/DEBT.md",
        ".agent/shared/PLANS.md"
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
