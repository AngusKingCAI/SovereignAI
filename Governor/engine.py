"""
Engine - Load rules, match triggers, execute actions
Layer 3: Self-contained. Imports actions/_base.py ONLY.
"""

import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime

# Get Governor package root
GOVERNOR_ROOT = os.path.dirname(os.path.abspath(__file__))


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(GOVERNOR_ROOT, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = datetime.utcnow().strftime("%m-%d-%Y")
        log_file = os.path.join(log_dir, f"Governor-Log-{today}.jsonl")
        
        entry = {
            "File": "engine.py",
            "hook": component,
            "Time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            
    except Exception as e:
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()


# Import action base classes
try:
    from .actions._base import RuleAction, ActionResult, ActionContext
except ImportError:
    from actions._base import RuleAction, ActionResult, ActionContext

# Import actions registry
try:
    from .actions import _ACTIONS
except ImportError:
    from actions import _ACTIONS


# Rule directory
RULES_DIR = os.path.join(GOVERNOR_ROOT, "rules")


class Engine:
    """Rule engine for Governor."""
    
    def __init__(self):
        """Initialize engine."""
        self.rules: List[Dict[str, Any]] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load rule YAML files."""
        if not os.path.exists(RULES_DIR):
            log_execution("Engine", {"action": "load_rules", "status": "no_rules_dir"})
            return
        
        try:
            import yaml
        except ImportError:
            print("Warning: yaml not installed, rules not loaded", file=sys.stderr)
            log_execution("Engine", {"action": "load_rules", "status": "yaml_missing"})
            return
        
        for filename in os.listdir(RULES_DIR):
            if not filename.endswith('.yaml') and not filename.endswith('.yml'):
                continue
            
            filepath = os.path.join(RULES_DIR, filename)
            try:
                with open(filepath, 'r') as f:
                    rule_data = yaml.safe_load(f)
                    if rule_data:
                        self.rules.append(rule_data)
                        log_execution("Engine", {"action": "rule_loaded", "file": filename, "rule_id": rule_data.get("id", "unknown")})
            except Exception as e:
                print(f"Warning: Failed to load rule {filename}: {e}", file=sys.stderr)
                log_execution("Engine", {"action": "rule_load_failed", "file": filename, "error": str(e)})
        
        log_execution("Engine", {"action": "load_rules_complete", "total_rules": len(self.rules)})
    
    def evaluate_rules(self, hook_name: str, payload: Dict[str, Any], 
                      context: ActionContext) -> List[ActionResult]:
        """Evaluate rules for hook event."""
        results = []
        
        for rule in self.rules:
            if self._matches_trigger(rule, hook_name, payload):
                result = self._execute_rule(rule, payload, context)
                if result:
                    results.append(result)
        
        return results
    
    def _matches_trigger(self, rule: Dict[str, Any], hook_name: str, 
                        payload: Dict[str, Any]) -> bool:
        """Check if rule trigger matches."""
        trigger = rule.get("trigger", {})
        
        # Check hook name
        if trigger.get("hook") != hook_name:
            return False
        
        # Check tool name if specified
        if "tool" in trigger:
            tool_name = payload.get("tool_name", "")
            if trigger["tool"] != tool_name:
                return False
        
        # Check file path condition if specified in rule
        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
        
        # Check if rule has condition for file path
        check = rule.get("check", {})
        if check:
            condition = check.get("condition", {})
            field = condition.get("field", "")
            operator = condition.get("operator", "")
            pattern = condition.get("pattern", "")
            
            if field == "tool_input" and operator == "equals" and pattern:
                # More precise matching - check if filename matches exactly
                import os
                filename = os.path.basename(file_path)
                if filename != pattern:
                    return False
        
        return True
    
    def _execute_rule(self, rule: Dict[str, Any], payload: Dict[str, Any],
                     context: ActionContext) -> ActionResult:
        """Execute rule action."""
        action_name = rule.get("action", "block_command")
        action_params = rule.get("params", {})
        
        log_execution("Engine", {
            "action": "execute_rule",
            "rule": rule.get("id", "unknown"),
            "action_name": action_name
        })
        
        # Get action instance
        action = _ACTIONS.get(action_name)
        if not action:
            return ActionResult(
                decision="allow",
                reason=f"Action not found: {action_name}"
            )
        
        # Execute action
        try:
            return action.evaluate(payload, action_params, context)
        except Exception as e:
            return ActionResult(
                decision="allow",
                reason=f"Action execution error: {e}"
            )
