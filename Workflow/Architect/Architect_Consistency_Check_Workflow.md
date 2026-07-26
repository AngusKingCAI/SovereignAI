# Architect Consistency Check Workflow

**ID**: WF-ARCH-CONS-CHECK  
**Owner**: Architect Agent  
**Frequency**: On-demand (recommended: weekly basic, monthly comprehensive)  
**Duration**: Variable (15-60 minutes depending on scope)  
**Priority**: High

## Purpose
Systematic validation of harness architecture consistency across the entire project to identify structural issues, broken references, terminology inconsistencies, and governance gaps.

## Scope
**Harness Architecture Only**: Governance files, workflows, rules, documentation (excludes /app folder)

**Report Location**: Logs/Architect/Consistency Review/Scan_{YYYY-MM-DD_HH-MM-SS}.md

## Roles and Owners
- **Architect Agent**: Executes consistency check, generates report, analyzes findings
- **User**: Reviews findings, decides on fix strategy, approves architectural changes
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: User requests consistency check OR before/after major architectural changes
- **End State**: Comprehensive consistency report generated in Logs/Architect/Consistency Review/

## Workflow Steps (47 steps)

### Phase 0. Read Architect Rules + Scan Scope
- 1. Read Rules/Architect/Architect_Rules.md to understand governance constraints
- 2. Read Workflow/Architect/Reference/Workflow_Template.md for workflow structure patterns
- 3. Determine scan scope (full harness vs specific components)
- 4. Store governance context for reference throughout scan
- 5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 6. **PRINT**: "Architect rules loaded - initiating harness architecture consistency scan"

### Phase 1. Select Scan Strategy
- 7. Ask user to select scan strategy using popup menu:
  - **Full Comprehensive**: All 10 consistency variables (recommended monthly)
  - **Basic Essential**: File references + terminology + workflow structure (recommended weekly)
  - **Targeted**: User selects specific consistency variables
  - **Quick Check**: File references only (recommended before changes)
- 8. Store selected scan strategy for execution
- 9. **PRINT**: "Scan strategy selected - {Strategy} will govern consistency check scope"

### Phase 2. Harness Architecture File Discovery
- 10. Use `find` to enumerate all harness architecture files:
  - `find /c/SovereignAI -name "*.md" -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md"`
- 11. Exclude /app folder from scan results
- 12. Generate file inventory with paths and types
- 13. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 14. **PRINT**: "File discovery complete - {N} harness architecture files identified"

### Phase 3. File Reference Consistency Check
- 15. Extract all file references using `grep -r "Workflow/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/`
- 16. Extract all Rules/ references using `grep -r "Rules/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/`
- 17. Validate each referenced file exists at specified path
- 18. Log broken references with file locations
- 19. **VALIDATION**: Validate file reference extraction completed successfully
- 20. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 21. **PRINT**: "File reference check complete - {N} broken references found"

### Phase 4. Terminology Consistency Check
- 22. Search for outdated terminology: `grep -r "gate\|validation" /c/SovereignAI/Workflow/`
- 23. Check for "Workflow_Template.md" location references
- 24. Validate framework naming (Quality_Metrics vs Performance_Metrics)
- 25. Check agent naming convention consistency
- 26. **VALIDATION**: Validate terminology check completed successfully
- 27. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 28. **PRINT**: "Terminology check complete - {N} terminology inconsistencies found"

### Phase 5. Workflow Structure Consistency Check
- 29. Compare each workflow against Workflow/Architect/Reference/Workflow_Template.md
- 30. Check for Phase 0, Phase 3, Phase 10 presence
- 31. Validate STATUS TRACKING entries in each phase
- 32. Validate VALIDATION entries in each phase
- 33. Check Universal Framework References section presence
- 34. Validate step numbering sequential consistency
- 35. **VALIDATION**: Validate workflow structure check completed successfully
- 36. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 37. **PRINT**: "Workflow structure check complete - {N} structure issues found"

### Phase 6. Additional Consistency Checks (if full scan)
- 38. Governance Rule Consistency: Check Rules/ files structure and patterns
- 39. Documentation Structure: Validate INDEX.md and documentation conventions
- 40. Agent Capability Alignment: Compare AGENTS.md with actual capabilities
- 41. Universal Framework Coverage: Check proper separation and references
- 42. Execution Strategy Consistency: Validate execution patterns across agents
- 43. State Management Consistency: Check state schemas and tracking patterns
- 44. Runtime Prerequisites: Validate runtime infrastructure documentation
- 45. **VALIDATION**: Validate additional checks completed successfully
- 46. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 47. **PRINT**: "Additional consistency checks complete - full scan analysis finished"

### Phase 7. Report Generation
- 48. Create Logs/Architect/Consistency Review/ directory if not exists
- 49. Generate report with timestamp: Scan_{YYYY-MM-DD_HH-MM-SS}.md
- 50. Include executive summary with overall consistency score
- 51. Document findings for each consistency variable checked
- 52. Classify issues by severity (Critical/High/Medium/Low)
- 53. Provide actionable recommendations with timeline
- 54. **VALIDATION**: Validate report generation completed successfully
- 55. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 56. **PRINT**: "Report generation complete - report saved to Logs/Architect/Consistency Review/"

