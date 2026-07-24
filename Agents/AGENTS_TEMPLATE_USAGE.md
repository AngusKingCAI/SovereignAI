# AGENTS.md Template Usage Guide

## Overview

The `AGENTS_TEMPLATE.md` provides an industry-standard template for creating agent documentation in the SovereignAI project. It combines the AGENTS.md open standard (used by Anthropic, OpenAI, Google, and 20+ AI coding tools) with SovereignAI-specific governance framework extensions.

## Template Structure

The template consists of two main parts:

### 1. Industry-Standard Base Sections (Lines 1-66)
These sections follow the AGENTS.md open standard specification and are compatible with 20+ major AI coding tools including:
- OpenAI Codex
- Cursor
- GitHub Copilot
- Google Jules
- Aider
- Windsurf
- Zed
- Sourcegraph Amp

**Standard Sections:**
- Agent name and purpose statement
- Core Philosophy (optional)
- Purpose (2-3 sentence description)
- Setup Commands (exact commands)
- Code Style (executable rules)
- Testing (framework and commands)
- Boundaries (Always/Ask First/Never pattern)
- Security Considerations
- Integration Points
- Agent-Specific Constraints
- Tool Access

### 2. SovereignAI Framework Extensions (Lines 67-95)
These sections add project-specific governance framework requirements:
- Constitutional Framework
- Scope Boundaries (IN SCOPE/OUT OF SCOPE/SCOPE DRIFT PREVENTION)
- Git Operations Restrictions

## How to Use the Template

### Step 1: Copy the Template
```bash
cp Agents/AGENTS_TEMPLATE.md Agents/{AgentName}/AGENTS.md
```

### Step 2: Replace Placeholders
Replace all `{placeholder}` text with agent-specific information:

**Required Placeholders:**
- `{Agent Name}` - The name of your agent (e.g., "Architect", "Planner")
- `{One-line purpose statement}` - Single line describing what the agent does
- `{2-3 sentence description}` - More detailed purpose description
- `{exact command}` - Actual commands for setup, testing, etc.
- `{Language/Framework}` - Specific technologies used
- `{framework name}` - Testing framework used
- `{directory pattern}` - Where test files are located
- `{PRINCIPLES.md/AGENTS.md}` - Constitutional framework reference
- `{AgentName}` - Agent name for file paths
- `{agent}` - Lowercase agent name for skills path

**Optional Placeholders:**
- `{Optional: Core philosophy}` - For complex agents needing philosophical guidance
- `{Specific in-scope activities}` - Detailed in-scope responsibilities
- `{Specific out-of-scope activities}` - Detailed out-of-scope boundaries
- `{Specific scope drift prevention measures}` - Specific prevention strategies
- `{Agent-specific limitations}` - Any additional constraints
- `{Specific tools and permissions}` - Tool access requirements

### Step 3: Fill in Industry-Standard Sections

**Setup Commands Example:**
```markdown
## Setup Commands
- Install dependencies: `pip install -r requirements.txt`
- Start development: `python main.py`
- Run tests: `pytest tests/`
- Build: `python setup.py build`
```

**Code Style Example:**
```markdown
## Code Style
- Python 3.8+ with type hints
- Black formatter with line length 88
- isort for import organization
- PEP 8 naming conventions
- Google-style docstrings
```

**Testing Example:**
```markdown
## Testing
- Test framework: pytest
- Test command: `pytest tests/ -v --cov`
- Coverage requirements: 80% minimum
- Test file locations: `tests/test_*.py`
```

**Boundaries Example:**
```markdown
## Boundaries
### Always
- Follow architectural guidelines
- Verify directory structure compliance
- Log all architectural decisions
- Check constitutional compliance

### Ask First
- Make architectural changes affecting multiple agents
- Modify directory structure
- Change governance rules
- Approve phase transitions

### Never
- Implement application code directly
- Skip gate verification
- Modify git state without approval
- Bypass constitutional compliance
```

### Step 4: Fill in SovereignAI Extensions

**Constitutional Framework Example:**
```markdown
## Constitutional Framework
Operate under PRINCIPLES.md workflow principles
```

**Scope Boundaries Example:**
```markdown
## Scope Boundaries

### ✅ IN SCOPE
- Infrastructure design and architecture planning
- Directory structure and file organization standards
- Workflow definition and procedure documentation
- Gate system design and verification

### ❌ OUT OF SCOPE
- SovereignAI application code implementation (deferred to Phase 12)
- Direct application feature development (deferred to Phase 12)
- Application-level testing and debugging (deferred to Phase 12)

### 🚫 SCOPE DRIFT PREVENTION
Stop immediately if asked to implement SovereignAI application features. Redirect requests to appropriate future phases.
```

## Example: Completed Architect Agent AGENTS.md

Here's how the template looks when completed for the Architect agent:

