# Unrolling the Codex Agent Loop

**Source:** https://openai.com/index/unrolling-the-codex-agent-loop/
**Author:** Michael Bolin, Member of the Technical Staff
**Date:** January 23, 2026

---

## Overview

[Codex CLI](https://github.com/openai/codex) is our cross-platform local software agent, designed to produce high-quality, reliable software changes while operating safely and efficiently on your machine. We've learned a tremendous amount about how to build a world-class software agent since we first launched the CLI in April. To unpack those insights, this is the first post in an ongoing series where we'll explore various aspects of how Codex works, as well as hard-earned lessons.

To kick off, we'll focus on the agent loop, which is the core logic in Codex CLI that is responsible for orchestrating the interaction between the user, the model, and the tools the model invokes to perform meaningful software work. We hope this post gives you a good view into the role our agent (or "harness") plays in making use of an LLM.

Before we dive in, a quick note on terminology: at OpenAI, "Codex" encompasses a suite of software agent offerings, including Codex CLI, Codex Cloud, and the Codex VS Code extension. This post focuses on the Codex harness, which provides the core agent loop and execution logic that underlies all Codex experiences and is surfaced through the Codex CLI. For ease here, we'll use the terms "Codex" and "Codex CLI" interchangeably.

---

## The Agent Loop

At the heart of every AI agent is something called "the agent loop." A simplified illustration of the agent loop looks like this:

1. **User Input** - The agent takes input from the user to include in the set of textual instructions it prepares for the model known as a prompt
2. **Model Inference** - The next step is to query the model by sending it our instructions and asking it to generate a response, a process known as inference
3. **Tool Execution** - The model either produces a final response or requests a tool call that the agent is expected to perform
4. **Result Integration** - The agent executes the tool call and appends its output to the original prompt
5. **Iteration** - This output is used to generate a new input that's used to re-query the model; the agent can then take this new information into account and try again
6. **Termination** - The process repeats until the model stops emitting tool calls and instead produces a message for the user

### Model Inference Process

During inference, the textual prompt is first translated into a sequence of input tokens—integers that index into the model's vocabulary. These tokens are then used to sample the model, producing a new sequence of output tokens.

The output tokens are translated back into text, which becomes the model's response. Because tokens are produced incrementally, this translation can happen as the model runs, which is why many LLM-based applications display streaming output. In practice, inference is usually encapsulated behind an API that operates on text, abstracting away the details of tokenization.

### Tool Call Handling

As the result of the inference step, the model either:
1. Produces a final response to the user's original input, or
2. Requests a tool call that the agent is expected to perform (e.g., "run `ls` and report the output")

In the case of (2), the agent executes the tool call and appends its output to the original prompt. This output is used to generate a new input that's used to re-query the model; the agent can then take this new information into account and try again.

### Agent Output

Because the agent can execute tool calls that modify the local environment, its "output" is not limited to the assistant message. In many cases, the primary output of a software agent is the code it writes or edits on your machine. Nevertheless, each turn always ends with an assistant message—such as "I added the `architecture.md` you asked for"—which signals a termination state in the agent loop. From the agent's perspective, its work is complete and control returns to the user.

### Multi-Turn Conversations

The journey from user input to agent response is referred to as one turn of a conversation (a thread in Codex). Though this conversation turn can include many iterations between the model inference and tool calls. Every time you send a new message to an existing conversation, the conversation history is included as part of the prompt for the new turn, which includes the messages and tool calls from previous turns.

This means that as the conversation grows, so does the length of the prompt used to sample the model. This length matters because every model has a context window, which is the maximum number of tokens it can use for one inference call. Note this window includes both input and output tokens. As you might imagine, an agent could decide to make hundreds of tool calls in a single turn, potentially exhausting the context window. For this reason, context window management is one of the agent's many responsibilities.

---

## Model Inference

The Codex CLI sends HTTP requests to the Responses API to run model inference. We'll examine how information flows through Codex, which uses the Responses API to drive the agent loop.

The Responses API endpoint that the Codex CLI uses is configurable, so it can be used with any endpoint that implements the Responses API:
- When using ChatGPT login with the Codex CLI, it uses `https://chatgpt.com/backend-api/codex/responses` as the endpoint
- When using API-key authentication with OpenAI hosted models, it uses `https://api.openai.com/v1/responses` as the endpoint
- When running Codex CLI with `--oss` to use gpt-oss with ollama 0.13.4+ or LM Studio 0.3.39+, it defaults to `http://localhost:11434/v1/responses` running locally on your computer
- Codex CLI can be used with the Responses API hosted by a cloud provider such as Azure

### Building the Initial Prompt

As an end user, you don't specify the prompt used to sample the model verbatim when you query the Responses API. Instead, you specify various input types as part of your query, and the Responses API server decides how to structure this information into a prompt that the model is designed to consume. You can think of the prompt as a "list of items"; this section will explain how your query gets transformed into that list.

In the initial prompt, every item in the list is associated with a role. The `role` indicates how much weight the associated content should have and is one of the following values (in decreasing order of priority): `system`, `developer`, `user`, `assistant`.

The Responses API takes a JSON payload with many parameters. We'll focus on these three:
- `instructions`: system (or developer) message inserted into the model's context
- `tools`: a list of tools the model may call while generating a response
- `input`: a list of text, image, or file inputs to the model

#### Instructions

In Codex, the `instructions` field is read from the `model_instructions_file` in `~/.codex/config.toml`, if specified; otherwise, the `base_instructions` associated with a model are used. Model-specific instructions live in the Codex repo and are bundled into the CLI (e.g., `gpt-5.2-codex_prompt.md`).

#### Tools

The `tools` field is a list of tool definitions that conform to a schema defined by the Responses API. For Codex, this includes tools that are provided by the Codex CLI, tools that are provided by the Responses API that should be made available to Codex, as well as tools provided by the user, usually via MCP servers:

```javascript
[
  // Codex's default shell tool for spawning new processes locally.
  {
    "type": "function",
    "name": "shell",
    "description": "Runs a shell command and returns its output...",
    "strict": false,
    "parameters": {
      "type": "object",
      "properties": {
        "command": {"type": "array", "description": "The command to execute", ...},
        "workdir": {"description": "The working directory...", ...},
        "timeout_ms": {"description": "Timeout in milliseconds...", ...}
      }
    }
  },
  // Additional tools from Codex CLI, Responses API, and MCP servers...
]
```

#### Input

The `input` field is a list of text, image, or file inputs to the model. For Codex, this typically includes:
- The user's message or request
- Relevant files from the codebase
- Context from the repository's documentation
- Previous conversation history (for multi-turn conversations)

### The First Turn

The first turn of a conversation is special because there's no previous conversation history to include. The prompt consists of:
1. System/developer instructions
2. The list of available tools
3. The user's input

The model then generates a response, which may include tool calls. If tool calls are made, the agent executes them and appends the results to the prompt for the next inference call.

### Performance Considerations

There are several performance considerations for the agent loop:

1. **Context Window Management** - As conversations grow, the prompt can exceed the model's context window. Codex implements strategies to manage this, including:
   - Selective inclusion of conversation history
   - Summarization of old turns
   - Prioritization of recent over old content

2. **Tool Call Optimization** - Tool calls can be expensive, especially if they involve network requests or long-running processes. Codex optimizes by:
   - Batching related tool calls when possible
   - Caching tool results when appropriate
   - Implementing timeouts for long-running tools

3. **Streaming Responses** - To provide a responsive user experience, Codex streams responses as they're generated, rather than waiting for the complete response.

4. **Parallel Tool Execution** - When the model requests multiple independent tool calls, Codex can execute them in parallel to reduce latency.

---

## Coming Next

This post covered the basics of the agent loop. Future posts in this series will explore:
- How Codex manages context across long conversations
- The design of Codex's tool system
- How Codex handles errors and retries
- The architecture of Codex's safety systems
- How Codex integrates with development workflows

---

## Key Takeaways

1. **The agent loop is the core** - The agent loop orchestrates the interaction between user, model, and tools
2. **Tool calls enable action** - Tool calls are what give agents the ability to perform meaningful work
3. **Context management is critical** - Managing context window limits is a key responsibility of the agent
4. **Multi-turn conversations grow context** - Each turn adds to the conversation history, requiring careful management
5. **The harness is the orchestrator** - The agent harness (Codex CLI) is responsible for executing the loop reliably

---

*Note: This content was fetched from OpenAI's engineering blog and saved for offline reference. For the most up-to-date version, visit the source URL.*
