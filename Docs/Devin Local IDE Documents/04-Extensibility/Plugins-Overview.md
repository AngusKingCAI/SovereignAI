# Plugins Overview

Install and share bundles of skills from a repo, git URL, or local folder.

**Note**: Plugins are in **beta**. Behavior and configuration may change in future releases.

A **plugin** is a bundle of skills you can install from a GitHub repo, a git URL, or a local folder and reuse across projects. Installing a plugin makes its skills available as `/<plugin>:<skill>` slash commands, and it can pull in other plugins it depends on automatically.

A plugin is just a source that contains:

```
my-plugin/
├── .devin-plugin/
│   └── plugin.json     # The plugin manifest
├── AGENTS.md           # Optional rules
└── skills/
    └── review/
        └── SKILL.md    # An ordinary skill
```

The `skills/` directory holds ordinary skills — plugins introduce no new skill format. See [Creating Skills](./Skills-Overview.md) for the `SKILL.md` format.

A plugin can also ship **rules**: an `AGENTS.md` at the plugin root is injected as an always-on rule in every session, alongside your project's own rules. Markdown files in a `rules/` folder are loaded too, with the same `trigger` frontmatter and activation types as Windsurf rules.

## Installing a plugin

A plugin source can be a GitHub `owner/repo`, a git URL, or a local path:

```bash
# From GitHub
devin plugins install acme/review-tools

# From any git host
devin plugins install https://gitlab.com/acme/review-tools.git

# From a local folder (great for authoring)
devin plugins install ./my-plugin
```

Before installing, Devin shows what the plugin adds — the skills it provides, any required plugins that will be auto-installed, and any policy it introduces (for example, if it forbids other plugins). Pass `-y` / `--yes` to skip the prompt.

Plugins are installed at the **user** level and are available across all your projects.

## Managing plugins

```bash
# List installed plugins, their versions, and whether any are blocked by policy
devin plugins list

# Show a plugin's skills and its required/optional/forbidden lists
devin plugins info review-tools

# Re-fetch a plugin (or all plugins) at the latest version
devin plugins update review-tools
devin plugins update

# Remove a plugin (auto-installed required plugins are left in place)
devin plugins remove review-tools
```

Local plugins are linked directly to their source folder, so edits are live:
`devin plugins install ./my-plugin` → edit `skills/<name>/SKILL.md` → changes apply on the next session, no `update` needed.

## The manifest

`.devin-plugin/plugin.json` describes the plugin. Only `name` is required, and it must be unique among installed plugins (it is the `/<name>:…` namespace).

```json
{
  "name": "review-tools",
  "version": "1.0.0",
  "description": "Code-review skills for our team",
  "requiredPlugins": [
    "acme/secure-base",
    { "source": "github", "repo": "acme/audit-logging" }
  ],
  "optionalPlugins": [
    "acme/deploy-tools",
    { "source": "url", "url": "https://gitlab.com/acme/extra.git" }
  ],
  "forbiddenPlugins": ["sketchy-org/bad-plugin", "acme/*", "*"]
}
```

Supported metadata fields: `name`, `version`, `description`, `author` (`{ name, email }`), `homepage`, `repository`, `license`, and `keywords`.

A dependency entry is a **source** — either a string shorthand or an object:

| Form | Meaning |
|------|---------|
| `"owner/repo"` | GitHub repository |
| `"https://…"`, `"git@…"`, `"ssh://…"` | any git URL |
| `{ "source": "github", "repo": "owner/repo" }` | GitHub, object form |
| `{ "source": "url", "url": "https://gitlab.com/team/plugin.git" }` | git URL, object form |
| `{ "source": "git-subdir", "url": "…", "path": "sub/dir" }` | a plugin living in a subfolder of a shared repo |

All GitHub forms for the same repo (`owner/repo`, the HTTPS URL, the `.git` URL, the SSH form) refer to the same plugin identity.

## Dependencies and governance

A plugin can declare three lists, which let a single plugin act as a curated, governed collection of other plugins.

### requiredPlugins

Auto-installed (recursively) when the plugin is installed. If a required plugin is blocked by policy, the whole install fails — there is no partial install.

### optionalPlugins

An **allow-list** of plugins this plugin endorses. They are **not** auto-installed; the list only matters as a carve-out against a forbidden entry (see below).

### forbiddenPlugins

A **deny-list** of plugin identities and glob patterns.

`forbiddenPlugins` entries are matched against plugin identities:

- An **exact identity**, written as `owner/repo` or a git URL. All GitHub forms of the same repo (`owner/repo`, the HTTPS URL, the `.git` URL, the SSH form) refer to the same identity.
- A **glob pattern** — any entry containing `*`. The `*` matches any sequence of characters, including `/`: `acme/*` matches all of `acme`'s GitHub repos, `*/secrets` matches a repo named `secrets` under any owner, and `https://gitlab.com/acme/*` matches any repo under that path.
- The lone `"*"`, which matches everything else (a full lockdown).

The lists combine deny-wins:

- **Deny wins.** A plugin is blocked if any active manifest or installed plugin forbids it. If nothing forbids anything, nothing is blocked.
- **Self-override.** A manifest's (or plugin's) own `requiredPlugins` and `optionalPlugins` — and, for a plugin, the plugin itself — are exempt from its **own** forbidden list, so `"forbiddenPlugins": ["*"]` plus `"optionalPlugins": ["acme/approved"]` means "allow only what this manifest lists; forbid everything else." The carve-out covers only those direct entries, not a required plugin's transitive dependencies — list those explicitly under a lockdown.
- **No cross-scope re-permitting.** One manifest's or plugin's allow-list cannot re-permit what **another** forbids. A `"forbiddenPlugins": ["*"]` lockdown can't be defeated from a lower scope.

Enforcement happens at two points:

- **Install time** — installing a blocked plugin (or one whose required plugins can't be satisfied, or whose name collides with an installed plugin) is refused.
- **Load time** — a plugin blocked after it's already installed stays on disk, but its skills are skipped at session start with a warning naming the forbidder.

A forbidden identity can also be a **local path** (for plugins installed from a local folder), in addition to the `owner/repo` and git-URL forms above.

## Enterprise controls

Expanded controls for admins to govern what Devin Local can do and which tools it can reach.

- Teams can define terminal command allow/deny lists, enforced through CLI permission scopes with exact-command matching and `*` wildcards.
- Org-level control to disable Devin CLI plugins: when set, the CLI refuses to install or update plugins and skips the skills from any installed plugins.
- The "Disable CLI access" team setting is now enforced for Devin Local (the CLI hosted in Windsurf), including the bundled agent registry and the allowed-MCP-server allowlist.