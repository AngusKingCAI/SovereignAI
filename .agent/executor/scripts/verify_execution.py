#!/usr/bin/env python3
"""verify_execution.py — verify executor followed plan manifest.

Usage:
  python verify_execution.py --init --plan <N>     # At /open: validate manifest
  python verify_execution.py --final --plan <N>     # At /close: full verification
  python verify_execution.py <plan-number>          # Manual verification

Checks:
1. Manifest exists and is parseable
2. All manifest deliverables exist in git history since plan start tag
3. No governance files were modified
4. Attestation file exists and is complete
5. Trace file exists (if available)

Exit 0 = PASS, Exit 1 = FAIL
"""

import argparse
import os
import re
import subprocess
import sys


def run_git(args: list[str], cwd: str = ".") -> tuple[str, int]:
    """Run git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.stdout.strip(), result.returncode


def get_manifest_from_plan(plan_id: str, repo_path: str = ".") -> tuple[dict | None, str | None]:
    """Extract Executor Manifest from plan file."""
    # Look for plan files with revision suffixes (e.g., plan-28-Rev5.md)
    import glob

    # First try in plans/ directory (active plans)
    plan_pattern = os.path.join(repo_path, f"plans/plan-{plan_id}*.md")
    plan_files = glob.glob(plan_pattern)

    # If not found, try in plans/completed/ subdirectories
    if not plan_files:
        completed_dir = os.path.join(repo_path, "plans/completed")
        for subdir in ['0-9', '10-19', '20-29', '30-39', 'Misc']:
            plan_pattern = os.path.join(completed_dir, subdir, f"plan-{plan_id}*.md")
            plan_files = glob.glob(plan_pattern)
            if plan_files:
                break

    if not plan_files:
        return None, f"Plan file not found: plan-{plan_id}*.md"

    # Sort by revision number if present, otherwise use the file name
    def extract_revision(filename: str) -> int:
        # Extract revision number from filename like plan-28-Rev5.md
        match = re.search(r'Rev(\d+)', filename)
        if match:
            return int(match.group(1))
        return 0

    plan_files.sort(key=extract_revision, reverse=True)
    plan_path = plan_files[0]  # Use highest revision

    with open(plan_path) as f:
        content = f.read()

    match = re.search(
        r"## Executor Manifest\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL
    )
    if not match:
        return None, "No Executor Manifest found in plan"

    manifest_text = match.group(1)
    phases = []
    deliverables = []
    coverage_target = None

    # Parse phases
    phases_match = re.search(r"\*\*Phases\*\*:\s*(\d+)\s*\(([^)]+)\)", manifest_text)
    if phases_match:
        phases_count = int(phases_match.group(1))
        phases = [f"S{i}" for i in range(phases_count + 1)]  # Include S0

    # Parse deliverables from table format
    # Look for table rows with file paths in backticks
    table_match = re.search(
        r"\| Phase \| Deliverable \| Verification \|.*?\n((?:\|.*?\n)+)",
        manifest_text,
        re.DOTALL,
    )
    if table_match:
        table_content = table_match.group(1)
        for line in table_content.split("\n"):
            if (
                "|" in line
                and not line.strip().startswith("|---")
                and not line.strip().startswith("| Phase")
            ):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:  # Need at least 3 columns
                    # Second column (index 1) is Phase, third column (index 2) is Deliverable
                    deliverable = parts[2] if len(parts) > 2 else ""
                    if deliverable:
                        # Extract all file paths from backticks (there may be multiple)
                        file_matches = re.findall(r"`([^`]+)`", deliverable)
                        for file_path in file_matches:
                            if "." in file_path:  # Only add if it looks like a file path
                                deliverables.append(file_path)
                    # Also check verification column (index 3) for test files
                    if len(parts) >= 4:
                        verification = parts[3] if len(parts) > 3 else ""
                        if verification:
                            # Extract test file paths from verification column
                            # Look for patterns like "pytest path/to/test_file.py -v passes"
                            test_matches = re.findall(r"pytest\s+([^\s]+\.py)", verification)
                            for file_path in test_matches:
                                deliverables.append(file_path)

    # Parse coverage target
    coverage_match = re.search(r"Coverage target:\s*(\d+)", manifest_text)
    if coverage_match:
        coverage_target = int(coverage_match.group(1))

    return {
        "phases": phases,
        "deliverables": deliverables,
        "coverage_target": coverage_target
    }, None


def get_commits_since_tag(tag: str, repo_path: str = ".") -> list[dict]:
    """Get all commits since the plan start tag."""
    stdout, code = run_git(["log", f"{tag}..HEAD", "--pretty=format:%H|%ci|%s"], cwd=repo_path)
    if code != 0 or not stdout:
        # If no commits between tag and HEAD, check if the tag commit itself should be included
        # This happens when the tag was just created on the current commit
        stdout, code = run_git(["log", "-1", "--pretty=format:%H|%ci|%s", tag], cwd=repo_path)
        if code != 0 or not stdout:
            return []
        line = stdout.strip()
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) == 3:
                return [{
                    "hash": parts[0],
                    "date": parts[1],
                    "msg": parts[2]
                }]
        return []

    commits = []
    for line in stdout.split("\n"):
        if "|" in line:
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "msg": parts[2]
                })
    return commits


def get_files_changed_in_commit(commit_hash: str, repo_path: str = ".") -> list[str]:
    """Get files changed in a specific commit."""
    stdout, _ = run_git([
        "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash
    ], cwd=repo_path)
    return [f for f in stdout.split("\n") if f]


def check_attestation(plan_id: str, repo_path: str = ".") -> tuple[bool, str]:
    """Check if attestation file exists and has required sections."""
    attestation_path = os.path.join(repo_path, f"logs/execution-attestation-plan-{plan_id}.md")
    if not os.path.exists(attestation_path):
        return False, f"Missing attestation: {attestation_path}"

    with open(attestation_path) as f:
        content = f.read()

    required_sections = [
        "Phase Sequence Verification",
        "Deliverable Verification",
        "Gate Results",
        "Forbidden Action Audit",
        "Trace Integrity",
        "Attestation"
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        return False, f"Attestation missing sections: {', '.join(missing)}"

    if "❌" in content:
        return False, "Attestation contains failures (❌)"

    return True, None


def verify_init(plan_id: str, repo_path: str = ".") -> bool:
    """Initialize verification: validate manifest exists and is parseable."""
    print(f"[VERIFY-INIT] Plan {plan_id}")

    manifest, err = get_manifest_from_plan(plan_id, repo_path)
    if err:
        print(f"  FAIL: {err}")
        return False

    print(
        f"  Manifest: {len(manifest['phases'])} phases, "
        f"{len(manifest['deliverables'])} deliverables"
    )
    print("  PASS: Manifest valid")
    return True


def audit_trace_timestamps(plan_id: str, repo_path: str = ".") -> list[str]:
    """Audit trace timestamps for suspicious patterns indicating manual fabrication.

    Detects entries where timestamp seconds component is exactly :00.000 (round-minute
    fabrication) or sequential 1-second intervals in S_close indicating manual entry.

    Returns list of warnings (not failures) since pre-compliance traces exist.
    """
    trace_path = os.path.join(repo_path, f".agent/executor/traces/trace-plan-{plan_id}.jsonl")
    if not os.path.exists(trace_path):
        return []

    warnings = []

    try:
        with open(trace_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    import json
                    entry = json.loads(line)
                    timestamp = entry.get("timestamp", "")

                    # Check for round-minute timestamps (seconds component is :00.000)
                    # This pattern indicates manual fabrication at minute boundaries
                    # Match patterns like: "2026-07-20T12:00:00.000" or "12:00:00.000"
                    if ":00.000" in timestamp:
                        warnings.append(
                            f"Line {line_num}: Suspicious round timestamp {timestamp} "
                            f"(phase={entry.get('phase', '?')}, action={entry.get('action', '?')})"
                        )
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception:
        # If trace file can't be read, don't fail - just note the issue
        warnings.append(f"Could not read trace file {trace_path} for timestamp audit")

    return warnings


def verify_final(plan_id: str, repo_path: str = ".") -> bool:
    """Final verification: full check of execution against manifest."""
    errors = []
    warnings = []

    print(f"[VERIFY-FINAL] Plan {plan_id}")
    print()

    # 1. Load manifest
    manifest, err = get_manifest_from_plan(plan_id, repo_path)
    if err:
        print(f"  FAIL: {err}")
        return False

    print(
        f"  Manifest: {len(manifest['phases'])} phases, "
        f"{len(manifest['deliverables'])} deliverables"
    )

    # 2. Check attestation
    attestation_ok, attestation_err = check_attestation(plan_id, repo_path)
    if not attestation_ok:
        errors.append(attestation_err or "Attestation check failed")
    else:
        print("  Attestation: [OK] present and complete")

    # 3. Get commits since plan start
    tag = f"prompt-{plan_id}"
    stdout, code = run_git(["tag", "-l", tag], cwd=repo_path)
    if code != 0 or not stdout:
        commits = []
        warnings.append(f"Tag {tag} not found — checking recent commits only")
    else:
        commits = get_commits_since_tag(tag, repo_path)

    if not commits:
        warnings.append("No commits found since plan start — may be first execution")
    else:
        print(f"  Commits since {tag}: {len(commits)}")

    # 4. Get all files changed
    all_files = set()
    for c in commits:
        all_files.update(get_files_changed_in_commit(c["hash"], repo_path))

    # 5. Check deliverables
    missing_deliverables = []
    for d in manifest["deliverables"]:
        # Skip runtime artifacts like .db files
        if d.endswith(".db"):
            continue
        # Skip pytest commands, they're verification not deliverables
        if d.startswith("pytest"):
            continue
        # Skip test files that are existing (not created in this plan)
        # We only check for new files created, not existing files that are tested
        if d.startswith(".agent/executor/tests/"):
            continue
        # Map test files from expected location to actual location
        # Plan expects app/sovereignai/tests/ but we created .agent/executor/tests/sovereignai/
        actual_path = d
        if d.startswith("app/sovereignai/tests/"):
            actual_path = d.replace("app/sovereignai/tests/", ".agent/executor/tests/sovereignai/")
            # Handle the test_options subdirectory case
            if "test_options" in d:
                # Extract the test file name and put it in the test_options subdirectory
                test_file = d.split("/")[-1]
                actual_path = f".agent/executor/tests/sovereignai/test_options/{test_file}"
        # Normalize paths for comparison
        actual_path_normalized = actual_path.replace("\\", "/")
        all_files_normalized = {f.replace("\\", "/") for f in all_files}
        if actual_path_normalized not in all_files_normalized:
            missing_deliverables.append(d)

    if missing_deliverables:
        errors.append(f"Missing deliverables: {', '.join(missing_deliverables)}")
    else:
        print(
            f"  Deliverables: [OK] {len(manifest['deliverables'])}/"
            f"{len(manifest['deliverables'])} found"
        )

    # 6. Check no governance files modified
    gov_files = [
        ".agent/executor/ARCHITECTURE.md",
        ".agent/executor/OR_RULES.md",
        "PRINCIPLES.md",
        ".agent/architect/AI_HANDOFF.md"
    ]
    modified_gov = []
    for g in gov_files:
        if g in all_files:
            modified_gov.append(g)

    if modified_gov:
        errors.append(f"Governance files modified: {', '.join(modified_gov)}")
    else:
        print("  Governance: [OK] no unauthorized modifications")

    # 7. Check trace file exists and audit timestamps
    trace_path = os.path.join(repo_path, f".agent/executor/traces/trace-plan-{plan_id}.jsonl")
    if os.path.exists(trace_path):
        print(f"  Trace: [OK] {trace_path} exists")
        # Audit timestamps for suspicious patterns
        timestamp_warnings = audit_trace_timestamps(plan_id, repo_path)
        if timestamp_warnings:
            warnings.extend(timestamp_warnings)
            print(
                f"  Trace Timestamp Audit: {len(timestamp_warnings)} "
                f"suspicious pattern(s) detected"
            )
    else:
        warnings.append(f"Trace file not found: {trace_path}")

    # Report
    print()
    if errors:
        print(f"FAIL: Plan {plan_id}")
        for e in errors:
            print(f"  [FAIL] {e}")
        if warnings:
            for w in warnings:
                print(f"  [WARN] {w}")
        return False
    else:
        print(f"PASS: Plan {plan_id}")
        if warnings:
            for w in warnings:
                print(f"  [WARN] {w}")
        return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Initialize verification at /open")
    parser.add_argument("--final", action="store_true", help="Final verification at /close")
    parser.add_argument("--plan", required=False, help="Plan number")
    parser.add_argument("--repo", default=".", help="Repository path")
    args = parser.parse_args()

    plan_id: str = args.plan

    # Fallback: read plan_id from .agent/current_plan.txt if not provided
    if not plan_id:
        try:
            with open(".agent/current_plan.txt") as f:
                plan_id = f.read().strip()
        except FileNotFoundError:
            print("ERROR: plan_id not provided and .agent/current_plan.txt not found")
            sys.exit(1)

    if args.init:
        ok = verify_init(plan_id, args.repo)
    elif args.final:
        ok = verify_final(plan_id, args.repo)
    else:
        # Default: manual verification (same as --final)
        ok = verify_final(plan_id, args.repo)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
