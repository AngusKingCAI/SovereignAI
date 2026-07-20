#!/usr/bin/env python3
"""
Move completed plan files and all their revisions to prompts/completed/.

This script is called during /close to move the completed plan and all its
previous revisions to the completed directory. It also moves associated brief
batch files (brief-batch{N}-{M}.md) that include this plan number in their range.
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


def get_brief_plan_numbers(filename: str) -> list[int] | None:
    """Extract plan numbers from brief filename like 'brief-batch31-34-Rev1.md'."""
    match = re.search(r'brief-batch(\d+)-(\d+)', filename)
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        return list(range(start, end + 1))
    return None


def get_target_folder(plan_number: int) -> str:
    """Determine the target folder for a plan number based on numbered ranges."""
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


def move_completed_plans(plan_number: int) -> None:
    """Move all revisions of a completed plan and associated brief files to the completed directory."""
    prompts_dir = Path("prompts")
    completed_dir = prompts_dir / "completed"
    
    if not completed_dir.exists():
        completed_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine target folder based on plan number
    target_folder = get_target_folder(plan_number)
    target_dir = completed_dir / target_folder
    
    if not target_dir.exists():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all revisions of the plan (both Rev and rev formats)
    plan_files = list(prompts_dir.glob(f"plan-{plan_number}-Rev*.md"))
    plan_files.extend(prompts_dir.glob(f"plan-{plan_number}-rev*.md"))
    
    # Find associated brief batch files (brief-batch{N}*.md)
    brief_files = list(prompts_dir.glob("brief-batch*.md"))
    
    # Filter brief files that include this plan number in their range
    matching_briefs = []
    for brief_file in brief_files:
        plan_numbers = get_brief_plan_numbers(brief_file.name)
        if plan_numbers and plan_number in plan_numbers:
            matching_briefs.append(brief_file)
    
    # Combine all files to move
    all_files = plan_files + matching_briefs
    
    # Remove duplicates and filter out files that don't exist
    all_files = list(set(all_files))
    all_files = [f for f in all_files if f.exists()]
    
    if not all_files:
        print(f"No plan files found for plan-{plan_number}")
        return
    
    # Move each file
    moved_count = 0
    for file_path in all_files:
        # Skip if file is already in completed directory
        if file_path.parent != prompts_dir:
            print(f"Skipped: {file_path.name} (already in completed/)")
            continue
        
        dest_path = target_dir / file_path.name
        if dest_path.exists():
            # File already in completed - overwrite
            dest_path.unlink()
        
        try:
            shutil.move(str(file_path), str(dest_path))
            file_type = "plan file" if "plan-" in file_path.name else "brief file"
            print(f"Moved: {file_path.name} -> completed/{target_folder}/ ({file_type})")
            moved_count += 1
        except Exception as e:
            print(f"Error moving {file_path.name}: {e}")
    
    print(f"Moved {moved_count} file(s) of plan-{plan_number} to completed/{target_folder}/")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: move_completed_plans.py <plan-number>")
        sys.exit(1)
    
    plan_number = int(sys.argv[1])
    move_completed_plans(plan_number)
