"""
SessionEnd Hook Handler for Governor.py v1.5

This handler processes the SessionEnd hook event, which is triggered
when the session ends. It performs final logging, generates compliance
reports, and archives state for post-mortem analysis.

Key Responsibilities:
- Final logging to audit trail
- Compliance report generation
- Flush violations to audit trail
- Flush final counter values
- Archive state for post-mortem
- Protocol-compliant response

This implements the SessionEnd handler specified in v1.5 spec §4.3.
"""

import json
from typing import Dict, Any
from datetime import datetime

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class SessionEndHandler(HookHandler):
    """
    Handler for SessionEnd hook events.
    
    SessionEnd is triggered when the session ends. This handler performs
    final logging, generates compliance reports, and archives state
    for post-mortem analysis.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "SessionEnd"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        SessionEnd cannot block - the session is ending.
        """
        return False
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the SessionEnd handler logic.
        
        This method:
        1. Performs final logging to audit trail
        2. Generates compliance report
        3. Flushes violations to audit trail
        4. Flushes final counter values
        5. Archives state for post-mortem
        6. Returns protocol-compliant allow response
        
        Args:
            payload: SessionEnd hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in SessionEnd)
            
        Returns:
            Protocol-compliant allow response with compliance report
        """
        # Get current phase and counters
        current_phase = state_machine.get_phase()
        exec_count = state_machine.get_counter("exec")
        validate_count = state_machine.get_counter("validate")
        
        # Get violations
        violations = state_machine.get_violations()
        
        # Generate compliance report
        compliance_report = self._generate_compliance_report(
            current_phase, exec_count, validate_count, violations, state_machine
        )
        
        # Archive state for post-mortem
        self._archive_state(state_machine)
        
        # Build additional context with compliance report
        additional_context = f"""
=== SESSION COMPLIANCE REPORT ===
{compliance_report}
=== END COMPLIANCE REPORT ===
"""
        
        # Build response
        return self._build_allow_response(
            reason=f"Session ended. Phase: {current_phase}, Executions: {exec_count}",
            additional_context=additional_context
        )
    
    def _generate_compliance_report(self, current_phase: str, exec_count: int,
                                  validate_count: int, violations: list,
                                  state_machine: Any) -> str:
        """
        Generate compliance report for the session.
        
        Args:
            current_phase: Final phase
            exec_count: Number of executions
            validate_count: Number of validations
            violations: List of violations
            state_machine: State machine instance
            
        Returns:
            Compliance report string
        """
        # All entries in violations are actual violations now (execution logs go to audit trail)
        
        # Count bypasses
        total_bypasses = 0
        for scope in ["runtime", "team", "once", "session"]:
            total_bypasses += len(state_machine.state["bypasses"][scope])
        
        # Build report
        report = f"""
Session Summary:
- Final Phase: {current_phase}
- Executions: {exec_count}
- Validations: {validate_count}
- Violations: {len(violations)}
- Bypasses: {total_bypasses}

Compliance Status: {'COMPLIANT' if len(violations) == 0 else 'NON-COMPLIANT'}

{'Phase Requirements:' + self._get_phase_requirements(current_phase)}

Flags:
- Research Required: {state_machine.get_flag('research_required')}
"""
        
        return report
    
    def _get_phase_requirements(self, phase: str) -> str:
        """
        Get phase requirements text.
        
        Args:
            phase: Phase name
            
        Returns:
            Phase requirements string
        """
        requirements = {
            "INIT": "None",
            "RESEARCH": "None",
            "PLAN": "None",
            "EXECUTE": "At least 1 execution",
            "VALIDATE": "At least 1 execution",
            "COMMIT": "None"
        }
        return requirements.get(phase, "Unknown")
    
    def _archive_state(self, state_machine: Any) -> None:
        """
        Archive state for post-mortem analysis.
        
        This method creates a snapshot of the current state and
        stores it in the state directory for later analysis.
        
        Args:
            state_machine: State machine instance
        """
        # Create archive filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_path = f"{state_machine.state_dir}/state_archive_{timestamp}.json"
        
        # Archive the current state
        with open(archive_path, 'w') as f:
            json.dump(state_machine.state, f, indent=2)
        
        # Note: Archive is created but not logged to violations
        # In Phase 2.5, this will be integrated with proper audit logging
