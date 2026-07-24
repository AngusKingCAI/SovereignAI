# Intercept and control agent behavior with hooks

> Intercept and customize agent behavior at key execution points with hooks

Hooks are callback functions that run your code in response to agent events, like a tool being called, a session starting, or execution stopping. With hooks, you can:

* **Block dangerous operations** before they execute, like destructive shell commands or unauthorized file access
* **Log and audit** every tool call for compliance, debugging, or analytics
* **Transform inputs and outputs** to sanitize data, inject credentials, or redirect file paths
* **Require human approval** for sensitive actions like database writes or API calls
* **Track session lifecycle** to manage state, clean up resources, or send notifications

This guide covers how hooks work and how to configure them, with examples for common patterns like blocking tools, modifying inputs, and forwarding notifications.

## How hooks work

<Steps>
  <Step title="An event fires">
    Something happens during agent execution and the SDK fires an event: a tool is about to be called (`PreToolUse`), a tool returned a result (`PostToolUse`), a subagent started or stopped, the agent is idle, or execution finished. See the [full list of events](#available-hooks).
  </Step>

  <Step title="The SDK collects registered hooks">
    The SDK checks for hooks registered for that event type. This includes callback hooks you pass in `options.hooks` and shell command hooks from settings files when the corresponding [`settingSources`](/docs/en/agent-sdk/typescript#settingsource) or [`setting_sources`](/docs/en/agent-sdk/python#settingsource) entry is enabled, which it is for default `query()` options.
  </Step>

  <Step title="Matchers filter which hooks run">
    If a hook has a [`matcher`](#matchers) pattern (like `"Write|Edit"`), the SDK tests it against the event's target (for example, the tool name). Hooks without a matcher run for every event of that type.
  </Step>

  <Step title="Callback functions execute">
    Each matching hook's [callback function](#callback-functions) receives input about what's happening: the tool name, its arguments, the session ID, and other event-specific details.
  </Step>

  <Step title="Your callback returns a decision">
    After performing any operations (logging, API calls, validation), your callback returns an [output object](#outputs) that tells the agent what to do: allow the operation, block it, modify the input, or inject context into the conversation.
  </Step>
</Steps>

The following example puts these steps together. It registers a `PreToolUse` hook (step 1) with a `"Write|Edit"` matcher (step 3) so the callback only fires for file-writing tools. When triggered, the callback receives the tool's input (step 4), checks if the file path targets a `.env` file, and returns `permissionDecision: "deny"` to block the operation (step 5):

<CodeGroup>
  ```python Python theme={null}
  import asyncio
  from claude_agent_sdk import (
      AssistantMessage,
      ClaudeSDKClient,
      ClaudeAgentOptions,
      HookMatcher,
      ResultMessage,
  )


  # Define a hook callback that receives tool call details
  async def protect_env_files(input_data, tool_use_id, context):
      # Extract the file path from the tool's input arguments
      file_path = input_data["tool_input"].get("file_path", "")
      file_name = file_path.split("/")[-1]

      # Block the operation if targeting a .env file
      if file_name == ".env":
          return {
              "hookSpecificOutput": {
                  "hookEventName": input_data["hook_event_name"],
                  "permissionDecision": "deny",
                  "permissionDecisionReason": "Cannot modify .env files",
              }
          }

      # Return empty object to allow the operation
      return {}


  async def main():
      options = ClaudeAgentOptions(
          hooks={
              # Register the hook for PreToolUse events
              # The matcher filters to only Write and Edit tool calls
              "PreToolUse": [HookMatcher(matcher="Write|Edit", hooks=[protect_env_files])]
          }
      )

      async with ClaudeSDKClient(options=options) as client:
          await client.query("Create a .env file with the standard local development database configuration")
          async for message in client.receive_response():
              # Filter for assistant and result messages
              if isinstance(message, (AssistantMessage, ResultMessage)):
                  print(message)


  asyncio.run(main())
  ```

  ```typescript TypeScript theme={null}
  import { query, HookCallback, PreToolUseHookInput } from "@anthropic-ai/claude-agent-sdk";

  // Define a hook callback with the HookCallback type
  const protectEnvFiles: HookCallback = async (input, toolUseID, { signal }) => {
    // Cast input to the specific hook type for type safety
    const preInput = input as PreToolUseHookInput;

    // Cast tool_input to access its properties (typed as unknown in the SDK)
    const toolInput = preInput.tool_input as Record<string, unknown>;
    const filePath = toolInput?.file_path as string;
    const fileName = filePath?.split("/").pop();

    // Block the operation if targeting a .env file
    if (fileName === ".env") {
      return {
        hookSpecificOutput: {
          hookEventName: preInput.hook_event_name,
          permissionDecision: "deny",
          permissionDecisionReason: "Cannot modify .env files"
        }
      };
    }

    // Return empty object to allow the operation
    return {};
  };

  for await (const message of query({
    prompt: "Create a .env file with the standard local development database configuration",
    options: {
      hooks: {
        // Register the hook for PreToolUse events
        // The matcher filters to only Write and Edit tool calls
        PreToolUse: [{ matcher: "Write|Edit", hooks: [protectEnvFiles] }]
      }
    }
  })) {
    // Filter for assistant and result messages
    if (message.type === "assistant" || message.type === "result") {
      console.log(message);
    }
  }
  ```
</CodeGroup>

When you run either script, Claude attempts to create the `.env` file, the hook denies the tool call, and Claude's final response explains that it can't create `.env` files.

## Available hooks

The SDK provides hooks for different stages of agent execution. Some hooks are available in both SDKs, while others are TypeScript-only.

| Hook Event                                             | Python SDK | TypeScript SDK | What triggers it                                                                                                                        | Example use case                                                            |
| ------------------------------------------------------ | ---------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `PreToolUse`                                           | Yes        | Yes            | Tool call request (can block or modify)                                                                                                 | Block dangerous shell commands                                              |
| `PostToolUse`                                          | Yes        | Yes            | Tool execution result                                                                                                                   | Log all file changes to audit trail                                         |
| `PostToolUseFailure`                                   | Yes        | Yes            | Tool execution failure                                                                                                                  | Handle or log tool errors                                                   |
| `PostToolBatch`                                        | No         | Yes            | A full batch of tool calls resolves, once per batch before the next model call                                                          | Inject conventions once for the whole batch                                 |
| `UserPromptSubmit`                                     | Yes        | Yes            | User prompt submission                                                                                                                  | Inject additional context into prompts                                      |
| [`UserPromptExpansion`](/docs/en/hooks#userpromptexpansion) | No         | Yes            | A user-typed command, or an MCP prompt, expands into a prompt before it reaches Claude. Doesn't fire when Claude invokes a skill itself | Block a command from direct invocation or add context when a skill is typed |
| `MessageDisplay`                                       | No         | Yes            | An assistant message with text completes, once per message with the full message text                                                   | Redact or reformat the displayed text without changing the transcript       |
| `Stop`                                                 | Yes        | Yes            | Agent execution stop                                                                                                                    | Save session state before exit                                              |
| `StopFailure`                                          | No         | Yes            | The turn ends with an API error instead of a normal stop                                                                                | Log failure for debugging                                                   |

## Callback functions

Hook callbacks are functions you define that receive event data and return decisions. The signature varies by SDK and hook type.

### Python callback signature

```python
async def hook_callback(input_data, tool_use_id, context):
    # input_data: Dict with event-specific data
    # tool_use_id: String identifier for the tool call
    # context: Dict with session metadata
    return {
        "hookSpecificOutput": {
            "hookEventName": input_data["hook_event_name"],
            # Decision fields here
        }
    }
```

### TypeScript callback signature

```typescript
const hookCallback: HookCallback = async (input, toolUseID, { signal }) => {
  // input: Event-specific data (cast to appropriate type)
  // toolUseID: String identifier for the tool call
  // signal: AbortSignal for cancellation
  return {
    hookSpecificOutput: {
      hookEventName: input.hook_event_name,
      // Decision fields here
    }
  };
};
```

## Matchers

Matchers filter which events trigger a hook. They use regex patterns to match against event-specific fields like tool names.

```python
# Python
HookMatcher(matcher="Write|Edit", hooks=[my_callback])
```

```typescript
// TypeScript
{ matcher: "Write|Edit", hooks: [myCallback] }
```

Common matcher patterns:

| Pattern        | Matches                              |
| -------------- | ------------------------------------ |
| `"Write|Edit"`  | Write or Edit tools                  |
| `"Bash"`       | Only the Bash tool                   |
| `"*"`          | All tools (no filtering)             |
| `"^mcp__.*"`   | All MCP tools                        |

## Outputs

Hook callbacks return output objects that control agent behavior. The structure varies by hook type and what you want to control.

### Permission decisions

For `PreToolUse` and `PermissionRequest` hooks:

```python
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",  # or "allow"
    "permissionDecisionReason": "Destructive command blocked"
  }
}
```

### Input modification

For `PreToolUse` hooks, you can modify tool inputs:

```python
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "updatedInput": {
      "command": "safe_command_here"
    }
  }
}
```

### Context injection

For most hooks, you can inject additional context:

```python
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "Remember: deploys require approval"
  }
}
```

## Common patterns

### Block dangerous operations

```python
async def block_destructive_commands(input_data, tool_use_id, context):
  if input_data.get("tool_name") == "Bash":
    command = input_data["tool_input"].get("command", "")
    if "rm -rf" in command:
      return {
        "hookSpecificOutput": {
          "hookEventName": "PreToolUse",
          "permissionDecision": "deny",
          "permissionDecisionReason": "Destructive command blocked"
        }
      }
  return {}
```

### Log all tool calls

```python
async def log_tool_calls(input_data, tool_use_id, context):
  tool_name = input_data.get("tool_name")
  tool_input = input_data.get("tool_input")
  print(f"Tool called: {tool_name} with input: {tool_input}")
  return {}
```

### Modify tool inputs

```python
async def redirect_file_paths(input_data, tool_use_id, context):
  if input_data.get("tool_name") in ["Write", "Edit"]:
    file_path = input_data["tool_input"].get("file_path", "")
    # Redirect to a different directory
    if file_path.startswith("/tmp/"):
      new_path = file_path.replace("/tmp/", "/safe/tmp/")
      return {
        "hookSpecificOutput": {
          "hookEventName": "PreToolUse",
          "updatedInput": {
            "file_path": new_path
          }
        }
      }
  return {}
```

### Inject session context

```python
async def inject_project_context(input_data, tool_use_id, context):
  if input_data.get("hook_event_name") == "SessionStart":
    return {
      "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": "This project uses TypeScript with strict mode."
      }
    }
  return {}
```

## Integration with settings file hooks

The SDK can load hooks from Claude Code settings files in addition to callback hooks. This lets you share hooks between CLI and SDK usage.

### Python

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    setting_sources=["settings"],  # Load from .claude/settings.json
    hooks={
        # Callback hooks
        "PreToolUse": [my_callback]
    }
)
```

### TypeScript

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

await query({
  prompt: "Your prompt here",
  options: {
    settingSources: ["settings"],  // Load from .claude/settings.json
    hooks: {
      // Callback hooks
      PreToolUse: [myCallback]
    }
  }
});
```

When both callback hooks and settings file hooks are registered, they both execute for matching events.

## Error handling

Hook callbacks should handle errors gracefully to avoid breaking the agent execution.

### Python

```python
async def safe_hook(input_data, tool_use_id, context):
  try:
    # Your hook logic here
    return {}
  except Exception as e:
    print(f"Hook error: {e}")
    # Return empty object to allow operation to proceed
    return {}
```

### TypeScript

```typescript
const safeHook: HookCallback = async (input, toolUseID, { signal }) => {
  try {
    // Your hook logic here
    return {};
  } catch (error) {
    console.error("Hook error:", error);
    // Return empty object to allow operation to proceed
    return {};
  }
};
```

## Testing hooks

Test your hooks by running them with sample input data before using them in production.

### Python test example

```python
import asyncio
from claude_agent_sdk import protect_env_files

async def test_hook():
  # Sample input simulating a Write tool call
  test_input = {
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {
      "file_path": "/path/to/.env"
    }
  }
  
  result = await protect_env_files(test_input, "test-id", {})
  print(f"Hook result: {result}")

asyncio.run(test_hook())
```

### TypeScript test example

```typescript
import { protectEnvFiles } from "./hooks";

async function testHook() {
  const testInput = {
    hook_event_name: "PreToolUse",
    tool_name: "Write",
    tool_input: {
      file_path: "/path/to/.env"
    }
  } as PreToolUseHookInput;
  
  const result = await protectEnvFiles(testInput, "test-id", { signal: AbortSignal.timeout(5000) });
  console.log("Hook result:", result);
}

testHook();
```

## Best practices

1. **Keep hooks fast**: Hooks execute synchronously and can slow down the agent if they're slow.
2. **Handle errors gracefully**: Always use try-catch blocks to prevent hook errors from breaking agent execution.
3. **Use specific matchers**: Avoid wildcard matchers when possible to reduce unnecessary hook executions.
4. **Log appropriately**: Log what you need for debugging and compliance, but avoid logging sensitive information.
5. **Test thoroughly**: Test hooks with various scenarios before relying on them in production.
6. **Document your hooks**: Add comments explaining what each hook does and why it's needed.
7. **Version control hook configurations**: Share hook configurations across your team via settings files.
