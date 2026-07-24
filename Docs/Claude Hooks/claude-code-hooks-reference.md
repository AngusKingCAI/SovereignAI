# Claude Code Hooks Reference

> Reference for Claude Code hook events, configuration schema, JSON input/output formats, exit codes, async hooks, HTTP hooks, prompt hooks, and MCP tool hooks.

<Tip>
  For a quickstart guide with examples, see [Automate actions with hooks](/docs/en/hooks-guide).
</Tip>

Hooks are user-defined shell commands, HTTP endpoints, or LLM prompts that execute automatically at specific points in Claude Code's lifecycle. Use this reference to look up event schemas, configuration options, JSON input/output formats, and advanced features like async hooks, HTTP hooks, and MCP tool hooks. If you're setting up hooks for the first time, start with the [guide](/docs/en/hooks-guide) instead.

## Hook lifecycle

Hooks fire at specific points during a Claude Code session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision.

Events fall into three cadences:

* once per session: `SessionStart` and `SessionEnd`
* once per turn: `UserPromptSubmit`, `Stop`, and `StopFailure`
* on every tool call inside the agentic loop: `PreToolUse` and `PostToolUse`, except [`EndConversation`](/docs/en/tools-reference#endconversation-tool-behavior) calls, which skip both

The table below summarizes when each event fires. The [Hook events](#hook-events) section documents the full input schema and decision control options for each one.

| Event                 | When it fires                                                                                                                                          |
| :-------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SessionStart`        | When a session begins or resumes                                                                                                                       |
| `Setup`               | When you start Claude Code with `--init-only`, or with `--init` or `--maintenance` in `-p` mode. For one-time preparation in CI or scripts             |
| `UserPromptSubmit`    | When you submit a prompt, before Claude processes it                                                                                                   |
| `UserPromptExpansion` | When a user-typed command expands into a prompt, before it reaches Claude. Can block the expansion                                                     |
| `PreToolUse`          | Before a tool call executes. Can block it                                                                                                              |
| `PermissionRequest`   | When a permission dialog appears                                                                                                                       |
| `PermissionDenied`    | When a tool call is denied by the auto mode classifier. Return `{retry: true}` to tell the model it may retry the denied tool call                     |
| `PostToolUse`         | After a tool call succeeds                                                                                                                             |
| `PostToolUseFailure`  | After a tool call fails                                                                                                                                |
| `PostToolBatch`       | After a full batch of parallel tool calls resolves, before the next model call                                                                         |
| `Notification`        | When Claude Code sends a notification                                                                                                                  |
| `MessageDisplay`      | While assistant message text is displayed                                                                                                              |
| `SubagentStart`       | When a subagent is spawned                                                                                                                             |
| `SubagentStop`        | When a subagent finishes                                                                                                                               |
| `TaskCreated`         | When a task is being created via `TaskCreate`                                                                                                          |
| `TaskCompleted`       | When a task is being marked as completed                                                                                                               |
| `Stop`                | When Claude finishes responding                                                                                                                        |
| `StopFailure`         | When the turn ends due to an API error. Output and exit code are ignored                                                                               |
| `TeammateIdle`        | When an [agent team](/docs/en/agent-teams) teammate is about to go idle                                                                                     |
| `InstructionsLoaded`  | When a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session         |
| `ConfigChange`        | When a configuration file changes during a session                                                                                                     |
| `CwdChanged`          | When the working directory changes, for example when Claude executes a `cd` command. Useful for reactive environment management with tools like direnv |
| `FileChanged`         | When a watched file changes on disk. The `matcher` field specifies which filenames to watch                                                            |
| `WorktreeCreate`      | When a worktree is being created via `--worktree`, `isolation: "worktree"`, or for a background session. Replaces default git behavior                 |
| `WorktreeRemove`      | When a worktree is being removed at session exit, when a subagent finishes, or when you delete a background session                                    |
| `PreCompact`          | Before context compaction                                                                                                                              |
| `PostCompact`         | After context compaction completes                                                                                                                     |
| `Elicitation`         | When an MCP server requests user input during a tool call                                                                                              |
| `ElicitationResult`   | After a user responds to an MCP elicitation, before the response is sent back to the server                                                            |
| `SessionEnd`          | When a session terminates                                                                                                                              |

### How a hook resolves

To see how these pieces fit together, consider this `PreToolUse` hook that blocks destructive shell commands. The `matcher` narrows to Bash tool calls and the `if` condition narrows further to Bash subcommands matching `rm *`, so `block-rm.sh` only spawns when both filters match:

```json theme={null}
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

The script reads the JSON input from stdin, extracts the command, and returns a `permissionDecision` of `"deny"` if it contains `rm -rf`:

```bash theme={null}
#!/bin/bash
# .claude/hooks/block-rm.sh
COMMAND=$(jq -r '.tool_input.command')

if echo "$COMMAND" | grep -q 'rm -rf'; then
  jq -n '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: "Destructive command blocked by hook"
    }
  }'
else
  exit 0  # no decision; normal permission flow applies
fi
```

This script and the Bash examples on this page that parse JSON input use `jq`, so install `jq` and make sure it is on your `PATH` before trying them.

Now let's walk through each step:

1. **Event fires**: Claude is about to call the Bash tool with a command
2. **Matcher check**: The `"Bash"` matcher matches the tool name
3. **If condition**: The `Bash(rm *)` permission rule syntax checks if the command contains `rm` followed by anything
4. **Hook handler spawns**: `block-rm.sh` runs with the event JSON on stdin
5. **Decision returns**: The script returns `{ permissionDecision: "deny" }` to block the operation

The hook handler can return a decision object to control what happens next:

| Decision field         | Effect                                                                      |
| ---------------------- | --------------------------------------------------------------------------- |
| `permissionDecision`   | `"allow"` or `"deny"` — overrides the normal permission flow                 |
| `permissionDecisionReason` | Text shown to the user explaining the decision                              |
| `additionalContext`    | Text injected into the conversation                                          |
| `updatedInput`         | Object merged into the tool's arguments before execution (PreToolUse only)  |

## Hook locations

Hooks are defined in JSON settings files at three levels:

| Level          | Path                                  | Scope                                      |
| -------------- | ------------------------------------- | ------------------------------------------ |
| Project        | `.claude/settings.json`               | Shared via git, applies to this project    |
| User           | `~/.claude/settings.json`             | Applies to all your projects              |
| Local          | `.claude/settings.local.json`        | Gitignored, overrides project/user hooks   |
| Plugin         | `.claude/plugins/<name>/hooks.json`  | Bundled with a plugin                     |

Project hooks are committed to git and shared with your team. User hooks apply across all your projects and are useful for personal preferences. Local hooks override both and stay out of version control.

The hooks browser at `/hooks` shows all loaded hooks and their source files.

## Matcher patterns

Matcher patterns filter when a hook runs. The syntax depends on the event type:

### Tool name matchers

For `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, and tool-related events, matchers are evaluated against the tool name:

| Pattern        | Matches                              |
| -------------- | ------------------------------------ |
| `Bash`         | Only the Bash tool                   |
| `Edit|Write`    | Edit or Write tools                  |
| `*`            | All tools                            |
| `^mcp__.*`     | All MCP tools                        |
| `^mcp__github__.*` | All tools from the github MCP server |

Matchers containing only letters, digits, underscores, and pipes are treated as simple lists. Any other characters (including `*`, `^`, `.`) trigger regex evaluation.

### Event-specific matchers

Some events have special matcher semantics:

| Event          | Matcher target                      |
| -------------- | ----------------------------------- |
| `Notification` | Notification type (e.g., `permission_prompt`, `idle_prompt`) |
| `FileChanged`  | Filename pattern to watch           |
| `SessionStart` | Session source (`startup`, `resume`, `clear`) |
| `Setup`        | Setup mode (`init-only`, `init`, `maintenance`) |

### Handler-level `if` conditions

Inside a hook handler, the `if` field uses permission rule syntax to inspect tool arguments:

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

This combines with the matcher: the hook only runs for Bash tool calls where the command matches `rm -rf *`.

## Hook handler fields

Each object in the inner `hooks` array is a hook handler: the shell command, HTTP endpoint, MCP tool, prompt, or agent that runs when the matcher matches. There are five types:

### Command hooks (`type: "command"`)

Run a shell command. The event's JSON input is passed on stdin, and the handler communicates results through exit codes and stdout.

```json theme={null}
{
  "type": "command",
  "command": "./hooks/my-script.sh",
  "args": [],
  "timeout": 10,
  "if": "Bash(rm *)"
}
```

| Field    | Description                                                                 |
| -------- | --------------------------------------------------------------------------- |
| `command` | Shell command to execute                                                    |
| `args`    | Array of additional arguments (rarely needed)                                |
| `timeout` | Maximum seconds to wait before terminating (default: 30)                     |
| `if`      | Permission rule condition to further filter when the handler runs           |

### HTTP hooks (`type: "http"`)

Send the event's JSON input as an HTTP POST request to a URL. The endpoint communicates results back through the response body using the same JSON output format as command hooks.

```json theme={null}
{
  "type": "http",
  "url": "https://api.example.com/hooks/tool-use",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  },
  "timeout": 5
}
```

| Field     | Description                                                    |
| --------- | -------------------------------------------------------------- |
| `url`     | HTTP endpoint to POST the event JSON to                        |
| `headers` | Object of HTTP headers (supports environment variable expansion) |
| `timeout` | Maximum seconds to wait for the response (default: 30)         |

### MCP tool hooks (`type: "mcpTool"`)

Call a tool on a connected MCP server instead of running a local script.

```json theme={null}
{
  "type": "mcpTool",
  "serverName": "my-hooks-server",
  "toolName": "validate_tool_use",
  "timeout": 10
}
```

| Field        | Description                                  |
| ------------ | -------------------------------------------- |
| `serverName` | MCP server name as configured in settings    |
| `toolName`   | Tool name to call on that server             |
| `timeout`    | Maximum seconds to wait for the tool response |

### Prompt hooks (`type: "prompt"`)

Send a text prompt to a fast Claude model (Haiku by default) for single-turn evaluation. The model returns an `ok: true` or `ok: false` decision as JSON.

```json theme={null}
{
  "type": "prompt",
  "prompt": "Does this tool call look safe? Respond with {\"ok\": true} or {\"ok\": false}.",
  "model": "claude-3-5-haiku-20241022"
}
```

| Field   | Description                                                           |
| ------ | --------------------------------------------------------------------- |
| `prompt` | Text prompt to send to the model                                      |
| `model`  | Model to use (defaults to Haiku; can use any available Claude model) |

### Agent hooks (`type: "agent"`)

Spawn a sub-agent with access to tools like Read and Grep for multi-turn codebase verification.

```json theme={null}
{
  "type": "agent",
  "prompt": "Review this code change for security issues.",
  "tools": ["read", "grep"],
  "timeout": 30
}
```

| Field   | Description                                                  |
| ------ | ------------------------------------------------------------ |
| `prompt` | Instructions for the sub-agent                               |
| `tools`  | Array of tools the sub-agent can access (default: all tools)  |
| `timeout` | Maximum seconds to wait for the agent to finish (default: 120) |

## Hook events

This section documents the full input schema and decision control options for each hook event.

### SessionStart

Fires when a session begins or resumes (including after compaction). Use this for one-time initialization, loading external state, or injecting session-wide context.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "SessionStart",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "source": "startup"  // "startup", "resume", or "clear"
}
```

**Decision control:** Can inject `additionalContext` into the conversation.

**Example:** Inject project-specific context at session start

```json theme={null}
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "./hooks/inject-context.sh"
          }
        ]
      }
    ]
  }
}
```

### Setup

Fires when you start Claude Code with `--init-only`, or with `--init` or `--maintenance` in `-p` mode. Use this for one-time preparation in CI or scripts.

**Input schema:** Same as SessionStart, with `source` indicating the setup mode.

**Decision control:** Can inject `additionalContext`.

### UserPromptSubmit

Fires when you submit a prompt, before Claude processes it. Use this to validate prompts, inject additional context, or log user input.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "UserPromptSubmit",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "prompt": "the user's prompt text"
}
```

**Decision control:** Can inject `additionalContext` or block with exit code 2.

### UserPromptExpansion

Fires when a user-typed command expands into a prompt, before it reaches Claude. This includes slash commands and skill invocations. Can block the expansion.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "UserPromptExpansion",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "expanded_prompt": "the expanded prompt text",
  "original_input": "the user's original command"
}
```

