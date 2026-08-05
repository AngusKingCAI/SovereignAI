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

# Import action base classes (package-relative for module execution)
try:
    from .actions._base import RuleAction, ActionResult, ActionContext
except ImportError:
    # Fallback for direct execution during development
    from actions._base import RuleAction, ActionResult, ActionContext

# YAML import with stdlib fallback
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

# Rule directory
RULES_DIR = "Governor/rules"

# Priority levels (spec uses "tier" but we keep priority for compatibility)
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
    Parsed rule definition (aligned with v1.5 spec §3.2).
    
    Attributes:
        id: Unique rule identifier
        version: Rule version (semver)
        tier: Priority level (blocking/warning/observational)
        agent: Agent identifier for filtering
        domain: Domain identifier
        name: Human-readable rule name
        description: Rule description
        triggers: List of trigger conditions (hook names)
        check: Rule check configuration with params
        enabled: Whether rule is enabled
        aliases: Alternative rule names
        metadata: Additional rule metadata
    """
    id: str
    version: str = "1.0.0"
    tier: str = "observational"  # Spec uses "tier" instead of "priority"
    agent: Optional[str] = None
    domain: Optional[str] = None
    name: str = ""
    description: str = ""
    triggers: List[str] = None  # Spec says list of strings (hook names)
    check: Optional[Dict[str, Any]] = None  # Spec nests actions under check.params
    enabled: bool = True
    aliases: List[str] = None
    metadata: Dict[str, Any] = None
    
    # Backward compatibility: map priority to tier
    @property
    def priority(self) -> str:
        """Backward compatibility property for priority."""
        return self.tier
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.triggers is None:
            self.triggers = []
        if self.aliases is None:
            self.aliases = []
        if self.check is None:
            self.check = {}


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
            
            # Create Rule object (aligned with spec §3.2)
            rule = Rule(
                id=rule_data.get("id", rule_file.stem),
                version=rule_data.get("version", "1.0.0"),
                tier=rule_data.get("tier", rule_data.get("priority", "observational")),  # Backward compat
                agent=rule_data.get("agent"),
                domain=rule_data.get("domain"),
                name=rule_data.get("name", rule_file.stem),
                description=rule_data.get("description", ""),
                triggers=rule_data.get("triggers", []),
                check=rule_data.get("check", {}),
                enabled=rule_data.get("enabled", True),
                aliases=rule_data.get("aliases", []),
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


def match_trigger(trigger: str, hook_name: str, payload: Dict[str, Any]) -> bool:
    """
    Check if a trigger matches the current hook event.
    
    Spec §3.2: triggers are list of hook names (strings), not dicts.
    
    Args:
        trigger: Hook name string from rule triggers list
        hook_name: Current hook name
        payload: Hook event payload
        
    Returns:
        True if trigger matches, False otherwise
    """
    # Spec §3.2: triggers are simple hook name strings
    return trigger == hook_name


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
    
    # Execute actions (actions are nested under check.params per spec §3.2)
    for rule in matched_rules:
        # Get actions from check.params.actions
        actions_config = rule.check.get("params", {}).get("actions", []) if rule.check else []
        
        for action_config in actions_config:
            try:
                result = _execute_action(action_config, payload, context)
                results.append(result)
                
                # Short-circuit on blocking deny
                if rule.tier == "blocking" and result.decision == "deny":
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
    action_name = action_config.get("name")  # Spec §3.2 uses "name" key
    # Spec §3.2: action params are at top level of action config, not nested under params
    params = {k: v for k, v in action_config.items() if k != "name"}
    
    # Import action class
    try:
        # Actions are in Governor/actions/ directory (package-relative import)
        if __package__:
            action_module = importlib.import_module(f".actions.{action_name}", package=__package__)
        else:
            # Fallback for direct execution during development
            action_module = importlib.import_module(f"actions.{action_name}")
        # Convert snake_case to PascalCase and append "Action" suffix per spec §6.3
        action_class_name = "".join(word.capitalize() for word in action_name.split("_")) + "Action"
        action_class = getattr(action_module, action_class_name)
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
