"""
Debug CLI for Governor.py v1.5

This module provides command-line tools for inspecting Governor state,
tracing rule execution, and debugging hook events.

Commands:
- inspect-state: View current state machine state
- trace-rule: Trace rule execution for a specific rule
- trace-bypass: Trace bypass history for a specific rule
- replay-hook: Replay a hook event with current rules

This implements the debug CLI specified in v1.5 spec §4.4.
"""

import sys
import json
import os
from typing import Dict, Any, Optional

# Add Governor to path for module execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Governor components
try:
    from state_machine import StateMachine
    from engine import load_rules, get_rule_stats
    from memoization import get_memoization_stats, reset_memoization_stats
except ImportError:
    print("Error: Cannot import Governor components")
    sys.exit(1)

# Try to import structured logging (optional)
try:
    from structured_logging import is_structlog_enabled
except (ImportError, NameError):
    def is_structlog_enabled():
        return False


def cmd_inspect_state(args):
    """
    Inspect current state machine state.
    
    Usage:
        python -m Governor.debug inspect-state
    """
    print("=== Governor State Inspection ===\n")
    
    try:
        state_machine = StateMachine()
        state = state_machine.get_state_snapshot()
        
        print(f"Phase: {state.get('phase', 'INIT')}")
        print(f"Mode: {state.get('mode', 'app')}")
        print(f"\nCounters:")
        for counter, value in state.get('counters', {}).items():
            print(f"  {counter}: {value}")
        
        print(f"\nFlags:")
        for flag, value in state.get('flags', {}).items():
            print(f"  {flag}: {value}")
        
        print(f"\nBypasses:")
        for scope, bypasses in state.get('bypasses', {}).items():
            print(f"  {scope}: {len(bypasses)} bypasses")
        
        print(f"\nMetadata:")
        print(f"  Last updated: {state.get('metadata', {}).get('last_updated', 'unknown')}")
        print(f"  Session started: {state.get('metadata', {}).get('session_started', 'unknown')}")
        
    except Exception as e:
        print(f"Error inspecting state: {e}")
        sys.exit(1)


def cmd_trace_rule(args):
    """
    Trace rule execution for a specific rule.
    
    Usage:
        python -m Governor.debug trace-rule <rule_id>
    """
    if len(args) < 1:
        print("Usage: python -m Governor.debug trace-rule <rule_id>")
        sys.exit(1)
    
    rule_id = args[0]
    print(f"=== Tracing Rule: {rule_id} ===\n")
    
    try:
        rules = load_rules()
        rule = next((r for r in rules if r.id == rule_id), None)
        
        if not rule:
            print(f"Rule not found: {rule_id}")
            sys.exit(1)
        
        print(f"Rule ID: {rule.id}")
        print(f"Version: {rule.version}")
        print(f"Priority: {rule.priority}")
        print(f"Enabled: {rule.enabled}")
        print(f"Agent: {rule.agent or 'all'}")
        print(f"Scope: {getattr(rule, 'scope', 'all')}")
        print(f"\nTriggers:")
        for trigger in rule.triggers:
            print(f"  - {trigger}")
        print(f"\nCheck: {rule.check}")
        print(f"\nActions:")
        if rule.check and 'params' in rule.check and 'actions' in rule.check['params']:
            for action in rule.check['params']['actions']:
                print(f"  - {action}")
        
    except Exception as e:
        print(f"Error tracing rule: {e}")
        sys.exit(1)


def cmd_trace_bypass(args):
    """
    Trace bypass history for a specific rule.
    
    Usage:
        python -m Governor.debug trace-bypass <rule_id>
    """
    if len(args) < 1:
        print("Usage: python -m Governor.debug trace-bypass <rule_id>")
        sys.exit(1)
    
    rule_id = args[0]
    print(f"=== Tracing Bypasses for Rule: {rule_id} ===\n")
    
    try:
        state_machine = StateMachine()
        state = state_machine.get_state_snapshot()
        
        # Search for bypasses matching the rule
        for scope, bypasses in state.get('bypasses', {}).items():
            for bypass in bypasses:
                if bypass.get('rule_id') == rule_id:
                    print(f"Scope: {scope}")
                    print(f"Timestamp: {bypass.get('timestamp', 'unknown')}")
                    print(f"Reason: {bypass.get('reason', 'unknown')}")
                    print(f"Tool: {bypass.get('tool', 'unknown')}")
                    print()
        
    except Exception as e:
        print(f"Error tracing bypass: {e}")
        sys.exit(1)


