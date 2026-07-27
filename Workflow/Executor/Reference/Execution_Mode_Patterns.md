# Executor Execution Mode When-to-Use Scenarios

**Purpose**: Executor-specific when-to-use scenarios for execution mode selection.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Execution_Mode_Patterns.md for universal execution mode patterns including:
- Universal execution mode definitions (Manual, Auto, Complete)
- Universal execution mode handling patterns
- Universal failure handling patterns
- Universal retry logic with exponential backoff
- Universal execution mode tracking
- Universal usage guidelines

## Executor Execution Mode When-to-Use Scenarios

### Manual Mode When to Use
- High-risk plan steps
- Novel or experimental implementations
- When user wants close control over plan execution
- Complex implementation requirements
- Code changes affecting core functionality
- Security-critical implementation steps

### Auto Mode When to Use
- Standard plan execution tasks
- Well-understood implementation patterns
- When user wants some automation with safety
- Medium-risk implementation steps
- Routine function implementations
- Well-documented code changes

### Complete Mode When to Use
- Low-risk, routine implementation tasks
- Experimental or exploratory implementation work
- When user wants maximum automation
- Plan steps where failures are acceptable
- Non-critical utility functions
- Testing and debugging workflows