```markdown
# Architect Agent

Design deterministic engineering infrastructure and harness systems for AI-driven software development.

<!--
TEMPLATE STRUCTURE:
- Base sections (above): Industry-standard AGENTS.md format (compatible with 20+ AI coding tools)
- SovereignAI extensions (below): Project-specific governance framework additions

INDUSTRY STANDARD SECTIONS:
- Core Philosophy, Purpose, Setup Commands, Code Style, Testing, Boundaries
- Security Considerations, Integration Points, Agent-Specific Constraints, Tool Access

SOVEREIGNAI EXTENSIONS:
- Constitutional Framework, Scope Boundaries, Git Operations Restrictions
-->

## Core Philosophy
Infrastructure owns authority. Agents own intelligence. Authority and intelligence must never exist inside the same component.

## Purpose
The Architect agent is responsible for designing deterministic engineering infrastructure and harness systems for AI-driven software development, following infrastructure-first principles.

## Setup Commands
- Install dependencies: `No external dependencies required`
- Start development: `Invoke architect skill via .devin/skills/architect/SKILL.md`
- Run tests: `Verify directory structure compliance manually`
- Build: `N/A - infrastructure design only`

## Code Style
- Markdown documentation
- Clear section hierarchy
- Consistent formatting
- Explicit boundaries and constraints

## Testing
- Test framework: Manual verification
- Test command: Verify directory structure compliance
- Coverage requirements: All infrastructure components documented
- Test file locations: `Logs/Architect/Conversations/`

## Boundaries
### Always
- Follow infrastructure-first principles
- Verify directory structure compliance
- Enforce IDE architecture rules
- Check constitutional compliance

### Ask First
- Make architectural changes affecting multiple agents
- Modify directory structure
- Change governance rules
- Approve phase transitions

### Never
- Implement application code directly
- Skip gate verification
- Modify git state without approval
- Bypass constitutional compliance

## Security Considerations
- No sensitive data in infrastructure documentation
- Follow least privilege access principles
- Verify all architectural decisions for security implications

## Integration Points
- **Rules**: `Rules/Architect/Architect_Rules.md`
- **Workflows**: `Workflow/Architect/Architect_Implementation_Cycle.md`
- **Skills**: `.devin/skills/architect/SKILL.md`
- **Logs**: `Logs/Architect/`

---

## SovereignAI Framework Extensions

## Constitutional Framework
Operate under infrastructure-first principles

## Scope Boundaries

### ✅ IN SCOPE
- Infrastructure design and architecture planning
- Directory structure and file organization standards
- Workflow definition and procedure documentation
- Gate system design and verification
- Constitutional compliance verification
- IDE architecture rules definition and enforcement

### ❌ OUT OF SCOPE
- SovereignAI application code implementation (deferred to Phase 12)
- Direct application feature development (deferred to Phase 12)
- Application-level testing and debugging (deferred to Phase 12)
- Direct file editing in App/ directory (reference only)
- Production deployment operations (deferred to Phase 12)
- User interface development (deferred to Phase 12)
- Database schema modifications (deferred to Phase 12)

### 🚫 SCOPE DRIFT PREVENTION
Stop immediately if asked to implement SovereignAI application features. Redirect requests to appropriate future phases.

### 🚫 GIT OPERATIONS RESTRICTIONS
**NO Restore or Pull operations unless user explicitly specifies**
**Pushing to git is permitted as it is reversible**

## Agent-Specific Constraints
Architect agent operates under infrastructure-first principles and must maintain separation between authority and intelligence.

## Tool Access
Architect agent requires read access to all project files for architecture verification and design.
```

## Best Practices

### 1. Keep It Concise
- Industry standard recommends 60-300 lines
- Current template is 95 lines
- Focus on essential information
- Link to detailed docs rather than duplicating

### 2. Use Exact Commands
- Always provide copy-pasteable commands
- Include version numbers where relevant
- Specify exact file paths
- Use consistent command patterns

### 3. Be Specific About Boundaries
- Use Always/Ask First/Never pattern consistently
- Provide clear examples for each category
- Include rationale for boundaries
- Reference governance documents where applicable

### 4. Maintain SovereignAI Framework
- Always include SovereignAI extensions
- Keep constitutional framework references
- Maintain scope boundary structure
- Follow git operation restrictions

### 5. Update Regularly
- Keep commands up to date
- Review boundaries periodically
- Update integration points when structure changes
- Maintain consistency across agents

## Troubleshooting

### Template Not Found
Ensure you're copying from `Agents/AGENTS_TEMPLATE.md` and not from agent-specific AGENTS.md files.

### Placeholders Not Replaced
After copying, search for `{` and `}` to find any remaining placeholders that need to be filled in.

### Tool Compatibility Issues
If you experience issues with specific AI coding tools, verify that:
- Industry-standard sections are complete
- Commands are exact and copy-pasteable
- File paths are correct
- Markdown formatting is valid

### SovereignAI Framework Issues
If governance framework integration fails, check:
- Constitutional framework references are correct
- Scope boundaries follow the emoji pattern
- Git operation restrictions text matches standard
- Integration points file paths are accurate

## Template Evolution

The template is designed to evolve with:
- Industry standards updates (via AGENTS.md specification)
- SovereignAI governance framework changes
- Best practice improvements from the community
- Tool ecosystem developments

For template improvement suggestions, reference the AGENTS.md specification at https://agents.md/ and the SovereignAI governance framework in PRINCIPLES.md.

## Related Documentation

- **AGENTS.md Specification**: https://agents.md/
- **SovereignAI Principles**: `PRINCIPLES.md`
- **IDE Architecture Rules**: `Rules/Architect/IDE_Architecture_Rules.md`
- **Agent Documentation**: `Agents/{AgentName}/AGENTS.md`
- **Workflow Documentation**: `Workflow/{AgentName}/`

## Support

For template usage questions or issues:
1. Review this usage guide
2. Check the AGENTS.md specification
3. Reference existing agent AGENTS.md files
4. Consult SovereignAI governance documentation
