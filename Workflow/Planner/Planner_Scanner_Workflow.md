---
id: wf-plan-scanner
status: active
owner: planner-agent
updated: 2026-07-28
purpose: Create implementation-ready plans from existing governance scan results
---

# Planner Plan Creation Workflow

**ID**: WF-PLAN-SCAN-001  
**Owner**: Planner Agent  
**Frequency**: On-demand  
**Duration**: Standard (plan creation from existing scan results)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual

## Purpose
Create implementation-ready plans from existing governance scan results. This workflow accepts scan findings as input (from scanning processes performed by other agents or workflows) and structures them into planning-focused recommendations following the authoritative Plan Template format. The workflow focuses on systematically processing entire scan logs and translating findings into actionable plans (Context, Steps, Dependencies with planning language) based on AI agent planning best practices. Plan number is determined by reading Plans/PLAN_TRACKING.md to identify next available sequential plan number.

**Plan Output**: Scan findings are structured as planning-focused recommendations following Plan Template format (Context, Steps, Dependencies with planning language) for manual implementation. Plan number is determined by reading Plans/PLAN_TRACKING.md to identify next available sequential plan number.

## Scope
**Input**: Existing scan results and findings from governance scanning processes (performed by other agents or workflows) - must read entire scan log systematically

**Plan Output**: Plans/plan-{N}-Rev1.md (single plan following Plan Template format with Context, Steps, Dependencies using planning language)

## Reference Files (SSOT)
- **Plan Template**: Workflow/Planner/Templates/Plan_Template.md (authoritative format reference)
- **Plan Tracking**: Plans/PLAN_TRACKING.md (single source of truth for plan numbering and history)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality assessment criteria)
- **Convergence Loops**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md (internal review iteration patterns)
- **Plan Brief Template**: Workflow/Planner/Templates/Plan_Brief_Template.md (internal review structure)
- **Plan Prompt Template**: Workflow/Planner/Templates/Plan_Prompt_Template.md (internal panelist instructions)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (validation patterns)
- **Terminology Glossary**: Workflow/Workflow_Reference/Terminology_Glossary.md (terminology definitions)

## Roles and Owners
- **Planner Agent**: Creates implementation-ready plans from existing scan results, applies Plan Template format, validates plan structure
- **User**: Provides scan results as input, approves plan structure and content
- **Governance System**: Validation against Plan Template and planning standards

## Trigger and End State
- **Trigger**: User provides existing scan results and requests plan creation
- **End State**: Implementation-ready plan (with appropriate revision splitting) following Plan Template format for implementation planning, using next available sequential plan number from PLAN_TRACKING.md

## Workflow Steps (43 steps)

### Phase 0. Read Planner Rules + Governance
- 1. Read Rules/Planner/Planner_Rules.md to understand planning criteria and infrastructure compliance requirements
- 2. Read PRINCIPLES.md to understand constitutional framework and architectural principles
- 3. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Planner rules and infrastructure compliance criteria loaded"

### Phase 1. Accept Scan Results Input
- 1. Request user to provide existing scan results and findings from governance scanning processes
- 2. **VALIDATION**: Validate that scan results are provided and contain sufficient information for plan creation
- 3. **SYSTEMATIC SCAN PROCESSING**: Read entire scan log file systematically to extract all findings (not just partial results)
- 4. **FINDINGS AGGREGATION**: Group findings by category (e.g., Single Responsibility violations, missing ABC base classes, hardcoded values)
- 5. **PRIORITY ASSESSMENT**: Assess severity and impact of findings to determine plan structure
- 6. **STATUS TRACKING**: Update workflow status to "phase_1_complete"
- 7. **PRINT** "Scan results input received and systematically processed - proceeding with plan creation"

### Phase 2. Plan Creation from Scan Results
- 1. **PLAN NUMBER ASSIGNMENT**: Read Plans/PLAN_TRACKING.md to determine next available sequential plan number
- 2. **PLAN TEMPLATE COMPLIANCE**: Apply authoritative Plan Template format (Workflow/Planner/Templates/Plan_Template.md) to scan findings:
  - Follow Plan Template structure exactly as defined (Context, Steps, Dependencies)
  - Include all required sections per Plan Template specifications
  - Use planning language per Plan Template guidelines (design, specify, define, outline, structure)
- 3. **FINDINGS INTEGRATION**: Systematically integrate all scan findings into appropriate plan sections:
  - Group related findings by category and severity
  - Ensure each finding from scan log is addressed in plan steps
  - Maintain traceability between scan findings and plan steps
- 4. **PLAN STRUCTURE**: Create plan-{N}-Rev1.md following authoritative Plan Template format:
  - Single comprehensive plan following Plan Template structure
  - All required sections per Plan Template specifications
  - Proper planning language per Plan Template guidelines
  - ≤120 lines total when possible per Plan Template constraints
- 5. **VALIDATION**: Validate plan against Plan Template quality checks:
  - All required sections present per Plan Template (Context, Steps, Dependencies)
  - Metadata complete per Plan Template specifications (Revision, Date, Goal)
  - Steps follow planning language guidelines per Plan Template
  - Dependencies clear and executable per Plan Template
  - No circular dependencies per Plan Template
  - Plan length constraints per Plan Template (≤120 lines when possible)
- 6. Save plan to Plans/plan-{N}-Rev1.md
- 7. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 8. **PRINT** "Plan {N}-Rev1 created from scan findings - follows authoritative Plan Template format"
- **NOTE**: PLAN_TRACKING.md update (plan completion status, dependency updates) is Executor responsibility upon plan implementation completion

