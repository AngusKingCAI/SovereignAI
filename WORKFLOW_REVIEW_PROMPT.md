# Workflow Folder Consistency Review Prompt

**Purpose**: External reviewer prompt for comprehensive consistency evaluation of the Workflow folder structure based on defined metrics.

**Review Scope**: `Workflow/` directory and all subdirectories
**Review Focus**: Consistency across all workflow files, reference documents, and template compliance

---

## Review Instructions

Please conduct a comprehensive consistency review of the Workflow folder using the following metrics and evaluation criteria. For each metric, provide:

1. **Status**: ✅ PASS / ⚠️ WARNING / ❌ FAIL
2. **Findings**: Specific issues identified with file paths and line numbers
3. **Impact**: Assessment of impact on workflow execution (High/Medium/Low)
4. **Recommendations**: Specific actions to resolve any issues

---

## Metric 1: File References Consistency

### Evaluation Criteria
- All file references within workflow files are consistent and use correct paths
- References to templates, reference documents, and governance files are accurate
- No references to non-existent files
- Consistent naming conventions across references

### Review Checklist
- [ ] Check all workflow files for references to other files
- [ ] Verify referenced files exist at specified paths
- [ ] Check for broken links or dead references
- [ ] Ensure relative paths are used consistently
- [ ] Validate that universal framework references point to Workflow_Reference/
- [ ] Validate that agent-specific references point to correct Agent/Reference/ folders

### Key Files to Review
- `Workflow/Architect/Architect_General_Workflow.md`
- `Workflow/Planner/Planner_Plan_Workflow.md`
- `Workflow/Executor/Executor_Implementation_Cycle.md`
- `Workflow/Workflow_Template.md`
- All Reference/ files (check cross-references)

---

## Metric 2: Best Practices Compliance

### Evaluation Criteria
- Documentation organization follows industry best practices
- Clear separation between universal frameworks and agent-specific content
- Consistent naming patterns across files
- Proper documentation structure and formatting

### Review Checklist
- [ ] Verify two-layer documentation structure (Universal + Agent-Specific)
- [ ] Check that universal frameworks use consistent naming: `{Concept}_Framework.md`, `{Concept}_Patterns.md`, `{Concept}_Guidelines.md`
- [ ] Check that agent-specific documents use consistent naming: `{Agent}_{Concept}_Specifications.md`
- [ ] Ensure clear separation between universal standards (Workflow_Reference/) and agent-specific context (Agent/Reference/)
- [ ] Validate that template usage guidelines are comprehensive and actionable

### Key Best Practices to Verify
- Universal frameworks in `Workflow/Workflow_Reference/`
- Agent-specific documents in `Workflow/{Agent}/Reference/`
- No agent-specific content in universal folders
- No universal content in agent-specific folders

---

## Metric 3: Universal vs Agent-Specific Separation

### Evaluation Criteria
- Clear and logical separation between universal frameworks and agent-specific implementations
- Universal frameworks contain patterns applicable to all agents
- Agent-specific files contain only agent-customized implementations
- Cross-references properly distinguish between universal and agent-specific content

### Review Checklist
- [ ] Verify `Workflow/Workflow_Reference/` contains only universal patterns
- [ ] Verify `Workflow/{Agent}/Reference/` contains only agent-specific content
- [ ] Check that agent-specific files reference universal frameworks appropriately
- [ ] Ensure no duplicate content between universal and agent-specific files
- [ ] Validate that universal frameworks provide agent customization guidance

### Separation Patterns to Verify
- Universal: Execution_Strategy_Guidelines.md, Template_Usage_Guidelines.md, Quality_Assessment_Framework.md, etc.
- Agent-Specific: Gate definitions, convergence criteria, phase definitions
- Cross-Reference Pattern: "See universal framework for pattern, see agent-specific for implementation"

---

## Metric 4: Path Accuracy

### Evaluation Criteria
- All file paths referenced in workflow files are accurate
- Referenced files exist at specified locations
- No references to files that have been moved or deleted
- Directory structure matches all file references

### Review Checklist
- [ ] Verify all template file paths include `/Templates/` subdirectory where applicable
- [ ] Check all reference file paths point to correct `/Reference/` subdirectories
- [ ] Validate governance file paths (Rules/, AGENTS.md, INDEX.md)
- [ ] Check script directory references (Scripts/)
- [ ] Verify runtime directory references (Plans/, Logs/)

### Common Path Patterns to Check
- Templates: `Workflow/{Agent}/Templates/{Template}.md`
- References: `Workflow/{Agent}/Reference/{Document}.md`
- Universal: `Workflow/Workflow_Reference/{Document}.md`
- Governance: `Rules/{Agent}/{Agent}_Rules.md`

---

## Metric 5: No Redundancy