def cmd_replay_hook(args):
    """
    Replay a hook event with current rules.
    
    Usage:
        python -m Governor.debug replay-hook <hook_name> <payload_file>
    """
    if len(args) < 2:
        print("Usage: python -m Governor.debug replay-hook <hook_name> <payload_file>")
        sys.exit(1)
    
    hook_name = args[0]
    payload_file = args[1]
    print(f"=== Replaying Hook: {hook_name} ===\n")
    
    try:
        with open(payload_file, 'r') as f:
            payload = json.load(f)
        
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print(f"\nReplay would use current rules:")
        rules = load_rules()
        print(f"  Total rules: {len(rules)}")
        print(f"  Rule stats: {get_rule_stats()}")
        
    except Exception as e:
        print(f"Error replaying hook: {e}")
        sys.exit(1)


def cmd_list_rules(args):
    """
    List all loaded rules.
    
    Usage:
        python -m Governor.debug list-rules
    """
    print("=== Loaded Rules ===\n")
    
    try:
        rules = load_rules()
        
        for rule in rules:
            status = "[OK]" if rule.enabled else "[OFF]"
            print(f"{status} {rule.id} (priority: {rule.priority}, agent: {rule.agent or 'all'})")
        
        print(f"\nTotal: {len(rules)} rules")
        print(f"\nStats: {get_rule_stats()}")
        
    except Exception as e:
        print(f"Error listing rules: {e}")
        sys.exit(1)


def cmd_memoization_stats(args):
    """
    Show memoization statistics.
    
    Usage:
        python -m Governor.debug memoization-stats
    """
    print("=== Memoization Statistics ===\n")
    
    try:
        stats = get_memoization_stats()
        print(f"Hits: {stats['hits']}")
        print(f"Misses: {stats['misses']}")
        print(f"Evictions: {stats['evictions']}")
        
        total = stats['hits'] + stats['misses']
        if total > 0:
            hit_rate = (stats['hits'] / total) * 100
            print(f"Hit Rate: {hit_rate:.2f}%")
        else:
            print("Hit Rate: N/A (no cache activity)")
        
    except Exception as e:
        print(f"Error getting memoization stats: {e}")
        sys.exit(1)


def cmd_reset_memoization(args):
    """
    Reset memoization statistics.
    
    Usage:
        python -m Governor.debug reset-memoization
    """
    print("=== Resetting Memoization Statistics ===\n")
    
    try:
        reset_memoization_stats()
        print("Memoization statistics reset successfully.")
        
    except Exception as e:
        print(f"Error resetting memoization stats: {e}")
        sys.exit(1)


def cmd_logging_status(args):
    """
    Show logging configuration status.
    
    Usage:
        python -m Governor.debug logging-status
    """
    print("=== Logging Configuration Status ===\n")
    
    try:
        structlog_enabled = is_structlog_enabled()
        print(f"Structlog Enabled: {structlog_enabled}")
        
        if structlog_enabled:
            print("Logging Format: JSON (structlog)")
        else:
            print("Logging Format: Text (stdlib fallback)")
        
        print("\nEnvironment Variables:")
        for env_var, layer in {
            "GOVERNOR_DEBUG_ENGINE": "engine",
            "GOVERNOR_DEBUG_STATE_MACHINE": "state_machine",
            "GOVERNOR_DEBUG_HOOK_HANDLERS": "hook_handlers",
            "GOVERNOR_DEBUG_ACTIONS": "actions",
            "GOVERNOR_DEBUG_AUDIT": "audit"
        }.items():
            enabled = os.getenv(env_var, "").lower() in ("1", "true", "yes", "on")
            status = "enabled" if enabled else "disabled"
            print(f"  {env_var}: {status}")
        
    except Exception as e:
        print(f"Error getting logging status: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for debug CLI.
    
    Usage:
        python -m Governor.debug <command> [args...]
    """
    if len(sys.argv) < 2:
        print("Governor Debug CLI")
        print("\nCommands:")
        print("  inspect-state          - View current state machine state")
        print("  trace-rule <id>        - Trace rule execution for a specific rule")
        print("  trace-bypass <id>      - Trace bypass history for a specific rule")
        print("  replay-hook <name> <file> - Replay a hook event")
        print("  list-rules             - List all loaded rules")
        print("  memoization-stats      - Show memoization statistics")
        print("  reset-memoization      - Reset memoization statistics")
        print("  logging-status         - Show logging configuration status")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'inspect-state': cmd_inspect_state,
        'trace-rule': cmd_trace_rule,
        'trace-bypass': cmd_trace_bypass,
        'replay-hook': cmd_replay_hook,
        'list-rules': cmd_list_rules,
        'memoization-stats': cmd_memoization_stats,
        'reset-memoization': cmd_reset_memoization,
        'logging-status': cmd_logging_status,
    }
    
    if command not in commands:
        print(f"Unknown command: {command}")
        print(f"Available commands: {', '.join(commands.keys())}")
        sys.exit(1)
    
    commands[command](args)


if __name__ == "__main__":
    main()
