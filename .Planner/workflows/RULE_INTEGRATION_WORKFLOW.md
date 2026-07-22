# Rule Integration Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Design Phase

## Purpose
Integrate rule suggestions from Reviewer pattern analysis into PLANNER_RULES.md. This is Phase 8 of PLAN_WORKFLOW.md, following GR3 single-responsibility principle (Reviewer analyzes, Planner integrates).

## Workflow Overview

```
Reviewer Rule Suggestions → Rule Review → User Approval → Rule Formatting → Rule Integration → JSON Export
```

## Phase 1: Rule Suggestion Review

**Trigger**: Reviewer provides rule suggestion report  
**Goal**: Review and validate rule suggestions from Reviewer

**Steps**:
1. **Report Analysis**: Analyze Reviewer's rule suggestion report
2. **Evidence Review**: Review evidence for each suggested rule
3. **Priority Assessment**: Assess priority scores and impact
4. **Compatibility Check**: Check compatibility with existing rules
5. **Compliance**: Post `✅ Gate RI-1 PASS: Rule suggestions reviewed and validated`

**Review Criteria**:
- Evidence quality (affected plans, occurrence count)
- Priority score (≥ 5 recommended for integration)
- Compatibility with existing rules
- Enforcement level appropriateness
- Category alignment with PLANNER_RULES.md structure

## Phase 2: User Approval

**Trigger**: Rule suggestions reviewed  
**Goal**: Get user approval for rule integration

**Steps**:
1. **Present Suggestions**: Present top priority rule suggestions to user
2. **Evidence Display**: Display evidence for each suggested rule
3. **Impact Assessment**: Show potential impact on revision reduction
4. **User Decision**: Get user approval/rejection for each suggestion
5. **Compliance**: Post `✅ Gate RI-2 PASS: User approval obtained for rule integration`

**Approval Process**:
```python
def present_rule_suggestions(rule_suggestions):
    approved_rules = []
    
    for suggestion in rule_suggestions[:10]:  # Top 10 suggestions
        print(f"""
Rule ID: {suggestion['rule_id']}
Title: {suggestion['title']}
Description: {suggestion['description']}
Category: {suggestion['category']}
Enforcement Level: {suggestion['enforcement_level']}
Priority Score: {suggestion['integration_priority']}
Evidence:
- Affected Plans: {', '.join(suggestion['evidence']['affected_plans'])}
- Finding Count: {suggestion['evidence']['finding_count']}
- Revision Reduction Potential: {suggestion['evidence']['revision_reduction_potential']}

Pattern Source: {suggestion['pattern_source']}

Integrate this rule? (yes/no)
""")
        
        user_response = input().strip().lower()
        if user_response == 'yes':
            approved_rules.append(suggestion)
    
    return approved_rules
```

## Phase 3: Rule Formatting

**Trigger**: User approval obtained  
**Goal**: Format approved rules according to PLANNER_RULES.md structure

**Steps**:
1. **Section Assignment**: Assign section numbers to new rules
2. **Rule Formatting**: Format rules according to PLANNER_RULES.md schema
3. **Compliance Lines**: Add compliance lines to each rule
4. **Evolution Conditions**: Add evolution conditions to each rule
5. **Compliance**: Post `✅ Gate RI-3 PASS: Rules formatted according to PLANNER_RULES.md structure`

**Formatting Template**:
```python
def format_rule_for_integration(suggestion, section_number):
    formatted_rule = f"""

---

## §{section_number} - {suggestion['title']} ({suggestion['rule_id']})

**Trigger**: `{suggestion['trigger_conditions']}`  
**Situation**: {suggestion['description']}  
**Judgment**: {suggestion['description']}

**Detailed Rule**:
- **Pattern Source**: {suggestion['pattern_source']}
- **Evidence**: Affects {len(suggestion['evidence']['affected_plans'])} plans, {suggestion['evidence']['finding_count']} findings
- **Enforcement Level**: {suggestion['enforcement_level']}
- **Affected Plans**: {', '.join(suggestion['evidence']['affected_plans'])}
- **Revision Reduction Potential**: {suggestion['evidence']['revision_reduction_potential']}
- **Compliance**: Post `✅ Gate {suggestion['rule_id']} PASS: {suggestion['title']}`

**Evolution Condition**: Pattern reoccurs in future findings or evidence strength increases
"""
    
    return formatted_rule
```

## Phase 4: Rule Integration

