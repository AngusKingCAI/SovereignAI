# Claude Code Harness: The Runtime Architecture That Turns an LLM into an Autonomous Agent (2026 Guide)

**Source:** https://pasqualepillitteri.it/en/news/1892/claude-code-harness-runtime-architecture-2026-guide

**Description:** This comprehensive guide explains the Claude Code harness runtime architecture, covering the agent loop, tool executor, permission manager, hook system, context manager, MCP layer, skill system, subagent framework, and session storage. It provides practical insights for configuring and optimizing the harness.

---

# Claude Code Harness: The Runtime Architecture That Turns an LLM into an Autonomous Agent (2026 Guide)

**Claude Code Harness explained: the runtime around the LLM model. Agentic loop, hooks, MCP,
skills, subagents, permissions and session storage.**

The **claude-opus-4-7** model on its own, with nothing else around it, is a token generator. It
receives a prompt, returns text, end of story. Everything that makes Claude Code capable of
reading files, running shell commands, opening pull requests and remembering your preferences from
one session to the next does not live inside the model. It lives in a software layer wrapped around
it called the **harness**. Understanding how this layer is built is the difference between using
Claude Code as a black box and truly mastering it, configuring hooks, permissions, skills and
subagents with intention.

## What an Agent Harness Is and Why the Model Alone Is Not Enough

A **harness** (literally a "harness" or "frame") is the software layer that turns a Large Language
Model (LLM, the large-scale language model that generates text) into an autonomous agent capable of
taking actions in the real world. When you interact with Claude through the claude.ai web app, the
harness is minimal and lets you do little more than chat. When you launch `claude` from the
terminal, by contrast, the harness is hefty and manages the filesystem, permissions, sandbox, MCP,
hooks and session history.

The clearest definition comes from the official Anthropic documentation: *"Claude Code serves
as the agentic harness around Claude: it provides the tools, context management, and execution
environment that turn a language model into a capable coding agent."* In other words, the same model
that inside claude.ai is limited to producing replies can, inside Claude Code, modify your source
code, run tests and commit the result. The difference lies entirely in the harness.

To grasp the scope of this distinction, consider the typical Claude Code work cycle, which the
documentation describes in three phases: **gather context**, **take action**, and **verify
results**. None of these three phases is executed by the model in the strict sense. The model
decides what to do, but it is the harness that reads files, launches shell commands, checks
permissions, saves the conversation and handles networking.

## The Agent Loop: A Surprisingly Simple Core

The heart of the harness is a very simple `while` loop, a structure the MBZUAI academic paper later
quantified: 98.4% infrastructure, 1.6% AI logic, described in pseudocode by those who have
decompiled the Claude Code binary:

```python
# Main harness loop (simplified)
while needs_follow_up:
    history = gather_conversation_history()
    response = call_model(history, tools=available_tools)
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        history.append(result)
    needs_follow_up = response.stop_reason != "end_turn"
```

All the perceived magic of Claude Code, the apparent intelligence with which it explores a
repository, figures out where the bug lives and proposes a fix, comes from this iterative cycle that
the harness closes tightly around the model. The model is not "aware" of the loop. At each
invocation it sees only the accumulated history, decides whether to call a tool or return final
text, and the harness handles the rest. Anthropic deliberately avoided complex planning systems: no
search trees, no elaborate reflection. Just a loop of tool calls that stops when the model declares
`end_turn`.

## The Real Components of the Claude Code Runtime

Beneath the loop, the Claude Code harness assembles at least eight independent components that make
up the runtime. Knowing them by name helps you configure each one carefully, since each has its own
settings files, commands and dedicated logs.

### 1. Tool Executor

This is the module that receives a `tool_use` block from the model (the structured request to run a
tool) and turns it into a real action. According to the documentation, the native tools fall into
five categories: file operations (Read, Write, Edit), search (Glob, Grep), execution (Bash with
Seatbelt sandbox on macOS or Landlock on Linux), web (WebFetch, WebSearch) and code intelligence
(definitions, references, compiler errors). Every execution is bound to the original request through
a `call_id`, so the model can reconstruct cause and effect.

### 2. Permission Manager

