---
name: architect
description: Load Architect workflows and provide workflow selection
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

# Architect Workflow Discovery Skill

## Purpose
Load Architect agent documentation and provide workflow selection from Workflow/Architect/ directory.

## Skill Execution
When this skill is invoked, execute the following steps:

### Step 1: Load Architect Agent Documentation
Read `Agents/Architect/AGENTS.md` to understand Architect agent scope and responsibilities.

### Step 2: Discover Available Workflows
Scan `Workflow/Architect/` directory for `.md` files and extract metadata:
- Use `find_file_by_name` with pattern `*.md` in `Workflow/Architect/`
- For each file found, read the first 10 lines to extract metadata
- Look for workflow name and description in file headers

### Step 3: Present Workflow Selection
Present discovered workflows to user using `ask_user_question`:
- Include "Close" option to exit workflow discovery
- List all discovered workflows with their descriptions

### Step 4: Load Selected Workflow
When user selects a workflow:
- Load the selected workflow file from `Workflow/Architect/`
- Read the full workflow content
- Present the workflow steps to the user

### Step 5: Execute Workflow
Follow the workflow's defined steps and gates as specified in the workflow file.

## Workflow File Format
Each workflow file in `Workflow/Architect/` should:
- Define its own steps and procedures
- Include its own gate enforcement logic
- Follow the naming convention `{Agent}_{Workflow_Name}.md`
- Include metadata header (name, description) for discovery

## Close Workflow
To exit the Architect workflow discovery, use the global `close` skill.