**Decision control:** Can block with exit code 2 or inject `additionalContext`.

### PreToolUse

Fires before a tool call executes. Use this to block dangerous operations, modify tool inputs, or add validation.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PreToolUse",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "tool_name": "Bash",
  "tool_use_id": "...",
  "tool_input": {
    // tool-specific arguments
  }
}
```

**Decision control:** Can return `permissionDecision` to allow/deny, `updatedInput` to modify arguments, or `additionalContext`.

### PermissionRequest

Fires when a permission dialog is about to be shown. Use this to auto-approve safe operations or implement custom approval logic.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PermissionRequest",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "tool_name": "Bash",
  "tool_use_id": "...",
  "tool_input": {
    // tool-specific arguments
  }
}
```

**Decision control:** Can return `permissionDecision` to allow/deny without showing the dialog.

### PermissionDenied

Fires when a tool call is denied by the auto mode classifier. Return `{retry: true}` to tell the model it may retry the denied tool call.

**Input schema:** Same as PermissionRequest.

**Decision control:** Can return `{retry: true}` to allow a retry.

### PostToolUse

Fires after a tool call succeeds. Use this for logging, triggering follow-up actions, or running formatters.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PostToolUse",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "tool_name": "Bash",
  "tool_use_id": "...",
  "tool_input": {
    // tool-specific arguments
  },
  "tool_response": {
    // tool-specific response
  }
}
```

**Decision control:** Can inject `additionalContext`.

### PostToolUseFailure

Fires after a tool call fails. Use this for error handling, logging, or recovery logic.

**Input schema:** Same as PostToolUse, with `tool_response` containing error information.

**Decision control:** Can inject `additionalContext`.

### PostToolBatch

Fires after a full batch of parallel tool calls resolves, before the next model call. Use this to inject context once for the whole batch rather than per-tool.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PostToolBatch",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "batch_results": [
    {
      "tool_name": "Bash",
      "tool_use_id": "...",
      "tool_input": {...},
      "tool_response": {...}
    },
    // ... more results
  ]
}
```

