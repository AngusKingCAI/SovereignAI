#!/usr/bin/env python3
"""
Move completed plan files and all their revisions to prompts/completed/.

This script is called during /close to move the completed plan and all its
previous revisions to the completed directory.
"""

import re
import shutil
from pathlib import Path


def get_plan_number_and_rev(filename: str) -> tuple[int, int] | None:
    """Extract plan number and revision from filename like 'plan-29-Rev5.md' or 'plan-21-rev10.md'."""
    # Try standard Rev format first
    match = re.search(r'plan-(\d+)-Rev(\d+)\.md', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    # Try lowercase rev format
    match = re.search(r'plan-(\d+)-rev(\d+)\.md', filename)
    if match:
        return int(match.group(1)), int(match.group(2))
    
    return None


def move_completed_plans(plan_number: int) -> None:
    """Move all revisions of a completed plan to the completed directory."""
    prompts_dir = Path("prompts")
    completed_dir = prompts_dir / "completed"
    
    if not completed_dir.exists():
        completed_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all revisions of the plan (both Rev and rev formats)
    plan_files = list(prompts_dir.glob(f"plan-{plan_number}-Rev*.md"))
    plan_files.extend(prompts_dir.glob(f"plan-{plan_number}-rev*.md"))
    
    # Remove duplicates and filter out files that don't exist
    plan_files = list(set(plan_files))
    plan_files = [f for f in plan_files if f.exists()]
    
    if not plan_files:
        print(f"No plan files found for plan-{plan_number}")
        return
    
    # Move each revision
    moved_count = 0
    for plan_file in plan_files:
        # Skip if file is already in completed directory
        if plan_file.parent != prompts_dir:
            print(f"Skipped: {plan_file.name} (already in completed/)")
            continue
        
        plan_info = get_plan_number_and_rev(plan_file.name)
        if plan_info:
            dest_path = completed_dir / plan_file.name
            if dest_path.exists():
                # File already in completed - overwrite
                dest_path.unlink()
            
            try:
                shutil.move(str(plan_file), str(dest_path))
                print(f"Moved: {plan_file.name} -> completed/")
                moved_count += 1
            except Exception as e:
                print(f"Error moving {plan_file.name}: {e}")
    
    print(f"Moved {moved_count} revision(s) of plan-{plan_number} to completed/")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: move_completed_plans.py <plan-number>")
        sys.exit(1)
    
    plan_number = int(sys.argv[1])
    move_completed_plans(plan_number)
