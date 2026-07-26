# Architect Consistency Fix Workflow

**ID**: WF-ARCH-CONS-FIX  
**Owner**: Architect Agent  
**Frequency**: On-demand (triggered after consistency check review)  
**Duration**: Variable (30-120 minutes depending on issue count)  
**Priority**: High
**Workflow Type**: Single-Execution (executes once and terminates)

## Purpose
Systematic resolution of consistency issues identified by Architect Consistency Check Workflow to improve harness architecture integrity and maintain governance compliance.

## Scope
**Harness Architecture Only**: Governance files, workflows, rules, documentation (excludes /app folder)

**Trigger**: After reviewing consistency check report from Logs/Architect/Consistency Review/

## Roles and Owners
- **Architect Agent**: Executes consistency fixes, validates improvements, documents changes
- **User**: Reviews findings, selects fix strategy, approves architectural changes
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: User reviews consistency check report and requests fixes
- **End State**: Selected consistency issues resolved, harness architecture improved

## Workflow Steps (55 steps)

### Phase 0. Read Consistency Report + Governance Rules
- 1. Read latest consistency check report from Logs/Architect/Consistency Review/
- 2. Parse report structure and identify issues by severity
- 3. Read Rules/Architect/Architect_Rules.md for fix patterns
- 4. Read Workflow/Architect/Reference/Workflow_Template.md for structure compliance
- 5. Store fix context for reference throughout execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT**: "Consistency report loaded - {N} issues identified, {N} critical"

### Phase 1. Select Fix Strategy
- 8. Ask user to select fix strategy using popup menu:
  - **Critical Only**: Fix only critical issues
  - **Critical + High**: Fix critical and high-priority issues
  - **Comprehensive**: Fix all issues (critical, high, medium, low)
  - **Selective**: User selects specific issues to fix
- 9. Store selected fix strategy for execution
- 10. **PRINT**: "Fix strategy selected - {Strategy} will govern issue resolution"

### Phase 2. Prioritize Issues
- 11. Load latest consistency check report
- 12. Filter issues based on selected fix strategy
- 13. Sort issues by severity and impact
- 14. Group issues by consistency variable (file references, terminology, etc.)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT**: "Issues prioritized - {N} issues selected for fix based on {Strategy}"

### Phase 3. Fix Critical Issues
- 17. Start with critical issues (severity: critical)
- 18. For each critical issue:
  - Read the file containing the issue
  - Identify the specific line/pattern causing the issue
  - Apply fix using appropriate method (edit, sed, manual)
  - Validate fix resolves the issue
  - Log fix to session record
