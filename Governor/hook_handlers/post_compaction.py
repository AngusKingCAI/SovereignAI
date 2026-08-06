"""
PostCompaction Hook Handler for Governor.py v1.5

This handler processes the PostCompaction hook event, which is triggered
after conversation compaction. It re-injects Governor state into the
compacted conversation to maintain governance continuity.

Key Responsibilities:
- Phase state re-injection
- Counter state re-injection
- Flag state re-injection
- Bypass registry re-injection
- State integrity verification
- Phase reminder context injection
- Protocol-compliant response

This implements the PostCompaction handler specified in v1.5 spec §4.3.
"""

from typing import Dict, Any

# Import base class (package-relative)
try:
    from ._base import HookHandler, log_handler_execution
except ImportError:
    from hook_handlers._base import HookHandler, log_handler_execution


class PostCompactionHandler(HookHandler):
    """
    Handler for PostCompaction hook events.
    
    PostCompaction is triggered after conversation compaction. This handler
    re-injects Governor state into the compacted conversation to maintain
    governance continuity across compaction events.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "PostCompaction"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        PostCompaction cannot block - compaction has already occurred.
        """
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the PostCompaction handler logic.
        
        This method:
        1. Re-injects phase state into context
        2. Re-injects counter state into context
        3. Re-injects flag state into context
        4. Re-injects bypass registry into context
        5. Verifies state integrity
        6. Forces phase reminder into context
        7. Returns protocol-compliant allow response
        
        Args:
            payload: PostCompaction hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in PostCompaction)
            
        Returns:
            Protocol-compliant allow response with state re-injection
        """
        # Get current state
        current_phase = state_machine.get_phase()
        exec_count = state_machine.get_counter("exec")
        validate_count = state_machine.get_counter("validate")
        research_required = state_machine.get_flag("research_required")
        
        # Get bypass count
        total_bypasses = 0
        for scope in ["runtime", "team", "once", "session"]:
            total_bypasses += len(state_machine.state["bypasses"][scope])
        
        # Verify state integrity
        integrity_check = self._verify_state_integrity(state_machine)
        
        # Build state re-injection context
        state_context = self._build_state_reinjection_context(
            current_phase, exec_count, validate_count, research_required,
            total_bypasses, integrity_check
        )
        
        # Build response
        result = self._build_allow_response(
            reason=f"Post-compaction state re-injection complete. Phase: {current_phase}",
            additional_context=state_context
        )
        
        # Log execution
        log_handler_execution("post_compaction", payload, result)
        
        return result
    
    def _verify_state_integrity(self, state_machine: Any) -> bool:
        """
        Verify state integrity after compaction.
        
        This method checks that the state machine's internal state
        is consistent and valid after compaction.
        
        Args:
            state_machine: State machine instance
            
        Returns:
            True if state is valid, False otherwise
        """
        # Check that required state keys exist
        required_keys = ["phase", "counters", "flags", "bypasses", "violations", "metadata"]
        for key in required_keys:
            if key not in state_machine.state:
                return False
        
        # Check that counters are non-negative
        for counter_name, counter_value in state_machine.state["counters"].items():
            if counter_value < 0:
                return False
        
        # Check that bypass scopes exist
        required_scopes = ["runtime", "team", "once", "session"]
        for scope in required_scopes:
            if scope not in state_machine.state["bypasses"]:
                return False
        
        return True
    
    def _build_state_reinjection_context(self, current_phase: str, exec_count: int,
                                       validate_count: int, research_required: bool,
                                       total_bypasses: int, integrity_check: bool) -> str:
        """
        Build state re-injection context for the agent.
        
        This method creates a context string that reminds the agent
        of the current Governor state after compaction.
        
        Args:
            current_phase: Current phase
            exec_count: Number of executions
            validate_count: Number of validations
            research_required: Research required flag
            total_bypasses: Total bypass count
            integrity_check: State integrity check result
            
        Returns:
            Context string with state information
        """
        context = f"""
=== GOVERNOR STATE RE-INJECTION ===
Current Phase: {current_phase}

Counters:
- Executions: {exec_count}
- Validations: {validate_count}

Flags:
- Research Required: {research_required}

Bypasses:
- Active bypasses: {total_bypasses}

State Integrity: {'VALID' if integrity_check else 'INVALID'}

=== PHASE REMINDER ===
You are currently in the {current_phase} phase.
Ensure all tool usage complies with phase requirements.
Available tools in {current_phase}: {self._get_allowed_tools(current_phase)}

To check phase requirements, use the constitution context from SessionStart.
=== END STATE RE-INJECTION ===
"""
        return context
    
    def _get_allowed_tools(self, phase: str) -> str:
        """
        Get allowed tools for a phase as a string.
        
        Args:
            phase: Phase name
            
        Returns:
            Comma-separated list of allowed tools
        """
        # Import state_machine for PHASE_ALLOWLIST (package-relative)
        try:
            from ..state_machine import PHASE_ALLOWLIST
        except ImportError:
            from state_machine import PHASE_ALLOWLIST
        
        allowed = PHASE_ALLOWLIST.get(phase, [])
        return ", ".join(allowed) if allowed else "None"
