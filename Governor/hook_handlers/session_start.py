"""
SessionStart Hook Handler for Governor.py v1.5

This handler processes the SessionStart hook event, which is triggered
when a new Devin CLI session begins. It initializes the Governor state
machine and prepares the session for governance.

Key Responsibilities:
- Initialize phase to INIT
- Inject constitution context into agent's prompt
- Load past errors from state flags
- Pre-populate bypasses from environment variables
- Reset counters to 0
- Return protocol-compliant response

This implements the SessionStart handler specified in v1.5 spec §4.3.
"""

import os
from typing import Dict, Any

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class SessionStartHandler(HookHandler):
    """
    Handler for SessionStart hook events.
    
    SessionStart is triggered when a new Devin CLI session begins.
    This handler initializes the Governor state machine and prepares
    the session for governance.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "SessionStart"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        SessionStart cannot block - it's always an allow operation.
        """
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the SessionStart handler logic.
        
        This method:
        1. Initializes the phase to INIT
        2. Injects constitution context into the agent's prompt
        3. Loads past errors from state flags
        4. Pre-populates bypasses from environment variables
        5. Resets counters to 0
        6. Returns a protocol-compliant allow response
        
        Args:
            payload: SessionStart hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in SessionStart)
            
        Returns:
            Protocol-compliant allow response with constitution context
        """
        # Initialize phase to INIT
        state_machine.set_phase("INIT")
        
        # Reset counters to 0
        state_machine.set_counter("exec", 0)
        state_machine.set_counter("validate", 0)
        
        # Load past errors from flags
        research_required = state_machine.get_flag("research_required")
        
        # Pre-populate bypasses from environment variable
        # Format: GOVERNOR_BYPASSES="rule_id:tool,rule_id:tool,..."
        bypass_env = os.environ.get("GOVERNOR_BYPASSES", "")
        if bypass_env:
            for bypass_key in bypass_env.split(","):
                bypass_key = bypass_key.strip()
                if bypass_key:
                    # Parse rule_id:tool format or just rule_id
                    parts = bypass_key.split(":")
                    if len(parts) >= 2:
                        rule_id = parts[0]
                        tool_name = parts[1]
                    else:
                        rule_id = bypass_key
                        tool_name = "*"
                    
                    state_machine.add_bypass(
                        rule_id=rule_id,
                        tool_name=tool_name,
                        scope="session",
                        reason="Pre-populated from GOVERNOR_BYPASSES environment variable",
                        source="environment"
                    )
        
        # Build constitution context for injection
        constitution_context = self._build_constitution_context(state_machine)
        
        # Build additional context with past errors
        additional_context = ""
        if research_required:
            additional_context += "\n⚠️ PAST ERROR: Research phase was required in previous session."
        
        # Return protocol-compliant allow response
        return self._build_allow_response(
            reason="Session initialized. Governor is active.",
            additional_context=constitution_context + additional_context
        )
    
    def _build_constitution_context(self, state_machine: Any) -> str:
        """
        Build constitution context for injection into agent's prompt.
        
        The constitution context reminds the agent of the governance
        framework and the current phase requirements.
        
        Args:
            state_machine: Governor state machine instance
            
        Returns:
            Constitution context string
        """
        current_phase = state_machine.get_phase()
        
        context = f"""
=== GOVERNOR CONSTITUTION ===
Governor v1.5 is active. Current phase: {current_phase}

Phase Requirements:
- INIT: Read-only mode for context gathering
- RESEARCH: Information gathering and analysis
- PLAN: Strategy and task planning
- EXECUTE: Implementation and execution
- VALIDATE: Testing and verification
- COMMIT: Final review and commitment

Governance Rules:
- All tool usage is subject to phase-based gating
- Destructive operations require explicit approval
- Violations are logged and may block session completion
- Bypass commands available: /bypass <rule_id>:<tool>

Compliance Status: Active
=== END CONSTITUTION ===
"""
        return context
