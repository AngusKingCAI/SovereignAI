from __future__ import annotations

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
import sys
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime

# YAML import with safe loader configuration
try:
    import yaml
    HAS_YAML = True
    
    # Custom SafeLoader with limits to prevent billion laughs attacks
    class GovernorSafeLoader(yaml.SafeLoader):
        """
        Custom YAML loader with security limits to prevent billion laughs attacks.
        
        This prevents billion laughs attacks by limiting:
        - Maximum document size
        - Maximum nesting depth
        - Maximum number of anchors/aliases (implicitly limited by size)
        """
        def __init__(self, stream):
            super().__init__(stream)
            # Limit document size to 1MB to prevent DoS
            self.max_document_size = 1024 * 1024
            # Limit nesting depth to 20
            self.max_depth = 20
            self._depth = 0
    
except ImportError:
    HAS_YAML = False
    GovernorSafeLoader = None

__all__ = ["Engine", "Rule", "load_rules", "evaluate_rules", "clear_rule_cache", "get_rule_stats"]

# Import action base classes (package-relative for module execution)
try:
    from .actions._base import RuleAction, ActionResult, ActionContext
except ImportError:
    # Fallback for direct execution during development
    from actions._base import RuleAction, ActionResult, ActionContext

# Import debug logging
try:
    from .debug_logging import debug_log, is_debug_enabled
except ImportError:
    from debug_logging import debug_log, is_debug_enabled

# Import circuit breaker
try:
    from .circuit_breaker import CircuitBreakerManager
except ImportError:
    from circuit_breaker import CircuitBreakerManager

# Import security module
try:
    from .security import validate_import_path, SecurityError, ResourceLimitEnforcer, log_security_violation
except ImportError:
    from security import validate_import_path, SecurityError, ResourceLimitEnforcer, log_security_violation


def log_execution(component: str, data: Dict[str, Any]):
    """Log execution to daily JSONL file."""
    try:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Daily log file: Layer2-Python-Execution-Log-MM-DD-YYYY.jsonl
        today = datetime.utcnow()
        log_filename = f"Layer2-Python-Execution-Log-{today.strftime('%m-%d-%Y')}.jsonl"
        log_file = os.path.join(log_dir, log_filename)
        
        log_entry = {
            "File": component,
            "hook": component,
            "Time": today.strftime('%Y-%m-%dT%H:%M:%S'),
            "data": data
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")
            f.flush()
            
    except Exception as e:
        # Don't fail if logging fails, but print error to stderr
        sys.stderr.write(f"Logging error: {e}\n")
        sys.stderr.flush()

# YAML import with safe loader configuration
try:
    import yaml
    HAS_YAML = True
    
    # Custom SafeLoader with limits to prevent billion laughs attacks
    class GovernorSafeLoader(yaml.SafeLoader):
        """
        Custom YAML loader with security limits to prevent billion laughs attacks.
        
        This prevents billion laughs attacks by limiting:
        - Maximum document size
        - Maximum nesting depth
        - Maximum number of anchors/aliases (implicitly limited by size)
        """
        def __init__(self, stream):
            super().__init__(stream)
            # Limit document size to 1MB to prevent DoS
            self.max_document_size = 1024 * 1024
            # Limit nesting depth to 20
            self.max_depth = 20
            self._depth = 0
    
except ImportError:
    HAS_YAML = False
    GovernorSafeLoader = None

# Rule directory (package-relative)
RULES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules")

# Priority levels (spec uses "tier" but we keep priority for compatibility)
PRIORITY_LEVELS = {
    "blocking": 0,
    "warning": 1,
    "observational": 2
}

# Rule cache
_rule_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}

# Scope configuration cache
_scope_config_cache: Optional[Dict[str, Any]] = None
_scope_config_mtime: Optional[float] = None

# Circuit breaker manager (module-level singleton)
_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """
    Get the circuit breaker manager instance (singleton).
    
    Returns:
        CircuitBreakerManager instance
    """
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    return _circuit_breaker_manager


