#!/usr/bin/env python3
"""
Sync workflow-related files to the /Workflow folder for external AI review.
This script copies the latest versions of workflow files to the Workflow directory.
"""

import os
import shutil
from pathlib import Path


def sync_file(source_path: str, dest_name: str, workflow_dir: Path) -> None:
    """Copy a single file to the workflow directory."""
    source = Path(source_path)
    if not source.exists():
        print(f"Warning: Source file {source_path} does not exist, skipping")
        return
    
    dest = workflow_dir / dest_name
    shutil.copy2(source, dest)
    print(f"Copied: {source_path} -> {dest}")


def main():
    """Sync all workflow files."""
    workflow_dir = Path("Workflow")
    workflow_dir.mkdir(exist_ok=True)
    
    # Skills
    sync_file(".devin/skills/close/SKILL.md", "close-SKILL.md", workflow_dir)
    sync_file(".devin/skills/open/SKILL.md", "open-SKILL.md", workflow_dir)
    sync_file(".devin/skills/scan/SKILL.md", "scan-SKILL.md", workflow_dir)
    sync_file(".devin/skills/verify/SKILL.md", "verify-SKILL.md", workflow_dir)
    
    # Executor framework
    sync_file(".agent/executor/ARCHITECTURE.md", "ARCHITECTURE.md", workflow_dir)
    sync_file(".agent/executor/ATTESTATION_TEMPLATE.md", "ATTESTATION_TEMPLATE.md", workflow_dir)
    sync_file(".agent/executor/OR_RULES.md", "OR_RULES.md", workflow_dir)
    
    # Executor scripts
    sync_file(".agent/executor/scripts/verify_execution.py", "executor-scripts-verify_execution.py", workflow_dir)
    sync_file(".agent/executor/scripts/verify_close.py", "executor-scripts-verify_close.py", workflow_dir)
    sync_file(".agent/executor/scripts/run_failing_tests.py", "executor-scripts-run_failing_tests.py", workflow_dir)
    sync_file(".agent/executor/scripts/get_current_plan.py", "executor-scripts-get_current_plan.py", workflow_dir)
    sync_file(".agent/executor/scripts/get_scoped_tests.py", "executor-scripts-get_scoped_tests.py", workflow_dir)
    sync_file(".agent/executor/scripts/verify_syntax.py", "executor-scripts-verify_syntax.py", workflow_dir)
    sync_file(".agent/executor/scripts/check_import_paths.py", "executor-scripts-check_import_paths.py", workflow_dir)
    sync_file(".agent/executor/scripts/check_rule_crossrefs.py", "executor-scripts-check_rule_crossrefs.py", workflow_dir)
    sync_file(".agent/executor/scripts/move_completed_plans.py", "executor-scripts-move_completed_plans.py", workflow_dir)
    sync_file(".agent/executor/scripts/organize_logs.py", "executor-scripts-organize_logs.py", workflow_dir)
    sync_file(".agent/executor/scripts/check_component_manifest_kwargs.py", "executor-scripts-check_component_manifest_kwargs.py", workflow_dir)
    sync_file(".agent/executor/scripts/is_scan_plan.py", "executor-scripts-is_scan_plan.py", workflow_dir)
    
    # Executor hooks
    sync_file(".agent/executor/hooks/append_trace.py", "executor-hooks-append_trace.py", workflow_dir)
    sync_file(".agent/executor/hooks/check_manifest.py", "executor-hooks-check_manifest.py", workflow_dir)
    sync_file(".agent/executor/hooks/preflight_check.py", "executor-hooks-preflight_check.py", workflow_dir)
    sync_file(".agent/executor/hooks/verify_attestation.py", "executor-hooks-verify_attestation.py", workflow_dir)
    
    # Executor checks
    sync_file(".agent/executor/checks/check_model_registry_adapter_registry.py", "executor-checks-check_model_registry_adapter_registry.py", workflow_dir)
    sync_file(".agent/executor/checks/check_model_registry_no_direct_provider_calls.py", "executor-checks-check_model_registry_no_direct_provider_calls.py", workflow_dir)
    sync_file(".agent/executor/checks/check_model_registry_transaction_safety.py", "executor-checks-check_model_registry_transaction_safety.py", workflow_dir)
    sync_file(".agent/executor/checks/run_model_registry_ar_checks.py", "executor-checks-run_model_registry_ar_checks.py", workflow_dir)
    
    # Executor AR checks (root)
    sync_file(".agent/executor/ar_checks/check_options_encryption_at_rest.py", "executor-ar_checks-check_options_encryption_at_rest.py", workflow_dir)
    
    # Executor AR checks
    sync_file(".agent/executor/scripts/ar_checks/run_all.py", "executor-scripts-ar_checks-run_all.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/spec_match.py", "executor-scripts-ar_checks-spec_match.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_plan_immutability.py", "executor-scripts-ar_checks-check_plan_immutability.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_placeholders.py", "executor-scripts-ar_checks-check_placeholders.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_rule_crossrefs.py", "executor-scripts-ar_checks-check_rule_crossrefs.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_dependencies.py", "executor-scripts-ar_checks-check_dependencies.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_rule_conciseness.py", "executor-scripts-ar_checks-check_rule_conciseness.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_changelog.py", "executor-scripts-ar_checks-check_changelog.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_p4_compliance.py", "executor-scripts-ar_checks-check_p4_compliance.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/check_tracing.py", "executor-scripts-ar_checks-check_tracing.py", workflow_dir)
    
    # Executor landmine checks
    sync_file(".agent/executor/scripts/landmine_checks/run_all.py", "executor-scripts-landmine_checks-run_all.py", workflow_dir)
    sync_file(".agent/executor/scripts/landmine_checks/check_m1_import_paths.py", "executor-scripts-landmine_checks-check_m1_import_paths.py", workflow_dir)
    sync_file(".agent/executor/scripts/landmine_checks/check_m6_namespace_collision.py", "executor-scripts-landmine_checks-check_m6_namespace_collision.py", workflow_dir)
    sync_file(".agent/executor/scripts/landmine_checks/detect_m1.py", "executor-scripts-landmine_checks-detect_m1.py", workflow_dir)
    sync_file(".agent/executor/scripts/landmine_checks/detect_m4.py", "executor-scripts-landmine_checks-detect_m4.py", workflow_dir)
    
    # Executor OR checks
    sync_file(".agent/executor/scripts/or_checks/run_all.py", "executor-scripts-or_checks-run_all.py", workflow_dir)
    
    # Architect framework
    sync_file(".agent/architect/PRINCIPLES.md", "PRINCIPLES.md", workflow_dir)
    sync_file(".agent/architect/AI_HANDOFF.md", "AI_HANDOFF.md", workflow_dir)
    
    # Root governance
    sync_file("AGENTS.md", "AGENTS.md", workflow_dir)
    
    print("\nWorkflow files synced successfully!")


if __name__ == "__main__":
    main()