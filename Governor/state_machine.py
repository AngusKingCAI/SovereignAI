"""
State Machine for Governor.py v1.5

This module implements the runtime state machine that persists Governor's
execution state across hook invocations. It implements the state management
specified in v1.5 spec §3.3 with crash-safety via fsync and checksums.

State Structure (v1.3 consolidated state.json):
{
  "phase": "INIT",
  "counters": {"exec": 0, "validate": 0},
  "flags": {"research_required": false},
  "bypasses": {"runtime": [], "team": []},
  "violations": [],
  "pending_menus": []
}

Phases:
- INIT: Session initialization
- RESEARCH: Information gathering
- PLAN: Planning and design
- EXECUTE: Implementation
- VALIDATE: Testing and validation
- COMMIT: Final review and integration

Crash-Safety:
- Atomic writes with temp file + os.replace
- fsync for data durability
- Checksum sidecar for integrity verification
- File locking for concurrent access protection
"""

import os
import sys
import json
import hashlib
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager

# Import locking module (package-relative for module execution)
try:
    from .locking import exclusive_lock
except ImportError:
    # Fallback for direct execution during development
    from locking import exclusive_lock

# State file paths
STATE_DIR = "Governor/state"
STATE_FILE = os.path.join(STATE_DIR, "state.json")
STATE_LOCK_FILE = os.path.join(STATE_DIR, ".state.lock")
CHECKSUM_FILE = os.path.join(STATE_DIR, "state.json.checksum")

# Valid phases per v1.5 spec
VALID_PHASES = ["INIT", "RESEARCH", "PLAN", "EXECUTE", "VALIDATE", "COMMIT"]

# Phase allowlist (tools allowed in each phase)
PHASE_ALLOWLIST = {
    "INIT": ["read", "web_search"],
    "RESEARCH": ["read", "web_search"],
    "PLAN": ["read", "web_search"],
    "EXECUTE": ["read", "file_write", "file_edit", "exec"],
    "VALIDATE": ["read", "exec"],
    "COMMIT": ["read", "file_write", "file_edit", "exec"]
}


