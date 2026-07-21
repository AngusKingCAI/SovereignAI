#!/usr/bin/env python3
"""
Move log files from root back to their appropriate numbered folders.
This organizes logs after plan execution is complete.
Accepts optional plan number to skip that plan's logs (current plan).
"""

import re
import shutil
import sys
from pathlib import Path


def get_folder_for_log(filename):
    """Determine which folder a log file belongs to based on its name."""
    # Extract plan number from execution-log-plan-N or execution-attestation-plan-N
    plan_match = re.search(r'execution-(?:log|attestation)-plan-(\d+)', filename)
    if plan_match:
        plan_number = int(plan_match.group(1))
        if plan_number < 10:
            return "0-9"
        elif plan_number < 20:
            return "10-19"
        elif plan_number < 30:
            return "20-29"
        elif plan_number < 40:
            return "30-39"
        else:
            return "Misc"

    # Check for numbered patterns in prompt logs
    match = re.search(r'execution-log-prompt-(\d+)', filename)
    if match:
        number = int(match.group(1))
        if number < 10:
            return "0-9"
        elif 10 <= number < 20:
            return "10-19"
        elif 20 <= number < 30:
            return "20-29"

    # Default to Misc for non-numbered or out-of-range files
    return "Misc"


def move_logs_to_folders(skip_plan_number=None):
    """Move log files to appropriate numbered subdirectories."""
    # Use proper path resolution instead of hardcoded path
    repo_root = Path(__file__).parent.parent.parent.parent
    logs_dir = repo_root / "logs"

    if not logs_dir.exists():
        print(f"Warning: logs directory not found at {logs_dir}")
        return

    for log_file in logs_dir.glob("*.md"):
        # Skip if file is in a subfolder already
        if log_file.parent != logs_dir:
            continue

        # Skip specified plan's logs (usually current plan)
        if skip_plan_number:
            plan_match = re.search(r'execution-(?:log|attestation)-plan-(\d+)', log_file.name)
            if plan_match and int(plan_match.group(1)) == skip_plan_number:
                print(f"Skipped: {log_file.name} (plan {skip_plan_number} log)")
                continue

        folder_name = get_folder_for_log(log_file.name)
        dest_folder = logs_dir / folder_name
        dest_folder.mkdir(exist_ok=True)

        dest_path = dest_folder / log_file.name
        shutil.move(str(log_file), str(dest_path))
        print(f"Moved: {log_file.name} -> {folder_name}/")


if __name__ == "__main__":
    # Accept optional plan number to skip
    skip_plan = None
    if len(sys.argv) > 1:
        try:
            skip_plan = int(sys.argv[1])
        except ValueError:
            print(f"Invalid plan number: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
    
    move_logs_to_folders(skip_plan_number=skip_plan)