**Trigger**: Rules formatted  
**Goal**: Integrate formatted rules into PLANNER_RULES.md

**Steps**:
1. **Read Existing Rules**: Read current PLANNER_RULES.md content
2. **Find Insertion Point**: Locate appropriate insertion point (before Evolution section)
3. **Insert Rules**: Insert formatted rules into PLANNER_RULES.md
4. **Update Index**: Update rule index at top of PLANNER_RULES.md
5. **Verify Integration**: Verify rules are correctly integrated
6. **Compliance**: Post `✅ Gate RI-4 PASS: Rules integrated into PLANNER_RULES.md`

**Integration Logic**:
```python
def integrate_rules_into_planner_rules(approved_rules, planner_rules_path):
    # Read existing rules
    with open(planner_rules_path, 'r') as f:
        existing_content = f.read()
    
    # Calculate next section numbers
    section_number = extract_next_section_number(existing_content)
    
    # Format all approved rules
    formatted_rules = ""
    for suggestion in approved_rules:
        formatted_rule = format_rule_for_integration(suggestion, section_number)
        formatted_rules += formatted_rule
        section_number += 1
    
    # Insert rules before Evolution section
    evolution_section = "## Evolution"
    if evolution_section in existing_content:
        updated_content = existing_content.replace(evolution_section, formatted_rules + "\n\n" + evolution_section)
    else:
        updated_content = existing_content + formatted_rules
    
    # Write updated rules
    with open(planner_rules_path, 'w') as f:
        f.write(updated_content)
    
    # Update rule index
    update_rule_index(planner_rules_path, approved_rules)
    
    return approved_rules
```

## Phase 5: JSON Export

**Trigger**: Rules integrated  
**Goal**: Export findings and updated rules to JSON for git persistence

**Steps**:
1. **Findings Export**: Export findings using JSON_EXPORT_FORMAT.md
2. **Rules Export**: Export updated rules using JSON_EXPORT_FORMAT.md
3. **Schema Validation**: Validate JSON exports against schema
4. **Git Commit**: Commit exported JSON files with structured message
5. **Audit Trail**: Update audit log with export event
6. **Compliance**: Post `✅ Gate RI-5 PASS: Findings and rules exported to git`

**Export Logic**:
```python
def export_updated_rules(batch_id, timestamp):
    # Export findings
    findings_export = generate_findings_export(batch_id, timestamp)
    findings_file = f".Planner/roundtable/export/findings/findings_batch_{batch_id}_{timestamp}.json"
    with open(findings_file, 'w') as f:
        json.dump(findings_export, f, indent=2)
    
    # Export updated rules
    rules_export = generate_rules_export(timestamp)
    rules_file = f".Planner/roundtable/export/rules/roundtable_rules_{timestamp}.json"
    with open(rules_file, 'w') as f:
        json.dump(rules_export, f, indent=2)
    
    # Git commit
    commit_message = f"""RoundTable: Export findings and integrated rules for batch {batch_id}

Export timestamp: {timestamp}
Total findings: {findings_export['export_metadata']['total_findings']}
Total rules: {rules_export['export_metadata']['total_rules']}
New rules integrated: {len(approved_rules)}

Generated with Devin RoundTable workflow"""
    
    # Execute git commands
    subprocess.run(['git', 'add', findings_file, rules_file])
    subprocess.run(['git', 'commit', '-m', commit_message])
```

## Quality Gates

- **Gate RI-1**: Rule suggestions must pass evidence review and compatibility check
- **Gate RI-2**: User must explicitly approve each rule before integration
- **Gate RI-3**: Rules must be formatted according to PLANNER_RULES.md structure
- **Gate RI-4**: Rule index must be updated with new rule entries
- **Gate RI-5**: JSON exports must pass schema validation before git commit

## Integration with Plan Workflow

This workflow is Phase 8 of PLAN_WORKFLOW.md, executed by Planner after receiving rule suggestions from Reviewer (Phase 7). This follows GR3 single-responsibility principle:
- **Reviewer**: Analyzes findings patterns and suggests rules (Phase 7)
- **Planner**: Reviews suggestions and integrates approved rules (Phase 8)

## Stop Conditions

**Halt integration if**:
- User rejects all rule suggestions
- Rule suggestions fail compatibility check
- Formatted rules don't match PLANNER_RULES.md structure
- JSON export fails schema validation
- Git commit fails