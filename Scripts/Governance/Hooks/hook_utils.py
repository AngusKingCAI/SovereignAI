#!/usr/bin/env python3
"""
Shared utility functions for governance hooks.
Provides verbosity control and common functionality.
"""

import json
import sys
import os
from pathlib import Path

def get_verbosity():
    """Get current verbosity level from skill configuration."""
    verbosity_file = Path(".devin/verbosity.json")
    if verbosity_file.exists():
        try:
            with open(verbosity_file) as f:
                config = json.load(f)
                return config.get("verbosity", "normal")
        except:
            pass
    return "normal"  # Default verbosity

def should_print(message_type, verbosity=None):
    """Determine if message should be printed based on verbosity."""
    if verbosity is None:
        verbosity = get_verbosity()
    
    if verbosity == "quiet":
        return message_type == "error"
    elif verbosity == "minimal":
        return message_type in ["error", "failure"]
    elif verbosity == "normal":
        return message_type in ["error", "failure", "success"]
    elif verbosity == "verbose":
        return True  # Print everything
    return True  # Default to showing everything

def hook_print(message, message_type="info", verbosity=None):
    """Print message based on current verbosity level."""
    if should_print(message_type, verbosity):
        print(message, file=sys.stderr if message_type == "error" else sys.stdout)
        # Also log to session file if available
        session_file = os.environ.get('DEVIN_SESSION_FILE')
        if session_file:
            try:
                from datetime import datetime
                session_file_path = Path(session_file)
                if session_file_path.exists():
                    with open(session_file_path, 'a', encoding='utf-8') as f:
                        timestamp = datetime.now().isoformat()
                        f.write(f"\n### {message_type.upper()}\n")
                        f.write(f"**Timestamp**: {timestamp}\n")
                        f.write(f"**Source**: Hook System\n\n")
                        f.write(f"{message}\n")
                        f.write("---\n")
            except Exception:
                pass  # Don't fail if session logging fails

def show_hook_header(hook_name, verbosity=None):
    """Show hook header based on verbosity level."""
    if should_print("success", verbosity):
        hook_print(f"=== {hook_name} ===", "success", verbosity)

def show_hook_result(message, success=True, verbosity=None):
    """Show hook result based on verbosity level."""
    message_type = "success" if success else "failure"
    prefix = "OK" if success else "X"
    if should_print(message_type, verbosity):
        hook_print(f"{prefix} {message}", message_type, verbosity)

def show_hook_error(message, verbosity=None):
    """Show hook error (always shown regardless of verbosity)."""
    hook_print(f"ERROR: {message}", "error", verbosity)

def show_hook_error_details(message, verbosity=None):
    """Show hook error details (shown based on verbosity)."""
    if verbosity != "quiet":
        hook_print(f"X {message}", "failure", verbosity)
