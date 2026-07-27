# Architect Consistency Check Workflow

**ID**: WF-ARCH-CONS-CHECK  
**Owner**: Architect Agent  
**Frequency**: On-demand (recommended: weekly basic, monthly comprehensive)  
**Duration**: Variable (15-60 minutes depending on scope)  
**Priority**: High
**Workflow Type**: Single-Execution
**Execution Modes**: Full Comprehensive, Basic Essential, Targeted, Quick Check

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

## Workflow Steps (73 steps)

### Phase 0. Read Architect Rules + Scan Scope
- 1. Read Rules/Architect/Architect_Rules.md to understand governance constraints
- 2. Read Workflow/Workflow_Reference/Workflow_Template.md for workflow structure patterns
- 3. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 4. Determine scan scope (full harness vs specific components)
- 5. Store governance context for reference throughout scan
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT**: "Architect rules loaded - initiating harness architecture consistency scan"

### Phase 1. Select Scan Strategy
- 7. Ask user to select scan strategy using popup menu:
  - **Full Comprehensive**: All 13 consistency variables (recommended monthly)
  - **Basic Essential**: File references + terminology + workflow structure (recommended weekly)
  - **Targeted**: User selects specific consistency variables
  - **Quick Check**: File references only (recommended before changes)
- 8. Store selected scan strategy for execution
- 9. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 10. **PRINT**: "Scan strategy selected - {Strategy} will govern consistency check scope"

### Phase 2. Harness Architecture File Discovery
- 12. Use `find` to enumerate all harness architecture files:
  - `find /c/SovereignAI -name "*.md" -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md"`
- 13. Exclude /app folder from scan results
- 14. Generate file inventory with paths and types
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT**: "File discovery complete - {N} harness architecture files identified"

### Phase 3. File Reference Consistency Check
- 17. **SCAN**: Read each harness architecture file line by line to extract all file references
- 18. Extract all file references using `grep -r "Workflow/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/` as supplemental check
- 19. Extract all Rules/ references using `grep -r "Rules/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/` as supplemental check
- 20. Validate each referenced file exists at specified path
- 21. Log broken references with file locations
- 22. **VALIDATION**: Validate file reference extraction completed successfully
- 23. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 24. **PRINT**: "File reference check complete - {N} broken references found"

### Phase 4. Terminology Consistency Check
- 25. **SCAN**: Read each harness architecture file line by line to check for outdated terminology
- 26. Search for outdated terminology: `grep -r "gate" /c/SovereignAI/Workflow/` (should return no results if cleanup complete, except in meta-references like this line) as supplemental check
- 27. Check for "Workflow_Template.md" location references
- 28. Check agent naming convention consistency
- 29. **VALIDATION**: Validate terminology check completed successfully
- 30. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 31. **PRINT**: "Terminology check complete - {N} terminology inconsistencies found"

### Phase 5. Workflow Structure Consistency Check
- 32. **SCAN**: Read each workflow file line by line to compare against Workflow/Workflow_Reference/Workflow_Template.md
- 33. Check for mandated sections: Workflow Header, Universal Framework References
- 34. Validate workflow follows header structure requirements (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State)
- 35. Check Universal Framework References section presence and completeness
- 36. Note any missing suggested phases (Phase 0, Phase 3, Phase 10) as informational, not as issues
- 37. Validate step numbering sequential consistency (if steps are used)
- 38. **EXECUTION MODES VALIDATION**: Validate that workflow defines its specific execution mode options in header and Phase 1 (accept workflow-specific mode definitions)
- 39. **VALIDATION**: Validate workflow structure check completed successfully
- 40. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 41. **PRINT**: "Workflow structure check complete - {N} structure issues found"

