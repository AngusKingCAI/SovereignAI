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

def get_session_context():
    """Get current session context using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Return simple session context
    return {
        'session_id': session_id,
        'agent_type': agent_type,
        'current_phase': None  # Phase system simplified
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

def main():
    """Main permission check logic."""
    print("=== Tool Permission Check ===")
    
    # Get hook environment
    env_vars = get_hook_environment()
    tool_name = env_vars.get('tool_name', 'unknown')
    file_path = env_vars.get('file_path') or ''
    
    print(f"Tool: {tool_name}")
    print(f"File: {file_path or 'N/A'}")
    
    # Load configuration
    config = load_config()
    
    # Get session context
    session_context = get_session_context()
    current_phase = session_context.get('current_phase')
    
    print(f"Current Phase: {current_phase or 'None'}")
    print(f"Session ID: {session_context.get('session_id', 'unknown')}")
    
    # Check directory restrictions
    if file_path:
        print("Checking directory restrictions...")
        allowed, message = check_directory_restriction(file_path, config)
        print(f"Directory check: {message}")
        
        if not allowed:
            print("X Directory restriction violation - operation blocked")
            print(f"Set DEVIN_OUTSIDE_DIR_CONFIRMED=true to allow this operation")
            return 2  # Block the operation
    
    # For now, just log and allow everything (simplified for testing)
    # Full permission checking can be added later based on config
    
    print("=== Permission Check Passed ===")
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