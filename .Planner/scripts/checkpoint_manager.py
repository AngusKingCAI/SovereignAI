#!/usr/bin/env python3
"""
Checkpoint Manager: Durable Execution & Checkpointing

Manages workflow state checkpointing for session resumption and recovery.
Implements PR21: Durable Execution & Checkpointing
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class CheckpointManager:
    """Manages workflow state checkpointing"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.checkpoint_dir = project_root / ".Planner" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def create_checkpoint(self, phase: str, pending_items: list = None, 
                         compliance_lines: list = None, plan_files: list = None,
                         execution_metadata: Dict[str, Any] = None) -> Path:
        """
        Create a checkpoint with current workflow state
        
        Args:
            phase: Current phase (e.g., "Phase 2.5")
            pending_items: List of pending items/tasks
            compliance_lines: List of compliance lines posted
            plan_files: List of plan file references
            execution_metadata: Additional execution metadata
        
        Returns:
            Path to created checkpoint file
        """
        timestamp = datetime.now().isoformat()
        checkpoint_filename = f"checkpoint-{timestamp.replace(':', '-')}.json"
        checkpoint_path = self.checkpoint_dir / checkpoint_filename
        
        checkpoint_data = {
            "timestamp": timestamp,
            "phase": phase,
            "pending_items": pending_items or [],
            "compliance_lines": compliance_lines or [],
            "plan_files": plan_files or [],
            "execution_metadata": execution_metadata or {},
            "project_root": str(self.project_root)
        }
        
        try:
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            # Create symlink to latest checkpoint
            latest_link = self.checkpoint_dir / "latest.json"
            if latest_link.exists():
                latest_link.unlink()
            
            # On Windows, we need to use a different approach for symlinks
            # For now, we'll just copy the file
            import shutil
            shutil.copy2(checkpoint_path, latest_link)
            
            print(f"[INFO] Checkpoint created: {checkpoint_path}")
            print(f"[INFO] Phase: {phase}, Pending items: {len(pending_items or [])}")
            
            return checkpoint_path
        except Exception as e:
            print(f"[ERROR] Failed to create checkpoint: {e}")
            raise
    
    def load_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load the latest checkpoint
        
        Returns:
            Checkpoint data dict or None if no checkpoint exists
        """
        latest_checkpoint = self.checkpoint_dir / "latest.json"
        
        if not latest_checkpoint.exists():
            print("[INFO] No checkpoint found, starting fresh session")
            return None
        
        try:
            with open(latest_checkpoint, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            print(f"[INFO] Checkpoint loaded: {latest_checkpoint}")
            print(f"[INFO] Resuming from phase: {checkpoint_data.get('phase', 'Unknown')}")
            print(f"[INFO] Pending items: {len(checkpoint_data.get('pending_items', []))}")
            
            return checkpoint_data
        except Exception as e:
            print(f"[ERROR] Failed to load checkpoint: {e}")
            return None
    
    def validate_checkpoint(self, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Validate checkpoint integrity and consistency with current file state
        
        Args:
            checkpoint_data: Checkpoint data to validate
        
        Returns:
            True if checkpoint is valid, False otherwise
        """
        # Basic validation
        required_fields = ["timestamp", "phase", "project_root"]
        for field in required_fields:
            if field not in checkpoint_data:
                print(f"[ERROR] Checkpoint validation failed: Missing field '{field}'")
                return False
        
        # Validate project root consistency
        if str(self.project_root) != checkpoint_data["project_root"]:
            print(f"[WARN] Checkpoint project root mismatch: {checkpoint_data['project_root']} vs {self.project_root}")
            print(f"[WARN] This may indicate the checkpoint was created in a different location")
        
        # Validate plan files exist
        plan_files = checkpoint_data.get("plan_files", [])
        for plan_file in plan_files:
            plan_path = self.project_root / plan_file
            if not plan_path.exists():
                print(f"[WARN] Plan file from checkpoint not found: {plan_file}")
        
        print("[INFO] Checkpoint validation completed")
        return True
    
    def list_checkpoints(self) -> list:
        """
        List all available checkpoints
        
        Returns:
            List of checkpoint filenames sorted by timestamp (newest first)
        """
        checkpoints = list(self.checkpoint_dir.glob("checkpoint-*.json"))
        # Remove the latest.json symlink from the list
        checkpoints = [cp for cp in checkpoints if cp.name != "latest.json"]
        
        # Sort by timestamp (newest first)
        checkpoints.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return checkpoints
    
    def rollback_to_checkpoint(self, checkpoint_path: Path) -> bool:
        """
        Rollback to a specific checkpoint
        
        Args:
            checkpoint_path: Path to checkpoint file to rollback to
        
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # Load the checkpoint
            with open(checkpoint_path, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)
            
            # Validate checkpoint
            if not self.validate_checkpoint(checkpoint_data):
                print("[ERROR] Checkpoint validation failed, aborting rollback")
                return False
            
            # Set as latest checkpoint
            latest_link = self.checkpoint_dir / "latest.json"
            if latest_link.exists():
                latest_link.unlink()
            
            import shutil
            shutil.copy2(checkpoint_path, latest_link)
            
            print(f"[INFO] Rolled back to checkpoint: {checkpoint_path}")
            print(f"[INFO] Phase: {checkpoint_data.get('phase', 'Unknown')}")
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to rollback to checkpoint: {e}")
            return False

def main():
    """CLI interface for checkpoint management"""
    if len(sys.argv) < 2:
        print("Usage: python checkpoint_manager.py <command> [args]")
        print("Commands:")
        print("  create <phase> [pending_items] [compliance_lines] [plan_files]")
        print("  load")
        print("  list")
        print("  rollback <checkpoint_file>")
        sys.exit(1)
    
    command = sys.argv[1]
    project_root = Path.cwd()
    manager = CheckpointManager(project_root)
    
    if command == "create":
        if len(sys.argv) < 3:
            print("Error: create command requires phase argument")
            sys.exit(1)
        
        phase = sys.argv[2]
        pending_items = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        compliance_lines = sys.argv[4].split(",") if len(sys.argv) > 4 else []
        plan_files = sys.argv[5].split(",") if len(sys.argv) > 5 else []
        
        manager.create_checkpoint(phase, pending_items, compliance_lines, plan_files)
    
    elif command == "load":
        checkpoint_data = manager.load_latest_checkpoint()
        if checkpoint_data:
            print(json.dumps(checkpoint_data, indent=2))
    
    elif command == "list":
        checkpoints = manager.list_checkpoints()
        print(f"Found {len(checkpoints)} checkpoints:")
        for cp in checkpoints:
            print(f"  - {cp.name}")
    
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Error: rollback command requires checkpoint_file argument")
            sys.exit(1)
        
        checkpoint_file = sys.argv[2]
        checkpoint_path = manager.checkpoint_dir / checkpoint_file
        
        if not checkpoint_path.exists():
            print(f"Error: Checkpoint not found: {checkpoint_file}")
            sys.exit(1)
        
        manager.rollback_to_checkpoint(checkpoint_path)
    
    else:
        print(f"Error: Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()