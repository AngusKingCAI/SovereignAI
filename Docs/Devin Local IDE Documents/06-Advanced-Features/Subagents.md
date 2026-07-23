# Subagents

Delegate tasks to independent subagents that work in the foreground or background

Subagents let the main agent spawn independent workers to handle subtasks. A subagent shares tools and codebase context with the parent, but operates in its own conversation chain -- it does not inherit the parent's conversation history. This is useful for tasks that benefit from focused, independent work -- like exploring a codebase, running tests, or implementing a feature in parallel.

You can ask the agent to use subagents explicitly (e.g. "research how auth works in a subagent"), or the agent may decide to delegate on its own when it determines a task would benefit from independent work.

In our measurements, **subagents** **both** **improve overall coding performance** **and** **reduce cost**.

## How Subagents Work

When the agent spawns a subagent, it selects one of the available **subagent profiles** and chooses whether the subagent should run in the foreground or background. Subagents can run in two modes:

### Foreground
Runs inline in your session. The parent agent pauses and waits for the subagent to finish before continuing. You can approve or deny tool calls as they come up.

### Background
Runs in parallel while the parent agent continues working. The parent is automatically notified when the subagent completes. Unapproved tools are automatically denied.

**Note**: You do not see the subagent's raw output directly. When a subagent finishes, the parent agent reads the result and summarizes the key findings and actions for you.

### Subagent Cost

Subagents run as their own agent sessions, each with its own context window and inference calls, so they consume cost independently of the parent. The parent's spend covers its own work; every subagent it spawns adds its own usage on top of that.

Because cost scales with the number of subagents, tasks that fan out into many subagents (or nest them) cost more. Use subagents deliberately when the parallelism or focused context is worth the additional spend.

## Which Model Does a Subagent Use?

Subagents do not all run on the model you picked in the model picker. Each profile decides where its model comes from:

| Profile | Model used | Effect on quota / credits |
| --- | --- | --- |
| `subagent_explore` | The **default subagent model** — a fast, cheap model (SWE-1.6 by default) | Cheap: SWE-1.6 usage is billed at SWE rates, not at your primary model's rate |
| `subagent_general` | **The same model as the parent agent** — whatever you selected in the model picker (e.g. Claude Opus, GPT-5) | Same rate as the parent: a general subagent costs like a full extra session on your selected model |
| Custom subagents | The `model` field in `AGENT.md` if set, otherwise the **default subagent model** | Depends on the model you pin |

**Warning**: `subagent_general` inherits the parent's model. If you are running a premium model, every general subagent runs on that premium model too, with its own context window and inference calls — so a task that fans out into several general subagents multiplies your spend. Ask for an explore subagent (or a custom subagent with a cheaper `model:` pinned) when the work is research rather than code changes.

The **default subagent model** is not a fixed model name — it resolves through a router at spawn time, and an admin can override it. With the default **Subagent router** setting it resolves to SWE-1.6 (a faster or slower SWE-1.6 variant depending on your plan tier).

### Influencing the Model

There is no way to name a model for a subagent in a prompt — the `run_subagent` tool takes a *profile*, not a model. You have two levers:

1. **Ask for a profile in natural language.** Requesting an explore subagent ("research how auth works in an explore subagent") keeps the work on the cheap default subagent model. Asking for code changes gets you `subagent_general`, which runs on your selected model.
2. **Pin a model in a custom subagent profile.** `model:` in `AGENT.md` is the only way to run a *write-capable* subagent on a model other than the parent's. A skill that runs in a subagent can also set `model:` in its frontmatter to override the profile's model.

### Enterprise Controls

Administrators can govern which model subagents use — and whether subagents run at all — through the **Default subagent model** setting in the org/enterprise settings. This setting controls the model for `subagent_explore` and for custom subagents that don't pin a `model:` — it does not change `subagent_general`, which always follows the parent agent's model.

It has three choices:

| Option | Behavior |
| --- | --- |
| **Subagent router (default)** | The default subagent model is chosen by a router at spawn time. Today it resolves to SWE-1.6 (the exact variant depends on your plan tier). |
| **A specific model** | Pins the default subagent model to the selected model, for every subagent that doesn't run on the parent's model. |
| **None** | Disables subagents entirely — Devin will not spawn any subagents. |

## Subagent Profiles

Each subagent runs with a specific profile that determines its capabilities. There are two built-in profiles:

| Profile | Description | Tool Access | Model |
| --- | --- | --- | --- |
| `subagent_explore` | Read-only codebase exploration and research | Read-only codebase tools plus web search; cannot edit files or fetch arbitrary URLs (regardless of foreground or background) | Default subagent model (SWE-1.6 by default) |
| `subagent_general` | General-purpose tasks including code changes | Full tool access (foreground) or pre-approved tools only (background) | Same model as the parent agent |

