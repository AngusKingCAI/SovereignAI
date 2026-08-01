# Anthropic CWC Long-Running Agents

**Source:** https://github.com/anthropics/cwc-long-running-agents

## Overview
Harness primitives for long-running Claude agents. This repository provides the same underlying primitives as Claude Code's built-in `/goal` command as short, readable hooks and a subagent, so you can see how each mechanism works and assemble a harness tuned to your project.

## Comparison: In-product vs Custom Harness

| Feature | In-product | Custom harness (this repo) |
|---------|------------|----------------------------|
| **What runs the loop** | `/goal` command | the primitives below + a loop you write |
| **Who judges "done"** | a separate fast model checking your condition | your `agents/evaluator.md` with your prompt |
| **Where it works** | Claude Code interactive, `-p`, Remote Control | Claude Code, headless, or Agent SDK |

## Repository Structure
- `claude-code-config` - Claude Code configuration files
- `README.md` - Documentation and usage instructions
- `LICENSE` - Apache-2.0 license

## Key Features
- Generator/evaluator loop primitives
- Hooks for long-running agent workflows
- Subagent implementation examples
- Patterns from Anthropic's harness engineering research

## Background
The patterns come from:
- "Effective Harnesses for Long-Running Agents" (Nov 2025)
- "Harness Design for Long-Running Application Development" (Mar 2026)

## Usage
This repository provides the building blocks for creating custom harnesses for long-running Claude agents. It's recommended to try both the in-product features and a custom harness to see which fits your workflow.

## Related
- Claude Code's built-in `/goal` command
- Anthropic's harness engineering research
- Long-running agent patterns and best practices
