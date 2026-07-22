#!/usr/bin/env python3
"""
SessionStart Hook: State Awareness

Runs when session starts.
Queries workflow state and prints "Resuming from Phase X.Y" for state awareness.
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
    print(f"SessionStart Hook: Checking workflow state")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Working Directory: {os.getcwd()}")
    print(f"   Project: SovereignAI Planner Workflow")
    
    if CheckpointManager:
        try:
            # Initialize checkpoint manager
            project_root = Path.cwd()
            manager = CheckpointManager(project_root)
            
            # Load latest checkpoint
            checkpoint_data = manager.load_latest_checkpoint()
            
            if checkpoint_data:
                # Validate checkpoint
                if manager.validate_checkpoint(checkpoint_data):
                    phase = checkpoint_data.get("phase", "Unknown")
                    pending_items = checkpoint_data.get("pending_items", [])
                    plan_files = checkpoint_data.get("plan_files", [])
                    
                    print(f"[INFO] Resuming from {phase}")
                    print(f"[INFO] Pending items: {len(pending_items)}")
                    print(f"[INFO] Plan files: {len(plan_files)}")
                    
                    # In production, this would restore the full workflow state
                    # For now, we just print the resumption information
                else:
                    print("[WARN] Checkpoint validation failed, starting fresh session")
            else:
                print("[INFO] No checkpoint found, starting fresh session")
        except Exception as e:
            print(f"[ERROR] Checkpoint loading failed: {e}")
            print("[INFO] Starting fresh session")
    else:
        print("[INFO] Checkpoint manager not available, starting fresh session")
    
    sys.exit(0)  # Always allow session start

if __name__ == "__main__":
    main()