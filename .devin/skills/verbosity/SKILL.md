---
name: verbosity
description: Control the output verbosity of SovereignAI governance hooks
argument-hint: "[level]"
triggers:
  - user
allowed-tools:
  - read
  - write
  - exec
---

# Verbosity Control Skill

## Purpose
Control the output verbosity of SovereignAI governance hooks to manage chat noise during operations.

## Verbosity Levels

### quiet
- Only show critical errors and security violations
- Minimal chat output
- All operations still execute normally
- Best for normal development work

### minimal  
- Show pass/fail results for hooks
- Show security violations and critical failures
- Brief status messages
- Good balance of visibility and noise

### normal (default)
- Show all hook operations with status
- Display validation results
- Show both successes and failures
- Full transparency of hook behavior

### verbose
- Show detailed hook execution information
- Display validation steps and intermediate results
- Comprehensive debugging information
- Best for troubleshooting hook issues

## Skill Execution

When this skill is invoked with a verbosity level:

### Step 1: Set Verbosity Level
- Write the current verbosity level to `.devin/verbosity.json`
- File structure: `{"verbosity": "level", "timestamp": "ISO-8601"}`
- If no level specified, show current level and available options

### Step 2: Display Confirmation
- Show the current verbosity level
- Display how hooks will behave with this setting
- Confirm the change is active for the current session

### Step 3: Hook Integration
- All hooks read `.devin/verbosity.json` on execution
- Hooks adjust their print() statements based on verbosity level
- Changes take effect immediately for subsequent hook executions

## Usage Examples

### Set verbosity to quiet
```
/Verbosity quiet
```
Result: Hooks only show critical errors

### Set verbosity to minimal  
```
/Verbosity minimal
```
Result: Hooks show pass/fail results only

### Set verbosity to normal
```
/Verbosity normal
```
Result: Full hook output (default behavior)

### Set verbosity to verbose
```
/Verbosity verbose
```
Result: Detailed hook execution information

### Check current verbosity
```
/Verbosity
```
Result: Display current verbosity level and options

## Verbosity Level Reference

| Level | Success Messages | Failure Messages | Debug Info | Use Case |
|-------|----------------|-----------------|------------|----------|
| quiet | No | Yes | No | Normal development, minimal noise |
| minimal | No | Yes | No | Balanced visibility |
| normal | Yes | Yes | No | Full transparency (default) |
| verbose | Yes | Yes | Yes | Troubleshooting, debugging |

## Technical Implementation

Hooks read verbosity configuration using this pattern:

```python
def get_verbosity():
    """Get current verbosity level from skill configuration."""
    verbosity_file = Path(".devin/verbosity.json")
    if verbosity_file.exists():
        with open(verbosity_file) as f:
            config = json.load(f)
            return config.get("verbosity", "normal")
    return "normal"  # Default verbosity

def should_print(verbosity, message_type):
    """Determine if message should be printed based on verbosity."""
    if verbosity == "quiet":
        return message_type == "error"
    elif verbosity == "minimal":
        return message_type in ["error", "failure"]
    elif verbosity == "normal":
        return message_type in ["error", "failure", "success"]
    elif verbosity == "verbose":
        return True  # Print everything
    return True  # Default to showing everything
```

## File Changes

This skill creates/updates:
- `.devin/verbosity.json` - Current verbosity setting
- File format: `{"verbosity": "level", "timestamp": "2026-07-24T12:00:00Z"}`

## Integration with Hooks

All governance hooks will be updated to:
1. Read current verbosity from `.devin/verbosity.json`
2. Conditionally print output based on verbosity level
3. Always print critical errors regardless of verbosity
4. Respect user's preference for chat noise level

## Notes

- Verbosity changes take effect immediately for subsequent hook executions
- Setting persists for the current session only
- Default verbosity is "normal" if not specified
- Hooks always log to their respective log files regardless of verbosity
- Critical security violations always show regardless of verbosity level
