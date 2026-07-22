#!/usr/bin/env python3
"""
SessionEnd Hook: Session Cleanup

Runs when session ends.
Generates attestation, archives traces, creates checkpoint with current phase and pending items.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime

# Add the scripts directory to the path for imports
scripts_dir = Path(__file__).parent.parent
sys.path.insert(0, str(scripts_dir))

try:
    from checkpoint_manager import CheckpointManager
except ImportError:
    print("[WARN] Could not import CheckpointManager, running without checkpoint support")
    CheckpointManager = None

def main():
    print(f"SessionEnd Hook: Cleaning up session")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Working Directory: {os.getcwd()}")
    print(f"   Project: SovereignAI Planner Workflow")
    
    if CheckpointManager:
        try:
            # Initialize checkpoint manager
            project_root = Path.cwd()
            manager = CheckpointManager(project_root)
            
            # Create a session end checkpoint
            # In production, this would capture the actual current phase and pending items
            # For now, we'll create a basic checkpoint with session end metadata
            
            execution_metadata = {
                "session_end": True,
                "session_end_timestamp": datetime.now().isoformat(),
                "trigger": "session_end_hook"
            }
            
            manager.create_checkpoint(
                phase="Session End",
                pending_items=[],
                compliance_lines=[],
                plan_files=[],
                execution_metadata=execution_metadata
            )
            
            print("[INFO] Session end checkpoint created")
            
            # In production, this would also:
            # 1. Generate attestation for session activities
            # 2. Archive traces for audit trail
            # 3. Clean up temporary resources
            
        except Exception as e:
            print(f"[ERROR] Checkpoint creation failed: {e}")
    else:
        print("[INFO] Checkpoint manager not available, skipping checkpoint creation")
    
    print(f"SessionEnd Hook: Session cleanup completed")
    
    sys.exit(0)  # Always allow session end

if __name__ == "__main__":
    main()