**Decision control:** Can inject `additionalContext`.

### Notification

Fires when Claude Code sends a notification. Use this for custom notification handling or integration with external systems.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "Notification",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "notification_type": "permission_prompt",  // or "idle_prompt", "auth_success", etc.
  "message": "notification text"
}
```

**Decision control:** None (display-only event).

### MessageDisplay

Fires while assistant message text is displayed. Use this to redact or reformat displayed text without changing the transcript.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "MessageDisplay",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "message_text": "the full message text"
}
```

**Decision control:** Can return `updatedMessage` to change what's displayed.

### SubagentStart

Fires when a subagent is spawned. Use this for logging or tracking subagent activity.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "SubagentStart",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "agent_id": "...",
  "agent_type": "planner"  // or other agent type
}
```

**Decision control:** Can inject `additionalContext`.

### SubagentStop

Fires when a subagent finishes. Use this for cleanup or logging subagent results.

**Input schema:** Same as SubagentStart, plus result information.

**Decision control:** Can inject `additionalContext`.

### TaskCreated

Fires when a task is being created via `TaskCreate`. Use this for task tracking or integrations.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "TaskCreated",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "task_id": "...",
  "task_content": "the task description"
}
```

**Decision control:** Can inject `additionalContext`.

### TaskCompleted

