#!/usr/bin/env python3
"""
Unified session logger hook for SessionStart and SessionEnd.
Creates agent-specific session files containing all chat interactions, tool executions, and thinking in real-time.
"""

import sys
import json
import os
import uuid
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

class UnifiedSessionLogger:
    """Unified session logger that captures everything in one file."""
    
    def __init__(self):
        self.project_root = Path("C:/SovereignAI")
        self.logs_dir = self.project_root / "Logs"
        self.config_file = self.project_root / ".devin" / "agent_config.json"
        self.session_file = None
        self.session_id = None
        self.current_agent = None
        self.session_start_time = None
    
    def get_session_id(self):
        """Generate or retrieve session ID."""
        # Check if session ID already exists in environment
        session_id = os.environ.get('DEVIN_SESSION_ID')
        if session_id:
            return session_id
        
        # Generate new session ID
        return str(uuid.uuid4())
    
    def read_agent_config(self):
        """Read agent configuration from file."""
        if not self.config_file.exists():
            # Create default config
            default_config = {
                "default_agent": "Architect",
                "current_agent": "Architect",
                "last_updated": datetime.now().isoformat(),
                "session_count": 0
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "default_agent": "Architect",
                "current_agent": "Architect",
                "last_updated": datetime.now().isoformat(),
                "session_count": 0
            }
    
    def write_agent_config(self, config):
        """Write agent configuration to file."""
        try:
            config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except:
            return False
    
    def get_current_agent(self):
        """Determine current agent from config, environment, or skill."""
        # First check environment variable (highest priority during session)
        agent = os.environ.get('DEVIN_CURRENT_AGENT')
        if agent:
            return agent
        
        # Then check configuration file (for session startup)
        config = self.read_agent_config()
        if config and config.get('current_agent'):
            return config['current_agent']
        
        # Then check current skill
        skill = os.environ.get('DEVIN_CURRENT_SKILL')
        if skill:
            return skill.capitalize()
        
        # Default to Architect
        return "Architect"
    
    def get_next_session_number(self, agent_logs_dir):
        """Get the next session number based on existing log files."""
        try:
            # Find all existing session files for this agent
            existing_files = list(agent_logs_dir.glob("*.md"))
            
            if not existing_files:
                return 1
            
            # Extract session numbers from existing files
            # Expected format: Agent_DD-M-YYYY_HH:MM:SS_number.md
            session_numbers = []
            for file in existing_files:
                # Extract the number before .md
                filename = file.stem  # filename without extension
                parts = filename.split('_')
                if len(parts) >= 4:
                    try:
                        number = int(parts[-1])
                        session_numbers.append(number)
                    except ValueError:
                        continue
            
            if not session_numbers:
                return 1
            
            # Return max + 1
            return max(session_numbers) + 1
            
        except Exception:
            return 1

    def initialize_session(self):
        """Initialize a new agent-specific session log file."""
        self.session_id = self.get_session_id()
        self.current_agent = self.get_current_agent()
        self.session_start_time = datetime.now()
        
        # Check if session file already exists in environment (reusing active session)
        existing_session_file = os.environ.get('DEVIN_SESSION_FILE')
        if existing_session_file and Path(existing_session_file).exists():
            self.session_file = Path(existing_session_file)
            return str(self.session_id), str(self.session_file)
        
        # Create agent-specific logs directory
        self.logs_dir.mkdir(exist_ok=True)
        agent_logs_dir = self.logs_dir / self.current_agent
        agent_logs_dir.mkdir(exist_ok=True)
        
        # Get next session number based on existing files
        session_number = self.get_next_session_number(agent_logs_dir)
        
        # Update configuration file with current agent and session count
        config = self.read_agent_config()
        config['current_agent'] = self.current_agent
        config['session_count'] = session_number
        self.write_agent_config(config)
        
        # Create session log file with more readable name
        # Format: AgentName_DD-M-YYYY_HH-MM-SS_number.md (using - instead of : for file system compatibility)
        readable_date = self.session_start_time.strftime("%d-%m-%Y")
        readable_time = self.session_start_time.strftime("%H-%M-%S")
        session_filename = f"{self.current_agent}_{readable_date}_{readable_time}_{session_number}.md"
        self.session_file = agent_logs_dir / session_filename
        
        # Initialize session file with header
        session_header = f"""# {self.current_agent} Session Log

**Session ID**: {self.session_id}
**Agent**: {self.current_agent}
**Start Time**: {self.session_start_time.isoformat()}
**Log File**: {session_filename}

---

## Session Started

**Timestamp**: {self.session_start_time.isoformat()}
**Agent**: {self.current_agent}
**Session ID**: {self.session_id}

**Environment**:
- Working Directory: {os.getcwd()}
- Project Root: {self.project_root}
- Python Version: {sys.version}

**Agent Configuration**:
- Default Agent: {config.get('default_agent', 'Architect')}
- Current Agent: {self.current_agent}
- Session Count: {config.get('session_count', 0)}

---

## Session Activity

"""
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            f.write(session_header)
        
        # Set environment variable for other hooks
        os.environ['DEVIN_SESSION_ID'] = self.session_id
        os.environ['DEVIN_SESSION_FILE'] = str(self.session_file)
        os.environ['DEVIN_CURRENT_AGENT'] = self.current_agent
        
        # Set default agent to Architect for session
        os.environ['DEVIN_DEFAULT_AGENT'] = 'Architect'
        
        return self.session_id, str(self.session_file)
    
    def log_activity(self, activity_type, content, timestamp=None, sender="System"):
        """Log activity to the agent-specific session file."""
        if not self.session_file or not self.session_file.exists():
            return False
        
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(f"\n### {activity_type}\n")
                f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
                f.write(f"**Sender**: {sender}\n\n")
                f.write(f"{content}\n")
                f.write("---\n")
            return True
        except Exception as e:
            return False
    
    def log_hook_output(self, hook_name, output, timestamp=None):
        """Log hook output to the session file."""
        if not self.session_file or not self.session_file.exists():
            return False
        
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(f"\n### Hook Output: {hook_name}\n")
                f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
                f.write(f"**Hook**: {hook_name}\n\n")
                f.write(f"```\n{output}\n```\n")
                f.write("---\n")
            return True
        except Exception as e:
            return False
    
    def close_session(self):
        """Close the session with final summary and reset agent to Architect."""
        if not self.session_file or not self.session_file.exists():
            return
        
        session_end_time = datetime.now()
        duration = session_end_time - self.session_start_time
        
        session_footer = f"""

## Session Ended

**Timestamp**: {session_end_time.isoformat()}
**Duration**: {duration.total_seconds():.2f} seconds
**Agent**: {self.current_agent}
**Session ID**: {self.session_id}

---

## Session Summary

- **Total Duration**: {duration.total_seconds():.2f} seconds
- **Agent**: {self.current_agent}
- **Session ID**: {self.session_id}
- **End Reason**: Session closed or agent switch

---

## Agent Reset

**Previous Agent**: {self.current_agent}
**Reset to**: Architect (default)

---

*End of Session Log*
"""
        
        try:
            with open(self.session_file, 'a', encoding='utf-8') as f:
                f.write(session_footer)
        except Exception as e:
            pass
        
        # Reset agent to Architect in configuration file
        config = self.read_agent_config()
        config['current_agent'] = 'Architect'
        config['default_agent'] = 'Architect'
        self.write_agent_config(config)
        
        # Reset environment variables
        os.environ['DEVIN_CURRENT_AGENT'] = 'Architect'
        os.environ['DEVIN_CURRENT_SKILL'] = ''

