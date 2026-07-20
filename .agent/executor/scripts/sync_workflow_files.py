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
    sync_file(".devin/skills/close/SKILL.md", "skills-close-SKILL.md", workflow_dir)
    sync_file(".devin/skills/open/SKILL.md", "skills-open-SKILL.md", workflow_dir)
    sync_file(".devin/skills/scan/SKILL.md", "skills-scan-SKILL.md", workflow_dir)
    sync_file(".devin/skills/verify/SKILL.md", "skills-verify-SKILL.md", workflow_dir)
    
    # Executor framework
    sync_file(".agent/executor/ARCHITECTURE.md", "executor-ARCHITECTURE.md", workflow_dir)
    sync_file(".agent/executor/ATTESTATION_TEMPLATE.md", "executor-ATTESTATION_TEMPLATE.md", workflow_dir)
    sync_file(".agent/executor/OR_RULES.md", "executor-OR_RULES.md", workflow_dir)
    
    # Executor scripts
    sync_file(".agent/executor/scripts/verify_execution.py", "executor-scripts-verify_execution.py", workflow_dir)
    sync_file(".agent/executor/scripts/verify_close.py", "executor-scripts-verify_close.py", workflow_dir)
    sync_file(".agent/executor/scripts/run_failing_tests.py", "executor-scripts-run_failing_tests.py", workflow_dir)
    
    # Executor hooks
    sync_file(".agent/executor/hooks/append_trace.py", "executor-hooks-append_trace.py", workflow_dir)
    sync_file(".agent/executor/hooks/check_manifest.py", "executor-hooks-check_manifest.py", workflow_dir)
    sync_file(".agent/executor/hooks/preflight_check.py", "executor-hooks-preflight_check.py", workflow_dir)
    sync_file(".agent/executor/hooks/verify_attestation.py", "executor-hooks-verify_attestation.py", workflow_dir)
    
    # Executor AR checks
    sync_file(".agent/executor/scripts/ar_checks/run_all.py", "executor-scripts-ar_checks-run_all.py", workflow_dir)
    sync_file(".agent/executor/scripts/ar_checks/spec_match.py", "executor-scripts-ar_checks-spec_match.py", workflow_dir)
    
    # Executor landmine checks
    sync_file(".agent/executor/scripts/landmine_checks/run_all.py", "executor-scripts-landmine_checks-run_all.py", workflow_dir)
    
    # Executor OR checks
    sync_file(".agent/executor/scripts/or_checks/run_all.py", "executor-scripts-or_checks-run_all.py", workflow_dir)
    
    # Architect framework
    sync_file(".agent/architect/PRINCIPLES.md", "architect-PRINCIPLES.md", workflow_dir)
    sync_file(".agent/architect/AI_HANDOFF.md", "architect-AI_HANDOFF.md", workflow_dir)
    
    # Root governance
    sync_file("AGENTS.md", "AGENTS.md", workflow_dir)
    
    print("\nWorkflow files synced successfully!")


if __name__ == "__main__":
    main()