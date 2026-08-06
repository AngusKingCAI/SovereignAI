"""
Circuit Breaker Pattern for Governor.py v1.5

This module implements the circuit breaker pattern per v1.5 spec §12.7.
Circuit breakers prevent cascading failures by temporarily blocking
actions that have failed repeatedly.

Key Components:
- CircuitBreakerManager: Manages multiple circuit breakers per action/rule
- CircuitBreaker: Individual circuit breaker with state machine
- Three states: closed, open, half-open

This implements the circuit breaker specified in v1.5 spec §12.7.
"""

from collections import deque
from threading import Lock
import os
import sys
import json
import time
from typing import Dict, Tuple, Any
from datetime import datetime

HALF_OPEN_TIMEOUT_S = 30
FAILURE_WINDOW_S = 60


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily log file: Layer2-Python-Execution-Log-MM-DD-YYYY.jsonl
        today = datetime.utcnow()
        log_filename = f"Layer2-Python-Execution-Log-{today.strftime('%m-%d-%Y')}.jsonl"
        log_file = os.path.join(log_dir, log_filename)
        
        log_entry = {
            "File": component,
            "hook": component,
            "Time": today.strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
            f.flush()
            
    except Exception as e:
        # Don't fail if logging fails, but print error to stderr
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


class CircuitBreakerManager:
    """
    Per-action circuit breaker tracking per v1.5 spec §12.7.
    
    Manages circuit breakers for (action_name, rule_id) pairs.
    Uses environment variables for configuration:
    - GOVERNOR_CIRCUIT_BREAKER_THRESHOLD: Failure threshold (default: 3)
    - GOVERNOR_CIRCUIT_BREAKER_OPEN_S: Open timeout in seconds (default: 300)
    """
    
    def __init__(self):
        self.breakers: Dict[Tuple[str, str], 'CircuitBreaker'] = {}
        self.lock = Lock()
        self.threshold = int(os.getenv("GOVERNOR_CIRCUIT_BREAKER_THRESHOLD", "3"))
        self.open_timeout_s = int(os.getenv("GOVERNOR_CIRCUIT_BREAKER_OPEN_S", "300"))
        
    def allow(self, action_name: str, rule_id: str) -> Tuple[bool, str]:
        """
        Check if action is allowed, return (allowed, reason).
        
        Args:
            action_name: Name of the action
            rule_id: ID of the rule
            
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        key = (action_name, rule_id)
        with self.lock:
            if key not in self.breakers:
                self.breakers[key] = CircuitBreaker(self.threshold, self.open_timeout_s)
            allowed, reason = self.breakers[key].allow()
            
            # Log circuit breaker check
            log_execution("CircuitBreaker", {
                "action": "allow",
                "action_name": action_name,
                "rule_id": rule_id,
                "allowed": allowed,
                "reason": reason
            })
            
            return allowed, reason
            
    def record_success(self, action_name: str, rule_id: str) -> None:
        """
        Record a successful action execution.
        
        Args:
            action_name: Name of the action
            rule_id: ID of the rule
        """
        key = (action_name, rule_id)
        with self.lock:
            if key in self.breakers:
                self.breakers[key].record_success()
                
    def record_failure(self, action_name: str, rule_id: str) -> None:
        """
        Record a failed action execution.
        
        Args:
            action_name: Name of the action
            rule_id: ID of the rule
        """
        # Log circuit breaker failure
        log_execution("CircuitBreaker", {
            "action": "record_failure",
            "action_name": action_name,
            "rule_id": rule_id
        })
        
        key = (action_name, rule_id)
        with self.lock:
            if key not in self.breakers:
                self.breakers[key] = CircuitBreaker(self.threshold, self.open_timeout_s)
            self.breakers[key].record_failure()
            
    def status(self) -> Dict[Tuple[str, str], Dict[str, Any]]:
        """
        Return status of all circuit breakers for CLI inspection.
        
        Returns:
            Dictionary mapping (action_name, rule_id) to breaker status
        """
        with self.lock:
            return {
                key: breaker.status()
                for key, breaker in self.breakers.items()
            }


class CircuitBreaker:
    """
    Individual circuit breaker with state machine.
    
    States:
    - closed: Normal operation, actions allowed
    - open: Actions blocked due to repeated failures
    - half_open: Testing if the action has recovered
    
    Transition Rules:
    - closed → open: When failure threshold reached
    - open → half_open: After open timeout expires
    - half_open → closed: On successful action
    - half_open → open: On failed action
    """
    
    def __init__(self, failure_threshold: int, open_timeout_s: int):
        self.failure_threshold = failure_threshold
        self.open_timeout_s = open_timeout_s
        self.failures = deque(maxlen=10)  # Spec: maxlen=10
        self.state = "closed"
        self.last_failure_time = None
        self.half_open_since = None
        self.lock = Lock()
        
    def allow(self) -> Tuple[bool, str]:
        """
        Check if action is allowed, return (allowed, reason).
        
        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        with self.lock:
            if self.state == "open":
                # Check if timeout has expired
                if time.time() - self.last_failure_time > self.open_timeout_s:
                    self.state = "half_open"
                    self.half_open_since = time.time()
                    return True, "circuit_breaker_half_open"
                return False, "circuit_breaker_open"
            elif self.state == "half_open":
                # Check if half-open timeout has expired
                if time.time() - self.half_open_since > HALF_OPEN_TIMEOUT_S:
                    self.state = "open"
                    self.last_failure_time = time.time()
                    return False, "circuit_breaker_half_open_timeout"
                return True, "circuit_breaker_half_open_test"
            return True, "circuit_breaker_closed"
            
    def record_success(self) -> None:
        """Record a successful action execution."""
        with self.lock:
            if self.state == "half_open":
                # Success in half-open state, close the circuit
                self.state = "closed"
                self.failures.clear()
                self.half_open_since = None
                
    def record_failure(self) -> None:
        """Record a failed action execution."""
        with self.lock:
            # Filter failures outside window
            now = time.time()
            self.failures = deque([f for f in self.failures if now - f < FAILURE_WINDOW_S], maxlen=10)
            self.failures.append(now)
            
            if self.state == "half_open":
                # Reopen on half-open failure
                self.state = "open"
                self.last_failure_time = now
                self.half_open_since = None
            elif len(self.failures) >= self.failure_threshold:
                # Threshold reached, open the circuit
                self.state = "open"
                self.last_failure_time = now
                
    def status(self) -> Dict[str, Any]:
        """
        Return current status of the circuit breaker.
        
        Returns:
            Dictionary with current state and statistics
        """
        with self.lock:
            return {
                "state": self.state,
                "failure_count": len(self.failures),
                "failure_threshold": self.failure_threshold,
                "last_failure_time": self.last_failure_time,
                "half_open_since": self.half_open_since,
                "open_timeout_s": self.open_timeout_s
            }
