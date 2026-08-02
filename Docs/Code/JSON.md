# JSON Code Style Guide

**Purpose:** JSON configuration file standards for Architect agent implementations

## JSON Structure Standards

### Logical Organization
- **Group related settings** together (server settings, database settings, feature flags)
- **Use sensible defaults** for configuration values
- **Make it easy to scan** with clear section separation
- **Avoid deeply nested configs** (more than 4-5 levels becomes hard to reason about)
- **Flatten overly nested structures** when possible

### Configuration Pattern
- **Base config + environment overrides** pattern when applicable
- **Separate concerns** - different config files for different purposes
- **Logical grouping** of related configuration values
- **Clear naming** that indicates purpose and scope

## JSON Syntax Rules

### Standard JSON Requirements
- **No trailing commas** in standard JSON (invalid JSON)
- **No comments** in standard JSON (use JSONC for comments if needed)
- **No single quotes** - only double quotes for strings
- **No unquoted keys** - keys must be quoted
- **No undefined** - use `null` for missing values
- **UTF-8 encoding** without BOM

### JSON Extensions
- **JSONC (JSON with Comments):** Adds comments and trailing commas
- **JSON5:** Adds comments, trailing commas, unquoted keys, multi-line strings
- **Use JSONC** for VS Code settings files (`.vscode/settings.json`)
- **Use JSON5** for application configs where readability matters

## Naming Conventions

### File Naming
- **File naming:** Use `spinal-case` for file names (e.g., `app-config.json`, `hooks-config.json`)
- **Lowercase extension:** Always use `.json` (or `.jsonc` for JSONC files)

### Property Naming
- **Property naming:** Use `lowerCamelCase` for property names
- **Array properties:** Use plural or collective names
- **Property names:** Must be nouns or noun phrases
- **Descriptive names:** Clear indication of what the property represents

## Security and Secrets

### Secrets Management
- **Never commit secrets** to JSON config files
- **Use environment variables** for sensitive data
- **Reference environment variables** in code, not in config files
- **Separate sensitive configs** from version control
- **Use secrets management** tools for production deployments

## Formatting Standards

### Indentation and Layout
- **Pretty-printed** for config files (human-readable)
- **Minified** for API responses (machine-readable)
- **Indentation:** 2 spaces for web/JS ecosystems, 4 spaces for Python projects
- **Avoid tabs** - cause display inconsistencies across editors

### File Size and Complexity
- **Keep config files focused** - split large configs into logical files
- **Modular configuration** - separate concerns into different files
- **Maximum file size:** Avoid files >500 lines - split into focused modules
- **Logical separation:** Related configuration in same file

## Validation and Testing

### Validation Standards
- **Use JSON validators** to check syntax before committing
- **Test with try/catch** around JSON.parse in code
- **Use schema validation** when available (JSON Schema)
- **Format with proper indentation** for manual editing
- **Validate structure** against expected schema

### Error Handling
- **Graceful degradation** for missing or invalid config
- **Clear error messages** for validation failures
- **Fallback defaults** for missing configuration values
- **Validation at startup** rather than runtime

## Example Configuration

### Good JSON Configuration
```json
{
  "server": {
    "host": "localhost",
    "port": 3000,
    "environment": "development"
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "name": "app_database",
    "poolSize": 10
  },
  "features": {
    "enableCaching": true,
    "enableLogging": false,
    "maxRetries": 3
  }
}
```

### Bad JSON Configuration
```json
{
  "server": {
    "host": "localhost",
    "port": 3000,
  }, // Trailing comma - invalid JSON
  // Comments not allowed in standard JSON
  'badQuotes': "use double quotes", // Single quotes invalid
  unquotedKey: "keys must be quoted" // Unquoted keys invalid
}
```

## Best Practices Summary

### Do
- Group related settings logically
- Use standard JSON syntax (no trailing commas, no comments)
- Use proper naming conventions (lowerCamelCase, spinal-case files)
- Validate JSON syntax before committing
- Separate secrets from config files
- Use sensible defaults for configuration values

### Don't
- Put secrets in JSON config files
- Create deeply nested structures (flatten when possible)
- Use trailing commas in standard JSON
- Use single quotes for strings
- Leave unquoted keys
- Mix configuration types in single file

## Common Use Cases

### Hook Configuration
- **File:** `.devin/hooks.v1.json`
- **Purpose:** Define hook behavior and event handling
- **Structure:** Event definitions, tool permissions, execution rules

### Agent Configuration
- **File:** AGENTS.md frontmatter or separate config
- **Purpose:** Define agent behavior and capabilities
- **Structure:** Agent definitions, permissions, boundaries

### Project Configuration
- **File:** Various `.json` files in project root
- **Purpose:** Project-specific settings and tool configuration
- **Structure:** Tool-specific, follow individual tool documentation
