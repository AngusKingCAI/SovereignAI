#!/usr/bin/env python3
"""
PostCompaction Hook Script
Reloads current agent's AGENTS.md and associated governance files after context compression.
This ensures the agent maintains its behavioral compliance throughout long workflows.
"""

import json
import sys
import os
from pathlib import Path

def detect_current_agent(summary: str | None) -> str:
    """
    Detect the current agent based on compaction summary or conversation patterns.
    Returns: 'reviewer', 'architect', 'executor', 'planner', 'researcher', or 'general'
    """
    if summary:
        summary_lower = summary.lower()
        if 'reviewer' in summary_lower or 'compliance' in summary_lower or 'scan' in summary_lower:
            return 'reviewer'
        elif 'architect' in summary_lower or 'infrastructure' in summary_lower or 'governance' in summary_lower:
            return 'architect'
        elif 'executor' in summary_lower or 'implementation' in summary_lower or 'execute' in summary_lower:
            return 'executor'
        elif 'planner' in summary_lower or 'planning' in summary_lower or 'plan' in summary_lower:
            return 'planner'
        elif 'researcher' in summary_lower or 'research' in summary_lower or 'investigation' in summary_lower:
            return 'researcher'
    
    # Default to architect agent for this project (since it's the root AGENTS.md)
    return 'architect'

def reload_agent_context(agent: str) -> str:
    """
    Reload the appropriate AGENTS.md and associated governance files for the detected agent.
    Returns: additionalContext string to inject into agent's context
    """
    project_root = Path.cwd()
    
    # Agent-specific file mappings
    agent_config = {
        'reviewer': {
            'agents_md': 'Agents/Reviewer/AGENTS.md',
            'rules': 'Rules/Reviewer/Reviewer_Rules.md',
            'workflow': 'Workflow/Reviewer/Reviewer_Best_Practice_Scanner_Workflow.md',
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        },
        'architect': {
            'agents_md': 'AGENTS.md',  # Architect agent lives in root AGENTS.md
            'rules': 'Rules/Architect/Architect_Rules.md',
            'workflow': 'Workflow/Architect/Architect_General_Workflow.md',
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        },
        'executor': {
            'agents_md': 'Agents/Executor/AGENTS.md',
            'rules': 'Rules/Executor/Executor_Rules.md',
            'workflow': 'Workflow/Executor/Executor_Implementation_Workflow.md',
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        },
        'planner': {
            'agents_md': 'Agents/Planner/AGENTS.md',
            'rules': 'Rules/Planner/Planner_Rules.md',
            'workflow': 'Workflow/Planner/Planner_Plan_Workflow.md',
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        },
        'researcher': {
            'agents_md': 'Agents/Researcher/AGENTS.md',
            'rules': 'Rules/Researcher/Researcher_Rules.md',
            'workflow': None,  # Researcher uses skills instead of main workflow
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        },
        'general': {
            'agents_md': 'AGENTS.md',
            'rules': None,
            'workflow': None,
            'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
        }
    }
    
    config = agent_config.get(agent, agent_config['general'])
    
    context_messages = []
    
    # Load AGENTS.md with encoding handling
    agents_md_path = project_root / config['agents_md']
    if agents_md_path.exists():
        try:
            with open(agents_md_path, 'r', encoding='utf-8', errors='ignore') as f:
                agents_content = f.read()
            context_messages.append(f"Reloaded {config['agents_md']} for {agent} agent")
        except Exception as e:
            context_messages.append(f"Warning: Failed to load {config['agents_md']}: {e}")
    else:
        context_messages.append(f"Warning: {config['agents_md']} not found")
    
    # Load rules if specified
    if config['rules']:
        rules_path = project_root / config['rules']
        if rules_path.exists():
            try:
                with open(rules_path, 'r', encoding='utf-8', errors='ignore') as f:
                    rules_content = f.read()
                context_messages.append(f"Reloaded {config['rules']} for {agent} agent")
            except Exception as e:
                context_messages.append(f"Warning: Failed to load {config['rules']}: {e}")
        else:
            context_messages.append(f"Warning: {config['rules']} not found")
    
    # Load workflow if specified
    if config['workflow']:
        workflow_path = project_root / config['workflow']
        if workflow_path.exists():
            try:
                with open(workflow_path, 'r', encoding='utf-8', errors='ignore') as f:
                    workflow_content = f.read()
                context_messages.append(f"Reloaded {config['workflow']} for {agent} agent")
            except Exception as e:
                context_messages.append(f"Warning: Failed to load {config['workflow']}: {e}")
        else:
            context_messages.append(f"Warning: {config['workflow']} not found")
    
    # Load terminology glossary
    if config['terminology']:
        terminology_path = project_root / config['terminology']
        if terminology_path.exists():
            try:
                with open(terminology_path, 'r', encoding='utf-8', errors='ignore') as f:
                    terminology_content = f.read()
                context_messages.append(f"Reloaded {config['terminology']} for context clarity")
            except Exception as e:
                context_messages.append(f"Warning: Failed to load {config['terminology']}: {e}")
        else:
            context_messages.append(f"Warning: {config['terminology']} not found")
    
    # Return additionalContext for hook output
    additional_context = f"""
CONTEXT RESTORED AFTER COMPACTION:
Agent: {agent}
Files Reloaded:
{chr(10).join(f"  - {msg}" for msg in context_messages)}

Continue with your current task. Your governance context has been restored.
"""
    
    return additional_context

