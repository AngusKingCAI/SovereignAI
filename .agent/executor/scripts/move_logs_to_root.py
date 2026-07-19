#!/usr/bin/env python3
"""
Move all log files from subfolders to logs root directory.
This makes logs easily accessible for pasting/editing during plan execution.
"""

import os
import shutil
from pathlib import Path

def move_logs_to_root():
    logs_dir = Path("c:/SovereignAI/logs")
    subfolders = ["1-9", "10-19", "20-29", "Misc"]
    
    for subfolder in subfolders:
        subfolder_path = logs_dir / subfolder
        if subfolder_path.exists():
            for log_file in subfolder_path.glob("*.md"):
                dest_path = logs_dir / log_file.name
                # Move file to root, overwriting if exists
                shutil.move(str(log_file), str(dest_path))
                print(f"Moved: {log_file.name} -> logs root")

if __name__ == "__main__":
    move_logs_to_root()
