#!/usr/bin/env python3
"""
Organize log files from logs root into numbered subfolders.
This runs at /open to organize logs created during plan execution.
"""

import re
import shutil
from pathlib import Path


def get_plan_number(filename: str) -> int | None:
    """Extract plan number from filename like 'execution-log-plan-25-Rev1.md'."""
    # Try to match plan- or prompt- followed by a number
    match = re.search(r'(?:plan|prompt)-(\d+)', filename)
    if match:
        return int(match.group(1))
    return None


def organize_logs() -> None:
    logs_dir = Path("logs").resolve()
    subfolders = {
        "0-9": lambda n: 0 <= n <= 9,
        "10-19": lambda n: 10 <= n <= 19,
        "20-29": lambda n: 20 <= n <= 29,
        "30-39": lambda n: 30 <= n <= 39,
    }

    # Create subfolders if they don't exist
    for subfolder in subfolders:
        (logs_dir / subfolder).mkdir(exist_ok=True)
    (logs_dir / "Misc").mkdir(exist_ok=True)

    # Move log files from root to appropriate subfolders
    for log_file in logs_dir.glob("*.md"):
        plan_num = get_plan_number(log_file.name)

        if plan_num is None:
            # No plan number - move to Misc
            dest_folder = logs_dir / "Misc"
        else:
            # Find appropriate folder based on plan number
            dest_folder = logs_dir / "Misc"  # Default to Misc
            for subfolder, condition in subfolders.items():
                if condition(plan_num):
                    dest_folder = logs_dir / subfolder
                    break

        # Skip if file is already in a subfolder
        if log_file.parent != logs_dir:
            continue

        dest_path = dest_folder / log_file.name
        if dest_path.exists():
            # Handle conflicts - overwrite with current file
            dest_path.unlink()

        shutil.move(str(log_file), str(dest_path))
        print(f"Moved: {log_file.name} -> {dest_folder.name}/")


if __name__ == "__main__":
    organize_logs()
