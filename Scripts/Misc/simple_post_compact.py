#!/usr/bin/env python3
"""
PostCompaction Hook Script for Devin CLI
Reloads current agent's AGENTS.md and associated governance files after context compression.
Based on aide-memory's Devin CLI implementation pattern.
"""

import json
import sys
import os
from pathlib import Path

def main():
    """Main hook execution"""
    try:
        # Debug: Create a file to verify hook execution
        debug_file = Path("C:/SovereignAI/.hook_execution_test.txt")
        debug_file.write_text(f"Hook executed at {__import__('datetime').datetime.now()}")
        
        # Read stdin for hook event data
        stdin_data = sys.stdin.read()
        
        # Debug: Log stdin data to understand structure
        debug_data_file = Path("C:/SovereignAI/.hook_stdin_debug.txt")
        debug_data_file.write_text(f"Stdin data at {__import__('datetime').datetime.now()}:\n{stdin_data}")
        
        # Try to determine current agent from stdin data
        current_agent = None
        if stdin_data:
            try:
                event_data = json.loads(stdin_data)
                # Look for agent information in various possible fields
                current_agent = event_data.get('agent') or event_data.get('currentAgent') or event_data.get('agentName')
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to detect agent from environment or files
        if not current_agent:
            # Check if there's a current agent indicator file
            agent_indicator = Path("C:/SovereignAI/.current_agent")
            if agent_indicator.exists():
                current_agent = agent_indicator.read_text().strip()
        
        project_root = Path("C:/SovereignAI")
        context_message = ""
        
        # If we can determine the current agent, load its specific files
        if current_agent:
            agent_dir = project_root / "Agents" / current_agent
            if agent_dir.exists():
                # Load agent-specific AGENTS.md
                agent_agents_file = agent_dir / "AGENTS.md"
                if agent_agents_file.exists():
                    try:
                        agents_content = agent_agents_file.read_text()
                        context_message += f"=== {current_agent} AGENTS.md ===\n{agents_content}\n\n"
                    except Exception as e:
                        context_message += f"Error reading {current_agent} AGENTS.md: {e}\n\n"
                
                # Load agent-specific rules if they exist
                agent_rules_file = agent_dir / "RULES.md"
                if agent_rules_file.exists():
                    try:
                        rules_content = agent_rules_file.read_text()
                        context_message += f"=== {current_agent} RULES.md ===\n{rules_content}\n\n"
                    except Exception as e:
                        context_message += f"Error reading {current_agent} RULES.md: {e}\n\n"
            else:
                context_message += f"Agent directory not found: {agent_dir}\n\n"
        else:
            # Fallback: load main AGENTS.md if agent detection fails
            agents_file = project_root / "AGENTS.md"
            if agents_file.exists():
                try:
                    agents_content = agents_file.read_text()
                    context_message += f"=== AGENTS.md (fallback - could not detect current agent) ===\n{agents_content}\n\n"
                except Exception as e:
                    context_message += f"Error reading AGENTS.md: {e}\n\n"
            else:
                context_message += "AGENTS.md not found and could not detect current agent\n\n"
        
        # Devin CLI format from aide-memory example
        output = {
            "hookSpecificOutput": {
                "additionalContext": context_message
            }
        }
        print(json.dumps(output))
        
    except Exception as e:
        # Log error but don't fail the hook
        debug_file = Path("C:/SovereignAI/.hook_error.txt")
        debug_file.write_text(f"Hook error at {__import__('datetime').datetime.now()}: {e}")
        # Still output valid JSON even on error
        output = {
            "hookSpecificOutput": {
                "additionalContext": f"PostCompaction hook encountered error: {e}"
            }
        }
        print(json.dumps(output))

if __name__ == "__main__":
    main()