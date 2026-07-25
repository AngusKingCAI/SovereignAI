# YAML Configuration Best Practices Research

**Source:** Multiple web sources  
**Date:** 2026-07-25  
**Purpose:** YAML configuration best practices for Architect agent

## Key Best Practices from Research

### Indentation Standards
- **Tabs are forbidden** as indentation - use spaces only
- **Recommended:** 2 spaces per indentation level
- **Maximum:** 8 spaces per level (hard limit in future YAML versions)
- **Consistency:** Use same indentation for same level throughout document
- **Sequence indentation:** Zero-indented sequences recommended by YAML creators

### File Naming and Extensions
- **Recommended extension:** `.yaml`
- **Alternative:** `.yml` (widely used but `.yaml` preferred)
- **Be consistent** with extension choice across project

### Boolean Values
- **Use lowercase** `true` and `false` only
- **Avoid truthy boolean values** (they confuse people new to YAML)
- **Consistent boolean format** throughout configuration

### String Handling
- **Quote strings** that could be special types but you want strings
- **Quote strings** starting with non-alphanumeric characters
- **Quote strings** containing control characters or tabs
- **Quote strings** containing special characters: `:`, `#`, `-`, `>`
- **Use double quotes** for consistent quoting style
- **Use multiline strings** for long text (better readability)

### Sequence (List) Formatting
- **Prefer block style** sequences over flow style
- **Block style:** Indented under the key they belong to
- **Flow style:** Should be avoided for longer data (harder to read)
- **Flow style format:** Space after each comma, no space before/after brackets

### Mapping (Dictionary) Formatting
- **Key/value pairs:** Use colon and space (`: `) to separate
- **Consistent naming:** Use snake_case for keys (most common)
- **Descriptive names:** Avoid abbreviations when possible
- **Meaningful prefixes:** Group related settings

### Comments and Documentation
- **Comment format:** Start with capital letter, space after `#`
- **Comment placement:** Preferably above the line it applies to
- **Comment indentation:** Match current indentation level
- **Keep comments up to date:** Remove outdated comments
- **Document defaults:** Note when values differ from defaults
- **Use section headers:** Group related settings

### Document Structure
- **Start with `---`** to separate directives from content
- **End with `...`** to indicate document end (optional)
- **Logical grouping:** Related configuration sections together
- **Clear hierarchy:** Proper nesting and indentation

### Multiline Strings
- **Literal block scalar `|`:** Include newlines and trailing spaces
- **Folded block scalar `>`:** Fold newlines to spaces for readability
- **Indentation ignored** in both block scalar styles
- **Enforce newlines** with empty lines or `\n` characters in folded style

### Common Pitfalls to Avoid
- **Never mix tabs and spaces** - choose one and stick to it
- **Inconsistent indentation** within same level
- **Truthy boolean values** - use only `true`/`false`
- **Unquoted special characters** that could be misinterpreted
- **Flow style for complex data** - becomes hard to read
- **Outdated comments** - remove or update them

### Validation and Testing
- **Use YAML linter** to automatically check for issues
- **Validate syntax** before committing configuration files
- **Test parsing** in code with try/catch blocks
- **Use schema validation** when available
- **Check indentation consistency** across files

### Security Considerations
- **Never commit secrets** to YAML configuration files
- **Use environment variables** for sensitive data
- **Separate sensitive configs** from version control
- **Validate user input** in YAML configuration
- **Use secrets management** tools for production
