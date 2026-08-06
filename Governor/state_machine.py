"""
State Machine - Phase, bypass, counter state with inline locking
Layer 3: Self-contained. No imports from other Governor files.
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

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Governor-Log-{today}.jsonl")
        
        entry = {
            "File": "state_machine.py",
            "hook": component,
            "Time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
    except Exception as e:
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


# State file paths
STATE_DIR = os.path.join(GOVERNOR_ROOT, "state")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
CHECKSUM_FILE = os.path.join(STATE_DIR, "state.json.checksum")

# Valid phases
VALID_PHASES = ["INIT", "EXECUTE", "RESEARCH", "PLAN", "VALIDATE", "COMMIT"]

# Development mode
DEV_MODE = os.getenv("GOVERNOR_DEV_MODE", "0") == "1"


@contextmanager
def _file_lock(lock_path: str):
    """Simple file locking context manager."""
    lock_file = None
    try:
        # Create lock file
        lock_file = open(lock_path, 'w')
        # Try to acquire exclusive lock (platform-specific)
        if os.name == 'nt':  # Windows
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:  # Unix
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if lock_file:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
            lock_file.close()
            try:
                os.remove(lock_path)
            except:
                pass


def _compute_checksum(data: str) -> str:
    """Compute SHA-256 checksum of data."""
    return hashlib.sha256(data.encode()).hexdigest()


class StateMachine:
    """Runtime state machine for Governor."""
    
    def __init__(self, state_dir: str = STATE_DIR):
        """Initialize state machine."""
        self.state_dir = state_dir
        self.state_path = os.path.join(state_dir, "state.json")
        self.checksum_path = os.path.join(state_dir, "state.json.checksum")
        self.lock_path = os.path.join(state_dir, ".state.lock")
        
        self._state: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
        os.makedirs(state_dir, exist_ok=True)
        self._load_state()
    
    def _load_state(self):
        """Load state from disk with checksum verification."""
        if not os.path.exists(self.state_path):
            self._initialize_state()
            return
        
        try:
            with open(self.state_path, 'r') as f:
                data = f.read()
            
            # Verify checksum
            if os.path.exists(self.checksum_path):
                with open(self.checksum_path, 'r') as f:
                    stored_checksum = f.read().strip()
                computed_checksum = _compute_checksum(data)
                if stored_checksum != computed_checksum:
                    print(f"Warning: State checksum mismatch, reinitializing", file=sys.stderr)
                    self._initialize_state()
                    return
            
            self._state = json.loads(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load state, reinitializing: {e}", file=sys.stderr)
            self._initialize_state()
    
    def _initialize_state(self):
        """Initialize default state."""
        self._state = {
            "phase": "EXECUTE",
            "counters": {"exec": 0, "validate": 0},
            "flags": {"research_required": False},
            "bypasses": {"runtime": [], "team": [], "once": [], "session": []},
            "permissions": {"runtime": [], "session": []},
            "violations": [],
            "pending_menus": [],
            "metadata": {
                "version": "1.5.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        self._save_state()
    
    def _save_state(self):
        """Save state to disk with checksum."""
        self._state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        
        data = json.dumps(self._state, indent=2)
        checksum = _compute_checksum(data)
        
        # Write checksum first
        with open(self.checksum_path, 'w') as f:
            f.write(checksum)
            f.flush()
            os.fsync(f.fileno())
        
        # Write state with atomic operation
        temp_path = self.state_path + ".tmp"
        with open(temp_path, 'w') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        
        os.replace(temp_path, self.state_path)
    
    def get_phase(self) -> str:
        """Get current phase."""
        with self._lock:
            return self._state.get("phase", "EXECUTE")
    
    def set_phase(self, phase: str):
        """Set current phase."""
        if phase not in VALID_PHASES:
            raise ValueError(f"Invalid phase: {phase}")
        
        log_execution("StateMachine", {
            "action": "set_phase",
            "old_phase": self.get_phase(),
            "new_phase": phase
        })
        
        with self._lock:
            self._state["phase"] = phase
            self._save_state()
    
    def get_counter(self, counter_name: str) -> int:
        """Get counter value."""
        with self._lock:
            return self._state["counters"].get(counter_name, 0)
    
    def increment_counter(self, counter_name: str):
        """Increment counter."""
        with self._lock:
            old_value = self._state["counters"].get(counter_name, 0)
            self._state["counters"][counter_name] = old_value + 1
            self._save_state()
    
    def set_counter(self, counter_name: str, value: int):
        """Set counter value."""
        with self._lock:
            self._state["counters"][counter_name] = value
            self._save_state()
    
    def get_flag(self, flag_name: str) -> bool:
        """Get flag value."""
        with self._lock:
            return self._state["flags"].get(flag_name, False)
    
    def set_flag(self, flag_name: str, value: bool):
        """Set flag value."""
        with self._lock:
            self._state["flags"][flag_name] = value
            self._save_state()
    
    def add_bypass(self, rule_id: str, tool_name: str, scope: str = "session",
                   reason: str = "", source: str = ""):
        """Add bypass entry."""
        unique_id = str(uuid.uuid4())
        bypass_key = f"{rule_id}:{tool_name}:{unique_id}"
        
        log_execution("StateMachine", {
            "action": "add_bypass",
            "rule_id": rule_id,
            "tool_name": tool_name,
            "scope": scope
        })
        
        with self._lock:
            bypass_entry = {
                "key": bypass_key,
                "rule_id": rule_id,
                "tool_name": tool_name,
                "scope": scope,
                "reason": reason,
                "source": source,
                "created_at": datetime.utcnow().isoformat()
            }
            self._state["bypasses"][scope].append(bypass_entry)
            self._save_state()
    
    def is_bypassed(self, rule_id: str, tool_name: str) -> bool:
        """Check if tool is bypassed."""
        with self._lock:
            for scope in ["runtime", "team", "once", "session"]:
                for bypass in self._state["bypasses"][scope]:
                    if bypass["rule_id"] == rule_id or bypass["rule_id"] == "*":
                        if bypass["tool_name"] == tool_name or bypass["tool_name"] == "*":
                            return True
            return False
    
    def get_violations(self) -> List[Dict[str, Any]]:
        """Get violations list."""
        with self._lock:
            return self._state.get("violations", [])
    
    def add_violation(self, violation: Dict[str, Any]):
        """Add violation entry."""
        with self._lock:
            self._state["violations"].append(violation)
            self._save_state()
    
    def clear_permissions(self, scope: str = "session"):
        """Clear permissions for scope."""
        with self._lock:
            self._state["permissions"][scope] = []
            self._save_state()
    
    def set_mode(self, mode: str):
        """Set execution mode."""
        with self._lock:
            self._state["mode"] = mode
            self._save_state()
    
    @property
    def state(self) -> Dict[str, Any]:
        """Get state property for compatibility."""
        return self._state
    
    @state.setter
    def state(self, value: Dict[str, Any]):
        """Set state property for compatibility."""
        self._state = value
