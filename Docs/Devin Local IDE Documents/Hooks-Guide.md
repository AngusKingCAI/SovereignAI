# Devin CLI Hooks - Complete Guide

## Overview

Devin CLI hooks allow you to run custom logic in response to events in the agent's lifecycle. Hooks can enforce policies, add context, log actions, modify permissions, or integrate with external systems.

**Important**: Hooks ARE available in the free tier of Devin CLI. There is no paid restriction on hook functionality.

## When Hooks Fire

Hooks can respond to these lifecycle events:

| Event | When it fires | Use for |
|-------|---------------|---------|
| `PreToolUse` | Before a tool executes | Block dangerous commands, inject context, modify tool calls |
| `PostToolUse` | After a tool finishes | Log commands, validate outputs, trigger follow-up actions |
| `PermissionRequest` | When permission decision is needed | Auto-approve safe commands, implement custom approval logic |
| `UserPromptSubmit` | When user submits a message | Add context for certain requests, validate inputs |
| `Stop` | When agent wants to stop | Prevent stopping before required checks, add follow-up instructions |
| `SessionStart` | When a session begins | Run setup scripts, initialize environment, load context |
| `SessionEnd` | When a session ends | Cleanup, final logging, generate reports |

## Hook File Location

Devin CLI reads hooks from the following locations (all use the same JSON format):

### Project-Level (Recommended)
| Location | Description |
|----------|-------------|
| `.devin/hooks.v1.json` | Standalone hooks file (recommended) |
| `.devin/config.json` | `"hooks"` key in the config file |
| `.devin/config.local.json` | `"hooks"` key (local override, gitignored) |

### User-Level (Global)
| Location | Description |
|----------|-------------|
| `~/.config/devin/config.json` | `"hooks"` key in user config |
| `%APPDATA%\devin\config.json` | Windows user config path |

### Claude Code Compatibility
| Location | Description |
|----------|-------------|
| `.claude/settings.json` | `"hooks"` key (Claude Code format) |
| `.claude/settings.local.json` | `"hooks"` key (Claude Code format) |

**Important**: In `.devin/hooks.v1.json`, the hooks object is the **entire file** (no wrapper key needed). In all other locations, hooks are nested under the `"hooks"` key.

## Correct Hook Format

### Working Format Structure

```json
{
  "EventName": [
    {
      "matcher": "pattern",
      "hooks": [
        {
          "type": "command",
          "command": "your command here",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### Key Components

1. **Event Name**: The lifecycle event (e.g., `PreToolUse`, `SessionStart`)
2. **Matcher**: Regex pattern to match tool names (optional, defaults to all)
3. **Hooks Array**: Array of hook definitions
4. **Type**: Either `"command"` or `"prompt"`
5. **Command**: Shell command to execute (for command type)
6. **Timeout**: Optional timeout in seconds (default varies by event)

### Matcher Patterns

| Matcher | Matches |
|---------|---------|
| `""` (empty) or omitted | All tool names for tool events |
| `"exec"` | Tool names containing `exec` |
| `"^exec$"` | Only the `exec` tool |
| `"^(exec|edit)$"` | Only `exec` or `edit` |
| `"^mcp__.*"` | All MCP tools |
| `"^mcp__github_.*"` | All tools from the `github` MCP server |
| `"*"` | All tools (using wildcard pattern) |

## Common Hook Mistakes

### ❌ Wrong Format (Won't Work)
```json
{
  "PreToolUse": {
    "command": "echo 'test'",
    "description": "Test hook"
  }
}
```

### ✅ Correct Format (Will Work)
```json
{
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'test'"
        }
      ]
    }
  ]
}
```

### Key Differences

1. **Array Structure**: Each event must have an array `[]` of hook objects
2. **Nested Hooks**: Each hook object has a `hooks` array containing the actual hook definitions
3. **Type Field**: Each hook definition must specify `type: "command"` or `type: "prompt"`
4. **Matcher Field**: Must be in the outer object, not in the hook definition

## Testing Your Hooks

### Step 1: Create Test Hook File

Create `.devin/hooks.v1.json` with this test configuration:

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "echo 'SessionStart hook triggered' > /tmp/hook-test.log"
        }
      ]
    }
  ],
  "PreToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'PreToolUse hook triggered' >> /tmp/hook-test.log"
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'PostToolUse exec hook triggered' >> /tmp/hook-test.log"
        }
      ]
    }
  ]
}
```

### Step 2: Test with Simple Command

```bash
devin -p "test hooks"
```

### Step 3: Check Log File

```bash
cat /tmp/hook-test.log
```

Expected output:
```
SessionStart hook triggered
PreToolUse hook triggered
PostToolUse exec hook triggered
```

### Step 4: Troubleshooting

If hooks don't trigger:

1. **Check file location**: Ensure `.devin/hooks.v1.json` is in project root
2. **Verify JSON format**: Use JSON validator to check syntax
3. **Check file permissions**: Ensure file is readable
4. **Update Devin CLI**: Run `devin update` to ensure latest version
5. **Use absolute paths**: Use full paths in hook commands

## Hook Examples

### Block Dangerous Commands

