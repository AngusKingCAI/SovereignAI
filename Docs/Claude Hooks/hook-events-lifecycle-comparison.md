# Hook Events and the Agent Lifecycle

Before wiring anything up, it helps to know which events actually fire and when. The vocabulary is slightly different on each platform, but the lifecycle they describe is shared.

## The Shared Lifecycle

At the abstract level, every agent session moves through the same phases:

```
┌─────────────────────────────────────────────┐
│ Session starts                              │ ← SessionStart
├─────────────────────────────────────────────┤
│ Repeat for each turn:                       │
│   User submits a prompt                     │ ← UserPromptSubmit
│   Model reasons and may call tools          │
│     Before each tool call                   │ ← PreToolUse
│     After each tool call                    │ ← PostToolUse
│   Turn ends                                 │ ← Stop
├─────────────────────────────────────────────┤
│ Session ends                                │ ← SessionEnd
└─────────────────────────────────────────────┘
```

This is the shared mental model. The platforms in this course map onto these moments with different names, different configuration surfaces, and a few gaps or extra events.

## Events by Platform

### Claude Code

Claude Code has the richest event set of the four platforms. Every event uses `PascalCase` and is configured in `.claude/settings.json` (or inside a plugin's `hooks/hooks.json`).

**Core lifecycle events:**
- `SessionStart` — New session begins (fresh, resume, or compaction continuation).
- `InstructionsLoaded` — `CLAUDE.md` files have been loaded.
- `UserPromptSubmit` — User submitted a prompt, before the model sees it.
- `PreToolUse` — Before a tool call runs.
- `PermissionRequest` — Permission prompt about to be shown.
- `PermissionDenied` — A tool call was denied by the auto-mode classifier.
- `PostToolUse` — After a tool call returns.
- `PostToolUseFailure` — Tool call failed.
- `Stop` — Turn finished.
- `SessionEnd` — Session closed.

**Subagent and task events:**
- `SubagentStart`, `SubagentStop` — A delegated subagent starts or finishes.
- `TaskCreated`, `TaskCompleted` — The TodoWrite task list changes.

**Environment events:**
- `CwdChanged`, `FileChanged` — Working directory or a tracked file changed.
- `WorktreeCreate`, `WorktreeRemove` — Git worktree created or removed.
- `PreCompact`, `PostCompact` — Context compaction about to happen / just finished.
- `ConfigChange`, `Notification` — Settings changed; Claude raised a notification.

Matcher groups filter on event-specific fields. Tool events match tool names (for example, `"matcher": "Bash"` or `"matcher": "Edit|Write"`), while handler-level `if` conditions can use permission-rule syntax to inspect tool arguments (for example, `"if": "Bash(rm *)"`).

### Codex

Codex hooks are experimental and must be enabled explicitly. In `~/.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

Codex ships a smaller core set of events, all `PascalCase`, configured in `~/.codex/hooks.json` or `<repo>/.codex/hooks.json`:

- `SessionStart` — Session begins. Matcher filters the `source` field: `startup`, `resume`, or `clear`.
- `UserPromptSubmit` — User prompt submitted.
- `PreToolUse` — Before a supported tool call, including `Bash`, `apply_patch` (`Edit|Write` aliases), and MCP tools.
- `PermissionRequest` — Permission prompt about to be shown.
- `PostToolUse` — After a supported tool call, including `Bash`, `apply_patch` (`Edit|Write` aliases), and MCP tools.
- `Stop` — Turn finished.

The Codex event set is intentionally close to the classic Claude Code lifecycle, which makes cross-agent hook scripts easier to share — but note that the tool-event surface is still narrower than Claude Code's and does not intercept every tool path.

Matchers are regexes evaluated against `tool_name` for tool events or `source` for `SessionStart`. Codex hooks are changing quickly, so small details may differ between Codex versions. The examples below show the event set used in this course.

### OpenCode

OpenCode does not have a JSON event config. Plugins are TypeScript or JavaScript modules in `.opencode/plugins/`, and each exported plugin returns an object whose **keys are event names**. The runtime calls the matching key when the event fires.

**Typed hook keys (first-class):**
- `"tool.execute.before"` — About to execute a tool.
- `"tool.execute.after"` — Tool execution finished.
- `"shell.env"` — About to launch a shell command; mutate the environment.
- `"experimental.session.compacting"` — Session is being compacted.

**Generic `event` callback** — receives `{ event }` with an `event.type` field. Types include lifecycle and UI events like:
- `session.created`, `session.updated`, `session.idle`, `session.compacted`, `session.deleted`, `session.error`, `session.diff`, `session.status`
- `message.updated`, `message.removed`, `message.part.updated`, `message.part.removed`
- `command.executed`, `file.edited`, `file.watcher.updated`
- `permission.asked`, `permission.replied`
- `lsp.client.diagnostics`, `lsp.updated`
- `todo.updated`, `server.connected`, `installation.updated`
- `tui.prompt.append`, `tui.command.execute`, `tui.toast.show`

OpenCode has no `UserPromptSubmit` event. The nearest equivalent is reading the new user message through the generic `event` callback when `message.updated` fires.

### Pi

Pi hooks live inside TS/JS extensions in `.pi/extensions/` or `~/.pi/agent/extensions/`. The built-in lifecycle is lower_snake_case:

**Core lifecycle events:**
- `session_start` — Session begins (`startup`, `reload`, `new`, `resume`, or `fork`)
- `before_agent_start` — User prompt received; can inject messages or edit the system prompt
- `agent_start` — Agent loop begins
- `turn_start`, `turn_end` — One model turn starts or finishes
- `tool_call` — Before a tool executes; can mutate args or block
- `tool_result` — After a tool executes; can rewrite the result
- `agent_end` — Request finished
- `session_shutdown` — Extension runtime is being torn down

**Session/control events:**
- `session_before_switch`, `session_before_fork` — Intercept `/new`, `/resume`, `/fork`, or `/clone`
- `session_before_compact`, `session_compact`, `session_before_tree`, `session_tree` — Context management and tree navigation
- `model_select`, `user_bash` — Model changes and user-initiated shell commands

Pi doesn't use a JSON hook file. You register handlers in code with `pi.on("event_name", handler)` and ship them in an extension or Pi package.

## Event Input: What Your Hook Receives

### Claude Code

Command hooks receive a JSON payload on **stdin**. HTTP hooks receive the same payload as the POST body. Common fields across events:

```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

Tool-related events add `tool_name`, `tool_input`, and (on `PostToolUse`) `tool_response`. Subagent events add `agent_id` and `agent_type`. The project root is also available as an environment variable `CLAUDE_PROJECT_DIR`.

### Codex

Command hooks receive JSON on stdin. Common fields:

```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "model": "gpt-5-codex"
}
```

Turn-scoped events add `turn_id`. Tool events add `tool_name`, `tool_use_id`, and `tool_input`; for `Bash` and `apply_patch`, the command is in `tool_input.command`. `PostToolUse` also includes `tool_response`. `UserPromptSubmit` adds `prompt`. `Stop` adds `stop_hook_active` and `last_assistant_message`.

### OpenCode

OpenCode hooks are JS/TS functions, not stdin scripts. Each event type has a typed `(input, output)` signature:

```ts
"tool.execute.before": async (input, output) => {
  // input.tool       — tool name (e.g. "read", "bash")
  // input.sessionID  — session identifier
  // output.args      — tool arguments (mutable)
}
```

`"tool.execute.after"` adds the result on `output`. `"shell.env"` gives you `output.env` to mutate. The generic `event` callback receives `{ event }` where `event.type` identifies the event.

The plugin also receives a context object at construction time: `{ project, directory, worktree, client, $ }`. Use `client.app.log({...})` for structured logging and `$` (Bun shell) to run commands.

### Pi

Pi hooks are TS/JS functions registered in an extension. Common event shapes look like this:

```ts
pi.on("before_agent_start", async (event, ctx) => {
  // event.prompt        — user prompt text
  // event.systemPrompt  — current system prompt for this turn
  // event.images        — attached images (if any)
});

pi.on("tool_call", async (event, ctx) => {
  // event.toolName      — "bash", "read", "write", etc.
  // event.toolCallId    — unique tool call id
  // event.input         — mutable tool arguments
});

pi.on("tool_result", async (event, ctx) => {
  // event.toolName      — tool name
  // event.input         — final tool arguments
  // event.content       — tool result content blocks
  // event.details       — structured tool details
  // event.isError       — whether the tool failed
});
```

For nested async work inside a handler, use `ctx.signal` so Esc can cancel the extension's own `fetch()` calls or other abort-aware work.

## How Hooks Influence the Agent

Hooks are not pure observers — they can change what the agent does:

1. **Block operations**: PreToolUse hooks can deny tool calls
2. **Modify inputs**: Hooks can rewrite tool arguments before execution
3. **Inject context**: Hooks can add text to the conversation
4. **Trigger side effects**: Hooks can run external scripts, HTTP calls, etc.

The exact mechanism varies by platform:

### Claude Code

Return JSON on stdout with `hookSpecificOutput`:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Blocked by policy",
    "additionalContext": "Remember: deploys require approval",
    "updatedInput": { "command": "safe_command" }
  }
}
```

### Codex

Similar to Claude Code — return JSON on stdout or use exit codes for blocking.

### OpenCode

Mutate the `output` object passed to your handler:

```ts
"tool.execute.before": async (input, output) => {
  output.args = { ...output.args, safe: true };
}
```

### Pi

Mutate the `event` object or return modified values:

```ts
pi.on("tool_call", async (event, ctx) => {
  event.input = { ...event.input, safe: true };
});
```

## Cross-Platform Hook Scripts

You can write hook scripts that work across multiple platforms by:

1. **Checking for platform-specific fields** in the input JSON
2. **Using generic field names** that exist across platforms (`session_id`, `cwd`, etc.)
3. **Falling back gracefully** when platform-specific features aren't available

Example cross-platform PreToolUse hook:

```bash
#!/bin/bash
INPUT=$(cat)

