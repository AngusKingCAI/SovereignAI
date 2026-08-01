# Awesome Harness Engineering (ecosyste.ms)

**Source URL:** https://awesome.ecosyste.ms/lists/ai-boost%2Fawesome-harness-engineering

**Description:** This resource provides an API-indexed view of the awesome-harness-engineering list, offering structured data access to the curated collection of AI agent harness engineering resources. It includes tools, patterns, evals, memory systems, MCP (Model Context Protocol), permissions, observability, and orchestration resources. The ecosyste.ms platform provides this as an open API service indexing awesome lists of open source software, making the content available in machine-readable JSON format for programmatic access.

---

# Web Content from https://awesome.ecosyste.ms/lists/ai-boost%2Fawesome-harness-engineering

# [ecosyste.ms][1]

[All services ][2]

## Data
* [ Packages ][3]
* [ Repositories ][4]
* [ Advisories ][5]

## Tools
* [ Dependency Parser ][6]
* [ Dependency Resolver ][7]
* [ SBOM Parser ][8]
* [ License Parser ][9]
* [ Digest ][10]
* [ Archives ][11]
* [ Diff ][12]
* [ Summary ][13]

## Indexes
* [ Timeline ][14]
* [ Commits ][15]
* [ Issues ][16]
* [ Sponsors ][17]
* [ Docker ][18]
* [ Open Collective ][19]
* [ Dependabot ][20]

## Applications
* [ Funds ][21]
* [ Dashboards ][22]

## Experiments
* [ OST ][23]
* [ Papers ][24]
* [ Awesome ][25]
* [ Ruby ][26]

# [Awesome ][27]

An open API service indexing awesome lists of open source software.
* [Support][28]
* [GitHub][29]
* [API][30]

# awesome-harness-engineering

