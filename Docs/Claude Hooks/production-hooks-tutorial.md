# Claude Code Hooks: Build 5 Production Hooks From Scratch

Build 5 real Claude Code hooks step by step — auto-format, command blocker, AI linter, test runner, and context injector. Full configs and scripts included.

## TL;DR

Claude Code hooks let you attach shell commands, HTTP endpoints, or even AI prompts to lifecycle events: file edits, tool calls, session starts. They run deterministically, every time, unlike instructions Claude might interpret loosely. This tutorial walks through five hooks I actually use in production: an auto-formatter, a destructive-command blocker, an AI-powered lint gate, an automatic test runner, and a session-start context injector. Every hook includes the full configuration JSON and the backing script.

## Why Hooks Changed How I Use Claude Code

I spent my first month with Claude Code adding the same reminders to every prompt. "Run prettier after editing." "Don't delete the build directory." "Check the tests before you say you're done." Claude followed these instructions maybe 80% of the time. Good enough for casual use, maddening for a codebase where one missed format check means a failed CI pipeline.

Hooks fixed that problem entirely. Instead of hoping Claude remembers to format a file, a PostToolUse hook fires `prettier --write` on every edit. Instead of trusting that Claude won't run `rm -rf /`, a PreToolUse hook intercepts the command and blocks it before execution. The LLM doesn't get a vote. The hook runs every time, the same way, with zero prompt engineering required.

The shift from "Claude, please remember to do X" to "X happens automatically, always" was the biggest reliability improvement I made to my Claude Code workflow all year. These are the five hooks I rely on every day.

## How Claude Code Hooks Work

A hook is a handler (a shell command, HTTP call, or AI prompt) that fires at a specific point in Claude Code's lifecycle. If you've been comparing terminal coding agents, hooks are one of the features that set Claude Code apart from the competition. You configure hooks in your settings file (project-scoped, user-scoped, or local), and Claude Code runs them deterministically whenever the matching event occurs.

### Lifecycle Events

Claude Code exposes 30 lifecycle events. The ones you'll use most:

──────────────────┬────────────────────────────────────────────────────┬──────────
Event             │When It Fires                                       │Can Block?
──────────────────┼────────────────────────────────────────────────────┼──────────
`PreToolUse`      │Before Claude calls a tool (Bash, Edit, Write, etc.)│Yes       
──────────────────┼────────────────────────────────────────────────────┼──────────
`PostToolUse`     │After a tool call completes                         │Yes       
──────────────────┼────────────────────────────────────────────────────┼──────────
`UserPromptSubmit`│When you press Enter on a prompt                    │Yes       
──────────────────┼────────────────────────────────────────────────────┼──────────
`Stop`            │When Claude finishes a response                     │Yes       
──────────────────┼────────────────────────────────────────────────────┼──────────
`SessionStart`    │When a session begins or resumes                    │No        
──────────────────┴────────────────────────────────────────────────────┴──────────

The "Can Block?" column is what makes hooks useful. A PreToolUse hook that exits with code 2 blocks the tool call entirely and feeds the error message back to Claude so it can adjust.

### Handler Types

Five handler types exist, each suited to different complexity levels:

Command hooks run a shell command. They receive the event's JSON payload on stdin and communicate results through exit codes and stdout. You'll use these 90% of the time.

HTTP hooks POST the event JSON to a URL, which works well for integrating with external services or shared team tooling.

MCP tool hooks call a tool on a connected MCP server, bridging hooks into your existing MCP integrations without custom scripts.

For validation that needs judgment rather than pattern matching, prompt hooks send a text prompt to a fast Claude model (Haiku by default) for single-turn evaluation. The model returns an `ok: true` or `ok: false` decision as JSON.

Agent hooks are the heaviest option: they spawn a sub-agent with access to tools like Read and Grep for multi-turn codebase verification. If you've used Claude Code subagents before, agent hooks follow the same principle but triggered automatically instead of on demand.

### Configuration Structure

