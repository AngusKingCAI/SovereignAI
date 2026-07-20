#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path


def extract_will_edit_paths(plan_path: Path) -> set[str]:
    content = plan_path.read_text(encoding='utf-8')
    paths = set()

    pattern = r'^\s*[-*]\s+`?([\w./-]+\.[a-zA-Z0-9]+)'
    for match in re.finditer(pattern, content, re.MULTILINE):
        path = match.group(1)
        if path.startswith(
            "app/sovereignai/"
        ) or path.startswith("app/web/") or path.startswith("app/tui/") or path.startswith(
            "app/adapters/"
        ):
            paths.add(path)

    return paths


def get_baseline_tag(plan_path: Path) -> str:
    content = plan_path.read_text(encoding='utf-8')
    match = re.search(r'\*?\*?Depends on\*?\*?:\s*(.+)', content)
    if match:
        depends = match.group(1).strip()
        if depends.lower() == "none":
            return "none"
        # Plans write either "plan-N[.M...]", "Plan N[.M...]", or "plan-fix-N-RevX" — accept all.
        # Also accept legacy "prompt-N[.M...]" for backward-compat with older plans.
        tag_match = re.search(r'plan-[\d.]+', depends)
        if tag_match:
            return tag_match.group(0)
        # Backward-compat: fall back to prompt-N if plan-N not found
        prompt_match = re.search(r'prompt-[\d.]+', depends)
        if prompt_match:
            return prompt_match.group(0)
        plan_match = re.search(r'Plan\s+([\d.]+)', depends, re.IGNORECASE)
        if plan_match:
            return f"plan-{plan_match.group(1)}"
        fix_match = re.search(r'plan-fix-\d+-Rev\d+', depends)
        if fix_match:
            return fix_match.group(0)
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
                return {line.split()[1] for line in lines if len(line.split()) > 1}
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
    plans_dir = Path("plans")
    all_paths = set()

    for plan_file in plans_dir.rglob("plan-*.md"):
        paths = extract_will_edit_paths(plan_file)
        all_paths.update(paths)

    return all_paths


