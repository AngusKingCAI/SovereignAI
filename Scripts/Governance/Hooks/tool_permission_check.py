#!/usr/bin/env python3
"""
Tool permission check hook for Devin CLI governance system.
Validates tool permissions before execution, enforcing phase-based restrictions.
"""

import sys
import json
import os
import re
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simple logger with proper path handling
try:
    from simple_logger import get_current_session
except ImportError:
    # Fallback if import fails
    def get_current_session():
        import uuid
        session_id = os.environ.get('DEVIN_SESSION_ID')
        if not session_id:
            session_id = str(uuid.uuid4())
            os.environ['DEVIN_SESSION_ID'] = session_id
        return session_id

def load_config():
    """Load governance configuration."""
    config_dir = Path(__file__).parent.parent / "Config"
    governance_config = config_dir / "governance_rules.json"
    phase_config = config_dir / "phase_permissions.json"
    
    config = {}
    
    # Load governance rules
    if governance_config.exists():
        try:
            with open(governance_config) as f:
                config['governance'] = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse governance config: {e}")
            config['governance'] = {}
    
    # Load phase permissions
    if phase_config.exists():
        try:
            with open(phase_config) as f:
                config['phases'] = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse phase config: {e}")
            config['phases'] = {}
    
    return config

def get_current_phase():
    """Detect current phase from state files."""
    project_root = Path("C:/SovereignAI")
    gates_dir = project_root / "Logs" / "Architect" / "Gates"
    
    try:
        # Read session context if available
        session_context_file = gates_dir / "session-context.json"
        if session_context_file.exists():
            with open(session_context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
                return context.get('current_phase')
        
        # Fallback: check for state files to determine highest completed phase
        if gates_dir.exists():
            state_files = list(gates_dir.glob("phase-*-state.json"))
            if state_files:
                # Find the highest phase number
                phase_numbers = []
                for state_file in state_files:
                    match = re.search(r'phase-(\d+)-state', state_file.name)
                    if match:
                        phase_numbers.append(int(match.group(1)))
                
                if phase_numbers:
                    highest_phase = max(phase_numbers)
                    # Current phase is the next one after highest completed
                    return f"phase_{highest_phase + 1}"
        
        return "phase_0"  # Default to phase 0 if no state found
        
    except Exception as e:
        print(f"Error detecting current phase: {e}", file=sys.stderr)
        return "phase_0"  # Default fallback


def get_session_context():
    """Get current session context using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment or config
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'Architect')
    if agent_type == 'General':
        # Try to read from agent config
        try:
            config_file = Path("C:/SovereignAI/.devin/agent_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    agent_type = config.get('current_agent', 'Architect')
        except:
            pass
    
    # Get current phase from state files
    current_phase = get_current_phase()
    
    # Return enhanced session context
    return {
        'session_id': session_id,
        'agent_type': agent_type,
        'current_phase': current_phase
    }

def get_hook_environment():
    """Get hook environment variables from stdin."""
    import sys
    
    env_vars = {}
    try:
        # Read from stdin (hook environment)
        data = sys.stdin.read()
        if data:
            env_vars = json.loads(data)
    except:
        # Fallback to environment variables
        env_vars = {
            'tool_name': os.environ.get('DEVIN_TOOL_NAME', ''),
            'file_path': os.environ.get('DEVIN_FILE_PATH', ''),
            'phase_id': os.environ.get('DEVIN_PHASE_ID', '')
        }
    
    # If file_path is still empty, try to get from command line args for testing
    if not env_vars.get('file_path') and len(sys.argv) > 1:
        env_vars['file_path'] = sys.argv[1]
    
    return env_vars

def check_directory_restriction(file_path, config):
    """Check if operation is within C:/SovereignAI directory."""
    if not file_path:
        return True, "No file path specified, allowing operation"
    
    # Normalize the file path
    file_path_normalized = Path(file_path).resolve()
    
    # Define allowed base directory
    allowed_base = Path("C:/SovereignAI").resolve()
    
    # Check if file path is within allowed directory
    try:
        file_path_normalized.relative_to(allowed_base)
        return True, f"File path {file_path} is within allowed directory"
    except ValueError:
        # File is outside allowed directory
        # Check for user confirmation flag
        user_confirmed = os.environ.get('DEVIN_OUTSIDE_DIR_CONFIRMED', '').lower() == 'true'
        
        if user_confirmed:
            return True, f"User confirmed operation outside C:/SovereignAI for {file_path}"
        else:
            return False, f"File path {file_path} is outside C:/SovereignAI directory. User confirmation required."


def check_phase_permissions(tool_name, file_path, current_phase, config):
    """Check if operation is allowed in current phase."""
    if not current_phase:
        return True, "No phase detected, allowing operation"
    
    phases = config.get('phases', {})
    phase_config = phases.get(current_phase, {})
    
    # Check if tool is allowed in this phase
    allowed_tools = phase_config.get('allowed_tools', [])
    if allowed_tools and tool_name not in allowed_tools:
        return False, f"Tool '{tool_name}' is not allowed in {current_phase}. Allowed tools: {allowed_tools}"
    
    # Check file operation permissions
    if file_path:
        allowed_operations = phase_config.get('allowed_file_operations', [])
        forbidden_operations = phase_config.get('forbidden_operations', [])
        
        # Check forbidden operations first
        for forbidden in forbidden_operations:
            if forbidden.startswith('modify:') and file_path.startswith(forbidden.replace('modify:', '')):
                return False, f"Cannot modify files in {forbidden.replace('modify:', '')} during {current_phase}"
            elif forbidden.startswith('delete:') and forbidden == 'delete:*':
                return False, f"Delete operations are not allowed during {current_phase}"
        
        # Check if operation matches allowed operations
        operation_allowed = False
        for allowed in allowed_operations:
            if allowed.startswith('modify:') and file_path.startswith(allowed.replace('modify:', '')):
                operation_allowed = True
                break
            elif allowed.startswith('create:') and file_path.startswith(allowed.replace('create:', '')):
                operation_allowed = True
                break
            elif allowed == 'read:*' and tool_name == 'read':
                operation_allowed = True
                break
        
        if not operation_allowed and allowed_operations:
            return False, f"File operation on {file_path} is not allowed in {current_phase}. Allowed operations: {allowed_operations}"
    
    # Check required phase completions
    required_completions = phase_config.get('required_completions', [])
    if required_completions:
        project_root = Path("C:/SovereignAI")
        gates_dir = project_root / "Logs" / "Architect" / "Gates"
        
        for required_phase in required_completions:
            state_file = gates_dir / f"{required_phase}-state.json"
            if not state_file.exists():
                return False, f"Required phase {required_phase} is not complete. Cannot proceed with {current_phase} operations."
    
    return True, f"Operation allowed in {current_phase}"

def main():
    """Main permission check logic."""
    # Read event data from stdin for hook integration
    try:
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "PreToolUse")
        tool_name = input_data.get("tool_name", "unknown")
        tool_input = input_data.get("tool_input", {})
        file_path = tool_input.get("file_path", "")
    except:
        # Fallback to environment for testing
        env_vars = get_hook_environment()
        tool_name = env_vars.get('tool_name', 'unknown')
        file_path = env_vars.get('file_path') or ''
    
    print("=== Tool Permission Check ===")
    print(f"Tool: {tool_name}")
    print(f"File: {file_path or 'N/A'}")
    
    # Load configuration
    config = load_config()
    
    # Get session context with phase detection
    session_context = get_session_context()
    current_phase = session_context.get('current_phase')
    
    print(f"Current Phase: {current_phase or 'None'}")
    print(f"Session ID: {session_context.get('session_id', 'unknown')}")
    print(f"Agent Type: {session_context.get('agent_type', 'unknown')}")
    
    # Check directory restrictions
    if file_path:
        print("Checking directory restrictions...")
        allowed, message = check_directory_restriction(file_path, config)
        print(f"Directory check: {message}")
        
        if not allowed:
            print("X Directory restriction violation - operation blocked")
            print(f"Set DEVIN_OUTSIDE_DIR_CONFIRMED=true to allow this operation")
            # Return hook blocking response
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message
                }
            }
            print(json.dumps(output))
            return 2  # Block the operation
    
    # Check phase permissions
    print("Checking phase permissions...")
    phase_allowed, phase_message = check_phase_permissions(tool_name, file_path, current_phase, config)
    print(f"Phase check: {phase_message}")
    
    if not phase_allowed:
        print("X Phase permission violation - operation blocked")
        # Return hook blocking response
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": phase_message
            }
        }
        print(json.dumps(output))
        return 2  # Block the operation
    
    print("=== Permission Check Passed ===")
    # Return hook allowing response
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse"
        }
    }
    print(json.dumps(output))
    return 0  # Allow the operation

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        import traceback
        print(f"Error in permission check: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)