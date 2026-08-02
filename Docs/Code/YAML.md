# YAML Code Style Guide

**Purpose:** YAML configuration file standards for Architect agent implementations

## Indentation Standards

### Basic Rules
- **Tabs are forbidden** as indentation - use spaces only
- **Recommended:** 2 spaces per indentation level
- **Maximum:** 8 spaces per level (hard limit in future YAML versions)
- **Consistency:** Use same indentation for same level throughout document
- **Never mix tabs and spaces** - choose one and stick to it

### Sequence Indentation
- **Zero-indented sequences** recommended by YAML creators
- **Block style sequences** should be indented under the key they belong to
- **Flow style** should be avoided for complex data (harder to read)

## File Naming and Extensions

### File Extensions
- **Recommended extension:** `.yaml`
- **Alternative:** `.yml` (widely used but `.yaml` preferred)
- **Be consistent** with extension choice across project
- **Use lowercase** for file extensions

## Boolean Values

### Boolean Standards
- **Use lowercase** `true` and `false` only
- **Avoid truthy boolean values** (they confuse people new to YAML)
- **Consistent boolean format** throughout configuration
- **No yes/no, on/off, or other truthy values**

## String Handling

### Quoting Rules
- **Quote strings** that could be special types but you want strings
- **Quote strings** starting with non-alphanumeric characters
- **Quote strings** containing control characters or tabs
- **Quote strings** containing special characters: `:`, `#`, `-`, `>`, `{`, `}`, `[`, `]`
- **Use double quotes** for consistent quoting style
- **Use single quotes** when double quotes are in the string

### Multiline Strings
- **Literal block scalar `|`:** Include newlines and trailing spaces
- **Folded block scalar `>`:** Fold newlines to spaces for readability
- **Indentation ignored** in both block scalar styles
- **Enforce newlines** with empty lines or `\n` characters in folded style

## Naming Conventions

### Key Naming
- **Use snake_case** for keys (most common in YAML)
- **Descriptive names:** Avoid abbreviations when possible
- **Meaningful prefixes:** Group related settings
- **Consistent naming:** Don't mix camelCase and snake_case
- **Clear hierarchy:** Proper nesting structure

## Sequence (List) Formatting

### Block Style (Preferred)
```yaml
servers:
  - name: server1
    port: 8080
  - name: server2
    port: 8081
```

### Flow Style (Avoid for Complex Data)
```yaml
servers: [{name: server1, port: 8080}, {name: server2, port: 8081}]
```

### Flow Style Format
- Space after each comma `,`
- No space before opening `[` and after closing `]`
- Use only for simple, short lists

## Mapping (Dictionary) Formatting

### Basic Structure
- **Key/value pairs:** Use colon and space (`: `) to separate
- **Proper indentation:** Values indented under keys
- **Logical grouping:** Related configuration sections together

## Comments and Documentation

### Comment Format
- **Comment format:** Start with capital letter, space after `#`
- **Comment placement:** Preferably above the line it applies to
- **Comment indentation:** Match current indentation level
- **Keep comments up to date:** Remove outdated comments
- **Document defaults:** Note when values differ from defaults
- **Use section headers:** Group related settings

### Comment Examples
```yaml
# Server configuration
server:
  host: localhost  # Default host
  port: 3000      # Default port
  
# Database settings  
database:
  name: my_database
```

## Document Structure

### Document Start/End
- **Start with `---`** to separate directives from content
- **End with `...`** to indicate document end (optional)
- **Logical grouping:** Related configuration sections together
- **Clear hierarchy:** Proper nesting and indentation

## Security and Secrets

### Secrets Management
- **Never commit secrets** to YAML configuration files
- **Use environment variables** for sensitive data
- **Reference environment variables** in code, not in config files
- **Separate sensitive configs** from version control
- **Use secrets management** tools for production deployments

## Validation and Testing

### Validation Standards
- **Use YAML linter** to automatically check for issues
- **Validate syntax** before committing configuration files
- **Test parsing** in code with try/catch blocks
- **Use schema validation** when available
- **Check indentation consistency** across files

### Error Handling
- **Graceful degradation** for missing or invalid config
- **Clear error messages** for validation failures
- **Fallback defaults** for missing configuration values
- **Validation at startup** rather than runtime

## Example Configuration

### Good YAML Configuration
```yaml
---
# Server configuration
server:
  host: localhost
  port: 3000
  environment: development

# Database settings
database:
  host: localhost
  port: 5432
  name: app_database
  pool_size: 10

# Feature flags
features:
  enable_caching: true
  enable_logging: false
  max_retries: 3
```

### Bad YAML Configuration
```yaml
server:
  host: localhost
	port: 3000    # Mixed tabs and spaces
environment: "development"  # Unnecessary quotes
---
database:
  host: localhost
  port: 5432,
  name: app_database  # Trailing comma (JSON syntax, not YAML)
```

## Best Practices Summary

### Do
- Use 2 spaces for indentation (never tabs)
- Use lowercase `true`/`false` for booleans
- Prefer block style sequences over flow style
- Quote strings with special characters
- Use snake_case for keys
- Add meaningful comments
- Validate YAML syntax before committing
- Group related configuration logically

### Don't
- Mix tabs and spaces for indentation
- Use truthy boolean values (yes/no, on/off)
- Use flow style for complex data
- Leave unquoted special characters
- Mix naming conventions (camelCase vs snake_case)
- Leave outdated comments
- Commit secrets to config files
- Inconsistent indentation within same level

## Common Use Cases

### Frontmatter Configuration
- **File:** Markdown files with YAML frontmatter
- **Purpose:** Define metadata and configuration
- **Structure:** Key-value pairs at document start
- **Example:** AGENTS.md frontmatter with agent name and description

### Application Configuration
- **File:** Various `.yaml` or `.yml` config files
- **Purpose:** Application settings and feature flags
- **Structure:** Hierarchical configuration sections
- **Example:** Server, database, feature configuration sections

### CI/CD Configuration
- **File:** Pipeline and workflow configuration files
- **Purpose:** Define build and deployment processes
- **Structure:** Job definitions, steps, and environment variables
- **Example:** GitHub Actions workflow configuration