Hooks live in your settings file under the `hooks` key. The basic shape:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/my-script.sh"
          }
        ]
      }
    ]
  }
}
```

The `matcher` field filters which tool calls trigger the hook. `"Bash"` matches only Bash tool calls. `"Edit|Write"` matches both. Omitting it (or using `"*"`) matches everything. Matchers also support regex when the pattern contains characters beyond letters, digits, underscores, and pipes.

Put this in `.claude/settings.json` for project-scoped hooks (shared via git), `~/.claude/settings.json` for user-scoped, or `.claude/settings.local.json` for local-only hooks that stay out of version control.

## Hook 1: Auto-Format Every File Edit

Every time Claude edits or creates a file, this hook runs your formatter on it automatically. No more reviewing diffs full of inconsistent indentation, and no more manually running `prettier` after every session.

### Configuration

Add this to `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/auto-format.sh",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### Script

Create `.claude/hooks/auto-format.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat /dev/stdin)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ -z "$FILE_PATH" || ! -f "$FILE_PATH" ]]; then
  exit 0
fi

EXT="${FILE_PATH##*.}"

case "$EXT" in
  js|jsx|ts|tsx|json|css|md|html|yaml|yml)
    npx prettier --write "$FILE_PATH" 2>/dev/null
    ;;
  py)
    python3 -m black --quiet "$FILE_PATH" 2>/dev/null
    python3 -m isort --quiet "$FILE_PATH" 2>/dev/null
    ;;
  go)
    gofmt -w "$FILE_PATH" 2>/dev/null
    ;;
  rs)
    rustfmt "$FILE_PATH" 2>/dev/null
    ;;
esac

exit 0
```

`chmod +x .claude/hooks/auto-format.sh`

### How It Works

The PostToolUse event fires after any Edit, Write, or NotebookEdit call. The hook reads the event JSON from stdin, extracts the `file_path` from `tool_input`, checks the extension, and runs the appropriate formatter. Exit code 0 means success, so Claude continues normally. If the formatter isn't installed for a given language, the `2>/dev/null` silently swallows the error.

The 15-second timeout prevents a pathological formatter from blocking the entire session. In practice, formatting a single file takes under a second.

**Lesson learned:** I originally set the matcher to `"*"`. Bad idea. The hook fired on every tool call, including Bash, Read, and anything else. Narrowing to `Edit|Write|NotebookEdit` made it much faster and more predictable.

## Hook 2: Block Destructive Commands

Prevent Claude from running dangerous commands like `rm -rf /` by blocking them before execution.

### Configuration

```json
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

### Script

Create `.claude/hooks/block-destructive.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat /dev/stdin)
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

`chmod +x .claude/hooks/block-destructive.sh`

### Under the Hood

The `if` condition uses permission rule syntax: `Bash(rm -rf *)` matches Bash commands containing `rm` followed by `rf` and anything else. When both the matcher (`Bash`) and the `if` condition match, the hook script runs.

The script returns `{ permissionDecision: "deny" }` to block the command. Claude receives this decision and adjusts its behavior — it might try an alternative approach or explain why it can't proceed.

### Why This Beats Permission Mode

Permission mode (`-p`) requires manual approval for every tool call. It's safe but tedious. This hook blocks only the dangerous subset while letting safe commands run automatically. You get the safety without the friction.

## Hook 3: AI-Powered Code Quality Gate

Use a prompt hook to have Claude Haiku review code changes for quality issues before they're applied.

### Configuration

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review this code change for quality issues. If the code is good, respond with {\"ok\": true}. If there are issues, respond with {\"ok\": false, \"reason\": \"specific issue\"}.",
            "model": "claude-3-5-haiku-20241022"
          }
        ]
      }
    ]
  }
}
```

### The Execution Flow

1. Claude attempts to edit a file
2. The PreToolUse hook fires with the edit details
3. The prompt is sent to Claude Haiku with the code change
4. Haiku evaluates the code and returns `{ok: true}` or `{ok: false, reason: "..."}`
5. If `ok: false`, the hook blocks the edit and feeds the reason back to Claude
6. Claude can then fix the issue and try again

This is slower than a simple regex check (Haiku takes 1-2 seconds), but it catches semantic issues that pattern matching would miss.

## Hook 4: Auto-Run Tests After Changes

Automatically run relevant tests when Claude modifies test files or source code.

### Configuration

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "if": "Edit|Write(*.test.ts) | Edit|Write(*.spec.ts) | Edit|Write(src/*.ts)",
            "command": ".claude/hooks/run-tests.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

### Script

Create `.claude/hooks/run-tests.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat /dev/stdin)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path')

if [[ "$FILE_PATH" == *.test.ts ]] || [[ "$FILE_PATH" == *.spec.ts ]]; then
  # Run the specific test file
  npx jest "$FILE_PATH" 2>/dev/null
