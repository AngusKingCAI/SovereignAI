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

import subprocess
import re
import sys
import os
import argparse


def run_git(args, cwd="."):
    """Run git command and return stdout."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.stdout.strip(), result.returncode


def get_manifest_from_plan(plan_id, repo_path="."):
    """Extract Executor Manifest from plan file."""
    plan_path = os.path.join(repo_path, f"prompts/plan-{plan_id}.md")
    if not os.path.exists(plan_path):
        return None, f"Plan file not found: {plan_path}"

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

    for line in manifest_text.split("\n"):
        line = line.strip()
        if line.startswith("Phases:"):
            phases = [p.strip() for p in line.replace("Phases:", "").split(",")]
        elif line.startswith("- S") and ":" in line:
            parts = line.split(":", 1)
            if len(parts) == 2:
                file_part = parts[1].strip()
                file_match = re.search(r"`([^`]+)`", file_part)
                if file_match:
                    deliverables.append(file_match.group(1))
                else:
                    first_word = file_part.split()[0]
                    if "." in first_word:
                        deliverables.append(first_word)
        elif line.startswith("Coverage target:"):
            coverage_match = re.search(r"(\d+)", line)
            if coverage_match:
                coverage_target = int(coverage_match.group(1))

    return {
        "phases": phases,
        "deliverables": deliverables,
        "coverage_target": coverage_target
    }, None


def get_commits_since_tag(tag, repo_path="."):
    """Get all commits since the plan start tag."""
    stdout, code = run_git(["log", f"{tag}..HEAD", "--pretty=format:%H|%ci|%s"], cwd=repo_path)
    if code != 0 or not stdout:
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


def get_files_changed_in_commit(commit_hash, repo_path="."):
    """Get files changed in a specific commit."""
    stdout, _ = run_git([
        "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash
    ], cwd=repo_path)
    return [f for f in stdout.split("\n") if f]


def check_attestation(plan_id, repo_path="."):
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


def verify_init(plan_id, repo_path="."):
    """Initialize verification: validate manifest exists and is parseable."""
    print(f"[VERIFY-INIT] Plan {plan_id}")

    manifest, err = get_manifest_from_plan(plan_id, repo_path)
    if err:
        print(f"  FAIL: {err}")
        return False

    print(f"  Manifest: {len(manifest['phases'])} phases, {len(manifest['deliverables'])} deliverables")
    print(f"  PASS: Manifest valid")
    return True


def verify_final(plan_id, repo_path="."):
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

    print(f"  Manifest: {len(manifest['phases'])} phases, {len(manifest['deliverables'])} deliverables")

    # 2. Check attestation
    attestation_ok, attestation_err = check_attestation(plan_id, repo_path)
    if not attestation_ok:
        errors.append(attestation_err)
    else:
        print(f"  Attestation: [OK] present and complete")

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
        if d not in all_files:
            missing_deliverables.append(d)

    if missing_deliverables:
        errors.append(f"Missing deliverables: {', '.join(missing_deliverables)}")
    else:
        print(f"  Deliverables: [OK] {len(manifest['deliverables'])}/{len(manifest['deliverables'])} found")

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
        print(f"  Governance: [OK] no unauthorized modifications")

    # 7. Check trace file exists
    trace_path = os.path.join(repo_path, f".agent/executor/traces/trace-plan-{plan_id}.jsonl")
    if os.path.exists(trace_path):
        print(f"  Trace: [OK] {trace_path} exists")
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Initialize verification at /open")
    parser.add_argument("--final", action="store_true", help="Final verification at /close")
    parser.add_argument("--plan", required=False, help="Plan number")
    parser.add_argument("--repo", default=".", help="Repository path")
    args = parser.parse_args()

    plan_id = args.plan

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