ALLOWLIST = {
    "AGENTS.md",
    ".agent/shared/LANDMINES.md",
    ".agent/shared/PLANS.md",
    ".agent/shared/DEBT.md",
    ".agent/shared/DECISIONS.md",
    ".agent/shared/CHANGELOG.md",
    ".agent/architect/AI_HANDOFF.md",
    "pyproject.toml",
    "app/txt/requirements.txt",
    ".gitignore",
    ".open_hash",
    "app/logs/.gitkeep",
    ".agent/executor/scripts/verify_syntax.py",
    ".agent/executor/scripts/check_ar4_allowlist.py",
    ".agent/executor/scripts/get_current_plan.py",
    ".agent/executor/scripts/get_plan_rules.py",
    ".agent/executor/scripts/generate_rules_cache.py",
    ".agent/executor/scripts/check_all_lightweight.py",
    ".agent/executor/scripts/ar_checks/run_all_ar_checks.py",
    ".agent/executor/scripts/ar_checks/check_tracing_allowlist.txt",
    ".agent/executor/scripts/ar_checks/check_component_manifest_kwargs_ast.py",
    ".agent/executor/scripts/ar_checks/check_rule_crossrefs_ar.py",
    ".agent/executor/scripts/ar_checks/check_rule_crossrefs_doc.py",
    ".agent/executor/scripts/landmine_checks/run_all_landmine_checks.py",
    ".agent/executor/scripts/or_checks/run_all_or_checks.py",
    ".agent/executor/tests/test_verify_syntax.py",
    ".agent/executor/tests/test_check_ar4_allowlist.py",
    ".agent/executor/tests/test_ar4_no_core_imports_in_ui.py",
    ".agent/executor/tests/test_check_component_manifest_kwargs_ast.py",
    ".agent/executor/tests/test_check_rule_crossrefs_ar.py",
    ".agent/executor/tests/test_check_rule_crossrefs_doc.py",
    ".agent/executor/tests/test_run_all_landmine_checks.py",
    ".agent/executor/tests/test_run_all_or_checks.py",
    ".agent/executor/tests/test_get_current_plan.py",
    ".agent/executor/tests/test_trace_emitter_bounded_queue.py",
    ".agent/executor/tests/test_correlation_id.py",
    ".agent/executor/tests/test_document_hygiene.py",
    ".agent/architect/efficiency-audit-brief.md",
    ".agent/architect/documents/AGENTS-OR73-patch.md",
    ".agent/architect/documents/SovereignAI_Architecture_Decisions.md",
    ".agent/architect/documents/SovereignAI_Cross_Department_Messaging_Design_v1.0.md",
    ".agent/architect/documents/SovereignAI_Skill_Agent_System_Design_v1.0.md",
    ".agent/architect/documents/project-vision-Rev1.md",
    ".agent/architect/documents/project-vision-Rev2.md",
    ".agent/architect/documents/project-vision-Rev3.md",
    ".agent/architect/documents/project-vision-Rev4.md",
    ".agent/architect/documents/round-table-vision-Rev1-brief.md",
    ".agent/architect/documents/round-table-vision-Rev2-brief.md",
    ".agent/architect/documents/round-table-vision-Rev3-brief.md",
    ".agent/architect/documents/round-table-vision-Rev4-brief.md",
    ".agent/architect/documents/session-context-plans-16-19.md",
    ".agent/architect/documents/sovereignai_rescan1.md",
    "app/sovereignai/shared/trace_emitter.py",
    ".agent/executor/scripts/ar_checks/spec_match.py",
    "app/sovereignai/shared/event_registry.py",
    "app/sovereignai/shared/events.py",
    ".agent/executor/scripts/ar_checks/check_event_registration.py",
    ".agent/executor/scripts/ar_checks/check_event_frozen.py",
    ".agent/executor/scripts/ar_checks/check_component_manifest_kwargs_ar15.py",
    ".agent/executor/scripts/ar_checks/check_options_encryption_at_rest.py",
    ".agent/executor/tests/app_tests/test_typed_event_bus.py",
    ".agent/executor/tests/app_tests/test_event_registry.py",
    ".agent/executor/tests/app_tests/test_async_delivery.py",
    ".agent/executor/tests/app_tests/test_hardware_stream_requires_cookie.py",
    ".agent/executor/tests/app_tests/test_events_api.py",
    ".agent/executor/tests/app_tests/test_check_event_registration.py",
    ".agent/executor/tests/app_tests/test_check_event_frozen.py",
    "app/web/schemas.py",
    ".devin/skills/close/SKILL.md",
    ".devin/skills/open/SKILL.md",
    ".devin/skills/verify/SKILL.md",
    ".devin/workflows/close.md",
    ".devin/workflows/review.md",
    "app/sovereignai/managers/base.py",
    "app/sovereignai/managers/coding.py",
    "app/sovereignai/managers/types.py",
    "app/sovereignai/managers/__init__.py",
    "app/sovereignai/indexing/symbol_map.py",
    "app/sovereignai/indexing/__init__.py",
    "app/sovereignai/memory/graph_backend.py",
    "app/sovereignai/agent/__init__.py",
    "app/sovereignai/agent/factory.py",
    "app/sovereignai/agent/react.py",
    "app/sovereignai/main.py",
    "app/skills/official/file_edit/skill.py",
    "app/skills/official/file_edit/manifest.toml",
    "app/skills/official/file_edit/dag.json",
    "app/skills/official/file_edit/__init__.py",
    "app/tui/panels/workers.py",
    "app/web/main.py",
    ".agent/executor/tests/sovereignai/test_department_manager.py",
    ".agent/executor/tests/sovereignai/test_file_edit_skill.py",
    ".agent/executor/tests/sovereignai/test_symbol_map.py",
    ".agent/executor/tests/sovereignai/test_symbol_map_degraded.py",
    ".agent/executor/tests/sovereignai/test_symbol_map_tree_sitter.py",
    ".agent/executor/tests/sovereignai/test_symbol_map_latency_budget.py",
    ".agent/executor/tests/sovereignai/test_graph_memory.py",
    ".agent/executor/tests/sovereignai/test_department_full_cycle.py",
    ".agent/executor/tests/sovereignai/test_departments_api.py",
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
            and not p.startswith("plans/plan-")
            and not p.startswith("plans/completed/")
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
            and not p.startswith("plans/plan-")
            and not p.startswith("plans/completed/")
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