**Note**: The agent automatically chooses the appropriate profile based on the task. Explore subagents are ideal for research and understanding, while general subagents can make changes.

You can also define your own custom subagent profiles.

## Tool Permissions

How tool permissions work depends on whether the subagent is running in the foreground or background:

- **Foreground subagents** behave like the main agent -- you are prompted to approve or deny tool calls as usual.
- **Background subagents** inherit any tool permissions you have already granted during the current session. Any tool that has not been pre-approved is automatically denied. Background subagents cannot prompt you for new permissions.

**Tip**: If a background subagent fails because a required tool was denied, you can resume it in the foreground to approve the necessary permissions.

## Monitoring Subagents

### Subagent Indicator

When background subagents are running, an indicator appears below the input area showing their status. You can navigate to the indicator by pressing `↓` from the input area, then press `Enter` to open the subagent panel.

When a foreground subagent is running, the spinner displays **"Subagent running · Ctrl+B to run in background"**.

### Subagent Panel

The subagent panel lets you view and manage all active and completed subagents. It shows each subagent's profile, title, status, elapsed time, and tool call count.

## Foreground / Background Switching

You can move subagents between foreground and background while they're running:

- **Background a foreground subagent:** Press `Ctrl+B` while a foreground subagent is running. The subagent continues working in the background, and the parent agent resumes.
- **Foreground a background subagent:** Open the subagent panel and press `f` on a running background subagent. The subagent's output will display inline.

**Note**: When you move a subagent to the background, the parent agent's tool call has already returned, so the parent continues independently. The subagent's result won't feed back into the parent's current pipeline, but you'll be notified when it completes.

## Resuming Subagents

If a background subagent fails (e.g., due to denied tool permissions), you can resume it in the foreground to approve the necessary permissions:

1. Open the subagent panel
2. Navigate to the failed subagent
3. Press `f` to foreground it
4. Approve the required permissions
5. The subagent will continue from where it left off

## Custom Subagents

You can define your own subagent profiles with custom system prompts, tool access, and model selection. Create a custom subagent by creating an `AGENT.md` file in the `.devin/agents/` directory:

```
.devine/agents/
└── my-agent/
    └── AGENT.md
```

The `AGENT.md` file defines the subagent's behavior, capabilities, and model selection.

### Custom Subagent Frontmatter Fields

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `name` | string | directory name | Identifier for the profile (must not conflict with built-in profiles) |
| `description` | string | none | Shown to the agent when selecting a profile |
| `model` | string | default subagent model (SWE-1.6 by default) | Override the model used by this subagent |
| `allowed-tools` | list | all tools | Restrict which tools the subagent can use. Cannot grant `ask_user_question`, which is always withheld from subagents. |
| `permissions` | object | inherit | Permission overrides (`allow`, `deny`, `ask`) |
| `max-nesting` | integer | none | Override the maximum nesting depth, allowing this subagent to spawn its own subagents |

## Nesting Depth

By default, subagents cannot spawn their own subagents — only the root agent can. Subagent tools (`run_subagent` and `read_subagent`) are disabled inside a subagent to prevent unbounded nesting.

However, custom subagent profiles can opt in to nested spawning by setting the `max-nesting` field in their frontmatter. This value overrides the default maximum depth, allowing subagents to spawn children as long as the tree stays within that limit.

For example, `max-nesting: 3` allows the following chain:

```
Root agent (depth 0)
└── Custom subagent (depth 1) — can spawn children
    └── Child subagent (depth 2) — can spawn children
        └── Grandchild subagent (depth 3) — cannot spawn (depth limit reached)
```

**Warning**: Nested subagents can increase cost significantly. Each level of nesting spawns additional agents with their own context windows and inference calls. Use this feature deliberately.

## Enhanced Subagent Features

### Subagent Default Model Configuration

Subagents can now be configured with a default model through the `model` field in custom subagent profiles. This allows you to pin specific subagents to cost-effective models regardless of the parent agent's model selection.

### Enhanced Explore Subagent

The built-in Explore subagent can now use web search to research topics outside the codebase, in addition to its read-only codebase tools. It still cannot fetch arbitrary URLs or edit files, but web search capability extends its research capabilities beyond the local codebase.

### Live Streaming of Subagent Actions

When waiting on a foreground subagent or a `read_subagent` call, you can now see live streaming of subagent actions in the display. This provides better visibility into what the subagent is doing in real-time, rather than waiting for completion to see the results.

### Subagent MCP Tool Access

Subagents can now call MCP tools directly, extending their capabilities beyond the built-in tools. This allows subagents to interact with external services, databases, and APIs through configured MCP servers.