### Phase 8. Session Logging + Validate
- 57. Log scan parameters and results to Logs/Architect/
- 58. Generate scan attestation hash for verification
- 59. **VALIDATION**: Validate session logging completed successfully
- 60. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 61. **PRINT**: "Session logging complete - consistency check workflow finished"

### Phase 9. Return to Phase 0
- 62. **PRINT** "Consistency check cycle complete - returning to Phase 0 for next scan"
- 63. **PRINT** "Architect agent ready - awaiting next consistency check request"
- 64. Return to step 1

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
- **Architect Customization**: Consistency score metrics and improvement tracking
- **Focus**: Architecture consistency metrics and baseline tracking

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Consistency check state tracking
- **Focus**: Scan progress state and report generation tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Scan strategy selection and execution patterns
- **Focus**: Prioritized consistency checking and analysis execution

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Consistency check runtime requirements
- **Focus**: Scan execution environment and report generation infrastructure

### Workflow Template
- **Architect Tool**: Workflow/Architect/Reference/Workflow_Template.md
- **Architect Customization**: Template compliance validation during scans
- **Focus**: Ensuring workflows maintain template compliance

---

## Consistency Variables

### 1. File Reference Consistency
- **Check**: All referenced files exist at specified paths
- **Scope**: Workflow files, rule files, reference documents
- **Variables**: 
  - `Workflow/` path references in workflow files
  - `Rules/` path references in workflow files  
  - `Workflow_Reference/` path references
  - Agent-specific Reference/ path references
  - Template path references
  - External file references (INDEX.md, AGENTS.md)

### 2. Terminology Consistency
- **Check**: Consistent terminology across all governance files
- **Scope**: All markdown files in harness architecture
- **Variables**:
  - "gate" vs "validation" terminology
  - "Workflow_Template.md" location references
  - Framework naming (Quality_Metrics vs Performance_Metrics)
  - Agent naming conventions
  - Phase naming conventions

### 3. Workflow Structure Consistency
- **Check**: All workflows follow Architect template structure
- **Scope**: All workflow files in Workflow/ directory
- **Variables**:
  - Phase 0-10 structure compliance
  - STATUS TRACKING entries presence
  - VALIDATION entries presence
  - PRINT commands presence
  - Universal Framework References section
  - Universal framework coverage (6 frameworks)
  - Step numbering sequential consistency
  - Header metadata completeness

### 4. Governance Rule Consistency
- **Check**: Rules files are properly structured and consistent
- **Scope**: All Rules/{Agent}/{Agent}_Rules.md files
- **Variables**:
  - YAML frontmatter structure
  - Rule naming conventions
  - Rule categorization patterns
  - Rule enforcement patterns
  - Dependencies between rules

### 5. Documentation Structure Consistency
- **Check**: Documentation follows architectural conventions
- **Scope**: INDEX.md, Docs/ directory structure
- **Variables**:
  - INDEX.md references accuracy
  - File categorization compliance
  - Directory structure adherence
  - Documentation placement conventions
  - Categorization rules compliance

### 6. Agent Capability Consistency
- **Check**: Agent descriptions match actual capabilities
- **Scope**: AGENTS.md, workflow files, rule files
- **Variables**:
  - AGENTS.md agent descriptions
  - Workflow capabilities vs AGENTS.md
  - Role responsibilities vs actual work
  - Rule files vs agent scope
  - Cross-agent dependencies

### 7. Universal Framework Coverage
- **Check**: Proper separation of universal vs agent-specific content
- **Scope**: Workflow_Reference/ and agent Reference/ folders
- **Variables**:
  - Universal framework references in agent workflows
  - No agent-specific content in Workflow_Reference/
  - No universal content in agent Reference/
  - Universal Pattern Reference sections presence
  - Cross-reference patterns consistency

### 8. Execution Strategy Consistency
- **Check**: Execution patterns are consistent across agents
- **Scope**: Execution mode patterns, implementation modes
- **Variables**:
  - Execution mode definitions
  - Implementation mode patterns
  - Quota handling references
  - Execution strategy guidelines references
  - Cross-agent execution pattern alignment

### 9. State Management Consistency
- **Check**: State schemas and tracking patterns are consistent
- **Scope**: State schemas, state tracking in workflows
- **Variables**:
  - State schema definitions for each agent
  - State tracking patterns in workflows
  - State persistence mechanisms
  - State variable naming conventions
  - State management guidelines references

### 10. Runtime Prerequisites Consistency
- **Check**: Runtime infrastructure documentation is accurate
- **Scope**: Runtime paths, Scripts/, .devin/, Logs/ directories
- **Variables**:
  - Referenced runtime paths existence
  - Scripts/ directory structure
  - .devin/ configuration files
  - Logs/ directory structure
  - Runtime prerequisites documentation accuracy

## Consistency Check Process

