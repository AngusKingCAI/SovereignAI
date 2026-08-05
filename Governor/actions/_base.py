"""
Action Base Classes for Governor.py v1.5

This module defines the base classes and data structures for Governor's
action system. Actions are the executable components of rules that perform
specific governance logic.

Key Components:
- ActionResult: Dataclass for action execution results
- ActionContext: Dataclass for action execution context
- RuleAction: Abstract base class for all actions

This implements the action system specified in v1.5 spec §4.2.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


@dataclass
class ActionResult:
    """
    Result of action execution.
    
    Actions return an ActionResult that indicates:
    - decision: The governance decision (allow/deny/modify/warn)
    - reason: Human-readable explanation
    - modified_payload: Modified tool input (only for modify decisions)
    - additional_context: Context to inject into agent's prompt
    - bypass_key: Key for bypass registry (if action can be bypassed)
    - bypass_menu: Bypass menu options (if action presents menu)
    
    Attributes:
        decision: Internal decision string ("allow", "deny", "modify", "warn")
        reason: Human-readable explanation for the decision
        modified_payload: Modified tool input (only when decision == "modify")
        additional_context: Additional context to inject into agent's prompt
        bypass_key: Unique key for bypass registry (e.g., "rule_id:tool_name")
        bypass_menu: Bypass menu options (if action presents menu)
    """
    decision: str  # "allow" | "deny" | "modify" | "warn"
    reason: str
    modified_payload: Optional[Dict[str, Any]] = None
    additional_context: str = ""
    bypass_key: str = ""
    bypass_menu: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate decision value."""
        valid_decisions = ["allow", "deny", "modify", "warn"]
        if self.decision not in valid_decisions:
            raise ValueError(f"Invalid decision: {self.decision}. Must be one of {valid_decisions}")
        
        # Ensure modified_payload is only set for modify decisions
        if self.decision != "modify" and self.modified_payload is not None:
            raise ValueError("modified_payload can only be set when decision == 'modify'")


@dataclass
class ActionContext:
    """
    Context provided to actions during execution.
    
    This context contains all the information an action might need to
    make governance decisions, including:
    - State machine access for state-based rules
    - Tool normalizer for canonical tool names
    - Current hook name and payload
    - Trace ID for audit correlation
    
    Attributes:
        state_machine: State machine instance for state access
        tool_normalizer: Tool normalizer for canonical names
        hook_name: Name of the current hook event
        payload: Original hook payload
        trace_id: Trace ID for audit correlation
        timestamp: Execution timestamp
    """
    state_machine: Any  # StateMachine instance
    tool_normalizer: Any  # Tool normalizer instance
    hook_name: str
    payload: Dict[str, Any]
    trace_id: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class RuleAction(ABC):
    """
    Abstract base class for all Governor actions.
    
    Actions are the executable components of rules. Each action must:
    - Define a name
    - Specify required parameters
    - Implement evaluate() method
    
    Actions are instantiated by the rule engine and executed with specific
    parameters from rule YAML files.
    
    Example:
        class BlockFileDeletion(RuleAction):
            @property
            def name(self) -> str:
                return "block_file_deletion"
            
            def get_required_params(self) -> List[str]:
                return ["file_pattern"]
            
            # Optional: Add memoization for performance
            # from ..memoization import memoize_result
            # @memoize_result(ttl_seconds=120)
            def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any], 
                       context: ActionContext) -> ActionResult:
                # Implementation here
                pass
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get the action name.
        
        Returns:
            Unique action name used in rule YAML files
        """
        pass
    
    @abstractmethod
    def get_required_params(self) -> List[str]:
        """
        Get list of required parameter names.
        
        The rule engine will validate that all required parameters are
        provided in the rule YAML file before executing the action.
        
        Returns:
            List of parameter names that must be provided
        """
        pass
    
    @abstractmethod
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any], 
                 context: ActionContext) -> ActionResult:
        """
        Evaluate the action with given payload and parameters.
        
        This is the main execution method for the action. It receives:
        - payload: The original hook event payload
        - params: Parameters from the rule YAML file
        - context: ActionContext with state and utility access
        
        Args:
            payload: Original hook event payload
            params: Parameters from rule YAML file
            context: ActionContext with state machine and utilities
            
        Returns:
            ActionResult with decision and metadata
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate that all required parameters are provided.
        
        Args:
            params: Parameters dictionary to validate
            
        Raises:
            ValueError: If required parameters are missing
        """
        required = self.get_required_params()
        missing = [p for p in required if p not in params]
        if missing:
            raise ValueError(f"Missing required parameters for {self.name}: {missing}")
    
    def get_optional_params(self) -> List[str]:
        """
        Get list of optional parameter names.
        
        Subclasses can override this to specify optional parameters.
        
        Returns:
            List of optional parameter names
        """
        return []
    
    def get_param_schema(self) -> Dict[str, Any]:
        """
        Get parameter schema for validation.
        
        Subclasses can override this to provide detailed parameter
        schemas for validation. This is used by the rule engine to
        validate parameter types and values.
        
        Returns:
            Dictionary mapping parameter names to schema definitions
        """
        return {}
