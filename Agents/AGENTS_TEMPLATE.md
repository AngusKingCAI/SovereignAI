# {Agent Name} Agent

{One-line purpose statement}

## Core Philosophy
{Optional: Core philosophy for complex agents}

## Purpose
{2-3 sentence description of what this agent does}

## Setup Commands
- Install dependencies: `{exact command}`
- Start development: `{exact command}`
- Run tests: `{exact command}`
- Build: `{exact command}`

## Code Style
- {Language/Framework} specific conventions
- {Formatter} configuration
- {Line length} limits
- {Import organization} rules
- {Naming conventions}

## Testing
- Test framework: {framework name}
- Test command: `{exact command}`
- Coverage requirements: {percentage/requirements}
- Test file locations: {directory pattern}

## Boundaries
### Always
- {Actions this agent always performs}
- {Mandatory behaviors}

### Ask First
- {Actions requiring user confirmation}
- {Situations needing human input}

### Never
- {Actions this agent never performs}
- {Strict boundaries and restrictions}

## Security Considerations
- {Security constraints}
- {Data handling requirements}
- {Access limitations}

## Integration Points
- **Rules**: `Rules/{AgentName}/{Agent}_Rules.md`
- **Workflows**: `Workflow/{AgentName}/{Agent}_Workflow.md`
- **Skills**: `.devin/skills/{agent}/SKILL.md`
- **Logs**: `Logs/{AgentName}/`
- **Rule Cache Skills**: `.devin/skills/create-rule-cache/SKILL.md`, `.devin/skills/remind-rules/SKILL.md`, `.devin/skills/validate-compliance/SKILL.md`
- **Rule Cache Scripts**: `Scripts/src/rule_cache/md_rule_parser.py`, `Scripts/src/rule_cache/agent_compliance_validator.py`
- **Cache Storage**: `Scripts/config/rule_cache/{phase}_{agent}_cache.json`
- **Compliance Reports**: `Logs/{AgentName}/Gates/compliance_reports.json`

---

## SovereignAI Framework Extensions

## Constitutional Framework
Operate under {PRINCIPLES.md/AGENTS.md} constitutional principles

## Scope Boundaries

### ✅ IN SCOPE
- {Specific in-scope activities}
- {Agent responsibilities}

### ❌ OUT OF SCOPE
- {Specific out-of-scope activities}
- {Deferred to other agents/phases}

### 🚫 SCOPE DRIFT PREVENTION
{Specific scope drift prevention measures}

### 🚫 GIT OPERATIONS RESTRICTIONS
**NO Restore or Pull operations unless user explicitly specifies**
**Pushing to git is permitted as it is reversible**

## Agent-Specific Constraints
{Agent-specific limitations and requirements}

## Tool Access
{Specific tools and permissions this agent requires}
