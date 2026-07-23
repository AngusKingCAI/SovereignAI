# Commands & Flags

Complete reference for command arguments, subcommands, and interactive slash commands

## Usage

```bash
devin [OPTIONS] [prompt]
```

Pass an optional prompt to start a session with an initial message, or launch interactively with no arguments.

You can also read these from your terminal with `man devin`.

## Global Flags

| Flag | Short | Description |
| --- | --- | --- |
| `--model <MODEL>` |  | Set the AI model for this session |
| `--permission-mode <MODE>` |  | Permission mode (`normal`, `dangerous`, `bypass`) |
| `--continue` | `-c` | Resume the most recent session in the current directory |
| `--resume <SESSION_ID>` | `-r` | Resume a specific session by ID |
| `--print [PROMPT]` | `-p` | Print response and exit (non-interactive mode). Optionally accepts an inline prompt. |
| `--prompt-file <FILE>` |  | Load the initial prompt from a file |
| `--config <PATH>` |  | Configuration file path |
| `--export [PATH]` |  | Export conversation to a file after each turn (ATIF format). Uses a default path if none is provided. |
| `--respect-workspace-trust` |  | Whether to respect workspace trust settings |

**Examples:**

```bash
devin -- add a login page
devin --model opus -- refactor the auth module
devin -c                              # Resume last session
devin -r abc12345                     # Resume specific session
devin -p "list all TODO comments"    # Print response and exit
devin -p -- list all TODO comments    # Same, using -- separator (still works)
devin --export -- fix the tests       # Export conversation to default path
devin --export out.json -- fix tests   # Export to a specific file
```

## Subcommands

### devin auth

Authentication related commands.

| Command | Description |
| --- | --- |
| `devin auth login` | Log in to your account |
| `devin auth logout` | Log out and remove stored credentials |
| `devin auth status` | Check authentication status |

**Options for `devin auth login`:**
- `--force-manual-token-flow` — Skip browser-based auth and manually paste a token (useful for remote/SSH sessions)

### devin mcp

Connect and log in to Model Context Protocol servers.

| Command | Description |
| --- | --- |
| `devin mcp add <name>` | Add a new MCP server |
| `devin mcp list` | List all configured MCP servers |
| `devin mcp get <name>` | Show details for a specific MCP server |
| `devin mcp remove <name>` | Remove a configured MCP server |
| `devin mcp login <name>` | Authenticate with an MCP server via OAuth |
| `devin mcp logout <name>` | Remove stored OAuth credentials for an MCP server |
| `devin mcp enable <name>` | Enable a disabled MCP server |
| `devin mcp disable <name>` | Disable a MCP server without removing it |

**Options for `devin mcp add`:**
- `-t, --transport <stdio|http>` — Transport type (optional; inferred from URL → http, trailing args → stdio)
- `-s, --scope <local|project|user>` — Configuration scope (default: `local`)
- `--url <URL>` — URL for HTTP transport (can also be passed as a positional argument after the name)
- `--command <CMD>` — Command for stdio transport (optional when trailing args are provided)
- `-e, --env <KEY=VALUE>` — Environment variables (repeatable)
- `-H, --header <HEADER: VALUE>` — HTTP headers (repeatable)
- `--scopes <SCOPE,SCOPE>` — OAuth scopes to request (comma-separated)
- `--oauth-resource <RESOURCE>` — Override the RFC 8707 `resource` parameter sent in OAuth requests (default: the MCP server URL; pass an empty string to omit it for providers that reject it)
- `<URL>` — Positional URL argument for HTTP (alternative to `--url`)
- `-- <COMMAND> [ARGS...]` — Command and arguments for stdio (first arg is the command when `--command` is omitted)

**Examples:**

```bash
# stdio server
devin mcp add my-server -- npx @company/mcp-server --port 3000

# HTTP server (positional URL)
devin mcp add notion https://mcp.notion.com/mcp
devin mcp add --transport http datadog-mcp https://mcp.datadoghq.com/api/unstable/mcp-server/mcp

# HTTP server (--url flag, also works)
devin mcp add notion --url https://mcp.notion.com/mcp

# With environment variables and scope
devin mcp add -e GITHUB_TOKEN=ghp_xxx github -- npx -y @modelcontextprotocol/server-github
devin mcp add -s project sentry https://mcp.sentry.dev/mcp
```

### devin rules

Manage agent rules (always-on context blobs).

| Command | Description |
| --- | --- |
| `devin rules list` | List all available rules |
| `devin rules show <name>` | Show details for a specific rule |
| `devin rules paths` | Show rule directory locations |

**Options for `devin rules list`:**
- `--provider <cursor|windsurf>` — Filter by rule provider

### devin skills

Manage agent skills (slash commands and agent-triggered context blobs).

| Command | Description |
| --- | --- |
| `devin skills list` | List all available skills |
| `devin skills show <name>` | Show details for a specific skill |
| `devin skills paths` | Show skill directory locations |

**Options for `devin skills list`:**
- `--trigger <user|model>` — Filter by trigger type

### devin list

List sessions in the current directory. Alias: `devin ls`

| Command | Description |
| --- | --- |
| `devin list` | Interactive session picker (default) |
| `devin list --format json` | Output sessions as JSON |
| `devin list --format csv` | Output sessions as CSV |

### devin version

Print the current version and exit.

```bash
devin version
```

This is equivalent to `devin --version`.

### devin acp

Run Devin as an [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) server over stdio. This subcommand is intended to be invoked by an ACP-aware editor or IDE (such as Windsurf or Zed) as a subprocess — it speaks JSON-RPC over stdin/stdout and is not meant to be run interactively.

```bash
devin acp
```

The ACP server reads credentials from `WINDSURF_API_KEY` if set, otherwise from the credentials stored by `devin auth login`. It can also accept credentials at runtime via the ACP `authenticate` request.

### devin update

Check for updates and optionally install them.

```bash
devin update
```

Use `--force` to re-install even if already on the latest version:

```bash
devin update --force
```

### devin shell

[Feature Preview] Shell integration commands.

| Command | Description |
| --- | --- |
| `devin shell setup` | Install shell integration into your shell config file |
| `devin shell setup <shell>` | Install for a specific shell (`bash`, `zsh`, or `fish`) |

### devin sandbox

[Research Preview] Manage OS-level process sandboxing for the exec tool. Pass the global `--sandbox` flag to run a session with the sandbox enforced.

#### devin sandbox setup

Print the sandbox prerequisites for the current platform.

Requirements to run with `--sandbox`:

- **Linux**: requires bubblewrap (`bwrap`) and `socat`. A sandbox session fails to start with installation instructions when these are missing.
- **macOS**: Requires a macOS-compatible sandboxing implementation. A sandbox session fails to start with platform-specific instructions when unavailable.
- **Windows**: OS-level sandboxing is not currently supported. Sessions hard-fail when `--sandbox` is passed or when sandbox enforcement is **Required**.