# E2B Coding Agents

**Source:** https://www.e2b.dev/docs/use-cases/coding-agents

## Overview
Run AI coding agents like Claude Code, Codex, and Amp in secure E2B sandboxes with full terminal, filesystem, and git access.

## Why Use a Sandbox
Running coding agents directly on your machine or servers means giving AI-generated code unrestricted access to your environment. E2B sandboxes solve this:

1. **Isolation** — agent-generated code runs in a secure sandbox, never touching your production systems or local machine
2. **Full dev environment** — terminal, filesystem, git, and package managers are all available out of the box, so agents work like a developer would
3. **Pre-built templates** — ready-made templates for popular agents get you started fast, and you can build your own for any agent
4. **Scalability** — run many sandboxes in parallel, each with its own agent on a separate task

## How It Works

1. **Create a sandbox** — use a pre-built template or build your own with any agent installed
2. **Agent gets a full environment** — terminal, filesystem, git access, and any tools installed in the template
3. **Agent works autonomously** — it reads the codebase, writes code, runs tests, and iterates until the task is done
4. **Extract results** — pull out the git diff, structured output, or modified files via the SDK. The sandbox stays available for follow-up work, or you can pause it to pick up later

## Supported Agents

### Claude Code
Anthropic's autonomous coding agent with structured output and MCP tool support

### Codex
OpenAI's coding agent with schema-validated output and image input

### Amp
Coding agent with streaming JSON and thread management

### OpenCode
Open-source multi-provider agent with a built-in web UI

### Mastra
Build custom TypeScript coding agents with E2B-backed workspaces

## Related Features

### Git Integration
Clone repos, manage branches, and push changes from sandboxes

### Sandbox Persistence
Pause and resume sandboxes to preserve state

### Custom Templates
Build your own sandbox templates with custom tools and dependencies
