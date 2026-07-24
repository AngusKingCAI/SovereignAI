---
name: agent
description: Select and switch between available agents
argument-hint: "[agent-name]"
triggers:
  - user
allowed-tools:
  - ask_user_question
  - read
  - write
  - exec
---

# Agent Selection Skill

## Purpose
Allow users to select and switch between available agents in the SovereignAI system.

## Skill Execution
When this skill is invoked, execute the following steps:

### Step 1: Load Current Agent Configuration
Read `.devin/agent_config.json` to understand current agent state.

### Step 2: Present Agent Selection
Present available agents to user using `ask_user_question`:
- Include "Cancel" option to exit without changing agent
- List all available agents with their descriptions
- Show current agent for reference

### Step 3: Update Agent Configuration
When user selects an agent:
- Update `.devin/agent_config.json` with selected agent
- Set environment variable `DEVIN_CURRENT_AGENT` to selected agent
- Log the agent change to current session file
- Confirm the change to user

## Available Agents

### Architect
**Description**: Design deterministic engineering infrastructure and harness systems for AI-driven software development
**Scope**: Infrastructure design, directory structure, workflow definition, gate system design
**Best For**: Architectural decisions, infrastructure planning, governance rules

### Executor
**Description**: Execute plans and implement application code with hook-based governance enforcement
**Scope**: Application code implementation, plan execution, development tasks
**Best For**: Implementation work, code development, executing plans

### Planner
**Description**: Create plans for Executor execution with internal and external review
**Scope**: Planning, workflow creation, task breakdown
**Best For**: Creating implementation plans, task organization

### Researcher
**Description**: Perform external research and create design documents
**Scope**: Research, documentation, design exploration
**Best For**: Research tasks, documentation, design research

### Reviewer
**Description**: Review execution logs and check against rules and gates
**Scope**: Review, verification, compliance checking
**Best For**: Reviewing work, verification, compliance

## Usage Examples

### Select an agent
```
/agent
```
Result: Presents agent selection menu

### Direct agent selection
```
/agent executor
```
Result: Switches to Executor agent directly

## Integration Points

**Configuration**: `.devin/agent_config.json`
**Environment Variables**: `DEVIN_CURRENT_AGENT`, `DEVIN_CURRENT_SKILL`
**Session Logs**: `Logs/{Agent}/{YYYYMMDD-HHMMSS}.md`
**Hooks**: SessionStart hook reads configuration, skill agent tracker updates configuration

## Notes

- Agent changes take effect immediately for the current session
- Agent selection persists in configuration file for future sessions
- Close skill resets agent to Architect as default
- Agent-specific log files are created based on current agent
