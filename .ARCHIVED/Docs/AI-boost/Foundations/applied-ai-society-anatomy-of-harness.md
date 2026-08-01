# Anatomy of a Harness: Lessons from Claude Code's Source

**Source:** https://docs.appliedaisociety.org/docs/concepts/anatomy-of-a-harness

**Description:** This article provides a deep architectural analysis of Claude Code's source code when it became publicly visible in March 2026. It breaks down the ten major subsystems of the harness and provides practical lessons for practitioners building their own agent systems.

---

# Anatomy of a Harness: Lessons from Claude Code's Source

In March 2026, Claude Code's source code became publicly visible. For the first time, we could
study the internals of the most capable AI harness in the world. Here is what we found, and what it
teaches practitioners about building their own systems.

## What Happened

In late March 2026, the full TypeScript source code for Claude Code (Anthropic's agentic coding
tool) surfaced publicly via community mirrors on GitHub. The codebase is roughly 800,000
lines in its main module alone, with over 50 directories covering tools, hooks, skills, memory,
context assembly, state management, plugins, and the core agent loop.

For anyone who has read the Harness Engineering article, this is an extraordinary
opportunity. That article argued that the code wrapped around an AI model is just as important as
the model itself, and cited the MetaHarness research showing 6x performance gaps from harness
variations alone. Now we can see exactly how the best harness in the world is built. Not in theory.
In source code.

## The Big Picture

Claude Code is not a chatbot with file access. It is a state machine that assembles context,
dispatches tools, manages permissions, tracks budgets, and recovers from failures, all wrapped
around a single model call in a loop. The model (Claude) provides the intelligence. The harness
provides everything else.

The architecture breaks into ten major subsystems:
1.  **The Agent Loop** (the heartbeat)
2.  **Context Assembly** (what the model sees)
3.  **Tools** (what the model can do)
4.  **Hooks** (event-driven extensibility)
5.  **Skills** (data-driven commands)
6.  **Memory** (persistent knowledge)
7.  **Tasks** (background work)
8.  **Commands** (user interface)
9.  **State** (session tracking)
10. **Plugins** (extensible capabilities)

## 1. The Agent Loop Is a State Machine

The most important file in the entire codebase is `query.ts`. It contains the main agent loop, and
it is not recursive. It is a pure state machine.

Each iteration of the loop follows the same pattern:
1. Assemble the current state (messages, tools, context, budget)
2. Normalize messages for the API (strip internal metadata, reorder attachments, merge thinking
   blocks)
3. Call the model
4. Stream the response (thinking blocks, text, tool calls)
5. Execute requested tools
6. Check continue conditions (budget remaining? stop hooks triggered? end_turn?)
7. Loop or exit

The state is split cleanly into two categories: **immutable parameters** (system prompt, model
config, available tools) and **mutable state** (messages, turn count, budget tracking, auto-compact
state). At the start of each iteration, the mutable state is destructured. At the end, it is
reconstructed. This prevents bugs from accidental cross-iteration mutation.

**Recovery is explicit, not hidden.** When the model hits its output token limit, the loop retries
up to three times with an increased budget. When the context gets too long, it triggers automatic
compaction (summarizing earlier conversation to free space). When a tool fails, it retries. Each
recovery path is a visible branch in the state machine, not a try/catch buried somewhere.

### Why This Matters for Practitioners

If you are building any kind of agent workflow (for a client, for your own operation, for a
product), the lesson is: **treat the agent loop as engineering, not magic.** The model is one
function call inside a larger system. Everything around that call (what context goes in, what
happens with tool results, how you handle failures, when you stop) is your responsibility to design.

The MetaHarness paper showed that changing this loop produces a 6x performance gap. Now we
can see exactly what "changing the loop" means in practice: it means changing how you assemble
context, which tools you offer, when you retry versus stop, and how you manage the token budget.

## 2. Context Assembly Is Layered and Lazy

Claude Code does not dump everything into the system prompt. It assembles context in layers, each
with different lifecycle and caching behavior.

**Layer 1: System prompt.** The base instructions that define what the model is and how it should
behave. This is static within a session. It includes the tool descriptions, behavioral guidelines,
and formatting rules.

**Layer 2: System context.** Runtime state like git branch, recent commits, working directory, and
platform info. This is memoized (computed once, cached, and reused). It resets between sessions but
stays stable within one.

**Layer 3: User context.** CLAUDE.md files discovered from the project tree, current date, and user
preferences. Also memoized. This is the layer that makes Claude Code project-aware.

**Layer 4: Memory attachments.** Relevance-filtered files from the
`~/.claude/projects/<slug>/memory/` directory. These are prefetched in parallel while the model is
streaming its response, so by the time the model needs to call a tool, memory is already loaded.
This is a performance optimization that most harnesses miss.

**Layer 5: Skill content.** Loaded on demand, only when a skill is invoked. The skill index (names
and descriptions) loads upfront. The full skill content (the actual instructions) loads only when
the model decides to use that skill.

### The Economics Are Deliberate

This architecture directly reflects the economics described in the Context Engineering article: "load the minimum sufficient context for the task at hand." Claude Code does not load every
CLAUDE.md, every memory file, and every skill on every turn. It loads the base, caches what's
stable, prefetches what's likely, and lazy-loads everything else.