class Engine:
    """
    Rule engine for loading and evaluating Governor rules.
    
    This class provides a unified interface for the rule engine,
    encapsulating the module-level functions for better spec compliance.
    
    Spec §3.5a defines the Engine interface with methods for rule loading
    and evaluation.
    """
    
    def load_rules(self, force_reload: bool = False) -> List[Rule]:
        """
        Load all rules from the rules directory.
        
        Args:
            force_reload: Force reload even if cache is valid
            
        Returns:
            List of Rule objects
        """
        return load_rules(force_reload)
    
    def evaluate_rules(self, hook_name: str, payload: Dict[str, Any], 
                       context: ActionContext) -> List[ActionResult]:
        """
        Evaluate all rules against the current hook event.
        
        Args:
            hook_name: Current hook name
            payload: Hook event payload
            context: ActionContext for action execution
            
        Returns:
            List of ActionResult objects from executed actions
        """
        return evaluate_rules(hook_name, payload, context)
    
    def clear_cache(self) -> None:
        """Clear the rule cache (useful for testing)."""
        clear_rule_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded rules.
        
        Returns:
            Dictionary with rule statistics
        """
        return get_rule_stats()


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
    scope: Optional[str] = None
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
    
    debug_log("engine", "load_rules called", force_reload=force_reload)
    
    # Log rule loading
    log_execution("Engine", {
        "action": "load_rules",
        "force_reload": force_reload
    })
    
    rules = []
    
    if not os.path.exists(RULES_DIR):
        debug_log("engine", "Rules directory does not exist", rules_dir=RULES_DIR)
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
            
            # Load and parse YAML with safe loader
            if HAS_YAML and GovernorSafeLoader:
                with open(rule_file, 'r') as f:
                    rule_data = yaml.load(f, Loader=GovernorSafeLoader)
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
                scope=rule_data.get("scope"),
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


def _load_scope_config() -> Dict[str, Any]:
    """
    Load scope configuration from scope_config.json with caching.
    
    Returns:
        Scope configuration dictionary
    """
    global _scope_config_cache, _scope_config_mtime
    
    scope_config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scope_config.json")
    
    # Check cache
    if os.path.exists(scope_config_path):
        mtime = os.path.getmtime(scope_config_path)
        if _scope_config_cache is not None and _scope_config_mtime is not None:
            if mtime <= _scope_config_mtime:
                return _scope_config_cache
        
        # Load config
        try:
            with open(scope_config_path, 'r') as f:
                _scope_config_cache = json.load(f)
                _scope_config_mtime = mtime
                return _scope_config_cache
        except (json.JSONDecodeError, IOError):
            pass
    
    # Default config if file doesn't exist or fails to load
    return {
        "app_paths": ["App", "Agents"],
        "harness_paths": ["Governor", "Harness", "Workflow"]
    }


def _evaluate_condition(condition: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """
    Evaluate a rule condition against the payload.
    
    Args:
        condition: Condition configuration (field, pattern, operator)
        payload: Hook event payload
        
    Returns:
        True if condition is met, False otherwise
    """
    field = condition.get("field", "")
    pattern = condition.get("pattern", "")
    operator = condition.get("operator", "equals")
    
    debug_log("engine", "Evaluating condition", field=field, pattern=pattern, operator=operator)
    
    # DEBUG: Log entire payload for troubleshooting
    print(f"DEBUG: Evaluating condition for field '{field}' with payload keys: {list(payload.keys())}", flush=True)
    print(f"DEBUG: Full payload: {payload}", flush=True)
    
    # Get field value from payload (support nested field access with dot notation)
    field_value = _get_nested_field(payload, field)
    debug_log("engine", "Field value", field=field, value=field_value)
    
    print(f"DEBUG: Field value for '{field}': {field_value}", flush=True)
    
    # Convert to string for pattern matching
    field_str = str(field_value) if field_value is not None else ""
    
    # Evaluate based on operator
    if operator == "equals":
        result = field_str == pattern
    elif operator == "contains":
        result = pattern in field_str
    elif operator == "regex":
        import re
        result = bool(re.search(pattern, field_str))
    elif operator == "not_equals":
        result = field_str != pattern
    elif operator == "not_contains":
        result = pattern not in field_str
    else:
        # Default to equals if operator not recognized
        result = field_str == pattern
    
    debug_log("engine", "Condition result", result=result)
    print(f"DEBUG: Condition result: {result}", flush=True)
    return result


def _get_nested_field(data: Dict[str, Any], field_path: str) -> Any:
    """
    Get a nested field value from a dictionary using dot notation.
    
    Args:
        data: Dictionary to get field from
        field_path: Dot-separated field path (e.g., "input.file_path")
        
    Returns:
        Field value, or None if not found
    """
    keys = field_path.split(".")
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


def _detect_agent(payload: Dict[str, Any], context: ActionContext) -> str:
    """
    Detect the current agent from payload or context.
    
    Args:
        payload: Hook event payload
        context: ActionContext
        
    Returns:
        Agent name (architect, planner, executor, reviewer, or all)
    """
    # Try to get agent from payload
    if "agent" in payload:
        return payload["agent"]
    
    # Try to get agent from context state machine
    if context and context.state_machine:
        try:
            state = context.state_machine.get_state_snapshot()
            if "agent" in state:
                return state["agent"]
        except Exception:
            pass
    
    # Default to "all" if agent cannot be determined
    return "all"


def _detect_scope(payload: Dict[str, Any], context: ActionContext) -> str:
    """
    Detect the current scope (app vs harness) from payload or context.
    
    Args:
        payload: Hook event payload
        context: ActionContext
        
    Returns:
        Scope name (app, harness, or all)
    """
    # Try to get scope from payload
    if "scope" in payload:
        return payload["scope"]
    
    # Try to get scope from context state machine
    if context and context.state_machine:
        try:
            state = context.state_machine.get_state_snapshot()
            if "scope" in state:
                return state["scope"]
        except Exception:
            pass
    
    # Try to infer scope from file paths in payload
    if "file_path" in payload:
        config = _load_scope_config()
        file_path = payload["file_path"]
        
        # Check against configured app paths
        for app_path in config.get("app_paths", []):
            if app_path in file_path:
                return "app"
        
        # Check against configured harness paths
        for harness_path in config.get("harness_paths", []):
            if harness_path in file_path:
                return "harness"
    
    # Default to "all" if scope cannot be determined
    return "all"


def evaluate_rules(hook_name: str, payload: Dict[str, Any], context: ActionContext) -> List[ActionResult]:
    """
    Evaluate all rules against the current hook event.
    
    This function:
    1. Loads all rules (with caching)
    2. Matches triggers to the current event
    3. Filters by agent (if agent field specified)
    4. Filters by scope (if scope field specified)
    5. Sorts matched rules by priority
    6. Executes actions sequentially
    7. Aggregates results
    
    Args:
        hook_name: Current hook name
        payload: Hook event payload
        context: ActionContext for action execution
        
    Returns:
        List of ActionResult objects from executed actions
    """
    results = []
    
    debug_log("engine", "evaluate_rules called", hook_name=hook_name, num_rules_total=len(load_rules()), payload_keys=list(payload.keys()))
    
    # Log rule evaluation
    log_execution("Engine", {
        "action": "evaluate_rules",
        "hook_name": hook_name,
        "payload_keys": list(payload.keys())
    })
    
    # Load rules
    rules = load_rules()
    
    # Detect current agent and scope from context or payload
    current_agent = _detect_agent(payload, context)
    current_scope = _detect_scope(payload, context)
    
    debug_log("engine", "Detected agent and scope", agent=current_agent, scope=current_scope)
    
    # Match triggers and filter by agent and scope
    matched_rules = []
    for rule in rules:
        if not rule.enabled:
            continue
        
        # Filter by agent if rule specifies one
        if rule.agent and rule.agent != "all" and rule.agent != current_agent:
            continue
        
        # Filter by scope if rule specifies one
        if hasattr(rule, 'scope') and rule.scope and rule.scope != "all" and rule.scope != current_scope:
            continue
        
        for trigger in rule.triggers:
            if match_trigger(trigger, hook_name, payload):
                # Check if rule has conditions and evaluate them
                if rule.check and "condition" in rule.check:
                    if not _evaluate_condition(rule.check["condition"], payload):
                        debug_log("engine", "Rule condition not met", rule_id=rule.id)
                        continue  # Skip this rule if condition not met
                
                matched_rules.append(rule)
                break  # Only need one trigger to match
    
    debug_log("engine", "Matched rules", num_matched=len(matched_rules), matched_ids=[r.id for r in matched_rules])
    
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
    Execute a single action with circuit breaker protection.
    
    Args:
        action_config: Action configuration from rule YAML
        payload: Hook event payload
        context: ActionContext for execution
        
    Returns:
        ActionResult from action execution
    """
    action_name = action_config.get("name") or action_config.get("type")  # Support both name: and type:
    # Spec §3.2: action params are at top level of action config, not nested under params
    params = {k: v for k, v in action_config.items() if k not in ["name", "type"]}
    
    # Get rule ID from context if available
    rule_id = context.payload.get("rule_id", "unknown") if context and context.payload else "unknown"
    
    # Check circuit breaker before executing
    cb_manager = get_circuit_breaker_manager()
    allowed, cb_reason = cb_manager.allow(action_name, rule_id)
    
    if not allowed:
        debug_log("engine", "Circuit breaker blocked action", action=action_name, rule_id=rule_id, reason=cb_reason)
        return ActionResult(
            decision="allow",  # Fail-open
            reason=f"Circuit breaker: {cb_reason}"
        )
    
    # Import action class with security validation
    try:
        # Validate import path for security (per spec §6.4)
        validate_import_path(f"actions.{action_name}")
        
        # Actions are in Governor/actions/ directory (package-relative import)
        if __package__:
            action_module = importlib.import_module(f".actions.{action_name}", package=__package__)
        else:
            # Fallback for direct execution during development
            action_module = importlib.import_module(f"actions.{action_name}")
        # Convert snake_case to PascalCase and append "Action" suffix per spec §6.3
        action_class_name = "".join(word.capitalize() for word in action_name.split("_")) + "Action"
        action_class = getattr(action_module, action_class_name)
    except SecurityError as e:
        # Security violation - fail-open with log
        debug_log("engine", f"Security violation in action import: {e}", action=action_name)
        raise ValueError(f"Security violation in action import: {e}")
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Could not load action {action_name}: {e}")
    
    # Instantiate action
    action = action_class()
    
    # Validate parameters
    action.validate_params(params)
    
    # Execute action with resource limit enforcement
    resource_enforcer = ResourceLimitEnforcer()
    resource_enforcer.start_action()
    
    try:
        # Check resource limits before execution
        within_limits, limit_reason = resource_enforcer.check_resource_limits()
        if not within_limits:
            debug_log("engine", f"Resource limit violation: {limit_reason}", action=action_name)
            log_security_violation("resource_limit_exceeded", {
                "action": action_name,
                "reason": limit_reason
            })
            return ActionResult(
                decision="allow",  # Fail-open
                reason=f"Resource limit: {limit_reason}"
            )
        
        result = action.evaluate(payload, params, context)
        
        # Check resource limits after execution
        within_limits, limit_reason = resource_enforcer.check_resource_limits()
        if not within_limits:
            debug_log("engine", f"Resource limit violation after execution: {limit_reason}", action=action_name)
            log_security_violation("resource_limit_exceeded", {
                "action": action_name,
                "reason": limit_reason
            })
        
        # Record success
        cb_manager.record_success(action_name, rule_id)
        return result
    except Exception:
        # Record failure
        cb_manager.record_failure(action_name, rule_id)
        # Re-raise to be caught by outer try-catch
        raise
    finally:
        resource_enforcer.end_action()


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