### Phase 3. Internal Round Table Review
- 1. **PLAN BRIEF CREATION**: Create plan brief using Workflow/Planner/Templates/Plan_Brief_Template.md for internal panelist review
- 2. **PANELIST ASSIGNMENT**: Assign domain-split personas for internal review (Structure Expert, Scope Expert, Planning Language Expert)
- 3. **PANELIST INSTRUCTIONS**: Provide panelists with persona instructions from Workflow/Planner/Templates/Plan_Prompt_Template.md
- 4. **INTERNAL QUALITY EVALUATION**: Panelists evaluate plan using Workflow/Workflow_Reference/Quality_Assessment_Framework.md with planning language compliance focus
- 5. **FINDINGS APPLICATION**: Apply panelist findings to improve plan quality through plan revisions
- 6. **CONVERGENCE LOOPS**: Internal review iteration until convergence achieved (≥4.5 score or 3.5-4.4 with rationale)
- 7. **LOOP CAPS**: Maximum 5 internal iterations before escalation to user
- 8. **INTERNAL REVIEW LOGGING**: Log internal reviews to Logs/Planner/Roundtable/Internal/plan{N}/{Agent_Persona}.md
- 9. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 10. **PRINT** "Internal Round Table review complete - plan {N} revised based on panelist feedback"

### Phase 4. Final Validation + User Review
- 1. Verify plan completeness and accuracy
- 2. Ensure all scan findings are systematically processed and reflected in plan steps
- 3. Check that recommendations are actionable and implementation-ready
- 4. Verify plan structure compliance with authoritative Plan Template format (Context, Steps, Dependencies)
- 5. **VALIDATION**: Validate that final validation completed successfully
- 6. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 7. **PRINT** "Final validation complete - plan {N} ready for user review"

### Phase 5. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 1. **PRINT** "Planner Plan Creation workflow execution complete - workflow terminated"
- 2. **PRINT** "Plan {N}-Rev1 available in Plans/ directory for implementation"
- 3. **PRINT** "Note: PLAN_TRACKING.md will be updated by Executor upon plan implementation completion"
- 4. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Planner Customization**: Planner-specific quality criteria for plan validation
- **Focus**: Plan quality assessment with planning language compliance

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Planner Customization**: Planner-specific validation patterns for plan structure verification
- **Focus**: Plan template validation and planning language verification

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Planner Customization**: Planner-specific state tracking for plan creation progress
- **Focus**: Plan creation progress tracking and validation state management

## Plan Creation Complexity Assessment

Based on scan results input:
- **Input**: Existing scan results and findings from governance scanning processes (must read entire scan log systematically)
- **Processing Strategy**: Systematic processing of entire scan log → Findings aggregation → Priority assessment → Plan Template format plan creation → Internal Round Table review → Final validation
- **Estimated Duration**: Extended (comprehensive plan creation from full scan results with internal review)
- **Token Usage**: High (systematic scan log processing, comprehensive plan creation per Plan Template, internal review iterations)
- **Coverage**: Translate all scan findings into planning-focused format per authoritative Plan Template (Context, Steps, Dependencies) with internal quality validation
- **Process**: Accept scan results → Systematically read entire scan log → Aggregate findings by category → Assess priority → Create plan following authoritative Plan Template format → Internal Round Table review (max 5 iterations) → Final validation → User review
- **Internal Review**: Domain-split personas (Structure Expert, Scope Expert, Planning Language Expert) evaluate plan quality with convergence loops (≥4.5 score or 3.5-4.4 with rationale)
- **Plan Tracking**: PLAN_TRACKING.md update (plan completion status, dependency updates) is Executor responsibility upon plan implementation completion

## Infrastructure Requirements

### Required Reference Files
- **Plan Template**: Workflow/Planner/Templates/Plan_Template.md (authoritative format reference)
- **Plan Brief Template**: Workflow/Planner/Templates/Plan_Brief_Template.md (internal review structure)
- **Plan Prompt Template**: Workflow/Planner/Templates/Plan_Prompt_Template.md (internal panelist instructions)
- **Convergence Loops**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md (internal review iteration patterns)
- **Plan Tracking**: Plans/PLAN_TRACKING.md (plan number assignment)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality criteria)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (validation patterns)
- **Terminology Glossary**: Workflow/Workflow_Reference/Terminology_Glossary.md (terminology definitions)

### Required Directory Structure
- **Plans**: Plans/ (for comprehensive plan output)
- **Tracking**: Plans/PLAN_TRACKING.md (for plan number assignment)
- **Internal Review Logs**: Logs/Planner/Roundtable/Internal/plan{N}/ (for internal review logging)

### Plan Template Compliance Requirements
- **Structure Compliance**: Plans must follow Workflow/Planner/Templates/Plan_Template.md format exactly
- **Required Sections**: Context, Steps, Dependencies per Plan Template specifications
- **Header Information**: Revision, Date, Goal per Plan Template specifications
- **Planning Language**: Steps must use planning language (design, specify, define, outline, structure) per Plan Template guidelines
- **Length Constraints**: ≤120 lines total when possible per Plan Template specifications
- **Quality Checks**: All Plan Template quality checks must pass before delivery

---

**Last Updated**: 2026-07-28
**Version**: 6.0 (Added Internal Round Table review phase for quality control, removed external review)
**Maintained By**: Architect Agent