The 200-line, 25KB limit on the MEMORY.md index is a hard constraint. If your memory index exceeds
this, it gets truncated with a warning. This is not a bug. It is a design choice: the memory index
must fit in context without crowding out the actual work.

## 3. Tools Are Loosely Coupled Through Dependency Injection

Claude Code ships with over 30 tools: file I/O (Read, Write, Edit, Glob, Grep), execution (Bash),
agents (Agent tool for subagents), skills (SkillTool), task management (TaskCreate, TaskUpdate), web
access (WebSearch, WebFetch), and more.

Every tool follows the same interface:
* **Name and aliases** (how the model calls it)
* **Input schema** (Zod-validated, converted to JSON Schema for the API)
* **Execute function** (receives input and a `ToolUseContext`, returns a `ToolResult`)
* **Optional prompt and progress functions** (for dynamic descriptions and status updates)

The critical design choice: tools receive all their dependencies through `ToolUseContext`, a shared
context object that carries the current state, permission settings, file cache, MCP clients, abort
signals, and message store. Tools never import each other. They never import the main loop. They
never access global state.

This is dependency injection, and it has three consequences:
1. **Tools are testable in isolation.** You can construct a mock `ToolUseContext` and test any tool
   without running the full agent loop.
2. **Tools are composable.** The Agent tool launches subagents that have their own tool sets and
   contexts. Because tools don't reach into global state, subagents cannot corrupt the parent's
   state.
3. **Tools are feature-gatable.** A `feature('FLAG')` check at load time determines whether a tool
   is registered. Unused tools are stripped by the bundler. Different users get different tool sets
   from the same codebase.

## 4. The Permission System Is Intent Engineering in Code

Before any tool executes, it passes through `canUseTool()`. This function checks the tool call
against three rule sets:
* **Always allow rules:** Actions the user has pre-approved (e.g., "always allow Read on any file in
  this project")
* **Always deny rules:** Actions the user has forbidden (e.g., "never allow Bash commands with `rm
  -rf`")
* **Always ask rules:** Actions that require explicit approval each time

Hooks can intercept this process and auto-approve or auto-deny via structured JSON responses. This
means organizations can encode their intent into hook configurations: "when an agent tries to push
to main, always ask." "When an agent reads a file in the project directory, always allow." "When an
agent tries to install a package, check against the approved list."

This is exactly the Intent Engineering pattern: organizational values translated into
decision boundaries that agents respect autonomously.

## 5. Skills Are Specs, Not Code

This is one of the most important insights from the source code, and it directly validates "The Spec
Is the Product."

Skills in Claude Code are markdown files with YAML frontmatter. They are not TypeScript. They are
not compiled. They are plain text documents that describe a workflow, and the model follows them.

A skill file contains:
* **Name and description** (for discovery and matching)
* **When to use** (triggers and relevance criteria)
* **Allowed tools** (which tools the skill can access)
* **Model override** (optionally run on a different model)
* **The actual instructions** (markdown describing the workflow step by step)

The harness discovers skills from three locations: bundled skills shipped with the CLI, project
skills in `.claude/skills/`, and user skills in `~/.claude/skills/`. It loads only the metadata
(name, description) upfront. The full content loads only when the model decides to invoke a skill.

Here is what this means: **the quality of your skill file directly determines the quality of the
agent's output.** A vague skill file produces vague behavior. A precise skill file produces precise
behavior. Same model. Same harness. Same tools. The only variable is the spec.

This is the quality chain from "The Spec Is the Product" made real: **Spec quality -> System
quality -> Outcome quality.** Every skill file you write for your Personal Agentic OS is a spec.
Every CLAUDE.md is a spec. Every instruction you put in a context file is a spec. The model executes
them literally.

## 6. Memory Is Declaratively Indexed

Claude Code's memory system lives in `~/.claude/projects/<slug>/memory/`. It consists of:
* **MEMORY.md:** A master index file (200-line limit, 25KB max) containing one-line pointers to
  individual memory files
* **Individual memory files:** Markdown files with typed frontmatter (user, feedback, project,
  reference)
* **An auto-discovery system** that finds and attaches relevant memories at the start of each turn

The index is always loaded. Individual files are loaded when relevant. The model can write new
memories, update existing ones, and delete stale ones.

Three design choices stand out:

**Typed memories with structured frontmatter.** Each memory has a type (user, feedback, project,
reference), a name, and a description. The type tells the system when this memory is relevant. The
description helps with discovery. This is not a blob of text. It is structured knowledge with
metadata.

**Bounded index size.** The 200-line limit forces prioritization. You cannot store everything. You
must decide what matters. This constraint is a feature: it prevents the context window from being
consumed by memory overhead, leaving room for the actual work.

**Write-through pattern.** The model writes memories in a two-step process: first write the memory
file, then update the index. This ensures the index stays in sync with the files. If the model
writes a file but fails to update the index, the memory exists on disk but won't be discovered. This
is a deliberate trade-off: consistency of the index is more important than completeness.

This architectural analysis demonstrates that sophisticated harness engineering involves careful design of state management, context assembly, tool systems, permission layers, and declarative specifications. The Claude Code source provides a real-world example of these principles in practice.
