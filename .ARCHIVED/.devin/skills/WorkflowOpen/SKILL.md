---
name: WorkflowOpen
description: Dynamically loads agent-specific governance rules for the current agent
allowed-tools:
  - read
triggers:
  - user
  - model
---

# WorkflowOpen - Governance Rules Loader

Load the appropriate governance rules based on which agent is currently executing.

## Instructions

1. **Detect Current Agent**: Read the session state file to determine current agent:
   - Read: `Scripts/Logging/.session_state/session_state.json`
   - Get the `agent` field (contains: "architect", "planner", "executor", "researcher", or "reviewer")

2. **Load Agent-Specific Rules**: Based on the detected agent, load the corresponding rules file:
   - Read `.devin/rules/{agent}.md` (lowercase agent name)

3. **Load Universal Governance Files**: Always load these files:
   - `PRINCIPLES.md` (constitutional framework)
   - `Workflow/Workflow_Reference/Terminology_Glossary.md` (terminology definitions)

4. **Parse and Store**: Extract rule definitions and compliance requirements from the loaded files

5. **Report Status**: Print which agent rules were loaded and confirm governance context is ready

## Expected Output
Complete with a status message like: "Architect rules (.devin/rules/architect.md), constitutional principles, and terminology definitions loaded"