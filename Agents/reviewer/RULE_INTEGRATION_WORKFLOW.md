# Rule Integration Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active  
**Agent**: Reviewer

## Purpose
Integrate rule suggestions from pattern analysis into PLANNER_RULES.md. This workflow validates, formats, and integrates new rules following governance standards.

## Workflow Rule Index

| Rule ID | Trigger | Section |
|---------|---------|---------|
| RI1 | Rule validation and conflict detection | §1 |
| RI2 | Rule formatting and integration | §2 |
| RI3 | Rule activation and testing | §3 |

## Workflow Design Rules

### §1 - Rule Validation and Conflict Detection (RI1)

**Trigger**: New rule suggestion ready for integration  
**Situation**: Validating rule suggestion before integration into PLANNER_RULES.md  
**Judgment**: Validate rule quality and detect conflicts with existing rules before integration

**Detailed Rule**:
- **Duplicate Detection**: Check for duplicate or overlapping rules in PLANNER_RULES.md
- **Conflict Detection**: Check for conflicts with existing rules (contradictory requirements)
- **Trigger Validation**: Validate trigger conditions are clear and actionable
- **Enforcement Validation**: Validate enforcement level is appropriate (hard gate, soft gate, guideline)
- **Category Validation**: Validate category is appropriate and consistent
- **Compliance**: Post `✅ Gate RI1 PASS: Rule validation complete, no conflicts detected`

**Evidence**: Rule validation prevents conflicts and ensures rule quality before integration

### §2 - Rule Formatting and Integration (RI2)

**Trigger**: Rule suggestion validated and ready for integration  
**Situation**: Formatting and integrating rule into PLANNER_RULES.md  
**Judgment**: Use consistent rule formatting and integration pattern

**Detailed Rule**:
- **Rule ID Assignment**: Assign next available PR## ID sequentially
- **Rule Formatting**: Follow PLANNER_RULES.md formatting (title, description, trigger, enforcement)
- **Section Placement**: Place rule in appropriate section based on category
- **Indexing Update**: Update rule index at top of PLANNER_RULES.md
- **Linking Update**: Update any cross-references to rules
- **Compliance**: Post `✅ Gate RI2 PASS: Rule integrated into PLANNER_RULES.md`

**Evidence**: Consistent rule formatting enables automated rule discovery and clear governance

### §3 - Rule Activation and Testing (RI3)

**Trigger**: Rule integrated into PLANNER_RULES.md  
**Situation**: Activating rule and testing enforcement mechanism  
**Judgment**: Test rule enforcement mechanism before full activation

**Detailed Rule**:
- **Enforcement Test**: Test enforcement mechanism (hard gate script, soft gate script, or guideline)
- **Test Plan Execution**: Run test plan to verify rule enforcement works correctly
- **Impact Assessment**: Assess impact on existing plans and workflows
- **Rollback Plan**: Have rollback plan if rule causes issues
- **Gradual Activation**: Consider gradual activation for major rules
- **Compliance**: Post `✅ Gate RI3 PASS: Rule activated and tested successfully`

**Evidence**: Testing prevents rule enforcement issues and ensures smooth integration

## Rule Integration Pipeline

### Step 1: Rule Validation
1. **Duplicate Check**: Check for duplicate rules in PLANNER_RULES.md
2. **Conflict Check**: Check for conflicts with existing rules
3. **Trigger Validation**: Validate trigger conditions are clear
4. **Enforcement Validation**: Validate enforcement level is appropriate
5. **Category Validation**: Validate category is appropriate
6. **Quality Gate**: Pass validation check (RI1)

### Step 2: Rule Formatting
1. **ID Assignment**: Assign next available PR## ID
2. **Title Formatting**: Format title according to PLANNER_RULES.md standards
3. **Description Formatting**: Format description with clear requirements
4. **Trigger Formatting**: Format trigger conditions clearly
5. **Enforcement Formatting**: Format enforcement level clearly
6. **Evidence Linking**: Link to source findings and pattern analysis

