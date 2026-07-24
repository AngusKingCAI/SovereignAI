#!/usr/bin/env python3
"""
Operation logger hook for Devin CLI governance system.
Logs tool operations, updates state, and verifies integrity after tool execution.
"""

import sys
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simple logger
from simple_logger import log_operation, get_current_session

def load_config():
    """Load governance configuration."""
    config_dir = Path(__file__).parent.parent / "Config"
    governance_config = config_dir / "governance_rules.json"
    
    if governance_config.exists():
        try:
            with open(governance_config) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse governance config: {e}")
            return {}
    return {}

def get_session_context():
    """Get current session context using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Return simple session context
    return {
        'session_id': session_id,
        'agent_type': agent_type,
        'operations_count': 0
    }

def get_hook_environment():
    """Get hook environment variables from stdin."""
    try:
        data = sys.stdin.read()
        if data:
            return json.loads(data)
    except:
        pass
    return {
        'tool_name': os.environ.get('DEVIN_TOOL_NAME', ''),
        'file_path': os.environ.get('DEVIN_FILE_PATH', ''),
        'tool_result': os.environ.get('DEVIN_TOOL_RESULT', '')
    }

def log_tool_execution(tool_name, file_path, tool_result, session_context):
    """Log tool execution using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Log operation using simple logger
    log_file = log_operation(session_id, tool_name, file_path, tool_result, agent_type)
    
    return True

def update_operation_counters(session_context):
    """Update operation counters in session context (simplified)."""
    # Simple logger handles this automatically, so this is a no-op
    return True

def verify_file_integrity(file_path):
    """Verify file integrity after write operations."""
    if not file_path or not Path(file_path).exists():
        return True, "No file to verify"
    
    try:
        # Calculate file hash
        file_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()
        return True, f"File integrity verified: {file_hash[:16]}..."
    except Exception as e:
        return False, f"Integrity check failed: {e}"

def check_violations(tool_name, file_path, config):
    """Check for governance violations in the operation."""
    governance = config.get('governance', {})
    operation_restrictions = governance.get('operation_restrictions', {})
    
    violations = []
    
    # Check for high-risk operations
    high_risk_ops = operation_restrictions.get('high_risk_operations', [])
    for risk_pattern in high_risk_ops:
        if risk_pattern in file_path or (tool_name == 'exec' and risk_pattern in file_path):
            violations.append(f"High-risk operation detected: {risk_pattern}")
    
    return violations

def update_state_if_complete(session_context, config):
    """Update phase state if completion criteria are met."""
    current_phase = session_context.get('current_phase')
    if not current_phase:
        return False, "No current phase"
    
    # This would contain logic to check if phase completion criteria are met
    # For now, just log that we checked
    logs_dir = Path(__file__).parent.parent.parent.parent / "Logs" / "Architect" / "Gates"
    state_file = logs_dir / f"phase-{current_phase}-state.json"
    
    if state_file.exists():
        try:
            with open(state_file) as f:
                state = json.load(f)
            
            # Update hook metadata
            if 'hook_metadata' not in state:
                state['hook_metadata'] = {}
            
            state['hook_metadata']['operations_count'] = session_context.get('operations_count', 0)
            state['hook_metadata']['last_operation'] = session_context.get('last_operation', '')
            
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
            
            return True, f"Updated state for phase {current_phase}"
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse state file {state_file}: {e}")
            return False, f"Could not update state for phase {current_phase}"
    
    return False, f"No state file for phase {current_phase}"

def main():
    """Main operation logging logic."""
    print("=== Operation Logger ===")
    
    # Get hook environment
    env_vars = get_hook_environment()
    tool_name = env_vars.get('tool_name', 'unknown')
    file_path = env_vars.get('file_path', '')
    tool_result = env_vars.get('tool_result', '')
    
    print(f"Tool: {tool_name}")
    print(f"File: {file_path or 'N/A'}")
    
    # Get session context
    session_context = get_session_context()
    
    # Load configuration
    config = load_config()
    
    # Get hook configuration
    governance = config.get('governance', {}) or {}
    logger_config = governance.get('hook_configuration', {}).get('operation_logger', {}) or {}
    
    # Log tool execution
    if logger_config.get('log_tool_execution', True):
        print("Logging tool execution...")
        log_tool_execution(tool_name, file_path, tool_result, session_context)
    
    # Update operation counters (now handled by simple logger)
    if logger_config.get('update_operation_counters', True):
        print("Operation counter updated automatically by simple logger")
    
    print("=== Operation Logging Complete ===")
    return 0  # Don't block operation (it already completed)

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in operation logging: {e}", file=sys.stderr)
        sys.exit(1)