- 19. **VALIDATION**: Validate all critical issues resolved (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 20. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 21. **PRINT**: "Critical issues fixed - {N} critical issues resolved"

### Phase 4. Fix High-Priority Issues
- 22. Continue with high-priority issues (severity: high)
- 23. For each high-priority issue:
  - Read the file containing the issue
  - Identify the specific line/pattern causing the issue
  - Apply fix using appropriate method (edit, sed, manual)
  - Validate fix resolves the issue
  - Log fix to session record
- 24. **VALIDATION**: Validate all high-priority issues resolved
- 25. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 26. **PRINT**: "High-priority issues fixed - {N} high-priority issues resolved"

### Phase 5. Fix Medium-Priority Issues (if applicable)
- 27. Continue with medium-priority issues (if comprehensive strategy selected)
- 28. For each medium-priority issue:
  - Read the file containing the issue
  - Identify the specific line/pattern causing the issue
  - Apply fix using appropriate method (edit, sed, manual)
  - Validate fix resolves the issue
  - Log fix to session record
- 29. **VALIDATION**: Validate all medium-priority issues resolved
- 30. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 31. **PRINT**: "Medium-priority issues fixed - {N} medium-priority issues resolved"

### Phase 6. Fix Low-Priority Issues (if applicable)
- 32. Continue with low-priority issues (if comprehensive strategy selected)
- 33. For each low-priority issue:
  - Read the file containing the issue
  - Identify the specific line/pattern causing the issue
  - Apply fix using appropriate method (edit, sed, manual)
  - Validate fix resolves the issue
  - Log fix to session record
- 34. **VALIDATION**: Validate all low-priority issues resolved
- 35. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 36. **PRINT**: "Low-priority issues fixed - {N} low-priority issues resolved"

### Phase 7. Re-Run Consistency Check
- 37. Execute Architect Consistency Check Workflow to validate fixes
- 38. Compare new consistency score with original score
- 39. Verify all selected issues are resolved
- 40. Identify any new issues introduced by fixes
- 41. **VALIDATION**: Validate consistency score improved appropriately
- 42. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 43. **PRINT**: "Re-scan complete - consistency score improved from {old_score} to {new_score}"

### Phase 8. Document Changes
- 44. Update relevant governance files for consistency fixes:
  - INDEX.md (if structural changes made)
  - Workflow/Architect/Reference/Workflow_Template.md (if template fixes)
  - AGENTS.md (if agent capability changes)
- 45. Create fix summary report in Logs/Architect/Consistency Review/Fix_{timestamp}.md
- 46. Log all changes with before/after states
- 47. **VALIDATION**: Validate documentation changes reflect actual fixes
- 48. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 49. **PRINT**: "Documentation complete - fix summary created in Logs/Architect/Consistency Review/"

### Phase 9. Final Validation
- 50. Verify harness architecture consistency improved
- 51. Ensure no new issues introduced
- 52. Validate compliance with Architect rules
- 53. **VALIDATION**: Validate final consistency state meets quality standards
- 54. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 55. **PRINT**: "Final validation complete - workflow terminated"

---

## Issue Fix Patterns

### File Reference Issues
**Pattern**: Replace incorrect file paths with correct paths
**Method**: `sed` for bulk replacements, `edit` for specific lines
**Validation**: Check referenced file exists after fix

### Terminology Issues
**Pattern**: Replace outdated terminology with current terminology
**Method**: `sed` for bulk replacements, `edit` for specific contexts
**Validation**: Check no remaining outdated terminology

### Workflow Structure Issues
**Pattern**: Add missing sections, restructure to match template
**Method**: `edit` for structural changes
**Validation**: Compare against Workflow/Architect/Reference/Workflow_Template.md

### Governance Rule Issues
**Pattern**: Fix rule file structure, add missing rules
**Method**: `edit` for rule file changes
**Validation**: Validate YAML frontmatter and rule structure

### Documentation Issues
**Pattern**: Update INDEX.md, fix categorization
**Method**: `edit` for documentation changes
**Validation**: Check documentation structure compliance

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Harness architecture quality assessment
- **Focus**: Governance file quality and architectural compliance

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific consistency management responsibilities
- **Focus**: Architecture integrity maintenance and governance compliance

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Consistency score improvement metrics
- **Focus**: Architecture consistency metrics and improvement tracking

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Consistency fix state tracking
- **Focus**: Fix progress state and re-scan validation

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Fix strategy selection and execution mode handling
- **Focus**: Prioritized issue resolution and fix execution patterns

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Consistency check runtime requirements
- **Focus**: Scan execution environment and report generation infrastructure

### Workflow Template
- **Architect Tool**: Workflow/Architect/Reference/Workflow_Template.md
- **Architect Customization**: Template compliance validation during fixes
- **Focus**: Ensuring fixes maintain workflow template compliance

## Fix Prioritization Rules

### Critical Issues (Fix Immediately)
- Broken file references (referenced files don't exist)
- Missing Phase 0, Phase 3, Phase 10 in workflows
- Missing Universal Framework References section
- Inconsistent workflow structure across agents
- Missing critical governance files

### High Priority Issues (Fix Soon)
- Terminology inconsistencies
- Missing STATUS TRACKING or VALIDATION entries
- Incomplete Universal Framework coverage
- Cross-reference pattern inconsistencies
- Agent capability mismatches

### Medium Priority Issues (Fix When Time Permits)
- Minor formatting inconsistencies
- Missing Universal Pattern Reference sections
- Documentation categorization issues
- State management inconsistencies
- Runtime prerequisites documentation gaps

### Low Priority Issues (Fix for Cleanliness)
- Comment formatting
- Spelling/grammar in documentation
- Minor stylistic inconsistencies
- Optional optimization opportunities

## Fix Validation

### Before Fix
- Confirm issue exists
- Document current state
- Assess fix complexity
- Estimate fix impact

### After Fix
- Validate issue resolved
- Check for side effects
- Verify no new issues introduced
- Document fix for audit trail

### Re-scan Validation
- Run full consistency check
- Compare scores
- Verify all selected issues resolved
- Check for regression

## Fix Report Structure

```markdown
# Architect Consistency Fix Report

**Fix Date**: {YYYY-MM-DD HH:MM:SS}
**Original Report**: Scan_{timestamp}.md
**Fix Strategy**: {Strategy}
**Issues Fixed**: {N} (Critical: {N}, High: {N}, Medium: {N}, Low: {N})

## Fix Summary

**Original Consistency Score**: {X/100}
**New Consistency Score**: {X/100}
**Improvement**: {+X/-X}

## Issues Fixed

### Critical Issues Fixed
[List of critical issues with fixes applied]

### High-Priority Issues Fixed
[List of high-priority issues with fixes applied]

### Medium-Priority Issues Fixed
[List of medium-priority issues with fixes applied]

### Low-Priority Issues Fixed
[List of low-priority issues with fixes applied]

## Files Modified

[List of files modified with change summary]

## Validation Results

**Re-scan Score**: {X/100}
**Issues Resolved**: {N}/{N}
**New Issues Introduced**: {N}
**Overall Status**: {SUCCESS/PARTIAL/FAILED}

## Next Steps

[Recommendations for remaining issues or further improvements]
```

## Execution Mode Handling

Apply execution mode handling patterns from Workflow/Architect/Reference/Execution_Mode_Patterns.md:
- **Manual Mode**: User confirmation for each fix
- **Auto Mode**: Automatic fixes for file references and terminology
- **Complete Mode**: Automatic fixes for all issue types

## Governance Compliance

All fixes must comply with Rules/Architect/Architect_Rules.md:
- File naming conventions
- Directory structure rules
- Categorization requirements
- Documentation standards

## Risk Assessment

### High-Risk Fixes
- Workflow structure changes
- Universal framework modifications
- Template updates
- Major architectural changes

### Medium-Risk Fixes
- Governance rule changes
- Agent capability modifications
- Cross-reference updates
- Documentation structure changes

### Low-Risk Fixes
- Terminology updates
- File reference corrections
- Minor formatting fixes
- Comment updates

High-risk fixes require user confirmation regardless of execution mode.