### Phase 6. Additional Consistency Checks (if full scan)
- 42. **SCAN**: Read each Rules/ file line by line to check structure and patterns
- 43. Governance Rule Consistency: Check Rules/ files structure and patterns
- 44. **SCAN**: Read INDEX.md and documentation files line by line to validate conventions
- 45. Documentation Structure: Validate INDEX.md and documentation conventions
- 46. **SCAN**: Read AGENTS.md line by line to compare with actual capabilities
- 47. Agent Capability Alignment: Compare AGENTS.md with actual capabilities
- 48. **SCAN**: Read framework files line by line to check proper separation and references with relevance requirement
- 49. Universal Framework Coverage: Check proper separation and references with relevance requirement
- 50. **SCAN**: Read workflow files line by line to validate execution patterns across agents
- 51. Execution Strategy Consistency: Validate execution patterns across agents
- 52. **SCAN**: Read workflow files line by line to check state schemas and tracking patterns
- 53. State Management Consistency: Check state schemas and tracking patterns
- 54. **SCAN**: Read configuration files line by line to validate runtime infrastructure documentation
- 55. Runtime Prerequisites: Validate runtime infrastructure documentation
- 56. **SCAN**: Read quality assessment files line by line to validate 1-5 scoring scale consistency
- 57. Scoring Scale Consistency: Validate 1-5 scoring scale consistency across quality assessments
- 58. **SCAN**: Read AGENTS.md line by line to validate behavior rules are properly defined
- 59. Agent Behavior Rules Consistency: Validate AGENTS.md behavior rules are properly defined
- 60. **SCAN**: Read each workflow file line by line to ensure Workflow/Workflow_Reference/Terminology_Glossary.md is referenced in Phase 0
- 61. Terminology Glossary Reference Consistency: Ensure all workflows reference Workflow/Workflow_Reference/Terminology_Glossary.md in Phase 0
- 62. **SCAN**: Validate Logs/ directory structure follows agent-specific organization (Logs/{Agent}/BP/{App/Harness}/)
- 63. Directory Structure Consistency: Validate Logs/ directory structure matches workflow output locations
- 64. **VALIDATION**: Validate additional checks completed successfully
- 65. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 66. **PRINT**: "Additional consistency checks complete - full scan analysis finished"

### Phase 7. Report Generation
- 67. Create Logs/Architect/Consistency Review/ directory if not exists
- 68. Generate report with timestamp: Scan_{YYYY-MM-DD_HH-MM-SS}.md
- 69. Include executive summary with overall consistency score
- 70. Document findings for each consistency variable checked
- 71. Classify issues by severity (Critical/High/Medium/Low)
- 72. Provide actionable recommendations with timeline
- 73. **VALIDATION**: Validate report generation completed successfully
- 74. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 75. **PRINT**: "Report generation complete - workflow terminated"

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
- **Architect Tool**: Workflow/Workflow_Reference/Workflow_Template.md
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
  - "gate" terminology (should be eliminated in favor of "validation", except in meta-references describing the check itself)
  - "Workflow_Template.md" location references
  - Framework naming (removed - naming issue resolved)
  - Agent naming conventions
  - Phase naming conventions

### 3. Workflow Structure Consistency
- **Check**: All workflows follow Architect template structure
- **Scope**: All workflow files in Workflow/ directory
- **Variables**:
  - Mandated sections: Workflow Header, Universal Framework References
  - Header metadata completeness (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State)
  - Universal framework coverage (relevant frameworks)
  - Execution Modes definition in header and Phase 1 (workflow-specific options accepted)
  - Suggested phases (Phase 0, Phase 3, Phase 10) - informational only
  - STATUS TRACKING entries presence (informational)
  - VALIDATION entries presence (informational)
  - PRINT commands presence (informational)
  - Step numbering sequential consistency (if steps are used)

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
- **Check**: Proper separation of universal vs agent-specific content with relevance requirement
- **Scope**: Workflow_Reference/ and agent Reference/ folders
- **Variables**:
  - Universal framework references in agent workflows (relevance requirement: only include frameworks relevant to agent purpose)
  - No agent-specific content in Workflow_Reference/
  - No universal content in agent Reference/
  - Universal Pattern Reference sections presence
  - Cross-reference patterns consistency
  - Framework reference count appropriateness (Architect: ~5, Planner: ~9, Executor: ~8 based on agent purpose)

### 8. Execution Strategy Consistency
- **Check**: Execution patterns are consistent across agents
- **Scope**: Execution mode patterns, implementation modes
- **Variables**:
  - Execution mode definitions (agent-specific options accepted)
  - Implementation mode patterns
  - Quota handling references
  - Execution strategy guidelines references
  - Cross-agent execution pattern alignment
  - Each agent has execution mode patterns in their Reference/ folder
  - Workflows reference their agent-specific Execution_Mode_Patterns.md
  - Universal patterns in Workflow/Workflow_Reference/Execution_Mode_Patterns.md provide general guidance

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

