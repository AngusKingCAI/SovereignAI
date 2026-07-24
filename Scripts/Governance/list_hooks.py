#!/usr/bin/env python3
"""
Hook viewer script for Devin CLI.
Lists all configured hooks from both .devin/hooks.v1.json and .claude/settings.json
"""

import json
from pathlib import Path

def load_hooks(file_path, description):
    """Load hooks from a JSON file."""
    hooks_file = Path(file_path)
    if not hooks_file.exists():
        return None, f"{description} not found"
    
    try:
        with open(hooks_file, 'r') as f:
            data = json.load(f)
        
        # Handle different formats
        if 'hooks' in data:
            hooks = data['hooks']
        else:
            # Assume the whole file is hooks (like .devin/hooks.v1.json)
            hooks = data
        
        return hooks, f"{description} loaded successfully"
    except Exception as e:
        return None, f"Error loading {description}: {e}"

def display_hooks(hooks, title):
    """Display hooks in a readable format."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    
    if not hooks:
        print("No hooks configured")
        return
    
    total_hooks = 0
    for event_name, event_hooks in hooks.items():
        if event_hooks:
            print(f"\n[EVENT] {event_name}")
            for hook_group in event_hooks:
                matcher = hook_group.get('matcher', 'all tools')
                hook_list = hook_group.get('hooks', [])
                
                print(f"   Matcher: {matcher if matcher else 'all'}")
                for hook in hook_list:
                    hook_type = hook.get('type', 'command')
                    command = hook.get('command', 'unknown')
                    timeout = hook.get('timeout', 'default')
                    
                    print(f"   - {hook_type}: {command[:60]}{'...' if len(command) > 60 else ''} (timeout: {timeout}s)")
                    total_hooks += 1
    
    print(f"\n[STATS] Total hooks: {total_hooks}")

def main():
    """Main hook viewer logic."""
    print("[HOOK VIEWER] Devin CLI Hook Viewer")
    print("="*60)
    
    # Load Devin hooks
    devin_hooks, devin_status = load_hooks(".devin/hooks.v1.json", "Devin hooks (.devin/hooks.v1.json)")
    if devin_hooks:
        display_hooks(devin_hooks, "Devin CLI Hooks")
    else:
        print(f"\n[ERROR] {devin_status}")
    
    # Load Claude hooks
    claude_hooks, claude_status = load_hooks(".claude/settings.json", "Claude hooks (.claude/settings.json)")
    if claude_hooks:
        display_hooks(claude_hooks, "Claude Code Hooks")
    else:
        print(f"\n[ERROR] {claude_status}")
    
    print(f"\n{'='*60}")
    print("[TIPS]")
    print("  - Devin hooks: .devin/hooks.v1.json")
    print("  - Claude hooks: .claude/settings.json")
    print("  - Both formats are automatically loaded by Devin CLI")
    print("="*60)

if __name__ == "__main__":
    main()