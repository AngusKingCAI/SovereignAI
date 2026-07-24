# Automate actions with hooks

> Run shell commands automatically when Claude Code edits files, finishes tasks, or needs input. Format code, send notifications, validate commands, and enforce project rules.

Hooks are user-defined shell commands that execute at specific points in Claude Code's lifecycle. They provide deterministic control over Claude Code's behavior, ensuring certain actions always happen rather than relying on the LLM to choose to run them. Use hooks to enforce project rules, automate repetitive tasks, and integrate Claude Code with your existing tools.

For decisions that require judgment rather than deterministic rules, you can also use [prompt-based hooks](#prompt-based-hooks) or [agent-based hooks](#agent-based-hooks) that use a Claude model to evaluate conditions.

For other ways to extend Claude Code, see [skills](/docs/en/skills) for giving Claude additional instructions and executable commands, [subagents](/docs/en/sub-agents) for running tasks in isolated contexts, and [plugins](/docs/en/plugins) for packaging extensions to share across projects.

<Tip>
  This guide covers common use cases and how to get started. For full event schemas, JSON input/output formats, and advanced features like async hooks and MCP tool hooks, see the [Hooks reference](/docs/en/hooks).
</Tip>

## Set up your first hook

To create a hook, add a `hooks` block to a [settings file](#configure-hook-location). This walkthrough creates a desktop notification hook, so you get alerted whenever Claude is waiting for your input instead of watching the terminal.

<Steps>
  <Step title="Add the hook to your settings">
    Open `~/.claude/settings.json` and add a `Notification` hook. If the file doesn't exist, create it. The example below uses `osascript` for macOS; see [Get notified when Claude needs input](#get-notified-when-claude-needs-input) for Linux and Windows commands.

    ```json theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
              }
            ]
          }
        ]
      }
    }
    ```

    If your settings file already has a `hooks` key, add `Notification` as a sibling of the existing event keys rather than replacing the whole object. Each event name is a key inside the single `hooks` object:

    ```json theme={null}
    {
      "hooks": {
        "PostToolUse": [
          {
            "matcher": "Edit|Write",
            "hooks": [{ "type": "command", "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write" }]
          }
        ],
        "Notification": [
          {
            "matcher": "",
            "hooks": [{ "type": "command", "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'" }]
          }
        ]
      }
    }
    ```

    You can also ask Claude to write the hook for you by describing what you want in the CLI.
  </Step>

  <Step title="Verify the configuration">
    Type `/hooks` to open the hooks browser. You'll see a list of all available hook events, with a count next to each event that has hooks configured. Select `Notification` to confirm your new hook appears in the list. Selecting the hook shows its details: the event, matcher, type, source file, and command.
  </Step>

  <Step title="Test the hook">
    Press `Esc` to return to the CLI. Ask Claude to do something that requires permission, then switch away from the terminal. You should receive a desktop notification.
  </Step>
</Steps>

<Tip>
  The `/hooks` menu is read-only. To add, modify, or remove hooks, edit your settings JSON directly or ask Claude to make the change.
</Tip>

## What you can automate

Hooks let you run code at key points in Claude Code's lifecycle: format files after edits, block commands before they execute, send notifications when Claude needs input, inject context at session start, and more. For the full list of hook events, see the [Hooks reference](/docs/en/hooks#hook-lifecycle).

Each example includes a ready-to-use configuration block that you add to a [settings file](#configure-hook-location).

For a production example of hooks that run a separate model review and feed findings back into the session, see [how the `security-guidance` plugin integrates with Claude Code](/docs/en/security-guidance#how-the-plugin-integrates-with-claude-code).

### Get notified when Claude needs input

Get a desktop notification whenever Claude finishes working and needs your input, so you can switch to other tasks without checking the terminal.

This hook uses the `Notification` event, which fires when Claude is waiting for input or permission. Each tab below uses the platform's native notification command. Add this to `~/.claude/settings.json`:

<Tabs>
  <Tab title="macOS">
    ```json theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "osascript -e 'display notification \"Claude Code needs your attention\" with title \"Claude Code\"'"
              }
            ]
          }
        ]
      }
    }
    ```

    <Accordion title="If no notification appears">
      `osascript` routes notifications through the built-in Script Editor app. If Script Editor doesn't have notification permission, the command fails silently, and macOS won't prompt you to grant it. Run this in Terminal once to make Script Editor appear in your notification settings:

      ```bash theme={null}
      osascript -e 'display notification "test"'
      ```

      Nothing will appear yet. Open **System Settings > Notifications**, find **Script Editor** in the list, and turn on **Allow Notifications**. Run the command again to confirm the test notification appears.
    </Accordion>
  </Tab>

  <Tab title="Linux">
    ```json theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "notify-send 'Claude Code' 'Claude Code needs your attention'"
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>

  <Tab title="Windows (PowerShell)">
    ```json theme={null}
    {
      "hooks": {
        "Notification": [
          {
            "matcher": "",
            "hooks": [
              {
                "type": "command",
                "command": "powershell.exe -Command \"[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('Claude Code needs your attention', 'Claude Code')\""
              }
            ]
          }
        ]
      }
    }
    ```
  </Tab>
</Tabs>

The empty `matcher` fires on all notification types. To fire only on specific events, set it to one of these values:

| Matcher                | Fires when                                                                                               |
| :--------------------- | :------------------------------------------------------------------------------------------------------- |
| `permission_prompt`    | Claude needs you to approve a tool use                                                                   |
| `idle_prompt`          | Claude is done and waiting for your next prompt                                                          |
| `auth_success`         | Authentication completes                                                                                 |
| `elicitation_dialog`   | An MCP server opens an elicitation form                                                                  |
| `elicitation_complete` | An MCP elicitation form is submitted or dismissed                                                        |
| `elicitation_response` | An MCP elicitation response is sent back to the server                                                   |
| `agent_needs_input`    | A background session starts waiting on your input. Fires only while [agent view](/docs/en/agent-view) is open |
| `agent_completed`      | A background session finishes or fails. Fires only while [agent view](/docs/en/agent-view) is open            |

The `agent_needs_input` and `agent_completed` matchers require Claude Code v2.1.198 or later.

Type `/hooks` and select `Notification` to confirm the hook is registered. For the full event schema, see the [Notification reference](/docs/en/hooks#notification).

### Auto-format code after edits

Automatically run [Prettier](https://prettier.io/) on every file Claude edits, so formatting stays consistent without manual intervention.

This hook uses the `PostToolUse` event with an `Edit|Write` matcher, so it runs only after file-editing tools. The command extracts the edited file path with [`jq`](https://jqlang.org/) and passes it to Prettier. Add this to `.claude/settings.json` in your project root:

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "jq -r '.tool_input.file_path' | xargs npx prettier --write"
          }
        ]
      }
    ]
  }
}
```

On Claude Code v2.1.191 or later you can also write the matcher as `Edit,Write`, since `|` and `,` are interchangeable list separators for tool-name matchers on those versions.

<Note>
  The Bash examples on this page use `jq` for JSON parsing. Install it with `brew install jq` on macOS, `apt-get install jq` on Ubuntu/Debian, or `choco install jq` on Windows.
</Note>

### Block destructive commands

Prevent Claude from running dangerous commands like `rm -rf` by blocking them before execution.

This hook uses the `PreToolUse` event with a `Bash` matcher and an `if` condition to check for destructive patterns:

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm -rf *)",
            "command": ".claude/hooks/block-destructive.sh"
          }
        ]
      }
    ]
  }
}
```

Create the script `.claude/hooks/block-destructive.sh`:

```bash theme={null}
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0
fi
```

Make it executable: `chmod +x .claude/hooks/block-destructive.sh`

The script returns `{ permissionDecision: "deny" }` to block the command and shows the reason to Claude, which it can then communicate to you.

### Inject context at session start

Automatically inject project-specific context when a session begins, so Claude has the right information from the start.

This hook uses the `SessionStart` event:

```json theme={null}
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/inject-context.sh"
          }
        ]
      }
    ]
  }
}
```

Create the script `.claude/hooks/inject-context.sh`:

```bash theme={null}
#!/bin/bash
set -euo pipefail