### Evaluation Criteria
- No duplicate content between universal and agent-specific documents
- Agent-specific files extend universal patterns rather than duplicating them
- No multiple files containing identical information
- Clear purpose for each document

### Review Checklist
- [ ] Identify any duplicate content between universal and agent-specific files
- [ ] Check for similar content that could be consolidated
- [ ] Verify that agent-specific files reference universal frameworks instead of duplicating
- [ ] Ensure each document has a unique, well-defined purpose
- [ ] Check for redundant quality metrics, role definitions, or similar content

### Redundancy Patterns to Identify
- Identical quality rubrics in multiple files
- Same role responsibilities defined in multiple places
- Duplicate gate enforcement patterns
- Repeated execution mode definitions

---

## Metric 6: Template Compliance

### Evaluation Criteria
- All workflows follow the defined template structure
- Phase numbering matches template requirements (Phase 0, Phase 3, Phase 10)
- Required template elements are present (VALIDATION, STATUS TRACKING, PRINT commands)
- Universal Framework References section is present in workflows

### Review Checklist
- [ ] Verify each workflow has Phase 0 (Read Governance)
- [ ] Verify each workflow has Phase 3 (Research/Analysis)
- [ ] Verify each workflow has Phase 10 (Return to Phase 0)
- [ ] Check for required template elements in each phase
- [ ] Verify Universal Framework References section at end of workflows
- [ ] Validate step numbering is sequential and consistent

### Template Requirements
- **Phase 0**: Load governance rules, STATUS TRACKING
- **Phase 3**: Research/analysis with web search where required
- **Phase 10**: Return to Phase 0 with PRINT statements
- **Universal Framework References**: Quality Assessment, Role Responsibilities, Quality Metrics, State Management, Execution Strategy

---

## Metric 7: Cross-References Accuracy

### Evaluation Criteria
- All cross-references use proper relative paths
- Cross-references are accurate and point to existing files
- Cross-references follow established patterns
- No circular or broken cross-references

### Review Checklist
- [ ] Verify all cross-references use correct relative path format
- [ ] Check that cross-referenced files exist
- [ ] Validate cross-reference patterns are consistent
- [ ] Ensure cross-references provide both universal and agent-specific context where applicable
- [ ] Check for missing cross-references to universal frameworks

### Cross-Reference Patterns
- Universal frameworks: `Workflow/Workflow_Reference/{Document}.md`
- Agent-specific: `Workflow/{Agent}/Reference/{Document}.md`
- Combined: "See universal framework for pattern, see agent-specific for implementation"

---

## Expected Review Structure

### 1. Executive Summary
- Overall consistency assessment
- Total issues found by severity (High/Medium/Low)
- Critical issues requiring immediate attention

### 2. Detailed Findings by Metric
For each of the 7 metrics above, provide:
- Status (PASS/WARNING/FAIL)
- Specific findings with file paths and line numbers
- Impact assessment
- Recommended actions

### 3. Critical Issues Summary
- List all High-impact issues
- Priority order for resolution
- Dependencies between issues

### 4. Positive Findings
- Areas where consistency is exemplary
- Best practices implemented well
- Patterns that should be maintained

### 5. Recommendations
- Short-term actions (immediate fixes)
- Medium-term improvements (structural changes)
- Long-term enhancements (process improvements)

---

## Review Deliverables

Please provide your review in the following format:

```markdown
# Workflow Folder Consistency Review Report

**Reviewer**: [Your Name]
**Review Date**: [Date]
**Review Scope**: Workflow/ directory
**Review Focus**: Consistency across all workflow files

## Executive Summary
[Overall assessment summary]

## Metric 1: File References Consistency
[Detailed findings for Metric 1]

## Metric 2: Best Practices Compliance
[Detailed findings for Metric 2]

[Continue for all 7 metrics]

## Critical Issues Summary
[Prioritized list of critical issues]

## Positive Findings
[Areas of excellence]

## Recommendations
[Short-term, medium-term, long-term recommendations]
```

---

## Review Timeline

- **Expected Duration**: 2-4 hours for comprehensive review
- **Priority Focus**: Start with Metrics 1 (File References) and 4 (Path Accuracy) as these have highest impact
- **Secondary Focus**: Metrics 3 (Separation) and 6 (Template Compliance) for structural integrity
- **Tertiary Focus**: Metrics 2, 5, 7 for refinement and optimization

---

## Contact Information

If you have questions about review criteria or need clarification on specific metrics, please refer to:
- `Workflow/Workflow_Template.md` for template requirements
- `Workflow/Workflow_Reference/Template_Usage_Guidelines.md` for customization guidelines
- `AGENTS.md` for overall governance context

---

**Review Note**: This review focuses specifically on consistency metrics. For functional correctness or workflow logic evaluation, please use the appropriate functional review prompt.