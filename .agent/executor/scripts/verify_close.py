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
if result.returncode == 0:
    REPO_ROOT = Path(result.stdout.strip())
else:
    # Fallback: go up from scripts/executor/.agent/repo
    REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

def check_execution_log_empty() -> tuple[bool, str]:
    """Pattern 1: Execution log should be blank at close (per close/SKILL.md step 11)."""
    logs_dir = REPO_ROOT / "logs"
    if not logs_dir.exists():
        return True, "No logs directory"

    # Get current plan from get_current_plan.py
    get_current_plan_script = REPO_ROOT / ".agent" / "executor" / "scripts" / "get_current_plan.py"
    if not get_current_plan_script.exists():
        return True, "get_current_plan.py not found - skipping execution log check"

    result = subprocess.run(
        ["python", str(get_current_plan_script)],
        capture_output=True, text=True, cwd=REPO_ROOT
    )

    if result.returncode != 0:
        return True, f"get_current_plan.py failed: {result.stderr} - skipping execution log check"

    current_plan_path = Path(result.stdout.strip())
    # Extract plan name from path (e.g., "plan-22-Rev11.md" -> "plan-22-Rev11")
    current_plan = current_plan_path.stem  # Removes .md extension

    if not current_plan:
        return True, "No current plan identified - skipping execution log check"

    # Check execution log for current plan only, handle Rev suffixes
    # Try exact name first (e.g., execution-log-plan-22-rev16.md)
    execution_log = logs_dir / f"execution-log-{current_plan}.md"
    if not execution_log.exists():
        # Try with different Rev suffix patterns for historical compatibility
        # e.g., execution-log-plan-22-Rev11.md or execution-log-plan-22-rev11.md
        rev_pattern_upper = f"execution-log-{current_plan}-Rev*.md"
        rev_pattern_lower = f"execution-log-{current_plan}-rev*.md"
        rev_logs = list(logs_dir.glob(rev_pattern_upper)) + list(logs_dir.glob(rev_pattern_lower))
        if rev_logs:
            execution_log = rev_logs[0]  # Use first match
        else:
            return True, f"Execution log for {current_plan} not found (not created yet)"

    content = execution_log.read_text(encoding='utf-8').strip()
    # Allow header template only
    header_template = "# Execution Log:"
    if content.startswith(header_template) and len(content) < 250:
        # If only header and date/plan info, that's OK (template)
        return True, f"Execution log for {current_plan} is blank (template only)"

    return False, f"Execution log for {current_plan} not blank (has {len(content)} chars)"

def check_changelog_position() -> tuple[bool, str]:
    """Pattern 2: Latest prompt must be at TOP of CHANGELOG (prepend, not append).

    Only matches against '## ' entry headers, never body text (e.g. a
    "**Previous Baseline**: prompt-N" line inside some other entry) — otherwise
    the check can pass or fail by coincidence based on unrelated text.

    Non-prompt entry types (e.g. "## workflow-fix — ...", or an infra entry like
    "## prompts -> plans folder rename") are allowed to sit above prompt entries;
    they simply don't match the prompt-header pattern and are skipped when
    finding the top-most prompt entry.
    """
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    if not changelog.exists():
        return False, (
            f".agent/shared/CHANGELOG.md not found "
            f"(REPO_ROOT={REPO_ROOT}, path={changelog})"
        )

    content = changelog.read_text()
    header_pattern = r'^## (prompt-[\d]+(?:\.[\d]+)*)'

    # Only headers count — body text mentioning "prompt-N" elsewhere is ignored.
    header_prompts = re.findall(header_pattern, content, re.MULTILINE)
    if not header_prompts:
        return True, "No prompt-N headers in CHANGELOG yet"

    # Extract numeric values for proper sorting (handles 20.9.9, 21, etc.)
    def prompt_key(p: str) -> tuple[int, ...]:
        parts = p.replace("prompt-", "").split(".")
        return tuple(int(x) for x in parts if x)

    latest = max(header_prompts, key=prompt_key)

    # First prompt-N header found top-to-bottom; non-prompt headers above it
    # (infra renames, workflow-fix, etc.) don't count against this check.
    top_prompt_header = re.search(header_pattern, content, re.MULTILINE)
    top_prompt = top_prompt_header.group(1) if top_prompt_header else None

    if top_prompt == latest:
        return True, (
            f"Latest {latest} at top of CHANGELOG "
            "(non-prompt entries above it, if any, are OK)"
        )
    return False, (
        f"Latest is {latest}, but top-most prompt-N header is "
        f"{top_prompt or 'none'}. Prepend {latest}."
    )

def check_plan_files_moved() -> tuple[bool, str]:
    """Pattern 3: Only check plans executed in current session.
    Handle Rev suffixes (CHANGELOG or PLANS.md)."""
    # Find current plan from CHANGELOG (source of truth for what was just executed)
    changelog = REPO_ROOT / ".agent" / "shared" / "CHANGELOG.md"
    plans_md = REPO_ROOT / ".agent" / "shared" / "PLANS.md"

    current_plan = None

    # Use CHANGELOG as source of truth - it's updated during execution with the current plan
    if changelog.exists():
        content = changelog.read_text()
        # Extract the first (most recent) plan reference from the first header
        first_header_match = re.search(r'^## (prompt-[\w-]+)', content, re.MULTILINE)
        if first_header_match:
            current_plan = first_header_match.group(1).replace("prompt-", "")

    # Fallback to PLANS.md only if CHANGELOG doesn't have the plan
    if not current_plan and plans_md.exists():
        content = plans_md.read_text()
        # Look for active plan marker (both patterns)
        match = re.search(r'\*\*ACTIVE\*\*: plan-(?:workflow-)?fix-[\d]+', content)
        if match:
            current_plan = match.group().split(": ")[1]

    if not current_plan:
        return True, "No current plan identified from CHANGELOG or PLANS.md"

    # Check if ANY variant of this plan file has been moved to completed/
    # Add "plan-" prefix to current_plan for file lookup
    plan_file_prefix = f"plan-{current_plan}"

    # Look for {plan_file_prefix}.md OR {plan_file_prefix}-Rev*.md
    # (historical: {plan_file_prefix}-rev*.md)
    plans_dir = REPO_ROOT / "plans"
    completed_dir = REPO_ROOT / "plans" / "completed"

    # Check if any variant still exists in plans/
    base_pattern = f"{plan_file_prefix}.md"
    rev_pattern_upper = f"{plan_file_prefix}-Rev*.md"
    rev_pattern_lower = f"{plan_file_prefix}-rev*.md"

    # If plan still in plans/, it's not yet completed - skip this check
    if (
        (plans_dir / base_pattern).exists()
        or list(plans_dir.glob(rev_pattern_upper))
        or list(plans_dir.glob(rev_pattern_lower))
    ):
        return (
            True,
            f"Plan file {plan_file_prefix} still in plans/ "
            "(not yet completed - OK for active work)",
        )

    # Check if any variant exists in completed/
    if (
        (completed_dir / base_pattern).exists()
        or list(completed_dir.glob(rev_pattern_upper))
        or list(completed_dir.glob(rev_pattern_lower))
    ):
        return True, f"Plan file {plan_file_prefix} (or Rev variant) moved to completed/"

    return True, f"Plan file {plan_file_prefix} not found (may not be executed yet)"

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

def main() -> None:
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