Before a tool actually runs, the harness checks permissions. There are four modes, cyclable with
`Shift+Tab` from the CLI: **default** (asks for confirmation on edits and commands), **auto-accept
edits** (auto-approves file edits but still asks for commands), **plan mode** (read-only tools only,
the user approves a plan before moving to execution) and **auto mode**, introduced in March 2026 as
a research preview. This last mode is particularly interesting because it evaluates each action
through a background safety classifier running on Sonnet 4.6 that sees only the user request and the
tool call, but not the prose from the main model: a design built precisely to prevent the model from
talking the harness into letting risky actions through.

### 3. Hook System

Hooks are shell commands that the harness runs in response to lifecycle events. The current
documentation lists twelve of them, including `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
`PostToolUse` and `Stop`. Configuring them in `settings.json` lets you inject context, block
dangerous commands, log audit trails, and integrate with external build systems.

### 4. Context Manager

Claude's context window (the set of tokens the model sees at every call) has a hardware limit: 200K
tokens in standard versions, 1M tokens in some enterprise configurations. The harness manages this
budget with five overlapping techniques: cleanup of older tool outputs, automatic conversation
compaction (auto-compact), prompt caching with a five-minute TTL, lazy loading of MCP schemas
through tool search, and skill snapshots that load only when needed. When the context grows too
full, the harness compacts and preserves user requests and key code snippets, while the
conversation's opening instructions can be lost. That is why Anthropic recommends putting persistent
rules inside `CLAUDE.md`.

### 5. MCP Layer

The **Model Context Protocol** (MCP, the open standard Anthropic released in late 2024 to connect
models to external tools) is the mechanism the harness uses to add third-party tools without having
to be recompiled. An MCP server defines a set of tools in JSON, along with their descriptions and
input schemas. The harness acts as the client, presents the tools to the model as if they were
native, and handles routing and authentication. To reduce token consumption, MCP schemas are
*deferred*: the model sees only tool names until it uses a specific one, at which point the full
schema is loaded through tool search.

### 6. Skill System

**Skills** are bundles of markdown and scripts that encapsulate domain knowledge in a modular way.
Each skill is a directory with a `SKILL.md` file that carries YAML frontmatter (a header with
structured metadata) and a *description* that the model reads at the start of the session. The full
content of the skill is loaded into context only when the model invokes it through the dedicated
tool, which keeps the token cost low. Anthropic has opened an official repository of common skills
and a community of plugins is growing around it.

### 7. Subagent Framework

**Subagents** are model instances with a separate context window and a configurable subset of tools,
spawnable from the main model through the `Agent` tool. They serve three practical purposes:
parallelizing independent work, isolating heavy research so it does not saturate the main
conversation, and specializing an agent on a domain (frontend, security, debugging). The subagent
receives an initial prompt, runs its own private loop and returns a single summary message to the
caller. They are configured in Markdown files with frontmatter under `.claude/agents/` at the
project level or `~/.claude/agents/` at the user level.

### 8. Session Storage

Every conversation is saved in JSONL format (a text file with one JSON object per line) under
`~/.claude/projects/`. This choice has three concrete consequences: you can *resume* an interrupted
session with `claude --continue`, you can *fork* it with `--fork-session` or `/branch` to explore
alternative paths without losing the original, and you can *rewind* individual edits through the
checkpoint system that snapshots files before modifying them. Rewind is triggered by pressing `Esc`
twice. It is a local mechanism, separate from git, that covers only file edits and not side effects
on remote systems like databases or APIs.

## The Three Execution Environments

The Claude Code harness can run in three environments, each with different tradeoffs:

**Local:** the default. The code runs on your machine, and the harness has full access to the
filesystem, terminal and git state. Maximum freedom, maximum responsibility.

**Cloud:** the code runs on VMs managed by Anthropic. Useful for offloading long tasks and working
on repositories you do not have locally. The harness is the same; what changes is the filesystem
underneath.

**Remote Control:** the code runs on your machine, but you control the harness through a browser. It
bridges the web UI with the power of the local setup.

## Settings.json: The Hierarchy That Rules Everything

The harness configuration file is `settings.json` and follows a three-tier hierarchy that merges in
cascade: `~/.claude/settings.json` for global user preferences, `<repo>/.claude/settings.json` for
the project (committable), and `<repo>/.claude/settings.local.json` for private overrides (not
committable). The more local settings win over the more global ones. The main fields are
`permissions` (allowlist and denylist of tool patterns), `hooks` (event-to-command map), `env`
(environment variables exposed to the tools), `model` (override of the default model), and
`statusLine` (custom badge in the bottom-left corner of the CLI).

An often-underestimated feature is the `CLAUDE.md` file at the project level: the harness reads it
on every startup and injects it into the system prompt as stable instructions. The same is true of the
*auto-memory* system that saves learnings from one session to the next inside
`~/.claude/projects/<repo>/memory/`.

## Comparison with Codex and Cursor

Understanding the Claude Code harness is easier when you place it next to its competitors. **OpenAI
Codex** integrates the harness more tightly with the model API: tool calling is native to the model
spec rather than a separate layer, which reduces the translation overhead between model and runtime.
**Cursor**, by contrast, optimizes for IDE integration and maintains a code index that retrieves
relevant context instead of loading entire files. Each of the three approaches has its strengths and
weaknesses: Claude Code prioritizes transparency with explicit approval gates for every destructive
operation, Codex trims latency by coupling harness and model, and Cursor reduces context bloat by
leaning on retrieval.

## Harness Security: The Real Differentiator

**Caution:** the main risk of the harness is not the model "going rogue", but the model executing
instructions injected into external content (files, web pages, tool output, emails). This threat is
called *prompt injection*, and it is the reason the harness adds hard-coded defenses that the model
cannot disable.

The harness implements a set of immutable rules in the system prompt that forbid destructive actions
without user confirmation, isolate content from untrusted sources, and filter output for copyright
and privacy. Anthropic has invested heavily in this layer, partly because an agent that runs code on
your filesystem is a very attractive attack vector.

## Frequently Asked Questions (FAQ)

### 1. Can I use the Claude Code harness with another LLM?

**No, not officially.** The Claude Code harness is designed to talk to Claude models through the
Anthropic API. There are open source projects that try to abstract the harness and make it
model-agnostic, such as OpenHarness and everything-claude-code, but they do not match the feature
parity of the official version and lose some Claude-specific optimizations like native prompt
caching and deferred tools.

### 2. What is the difference between Claude Code (the CLI) and the Claude Agent SDK?

**The SDK is the harness without the CLI.** The Claude Agent SDK exposes in Python and TypeScript
the same primitives that power Claude Code: agent loop, tool definitions, MCP client, context
management. You use it when you want to build a custom agent inside your application instead of a
terminal assistant. Underneath, it is the same runtime: the model, the loop, and the tool handling
are identical.

### 3. How many tokens does the harness really consume on top of the user prompt?

**Between 10K and 50K tokens of system overhead alone.** The harness system prompt takes up several
thousand tokens between safety rules, tool definitions, and base instructions. On top of that you
have CLAUDE.md (variable), auto-memory (capped at 25KB), descriptions of skills loaded but not yet
invoked, and the initial git state dump.

### 4. Does the harness work offline?

**Only for local tools, not for the model.** Filesystem, Bash, Glob and Grep run locally and require
no network access. But every iteration of the loop has to call the Anthropic API to get the model's
next decision, so the agent does not progress without a connection.

### 5. Can I write my own custom harness?

**Yes, and that is exactly what the Claude Agent SDK does.** You can import the SDK in Python or
TypeScript, configure the tools you want to expose, define the system prompt, manage permissions,
and effectively build a harness tailored to your use case.

## Conclusions

**The harness is where the real product design lives.** The model is an interchangeable commodity,
while the harness is what determines an agent's safety, ergonomics, real-world costs and
productivity. When you compare Claude Code to Codex or Cursor, you are not comparing models. You are
comparing different harnesses running on top of similar models.

For anyone who wants to get the most out of Claude Code, I recommend three concrete moves: configure
`settings.json` and `CLAUDE.md` with care, write modular skills instead of monolithic prompts, and
invest in hooks to automate safety checks. The Anthropic conference confirmed that the product roadmap is heading in this direction: less prompt
engineering, more harness engineering.
