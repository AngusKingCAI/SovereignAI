---
name: planner
description: Load Planner workflows and provide workflow selection
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

# Planner Workflow Discovery Skill

## Purpose
Load Planner agent documentation and provide workflow selection from Workflow/Planner/ directory.

## Skill Execution
When this skill is invoked, execute the following steps:

### Step 1: Load Planner Agent Documentation
Read `Agents/Planner/AGENTS.md` to understand Planner agent scope and responsibilities.

### Step 2: Discover Available Workflows
Scan `Workflow/Planner/` directory for `.md` files and extract metadata:
- Use `find_file_by_name` with pattern `*.md` in `Workflow/Planner/`
- For each file found, read the first 10 lines to extract metadata
- Look for workflow name and description in file headers

### Step 3: Present Workflow Selection
Present discovered workflows to user using `ask_user_question`:
- Include "Close" option to exit workflow discovery
- List all discovered workflows with their descriptions

### Step 4: Execute Selected Workflow
When user selects a workflow:
- Load the selected workflow file from `Workflow/Planner/`
- Read the full workflow content
- Immediately execute the workflow's defined steps and gates as specified in the workflow file
- User selection is the execution signal - no additional confirmation needed

## Workflow File Format
Each workflow file in `Workflow/Planner/` should:
- Define its own steps and procedures
- Include its own gate enforcement logic
- Follow the naming convention `{Agent}_{Workflow_Name}.md`
- Include metadata header (name, description) for discovery

## Close Workflow
To exit the Planner workflow discovery, use the global `close` skill.