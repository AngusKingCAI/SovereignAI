"""
Validate Governance Framework Action - Comprehensive validation for Governor integrity
Layer 4: Action. Imports _base.py ONLY.
"""

import os
import yaml
from typing import Dict, Any, List
from ._base import RuleAction, ActionResult, ActionContext

class ValidateGovernanceAction(RuleAction):
    """Action to validate Governor framework integrity and rule structure."""
    
    @property
    def name(self) -> str:
        return "validate_governance"
    
    def get_required_params(self) -> List[str]:
        return []
    
    def evaluate(self, payload: Dict[str, Any], params: Dict[str, Any],
                 context: ActionContext) -> ActionResult:
        """Evaluate the governance validation action."""
        scope = params.get("scope", "session_start")
        
        # Get Governor package root
        governor_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        validation_results = {
            "scope": scope,
            "checks": []
        }
        
        # Log action evaluation
        from ._base import log_execution
        log_execution("validate_governance_action", {
            "scope": scope,
            "governor_root": governor_root
        })
        
        # Perform validation based on scope
        if scope == "session_start":
            self._validate_framework_integrity(governor_root, validation_results)
        elif scope == "rule_validation":
            self._validate_rule_structure(governor_root, validation_results)
        
        # Check if all validations passed
        all_passed = all(check.get("passed", False) for check in validation_results["checks"])
        
        log_execution("validate_governance_action", {
            "validation_results": validation_results,
            "all_passed": all_passed
        })
        
        if all_passed:
            return ActionResult(
                decision="allow",
                reason="Governance framework validation passed",
                additional_context=f"\n=== GOVERNANCE VALIDATION PASSED ===\nAll {len(validation_results['checks'])} checks passed successfully."
            )
        else:
            failed_checks = [check for check in validation_results["checks"] if not check.get("passed", False)]
            return ActionResult(
                decision="allow",  # Non-blocking for now
                reason=f"Governance validation failed: {len(failed_checks)} checks failed",
                additional_context=f"\n=== GOVERNANCE VALIDATION FAILED ===\nFailed checks:\n" + "\n".join(
                    f"- {check['name']}: {check['error']}" for check in failed_checks
                )
            )
    
    def _validate_framework_integrity(self, governor_root: str, results: Dict[str, Any]):
        """Validate basic Governor framework integrity."""
        checks = results["checks"]
        
        # Check 1: Actions directory exists
        actions_dir = os.path.join(governor_root, "actions")
        actions_exist = os.path.isdir(actions_dir)
        checks.append({
            "name": "actions_directory_exists",
            "passed": actions_exist,
            "error": "Actions directory not found" if not actions_exist else None
        })
        
        # Check 2: Rules directory exists
        rules_dir = os.path.join(governor_root, "rules")
        rules_exist = os.path.isdir(rules_dir)
        checks.append({
            "name": "rules_directory_exists", 
            "passed": rules_exist,
            "error": "Rules directory not found" if not rules_exist else None
        })
        
        # Check 3: Hook handlers directory exists
        hook_handlers_dir = os.path.join(governor_root, "hook_handlers")
        hook_handlers_exist = os.path.isdir(hook_handlers_dir)
        checks.append({
            "name": "hook_handlers_directory_exists",
            "passed": hook_handlers_exist,
            "error": "Hook handlers directory not found" if not hook_handlers_exist else None
        })
        
        # Check 4: Required core files exist
        required_files = [
            "governor.py",
            "engine.py", 
            "state_machine.py",
            "protocol.py"
        ]
        for file_name in required_files:
            file_path = os.path.join(governor_root, file_name)
            file_exists = os.path.isfile(file_path)
            checks.append({
                "name": f"core_file_{file_name}",
                "passed": file_exists,
                "error": f"Core file {file_name} not found" if not file_exists else None
            })
    
    def _validate_rule_structure(self, governor_root: str, results: Dict[str, Any]):
        """Validate rule YAML files against expected structure."""
        checks = results["checks"]
        
        rules_dir = os.path.join(governor_root, "rules")
        if not os.path.isdir(rules_dir):
            checks.append({
                "name": "rules_directory_for_validation",
                "passed": False,
                "error": "Rules directory not found"
            })
            return
        
        # Load and validate all YAML rule files
        import glob
        rule_files = glob.glob(os.path.join(rules_dir, "*.yaml"))
        
        # Track rule IDs for uniqueness check (separate by scope)
        universal_rule_ids = []
        agent_rule_ids = {}  # agent -> list of rule IDs
        
        for rule_file in rule_files:
            try:
                with open(rule_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
                
                # Check required fields
                required_fields = ["id", "version", "tier", "trigger", "action"]
                missing_fields = [field for field in required_fields if field not in rule_data]
                
                if missing_fields:
                    checks.append({
                        "name": f"rule_structure_{os.path.basename(rule_file)}",
                        "passed": False,
                        "error": f"Missing required fields: {missing_fields}"
                    })
                    continue
                
                # Check rule ID uniqueness (separate by scope)
                rule_id = rule_data.get("id")
                rule_agent = rule_data.get("agent")
                
                if rule_agent:
                    # Agent-specific rule
                    if rule_agent not in agent_rule_ids:
                        agent_rule_ids[rule_agent] = []
                    if rule_id in agent_rule_ids[rule_agent]:
                        checks.append({
                            "name": f"rule_id_uniqueness_{rule_agent}_{rule_id}",
                            "passed": False,
                            "error": f"Duplicate rule ID for agent {rule_agent}: {rule_id}"
                        })
                    else:
                        agent_rule_ids[rule_agent].append(rule_id)
                else:
                    # Universal rule
                    if rule_id in universal_rule_ids:
                        checks.append({
                            "name": f"rule_id_uniqueness_{rule_id}",
                            "passed": False,
                            "error": f"Duplicate universal rule ID: {rule_id}"
                        })
                    else:
                        universal_rule_ids.append(rule_id)
                
                # Validate trigger structure
                trigger = rule_data.get("trigger", {})
                if not isinstance(trigger, dict) or "hook" not in trigger:
                    checks.append({
                        "name": f"rule_trigger_{rule_id}",
                        "passed": False,
                        "error": f"Invalid trigger structure for rule {rule_id}"
                    })
                    continue
                
                checks.append({
                    "name": f"rule_validation_{rule_id}",
                    "passed": True,
                    "error": None
                })
                
            except yaml.YAMLError as e:
                checks.append({
                    "name": f"rule_yaml_parse_{os.path.basename(rule_file)}",
                    "passed": False,
                    "error": f"YAML parsing error: {str(e)}"
                })
            except Exception as e:
                checks.append({
                    "name": f"rule_load_{os.path.basename(rule_file)}",
                    "passed": False,
                    "error": f"Error loading rule: {str(e)}"
                })
