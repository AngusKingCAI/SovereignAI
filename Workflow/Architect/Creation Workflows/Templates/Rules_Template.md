---
id: rules-template
status: active
owner: architect-agent
updated: 2026-07-31
purpose: Template for creating agent rules using Always/Never structure
---

# Rules Template

**Purpose**: Template for creating agent rules using Always/Never structure  
**Status**: Template  
**Created**: 2026-07-24  
**Template Type**: Always/Never Format  

---

## Template Structure

```markdown
---
id: {rule-id}
status: active
owner: {agent-name}
updated: {date}
purpose: {brief description}
trigger: always_on
---

# {Agent Name} Rules

## Always

- ALWAYS {specific action}
- ALWAYS {specific action}

## Never

- NEVER {specific action}
- NEVER {specific action}
```

---

## Format Guidelines

### Frontmatter
- **id**: Unique identifier for the rule file
- **status**: Current status (active, draft, deprecated)
- **owner**: Agent or team responsible for the rule
- **updated**: Last modification date
- **purpose**: Brief description of rule scope
- **trigger**: Activation type (always_on, manual, glob)

### Always Section
- Use imperative language with "ALWAYS" prefix
- Focus on required actions and behaviors
- Keep rules specific and actionable
- Each rule should be a single, clear directive

### Never Section
- Use imperative language with "NEVER" prefix
- Focus on prohibited actions and behaviors
- Keep rules specific and actionable
- Each rule should be a single, clear directive

---

## Best Practices

### Rule Creation
- **Keep rules concise**: Each rule should be one line
- **Be specific**: Use concrete actions instead of vague guidelines
- **Use evidence**: Base rules on actual session patterns or issues
- **Test incrementally**: Add rules one at a time and validate
- **Document rationale**: Include session evidence when adding rules

### Rule Quality
- **Actionable**: Rules should clearly state what to do/not do
- **Enforceable**: Rules should be verifiable and testable
- **Non-redundant**: Avoid duplicate or overlapping rules
- **Scoped**: Rules should have clear boundaries and applicability
- **Current**: Remove outdated rules that no longer apply

### Session Analysis
- **Review logs**: Analyze session logs for patterns and issues
- **Identify gaps**: Look for repeated mistakes or confusion
- **Extract patterns**: Convert session learnings into rule format
- **Validate evidence**: Ensure rules are based on real issues

---

## Rule Examples

### Example from Session Analysis

**Session Pattern**: Multiple restarts required for hook changes to take effect

**Rule Addition**:
```markdown
## Always
- ALWAYS inform users when infrastructure changes require Devin CLI restart
```

**Evidence**: User had to restart Devin CLI multiple times for hook changes to take effect, causing confusion about whether implementation was correct.

---

### Example from Best Practices Research

**Research Finding**: JSON response format allows agent continuation vs exit codes

**Rule Addition**:
```markdown
## Always
- ALWAYS use JSON response format instead of exit codes for blocking actions
```

**Evidence**: Web search revealed that exit code 2 stops agent workflow while JSON permissionDecision allows continuation.

---

## Rule Addition Process

### 1. Analyze Session Logs
- Review session logs for patterns and issues
- Identify repeated problems or confusion
- Extract specific behaviors that should be enforced

### 2. Research Best Practices
- Search for industry standards and guidelines
- Verify technical approaches through documentation
- Validate findings against multiple sources

### 3. Draft Rule
- Convert pattern to Always/Never format
- Ensure rule is specific and actionable
- Include evidence from session or research

### 4. Validate Rule
- Test rule in isolation before adding
- Verify rule doesn't conflict with existing rules
- Ensure rule is scoped appropriately

### 5. Add to Rules File
- Add rule one at a time using popup confirmation
- Update file with proper formatting
- Document addition session/date

---

## Template Usage

### For New Agents
1. Copy this template structure
2. Customize frontmatter for specific agent
3. Add Always/Never sections based on agent scope
4. Populate with agent-specific rules

### For Rule Updates
1. Review existing rules for relevance
2. Analyze recent sessions for new patterns
3. Add new rules one at a time with validation
4. Remove outdated rules that no longer apply

### For Template Maintenance
1. Update format guidelines based on best practices research
2. Add new examples from successful rule additions
3. Refine process based on usage patterns
4. Keep template aligned with Devin CLI documentation

---

## Compliance Checklist

- [ ] Frontmatter follows template structure
- [ ] Always section uses "ALWAYS" prefix
- [ ] Never section uses "NEVER" prefix
- [ ] Rules are specific and actionable
- [ ] Rules are based on session evidence or research
- [ ] Rules are tested before deployment
- [ ] Format follows Devin CLI documentation guidelines
- [ ] File location complies with directory structure
- [ ] Template is compatible with existing infrastructure