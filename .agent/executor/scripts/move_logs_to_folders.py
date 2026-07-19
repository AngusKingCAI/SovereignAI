#!/usr/bin/env python3
"""
Move log files from root back to their appropriate numbered folders.
This organizes logs after plan execution is complete.
"""

import os
import shutil
import re
from pathlib import Path

def get_folder_for_log(filename):
    """Determine which folder a log file belongs to based on its name."""
    # Plan logs always go to Misc
    if 'execution-log-plan-' in filename:
        return "Misc"
    
    # Check for numbered patterns in prompt logs
    match = re.search(r'execution-log-prompt-(\d+)', filename)
    if match:
        number = int(match.group(1))
        if number < 10:
            return "1-9"
        elif 10 <= number < 20:
            return "10-19"
        elif 20 <= number < 30:
            return "20-29"
    
    # Default to Misc for non-numbered or out-of-range files
    return "Misc"

def move_logs_to_folders():
    logs_dir = Path("c:/SovereignAI/logs")
    
    for log_file in logs_dir.glob("*.md"):
        # Skip if file is in a subfolder already
        if log_file.parent != logs_dir:
            continue
            
        folder_name = get_folder_for_log(log_file.name)
        dest_folder = logs_dir / folder_name
        dest_folder.mkdir(exist_ok=True)
        
        dest_path = dest_folder / log_file.name
        shutil.move(str(log_file), str(dest_path))
        print(f"Moved: {log_file.name} -> {folder_name}/")

if __name__ == "__main__":
    move_logs_to_folders()
