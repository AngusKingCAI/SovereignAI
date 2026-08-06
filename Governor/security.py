"""
Security Protection for Governor.py v1.5

This module implements security measures per v1.5 spec §6.4:
- Path traversal protection for auto-discovery
- Symlink validation for trusted directory enforcement
- File permission checks for critical paths
- Resource limit enforcement for actions

This implements the security threat model specified in v1.5 spec §6.4.
"""

import os
import sys
import time
import signal
from pathlib import Path
from typing import Union, List, Optional, Tuple
from datetime import datetime

# Get Governor package root for relative paths
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))

# Trusted directories (committed to VCS, reviewed via PR)
# These are relative to governor_root (Governor/ directory)
TRUSTED_DIRECTORIES = [
    "actions",
    "hook_handlers",
    "templates",
    "validators"
]

# Protected paths (agent cannot write to these)
# These are relative to project root (SovereignAI/ directory)
PROJECT_ROOT = os.path.dirname(GOVERNOR_ROOT)
PROTECTED_PATHS = [
    os.path.join("Governor", "state"),
    os.path.join("Governor", "logs"),
    os.path.join("Governor", "rules"),
    os.path.join("Governor", "team_bypasses.json"),
    os.path.join("Governor", "scope_config.json")
]

# Resource limits for actions (per spec §6.4)
ACTION_TIMEOUT_S = 1.0  # Actions must complete within 1 second
MAX_ACTION_MEMORY_MB = 100  # Maximum memory for action execution


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


def validate_import_path(module_path: str) -> None:
    """
    Validate that an import path is within trusted directories.
    
    This prevents path traversal attacks in auto-discovery.
    
    Args:
        module_path: Module path to validate (e.g., "actions.block_command")
        
    Raises:
        SecurityError: If path contains .. or resolves outside trusted directory
    """
    # Get Governor package root
    governor_root = Path(os.path.dirname(os.path.abspath(__file__))).resolve()
    
    # Check for path traversal (.. in path)
    if ".." in module_path:
        raise SecurityError(
            f"Path traversal detected in module path: {module_path}"
        )
    
    # Convert module path to file path RELATIVE to governor_root
    # actions.block_command -> actions/block_command.py
    file_path = module_path.replace(".", os.sep) + ".py"
    resolved_path = (governor_root / file_path).resolve()
    
    # Check if resolved path is within trusted directories
    is_trusted = False
    for trusted_dir in TRUSTED_DIRECTORIES:
        trusted_path = governor_root / trusted_dir
        try:
            resolved_path.relative_to(trusted_path)
            is_trusted = True
            break
        except ValueError:
            continue
    
    if not is_trusted:
        raise SecurityError(
            f"Module path {module_path} resolves outside trusted directories: {resolved_path}"
        )


def validate_symlink(file_path: Union[str, Path]) -> bool:
    """
    Validate that a symlink target is within trusted directories.
    
    Args:
        file_path: File path to validate
        
    Returns:
        True if symlink is safe to follow, False otherwise
    """
    path_obj = Path(file_path)
    
    # Check if it's a symlink
    if not path_obj.is_symlink():
        return True  # Not a symlink, safe
    
    # Resolve symlink target
    try:
        target = path_obj.resolve()
    except (OSError, RuntimeError):
        return False  # Broken symlink, unsafe
    
    # Check if target is within trusted directories
    governor_root = Path(os.path.dirname(os.path.abspath(__file__))).resolve()
    
    for trusted_dir in TRUSTED_DIRECTORIES:
        trusted_path = governor_root / trusted_dir
        try:
            target.relative_to(trusted_path)
            return True  # Symlink target is within trusted directory
        except ValueError:
            continue
    
    return False  # Symlink target is outside trusted directories


def is_protected_path(file_path: Union[str, Path]) -> bool:
    """
    Check if a path is protected (agent should not write to it).
    
    Args:
        file_path: File path to check
        
    Returns:
        True if path is protected, False otherwise
    """
    path_str = str(file_path)
    
    # Normalize path for comparison
    path_str = os.path.normpath(path_str)
    
    for protected in PROTECTED_PATHS:
        protected_normalized = os.path.normpath(protected)
        if path_str.startswith(protected_normalized) or protected_normalized in path_str:
            return True
    
    return False


