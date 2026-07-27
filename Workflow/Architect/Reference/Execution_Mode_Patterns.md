# Architect Execution Mode When-to-Use Scenarios

**Purpose**: Architect-specific when-to-use scenarios for execution mode selection.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Execution_Mode_Patterns.md for universal execution mode patterns including:
- Universal execution mode definitions (Manual, Auto, Complete)
- Universal execution mode handling patterns
- Universal failure handling patterns
- Universal retry logic with exponential backoff
- Universal execution mode tracking
- Universal usage guidelines

## Architect Execution Mode When-to-Use Scenarios

### Manual Mode When to Use
- High-risk architectural decisions
- Novel or experimental approaches
- When user wants close control
- Complex governance requirements
- Infrastructure changes affecting system boundaries
- Security-critical architectural modifications

### Auto Mode When to Use
- Standard architectural tasks
- Well-understood patterns
- When user wants some automation with safety
- Medium-risk decisions
- Routine infrastructure updates
- Documented architectural improvements

### Complete Mode When to Use
- Low-risk, routine tasks
- Experimental or exploratory work
- When user wants maximum automation
- Tasks where failures are acceptable
- Non-critical documentation updates
- Testing and validation workflows