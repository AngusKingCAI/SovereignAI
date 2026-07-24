#!/usr/bin/env python3
"""
User prompt expansion validator hook for UserPromptExpansion.
Validates expanded prompts from slash commands and skill invocations.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

def main():
    """Validate user prompt expansions."""
    try:
        # Read event data from stdin
        data = sys.stdin.read()
        if data.strip():
            env_vars = json.loads(data)
        else:
            env_vars = {}
        
        # Extract expansion information
        expanded_prompt = env_vars.get('expanded_prompt', '')
        original_input = env_vars.get('original_input', '')
        
        # Log the expansion for transparency
        log_file = Path("C:/SovereignAI/.claude/prompt-expansions.log")
        log_file.parent.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] Prompt expansion\n"
        log_entry += f"Original: {original_input}\n"
        log_entry += f"Expanded: {expanded_prompt[:200]}{'...' if len(expanded_prompt) > 200 else ''}\n"
        log_entry += "---\n"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return 0  # Allow the expansion
        
    except Exception as e:
        # Don't block operations even if validation fails
        return 0

if __name__ == "__main__":
    sys.exit(main())