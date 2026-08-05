"""
Stop Hook Handler for Governor.py v1.5

This handler processes the Stop hook event, which is triggered when
the agent requests to stop the session. It is the final gate that checks
completion requirements before allowing the session to end.

Key Responsibilities:
- Phase completion checking
- Un-bypassed violation checking
- Minimum tool usage checking
- Bypass validation
- Block with menu option if requirements not met
- Protocol-compliant response

This implements the Stop handler specified in v1.5 spec §4.3.
"""

from typing import Dict, Any, List

# Import base class (package-relative)
try:
    from ._base import HookHandler
except ImportError:
    from hook_handlers._base import HookHandler


class StopHandler(HookHandler):
    """
    Handler for Stop hook events.
    
    Stop is triggered when the agent requests to stop the session.
    This handler is the final gate that checks completion requirements
    before allowing the session to end.
    """
    
    @property
    def hook_name(self) -> str:
        """Return the hook name this handler processes."""
        return "Stop"
    
    @property
    def can_block(self) -> bool:
        """
        Indicate if this handler can block operations.
        
        Stop can block the session from ending if requirements are not met.
        """
        return True
    
    def execute(self, payload: Dict[str, Any], state_machine: Any, 
               engine: Any) -> Dict[str, Any]:
        """
        Execute the Stop handler logic.
        
        This method:
        1. Checks phase completion requirements
        2. Checks for un-bypassed violations
        3. Validates minimum tool usage
        4. Validates bypass entries
        5. Blocks with menu option if requirements not met
        6. Returns protocol-compliant response
        
        Args:
            payload: Stop hook event payload
            state_machine: Governor state machine instance
            engine: Rule engine instance (not used in Stop)
            
        Returns:
            Protocol-compliant allow/deny response
        """
        # Get current phase
        current_phase = state_machine.get_phase()
        
        # Check completion requirements
        completion_check = self._check_completion_requirements(state_machine)
        
        # Check for un-bypassed violations
        violation_check = self._check_violations(state_machine)
        
        # Check minimum tool usage
        usage_check = self._check_minimum_usage(state_machine)
        
        # Validate bypass entries
        bypass_check = self._validate_bypasses(state_machine)
        
        # Aggregate all checks
        all_checks = {
            "completion": completion_check,
            "violations": violation_check,
            "usage": usage_check,
            "bypasses": bypass_check
        }
        
        # Determine if session can stop
        can_stop = all(check["passed"] for check in all_checks.values())
        
        if can_stop:
            # All requirements met, allow stop
            return self._build_allow_response(
                reason=f"Session stop approved. Phase: {current_phase}, All requirements met."
            )
        else:
            # Requirements not met, block with menu
            return self._build_block_response(
                current_phase=current_phase,
                checks=all_checks,
                state_machine=state_machine
            )
    
    def _check_completion_requirements(self, state_machine: Any) -> Dict[str, Any]:
        """
        Check phase completion requirements.
        
        Args:
            state_machine: State machine instance
            
        Returns:
            Check result dict with 'passed' boolean and 'message' string
        """
        current_phase = state_machine.get_phase()
        
        # Phase-specific completion requirements
        phase_requirements = {
            "INIT": True,  # INIT has no specific requirements
            "RESEARCH": True,  # RESEARCH has no specific requirements
            "PLAN": True,  # PLAN has no specific requirements
            "EXECUTE": state_machine.get_counter("exec") > 0,  # EXECUTE requires at least 1 exec
            "VALIDATE": state_machine.get_counter("exec") > 0,  # VALIDATE requires at least 1 exec
            "COMMIT": True  # COMMIT has no specific requirements
        }
        
        passed = phase_requirements.get(current_phase, True)
        message = f"Phase {current_phase} completion: {'Passed' if passed else 'Failed - requires at least 1 execution'}"
        
        return {"passed": passed, "message": message}
    
    def _check_violations(self, state_machine: Any) -> Dict[str, Any]:
        """
        Check for un-bypassed violations.
        
        Args:
            state_machine: State machine instance
            
        Returns:
            Check result dict with 'passed' boolean and 'message' string
        """
        violations = state_machine.get_violations()
        
        # Filter for actual violations (not execution logs)
        actual_violations = [v for v in violations if v.get("type") != "execution"]
        
        passed = len(actual_violations) == 0
        message = f"Violations: {len(actual_violations)} un-bypassed violations found"
        
        return {"passed": passed, "message": message, "count": len(actual_violations)}
    
    def _check_minimum_usage(self, state_machine: Any) -> Dict[str, Any]:
        """
        Check minimum tool usage requirements.
        
        Args:
            state_machine: State machine instance
            
        Returns:
            Check result dict with 'passed' boolean and 'message' string
        """
        exec_count = state_machine.get_counter("exec")
        
        # Minimum requirement: at least 1 execution in non-INIT phases
        current_phase = state_machine.get_phase()
        if current_phase == "INIT":
            passed = True
            message = "Minimum usage: N/A (INIT phase)"
        else:
            passed = exec_count >= 1
            message = f"Minimum usage: {exec_count} executions (minimum: 1)"
        
        return {"passed": passed, "message": message, "count": exec_count}
    
    def _validate_bypasses(self, state_machine: Any) -> Dict[str, Any]:
        """
        Validate bypass entries for appropriateness.
        
        Args:
            state_machine: State machine instance
            
        Returns:
            Check result dict with 'passed' boolean and 'message' string
        """
        # Count bypass entries
        total_bypasses = 0
        for scope in ["runtime", "team", "once", "session"]:
            total_bypasses += len(state_machine.state["bypasses"][scope])
        
        # Validation: excessive bypasses may indicate compliance issues
        passed = total_bypasses < 10  # Arbitrary threshold
        message = f"Bypass validation: {total_bypasses} bypass entries"
        
        return {"passed": passed, "message": message, "count": total_bypasses}
    
    def _build_block_response(self, current_phase: str, checks: Dict[str, Any],
                             state_machine: Any) -> Dict[str, Any]:
        """
        Build a block response with menu options.
        
        Args:
            current_phase: Current phase
            checks: Dictionary of all check results
            state_machine: State machine instance
            
        Returns:
            Protocol-compliant block response with menu
        """
        # Build failure messages
        failure_messages = []
        for check_name, check_result in checks.items():
            if not check_result["passed"]:
                failure_messages.append(f"  - {check_result['message']}")
        
        # Build bypass menu
        bypass_menu = {
            "title": "Session Stop Blocked - Requirements Not Met",
            "message": f"Cannot stop session in {current_phase} phase. Requirements not met:",
            "options": [
                {
                    "label": "Force Stop (Acknowledge Violations)",
                    "action": "force_stop",
                    "warning": "This will acknowledge all violations and allow stop"
                },
                {
                    "label": "Continue Session",
                    "action": "continue"
                }
            ]
        }
        
        # Build additional context
        additional_context = f"""
=== STOP REQUIREMENTS CHECK ===
Phase: {current_phase}

Failed Requirements:
{chr(10).join(failure_messages)}

To proceed, you must either:
1. Address the failed requirements
2. Use the Force Stop option (acknowledges violations)
=== END REQUIREMENTS ===
"""
        
        return self._build_response(
            internal_decision="deny",
            reason=f"Session stop blocked in {current_phase} phase",
            additional_context=additional_context,
            bypass_menu=bypass_menu
        )