# Read project-specific context from a file
if [ -f ".claude/session-context.md" ]; then
  CONTEXT=$(cat .claude/session-context.md)
  jq -n "{
    hookSpecificOutput: {
      hookEventName: \"SessionStart\",
      additionalContext: \"$CONTEXT\"
    }
  }"
else
  exit 0
fi
```

Create `.claude/session-context.md` with your project-specific information:

```markdown theme={null}
This project uses TypeScript with strict mode enabled.
- Run tests with `npm test`
- Build with `npm run build`
- Deploy to staging with `npm run deploy:staging`
- Main branch is protected, requires PR approval
```

### Log all tool calls

Create an audit trail of every tool call for compliance or debugging.

This hook uses the `PostToolUse` event with a wildcard matcher:

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/log-tool-call.sh"
          }
        ]
      }
    ]
  }
}
```

Create the script `.claude/hooks/log-tool-call.sh`:

```bash theme={null}
#!/bin/bash
set -euo pipefail

INPUT=$(cat)
TIMESTAMP=$(date -Iseconds)
LOG_FILE=".claude/tool-audit.log"

echo "[$TIMESTAMP] $INPUT" >> "$LOG_FILE"
exit 0
```

## Configure hook location

Hooks can be configured at three levels, each with different scope:

### Project-level hooks