### Phase 1: Harness Architecture Scan
1. **File Discovery**: Use `find` to enumerate all harness architecture files
2. **Pattern Matching**: Use `grep` to extract specific patterns from files
3. **Cross-Reference Analysis**: Verify all file references exist
4. **Structure Validation**: Validate workflow structure compliance
5. **Terminology Analysis**: Check for inconsistent terminology

### Phase 2: Detailed Variable Analysis
1. **File Reference Validation**: Check each referenced file exists
2. **Workflow Structure Validation**: Compare workflows against template
3. **Governance Rule Validation**: Check rule file structure consistency
4. **Documentation Validation**: Verify INDEX.md and documentation structure
5. **Framework Coverage Validation**: Check universal framework usage

### Phase 3: Issue Aggregation
1. **Severity Classification**: Classify issues as Critical/High/Medium/Low
2. **Categorization**: Group issues by consistency variable
3. **Impact Analysis**: Assess impact on harness functionality
4. **Recommendation Generation**: Generate fix recommendations

### Phase 4: Report Generation
1. **Report Structure**: Create comprehensive report with findings
2. **Issue Prioritization**: Order issues by severity and impact
3. **Fix Recommendations**: Provide specific fix suggestions
4. **Metrics Summary**: Provide consistency metrics

## Report Structure

```markdown
# Architect Consistency Check Report

**Scan Date**: {YYYY-MM-DD HH:MM:SS}
**Scan Scope**: Harness Architecture (excludes /app folder)
**Report Location**: Logs/Architect/Consistency Review/Scan_{YYYY-MM-DD_HH-MM-SS}.md

## Executive Summary

**Overall Consistency Score**: {X/100}
**Critical Issues**: {N}
**High Issues**: {N}
**Medium Issues**: {N}
**Low Issues**: {N}

## Consistency Variable Results

### 1. File Reference Consistency
**Status**: {PASS/FAIL/WARNING}
**Issues Found**: {N}
**Critical Issues**: {N}

{Detailed findings}

### 2. Terminology Consistency
**Status**: {PASS/FAIL/WARNING}
**Issues Found**: {N}
**Critical Issues**: {N}

{Detailed findings}

[... continue for all 10 variables]

## Critical Issues Summary

[Critical issues requiring immediate attention]

## High Priority Issues

[High priority issues]

## Medium Priority Issues

[Medium priority issues]

## Low Priority Issues

[Low priority issues]

## Consistency Metrics

**File Reference Accuracy**: {X}%
**Terminology Consistency**: {X}%
**Workflow Structure Compliance**: {X}%
**Governance Rule Consistency**: {X}%
**Documentation Structure Accuracy**: {X}%
**Agent Capability Alignment**: {X}%
**Universal Framework Coverage**: {X}%
**Execution Strategy Consistency**: {X}%
**State Management Consistency**: {X}%
**Runtime Prerequisites Accuracy**: {X}%

## Recommendations

### Immediate Actions (Critical Issues)
[Recommendations for critical issues]

### Short-term Actions (High Priority)
[Recommendations for high priority issues]

### Long-term Improvements (Medium/Low Priority)
[Recommendations for medium/low priority issues]

## Next Steps

1. Review critical issues
2. Implement immediate fixes
3. Schedule short-term improvements
4. Plan long-term architectural enhancements
```

## Implementation Workflow

Yes, we need a separate workflow for implementing these changes. This should be:

**Architect Consistency Fix Workflow**: 
- Triggered after consistency check report review
- Focuses on systematic resolution of identified issues
- Prioritizes critical and high-priority issues
- Maintains audit trail of changes
- Includes validation after each fix

## Scan Frequency

**Recommended Scan Schedule**:
- **Before major architectural changes**: Full consistency check
- **After architectural refactoring**: Full consistency check  
- **Weekly automated scan**: Basic consistency check (file references only)
- **Monthly comprehensive scan**: Full consistency check with detailed report

## Scan Execution Commands

### File Discovery
```bash
find /c/SovereignAI -name "*.md" -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md"
```

### Pattern Extraction
```bash
grep -r "Workflow/" /c/SovereignAI/Workflow/
grep -r "Rules/" /c/SovereignAI/Workflow/
grep -r "gate\|validation" /c/SovereignAI/Workflow/
```

### Cross-Reference Validation
```bash
# Extract all Workflow/ references and validate file existence
grep -rh "Workflow/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/ | sort -u
```

## Consistency Scoring

**Overall Score Calculation**:
- File Reference Consistency: 20%
- Terminology Consistency: 10%
- Workflow Structure Consistency: 20%
- Governance Rule Consistency: 10%
- Documentation Structure: 10%
- Agent Capability Alignment: 10%
- Universal Framework Coverage: 10%
- Execution Strategy Consistency: 5%
- State Management Consistency: 3%
- Runtime Prerequisites: 2%

**Score Thresholds**:
- 90-100: Excellent - No critical issues
- 80-89: Good - Minor issues only
- 70-79: Fair - Some medium issues
- 60-69: Poor - High priority issues present
- Below 60: Critical - Architectural integrity at risk