Awesome list for AI agent harness engineering: tools, patterns, evals, memory, MCP, permissions,
observability, and orchestration.
[https://github.com/ai-boost/awesome-harness-engineering][31]

Last synced: 1 day ago
[JSON representation][32]
* ## Acknowledgments
  * ### Adjacent Collections
    * [linux.do][33]
* ## Design Primitives
  * ### Agent Loop
    * [ReAct: Synergizing Reasoning and Acting in Language Models][34] - acting cycle.
    * [LangGraph — Low Level Concepts][35] - loop state for resumption.
    * [Unlocking the Codex Harness: How We Built the App Server][36] - dive into the
      Item/Turn/Thread protocol (JSON-RPC/JSONL over stdio) that exposes the Codex harness to every
      client surface. The most direct first-party account of why approval flows, streaming diffs,
      and thread persistence demand a purpose-built protocol — and why MCP's tool-oriented model
      proved insufficient for these requirements.
    * [Improving Deep Agents with Harness Engineering][37] - only changes moved their coding agent
      from rank 30 to top 5 on Terminal Bench 2.0 with no model swap: structured verification loops,
      context injection (directory maps + time budget warnings), loop-detection middleware, and a
      "reasoning sandwich" concentrating maximum thinking at planning and verification phases. The
      most concrete published demonstration that harness design is the primary performance lever,
      not model capability.
    * [Agents Learn Their Runtime: Interpreter Persistence as Training-Time Semantics][38] - time
      semantics produces either 80% missing-variable errors (model expects state that doesn't
      persist) or 3.5× token overhead (model redundantly recomputes state it expects to already
      have). Persistence is a learned semantic that must be honored at deployment, not a free
      runtime choice.
    * [Real-Time Deadlines Reveal Temporal Awareness Failures in LLM Strategic Reasoning][39] -
      constrained tasks. Indicates temporal semantics as a learned behavior that must be integrated
      into harness-level context (current time, deadlines, time budgets) rather than assumed from
      capability alone.
    * [A Scheduler-Theoretic Framework for LLM Agent Execution][40] - source LLM agent projects
      showing 60% adopt the Agent Loop pattern. Proposes a formal scheduler framework that maps
      execution patterns (Agent Loop, Event-driven, State-machine, Graph/flow, Hybrid) onto a
      unified control model, making the controllability/expressiveness/implementability trade-offs
      explicit. Essential reading for choosing the right loop architecture rather than defaulting to
      the simplest pattern.
    * [Confucius Code Agent (CCA)][41] - grade coding agent from Meta/Harvard built on the Confucius
      SDK, which structures harness design around three perspectives: Agent Experience (AX), User
      Experience (UX), and Developer Experience (DX). Features a unified orchestrator with advanced
      context management, persistent note-taking for cross-session learning, and a meta-agent that
      automates build-test-improve cycles. Achieves 59% Resolve@1 on SWE-Bench-Pro, exceeding prior
      research and commercial baselines.
    * [The Design Space of Today's and Future AI Agent Systems][42] - engineering of Claude Code's
      architecture revealing five-stage progressive compaction (budget reduction → snip →
      microcompact → context collapse → auto-compact), subagent isolation with rebuilt permission
      contexts, and a 27-event-type hook pipeline. The most detailed public analysis of a production
      agent loop's internal design decisions — essential for understanding how context pressure,
      safety, and delegation are handled at scale.
    * [deepclaude][43] - compatible backends while preserving the same UX. The strongest practical
      evidence that loop architecture — not model identity — determines agent behavior, and a
      concrete starting point for building backend-agnostic harnesses.
      ![Stars](https://img.shields.io/github/stars/aattaran/deepclaude?style=flat-square&label=★&col
      or=yellow)
    * [The Coding Harness Behind GitHub Copilot in VS Code][44] - provider model routing across
      Anthropic, Google, OpenAI, xAI, and Mistral, and the VSC-Bench eval suite with PR-gated
      assessment. The clearest published account of how a major product treats harness changes as
      first-class code review criteria — "the model is the engine, the harness is the car."
    * [statewright][45] - ended loops into deterministic state transitions. The research result is
      striking: local models went from 2/10 to 10/10 passing on a SWE-bench subset purely by
      shrinking the tool space, proving that loop structure — not model size — is the binding
      constraint.
      ![Stars](https://img.shields.io/github/stars/statewright/statewright?style=flat-square&label=★
      &color=yellow)
    * [Hooks – Codex][46] - hook framework for Codex: inject deterministic scripts at
      `SessionStart`, `PreToolUse`, `PostToolUse`, and other loop events to enforce guardrails,
      audit actions, and customize agent behavior without relying on prompt-level trust. A concrete
      reference for programmable harness governance.
    * [Life-Harness][47] - aware runtime harness that improves frozen LLM agents by adapting the
      model-environment interface across four layers: environment contract, procedural skills,
      action realization, and trajectory regulation. The key result is that harness-side adaptation
      transfers across 18 model backbones, proving that many agent failures are interface mismatches
      rather than reasoning deficits.
      ![Stars](https://img.shields.io/github/stars/Tianshi-Xu/Life-Harness?style=flat-square&label=★&color=yellow)
    * [Introducing dynamic workflows in Claude Code][48] - line Bun Zig-to-Rust port. The key
      harness insight is that the plan lives in executable code rather than the model's context
      window, scaling the agent loop to work that would otherwise exceed a single context window.
    * [Getting started with loops][49] - based, goal-based (`/goal`), time-based (`/loop`,
      `/schedule`), and proactive loops. The framework for matching loop primitive to task shape —
      and the emphasis on deterministic stop conditions and token budgets — makes it a concise
      reference for choosing the right loop abstraction instead of defaulting to a single
      conversational turn cycle.
    * [AgentSPEX][50] - source specification and execution language for LLM-agent workflows:
      declarative YAML with typed steps, branching, loops, and explicit state management, backed by
      a Docker sandbox with 50+ MCP tools, checkpointing, and trajectory logging. A concrete
      reference for turning ad-hoc agent loops into version-controlled, reproducible harness
      artifacts.
      ![Stars](https://img.shields.io/github/stars/ScaleML/AgentSPEX?style=flat-square&label=★&color
      =yellow)
    * [Loop Engineering][51] - tool starter kits, and CLI tools that score readiness, scaffold
      state, estimate cost, detect drift, and isolate worktrees. The clearest open-source resource
      for moving from one-off prompting to durable, observable agent loops.
      ![Stars](https://img.shields.io/github/stars/cobusgreyling/loop-engineering?style=flat-square&
      label=★&color=yellow)
  * ### Context Delivery & Compaction
    * [Effective Context Engineering for AI Agents][52]
    * [Compaction — Claude API Docs][53] - side context compaction: automatically summarizes older
      context when approaching the window limit. Reduced token consumption by 84% in a 100-turn web
      search eval while allowing agents to complete workflows that would otherwise hit context
      limits.
    * [LLMLingua][54] - 2 adds 3–6x speed gains, making it viable for latency-sensitive agent loops.
      ![Stars](https://img.shields.io/github/stars/microsoft/LLMLingua?style=flat-square&label=★&col
      or=yellow)
    * [Autonomous Context Compression][55] - controlled (compacting at a fixed token threshold) to
      agent-controlled: agents call a dedicated tool to trigger compression when strategically
      appropriate — between tasks or before consuming large inputs. Eliminates the failure mode
      where reactive-at-limit compaction interrupts agents mid-subtask and corrupts in-flight
      reasoning state.
    * [Active Context Compression: Autonomous Memory Management in LLM Agents][56] - enforced policy
      to a model-controlled action. Produces 22.7% token reduction with no accuracy loss on
      long-horizon tasks; the core contribution is making the compression unit semantically coherent
      (the agent decides what knowledge is worth preserving) rather than mechanically
      token-budget-driven.
    * [context-mode][57] - read tool calls with one script execution — is a concrete harness pattern
      for turning context pressure into a programming problem rather than a compression problem.
      ![Stars](https://img… (76 chars truncated)
… (1240 lines truncated)

---

*Note: This content was fetched from ecosyste.ms and saved for offline reference. The full content includes a very extensive list of resources that was truncated during fetching. For the complete JSON representation and full content, visit the source URL.*