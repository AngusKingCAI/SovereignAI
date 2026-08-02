---
id: shared_rules
version: "1.0.0"
owner: SovereignAI
updated: 2026-08-02
purpose: Shared governance rules documentation for all agents
agent: all
persona: governance
---
# Shared Governance Rules

This document explains the shared governance rules that apply to all agents. Agents should read this before taking actions to avoid triggering enforcement bypass popups.

## Rule Overview

### SHR-01: Safety Commands
**Tier:** Safety  
**Severity:** Blocking  
**Domain:** Destructive Commands  

**Purpose:** Block destructive shell commands unless user has explicitly confirmed

**What triggers this rule:**
- `rm -rf` commands
- `rm` commands
- `DROP TABLE` database commands  
- `git push --force` commands
- `git restore` commands
- `git fetch` commands
- Fork bomb patterns: `:() { :|: & }; :`

**How to avoid violations:**
- Use `-f` flags sparingly and with user confirmation
- For git operations, prefer safe alternatives like `git push` without `--force`
- Use `git checkout` instead of `git restore` when possible
- Ask for user confirmation before destructive operations

### SHR-02: Encoding Compliance  
**Tier:** Compliance  
**Severity:** Blocking  
**Domain:** Encoding  

**Purpose:** Ensure all governance files use proper UTF-8 encoding

**What triggers this rule:**
- Files with Windows line endings (CRLF) instead of Unix line endings (LF)
- Content that cannot be encoded as UTF-8
- Invalid UTF-8 byte sequences

**How to avoid violations:**
- Always use Unix line endings (LF) in source files
- Ensure files are saved with UTF-8 encoding
- Convert CRLF to LF before committing files
- Use text editors that enforce UTF-8 and LF line endings

### SHR-03: Frontmatter Requirements
**Tier:** Compliance  
**Severity:** Blocking  
**Domain:** Frontmatter  

**Purpose:** Ensure all governance .md files have proper YAML frontmatter

**What triggers this rule:**
- .md files in `.devin/agents/`, `Governance/`, or `workflows/` without YAML frontmatter
- Missing required frontmatter fields: `id`, `version`, `owner`, `updated`, `purpose`, `agent`, `persona`

**How to avoid violations:**
- Always include YAML frontmatter in governance .md files
- Use this frontmatter format:
  ```yaml
  ---
  id: rule-id
  version: "1.0.0"
  owner: SovereignAI
  updated: 2026-08-02
  purpose: Description of the file
  agent: all
  persona: governance
  ---
  ```
- For Python files, use comment-style frontmatter to avoid syntax errors

### SHR-04: File Placement
**Tier:** Compliance  
**Severity:** Blocking  
**Domain:** File Placement  

**Purpose:** Ensure governance files are placed in correct locations

**What triggers this rule:**
- Governance YAML/MD files in `.devin/` directories
- Governance files in `GovernanceScripts/` directories

**How to avoid violations:**
- Place all governance policy cards in `Rules/`
- Place governance documentation in `Rules/` directory
- Place governance scripts in `Scripts/Rules/`
- Never place governance files in `.devin/` directories

## General Best Practices

1. **Read before acting:** Check these rules before performing operations
2. **Use safe alternatives:** Prefer safer command options when available
3. **Confirm with user:** Ask for confirmation before destructive operations
4. **Follow conventions:** Use proper encoding, line endings, and file structure
5. **Think before git:** Be careful with git operations that affect history

## Enforcement vs. Guidance

- **Enforcement layer:** These rules are enforced via hooks that can block operations
- **Guidance layer:** This document provides proactive guidance to avoid enforcement
- **User bypass:** When rules are violated, users can approve the operation with explicit confirmation

## Adding New Rules

When adding new shared rules:
1. Update this Shared_Rules.md file with the new rule documentation
2. Add the rule to `Rules/Shared/`
3. Update the evaluator if new check types are needed
4. Test the rule to ensure it doesn't break existing functionality
5. Ensure the rule is modular and isolated from other rules