def validate_file_permissions(file_path: Union[str, Path], required_mode: int = 0o600) -> bool:
    """
    Validate that a file has the required permissions.
    
    On POSIX, this checks actual file permissions.
    On Windows, this is a no-op (ACLs are used instead).
    
    Args:
        file_path: File path to check
        required_mode: Required file mode (default: 0o600 = owner read/write only)
        
    Returns:
        True if permissions are valid, False otherwise
    """
    if sys.platform == "win32":
        # Windows uses ACLs, skip permission check
        return True
    
    try:
        file_stat = os.stat(file_path)
        current_mode = file_stat.st_mode & 0o777
        
        # Check if owner has required permissions
        # For 0o600, owner needs read (0o400) + write (0o200)
        return (current_mode & required_mode) == required_mode
    except OSError:
        return False


def get_security_context() -> dict:
    """
    Get current security context for logging.
    
    Returns:
        Dictionary with security context information
    """
    return {
        "trusted_directories": TRUSTED_DIRECTORIES,
        "protected_paths": PROTECTED_PATHS,
        "platform": sys.platform,
        "symlink_validation_enabled": True,
        "path_traversal_protection_enabled": True
    }


def validate_team_bypasses(bypasses_data: dict) -> Tuple[bool, str]:
    """
    Validate team bypasses file structure and content.
    
    Args:
        bypasses_data: Dictionary containing team bypasses data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if not isinstance(bypasses_data, dict):
        return False, "Team bypasses data must be a dictionary"
    
    if "bypasses" not in bypasses_data:
        return False, "Missing 'bypasses' field in team bypasses data"
    
    if not isinstance(bypasses_data["bypasses"], list):
        return False, "'bypasses' field must be a list"
    
    # Validate each bypass entry
    for i, entry in enumerate(bypasses_data["bypasses"]):
        if not isinstance(entry, dict):
            return False, f"Bypass entry {i} must be a dictionary"
        
        # Check required fields
        required_fields = ["key", "rule_id", "tool", "scope", "reason", "source"]
        for field in required_fields:
            if field not in entry:
                return False, f"Bypass entry {i} missing required field: {field}"
        
        # Validate scope
        valid_scopes = ["team", "persistent", "session", "runtime", "once"]
        if entry["scope"] not in valid_scopes:
            return False, f"Bypass entry {i} has invalid scope: {entry['scope']}"
        
        # Validate timestamps if present
        if "created_at" in entry:
            try:
                datetime.fromisoformat(entry["created_at"])
            except ValueError:
                return False, f"Bypass entry {i} has invalid created_at timestamp"
        
        if "expires" in entry and entry["expires"]:
            try:
                datetime.fromisoformat(entry["expires"])
            except ValueError:
                return False, f"Bypass entry {i} has invalid expires timestamp"
    
    return True, ""


class ActionTimeoutError(Exception):
    """Raised when an action exceeds its timeout limit."""
    pass


class ResourceLimitEnforcer:
    """
    Enforce resource limits for action execution.
    
    This implements resource limit enforcement per spec §6.4:
    - Actions must complete within ACTION_TIMEOUT_S (default 1 second)
    - Actions should not exceed MAX_ACTION_MEMORY_MB (default 100 MB)
    """
    
    def __init__(self, timeout_seconds: float = ACTION_TIMEOUT_S):
        """
        Initialize resource limit enforcer.
        
        Args:
            timeout_seconds: Maximum execution time in seconds
        """
        self.timeout_seconds = timeout_seconds
        self._action_start_time = None
    
    def check_resource_limits(self) -> Tuple[bool, str]:
        """
        Check if current resource usage is within limits.
        
        Returns:
            Tuple of (within_limits, reason)
        """
        # Check timeout
        if self._action_start_time:
            elapsed = time.time() - self._action_start_time
            if elapsed > self.timeout_seconds:
                return False, f"Action exceeded timeout of {self.timeout_seconds}s"
        
        # Memory limit check (Unix only)
        if sys.platform != "win32":
            try:
                import resource
                memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024
                if memory_mb > MAX_ACTION_MEMORY_MB:
                    return False, f"Action exceeded memory limit of {MAX_ACTION_MEMORY_MB}MB"
            except (ImportError, AttributeError):
                # resource module not available or unsupported
                pass
        
        return True, ""
    
    def start_action(self) -> None:
        """Mark the start of action execution."""
        self._action_start_time = time.time()
    
    def end_action(self) -> None:
        """Mark the end of action execution."""
        self._action_start_time = None


def log_security_violation(violation_type: str, details: dict) -> None:
    """
    Log a security violation for audit trail.
    
    Args:
        violation_type: Type of security violation
        details: Dictionary with violation details
    """
    # In production, this would log to the audit log
    # For now, print to stderr for debugging
    violation_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "violation_type": violation_type,
        "details": details,
        "severity": "HIGH"
    }
    
    # Print to stderr (will be captured by audit log in production)
    print(f"SECURITY VIOLATION: {violation_log}", file=sys.stderr)