def main():
    """Main unified session logger logic."""
    verbosity = get_verbosity()
    show_hook_header("Unified Session Logger", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except Exception as e:
        env_vars = {}
    
    # Get hook event from stdin data (Devin CLI passes event in JSON, not env var)
    hook_event = env_vars.get('hook_event_name', 'SessionStart')
    
    # Initialize session logger
    logger = UnifiedSessionLogger()
    
    if hook_event == 'SessionStart':
        # Initialize new session
        session_id, session_file = logger.initialize_session()
        
        show_hook_result(f"Session initialized: {session_id[:8]}", success=True, verbosity=verbosity)
        
        # Output session info as additional context
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Session ID: {session_id}\nSession File: {session_file}\nAgent: {logger.current_agent}"
            }
        }
        
        print(json.dumps(output, indent=2))
        
    elif hook_event == 'SessionEnd':
        # Close session
        session_id = os.environ.get('DEVIN_SESSION_ID', 'unknown')
        session_file = os.environ.get('DEVIN_SESSION_FILE', '')
        
        if session_file:
            logger.session_file = Path(session_file)
            logger.session_id = session_id
            logger.current_agent = os.environ.get('DEVIN_CURRENT_AGENT', 'General')
            logger.close_session()
        
        show_hook_result(f"Session closed: {session_id[:8]}", success=True, verbosity=verbosity)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in unified session logger: {e}", file=sys.stderr)
        sys.exit(1)