def main():
    """Main hook execution"""
    try:
        # Debug: Create a file to verify hook execution
        debug_file = Path.cwd() / ".hook_execution_test.txt"
        debug_file.write_text(f"Hook executed at {__import__('datetime').datetime.now()}")
        
        # Read stdin for hook event data
        stdin_data = sys.stdin.read()
        if not stdin_data:
            return
        
        event_data = json.loads(stdin_data)
        summary = event_data.get('summary')
        
        # Detect current agent
        current_agent = detect_current_agent(summary)
        
        # Reload agent context
        additional_context = reload_agent_context(current_agent)
        
        # Output visible confirmation to stderr
        print(f"[PostCompaction Hook] Detected agent: {current_agent}", file=sys.stderr)
        print(f"[PostCompaction Hook] Reloading governance files...", file=sys.stderr)
        
        # Show which files were loaded
        project_root = Path.cwd()
        agent_config = {
            'reviewer': {
                'agents_md': 'Agents/Reviewer/AGENTS.md',
                'rules': 'Rules/Reviewer/Reviewer_Rules.md',
                'workflow': 'Workflow/Reviewer/Reviewer_Best_Practice_Scanner_Workflow.md',
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            },
            'architect': {
                'agents_md': 'AGENTS.md',
                'rules': 'Rules/Architect/Architect_Rules.md',
                'workflow': 'Workflow/Architect/Architect_General_Workflow.md',
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            },
            'executor': {
                'agents_md': 'Agents/Executor/AGENTS.md',
                'rules': 'Rules/Executor/Executor_Rules.md',
                'workflow': 'Workflow/Executor/Executor_Implementation_Workflow.md',
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            },
            'planner': {
                'agents_md': 'Agents/Planner/AGENTS.md',
                'rules': 'Rules/Planner/Planner_Rules.md',
                'workflow': 'Workflow/Planner/Planner_Plan_Workflow.md',
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            },
            'researcher': {
                'agents_md': 'Agents/Researcher/AGENTS.md',
                'rules': 'Rules/Researcher/Researcher_Rules.md',
                'workflow': None,
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            },
            'general': {
                'agents_md': 'AGENTS.md',
                'rules': None,
                'workflow': None,
                'terminology': 'Workflow/Workflow_Reference/Terminology_Glossary.md'
            }
        }
        
        config = agent_config.get(current_agent, agent_config['general'])
        
        # Check and report each file
        files_to_check = [
            ('AGENTS.md', config['agents_md']),
            ('Rules', config['rules']),
            ('Workflow', config['workflow']),
            ('Terminology', config['terminology'])
        ]
        
        for file_type, file_path in files_to_check:
            if file_path:
                full_path = project_root / file_path
                if full_path.exists():
                    print(f"[PostCompaction Hook] ✓ Loaded {file_type}: {file_path}", file=sys.stderr)
                else:
                    print(f"[PostCompaction Hook] ✗ Missing {file_type}: {file_path}", file=sys.stderr)
            else:
                print(f"[PostCompaction Hook] - {file_type}: Not configured for this agent", file=sys.stderr)
        
        print(f"[PostCompaction Hook] Context restoration complete", file=sys.stderr)
        
        # Output hook-specific context injection with user-visible message
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostCompaction",
                "additionalContext": additional_context,
                "userMessage": f"🔄 Context restored for {current_agent} agent. Governance files reloaded."
            }
        }
        
        print(json.dumps(output))
        
    except Exception as e:
        # Log error but don't fail the hook
        print(f"[PostCompaction Hook] ERROR: {e}", file=sys.stderr)
        error_context = f"ERROR in PostCompaction hook: {e}"
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PostCompaction",
                "additionalContext": error_context,
                "userMessage": f"❌ Error restoring context: {e}"
            }
        }
        print(json.dumps(output))

if __name__ == "__main__":
    main()