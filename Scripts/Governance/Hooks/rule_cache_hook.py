#!/usr/bin/env python3
"""
Rule caching hook for SessionStart.
Loads and caches governance rules for efficient access during the session.
"""

import sys
import json
import os
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_utils import get_verbosity, should_print, show_hook_header, show_hook_result

class RuleCache:
    """Governance rule cache with automatic reload detection."""
    
    def __init__(self):
        self.project_root = Path("C:/SovereignAI")
        self.config_dir = self.project_root / "Scripts" / "Governance" / "Config"
        self.cache_dir = self.project_root / ".devin" / "cache"
        self.cache_file = self.cache_dir / "rule_cache.json"
        self.hash_file = self.cache_dir / "rule_hashes.json"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.rules = {}
        self.rule_hashes = {}
        
    def compute_file_hash(self, file_path):
        """Compute SHA256 hash of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return None
    
    def load_governance_rules(self):
        """Load all governance rules from config directory."""
        rules = {}
        
        # Load governance rules
        governance_file = self.config_dir / "governance_rules.json"
        if governance_file.exists():
            try:
                with open(governance_file) as f:
                    rules['governance'] = json.load(f)
            except Exception as e:
                print(f"Error loading governance rules: {e}")
        
        # Load phase permissions
        phase_file = self.config_dir / "phase_permissions.json"
        if phase_file.exists():
            try:
                with open(phase_file) as f:
                    rules['phases'] = json.load(f)
            except Exception as e:
                print(f"Error loading phase permissions: {e}")
        
        return rules
    
    def compute_rule_hashes(self):
        """Compute hashes of all rule files."""
        hashes = {}
        
        governance_file = self.config_dir / "governance_rules.json"
        if governance_file.exists():
            hashes['governance_rules.json'] = self.compute_file_hash(governance_file)
        
        phase_file = self.config_dir / "phase_permissions.json"
        if phase_file.exists():
            hashes['phase_permissions.json'] = self.compute_file_hash(phase_file)
        
        return hashes
    
    def cache_needs_reload(self):
        """Check if cache needs to be reloaded based on file hashes."""
        if not self.hash_file.exists():
            return True
        
        try:
            with open(self.hash_file) as f:
                cached_hashes = json.load(f)
        except Exception:
            return True
        
        current_hashes = self.compute_rule_hashes()
        
        # Compare hashes
        for file_name, current_hash in current_hashes.items():
            if cached_hashes.get(file_name) != current_hash:
                return True
        
        return False
    
    def load_cache(self):
        """Load rules from cache if available and valid."""
        if not self.cache_file.exists():
            return False
        
        try:
            with open(self.cache_file) as f:
                cached_data = json.load(f)
            
            # Check cache age (reload if older than 1 hour)
            cache_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            age = (datetime.now() - cache_time).total_seconds()
            
            if age > 3600:  # 1 hour
                return False
            
            self.rules = cached_data.get('rules', {})
            return True
        except Exception:
            return False
    
    def save_cache(self):
        """Save rules to cache."""
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'rules': self.rules,
            'cache_version': '1.0'
        }
        
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def save_hashes(self):
        """Save current rule file hashes."""
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(self.rule_hashes, f, indent=2)
        except Exception as e:
            print(f"Error saving hashes: {e}")
    
    def initialize_cache(self):
        """Initialize rule cache with reload detection."""
        # Check if cache needs reload
        if self.cache_needs_reload():
            print("Rule cache: Reloading (files changed or cache expired)")
            self.rules = self.load_governance_rules()
            self.rule_hashes = self.compute_rule_hashes()
            self.save_cache()
            self.save_hashes()
        else:
            print("Rule cache: Loading from cache")
            if not self.load_cache():
                print("Rule cache: Cache load failed, reloading")
                self.rules = self.load_governance_rules()
                self.rule_hashes = self.compute_rule_hashes()
                self.save_cache()
                self.save_hashes()
        
        return self.rules
    
    def get_rules(self):
        """Get cached rules."""
        return self.rules
    
    def get_governance_rules(self):
        """Get governance rules from cache."""
        return self.rules.get('governance', {})
    
    def get_phase_permissions(self):
        """Get phase permissions from cache."""
        return self.rules.get('phases', {})

def log_to_session_file(message, message_type="Info"):
    """Log message to the unified session file."""
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    if not session_file:
        return False
    
    try:
        session_file_path = Path(session_file)
        if not session_file_path.exists():
            return False
        
        timestamp = datetime.now()
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### {message_type}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Source**: Rule Cache Hook\n\n")
            f.write(f"{message}\n")
            f.write("---\n")
        return True
    except Exception:
        return False

def log_hook_output(hook_name, output):
    """Log hook output to the session file."""
    session_file = os.environ.get('DEVIN_SESSION_FILE')
    if not session_file:
        return False
    
    try:
        session_file_path = Path(session_file)
        if not session_file_path.exists():
            return False
        
        timestamp = datetime.now()
        with open(session_file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n### Hook Output: {hook_name}\n")
            f.write(f"**Timestamp**: {timestamp.isoformat()}\n")
            f.write(f"**Hook**: {hook_name}\n\n")
            f.write(f"```\n{output}\n```\n")
            f.write("---\n")
        return True
    except Exception:
        return False

def main():
    """Main rule cache hook logic."""
    verbosity = get_verbosity()
    show_hook_header("Rule Cache Hook", verbosity)
    
    # Get hook environment from stdin
    try:
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
    except Exception as e:
        env_vars = {}
    
    # Get hook event from stdin data
    hook_event = env_vars.get('hook_event_name', 'SessionStart')
    
    if hook_event == 'SessionStart':
        # Initialize rule cache
        cache = RuleCache()
        rules = cache.initialize_cache()
        
        cache_message = f"Rule cache initialized with {len(rules)} rule sets\nCache file: {cache.cache_file}\nCache time: {datetime.now().isoformat()}"
        show_hook_result(f"Rule cache initialized with {len(rules)} rule sets", success=True, verbosity=verbosity)
        
        # Log to session file
        log_to_session_file(cache_message, "Rule Cache Initialization")
        
        # Log hook output to session file
        hook_output = f"Rule cache loaded: {len(rules)} rule sets available\nCache file: {cache.cache_file}"
        log_hook_output("Rule Cache Hook", hook_output)
        
        # Set environment variables for other hooks to use
        os.environ['DEVIN_RULE_CACHE_LOADED'] = 'true'
        os.environ['DEVIN_RULE_CACHE_TIME'] = datetime.now().isoformat()
        
        # Output cache status as additional context
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": f"Rule cache loaded: {len(rules)} rule sets available\nCache file: {cache.cache_file}"
            }
        }
        
        print(json.dumps(output, indent=2))
        
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"Error in rule cache hook: {e}", file=sys.stderr)
        sys.exit(1)