### Step 3: Rule Integration
1. **Section Placement**: Place rule in appropriate section
2. **Index Update**: Update rule index at top of PLANNER_RULES.md
3. **Cross-Reference Update**: Update any cross-references
4. **Database Update**: Add rule to rules table with source information
5. **Git Commit**: Commit changes to PLANNER_RULES.md
6. **Compliance Gate**: Pass integration check (RI2)

### Step 4: Rule Activation
1. **Enforcement Test**: Test enforcement mechanism
2. **Test Plan Execution**: Run test plan
3. **Impact Assessment**: Assess impact on existing plans
4. **Rollback Planning**: Prepare rollback plan
5. **Gradual Activation**: Consider gradual activation
6. **Compliance Gate**: Pass activation check (RI3)

### Step 5: Documentation
1. **Changelog Update**: Update changelog with new rule
2. **Communication**: Communicate new rule to stakeholders
3. **Training**: Provide training if needed
4. **Monitoring**: Monitor rule effectiveness
5. **Feedback Collection**: Collect feedback on rule effectiveness
6. **Compliance**: Post `✅ Gate RI-COMPLETE: Rule integration complete, PR{##} activated`

## Output Format

### Rule Integration Results JSON
```json
{
  "integration_timestamp": "2026-07-22T16:00:00Z",
  "rule_id": "PR17",
  "rule_title": "Governance Landmine Screening",
  "validation_status": "passed",
  "conflicts_detected": 0,
  "integration_status": "completed",
  "activation_status": "activated",
  "source_findings": [1, 3, 5, 8, 12, 15, 18],
  "pattern_analysis_id": "P001",
  "enforcement_mechanism": "hard_gate_script",
  "test_results": "passed",
  "impact_assessment": "low"
}
```

## Implementation Scripts

### Rule Integration Script
- **Location**: `Agents/reviewer/scripts/rule_integration/rule_integration.py`
- **Purpose**: Execute complete rule integration pipeline
- **Usage**: `python rule_integration.py --rule-suggestion rule_suggestion.json`

### Rule Validation Script
- **Location**: `Agents/reviewer/scripts/rule_integration/rule_validation.py`
- **Purpose**: Validate rule suggestion before integration
- **Usage**: `python rule_validation.py --rule-suggestion rule_suggestion.json`

### Rule Testing Script
- **Location**: `Agents/reviewer/scripts/rule_integration/rule_testing.py`
- **Purpose**: Test rule enforcement mechanism
- **Usage**: `python rule_testing.py --rule-id PR17`

## Quality Gates

### Soft Gates (Non-Blocking)
- **SG-Rule-Duplicates**: Warn if potential duplicate rule detected
- **SG-Rule-Conflicts**: Warn if potential conflict detected
- **SG-Rule-Impact**: Warn if rule may have high impact

### Hard Gates (Blocking)
- **HG-Rule-Validation**: Block if rule validation fails
- **HG-Rule-Format**: Block if rule format is invalid
- **HG-Rule-Test**: Block if rule enforcement test fails

## Integration with Pattern Analysis Workflow

1. **Pattern Analysis Trigger**: Pattern analysis workflow generates rule suggestions
2. **Rule Validation**: Rule validation script validates suggestions
3. **Manual Review**: Reviewer manually reviews validated suggestions
4. **Rule Integration**: Rule integration script integrates approved rules
5. **Rule Activation**: Rule testing script activates and tests rules
6. **Feedback Loop**: Pattern analysis monitors rule effectiveness

## Notes

- **Manual Review**: Rule suggestions require manual review before integration
- **Gradual Activation**: Major rules may require gradual activation
- **Rollback Planning**: Always have rollback plan for new rules
- **Monitoring**: Monitor rule effectiveness and adjust as needed
- **Documentation**: Maintain comprehensive documentation for new rules