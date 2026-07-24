---
name: executor
description: Load Executor workflows and provide workflow selection
argument-hint: "[workflow-name]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - find_file_by_name
  - ask_user_question
  - exec
  - write
  - edit
---

# Executor Workflow Discovery Skill

## Purpose
Load Executor agent documentation and provide workflow selection from Workflow/Executor/ directory.

## Skill Execution
When this skill is invoked, execute the following steps:

### Step 1: Load Executor Agent Documentation
Read `Agents/Executor/AGENTS.md` to understand Executor agent scope and responsibilities.

### Step 2: Discover Available Workflows
Scan `Workflow/Executor/` directory for `.md` files and extract metadata:
- Use `find_file_by_name` with pattern `*.md` in `Workflow/Executor/`
- For each file found, read the first 10 lines to extract metadata
- Look for workflow name and description in file headers

### Step 3: Present Workflow Selection
Present discovered workflows to user using `ask_user_question`:
- Include "Close" option to exit workflow discovery
- List all discovered workflows with their descriptions

### Step 4: Execute Selected Workflow
When user selects a workflow:
- Load the selected workflow file from `Workflow/Executor/`
- Read the full workflow content
- Immediately execute the workflow's defined steps and gates as specified in the workflow file
- User selection is the execution signal - no additional confirmation needed

## Workflow File Format
Each workflow file in `Workflow/Executor/` should:
- Define its own steps and procedures
- Include its own gate enforcement logic
- Follow the naming convention `{Agent}_{Workflow_Name}.md`
- Include metadata header (name, description) for discovery

## Close Workflow
To exit the Executor workflow discovery, use the global `close` skill.