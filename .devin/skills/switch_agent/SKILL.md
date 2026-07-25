---
name: switch
description: Switch between different agents (Executor, Planner, Researcher, Reviewer) using interactive selection menu
aliases: [switch_agent]
---

# Agent Switcher

## Purpose
Switch between available agents using an interactive selection menu. Read available agents from the Agents/ directory and present user with options using ask_user_question.

## Invocation
Invoke this skill using: `/switch` or `/switch_agent`

## Available Agents

Based on the Agents/ directory structure, the following agents are available for switching:
- **Executor**: Execute implementation plans with precision
- **Planner**: Create detailed implementation plans
- **Researcher**: Conduct research and gather information
- **Reviewer**: Review and validate work quality

Each agent has multiple workflows available in their Workflow/ directory.

## Actions

1. **Read available agents** from `Agents/` directory by calling skill.py without arguments
2. **Present agent selection menu** using ask_user_question with numbered choices for available agents
3. **Read available workflows** for selected agent by calling `skill.py workflows <agent_name>`
4. **Present workflow selection menu** using ask_user_question with numbered choices for workflows
5. **Update agent configuration** in `.devin/agent_config.json` by calling `skill.py switch <agent_name> <workflow_id>`
6. **Load selected agent's workflow file** from their Workflow/ directory
7. **Initiate selected agent's workflow** as specified in the workflow file
8. **Log agent switch** to appropriate log file
9. **Provide confirmation** to user

## Implementation Instructions

When this skill is invoked:

1. First call the skill.py script without arguments to get available agents:
   ```
   python .devin/skills/switch_agent/skill.py
   ```

2. Use ask_user_question to present the agent selection menu with numbered choices formatted like:
   ```
   Which agent would you like to switch to?

   1. Architect: System-level designer who creates deterministic harness infrastructure
   2. Executor: Execute implementation plans with precision
   3. Planner: Create detailed implementation plans
   4. Researcher: Conduct research and gather information
   5. Reviewer: Review and validate work quality
   ```

3. After user selects an agent, call the skill.py script to get workflows for that agent:
   ```
   python .devin/skills/switch_agent/skill.py workflows <selected_agent>
   ```

4. Use ask_user_question to present the workflow selection menu with numbered choices formatted like:
   ```
   Which workflow would you like to use for <selected_agent>?

   1. Architect_General_Workflow: General workflow for Architect agent
   2. Another_Workflow: Description of another workflow
   ```

5. After user selects a workflow, call the skill.py script to switch to the agent with the selected workflow:
   ```
   python .devin/skills/switch_agent/skill.py switch <selected_agent> <workflow_id>
   ```

6. Load the selected agent's workflow file and initiate their workflow

## Selection Menu Format

The menu should present agents in numbered format with their workflows indented below, similar to Architect workflow format:

```
Select an agent and workflow:

1. Executor - Execute implementation plans with precision
   1.1 Executor_Implementation_Cycle - Detailed execution cycle with plan following

2. Planner - Create detailed implementation plans  
   2.1 Planner_Plan_Workflow - Plan creation and validation workflow

3. Researcher - Conduct research and gather information
   3.1 Research - Research and information gathering workflow

4. Reviewer - Review and validate work quality
   4.1 Review - Review and validation workflow
```

## Skill Script Integration

Use the skill.py script to:
- Read available agents from Agents/ directory
- Update agent configuration in `.devin/agent_config.json`
- Log agent switch to Logs/Architect/

Call the script with: `python .devin/skills/switch_agent/skill.py <agent_name>`

## Configuration Update

The skill.py script will update `.devin/agent_config.json`:
```json
{
  "default_agent": "Architect",
  "current_agent": "<selected_agent>",
  "last_updated": "<current_timestamp>",
  "session_count": <current_count>
}
```

## Workflow Initiation

After agent selection:
1. Load the selected agent's AGENTS.md file from `Agents/{Agent}/AGENTS.md`
2. Read the agent's workflow specification from their AGENTS.md
3. Initiate the agent's standard workflow as specified
4. Begin agent-specific workflow execution

## Session Logging

The skill.py script will log agent switch to `Logs/Architect/{timestamp}.md`:
```
## Agent Switch
- From Agent: Architect
- To Agent: {SelectedAgent}
- Timestamp: {current_timestamp}
- Reason: User invoked /switch_agent
```

## Confirmation

Provide user confirmation:
```
Switched to {SelectedAgent} agent.
Loading {SelectedAgent} workflow...
```

## Agent Workflow Loading

Each agent has their own workflow defined in their AGENTS.md:
- **Executor**: Detailed execution cycle with plan following
- **Planner**: Plan creation and validation workflow
- **Researcher**: Research and information gathering workflow  
- **Reviewer**: Review and validation workflow

Load the appropriate AGENTS.md and initiate the workflow specified there.