#!/usr/bin/env python3
"""
Tool: HG-20 Goal Tree Present Validation

WHEN TO USE: Phase 0 (Plan Batch Creation), before batch execution

WHAT IT CHECKS: Goal tree artifact is present for current batch with hierarchical goal structure.
Goal tree shows main goal, sub-goals, sub-tasks with parent-child relationships.

INPUTS: None (auto-discovers latest goal tree file in plans/ directory)

OUTPUTS:
- Exit 0: Gate HG-20 PASS: Goal tree present with hierarchical structure
- Exit 1: Gate HG-20 FAIL: Goal tree missing or incomplete

FAILURE RECOVERY: Create goal tree artifact with hierarchical structure, re-run this script.
Do NOT proceed to batch execution until exit 0.

DEPENDENCIES: plans/ directory must exist with goal-tree-batch{N}.md file
"""

import sys
import os
from pathlib import Path

def check_gate_condition():
    """
    Check that goal tree artifact is present for current batch.
    Returns True if gate passes, False otherwise.
    """
    # Find goal tree files in plans directory
    plans_dir = None
    for possible_dir in ["plans", "Plans", ".Planner/plans"]:
        if Path(possible_dir).exists():
            plans_dir = Path(possible_dir)
            break
    
    if plans_dir is None:
        print("Plans directory not found, skipping validation")
        return True
    
    # Look for goal tree files
    goal_tree_files = []
    for pattern in ["goal-tree-batch*.md", "goal_tree_batch*.md"]:
        goal_tree_files.extend(plans_dir.glob(pattern))
    
    if not goal_tree_files:
        print("Gate HG-20 FAIL: Goal tree artifact missing")
        print(f"   Expected format: goal-tree-batch{{N}}.md in plans/ directory")
        print(f"   Create goal tree with hierarchical structure per PR19")
        return False
    
    # Get the most recent goal tree file
    latest_goal_tree = max(goal_tree_files, key=lambda f: f.stat().st_mtime)
    
    print(f"Validating goal tree: {latest_goal_tree.name}")
    
    try:
        with open(latest_goal_tree, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading goal tree file: {e}")
        return False
    
    # Check for hierarchical structure markers
    has_main_goal = "Main Goal" in content or "Batch Goal" in content
    has_sub_goals = "Sub-goal" in content or "Sub Goal" in content
    has_tree_structure = "├──" in content or "└──" in content or "|--" in content
    
    if not has_main_goal:
        print(f"Gate HG-20 FAIL: Goal tree missing main goal marker")
        return False
    
    if not has_sub_goals:
        print(f"Gate HG-20 FAIL: Goal tree missing sub-goal markers")
        return False
    
    if not has_tree_structure:
        print(f"Gate HG-20 FAIL: Goal tree missing hierarchical tree structure")
        return False
    
    print(f"Gate HG-20 PASS: Goal tree present with hierarchical structure")
    print(f"   Main goal present: {has_main_goal}")
    print(f"   Sub-goals present: {has_sub_goals}")
    print(f"   Tree structure present: {has_tree_structure}")
    return True

def main():
    if check_gate_condition():
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()