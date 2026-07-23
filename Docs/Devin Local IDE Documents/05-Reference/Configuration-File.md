# Configuration File

Complete reference for the Devin CLI config file format

Devin CLI uses JSON files (with comment support) for configuration. This page documents all available options.

## File Locations

| File | Purpose |
|------|---------|
| `~/.config/devin/config.json` | User-wide settings |
| `.devin/config.json` | Project settings (committed) |
| `.devin/config.local.json` | Project local overrides (gitignored) |

**Note**: On Windows, the user config path is `%APPDATA%\devin\config.json` (e.g. `C:\Users\<you>\AppData\Roaming\devin\config.json`), not `~\.config\devin\config.json`.

## Full Config Reference

### User config
```json
// ~/.config/devin/config.json
{
  // Agent behavior
  "agent": {
    "model": "swe-1-6-fast",           // Default model
    "show_history_on_continue": true  // Show messages when resuming
  },

  // Theme
  "theme_mode": null,            // "light", "dark", "terminal-dark", "terminal-light", "nocolor", or null (auto)

  // Permissions
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": []
  },

  // MCP servers
  "mcpServers": {},

  // Display
  "show_path": false,             // Show CWD in input border
  "unicode_mode": "auto",         // "auto", "unicode", or "ascii"
  "show_hints": true,             // Show tips between turns

  // File completion
  "include_gitignored_files": false, // Include gitignored files in @ completions

  // File access
  "respect_gitignore": false,        // Block tool access to gitignored paths

  // Commit & PR attribution
  "attribution": true,            // Add "Generated with Devin" / Co-Authored-By to commits & PRs

  // Updates
  "auto_update": true,            // Install new versions in the background

  // Notifications
  "notify": "smart",              // "never" | "smart" | "always" — terminal notifications

  // Proxy settings for CLI HTTP traffic
  "proxy": {
    "mode": "system",           // "system" | "manual" | "off"
    "url": null,                // Proxy URL (required for manual mode)
    "no_proxy": null            // Comma-separated bypass list
  },

  // Sandbox network filtering
  "sandbox": {
    "allowed_domains": [],       // Domain allowlist (empty = no filtering)
    "denied_domains": [],        // Domain denylist (takes precedence)
    "network_mode": "full",      // "full" or "limited" (GET/HEAD/OPTIONS only)
    "excluded": {
      "allow": [],              // Commands that run outside sandbox automatically
      "ask": [],                 // Commands that run outside sandbox after approval
      "deny": []                 // Commands that must never run outside sandbox
    }
  },

  // Import settings from other tools
  "read_config_from": {
    "cursor": true,
    "windsurf": true,
    "claude": true
  }
}
```

### Project config
```json
// .devin/config.json
{
  // Permissions
  "permissions": {
    "allow": [],
    "deny": [],
    "ask": []
  },

  // MCP servers
  "mcpServers": {},

  // Import settings from other tools
  "read_config_from": {
    "cursor": true,
    "windsurf": true,
    "claude": true
  }
}
```

## Options Reference

**Note**: Options marked with **User only** can only be set in the user config (`~/.config/devin/config.json`; `%APPDATA%\devin\config.json` on Windows). Only `permissions`, `mcpServers`, `read_config_from`, and `hooks` are available in project configs.

### agent (user only)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | string | `"swe-1-6-fast"` | Default AI model |
| `show_history_on_continue` | boolean | `true` | Show previous messages when resuming a session |

### theme_mode (user only)

| Value | Behavior |
|-------|----------|
| `null` | Auto-detect (asks on first run) |
| `"light"` | Light theme |
| `"dark"` | Dark theme |
| `"terminal-dark"` | Dark theme quantized to 16 ANSI colors (respects terminal color scheme) |
| `"terminal-light"` | Light theme quantized to 16 ANSI colors (respects terminal color scheme) |
| `"nocolor"` | No color output (monochrome, useful for VT100 terminals) |

### permissions

See [Permissions](./Permissions.md) for full documentation.

```json
{
  "permissions": {
    "allow": ["Read(**)", "Exec(git)"],
    "deny": ["Exec(sudo)"],
    "ask": ["Write(**/.env*)"]
  }
}
```

### mcpServers

Map of server name to server configuration. Supports both local command (stdio) and remote HTTP servers.

```json
{
  "mcpServers": {
    "server-name": {
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": { "KEY": "value" }
    },
    "remote-server": {
      "url": "https://mcp.example.com/mcp",
      "transport": "http"
    }
  }
}
```

