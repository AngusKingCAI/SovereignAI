"""
Rule Engine for Governor.py v1.5

This module implements the rule engine that loads, evaluates, and executes
Governor rules. It handles rule scanning, caching, trigger matching, priority
sorting, and action execution.

Key Functions:
- load_rules(): Scan and load rule YAML files
- evaluate_rules(): Match rules to payload and execute actions
- Rule caching with mtime-based invalidation
- Priority sorting (blocking → warning → observational)

This implements the rule engine specified in v1.5 spec §4.1.
"""

import os
import importlib
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

# Import action base classes
try:
    from actions._base import RuleAction, ActionResult, ActionContext
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from actions._base import RuleAction, ActionResult, ActionContext

# YAML import with stdlib fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Rule directory
RULES_DIR = "Governor/rules"

# Priority levels
PRIORITY_LEVELS = {
    "blocking": 0,
    "warning": 1,
    "observational": 2
}

# Rule cache
_rule_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}


@dataclass
class Rule:
    """
    Parsed rule definition.
    
    Attributes:
        id: Unique rule identifier
        name: Human-readable rule name
        description: Rule description
        priority: Priority level (blocking/warning/observational)
        triggers: List of trigger conditions
        actions: List of action configurations
        enabled: Whether rule is enabled
        metadata: Additional rule metadata
    """
    id: str
    name: str
    description: str
    priority: str
    triggers: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


def load_rules(force_reload: bool = False) -> List[Rule]:
    """
    Load all rules from the rules directory.
    
    This function scans the rules directory for YAML files, parses them,
    and caches the results. Caching is based on file modification times.
    
    Args:
        force_reload: Force reload even if cache is valid
        
    Returns:
        List of Rule objects
    """
    global _rule_cache, _cache_timestamps
    
    rules = []
    
    if not os.path.exists(RULES_DIR):
        return rules
    
    # Scan for YAML files
    for rule_file in Path(RULES_DIR).glob("*.yaml"):
        try:
            # Check cache
            mtime = os.path.getmtime(rule_file)
            if not force_reload and rule_file in _cache_timestamps:
                if mtime <= _cache_timestamps[rule_file]:
                    rules.append(_rule_cache[str(rule_file)])
                    continue
            
            # Load and parse YAML
            if HAS_YAML:
                with open(rule_file, 'r') as f:
                    rule_data = yaml.safe_load(f)
            else:
                # Fallback: simple key-value parsing (limited functionality)
                with open(rule_file, 'r') as f:
                    rule_data = _parse_simple_yaml(f)
            
            # Create Rule object
            rule = Rule(
                id=rule_data.get("id", rule_file.stem),
                name=rule_data.get("name", rule_file.stem),
                description=rule_data.get("description", ""),
                priority=rule_data.get("priority", "observational"),
                triggers=rule_data.get("triggers", []),
                actions=rule_data.get("actions", []),
                enabled=rule_data.get("enabled", True),
                metadata=rule_data.get("metadata", {})
            )
            
            # Cache the rule
            _rule_cache[str(rule_file)] = rule
            _cache_timestamps[str(rule_file)] = mtime
            rules.append(rule)
            
        except Exception as e:
            # Log error but continue loading other rules
            print(f"Error loading rule {rule_file}: {e}")
    
    # Sort by priority
    rules.sort(key=lambda r: PRIORITY_LEVELS.get(r.priority, 999))
    
    return rules


def _parse_simple_yaml(file_handle) -> Dict[str, Any]:
    """
    Simple YAML parser fallback for when PyYAML is not available.
    
    This is a very limited parser that only handles basic key-value pairs.
    For full YAML support, install PyYAML.
    
    Args:
        file_handle: File handle to read from
        
    Returns:
        Parsed dictionary
    """
    result = {}
    current_key = None
    current_list = None
    
    for line in file_handle:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            if value == '':
                # Start of nested structure
                current_key = key
                if key in result:
                    if isinstance(result[key], list):
                        current_list = result[key]
                    else:
                        result[key] = [result[key]]
                        current_list = result[key]
                else:
                    result[key] = []
                    current_list = result[key]
            else:
                # Simple key-value
                result[key] = value
        elif current_list is not None:
            # List item
            current_list.append(line.lstrip('- '))
    
    return result