# Try Claude Code field names
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

# Fall back to Codex field names
if [[ -z "$TOOL_NAME" ]]; then
  TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
fi

# Generic blocking logic
if [[ "$TOOL_NAME" == "Bash" ]] || [[ "$TOOL_NAME" == "bash" ]]; then
  COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // .command // empty')
  if echo "$COMMAND" | grep -q 'rm -rf'; then
    # Return platform-agnostic denial
    jq -n '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: "Destructive command blocked"
      }
    }'
  fi
fi

exit 0
```

## Best Practices

1. **Start simple**: Begin with Claude Code hooks — they have the best documentation and richest event set
2. **Test incrementally**: Add one hook at a time and verify it works before adding more
3. **Use platform-specific features**: Each platform has unique capabilities — leverage them rather than aiming for lowest-common-denominator compatibility
4. **Document your hooks**: Add comments explaining what each hook does and why
5. **Version control configurations**: Commit hook configurations to share with your team
6. **Monitor performance**: Hooks can slow down your agent if they're slow — keep them fast
7. **Handle errors gracefully**: Use try-catch blocks and proper error handling to prevent hook failures from breaking the agent

## Platform Selection Guide

Choose your platform based on your needs:

| Need                          | Best Platform      |
| ----------------------------- | ------------------ |
| Richest event set             | Claude Code        |
| Simple configuration         | Codex              |
| TypeScript/JS native         | OpenCode           |
| Extension system             | Pi                 |
| Cross-platform compatibility  | Claude Code + Codex |
| Enterprise features           | Claude Code        |
| Local-first development      | Any platform       |

For most users, Claude Code provides the best balance of features, documentation, and community support. Start there and explore other platforms if you have specific needs.