elif [[ "$FILE_PATH" == src/*.ts ]]; then
  # Run all tests if source code changed
  npx jest 2>/dev/null
fi

exit 0
```

`chmod +x .claude/hooks/run-tests.sh`

### How It Works

The `if` condition matches test files and source files. When a match occurs, the hook runs Jest. Test files trigger just that test; source files trigger the full suite. The 30-second timeout prevents long-running tests from blocking indefinitely.

**Lesson learned:** Don't run the full test suite on every edit. It's too slow. Match only the relevant tests or run a quick smoke test instead.

## Hook 5: Session-Start Context Injector

Automatically inject project-specific context when a session begins, so Claude has the right information from the start.

### Configuration

```json
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

### Script

Create `.claude/hooks/inject-context.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

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

Create `.claude/session-context.md`:

```markdown
This project uses TypeScript with strict mode enabled.
- Run tests with `npm test`
- Build with `npm run build`
- Deploy to staging with `npm run deploy:staging`
- Main branch is protected, requires PR approval
```

### What Gets Injected

The hook reads the context file and injects it as `additionalContext`. This text becomes part of Claude's context for the entire session, like a permanent CLAUDE.md but without editing the file itself.

### The Payoff

No more reminding Claude about project conventions. The context is there from the first message. This is especially useful for team projects where you want everyone to have the same baseline context.

## Debugging Hooks

When a hook isn't working:

1. **Check the hooks browser**: Type `/hooks` to see all loaded hooks and their configuration
2. **Add logging**: Add `echo` statements to your script to trace execution
3. **Test manually**: Pipe sample JSON to your script to test it in isolation
4. **Check permissions**: Ensure scripts are executable (`chmod +x`)
5. **Verify matchers**: Use `/hooks` to confirm your matcher patterns are correct

Common issues:

- **Hook not firing**: Check the matcher pattern and event type
- **Script failing silently**: Add `set -x` to the script for debugging output
- **Timeout errors**: Increase the timeout or optimize the script
- **Permission denied**: Check file permissions and script executable bit

## Hooks vs Skills vs CLAUDE.md

- **Hooks**: Deterministic, event-driven automation. Best for: formatting, blocking dangerous operations, logging, notifications.
- **Skills**: On-demand capabilities you invoke with slash commands. Best for: complex multi-step workflows, specialized tasks.
- **CLAUDE.md**: Always-on context and instructions. Best for: project conventions, coding standards, architectural guidance.

Use hooks for automation that must happen every time. Use skills for capabilities you call when needed. Use CLAUDE.md for context that should always be available.

## FAQ

### What are Claude Code hooks?

Hooks are user-defined shell commands, HTTP endpoints, or AI prompts that execute automatically at specific points in Claude Code's lifecycle. They provide deterministic control over Claude's behavior.

### What lifecycle events do Claude Code hooks support?

Claude Code supports 30 lifecycle events including SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, and many more. See the full list in the hooks reference.

### How are hooks different from skills in Claude Code?

Hooks run automatically when events occur and are best for deterministic automation. Skills are invoked manually with slash commands and are best for on-demand capabilities.

### Can Claude Code hooks block destructive commands?

Yes, PreToolUse hooks can block tool calls by returning a permission decision of "deny". This is commonly used to block dangerous shell commands.

### What is a prompt hook in Claude Code?

A prompt hook sends a text prompt to a Claude model (typically Haiku) for evaluation. The model returns a decision as JSON, enabling AI-powered validation that requires judgment rather than pattern matching.

### How do I debug Claude Code hooks?

Use the `/hooks` command to see all loaded hooks. Add logging to your scripts, test with sample input, and check file permissions. The hooks browser shows configuration details and helps verify hooks are registered correctly.

## Sources

- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Hooks Guide](https://code.claude.com/docs/en/hooks-guide)
- [Claude Agent SDK Hooks](https://code.claude.com/docs/en/agent-sdk/hooks.md)
- [Hook Events and Agent Lifecycle](https://huggingface.co/learn/context-course/unit5/hook-events)

## Bottom Line

Hooks transformed my Claude Code workflow from "hope Claude remembers" to "critical tasks happen automatically". The five hooks here took about an hour to set up and have saved countless hours of manual work since. Start with the auto-formatter — it's the easiest win and immediately improves code quality.