### 11. Scoring Scale Consistency
- **Check**: Quality assessment uses consistent scoring scales
- **Scope**: Quality assessment references, template scoring, workflow convergence checks
- **Variables**:
  - Quality assessment framework uses 1-5 scale consistently
  - Template scoring examples match 1-5 scale
  - Workflow convergence checks use 1-5 scale thresholds
  - No mixed scoring scales (0-100 vs 1-5)
  - Quality threshold consistency across workflows

### 12. Agent Behavior Rules Consistency
- **Check**: AGENTS.md behavior rules are properly defined and consistent
- **Scope**: AGENTS.md, agent workflows, agent rules
- **Variables**:
  - AGENTS.md contains current behavior rules (direct question answering, BP? search)
  - Behavior rules are consistent across all agents
  - Behavior rules are actionable and clear
  - Behavior rules align with actual agent behavior in workflows
  - No conflicting behavior rules

### 13. Directory Structure Consistency
- **Check**: Logs/ directory structure follows agent-specific organization patterns
- **Scope**: Logs/ directory structure across all agents
- **Variables**:
  - Logs/{Agent}/BP/{App/Harness}/ structure exists for relevant agents
  - Workflow output locations match actual directory structure
  - Timestamp formatting consistency (YYYY-MM-DD_HH-MM-SS)
  - Incremental report locations match workflow specifications
  - Directory structure supports workflow separation (App vs Harness outputs)

## Consistency Check Process

### Process Step 1: Harness Architecture Scan
1. **File Discovery**: Use `find` to enumerate all harness architecture files
2. **Comprehensive Line-by-Line Scanning**: **SCAN** each file line by line to examine all documents within scope without skipping anything - comprehensive examination required for governance compliance
3. **Pattern Matching**: Use `grep` to extract specific patterns from files as supplemental checks only
4. **Cross-Reference Analysis**: Verify all file references exist
5. **Structure Validation**: Validate workflow structure compliance
6. **Terminology Analysis**: Check for inconsistent terminology

### Process Step 2: Detailed Variable Analysis
1. **File Reference Validation**: Check each referenced file exists
2. **Workflow Structure Validation**: Compare workflows against template for mandated sections only
3. **Governance Rule Validation**: Check rule file structure consistency
4. **Documentation Validation**: Verify INDEX.md and documentation structure
5. **Framework Coverage Validation**: Check universal framework usage

### Process Step 3: Issue Aggregation
1. **Severity Classification**: Classify issues as Critical/High/Medium/Low
2. **Categorization**: Group issues by consistency variable
3. **Impact Analysis**: Assess impact on harness functionality
4. **Recommendation Generation**: Generate fix recommendations

### Process Step 4: Report Generation
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
**Scoring Scale Consistency**: {X}%
**Agent Behavior Rules Consistency**: {X}%

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

**Note**: Workflow terminates after single scan execution. Do not loop automatically.

## Scan Execution Commands

### File Discovery
```bash
find /c/SovereignAI -name "*.md" -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md"
```

### Primary Scanning Method (MANDATORY)
**CRITICAL**: All files must be read line by line using the `read` tool for comprehensive examination. This is the primary scanning method required for governance compliance.

### Supplemental Pattern Extraction (NOT PRIMARY)
```bash
grep -r "Workflow/" /c/SovereignAI/Workflow/
grep -r "Rules/" /c/SovereignAI/Workflow/
grep -r "gate" /c/SovereignAI/Workflow/ (should return no results if cleanup complete, except in meta-references)
```
**Note**: These grep commands are supplemental checks only and must not replace comprehensive line-by-line scanning.

### Cross-Reference Validation
```bash
# Extract all Workflow/ references and validate file existence
grep -rh "Workflow/[A-Za-z/]*\.md" /c/SovereignAI/Workflow/ | sort -u
```

## Consistency Scoring

**Overall Score Calculation**:
- File Reference Consistency: 18%
- Terminology Consistency: 9%
- Workflow Structure Consistency: 18%
- Governance Rule Consistency: 9%
- Documentation Structure: 9%
- Agent Capability Alignment: 9%
- Universal Framework Coverage: 9%
- Execution Strategy Consistency: 4%
- State Management Consistency: 3%
- Runtime Prerequisites: 2%
- Scoring Scale Consistency: 5%
- Agent Behavior Rules Consistency: 4%

**Score Thresholds**:
- 90-100: Excellent - No critical issues
- 80-89: Good - Minor issues only
- 70-79: Fair - Some medium issues
- 60-69: Poor - High priority issues present
- Below 60: Critical - Architectural integrity at risk