```json
{
  "PreToolUse": [
    {
      "matcher": "^exec$",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/block-dangerous-command.py",
          "timeout": 10
        }
      ]
    }
  ]
}
```

### Log All Tool Usage

```json
{
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/log-tool-usage.py",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### Auto-Approve Safe Commands

```json
{
  "PermissionRequest": [
    {
      "matcher": "^(read|grep)$",
      "hooks": [
        {
          "type": "command",
          "command": "echo 'auto-approve'",
          "timeout": 5
        }
      ]
    }
  ]
}
```

### Initialize Environment on Session Start

```json
{
  "SessionStart": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/init-environment.py",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### Generate Reports on Session End

```json
{
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/generate-session-report.py",
          "timeout": 60
        }
      ]
    }
  ]
}
```

## Exit Codes

Hook exit codes control behavior:

| Code | Meaning |
|------|---------|
| 0 | Success — hook continues normally |
| 2 | Block — action is denied |
| Other | Error — logged but doesn't block |

## Advanced Features

### Prompt-Based Hooks

You can use LLM prompts instead of shell commands:

```json
{
  "PreToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "Analyze this command for security risks. If dangerous, return exit code 2.",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### Multiple Hooks Per Event

You can define multiple hooks for the same event:

```json
{
  "PreToolUse": [
    {
      "matcher": "exec",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/check-1.py"
        },
        {
          "type": "command",
          "command": "python scripts/check-2.py"
        }
      ]
    }
  ]
}
```

### Multiple Event Matchers

You can match different tool patterns:

```json
{
  "PreToolUse": [
    {
      "matcher": "^exec$",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/check-exec.py"
        }
      ]
    },
    {
      "matcher": "^edit$",
      "hooks": [
        {
          "type": "command",
          "command": "python scripts/check-edit.py"
        }
      ]
    }
  ]
}
```

## Integration with SovereignAI

### Executor Workflow Hooks

For the SovereignAI Executor workflow, use hooks for:

```json
{
  "PreToolUse": [
    {
      "matcher": "^(edit|write)$",
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/check_manifest.py --file {file_path} --plan {plan_id}",
          "timeout": 10
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/append_trace.py --tool {tool_name} --plan {plan_id}",
          "timeout": 5
        }
      ]
    }
  ],
  "SessionEnd": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python Scripts/Governance/verify_attestation.py --plan {plan_id}",
          "timeout": 30
        }
      ]
    }
  ]
}
```

### Governance Variables

Hooks receive environment variables:
- `{file_path}`: Path of file being modified
- `{tool_name}`: Name of tool being invoked
- `{plan_id}`: Current plan identifier (if available)
- `{session_id}`: Unique session identifier

## Troubleshooting Guide

### Hooks Not Triggering

**Problem**: Hooks defined but not executing

**Solutions**:
1. Verify file location is `.devin/hooks.v1.json` in project root
2. Check JSON syntax with validator
3. Ensure hook commands have correct permissions
4. Test with simple echo command first
5. Check file encoding (should be UTF-8)

### Hook Commands Failing

**Problem**: Hook commands return errors

**Solutions**:
1. Use absolute paths in commands
2. Test commands manually in shell
3. Check script permissions (chmod +x)
4. Verify Python scripts have proper shebang
5. Check environment variables are available

### Hooks Blocking Legitimate Actions

**Problem**: Hooks blocking actions that should be allowed

**Solutions**:
1. Review hook logic and exit codes
2. Add logging to understand why blocking
3. Use more specific matchers
4. Implement whitelist logic in hook scripts
5. Test hooks with matcher patterns

### Performance Issues

**Problem**: Hooks slowing down execution

**Solutions**:
1. Add timeout limits to hooks
2. Optimize hook script performance
3. Use specific matchers to reduce hook frequency
4. Cache expensive operations
5. Consider using PostToolUse instead of PreToolUse where possible

## Best Practices

1. **Start Simple**: Begin with basic echo commands to verify hooks work
2. **Use Specific Matchers**: Don't use `*` matcher if you can be more specific
3. **Add Timeouts**: Always set reasonable timeout limits
4. **Handle Errors**: Make hook scripts robust and handle errors gracefully
5. **Log Everything**: Add comprehensive logging for debugging
6. **Test Regularly**: Test hooks after any changes
7. **Document Hooks**: Comment hook files to explain purpose
8. **Version Control**: Commit hook files to track changes
9. **Monitor Performance**: Watch for hooks that slow down execution
10. **Use Exit Codes**: Use proper exit codes (0 for success, 2 for block)

## Hook Version Compatibility

Devin CLI hooks are compatible with Claude Code hooks format. If you have existing Claude Code hooks in `.claude/` directories, they will work automatically when `read_config_from.claude` is enabled (default).

## Conclusion

Hooks are a powerful feature for enforcing governance and automation in Devin CLI. They work in both free and paid tiers, and with the correct format and structure, you can implement robust policy enforcement, logging, and automation for your development workflow.

The key to getting hooks working is:
1. Use the correct nested array structure
2. Always specify the `type` field
3. Use appropriate matchers for tool filtering
4. Test with simple commands first
5. Use absolute paths in hook commands

With these principles, you can successfully implement hooks for any governance or automation needs in your Devin CLI workflow.