class StateMachine:
    """
    Runtime state machine for Governor.
    
    Manages persistent state across hook invocations with crash-safety
    guarantees via atomic writes, fsync, and checksums.
    """
    
    def __init__(self, state_dir: str = STATE_DIR):
        """
        Initialize state machine.
        
        Args:
            state_dir: Directory containing state files
        """
        self.state_dir = state_dir
        self.state_path = os.path.join(state_dir, "state.json")
        self.lock_path = os.path.join(state_dir, ".state.lock")
        self.checksum_path = os.path.join(state_dir, "state.json.checksum")
        
        # In-memory state cache
        self.state: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        # Initialize state directory
        os.makedirs(state_dir, exist_ok=True)
        
        # Load or initialize state
        self._load_state()
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default initial state."""
        return {
            "phase": "INIT",
            "counters": {
                "exec": 0,
                "validate": 0
            },
            "flags": {
                "research_required": False
            },
            "bypasses": {
                "runtime": [],
                "team": [],
                "once": [],
                "session": []
            },
            "violations": [],
            "pending_menus": [],
            "metadata": {
                "version": "1.5.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
    
    def _load_state(self) -> None:
        """Load state from disk with crash-safety verification."""
        with exclusive_lock(self.lock_path, timeout=5.0):
            if os.path.exists(self.state_path):
                try:
                    # Verify checksum before loading
                    if self._verify_checksum():
                        with open(self.state_path, 'r') as f:
                            self.state = json.load(f)
                    else:
                        # Checksum mismatch - use default state
                        print("Warning: State checksum mismatch, using default state")
                        self.state = self._get_default_state()
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Failed to load state: {e}, using default state")
                    self.state = self._get_default_state()
                
                # Migration: ensure all 4 bypass scopes exist (for legacy state files)
                for scope in ["runtime", "team", "once", "session"]:
                    if scope not in self.state.get("bypasses", {}):
                        self.state.setdefault("bypasses", {})[scope] = []
            else:
                # No existing state, initialize with defaults
                self.state = self._get_default_state()
                self._save_state(_already_locked=True)
    
    def _save_state(self, _already_locked: bool = False) -> None:
        """
        Save state to disk with atomic write, fsync, and checksum.
        
        Implements crash-safety per v1.5 spec §3.3:
        1. Update metadata first
        2. Write to temp file
        3. fsync to ensure data reaches disk
        4. Atomic replace
        5. Update checksum from file contents
        
        Args:
            _already_locked: If True, skip lock acquisition (for re-entrant calls)
        """
        if _already_locked:
            self._save_state_unlocked()
        else:
            with exclusive_lock(self.lock_path, timeout=5.0):
                self._save_state_unlocked()
    
    def _save_state_unlocked(self) -> None:
        """
        Internal save method that does NOT acquire lock.
        Only call this when already holding the lock.
        """
        # Update metadata first
        self.state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        temp_path = f"{self.state_path}.tmp"
        
        # Write to temp file
        with open(temp_path, 'w', newline='\n') as f:
            json.dump(self.state, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        
        # Atomic replace
        os.replace(temp_path, self.state_path)
        
        # Update checksum from file contents (not in-memory state)
        self._update_checksum_from_file()
    
    def _compute_checksum(self) -> str:
        """Compute SHA-256 checksum of current state."""
        state_str = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(state_str.encode()).hexdigest()
    
    def _update_checksum(self) -> None:
        """Update checksum sidecar file (deprecated - use _update_checksum_from_file)."""
        checksum = self._compute_checksum()
        with open(self.checksum_path, 'w') as f:
            f.write(checksum)
            f.flush()
            os.fsync(f.fileno())
    
    def _update_checksum_from_file(self) -> None:
        """Update checksum sidecar file by hashing the file contents on disk."""
        if not os.path.exists(self.state_path):
            return
        
        with open(self.state_path, 'r') as f:
            file_contents = f.read()
        
        checksum = hashlib.sha256(file_contents.encode()).hexdigest()
        with open(self.checksum_path, 'w') as f:
            f.write(checksum)
            f.flush()
            os.fsync(f.fileno())
    
    def _verify_checksum(self) -> bool:
        """Verify that state file matches checksum by comparing file contents."""
        if not os.path.exists(self.checksum_path):
            return False
        if not os.path.exists(self.state_path):
            return False
        
        with open(self.checksum_path, 'r') as f:
            stored_checksum = f.read().strip()
        
        # Compute checksum from file contents, not in-memory state
        with open(self.state_path, 'r') as f:
            file_contents = f.read()
        actual_checksum = hashlib.sha256(file_contents.encode()).hexdigest()
        
        return stored_checksum == actual_checksum
    
    def get_phase(self) -> str:
        """Get current phase."""
        with self._lock:
            return self.state.get("phase", "INIT")
    
    def set_phase(self, phase: str) -> None:
        """
        Set current phase with validation.
        
        Args:
            phase: New phase name
            
        Raises:
            ValueError: If phase is not valid
        """
        if phase not in VALID_PHASES:
            raise ValueError(f"Invalid phase: {phase}. Valid phases: {VALID_PHASES}")
        
        with self._lock:
            self.state["phase"] = phase
            self._save_state()
    
    def is_tool_allowed(self, tool_name: str) -> bool:
        """
        Check if a tool is allowed in the current phase.
        
        Args:
            tool_name: Canonical tool name
            
        Returns:
            True if tool is allowed, False otherwise
        """
        current_phase = self.get_phase()
        allowed_tools = PHASE_ALLOWLIST.get(current_phase, [])
        return tool_name in allowed_tools
    
    def increment_counter(self, counter_name: str) -> None:
        """
        Increment a counter (only for PostToolUse).
        
        Args:
            counter_name: Name of counter to increment
        """
        with self._lock:
            if counter_name not in self.state["counters"]:
                self.state["counters"][counter_name] = 0
            self.state["counters"][counter_name] += 1
            self._save_state()
    
    def get_counter(self, counter_name: str) -> int:
        """Get counter value."""
        with self._lock:
            return self.state["counters"].get(counter_name, 0)
    
    def set_flag(self, flag_name: str, value: bool) -> None:
        """Set a flag value."""
        with self._lock:
            self.state["flags"][flag_name] = value
            self._save_state()
    
    def get_flag(self, flag_name: str) -> bool:
        """Get flag value."""
        with self._lock:
            return self.state["flags"].get(flag_name, False)
    
    def add_bypass(self, bypass_key: str, scope: str = "runtime", 
                   expires: Optional[str] = None, reason: str = "", 
                   source: str = "runtime") -> None:
        """
        Add a bypass entry to the registry (spec §3.3 compliant).
        
        Args:
            bypass_key: Unique bypass key (format: rule_id:tool)
            scope: Either "runtime", "team", "once", or "session"
            expires: Optional expiration timestamp (ISO format)
            reason: Human-readable reason for bypass
            source: Source of bypass (e.g., "user", "team", "runtime")
        """
        with self._lock:
            if scope not in ["runtime", "team", "once", "session"]:
                raise ValueError(f"Invalid bypass scope: {scope}")
            
            # Check if bypass already exists
            for entry in self.state["bypasses"][scope]:
                if entry.get("key") == bypass_key:
                    return  # Already exists
            
            # Create spec-compliant bypass entry
            bypass_entry = {
                "key": bypass_key,
                "rule_id": bypass_key.split(":")[0] if ":" in bypass_key else "",
                "tool": bypass_key.split(":")[1] if ":" in bypass_key else "",
                "scope": scope,
                "expires": expires,
                "reason": reason,
                "source": source,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.state["bypasses"][scope].append(bypass_entry)
            self._save_state()
    
    def is_bypassed(self, rule_id: str, tool_name: str) -> bool:
        """
        Check if a rule+tool combination is bypassed (spec §3.3 compliant).
        
        Args:
            rule_id: Rule identifier
            tool_name: Tool name
            
        Returns:
            True if bypassed, False otherwise
        """
        bypass_key = f"{rule_id}:{tool_name}"
        
        with self._lock:
            # Check all scopes for matching bypass
            for scope in ["runtime", "team", "once", "session"]:
                for entry in self.state["bypasses"][scope]:
                    if entry.get("key") == bypass_key:
                        # Check expiration
                        if entry.get("expires"):
                            # TODO: Check if bypass has expired
                            pass
                        return True
            
            return False
    
    def add_violation(self, violation: Dict[str, Any]) -> None:
        """Add a violation to the log."""
        with self._lock:
            violation["timestamp"] = datetime.utcnow().isoformat()
            self.state["violations"].append(violation)
            self._save_state()
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get all violations."""
        with self._lock:
            return self.state["violations"].copy()
    
    def clear_violations(self) -> None:
        """Clear all violations."""
        with self._lock:
            self.state["violations"] = []
            self._save_state()
    
    def add_pending_menu(self, menu: Dict[str, Any]) -> None:
        """Add a pending menu for user interaction."""
        with self._lock:
            self.state["pending_menus"].append(menu)
            self._save_state()
    
    def get_pending_menus(self) -> List[Dict[str, Any]]:
        """Get all pending menus."""
        with self._lock:
            return self.state["pending_menus"].copy()
    
    def clear_pending_menus(self) -> None:
        """Clear all pending menus."""
        with self._lock:
            self.state["pending_menus"] = []
            self._save_state()
    
    def reset(self) -> None:
        """Reset state to defaults (used for SessionStart)."""
        with self._lock:
            self.state = self._get_default_state()
            self._save_state()
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get a snapshot of current state (for debugging)."""
        with self._lock:
            return self.state.copy()
