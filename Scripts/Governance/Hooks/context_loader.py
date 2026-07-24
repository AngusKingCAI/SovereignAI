#!/usr/bin/env python3
"""
Context Loader Hook - SessionStart
Automatically loads governance rules and templates based on current agent type
Eliminates repetitive documentation reading at workflow session start
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

# Project root
PROJECT_ROOT = Path("C:/SovereignAI")

# Agent-specific rules mapping
AGENT_RULES = {
    "Architect": [
        "Rules/Architect/Architect_Rules.md",
        "Rules/Architect/IDE_Architecture_Rules.md"
    ],
    "Planner": [
        "Rules/Planner/Planner_Rules.md",
        "Workflow/Planner/Plan_Template.md"
    ],
    "Executor": [
        "Rules/Executor/Executor_Rules.md"
    ],
    "Researcher": [
        "Rules/Researcher/Researcher_Rules.md"
    ],
    "Reviewer": [
        "Rules/Reviewer/Reviewer_Rules.md"
    ]
}

# Common governance files for all agents
COMMON_GOVERNANCE = [
    "Scripts/Governance/Config/phase_permissions.json",
    "Docs/Hook-Based-Gate-System.md"
]


def get_current_agent() -> str:
    """Determine current agent from config file."""
    try:
        config_file = PROJECT_ROOT / ".devin" / "agent_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('current_agent', 'Architect')
    except Exception as e:
        print(f"Error reading agent config: {e}", file=sys.stderr)
    
    return "Architect"  # Default fallback


def load_file_content(file_path: str) -> Optional[str]:
    """Load file content if it exists."""
    full_path = PROJECT_ROOT / file_path
    if full_path.exists():
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)
    return None


def generate_context_summary(agent: str, loaded_files: Dict[str, str]) -> str:
    """Generate context summary for injection."""
    summary_parts = [
        f"## Context Loaded for {agent} Agent",
        "",
        "### Governance Rules and Templates",
        ""
    ]
    
    for file_path, content in loaded_files.items():
        if content:
            # For markdown files, include key sections
            if file_path.endswith('.md'):
                # Extract first 50 lines for context
                lines = content.split('\n')[:50]
                summary_parts.append(f"**{file_path}**:")
                summary_parts.append("```")
                summary_parts.extend(lines)
                summary_parts.append("```")
                summary_parts.append("")
            # For JSON files, include key configuration
            elif file_path.endswith('.json'):
                try:
                    data = json.loads(content)
                    summary_parts.append(f"**{file_path}**:")
                    summary_parts.append("```json")
                    summary_parts.append(json.dumps(data, indent=2))
                    summary_parts.append("```")
                    summary_parts.append("")
                except:
                    summary_parts.append(f"**{file_path}**: (JSON content loaded)")
                    summary_parts.append("")
    
    return "\n".join(summary_parts)


def main():
    """Main hook execution."""
    try:
        # Read event data from stdin
        input_data = json.loads(sys.stdin.read())
        hook_event = input_data.get("hook_event_name", "SessionStart")
        
        if hook_event != "SessionStart":
            # Only process SessionStart events
            print(json.dumps({"hookSpecificOutput": {"hookEventName": hook_event}}))
            sys.exit(0)
        
        # Get current agent
        agent = get_current_agent()
        
        # Load agent-specific rules
        agent_files = AGENT_RULES.get(agent, [])
        loaded_files = {}
        
        for file_path in agent_files:
            content = load_file_content(file_path)
            if content:
                loaded_files[file_path] = content
        
        # Load common governance files
        for file_path in COMMON_GOVERNANCE:
            content = load_file_content(file_path)
            if content:
                loaded_files[file_path] = content
        
        # Generate context summary
        context_summary = generate_context_summary(agent, loaded_files)
        
        # Output hook response with context injection
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context_summary
            }
        }
        
        print(json.dumps(output))
        sys.exit(0)
        
    except Exception as e:
        print(f"Context loader error: {e}", file=sys.stderr)
        # Return empty output on error (non-blocking)
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart"}}))
        sys.exit(1)


if __name__ == "__main__":
    main()