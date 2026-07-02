#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path


def extract_will_edit_paths(plan_path: Path) -> set[str]:
    content = plan_path.read_text()
    paths = set()

    pattern = r'^\s*[-*]\s+`?([\w./-]+\.[a-zA-Z0-9]+)'
    for match in re.finditer(pattern, content, re.MULTILINE):
        path = match.group(1)
        if path.startswith("sovereignai/") or path.startswith("web/") or path.startswith("tui/"):
            paths.add(path)

    return paths


def get_baseline_tag(plan_path: Path) -> str:
    content = plan_path.read_text()
    match = re.search(r'Depends on:\s*(.+)', content)
    if match:
        depends = match.group(1).strip()
        # Plans write either "prompt-N[.M...]" or "Plan N[.M...]" — accept both.
        tag_match = re.search(r'prompt-[\d.]+', depends)
        if tag_match:
            return tag_match.group(0)
        plan_match = re.search(r'Plan\s+([\d.]+)', depends, re.IGNORECASE)
        if plan_match:
            return f"prompt-{plan_match.group(1)}"
        print(f"Could not parse baseline from 'Depends on: {depends}' in {plan_path}")
        sys.exit(1)
    print(f"No 'Depends on:' line found in {plan_path}")
    sys.exit(1)


def get_diff_files(baseline: str) -> set[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{baseline}..HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return set(result.stdout.strip().splitlines()) if result.stdout.strip() else set()
    except subprocess.CalledProcessError:
        print(f"Failed to get diff from baseline {baseline}")
        sys.exit(1)


def get_all_plan_will_paths() -> set[str]:
    plans_dir = Path("prompts")
    all_paths = set()

    for plan_file in plans_dir.glob("plan-*.md"):
        paths = extract_will_edit_paths(plan_file)
        all_paths.update(paths)

    return all_paths


ALLOWLIST = {
    "AGENTS.md",
    "LANDMINES.md",
    "PLANS.md",
    "DEBT.md",
    "DECISIONS.md",
    "CHANGELOG.md",
    "AI_HANDOFF.md",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: spec_match.py <plan_file>")
        sys.exit(1)

    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        print(f"Plan file {plan_path} not found")
        sys.exit(1)

    will_edit_paths = extract_will_edit_paths(plan_path)
    baseline = get_baseline_tag(plan_path)
    diff_files = get_diff_files(baseline)
    all_plan_will_paths = get_all_plan_will_paths()

    missing_in_diff = will_edit_paths - diff_files
    if missing_in_diff:
        print(f"Missing in diff: {missing_in_diff}")
        sys.exit(1)

    unexpected_in_diff = diff_files - all_plan_will_paths - ALLOWLIST
    unexpected_in_diff = {
        p for p in unexpected_in_diff
        if not p.startswith(".devin/skills/")
        and not p.startswith("tests/")
        and not p.startswith("documents/plan-")
        and not p.startswith("prompts/plan-")  # noqa: E501
        # plan files are governance artifacts (Architect-authored), not Devin edits
        and not p.startswith("prompts/completed/")  # moved plan files
        and not p.startswith("logs/")  # execution logs are artifacts, not code
        and not p.startswith("scripts/ar_checks/")  # AR check scripts are governance artifacts
    }

    if unexpected_in_diff:
        print(f"Unexpected in diff: {unexpected_in_diff}")
        sys.exit(1)

    print("spec match clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
