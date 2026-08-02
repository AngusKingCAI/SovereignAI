# Extensibility Overview

Customize and extend Devin CLI with rules, skills, and MCP servers

Devin CLI is designed to be deeply customizable. You can shape how the agent behaves, what tools it has access to, and how it responds to events — all through configuration files in your project or home directory.

## Extensibility Features

- **Rules & AGENTS.md** - Provide always-on context and instructions that guide the agent's behavior across every session.
- **Skills** - Create reusable prompts and workflows the agent can invoke as slash commands or use autonomously.
- **Plugins** - Install and share bundles of skills across projects.
- **Custom Subagents** - Define specialized subagent profiles with their own system prompts, tools, and models.
- **MCP Servers** - Connect external tool servers to give the agent access to APIs, databases, and more.
- **Hooks** - Run shell commands or LLM prompts at key points in the agent's lifecycle to enforce policies and automate workflows.

## How It All Fits Together

These features work at different layers:

- **Rules** shape the agent's personality and constraints — they're always active.
- **Skills** give the agent new capabilities it can invoke on demand.
- **Custom Subagents** define specialized worker profiles the agent can delegate tasks to.
- **MCP Servers** provide entirely new tools the agent can call.
- **Hooks** run shell commands or LLM prompts at lifecycle events (e.g., before a tool runs) to enforce policies or trigger workflows.

You can combine all of these in a single project. For example, you might have an `AGENTS.md` file with coding standards, a `review` skill for code review, an MCP server for your issue tracker, and hooks to block destructive commands.

## Where Configuration Lives

All project-level extensibility configuration lives in the `.devin/` directory at your project root:

```
my-project/
├── .devin/
│   ├── config.json          # Project config (MCP, permissions)
│   ├── config.local.json    # Personal overrides (gitignored)
│   ├── hooks.v1.json        # Lifecycle hooks (Claude Code compatible)
│   ├── skills/
│   │   └── review/
│   │       └── SKILL.md     # A custom skill
│   └── agents/
│       └── reviewer/
│           └── AGENT.md     # A custom subagent profile
├── AGENTS.md                # Project rules
└── src/
```

User-level configuration lives in `~/.config/devin/` and applies to all projects. On Windows, this path is `%APPDATA%\devin\` instead.

**Tip**: Files with `.local.` in the name are automatically excluded from git, so you can have personal overrides without affecting your team.

## Importing From Other Tools

Devin CLI can read configuration from other AI coding tools you may already use:

| Source | What's Imported |
|--------|----------------|
| `AGENTS.md` / `AGENT.md` / `CLAUDE.md` | Rules (always-on context) |
| `.cursor/rules/*.md` / `.cursor/rules/*.mdc` | Rules |
| `.windsurf/rules/*.md` | Rules |
| `.claude/` directory | Commands, custom subagents, hooks |

This means you can start using Devin CLI without rewriting your existing configuration. Import is enabled by default and can be controlled in your config file:

```json
{
  "read_config_from": {
    "cursor": true,
    "windsurf": true,
    "claude": true
  }
}
```

Set any provider to `false` to disable importing from it.