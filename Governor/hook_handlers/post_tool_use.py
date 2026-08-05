"""
PostToolUse Hook Handler for Governor.py v1.5

This handler processes the PostToolUse hook event, which is triggered
after a tool has been executed. It logs execution, validates output,
determines phase transitions, and increments counters.

Key Responsibilities:
- Execution logging to audit trail
- Output validation
- Phase transition determination
- Counter increment (successful execution only)
- Auto-fix action triggering
- Protocol-compliant response

This implements the PostToolUse handler specified in v1.5 spec §4.3.
"""

from typing import Dict, Any

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler

# Import tool normalizer (package-relative)
try:
    from ..tool_normalizer import normalize_tool_name
except ImportError:
    from tool_normalizer import normalize_tool_name

# Import audit logger (package-relative)
try:
    from ..audit.audit_log import log_event
except ImportError:
    from audit.audit_log import log_event


class PostToolUseHandler(HookHandler):
    """
    Handler for PostToolUse hook events.
    
    PostToolUse is triggered after a tool has been executed. This handler
    logs execution, validates output, determines phase transitions, and
    increments counters for successful executions.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "PostToolUse"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        PostToolUse cannot block - the tool has already executed.
        """
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the PostToolUse handler logic.
        
        This method:
        1. Normalizes the tool name
        2. Logs execution to audit trail
        3. Validates tool output
        4. Determines phase transition based on execution
        5. Increments counter for successful execution
        6. Triggers auto-fix actions if needed
        7. Returns protocol-compliant allow response
        
        Args:
            payload: PostToolUse hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in PostToolUse)
            
        Returns:
            Protocol-compliant allow response
        """
        # Extract tool information from payload
        tool_name = payload.get("tool", "")
        tool_input = payload.get("input", {})
        tool_output = payload.get("output", {})
        tool_status = payload.get("status", "success")
        
        # Normalize tool name to canonical form
        canonical_tool = normalize_tool_name(tool_name)
        
        # Get current phase
        current_phase = state_machine.get_phase()
        
        # Log execution to audit trail
        self._log_execution(canonical_tool, tool_input, tool_output, tool_status, state_machine)
        
        # Evaluate rules for PostToolUse
        try:
            from ..actions._base import ActionContext
            from ..tool_normalizer import ToolNormalizer
        except ImportError:
            from actions._base import ActionContext
            from tool_normalizer import ToolNormalizer
        
        if engine:
            context = ActionContext(
                state_machine=state_machine,
                tool_normalizer=ToolNormalizer(),
                hook_name="PostToolUse",
                payload=payload,
                trace_id=payload.get("trace_id", "unknown")
            )
            rule_results = engine.evaluate_rules("PostToolUse", payload, context)
            
            # Check if any rules returned deny or warn
            for result in rule_results:
                if result.decision == "deny":
                    # Rules can deny in PostToolUse for cleanup/violation handling
                    return self._build_block_response(
                        reason=f"Rule enforcement in PostToolUse: {result.reason}",
                        additional_context=f"Rule: {result.action_name}"
                    )
                elif result.decision == "warn":
                    additional_context += f"\n⚠️ Rule warning: {result.reason}"
        
        # Validate tool output
        validation_result = self._validate_output(canonical_tool, tool_output, tool_status)
        
        # Determine phase transition based on execution
        self._determine_phase_transition(canonical_tool, tool_status, current_phase, state_machine)
        
        # Increment counter for successful execution
        if tool_status == "success":
            if canonical_tool in ["exec", "file_write", "file_edit"]:
                state_machine.increment_counter("exec")
            elif canonical_tool in ["web_search", "read"]:
                # Research tools don't increment exec counter
                pass
        
        # Trigger auto-fix actions if validation failed
        additional_context = ""
        if not validation_result["valid"]:
            additional_context = self._build_validation_context(validation_result)
        
        # Build response
        return self._build_allow_response(
            reason=f"Tool {canonical_tool} execution completed. Status: {tool_status}",
            additional_context=additional_context
        )
    
    def _log_execution(self, canonical_tool: str, tool_input: Dict[str, Any], 
                     tool_output: Dict[str, Any], tool_status: str, 
                     state_machine: Any) -> None:
        """
        Log tool execution to audit trail.
        
        Args:
            canonical_tool: Canonical tool name
            tool_input: Tool input parameters
            tool_output: Tool output data
            tool_status: Execution status (success/error)
            state_machine: State machine instance
        """
        # Log execution to audit trail
        log_event(
            hook_name="PostToolUse",
            payload={"tool": canonical_tool, "input": tool_input},
            response={"tool": canonical_tool, "status": tool_status, "output": tool_output},
            level="info"
        )
    
    def _validate_output(self, canonical_tool: str, tool_output: Dict[str, Any], 
                       tool_status: str) -> Dict[str, Any]:
        """
        Validate tool output.
        
        This method performs basic output validation. In Phase 2.5,
        this will be enhanced with rule-based validation.
        
        Args:
            canonical_tool: Canonical tool name
            tool_output: Tool output data
            tool_status: Execution status
            
        Returns:
            Validation result dict with 'valid' boolean and 'errors' list
        """
        validation_result = {
            "valid": True,
            "errors": []
        }
        
        # If execution failed, mark as invalid
        if tool_status != "success":
            validation_result["valid"] = False
            validation_result["errors"].append(f"Tool execution failed with status: {tool_status}")
            return validation_result
        
        # Tool-specific validation
        if canonical_tool == "exec":
            # Check for common error patterns in output
            output_str = str(tool_output)
            if "error" in output_str.lower() or "failed" in output_str.lower():
                validation_result["valid"] = False
                validation_result["errors"].append("Output contains error indicators")
        
        return validation_result
    
    def _determine_phase_transition(self, canonical_tool: str, tool_status: str,
                                  current_phase: str, state_machine: Any) -> None:
        """
        Determine phase transition based on tool execution.
        
        This method analyzes the tool execution and determines if
        a phase transition is appropriate.
        
        Args:
            canonical_tool: Canonical tool name
            tool_status: Execution status
            current_phase: Current phase
            state_machine: State machine instance
        """
        # Phase transition logic
        if tool_status != "success":
            # Failed execution - stay in current phase
            return
        
        # Successful execution - consider phase transitions
        if current_phase == "INIT" and canonical_tool in ["read", "web_search"]:
            # Initial research completed - transition to RESEARCH
            state_machine.set_phase("RESEARCH")
        elif current_phase == "RESEARCH" and canonical_tool in ["read", "web_search"]:
            # Research ongoing - stay in RESEARCH
            pass
        elif current_phase == "PLAN" and canonical_tool == "exec":
            # Starting execution - transition to EXECUTE
            state_machine.set_phase("EXECUTE")
        elif current_phase == "EXECUTE" and canonical_tool in ["exec", "file_write", "file_edit"]:
            # Execution ongoing - stay in EXECUTE
            pass
        elif current_phase == "VALIDATE" and canonical_tool == "exec":
            # Validation testing - stay in VALIDATE
            pass
        elif current_phase == "COMMIT":
            # Terminal phase - no transitions
            pass
    
    def _build_validation_context(self, validation_result: Dict[str, Any]) -> str:
        """
        Build validation context for additional information.
        
        Args:
            validation_result: Validation result from _validate_output
            
        Returns:
            Context string with validation errors
        """
        context = "\n=== OUTPUT VALIDATION ===\n"
        for error in validation_result["errors"]:
            context += f"⚠️ {error}\n"
        context += "=== END VALIDATION ===\n"
        return context
