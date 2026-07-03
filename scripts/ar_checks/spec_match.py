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
        if path.startswith(
            "sovereignai/"
        ) or path.startswith("web/") or path.startswith("tui/") or path.startswith(
            "adapters/"
        ):
            paths.add(path)

    return paths


def get_baseline_tag(plan_path: Path) -> str:
    content = plan_path.read_text()
    match = re.search(r'Depends on:\s*(.+)', content)
    if match:
        depends = match.group(1).strip()
        if depends.lower() == "none":
            return "none"
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
    if baseline == "none":
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout.strip():
                lines = result.stdout.strip().splitlines()
                return set(line.split()[1] for line in lines if len(line.split()) > 1)
            return set()
        except subprocess.CalledProcessError:
            print("Failed to get git status")
            sys.exit(1)
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
    "pyproject.toml",
    "txt/requirements.txt",
    ".gitignore",
    ".open_hash",
    "sailogs/.gitkeep",
    "scripts/verify_syntax.py",
    "scripts/check_rule_crossrefs.py",
    "scripts/check_ar7_allowlist.py",
    "scripts/get_current_plan.py",
    "scripts/ar_checks/run_all.py",
    "scripts/ar_checks/check_tracing_allowlist.txt",
    "tests/test_verify_syntax.py",
    "tests/test_check_rule_crossrefs.py",
    "tests/test_check_ar7_allowlist.py",
    "tests/test_get_current_plan.py",
    "tests/test_run_all.py",
    "tests/test_trace_emitter_bounded_queue.py",
    "tests/test_correlation_id.py",
    "efficiency-audit-brief.md",
    "documents/AGENTS-OR73-patch.md",
    "documents/SovereignAI_Architecture_Decisions.md",
    "documents/SovereignAI_Skill_Agent_System_Design_v1.0.md",
    "documents/project-vision-Rev1.md",
    "documents/project-vision-Rev2.md",
    "documents/project-vision-Rev3.md",
    "documents/project-vision-Rev4.md",
    "documents/round-table-vision-Rev1-brief.md",
    "documents/round-table-vision-Rev2-brief.md",
    "documents/round-table-vision-Rev3-brief.md",
    "documents/round-table-vision-Rev4-brief.md",
    "documents/session-context-plans-16-19.md",
    "documents/sovereignai_rescan1.md",
    "sovereignai/shared/trace_emitter.py",
}


def main() -> None:
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

    if baseline == "none":
        missing_in_diff = will_edit_paths - diff_files
        if missing_in_diff:
            print(f"Missing in diff (Depends on: none): {missing_in_diff}")
            sys.exit(1)

        unexpected_in_diff = diff_files - will_edit_paths - ALLOWLIST
        unexpected_in_diff = {
            p for p in unexpected_in_diff
            if not p.startswith(".devin/skills/")
            and not p.startswith(".devin/workflows/")
            and not p.startswith("tests/")
            and not p.startswith("documents/plan-")
            and not p.startswith("prompts/plan-")
            and not p.startswith("prompts/completed/")
            and not p.startswith("logs/")
            and not p.startswith("scripts/ar_checks/")
            and not p.startswith("txt/")
        }

        if unexpected_in_diff:
            print(f"Unexpected in diff (Depends on: none): {unexpected_in_diff}")
            sys.exit(1)
    else:
        missing_in_diff = will_edit_paths - diff_files
        if missing_in_diff:
            print(f"Missing in diff: {missing_in_diff}")
            sys.exit(1)

        unexpected_in_diff = diff_files - all_plan_will_paths - ALLOWLIST
        unexpected_in_diff = {
            p for p in unexpected_in_diff
            if not p.startswith(".devin/skills/")
            and not p.startswith(".devin/workflows/")
            and not p.startswith("tests/")
            and not p.startswith("documents/plan-")
            and not p.startswith("prompts/plan-")
            and not p.startswith("prompts/completed/")
            and not p.startswith("logs/")
            and not p.startswith("scripts/ar_checks/")
            and not p.startswith("txt/")
        }

        if unexpected_in_diff:
            print(f"Unexpected in diff: {unexpected_in_diff}")
            sys.exit(1)

    print("spec match clean")
    sys.exit(0)


if __name__ == "__main__":
    main()
