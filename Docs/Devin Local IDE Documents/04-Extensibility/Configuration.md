# Configuration

How to configure Devin CLI behavior with config files

Devin CLI is configured through JSON files (with comment support) at the user and project level. These config files control the agent's model, permissions, MCP servers, and more.

## Config File Locations

### User config
**Path:** `~/.config/devin/config.json`

Your personal defaults that apply across all projects. This is where you set your preferred model, theme, and global permissions.

You can also place an `AGENTS.md` file in this directory (`~/.config/devin/AGENTS.md`) to define global rules that apply to every project.

**Note**: On Windows, this path is `%APPDATA%\devin\config.json` (typically `C:\Users\<you>\AppData\Roaming\devin\config.json`).

```json
{
  "agent": { "model": "claude-sonnet-4.5" },
  "permissions": {
    "allow": ["Read(**)", "Exec(git)"]
  }
}
```

### Project config
**Path:** `.devin/config.json` (at your project root)

Shared team configuration committed to version control. Use this for project-specific MCP servers, permission policies, and import settings.

```json
{
  "permissions": {
    "allow": ["Exec(npm run)", "Read(src/**)"],
    "deny": ["Exec(sudo)"]
  },
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

### Local overrides
**Path:** `.devin/config.local.json`

Personal overrides for this project that aren't committed to git (automatically gitignored). Use this for secrets, API keys, and personal preference overrides.

```json
{
  "mcpServers": {
    "github": {
      "env": { "GITHUB_TOKEN": "ghp_your_token" }
    }
  }
}
```

## What You Can Configure

- **Model** - Choose which AI model powers the agent — from Claude Opus to GPT 5.2 to Gemini 3.
- **Permissions** - Pre-approve safe actions, block dangerous ones, and control what the agent can do without asking.
- **MCP Servers** - Connect external tool servers for GitHub, Linear, databases, and any custom APIs.
- **External Tool Imports** - Import rules, skills, and configuration from Cursor, Windsurf, and Claude Code.

## Quick Start

The fastest way to get started is to create a `.devin/config.json` in your project root:

```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Exec(git)",
      "Exec(npm run)"
    ]
  }
}
```

This pre-approves file reads and common commands so the agent doesn't prompt you for every action.

**Tip**: You can also configure Devin CLI interactively: when the agent asks for permission, choose to save the decision to your project or user config for next time.

## Project vs User Settings

Not all settings are available at every level. Project configs (`.devin/config.json` and `.devin/config.local.json`) support:

- **`permissions`** — allow, deny, and ask rules
- **`mcpServers`** — MCP server definitions
- **`read_config_from`** — import settings from Cursor, Windsurf, and Claude
- **`hooks`** — lifecycle hooks

All other settings — including `agent` (model), `theme_mode`, `unicode_mode`, `show_path`, `sandbox`, and other display/behavior options — are **user-config only** and can only be set in the user config (`~/.config/devin/config.json`; `%APPDATA%\devin\config.json` on Windows).

## Configuration Precedence

For settings that support multiple levels, higher-priority sources win:

| Priority | Source | Shared? |
| --- | --- | --- |
| 1 (highest) | Organization / Team settings | Yes (enterprise) |
| 2 | Session grants (interactive approvals) | No (in-memory) |
| 3 | Project local (`.devin/config.local.json`) | No (gitignored) |
| 4 | Project (`.devin/config.json`) | Yes (committed) |
| 5 (lowest) | User (`~/.config/devin/config.json`; `%APPDATA%\devin\config.json` on Windows) | No (personal) |

Permissions are merged across levels, while MCP servers are merged by name (higher-priority source wins for same-named servers).

**Note**: Organization-level (enterprise) settings can **never** be overridden by project or user config.

## Limitations

**Warning**: When run standalone, Devin CLI only respects `.gitignore` by default — it does not enforce `.devinignore`, `.codeiumignore`, or `.windsurfignore` files. When Devin CLI runs inside Devin Desktop, all four ignore files are enforced.