Fires when a task is being marked as completed. Use this for task tracking or triggering follow-up actions.

**Input schema:** Same as TaskCreated.

**Decision control:** Can inject `additionalContext`.

### Stop

Fires when Claude finishes responding. Use this for cleanup, state management, or preventing premature stopping.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "Stop",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "stop_hook_active": false
}
```

**Decision control:** Can block with exit code 2 or inject `additionalContext`.

### StopFailure

Fires when the turn ends due to an API error instead of a normal stop. Output and exit code are ignored.

**Input schema:** Same as Stop, plus error information.

**Decision control:** None (output ignored).

### TeammateIdle

Fires when an agent team teammate is about to go idle. Use this for team coordination or notifications.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "TeammateIdle",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "agent_id": "...",
  "agent_type": "..."
}
```

**Decision control:** Can inject `additionalContext`.

### InstructionsLoaded

Fires when a CLAUDE.md or `.claude/rules/*.md` file is loaded into context. Fires at session start and when files are lazily loaded during a session.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "InstructionsLoaded",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "file_path": "/path/to/CLAUDE.md",
  "content": "the file content"
}
```

**Decision control:** Can inject `additionalContext`.

### ConfigChange

Fires when a configuration file changes during a session. Use this for reactive configuration management.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "ConfigChange",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "config_file": "/path/to/settings.json",
  "change_type": "modified"  // or "created", "deleted"
}
```

**Decision control:** Can inject `additionalContext`.

### CwdChanged

Fires when the working directory changes, for example when Claude executes a `cd` command. Useful for reactive environment management with tools like direnv.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "CwdChanged",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "old_cwd": "/old/path",
  "new_cwd": "/new/path"
}
```

**Decision control:** Can inject `additionalContext`.

### FileChanged

Fires when a watched file changes on disk. The `matcher` field specifies which filenames to watch.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "FileChanged",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "file_path": "/path/to/changed/file",
  "change_type": "modified"  // or "created", "deleted"
}
```

