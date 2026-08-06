"""
Hook Handler Base Class for Governor.py v1.5

This module defines the base class for all hook handlers. Hook handlers
are responsible for processing specific Devin CLI hook events and
returning protocol-compliant responses.

Key Components:
- HookHandler: Abstract base class for all hook handlers
- execute() method: Main entry point for hook processing
- can_block() method: Indicates if handler can block operations
- Response building via protocol module

This implements the hook handler system specified in v1.5 spec §4.3.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

# Import protocol module for response building (package-relative)
try:
    from ..protocol import build_hook_response
except ImportError:
    # Fallback for direct execution during development
    from protocol import build_hook_response


def log_handler_execution(handler_name: str, payload: Dict[str, Any], result: Dict[str, Any] = None):
    """Log handler execution to daily JSONL file for debugging."""
    try:
        from datetime import datetime
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily log file: Python-Execution-Log-MM/DD/YYYY.jsonl
        today = datetime.utcnow()
        log_filename = f"Python-Execution-Log-{today.strftime('%m/%d/%Y')}.jsonl"
        log_file = os.path.join(log_dir, log_filename)
        
        log_entry = {
            "timestamp": today.isoformat(),
            "handler": handler_name,
            "payload": payload,
            "result": result
        }
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        # Don't fail if logging fails
        pass


class HookHandler(ABC):
    """
    Abstract base class for all hook handlers.
    
    Hook handlers process specific Devin CLI hook events and return
    protocol-compliant responses. Each handler must:
    - Define the hook name it handles
    - Implement the execute() method
    - Indicate if it can block operations
    
    The execute() method receives:
    - payload: The hook event payload from Devin CLI
    - state_machine: The Governor state machine instance
    - engine: The rule engine instance
    
    It returns a protocol-compliant response dict.
    
    Example:
        class PreToolUseHandler(HookHandler):
            @property
            def hook_name(self) -> str:
                return "PreToolUse"
            
            @property
            def can_block(self) -> bool:
                return True
            
            def execute(self, payload: Dict[str, Any], state_machine: Any, 
                       engine: Any) -> Dict[str, Any]:
                # Implementation here
                return build_hook_response(
                    internal_decision="allow",
                    reason="Tool is allowed",
                    hook_event_name="PreToolUse"
                )
    """
    
    @property
    @abstractmethod
    def hook_name(self) -> str:
        """
        Get the hook name this handler processes.
        
        Returns:
            Hook name (e.g., "PreToolUse", "SessionStart")
        """
        pass
    
    @property
    @abstractmethod
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        Returns:
            True if handler can return "deny" decisions, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
                engine: Any) -> Dict[str, Any]:
        """
        Execute the hook handler logic.
        
        This method processes the hook event and returns a protocol-compliant
        response. The response should be built using build_hook_response()
        from the protocol module.
        
        Args:
            payload: Hook event payload from Devin CLI
            state_machine: Governor state machine instance
            engine: Rule engine instance
            
        Returns:
            Protocol-compliant hook response dict
        """
        pass
    
    def _build_response(self, internal_decision: str, reason: str, 
                       additional_context: str = "", updated_input: Optional[Dict] = None,
                       bypass_menu: Optional[Dict] = None, 
                       permission_decision: Optional[str] = None) -> Dict[str, Any]:
        """
        Build a protocol-compliant hook response.
        
        This is a convenience method that wraps build_hook_response()
        with the current hook name.
        
        Args:
            internal_decision: Internal decision (allow/deny/modify/warn)
            reason: Human-readable explanation
            additional_context: Additional context for agent's prompt
            updated_input: Modified tool input (for modify decisions)
            bypass_menu: Bypass menu payload
            permission_decision: Permission decision for PermissionRequest
            
        Returns:
            Protocol-compliant hook response dict
        """
        return build_hook_response(
            internal_decision=internal_decision,
            reason=reason,
            hook_event_name=self.hook_name,
            additional_context=additional_context,
            updated_input=updated_input,
            bypass_menu=bypass_menu,
            permission_decision=permission_decision
        )
    
    def _build_allow_response(self, reason: str, additional_context: str = "") -> Dict[str, Any]:
        """
        Build an allow response.
        
        Args:
            reason: Human-readable explanation
            additional_context: Additional context for agent's prompt
            
        Returns:
            Protocol-compliant allow response
        """
        return self._build_response("allow", reason, additional_context)
    
    def _build_deny_response(self, reason: str, additional_context: str = "") -> Dict[str, Any]:
        """
        Build a deny response.
        
        Args:
            reason: Human-readable explanation
            additional_context: Additional context for agent's prompt
            
        Returns:
            Protocol-compliant deny response
        """
        return self._build_response("deny", reason, additional_context)
    
    def _build_modify_response(self, reason: str, updated_input: Dict[str, Any], 
                              additional_context: str = "") -> Dict[str, Any]:
        """
        Build a modify response.
        
        Args:
            reason: Human-readable explanation
            updated_input: Modified tool input
            additional_context: Additional context for agent's prompt
            
        Returns:
            Protocol-compliant modify response
        """
        return self._build_response("modify", reason, additional_context, updated_input)
    
    def _build_warn_response(self, reason: str, additional_context: str = "") -> Dict[str, Any]:
        """
        Build a warn response.
        
        Args:
            reason: Human-readable explanation
            additional_context: Additional context for agent's prompt
            
        Returns:
            Protocol-compliant warn response
        """
        return self._build_response("warn", reason, additional_context)