**Location:** `.claude/settings.json` in your project root

**Scope:** Shared via git, applies to everyone who works on this project

**Use case:** Team-wide conventions like code formatting, testing requirements, or security policies

### User-level hooks

**Location:** `~/.claude/settings.json`

**Scope:** Applies to all your projects

**Use case:** Personal preferences like notification settings, custom aliases, or personal tooling

### Local hooks

**Location:** `.claude/settings.local.json`

**Scope:** Overrides project and user hooks, gitignored

**Use case:** Local overrides that shouldn't be committed, like experimental hooks or machine-specific configuration

## Hook types

### Command hooks

Run shell commands. These are the most common type and work well for most automation needs.

```json theme={null}
{
  "type": "command",
  "command": "./hooks/my-script.sh",
  "timeout": 10
}
```

### HTTP hooks

Send event data to an HTTP endpoint for external processing or integration with web services.

```json theme={null}
{
  "type": "http",
  "url": "https://api.example.com/hooks",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

### Prompt hooks

Use a Claude model to evaluate conditions that require judgment rather than pattern matching.

```json theme={null}
{
  "type": "prompt",
  "prompt": "Does this tool call look safe? Respond with {\"ok\": true} or {\"ok\": false}.",
  "model": "claude-3-5-haiku-20241022"
}
```

### Agent hooks

Spawn a sub-agent for multi-turn verification or complex analysis.

```json theme={null}
{
  "type": "agent",
  "prompt": "Review this code change for security issues.",
  "tools": ["read", "grep"],
  "timeout": 30
}
```

### MCP tool hooks

Call a tool on a connected MCP server.

```json theme={null}
{
  "type": "mcpTool",
  "serverName": "my-hooks-server",
  "toolName": "validate_tool_use"
}
```

## Advanced patterns

### Conditional hook execution

Use the `if` field with permission rule syntax to conditionally execute hooks based on tool arguments:

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm -rf *)",
            "command": "./hooks/block-destructive.sh"
          }
        ]
      }
    ]
  }
}
```

### Multiple hooks per event

You can define multiple hooks for the same event. They run in parallel when the matcher matches:

```json theme={null}
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/format-file.sh"
          },
          {
            "type": "command",
            "command": "./hooks/log-change.sh"
          }
        ]
      }
    ]
  }
}
```

### Matcher patterns

Use regex patterns for complex matching:

```json theme={null}
{
  "matcher": "^mcp__github__.*"  // All GitHub MCP tools
}
```

Simple patterns without special characters are treated as lists:

```json theme={null}
{
  "matcher": "Edit|Write|NotebookEdit"  // These three tools
}
```

## Troubleshooting

### Hook not firing

1. Check the hook is registered: Type `/hooks` and verify it appears in the list
2. Verify the matcher pattern matches the event you're expecting
3. Check the settings file location (project vs user vs local)
4. Ensure the script is executable (for command hooks)

### Script fails silently

1. Add `show_output: true` to see stdout/stderr
2. Check the script has proper shebang (`#!/bin/bash` or `#!/usr/bin/env python3`)
3. Test the script manually with sample input
4. Check file permissions

### Hook blocks too much

1. Refine the matcher pattern to be more specific
2. Add conditional logic with the `if` field
3. Add logging to understand what's being blocked
4. Consider using a prompt hook for more nuanced decisions

## Best practices

1. **Keep hooks fast**: Hooks run synchronously and can slow down Claude if they're slow. Aim for sub-second execution.
2. **Use specific matchers**: Avoid wildcard matchers (`*`) when possible to reduce unnecessary hook executions.
3. **Handle errors gracefully**: Use `set -euo pipefail` in bash scripts and proper error handling in other languages.
4. **Log appropriately**: Log what you need for debugging and compliance, but avoid logging sensitive information.
5. **Test thoroughly**: Test hooks with various scenarios before relying on them in production.
6. **Version control project hooks**: Commit `.claude/settings.json` to share team conventions.
7. **Keep local hooks local**: Use `.claude/settings.local.json` for machine-specific configuration that shouldn't be shared.
