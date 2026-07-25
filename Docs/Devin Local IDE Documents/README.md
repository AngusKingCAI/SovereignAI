# Devin Local IDE Documentation

Complete documentation for Devin Local CLI and Devin Desktop IDE

## Table of Contents

### 1. Getting Started
- [Quickstart](./01-Getting-Started/Quickstart.md) - Get up and running in 2 minutes with Devin CLI

### 2. Essential Commands
- [Essential Commands](./02-Essential-Commands/Essential-Commands.md) - Must-know commands and slash commands

### 3. Models
- [Models](./03-Models/Models.md) - Available models and how to configure them

### 4. Extensibility
- [Extensibility Overview](./04-Extensibility/Extensibility-Overview.md) - Customize and extend Devin CLI with rules, skills, and MCP servers
- [Configuration](./04-Extensibility/Configuration.md) - How to configure Devin CLI behavior with config files
- [Skills Overview](./04-Extensibility/Skills-Overview.md) - Create reusable prompts and workflows that extend the agent's capabilities
- [Plugins Overview](./04-Extensibility/Plugins-Overview.md) - Install and share bundles of skills from repos, git URLs, or local folders
- [MCP Overview](./04-Extensibility/MCP-Overview.md) - Extend Devin CLI with external tool servers using the Model Context Protocol

### 5. Reference
- [Commands & Flags](./05-Reference/Commands.md) - Complete reference for command arguments, subcommands, and interactive slash commands
- [Configuration File](./05-Reference/Configuration-File.md) - Complete reference for the Devin CLI config file format
- [Permissions](./05-Reference/Permissions.md) - Control what the agent can do with fine-grained permission rules

### 6. Advanced Features
- [Handoff](./06-Advanced-Features/Handoff.md) - Hand off a task from the Devin CLI to a cloud Devin session
- [Subagents](./06-Advanced-Features/Subagents.md) - Delegate tasks to independent subagents that work in the foreground or background
- [Shell Integration](./06-Advanced-Features/Shell-Integration.md) - Wrap your shell with Devin to invoke it instantly and give Devin visibility into your recent commands
- [Sandbox](./06-Advanced-Features/Sandbox.md) - OS-level isolation for Devin CLI sessions

### 7. Enterprise
- Enterprise documentation available through Devin Desktop settings

### 8. Troubleshooting
- [Troubleshooting](./08-Troubleshooting/Troubleshooting.md) - Common issues and how to fix them

## Quick Links

### Installation
- [Quickstart Guide](./01-Getting-Started/Quickstart.md)
- [Troubleshooting Installation](./08-Troubleshooting/Troubleshooting.md#installation-issues)

### Core Features
- [Essential Commands](./02-Essential-Commands/Essential-Commands.md)
- [Models](./03-Models/Models.md)
- [Permissions](./05-Reference/Permissions.md)

### Customization
- [Configuration](./04-Extensibility/Configuration.md)
- [Skills](./04-Extensibility/Skills-Overview.md)
- [MCP Servers](./04-Extensibility/MCP-Overview.md)

### Advanced Usage
- [Subagents](./06-Advanced-Features/Subagents.md)
- [Handoff](./06-Advanced-Features/Handoff.md)
- [Sandbox](./06-Advanced-Features/Sandbox.md)

## Key Concepts

### Modes
Devin CLI has multiple permission modes:
- **Normal** - Auto-approves read-only tools, prompts for writes/commands
- **Accept Edits** - Auto-approves file edits in workspace
- **Bypass** - Auto-approves all tool calls
- **Autonomous** - Used with sandbox for contained execution

### Configuration Levels
- **User config** (`~/.config/devin/config.json`) - Personal defaults
- **Project config** (`.devin/config.json`) - Shared team settings
- **Local overrides** (`.devin/config.local.json`) - Personal project overrides

### Permission System
Three types of permission rules:
- **Allow** - Actions that proceed without prompting
- **Deny** - Actions that are blocked
- **Ask** - Actions that always prompt for approval

## Getting Help

- Run `/help` in any Devin CLI session for available commands
- Check [Troubleshooting](./08-Troubleshooting/Troubleshooting.md) for common issues
- Use `/bug` to report bugs to the Devin CLI developers

## Documentation Source

This documentation is sourced from the official Devin CLI documentation available at:
`\\?\C:\Users\King\AppData\Local\Programs\Devin\resources\app\extensions\windsurf\devin\share\devin\docs`

For the most up-to-date documentation, please refer to the official Devin documentation at https://docs.devin.ai