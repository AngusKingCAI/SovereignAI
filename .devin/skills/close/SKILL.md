---
name: close
description: Close current workflow session and return to normal chat
triggers:
  - user
  - model
allowed-tools:
  - read
  - edit
  - write
---

# Close Workflow Skill

## Purpose
Close the current workflow session and return to normal chat mode.

## Steps

### 1. Find Current Workflow
- Check for active workflow indicators (conversation logs, trace files, etc.)
- Identify the currently active workflow session

### 2. Close the Workflow
- Update the relevant log file with session end time
- Mark the workflow as CLOSED
- Document closure reason

### 3. Return to Normal Chat
- Confirm closure to user
- Return to normal chat mode

## Usage
Trigger with: "close", "/close", "close workflow"