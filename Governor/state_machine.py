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
  "bypasses": {"runtime": [], "team": [], "once": [], "session": []},
  "permissions": {"runtime": [], "session": []},
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
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager

# Import locking module (package-relative for module execution)
try:
    from .locking import exclusive_lock
except ImportError:
    # Fallback for direct execution during development
    from locking import exclusive_lock

# Import debug logging
try:
    from .debug_logging import debug_log, is_debug_enabled
except ImportError:
    from debug_logging import debug_log, is_debug_enabled

# Import security module for team bypasses validation
try:
    from .security import validate_team_bypasses
except ImportError:
    from security import validate_team_bypasses

# Get Governor package root for relative paths
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))

# State file paths (relative to Governor package root)
STATE_DIR = os.path.join(GOVERNOR_ROOT, "state")
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
        
        # Initialize state directory with secure permissions
        old_umask = os.umask(0o077)  # Restrict to owner-only
        try:
            os.makedirs(state_dir, exist_ok=True)
        finally:
            os.umask(old_umask)  # Restore original umask
        
        # Load or initialize state
        self._load_state()
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default initial state."""
        return {
            "phase": "INIT",
            "mode": "app",
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
            "permissions": {
                "runtime": [],
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
                
                # Migration: ensure permissions section exists (for legacy state files)
                if "permissions" not in self.state:
                    self.state["permissions"] = {
                        "runtime": [],
                        "session": []
                    }
            else:
                # No existing state, initialize with defaults
                self.state = self._get_default_state()
                self._save_state(_already_locked=True)
            
            # Load team bypasses from team_bypasses.json (per spec §3.3)
            self._load_team_bypasses()
    
    def _load_team_bypasses(self) -> None:
        """
        Load team bypasses from team_bypasses.json file.
        
        Team bypasses are committed to VCS and shared across the team.
        They are loaded on every hook invocation to ensure the latest
        overrides are always active.
        """
        team_bypasses_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "team_bypasses.json"
        )
        
        if os.path.exists(team_bypasses_path):
            try:
                with open(team_bypasses_path, 'r') as f:
                    team_data = json.load(f)
                
                # Validate team bypasses file structure with security module
                is_valid, error_msg = validate_team_bypasses(team_data)
                if not is_valid:
                    debug_log("state_machine", f"Invalid team_bypasses.json: {error_msg}")
                    self.state["bypasses"]["team"] = []
                    return
                
                # Replace team bypasses in state with file contents
                self.state["bypasses"]["team"] = team_data["bypasses"]
                debug_log("state_machine", f"Loaded {len(team_data['bypasses'])} team bypasses")
            except (json.JSONDecodeError, IOError) as e:
                debug_log("state_machine", f"Failed to load team bypasses: {e}")
                self.state["bypasses"]["team"] = []
        else:
            # No team bypasses file, initialize empty list
            self.state["bypasses"]["team"] = []
    
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
        
        # Fsync directory to ensure directory entry is durable (Unix only)
        # Windows doesn't support directory fsync, so we skip it there
        if sys.platform != "win32":
            try:
                dir_fd = os.open(os.path.dirname(self.state_path), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
            except (OSError, AttributeError):
                # Filesystem doesn't support directory fsync
                pass
        
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
        
        debug_log("state_machine", "Setting phase", old_phase=self.get_phase(), new_phase=phase)
        
        with self._lock:
            self.state["phase"] = phase
            self._save_state()
    
    def set_mode(self, mode: str) -> None:
        """
        Set current execution mode (app vs harness).
        
        Args:
            mode: Mode name ("app" or "harness")
            
        Raises:
            ValueError: If mode is not valid
        """
        if mode not in ["app", "harness"]:
            raise ValueError(f"Invalid mode: {mode}. Valid modes: app, harness")
        
        debug_log("state_machine", "Setting mode", old_mode=self.get_mode(), new_mode=mode)
        
        with self._lock:
            self.state["mode"] = mode
            self._save_state()
    
    def get_mode(self) -> str:
        """
        Get current execution mode.
        
        Returns:
            Current mode name ("app" or "harness")
        """
        with self._lock:
            return self.state.get("mode", "app")
    
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
        debug_log("state_machine", "Incrementing counter", counter=counter_name)
        
        with self._lock:
            if counter_name not in self.state["counters"]:
                self.state["counters"][counter_name] = 0
            self.state["counters"][counter_name] += 1
            self._save_state()
    
    def set_counter(self, counter_name: str, value: int) -> None:
        """
        Set a counter to a specific value (for SessionStart reset).
        
        Args:
            counter_name: Name of counter to set
            value: Value to set
        """
        with self._lock:
            self.state["counters"][counter_name] = value
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
    
    def add_bypass(self, rule_id: str, tool_name: str, scope: str = "runtime",
                   expires: Optional[str] = None, reason: str = "", 
                   source: str = "runtime", user_prompt_text: str = "") -> str:
        """
        Add a bypass entry to the registry (spec §3.3 compliant).
        
        Args:
            rule_id: Rule identifier (e.g., "block_destructive_commands")
            tool_name: Tool name (e.g., "exec")
            scope: Either "runtime", "team", "once", or "session", or "persistent"
            expires: Optional expiration timestamp (ISO format)
            reason: Human-readable reason for bypass
            source: Source of bypass (e.g., "user_prompt", "env_var", "team", "menu")
            user_prompt_text: Truncated user prompt text (max 200 chars) for audit trail
            
        Returns:
            Generated bypass key (UUID4 format)
        """
        with self._lock:
            if scope not in ["runtime", "team", "once", "session", "persistent"]:
                raise ValueError(f"Invalid bypass scope: {scope}")
            
            # Generate UUID4 bypass key per spec §1.4
            unique_id = str(uuid.uuid4())
            bypass_key = f"{rule_id}:{tool_name}:{unique_id}"
            
            # Create spec-compliant bypass entry
            bypass_entry = {
                "key": bypass_key,
                "rule_id": rule_id,
                "tool": tool_name,
                "scope": scope,
                "expires": expires,
                "reason": reason,
                "source": source,
                "created_at": datetime.utcnow().isoformat(),
                "user_prompt_text": user_prompt_text[:200] if user_prompt_text else ""
            }
            
            # Determine which bypass list to use
            # Team bypasses should go to team scope (but are not persisted to state.json)
            # They are persisted to team_bypasses.json separately
            if scope == "team":
                # Team bypasses are managed via team_bypasses.json file
                # We add them to runtime for current session, but they should be
                # committed to team_bypasses.json separately
                bypass_entry["scope"] = "runtime"  # Override for current session
                self.state["bypasses"]["runtime"].append(bypass_entry)
            elif scope == "persistent":
                # Persistent bypasses are team bypasses
                # Add to team scope (these get loaded from team_bypasses.json)
                bypass_entry["scope"] = "team"
                self.state["bypasses"]["team"].append(bypass_entry)
            else:
                # Runtime, once, session - add to runtime bypasses
                self.state["bypasses"][scope].append(bypass_entry)
            
            self._save_state()
            return bypass_key
    
    def is_bypassed(self, rule_id: str, tool_name: str) -> bool:
        """
        Check if a rule+tool combination is bypassed (spec §3.3 compliant).
        
        Args:
            rule_id: Rule identifier
            tool_name: Tool name
            
        Returns:
            True if bypassed, False otherwise
        """
        bypass_prefix = f"{rule_id}:{tool_name}"
        current_time = datetime.utcnow()
        
        with self._lock:
            # Check all scopes for matching bypass
            for scope in ["runtime", "team", "once", "session"]:
                # Filter expired bypasses first
                valid_bypasses = []
                for entry in self.state["bypasses"][scope]:
                    # Check expiration
                    if entry.get("expires"):
                        try:
                            expires_time = datetime.fromisoformat(entry["expires"])
                            if expires_time < current_time:
                                # Bypass has expired, remove it
                                continue
                        except ValueError:
                            # Invalid expiration format, treat as not expired
                            pass
                    valid_bypasses.append(entry)
                
                # Update bypass list with valid entries only
                self.state["bypasses"][scope] = valid_bypasses
                
                # Check for matching bypass
                for entry in valid_bypasses:
                    # Check if bypass key starts with prefix (supports UUID4 suffixes)
                    if entry.get("key", "").startswith(bypass_prefix):
                        # Check if it's a "once" scope bypass - consume it
                        if entry.get("scope") == "once":
                            # Remove the bypass after one use
                            self.state["bypasses"][scope].remove(entry)
                            self._save_state()
                        
                        return True
        
        return False
    
    def clear_bypasses(self, rule_id: Optional[str] = None, scope: Optional[str] = None) -> int:
        """
        Clear bypasses from the registry.
        
        Args:
            rule_id: Optional rule ID to clear bypasses for (clears all if None)
            scope: Optional scope to clear bypasses from (clears all scopes if None)
            
        Returns:
            Number of bypasses cleared
        """
        with self._lock:
            cleared_count = 0
            scopes_to_clear = [scope] if scope else ["runtime", "team", "once", "session"]
            
            for clear_scope in scopes_to_clear:
                if clear_scope not in self.state["bypasses"]:
                    continue
                
                if rule_id:
                    # Clear bypasses for specific rule
                    original_count = len(self.state["bypasses"][clear_scope])
                    self.state["bypasses"][clear_scope] = [
                        entry for entry in self.state["bypasses"][clear_scope]
                        if entry.get("rule_id") != rule_id
                    ]
                    cleared_count += original_count - len(self.state["bypasses"][clear_scope])
                else:
                    # Clear all bypasses in this scope
                    cleared_count += len(self.state["bypasses"][clear_scope])
                    self.state["bypasses"][clear_scope] = []
            
            if cleared_count > 0:
                self._save_state()
            
            return cleared_count
    
    def get_bypass_stats(self) -> Dict[str, Any]:
        """
        Get bypass statistics for audit trail.
        
        Returns:
            Dictionary with bypass statistics by scope and source
        """
        with self._lock:
            stats = {
                "total": 0,
                "by_scope": {},
                "by_source": {},
                "by_rule": {}
            }
            
            for scope in ["runtime", "team", "once", "session"]:
                count = len(self.state["bypasses"][scope])
                stats["by_scope"][scope] = count
                stats["total"] += count
                
                for entry in self.state["bypasses"][scope]:
                    source = entry.get("source", "unknown")
                    rule_id = entry.get("rule_id", "unknown")
                    
                    stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                    stats["by_rule"][rule_id] = stats["by_rule"].get(rule_id, 0) + 1
            
            return stats
    
    def add_permission(self, permission_type: str, resource: str, operation: str,
                      decision: str, scope: str = "session", reason: str = "") -> str:
        """
        Add a permission decision to the registry.
        
        Args:
            permission_type: Type of permission (read, write, execute, network)
            resource: Resource being accessed
            operation: Operation being performed
            decision: Permission decision (approve/deny)
            scope: Permission scope (runtime/session)
            reason: Human-readable reason
            
        Returns:
            Permission entry key (UUID4 format)
        """
        with self._lock:
            if scope not in ["runtime", "session"]:
                raise ValueError(f"Invalid permission scope: {scope}")
            
            # Generate UUID4 permission key
            unique_id = str(uuid.uuid4())
            permission_key = f"permission:{permission_type}:{resource}:{unique_id}"
            
            # Create permission entry
            permission_entry = {
                "key": permission_key,
                "permission_type": permission_type,
                "resource": resource,
                "operation": operation,
                "decision": decision,
                "scope": scope,
                "reason": reason,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.state["permissions"][scope].append(permission_entry)
            self._save_state()
            return permission_key
    
    def get_permission_decision(self, permission_type: str, resource: str, 
                             operation: str) -> Optional[str]:
        """
        Get saved permission decision for a specific request.
        
        Args:
            permission_type: Type of permission
            resource: Resource being accessed
            operation: Operation being performed
            
        Returns:
            Permission decision (approve/deny) or None if not found
        """
        with self._lock:
            # Check both runtime and session permissions
            for scope in ["runtime", "session"]:
                for entry in self.state["permissions"][scope]:
                    if (entry.get("permission_type") == permission_type and
                        entry.get("resource") == resource and
                        entry.get("operation") == operation):
                        return entry.get("decision")
            
            return None
    
    def clear_permissions(self, scope: Optional[str] = None) -> int:
        """
        Clear permissions from the registry.
        
        Args:
            scope: Optional scope to clear (runtime/session), clears all if None
            
        Returns:
            Number of permissions cleared
        """
        with self._lock:
            cleared_count = 0
            scopes_to_clear = [scope] if scope else ["runtime", "session"]
            
            for clear_scope in scopes_to_clear:
                cleared_count += len(self.state["permissions"][clear_scope])
                self.state["permissions"][clear_scope] = []
            
            if cleared_count > 0:
                self._save_state()
            
            return cleared_count
    
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
