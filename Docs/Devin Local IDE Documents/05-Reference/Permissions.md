# Permissions

Control what the agent can do with fine-grained permission rules

The permission system controls which actions the agent can perform without asking for your approval. You can pre-approve safe actions, block dangerous ones, and always prompt for sensitive operations.

## Default Permission Behavior

Devin CLI uses a tiered permission system to balance power and safety. The default behavior depends on the current mode:

Each cell shows whether that tool runs automatically (**Auto**, no prompt) or waits for your approval (**Prompt**) in that mode:

| Tool type | Example | Normal | Accept Edits | Bypass | Autonomous (sandbox) |
|-----------|---------|--------|--------------|--------|----------------------|
| Read-only | File reads, grep, glob | Auto | Auto | Auto | Auto |
| Fetch | HTTP requests | Prompt | Prompt | Auto | Auto |
| Bash commands | Shell execution | Prompt | Prompt | Auto | Auto |
| File edits via `edit`/`write` | Edit/write files | Prompt | Auto (in workspace) | Auto | Prompt |

In **Normal mode** (the default), read-only operations are auto-approved while writes and shell commands require your explicit approval. Each time you approve an action, you can choose to allow it once, for the session, or permanently for the project.

In **Accept Edits mode**, file edits within the workspace are auto-approved, but shell commands and writes outside the workspace still prompt.

In **Bypass mode**, all tool calls are auto-approved without prompting.

In **Autonomous mode**, shell commands and network fetches auto-approve because the OS-level sandbox enforces what they can touch. Direct file edits via the `edit`/`write` tools still prompt, because those tools operate outside the sandbox. Autonomous is only available when the OS-level sandbox is active.

**Warning**: Bypass and Autonomous modes do **not** override organization-level permissions. Admin-enforced deny and ask rules configured via [Team Settings](../07-Enterprise/Team-Settings.md) remain active regardless of the user's permission mode.

### Autonomous Mode

Autonomous is the permission mode that pairs with the `--sandbox` flag. Conceptually it is roughly "Accept Edits in the current workspace" plus the ability to run any shell command, with both behaviors contained by the OS-level sandbox. When sandbox is active:

- **It is the only permission mode available.** Normal, Accept Edits, and Bypass are hidden in sandbox sessions. Plan mode remains available.
- **Shell commands and fetches auto-approve** instead of prompting, because the sandbox enforces what they can read, write, and reach over the network.
- **Direct file edits via the `edit` and `write` tools still prompt.** These tools run inside the CLI process rather than inside the sandbox, so they cannot be bounded by it. Granting a `Write(...)` scope at the prompt dynamically expands the sandbox so subsequent shell commands can write there.
- **Scopes granted mid-session dynamically expand the sandbox** for subsequent commands.

```bash
devin --sandbox --permission-mode autonomous
```

Use Bypass when you want unrestricted execution without OS-level isolation; use `--sandbox` (which selects Autonomous) when you want unattended execution with OS-enforced limits on filesystem and network access.

## How Permissions Work

When the agent calls a tool, the permission system checks your rules in priority order:

1. **Deny rules** — Checked first. If matched, the action is blocked immediately.
2. **Ask rules** — Checked second. If matched, you're always prompted (overrides any allow rules).
3. **Allow rules** — Checked last. If matched, the action proceeds without prompting.
4. **Default** — If no rule matches, you're prompted for approval.

**Note**: Because deny is checked before ask, and ask is checked before allow, a deny rule always wins. If the same scope matches both a deny and an ask rule, the deny takes effect.

## Configuration

Add permissions to your config file's `permissions` section:

**Note**: On Windows, the user config path is `%APPDATA%\devin\config.json` (typically `C:\Users\<you>\AppData\Roaming\devin\config.json`) rather than `~/.config/devin/config.json`.

### Project config
```json
// .devin/config.json
{
  "permissions": {
    "allow": [
      "Read(src/**)",
      "Exec(npm run)"
    ],
    "deny": [
      "Exec(rm)"
    ]
  }
}
```

### User config
```json
// ~/.config/devin/config.json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Exec(git)"
    ]
  }
}
```

### Local override
```json
// .devin/config.local.json
{
  "permissions": {
    "allow": [
      "Exec(docker compose)"
    ]
  }
}
```

## Permission Syntax

There are two types of permission matchers: **scope-based** (controlling what paths/commands/URLs are accessible) and **tool-based** (controlling which tools can be used).

### Scope-Based Permissions

#### Read(glob)
Controls file read access. The glob pattern matches file paths.

```json
"allow": [
  "Read(src/**)",           // All files under src/
  "Read(~/.config/**)",     // Home config files
  "Read(/tmp/**)"           // Temp directory
]
```

Directory paths automatically match all files within them.

#### Write(glob)
Controls file write/edit access.

```json
"allow": [
  "Write(src/**)",          // Can write anywhere in src/
  "Write(tests/**)"         // Can write test files
],
"deny": [
  "Write(*.lock)",          // Can't modify lock files
  "Write(.env*)"            // Can't modify env files
]
```

#### Exec(prefix)
Controls shell command execution. Matches commands that start with the given prefix.

```json
"allow": [
  "Exec(git)",              // git, git status, git commit...
  "Exec(npm run)",          // npm run test, npm run build...
  "Exec(python)"            // python, python script.py...
],
"deny": [
  "Exec(rm)",               // Blocks rm, rm -rf, etc.
  "Exec(sudo)"              // Blocks sudo commands
]
```

**Note**: `Exec(git)` matches "git", "git status", "git commit -m 'msg'" but NOT "gitk" or "github-cli". The prefix must match as a complete word.

#### Fetch(pattern)
Controls HTTP fetch access using URL patterns.

```json
"allow": [
  "Fetch(https://api.github.com/*)",    // GitHub API
  "Fetch(https://*.example.com/*)",     // All example.com subdomains
  "Fetch(domain:npmjs.org)"             // Any URL on npmjs.org
]
```

URL patterns follow the [WHATWG URL Pattern](https://urlpattern.spec.whatwg.org/) standard. The `domain:` shorthand matches any path on the exact domain.

### Tool-Based Permissions

Match by tool name to control entire tools:

```json
{
  "permissions": {
    "deny": [
      "edit",       // Block all file edits
      "exec"        // Block all command execution
    ],
    "allow": [
      "read",       // Allow all file reads
      "grep",       // Allow all searches
      "glob"        // Allow all file finding
    ]
  }
}
```

**Available tool names:** `read`, `edit`, `grep`, `glob`, `exec`

### MCP Tool Permissions

Control access to MCP server tools:

```json
{
  "permissions": {
    "allow": [
      "mcp__github__*"
    ],
    "deny": [
      "mcp__github__delete_repo"
    ]
  }
}
```

MCP tools use the format `mcp__<server>__<tool>`. Wildcards are supported.

## Precedence

For settings that support multiple levels, higher-priority sources win:

| Priority | Source | Shared? |
| --- | --- | --- |
| 1 (highest) | Organization / Team settings | Yes (enterprise) |
| 2 | Session grants (interactive approvals) | No (in-memory) |
| 3 | Project local (`.devin/config.local.json`) | No (gitignored) |
| 4 | Project (`.devin/config.json`) | Yes (committed) |
| 5 (lowest) | User (`~/.config/devin/config.json`; `%APPDATA%\devin\config.json` on Windows) | No (personal) |

**Note**: Organization-level (enterprise) settings can **never** be overridden by project or user config.