### show_path (user only)

Show the current working directory path in the input border. When enabled, the top border of the input box displays your prettified CWD (e.g. `~/projects/my-app`).

| Value | Behavior |
|-------|----------|
| `false` | Hidden (default) |
| `true` | Show CWD path in input border |

### unicode_mode (user only)

Controls whether the terminal UI uses Unicode symbols or ASCII-safe fallbacks. Set to `"ascii"` if your terminal or font does not render Unicode glyphs correctly (e.g. the ⏺ symbol appearing as a box).

| Value | Behavior |
|-------|----------|
| `"auto"` | Detect Unicode support from environment (default) |
| `"unicode"` | Always use Unicode symbols |
| `"ascii"` | Always use ASCII-safe characters |

### show_hints (user only)

Show occasional tips between turns (e.g. "Did you know: Use /model to switch between available models"). Useful for discovering CLI features; set to `false` to suppress them once you're familiar.

| Value | Behavior |
|-------|----------|
| `true` | Show tips occasionally (default) |
| `false` | Never show tips |

### include_gitignored_files (user only)

Include gitignored files in `@` tab completion results. When enabled, files matching `.gitignore` patterns will appear in `@` mention completions. This is useful if you store documentation or other files in gitignored directories that you want to reference.

| Value | Behavior |
|-------|----------|
| `false` | Exclude gitignored files from completions (default) |
| `true` | Include gitignored files in @ completions |

### respect_gitignore (user only)

Control whether the agent respects `.gitignore` when reading or writing files via tools. When enabled, tool calls that access gitignored paths are blocked. This is separate from `include_gitignored_files`, which only affects `@` tab completion.

| Value | Behavior |
|-------|----------|
| `false` | Agent can access all files regardless of `.gitignore` (default) |
| `true` | Block tool access to gitignored paths |

### attribution (user only)

Control whether the agent adds Devin attribution to the commits and pull requests it creates. When enabled, commit and PR bodies include a `Generated with [Devin]` line and a `Co-Authored-By: Devin` trailer. Set to `false` to omit both so no Devin attribution is added.

| Value | Behavior |
|-------|----------|
| `true` | Add the `Generated with [Devin]` line and `Co-Authored-By` trailer to commits and PRs (default) |
| `false` | Omit all Devin attribution from commits and PRs |

### auto_update (user only)

Control background auto-update on macOS and Linux. When enabled, new releases are downloaded and activated while Devin CLI runs, so the next invocation of `devin` picks up the latest version automatically.

| Value | Behavior |
|-------|----------|
| `true` | Enable background auto-update (default on macOS/Linux) |
| `false` | Disable background auto-update |

### notify (user only)

Control terminal notifications. The `smart` mode only shows notifications for long-running operations.

| Value | Behavior |
|-------|----------|
| `"never"` | Never show terminal notifications |
| `"smart"` | Show notifications for long-running operations (default) |
| `"always"` | Show notifications for all operations |

### proxy (user only)

Configure proxy settings for CLI HTTP traffic (authentication, updates, model API calls, MCP servers).

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `mode` | string | `"system"` | `"system"` (use OS proxy settings), `"manual"` (use url), or `"off"` (no proxy) |
| `url` | string | `null` | Proxy URL (required for manual mode) |
| `no_proxy` | string | `null` | Comma-separated list of hosts to bypass proxy |

### sandbox (user only)

Configure network filtering for the OS-level sandbox. Only applies when `--sandbox` is active.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `allowed_domains` | string[] | `[]` | Domain allowlist (empty = no filtering) |
| `denied_domains` | string[] | `[]` | Domain denylist (takes precedence) |
| `network_mode` | string | `"full"` | `"full"` or `"limited"` (GET/HEAD/OPTIONS only) |
| `excluded.allow` | string[] | `[]` | Commands that run outside sandbox automatically |
| `excluded.ask` | string[] | `[]` | Commands that run outside sandbox after approval |
| `excluded.deny` | string[] | `[]` | Commands that must never run outside sandbox |

The `excluded` section allows specific commands to run outside the OS-level sandbox. This is useful for commands that need to access credentials or hooks that the sandbox blocks. Use `Exec(...)` rule syntax to specify commands.

### read_config_from

Control whether to import configuration from other AI coding tools.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cursor` | boolean | `true` | Import from Cursor |
| `windsurf` | boolean | `true` | Import from Windsurf |
| `claude` | boolean | `true` | Import from Claude Code |