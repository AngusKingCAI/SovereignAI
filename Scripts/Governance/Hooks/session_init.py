#!/usr/bin/env python3
"""
Session initialization hook for Devin CLI governance system.
Initializes session state, validates environment, and sets up governance context.
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import simple logger
from simple_logger import log_session_start, get_current_session

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

def get_project_root():
    """Get project root directory."""
    return Path.cwd()

def validate_environment():
    """Validate that required directories and files exist."""
    project_root = get_project_root()
    
    required_dirs = [
        "Agents",
        "Rules", 
        "Scripts",
        "Workflow",
        "Docs"
    ]
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not (project_root / dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"Warning: Missing required directories: {missing_dirs}")
        return False
    
    return True

def initialize_audit_log():
    """Initialize session audit log using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment or context
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Log session start using simple logger
    log_file = log_session_start(session_id, agent_type)
    
    # Store session ID in environment for other hooks
    os.environ['DEVIN_SESSION_ID'] = session_id
    
    return session_id, log_file

def create_session_context():
    """Create session context for governance using simple logger."""
    session_id = get_current_session()
    
    # Try to detect agent type from environment
    agent_type = os.environ.get('DEVIN_AGENT_TYPE', 'General')
    
    # Simple session context - the detailed logging is handled by simple_logger
    session_context = {
        'session_id': session_id,
        'agent_type': agent_type,
        'timestamp': datetime.now().isoformat(),
        'project_root': str(get_project_root()),
        'operations_count': 0
    }
    
    return session_context

def main():
    """Main session initialization logic."""
    print("=== Session Initialization Hook ===")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Load configuration
    config = load_config()
    session_config = config.get('hook_configuration', {}).get('session_init', {}) or {}
    
    # Validate environment
    if session_config.get('validate_environment', True):
        print("Validating environment...")
        env_valid = validate_environment()
        if not env_valid:
            print("Environment validation failed")
        else:
            print("Environment validation passed")
    
    # Initialize audit log using simple logger
    if session_config.get('initialize_audit_log', True):
        print("Initializing audit log...")
        session_id, log_file = initialize_audit_log()
        print(f"Session ID: {session_id}")
        print(f"Log file: {log_file}")
    
    # Create session context
    print("Creating session context...")
    session_context = create_session_context()
    
    print("=== Session Initialization Complete ===")
    print(f"Session ID: {session_context['session_id']}")
    print(f"Agent Type: {session_context['agent_type']}")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in session initialization: {e}", file=sys.stderr)
        sys.exit(1)