**Decision control:** Can inject `additionalContext`.

### WorktreeCreate

Fires when a worktree is being created via `--worktree`, `isolation: "worktree"`, or for a background session. Replaces default git behavior.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "WorktreeCreate",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "worktree_path": "/path/to/worktree"
}
```

**Decision control:** Can return custom worktree configuration.

### WorktreeRemove

Fires when a worktree is being removed at session exit, when a subagent finishes, or when you delete a background session.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "WorktreeRemove",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "worktree_path": "/path/to/worktree"
}
```

**Decision control:** None (cleanup notification).

### PreCompact

Fires before context compaction. Use this to prepare for compaction or save state.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PreCompact",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project"
}
```

**Decision control:** Can inject `additionalContext`.

### PostCompact

Fires after context compaction completes. Use this to restore state or re-inject context that may have been lost.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "PostCompact",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "summary": "compaction summary text"
}
```

**Decision control:** Can inject `additionalContext`.

### Elicitation

Fires when an MCP server requests user input during a tool call.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "Elicitation",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "mcp_server_name": "github",
  "elicitation_id": "...",
  " elicitation_data": {...}
}
```

**Decision control:** Can return elicitation responses.

### ElicitationResult

Fires after a user responds to an MCP elicitation, before the response is sent back to the server.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "ElicitationResult",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "mcp_server_name": "github",
  "elicitation_id": "...",
  "user_response": "the user's response"
}
```

**Decision control:** Can modify the response before it's sent to the server.

### SessionEnd

Fires when a session terminates. Use this for cleanup, final logging, or resource management.

**Input schema:**

```json theme={null}
{
  "hook_event_name": "SessionEnd",
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "reason": "user_exited"  // or other reason
}
```

**Decision control:** None (session is ending).

## Exit codes

Command hooks communicate results through exit codes:

| Exit code | Meaning                           | Effect                                                  |
| -------- | --------------------------------- | ------------------------------------------------------- |
| 0        | Success                           | Action proceeds normally                               |
| 2        | Block                             | Action is blocked (for blocking events)                 |
| Other     | Error                             | Action proceeds normally, error is logged              |

For events that support blocking (PreToolUse, UserPromptSubmit, UserPromptExpansion, Stop), exit code 2 blocks the action. For other events, exit code 2 is treated as an error but doesn't change behavior.

## JSON output format

Command hooks can return a JSON object on stdout to control behavior:

```json theme={null}
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked",
    "additionalContext": "Remember: deploys require approval",
    "updatedInput": {
      "command": "safe command"
    },
    "updatedMessage": "redacted message"
  }
}
```

| Field                      | When it applies                      | Effect                                                      |
| -------------------------- | ----------------------------------- | ----------------------------------------------------------- |
| `permissionDecision`       | PreToolUse, PermissionRequest       | Override permission decision ("allow" or "deny")            |
| `permissionDecisionReason` | PreToolUse, PermissionRequest       | Text shown to user explaining the decision                 |
| `additionalContext`        | Most events                         | Inject text into the conversation                           |
| `updatedInput`             | PreToolUse                          | Modify tool arguments before execution                      |
| `updatedMessage`          | MessageDisplay                      | Change what message text is displayed                       |
| `retry`                    | PermissionDenied                    | Allow model to retry denied tool call                       |

## Async hooks

Some events (`FileChanged`, `CwdChanged`, `ConfigChange`, `Notification`, `InstructionsLoaded`) fire asynchronously, outside the main request-response loop. These hooks run in the background and don't block the main flow.

Async hooks cannot return decisions that affect the main flow. They're useful for logging, triggering external actions, or updating state.

## Environment variables

Hook handlers have access to these environment variables:

| Variable                | Description                                |
| ----------------------- | ------------------------------------------ |
| `CLAUDE_PROJECT_DIR`    | Absolute path to the project root          |
| `CLAUDE_SESSION_ID`     | Current session ID                         |
| `CLAUDE_TRANSCRIPT_PATH`| Path to the session transcript file       |

## Debugging hooks

Use the `/hooks` command to see all loaded hooks and their configuration. To debug a specific hook:

1. Add `show_output: true` to see the hook's stdout/stderr
2. Add logging to your script to trace execution
3. Test with a simple script that logs the input JSON
4. Check the hook browser to confirm the hook is registered

Example debugging hook:

```bash theme={null}
#!/bin/bash
# Debug hook that logs everything
INPUT=$(cat)
echo "Hook triggered:" >&2
echo "$INPUT" >&2
exit 0
```
