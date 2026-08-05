"""
Audit Logging for Governor.py v1.5

This module implements hash-chained JSONL audit logging as specified in
v1.5 spec §5.1. All Governor events are logged with cryptographic
integrity verification and trace correlation.

Audit Trail Features:
- Hash-chained JSONL format (append-only)
- SHA-256 cryptographic linking between events
- Trace ID correlation for event tracing
- Internal decision recording (allow/deny/modify/warn)
- current_hash field naming per spec §5.1
- Append-only file operations for integrity

Audit Event Structure:
{
  "timestamp": "2026-08-05T12:00:00.000000",
  "hook_name": "PreToolUse",
  "trace_id": "uuid4",
  "prev_hash": "sha256_of_previous_event",
  "current_hash": "sha256_of_this_event",
  "decision": "allow",  # Internal decision
  "level": "info",
  "data": {...}  # Full response data
}
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Audit log file path
AUDIT_DIR = "Governor/logs"
AUDIT_FILE = os.path.join(AUDIT_DIR, "audit.jsonl")

# Current trace ID for this session
_current_trace_id: Optional[str] = None


def set_trace_id(trace_id: str) -> None:
    """
    Set the trace ID for the current session.
    
    Args:
        trace_id: UUID4 trace ID string
    """
    global _current_trace_id
    _current_trace_id = trace_id


def get_trace_id() -> str:
    """
    Get the current trace ID, generating one if not set.
    
    Returns:
        Trace ID string
    """
    global _current_trace_id
    if _current_trace_id is None:
        _current_trace_id = str(uuid.uuid4())
    return _current_trace_id


def _compute_hash(data: Dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of event data.
    
    Args:
        data: Event data dictionary
        
    Returns:
        SHA-256 hash string
    """
    # Canonical JSON representation (sorted keys, no extra whitespace)
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode()).hexdigest()


def _get_last_hash() -> str:
    """
    Get the hash of the last event in the audit log.
    
    Returns:
        SHA-256 hash string, or empty string if log is empty
    """
    if not os.path.exists(AUDIT_FILE):
        return ""
    
    try:
        with open(AUDIT_FILE, 'r') as f:
            lines = f.readlines()
            if not lines:
                return ""
            
            # Get the last line (most recent event)
            last_line = lines[-1].strip()
            if not last_line:
                return ""
            
            event = json.loads(last_line)
            return event.get("current_hash", "")
    except (json.JSONDecodeError, IOError):
        return ""


def log_event(hook_name: str, payload: Dict[str, Any], response: Dict[str, Any], level: str = "info") -> None:
    """
    Log event with hash chaining and internal decision.
    
    Args:
        hook_name: Name of the hook event
        payload: Original hook payload
        response: Governor's response
        level: Log level (info, warning, error)
        
    Implementation per v1.5 spec §5.1:
    - Records internal decision (allow/deny/modify/warn) not Devin protocol decision
    - Uses current_hash field naming (not event_hash)
    - Includes trace_id for correlation
    """
    # Ensure audit directory exists
    os.makedirs(AUDIT_DIR, exist_ok=True)
    
    # Get previous hash for chaining
    prev_hash = _get_last_hash()
    
    # Extract internal decision from governor_internal field
    internal_decision = response.get("governor_internal", {}).get("decision", "unknown")
    
    # Build event data for hashing (without the hash fields themselves)
    event_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "hook_name": hook_name,
        "trace_id": get_trace_id(),
        "prev_hash": prev_hash,
        "decision": internal_decision,  # INTERNAL decision per v1.2 fix
        "level": level,
        "data": response
    }
    
    # Compute current hash of this event
    current_hash = _compute_hash(event_data)
    
    # Add hash to event for logging
    event_data["current_hash"] = current_hash  # FIXED: current_hash per spec §5.1
    
    # Append to audit log (append-only)
    with open(AUDIT_FILE, 'a', newline='\n') as f:
        f.write(json.dumps(event_data))
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def get_audit_log() -> list:
    """
    Get all events from the audit log.
    
    Returns:
        List of audit event dictionaries
    """
    if not os.path.exists(AUDIT_FILE):
        return []
    
    events = []
    with open(AUDIT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
    
    return events


def verify_audit_integrity() -> bool:
    """
    Verify the integrity of the audit log by checking hash chain.
    
    Returns:
        True if audit log is intact, False if tampering detected
    """
    events = get_audit_log()
    
    if not events:
        return True  # Empty log is valid
    
    # Check hash chain
    for i, event in enumerate(events):
        # Verify current_hash matches computed hash
        event_copy = event.copy()
        computed_hash = event_copy.pop("current_hash", "")
        expected_hash = _compute_hash(event_copy)
        
        if computed_hash != expected_hash:
            return False
        
        # Verify prev_hash matches previous event's current_hash
        if i > 0:
            prev_hash = event.get("prev_hash", "")
            prev_event_hash = events[i-1].get("current_hash", "")
            if prev_hash != prev_event_hash:
                return False
        
        # First event should have empty prev_hash
        if i == 0 and event.get("prev_hash") != "":
            return False
    
    return True


def clear_audit_log() -> None:
    """Clear the audit log (use with caution - for testing only)."""
    if os.path.exists(AUDIT_FILE):
        os.remove(AUDIT_FILE)


@contextmanager
def audit_context(hook_name: str):
    """
    Context manager for automatic audit logging within a hook.
    
    Args:
        hook_name: Name of the hook event
        
    Example:
        with audit_context("PreToolUse"):
            # Perform hook logic
            log_event("PreToolUse", payload, response)
    """
    # Can be used to set up context for audit logging
    # Currently implemented as a pass-through
    yield


def get_audit_stats() -> Dict[str, Any]:
    """
    Get statistics about the audit log.
    
    Returns:
        Dictionary with audit log statistics
    """
    events = get_audit_log()
    
    if not events:
        return {
            "total_events": 0,
            "decision_counts": {},
            "level_counts": {},
            "hook_counts": {}
        }
    
    decision_counts = {}
    level_counts = {}
    hook_counts = {}
    
    for event in events:
        # Count decisions
        decision = event.get("decision", "unknown")
        decision_counts[decision] = decision_counts.get(decision, 0) + 1
        
        # Count levels
        level = event.get("level", "unknown")
        level_counts[level] = level_counts.get(level, 0) + 1
        
        # Count hooks
        hook = event.get("hook_name", "unknown")
        hook_counts[hook] = hook_counts.get(hook, 0) + 1
    
    return {
        "total_events": len(events),
        "decision_counts": decision_counts,
        "level_counts": level_counts,
        "hook_counts": hook_counts,
        "integrity_verified": verify_audit_integrity()
    }
