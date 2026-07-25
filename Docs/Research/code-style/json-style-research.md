# JSON Configuration Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** JSON code style guide for Architect agent

## Key Best Practices from Research

### JSON Structure Standards
- **Group related settings** together (server settings, database settings, feature flags)
- **Use sensible defaults** for configuration values
- **Make it easy to scan** with logical organization
- **Avoid deeply nested configs** (more than 4-5 levels becomes hard to reason about)
- **Flatten overly nested structures** when possible

### JSON Syntax Rules
- **No trailing commas** in standard JSON (invalid JSON)
- **No comments** in standard JSON (use JSONC for comments)
- **No single quotes** - only double quotes for strings
- **No unquoted keys** - keys must be quoted
- **No undefined** - use `null` for missing values
- **UTF-8 encoding** without BOM

### File Naming and Organization
- **File naming:** Use `spinal-case` for file names (e.g., `app-config.json`)
- **Property naming:** Use `lowerCamelCase` for property names
- **Array properties:** Use plural or collective names
- **Property names:** Must be nouns or noun phrases

### Configuration Management
- **Base config + environment overrides** pattern
- **Never commit secrets** to JSON config files
- **Use environment variables** for sensitive data
- **Schema-backed configs** for validation when possible
- **Separate concerns** - different config files for different purposes

### JSON Extensions
- **JSONC (JSON with Comments):** Adds comments and trailing commas
- **JSON5:** Adds comments, trailing commas, unquoted keys, multi-line strings
- **Use JSONC** for VS Code settings files
- **Use JSON5** for application configs where readability matters

### Formatting Standards
- **Pretty-printed** for config files (human-readable)
- **Minified** for API responses (machine-readable)
- **Indentation:** 2 spaces for web/JS, 4 spaces for Java/Python
- **Avoid tabs** - cause display inconsistencies

### Common Pitfalls to Avoid
- Secrets in config files
- Deeply nested structures
- Duplicated values (no variables/references in standard JSON)
- No environment support in standard JSON
- Multi-line strings not supported in standard JSON

### Validation and Testing
- Use JSON validators to check syntax
- Test with try/catch around JSON.parse in code
- Use schema validation when available
- Format with proper indentation for manual editing
