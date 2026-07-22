#!/usr/bin/env python3
"""
Create Checkpoint Script: Phase Completion Checkpointing

Creates a checkpoint after phase completion for durable execution.
Integrates with the hard gate system to automatically checkpoint after phase gates pass.
Implements PR21: Durable Execution & Checkpointing
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path for imports
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

try:
    from checkpoint_manager import CheckpointManager
except ImportError:
    print("[ERROR] Could not import CheckpointManager")
    sys.exit(1)

def parse_compliance_lines_from_plan(plan_file: Path) -> list:
    """
    Parse compliance lines from a plan file
    
    Args:
        plan_file: Path to plan file
    
    Returns:
        List of compliance lines found in the plan
    """
    if not plan_file.exists():
        return []
    
    try:
        content = plan_file.read_text(encoding='utf-8')
        compliance_lines = []
        
        # Find all compliance lines (e.g., "✅ Gate PLAN-1 PASS: ...")
        import re
        compliance_pattern = r"Gate (?:PLAN-|HG-|SG-)[\d\.]+ PASS.*"
        matches = re.findall(compliance_pattern, content)
        
        for match in matches:
            compliance_lines.append(match)
        
        return compliance_lines
    except Exception as e:
        print(f"[WARN] Failed to parse compliance lines from {plan_file}: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_checkpoint.py <phase> [plan_file]")
        print("Creates a checkpoint after phase completion")
        sys.exit(1)
    
    phase = sys.argv[1]
    plan_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize checkpoint manager
    project_root = Path.cwd()
    manager = CheckpointManager(project_root)
    
    # Gather checkpoint data
    pending_items = []  # In production, this would track actual pending items
    compliance_lines = []
    plan_files = []
    
    # If plan file provided, parse compliance lines
    if plan_file:
        plan_path = Path(plan_file)
        if plan_path.exists():
            plan_files.append(str(plan_path.relative_to(project_root)))
            compliance_lines = parse_compliance_lines_from_plan(plan_path)
    
    # Create execution metadata
    execution_metadata = {
        "phase_completion": True,
        "phase": phase,
        "completion_timestamp": datetime.now().isoformat(),
        "trigger": "phase_completion"
    }
    
    # Create checkpoint
    try:
        checkpoint_path = manager.create_checkpoint(
            phase=phase,
            pending_items=pending_items,
            compliance_lines=compliance_lines,
            plan_files=plan_files,
            execution_metadata=execution_metadata
        )
        
        print(f"[INFO] Checkpoint created successfully at {phase}")
        print(f"[INFO] Checkpoint file: {checkpoint_path}")
        print(f"[INFO] Compliance lines captured: {len(compliance_lines)}")
        
        # Post compliance for checkpoint creation
        print(f"[COMPLIANCE] Gate PR21 PASS: Checkpoint created at {phase}, state persisted for recovery")
        
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Checkpoint creation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()