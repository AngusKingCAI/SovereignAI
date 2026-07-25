---
name: close
description: Close current agent session and return to Architect as default agent
---

# Close Agent Session

## Purpose
Close the current agent session and return to Architect as the default agent for the next session.

## Actions

1. **Read current agent configuration** from `.devin/agent_config.json`
2. **Update configuration** to set `current_agent` to "Architect"
3. **Update timestamp** and increment session count
4. **Log session closure** to appropriate agent log file
5. **Get Architect workflows** by calling skill.py script
6. **Present workflow selection menu** using ask_user_question for Architect workflows
7. **Load selected Architect workflow** and initiate it
8. **Provide confirmation** to user

## Implementation Instructions

When this skill is invoked:

1. Call the skill.py script to close the session and get Architect workflows:
   ```
   python .devin/skills/close/skill.py
   ```

2. Parse the JSON output to get the list of Architect workflows

3. Use ask_user_question to present the workflow selection menu with numbered choices formatted like:
   ```
   Which Architect workflow would you like to load?

   1. Architect_General_Workflow: General workflow for Architect agent
   2. Another_Workflow: Description of another workflow
   ```

4. After user selects a workflow, load the workflow file from `Workflow/Architect/{selected_workflow}.md`

5. Read and initiate the selected workflow as specified in the workflow file

## Configuration Update

Update `.devin/agent_config.json`:
```json
{
  "default_agent": "Architect",
  "current_agent": "Architect",
  "last_updated": "<current_timestamp>",
  "session_count": <incremented_count>
}
```

## Session Logging

Log closure message to `Logs/{CurrentAgent}/{timestamp}.md`:
```
## Session End
- Agent: {CurrentAgent}
- Timestamp: {current_timestamp}
- Reason: User invoked /close
- Next Agent: Architect (default)
```

## Confirmation

Provide user confirmation:
```
Session closed. Current agent reset to Architect (default).
```

Then present Architect workflow selection menu:
```
Which Architect workflow would you like to load?

1. Architect_General_Workflow: General workflow for Architect agent
2. Another_Workflow: Description of another workflow
```

After user selects a workflow, load the workflow file from `Workflow/Architect/` and initiate it.

## Always Returns to Architect

Per project requirements, /close always returns to Architect as the default agent, regardless of which agent was active.