def match_trigger(trigger: Dict[str, Any], hook_name: str, payload: Dict[str, Any]) -> bool:
    """
    Check if a trigger matches the current hook event.
    
    Args:
        trigger: Trigger condition from rule
        hook_name: Current hook name
        payload: Hook event payload
        
    Returns:
        True if trigger matches, False otherwise
    """
    # Check hook name match
    if "hook" in trigger:
        if trigger["hook"] != hook_name:
            return False
    
    # Check tool name match (for PreToolUse/PostToolUse)
    if "tool" in trigger:
        if "tool" not in payload:
            return False
        if trigger["tool"] != payload["tool"]:
            return False
    
    # Check phase match
    if "phase" in trigger:
        # TODO: Integrate with state machine for phase check
        pass
    
    # Check custom conditions
    if "condition" in trigger:
        # TODO: Implement custom condition evaluation
        pass
    
    return True


def evaluate_rules(hook_name: str, payload: Dict[str, Any], context: ActionContext) -> List[ActionResult]:
    """
    Evaluate all rules against the current hook event.
    
    This function:
    1. Loads all rules (with caching)
    2. Matches triggers to the current event
    3. Sorts matched rules by priority
    4. Executes actions sequentially
    5. Aggregates results
    
    Args:
        hook_name: Current hook name
        payload: Hook event payload
        context: ActionContext for action execution
        
    Returns:
        List of ActionResult objects from executed actions
    """
    results = []
    
    # Load rules
    rules = load_rules()
    
    # Match triggers
    matched_rules = []
    for rule in rules:
        if not rule.enabled:
            continue
        
        for trigger in rule.triggers:
            if match_trigger(trigger, hook_name, payload):
                matched_rules.append(rule)
                break  # Only need one trigger to match
    
    # Sort by priority (already sorted by load_rules, but ensure)
    matched_rules.sort(key=lambda r: PRIORITY_LEVELS.get(r.priority, 999))
    
    # Execute actions
    for rule in matched_rules:
        for action_config in rule.actions:
            try:
                result = _execute_action(action_config, payload, context)
                results.append(result)
                
                # Short-circuit on blocking deny
                if rule.priority == "blocking" and result.decision == "deny":
                    break
                    
            except Exception as e:
                # Fail-graceful: log error but continue
                print(f"Error executing action in rule {rule.id}: {e}")
                # Add error result
                results.append(ActionResult(
                    decision="allow",  # Fail-open
                    reason=f"Action execution error: {e}"
                ))
    
    return results


def _execute_action(action_config: Dict[str, Any], payload: Dict[str, Any], 
                   context: ActionContext) -> ActionResult:
    """
    Execute a single action.
    
    Args:
        action_config: Action configuration from rule YAML
        payload: Hook event payload
        context: ActionContext for execution
        
    Returns:
        ActionResult from action execution
    """
    action_name = action_config.get("action")
    params = action_config.get("params", {})
    
    # Import action class
    try:
        # Actions are in Governor/actions/ directory
        action_module = importlib.import_module(f"actions.{action_name}")
        action_class = getattr(action_module, action_name.capitalize())
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Could not load action {action_name}: {e}")
    
    # Instantiate action
    action = action_class()
    
    # Validate parameters
    action.validate_params(params)
    
    # Execute action
    return action.evaluate(payload, params, context)


def clear_rule_cache() -> None:
    """Clear the rule cache (useful for testing)."""
    global _rule_cache, _cache_timestamps
    _rule_cache.clear()
    _cache_timestamps.clear()


def get_rule_stats() -> Dict[str, Any]:
    """
    Get statistics about loaded rules.
    
    Returns:
        Dictionary with rule statistics
    """
    rules = load_rules()
    
    priority_counts = {"blocking": 0, "warning": 0, "observational": 0}
    enabled_count = 0
    
    for rule in rules:
        priority_counts[rule.priority] = priority_counts.get(rule.priority, 0) + 1
        if rule.enabled:
            enabled_count += 1
    
    return {
        "total_rules": len(rules),
        "enabled_rules": enabled_count,
        "priority_counts": priority_counts,
        "cache_size": len(_rule_cache)
    }
