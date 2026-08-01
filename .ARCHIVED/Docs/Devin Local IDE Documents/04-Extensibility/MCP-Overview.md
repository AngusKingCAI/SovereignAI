# MCP Overview

Extend Devin CLI with external tool servers using the Model Context Protocol

MCP (Model Context Protocol) lets you connect external tool servers to Devin CLI, giving the agent access to APIs, databases, issue trackers, and any other service you can wrap in an MCP server.

When you configure an MCP server, its tools become available to the agent just like built-in tools. The agent can discover what tools are available and call them as needed.

## How It Works

1. **Configure a server** - You define an MCP server in your config file with a command, arguments, and optional environment variables.
2. **Server launches** - Devin CLI starts the server process when needed. The server connects to the external API (GitHub, Linear, etc.).
3. **Tool discovery** - The agent discovers what tools the server provides (e.g., `create_issue`, `list_repos`).
4. **Tool execution** - When the agent calls an MCP tool, the request flows through the server to the external service and the result is returned.

## Quick Example

Add a GitHub MCP server to your project:

```json
// .devin/config.local.json  (gitignored — keep tokens out of committed config)
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

Now the agent can create issues, read PRs, search repos, and more — all through natural language.

## Permission Control

Once configured, MCP tools appear with a namespaced format: `mcp__<server>__<tool>`. For example, a "github" server with a "create_issue" tool becomes `mcp__github__create_issue`.

MCP tools are subject to the same permission system as built-in tools. You can control access at multiple levels:

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

See [Permissions](../05-Reference/Permissions.md) for the full permission syntax.

## Authentication

Some remote MCP servers (such as Atlassian, Notion, and Linear) require OAuth authentication. Each MCP client authenticates independently — tokens from Windsurf or Claude Code are **not** shared with Devin CLI.

After adding a remote server, authenticate with:

```bash
devin mcp login <server-name>
```

This opens a browser window for the OAuth flow.

## Disabling Servers

You can temporarily disable an MCP server without removing its configuration or credentials:

```bash
devin mcp disable <server-name>
devin mcp enable <server-name>
```

## Enhanced MCP Features

### OAuth Resource Override

MCP servers can now override the RFC 8707 OAuth `resource` parameter via a new `oauthResource` field in the MCP server config (or `--oauth-resource` on `devin mcp add` / `devin mcp login`). This is needed for identity providers like Microsoft Entra that reject requests containing `resource`.

```json
{
  "mcpServers": {
    "entra": {
      "url": "https://mcp.example.com/mcp",
      "oauthResource": ""  // Empty string omits the parameter entirely
    }
  }
}
```

### MCP Slash Command

A new `/mcp` slash command provides a live MCP server status panel, showing the status of all configured MCP servers and their connection states.

### Server-Level Permission Approval

When prompted for an MCP tool permission, two additional server-level options are now offered:
- **Approve all tools on the server for the current session** - Grants broader access for this session only
- **Approve all tools on the server permanently** - Grants broader access for all future sessions

This lets you grant broader access without re-approving each tool individually.

### MCP Registry Cache Warming

The MCP registry cache is now warmed during startup, so MCP servers are ready sooner when sessions begin. This reduces the initial delay when using MCP tools.