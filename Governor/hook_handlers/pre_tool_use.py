"""
PreToolUse Hook Handler for Governor.py v1.5

This handler processes the PreToolUse hook event, which is triggered
before a tool is executed. It is the primary gate for tool usage enforcement.

Key Responsibilities:
- Phase allowlist checking
- Validation rule application via rule engine
- Phase inference from tool usage patterns
- Bypass registry checking
- Tool input rewriting (updatedInput)
- Block with bypass key generation
- Menu payload attachment (optional)
- Protocol-compliant response

This implements the PreToolUse handler specified in v1.5 spec §4.3.
"""

import uuid
import os
from typing import Dict, Any, Optional

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

# Import ActionContext (package-relative)
try:
    from ..actions._base import ActionContext
except ImportError:
    from actions._base import ActionContext


class PreToolUseHandler(HookHandler):
    """
    Handler for PreToolUse hook events.
    
    PreToolUse is triggered before a tool is executed. This handler is
    the primary enforcement point for phase-based tool gating and rule validation.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "PreToolUse"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        PreToolUse can block tool execution.
        """
        return True
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the PreToolUse handler logic.
        
        This method:
        1. Normalizes the tool name
        2. Checks phase allowlist
        3. Applies validation rules via rule engine
        4. Infers phase from tool usage patterns
        5. Checks bypass registry
        6. Generates bypass key if blocking
        7. Returns protocol-compliant response (allow/deny/modify)
        
        Args:
            payload: PreToolUse hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance
            
        Returns:
            Protocol-compliant hook response (allow/deny/modify)
        """
        # Extract tool information from payload
        tool_name = payload.get("tool", "")
        tool_input = payload.get("input", {})
        
        # Normalize tool name to canonical form
        canonical_tool = normalize_tool_name(tool_name)
        
        # Get current phase
        current_phase = state_machine.get_phase()
        
        # Check bypass registry FIRST (before phase allowlist)
        # Try multiple possible rule IDs for bypass
        possible_rule_ids = ["phase_enforcement", "block_destructive", canonical_tool]
        for rule_id in possible_rule_ids:
            if state_machine.is_bypassed(rule_id, canonical_tool):
                # Tool is bypassed, allow with warning
                return self._build_allow_response(
                    reason=f"Tool {canonical_tool} bypassed for phase {current_phase}",
                    additional_context="⚠️ Tool usage bypassed - ensure compliance with phase requirements"
                )
        
        # Check phase allowlist
        if not state_machine.is_tool_allowed(canonical_tool):
            # Tool not allowed in current phase
            return self._build_phase_block_response(
                canonical_tool=canonical_tool,
                current_phase=current_phase,
                state_machine=state_machine
            )
        
        # Apply validation rules via rule engine
        if engine:
            context = ActionContext(
                state_machine=state_machine,
                tool_normalizer=None,
                hook_name="PreToolUse",
                payload=payload,
                trace_id=os.environ.get("GOVERNOR_TRACE_ID", "")
            )
            results = engine.evaluate_rules("PreToolUse", payload, context)
            for result in results:
                if result.decision == "deny":
                    return self._build_response(
                        internal_decision="deny",
                        reason=result.reason,
                        additional_context=result.additional_context
                    )
        
        # Infer phase from tool usage patterns
        self._infer_phase_from_tool(canonical_tool, tool_input, state_machine)
        
        # Allow tool execution
        return self._build_allow_response(
            reason=f"Tool {canonical_tool} allowed in phase {current_phase}"
        )
    
    def _build_phase_block_response(self, canonical_tool: str, current_phase: str,
                                   state_machine: Any) -> Dict[str, Any]:
        """
        Build a block response for phase violations.
        
        This method generates a bypass key and provides a menu option
        for the user to bypass the block if needed.
        
        Args:
            canonical_tool: Canonical tool name
            current_phase: Current phase
            state_machine: State machine instance
            
        Returns:
            Protocol-compliant block response with bypass menu
        """
        # Generate bypass key with UUID4 per spec §3.6
        bypass_key = f"phase_enforcement:{canonical_tool}:{uuid.uuid4()}"
        
        # Build bypass menu
        # Note: The bypass key is presented to the user in the menu.
        # When the user selects "Bypass and Execute", UserPromptSubmit will
        # parse the menu response and register the bypass in the registry.
        bypass_menu = {
            "title": f"Tool Not Allowed in {current_phase} Phase",
            "message": f"The tool '{canonical_tool}' is not allowed in the {current_phase} phase.",
            "options": [
                {
                    "label": "Bypass and Execute",
                    "action": "bypass",
                    "bypass_key": bypass_key,
                    "expires": "once"
                },
                {
                    "label": "Cancel",
                    "action": "cancel"
                }
            ]
        }
        
        # Build additional context
        additional_context = f"""
=== PHASE VIOLATION ===
Tool: {canonical_tool}
Current Phase: {current_phase}
Allowed Tools in {current_phase}: {self._get_allowed_tools(current_phase)}

Phase Requirements:
- INIT: Read-only for context gathering
- RESEARCH: Information gathering and analysis
- PLAN: Strategy and task planning
- EXECUTE: Implementation and execution
- VALIDATE: Testing and verification
- COMMIT: Final review and commitment

To proceed, you must either:
1. Transition to an appropriate phase
2. Use the bypass option (requires explicit approval)
=== END VIOLATION ===
"""
        
        return self._build_response(
            internal_decision="deny",
            reason=f"Tool {canonical_tool} not allowed in phase {current_phase}",
            additional_context=additional_context,
            bypass_menu=bypass_menu
        )
    
    def _infer_phase_from_tool(self, canonical_tool: str, tool_input: Dict[str, Any],
                             state_machine: Any) -> None:
        """
        Infer phase from tool usage patterns.
        
        This method automatically infers the appropriate phase based on
        the tool being used and its input patterns.
        
        Args:
            canonical_tool: Canonical tool name
            tool_input: Tool input parameters
            state_machine: State machine instance
        """
        current_phase = state_machine.get_phase()
        
        # Phase inference rules
        phase_transitions = {
            "INIT": ["RESEARCH"],
            "RESEARCH": ["PLAN"],
            "PLAN": ["EXECUTE"],
            "EXECUTE": ["VALIDATE"],
            "VALIDATE": ["COMMIT"],
            "COMMIT": []  # Terminal phase
        }
        
        # Tool-based phase inference
        if canonical_tool == "exec" and current_phase == "PLAN":
            # Exec in PLAN phase suggests transition to EXECUTE
            state_machine.set_phase("EXECUTE")
        elif canonical_tool in ["file_write", "file_edit"] and current_phase == "VALIDATE":
            # File modifications in VALIDATE might need re-execution
            state_machine.set_phase("EXECUTE")
    
    def _get_allowed_tools(self, phase: str) -> str:
        """
        Get allowed tools for a phase as a string.
        
        Args:
            phase: Phase name
            
        Returns:
            Comma-separated list of allowed tools
        """
        try:
            from ..state_machine import PHASE_ALLOWLIST
        except ImportError:
            from state_machine import PHASE_ALLOWLIST
        allowed = PHASE_ALLOWLIST.get(phase, [])
        return ", ".join(allowed) if allowed else "None"
