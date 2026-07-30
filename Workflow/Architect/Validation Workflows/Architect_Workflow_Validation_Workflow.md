---
id: wf-arch-workflow-validation
status: active
owner: architect-agent
updated: 2026-07-30
version: "2.3"
purpose: Architect workflow for comprehensive consistency validation of workflow documents with KISS principles and systematic template validation
expected_agent_type: architect-agent
persona:
  role: "Validation Architect"
  expertise: "Document validation, consistency checking, best practice alignment, governance compliance, interactive fix guidance, KISS principle validation, template integrity validation, SSOT compliance enforcement, reference document integrity validation, workflow execution simulation and dry-run validation"
  process: "Interactive phase-by-phase validation with stop-and-fix approach, web search integration, SSOT compliance, early-exit patterns, systematic template validation, comprehensive cross-reference validation, and workflow execution simulation for dry-run validation"
  output: "Real-time inconsistency identification with specific fix suggestions, immediate user collaboration, and comprehensive quality gate enforcement"
  constraints: "Interactive validation-only scope, no direct modifications without user approval, SSOT compliance enforcement, KISS principle adherence, early-exit on critical errors"
---

# Architect Workflow Validation Workflow

**ID**: WF-ARCH-WORKFLOW-VALIDATION  
**Owner**: Architect Agent  
**Frequency**: Per workflow validation task  
**Duration**: Variable (workflow-dependent)  
**Priority**: High
**Workflow Type**: Single-Execution (systematic validation process)
**Execution Modes**: Manual, Automatic
**Phase Structure**: 22 modular phases (Phase 0-21) following KISS principles with comprehensive quality gates - including workflow execution simulation, KISS compliance, systematic template validation, comprehensive cross-reference validation, SSOT compliance checks, early-exit patterns, reference document integrity validation, and template integrity validation

## Purpose
Comprehensive workflow validation for Architect agents to ensure all workflow documents meet consistency standards, align with industry best practices, maintain SSOT compliance, and follow KISS principles. This workflow implements 22 modular validation phases (Phase 0-21) including workflow discovery and selection, workflow execution simulation, KISS compliance, systematic template validation, comprehensive cross-reference validation, SSOT compliance checks, early-exit patterns, reference document integrity validation, and template integrity validation. This workflow stops at each inconsistency found, suggests immediate fixes to the user, and awaits approval before proceeding. This is an interactive validation process, not a batch report generator.

## Reference Documents
- **Best Practice Integration**: Web search points (BP?) for current industry standards
- **Fact Check Integration**: Fact checking points (FC?) for factual accuracy verification
- **Validation Patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns)
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)
- **SSOT Principles**: PRINCIPLES.md architectural principles (CA-1 through CA-11)

## Roles and Owners
- **Architect Agent**: Executes consistency scan workflow, applies Validation Architect persona
- **Validation Architect Persona**: Session-scoped persona for workflow validation tasks
- **Governance System**: Validation-based compliance enforcement

## Trigger and End State
- **Trigger**: User requests workflow validation or Architect initiates systematic workflow review
- **End State**: Workflow validated with all inconsistencies fixed interactively during validation process

## Workflow Steps (22 phases: Phase 0-21)

### Phase 0. Persona Validation and Workflow Initialization
- 0.1. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 0.2. **VALIDATE PERSONA**: Verify expected_agent_type matches current agent (architect-agent)
- 0.3. **LOAD PERSONA**: Load Validation Architect persona from workflow YAML frontmatter
- 0.4. **VALIDATE PERSONA STRUCTURE**: Ensure persona contains all required elements (role, expertise, process, output, constraints)
- 0.5. **PRINT**: "Validation Architect persona loaded - ready for systematic workflow validation"
- 0.6. **VALIDATION**: Validate that persona loading completed successfully before proceeding to Phase 1
- 0.7. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Workflow Discovery and Selection
**Best Practice**: Comprehensive workflow discovery - ensure all available workflows are identified and user can select target workflow

- 1.1. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 1.2. **ACTION**: Scan entire Workflow/ directory for all workflow files
- 1.3. **ACTION**: Use file discovery to find all files matching pattern "*_Workflow.md"
- 1.4. **ACTION**: Build comprehensive list of all available workflows with full paths
- 1.5. **ACTION**: Organize workflows by agent/category (Architect, Planner, Executor, etc.)
- 1.6. **ACTION**: Display numbered list of all discovered workflows to user
- 1.7. **ASK USER**: "Which workflow would you like to validate? Please select from the numbered list above."
- 1.8. **AWAIT USER SELECTION**: Wait for user to specify workflow number or path
- 1.9. **ACTION**: Store selected workflow path for validation phases
- 1.10. **PRINT**: "Workflow selected for validation: [workflow path]"
- 1.11. **STATUS TRACKING**: Update workflow status to "phase_1_complete"

### Phase 2. Workflow Execution Simulation
**Best Practice**: Early executability validation - ensure workflow can execute before structural validation investment

- 2.1. **STATUS TRACKING**: Update workflow status to "phase_2_in_progress"
- 2.2. **ACTION**: BP? - "workflow execution simulation and dry-run validation best practices"
- 2.3. **ACTION**: FC? - "workflow execution path accuracy and factual correctness verification"
- 2.4. **ACTION**: Begin simulation starting at target workflow Phase 0
- 2.5. **ACTION**: Simulate each step of target workflow sequentially
- 2.6. **ACTION**: When workflow says to READ file: simulate READ operation, verify file exists and is accessible
- 2.7. **ACTION**: When workflow says to follow reference: simulate reference resolution, verify referenced file/document exists
- 2.8. **ACTION**: When workflow says to EXECUTE command: simulate command execution (do not actually run), verify command syntax and paths
- 2.9. **ACTION**: When workflow says to CREATE file: simulate file creation (do not actually create), verify target path is valid
- 2.10. **ACTION**: When workflow says to DELETE file: simulate file deletion (do not actually delete), verify file exists
- 2.11. **ACTION**: When workflow says to invoke skill/tool: simulate invocation, verify skill/tool exists and is accessible
- 2.12. **ACTION**: When workflow says to update session state: execute session state update command, verify session_state.py script works correctly and state file is updated
- 2.13. **CHECK**: All READ operations reference existing files
- 2.14. **CHECK**: All reference resolutions succeed (referenced files/documents exist)
- 2.15. **CHECK**: All command operations have valid syntax and accessible paths
- 2.16. **CHECK**: All file creation operations have valid target paths
- 2.17. **CHECK**: All file deletion operations reference existing files
- 2.18. **CHECK**: All skill/tool invocations reference accessible skills/tools
- 2.19. **CHECK**: All session state updates execute successfully and update both agent and workflow_state fields correctly
- 2.20. **CHECK**: Workflow execution path is logically consistent
- 2.21. **CHECK**: No circular dependencies or dead-end paths in execution
- 2.22. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific step, expected file/operation, and suggested fix
- 2.23. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 2.24. **VALIDATION**: Validate that workflow execution simulation completed successfully
- 2.25. **PRINT**: "Workflow execution simulation complete - workflow is executable"
- 2.26. **STATUS TRACKING**: Update workflow status to "phase_2_complete"

### Phase 3. Document Header Analysis
**Best Practice**: Document control standards - verify metadata accuracy and version control

- 3.1. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- 3.2. **ACTION**: BP? - "workflow document structure and metadata best practices"
- 3.3. **ACTION**: FC? - "document header metadata accuracy and factual correctness verification"
- 3.4. **ACTION**: Read selected workflow YAML frontmatter
- 3.5. **CHECK**: Document type (workflow vs template) is identified
- 3.6. **CHECK**: If template: expected_agent_type and persona fields should specify they are required for created workflows, not for the template itself
- 3.7. **CHECK**: If workflow: expected_agent_type field is present and valid
- 3.8. **CHECK**: If workflow: persona field is present and contains required elements
- 3.9. **CHECK**: Version number consistency with changes made (for workflows)
- 3.10. **CHECK**: Workflow type matches actual implementation
- 3.11. **CHECK**: Phase/step structure count matches actual implementation
- 3.12. **CHECK**: Status field is accurate
- 3.13. **CHECK**: Owner information is current
- 3.14. **CHECK**: Last updated date is accurate
- 3.15. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 3.16. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 3.17. **VALIDATION**: Validate that header analysis completed successfully
- 3.18. **STATUS TRACKING**: Update workflow status to "phase_3_complete"

### Phase 4. Purpose Section Analysis
**Best Practice**: Process documentation standards - ensure purpose is clear and accurate

- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4_in_progress"
- 4.2. **ACTION**: BP? - "workflow purpose documentation and description best practices"
- 4.3. **ACTION**: FC? - "purpose description accuracy and factual correctness verification"
- 4.4. **ACTION**: Read Purpose section
- 4.5. **CHECK**: Purpose description matches actual workflow behavior
- 4.6. **CHECK**: Scope boundaries are clearly defined
- 4.7. **CHECK**: Mode/type descriptions are accurate (if applicable)
- 4.8. **CHECK**: Purpose aligns with documented trigger conditions
- 4.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 4.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 4.11. **VALIDATION**: Validate that purpose analysis completed successfully
- 4.12. **STATUS TRACKING**: Update workflow status to "phase_4_complete"

### Phase 5. Reference Documents Section Analysis
**Best Practice**: Cross-reference validation - verify all references exist and are accurate

- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5_in_progress"
- 5.2. **ACTION**: BP? - "reference document management and documentation control standards"
- 5.3. **ACTION**: FC? - "reference document accuracy and factual correctness verification"
- 5.4. **ACTION**: Read Reference Documents section (if present)
- 5.5. **CHECK**: All listed reference documents exist
- 5.6. **CHECK**: Reference descriptions are accurate
- 5.7. **ACTION**: Read each reference document to verify it contains relevant content
- 5.8. **CHECK**: Reference document content aligns with workflow usage
- 5.9. **CHECK**: Reference document versions are compatible
- 5.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 5.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 5.12. **VALIDATION**: Validate that reference document analysis completed successfully
- 5.13. **STATUS TRACKING**: Update workflow status to "phase_5_complete"

### Phase 6. Roles and Owners Section Analysis
**Best Practice**: Documentation control standards - verify ownership and accountability

- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress"
- 6.2. **ACTION**: BP? - "workflow role definition and ownership best practices"
- 6.3. **ACTION**: FC? - "role assignment accuracy and factual correctness verification"
- 6.4. **ACTION**: Read Roles and Owners section (if present)
- 6.5. **CHECK**: Role descriptions match actual workflow responsibilities
- 6.6. **CHECK**: Owner assignments are current and accurate
- 6.7. **CHECK**: Role boundaries are clearly defined
- 6.8. **CHECK**: Accountability structures are clear
- 6.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 6.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 6.11. **VALIDATION**: Validate that roles and owners analysis completed successfully
- 6.12. **STATUS TRACKING**: Update workflow status to "phase_6_complete"

### Phase 7. Trigger and End State Section Analysis
**Best Practice**: Process coherence - ensure entry and exit conditions are consistent

- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7_in_progress"
- 7.2. **ACTION**: BP? - "workflow trigger and end state definition best practices"
- 7.3. **ACTION**: FC? - "trigger and end state accuracy and factual correctness verification"
- 7.4. **ACTION**: Read Trigger and End State section (if present)
- 7.5. **CHECK**: Trigger conditions match workflow entry points
- 7.6. **CHECK**: End states match actual workflow termination conditions
- 7.7. **CHECK**: Mode-specific end states match workflow behavior (if applicable)
- 7.8. **CHECK**: Trigger conditions are logically complete
- 7.9. **CHECK**: End state conditions cover all possible execution paths
- 7.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 7.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 7.12. **VALIDATION**: Validate that trigger and end state analysis completed successfully
- 7.13. **STATUS TRACKING**: Update workflow status to "phase_7_complete"

### Phase 8. KISS/Minimal Complexity Validation
**Best Practice**: Minimal viable validation - ensure workflow follows KISS principles

- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8_in_progress"
- 8.2. **ACTION**: BP? - "KISS principle document validation workflow minimal complexity"
- 8.3. **ACTION**: FC? - "workflow complexity and simplicity accuracy verification"
- 8.4. **CHECK**: Workflow avoids redundant validation layers
- 8.5. **CHECK**: Workflow uses deterministic rule-based validation (not AI reasoning)
- 8.6. **CHECK**: Workflow structure is linear without unnecessary branching
- 8.7. **CHECK**: Workflow implements early-exit on critical errors
- 8.8. **CHECK**: Workflow eliminates duplicate validation steps
- 8.9. **CHECK**: Workflow phases are essential (no bloat)
- 8.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 8.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 8.12. **VALIDATION**: Validate that KISS compliance validation completed successfully
- 8.13. **STATUS TRACKING**: Update workflow status to "phase_8_complete"

### Phase 9. Template Integrity Validation
**Best Practice**: Template integrity - ensure workflow follows template structure without markers

- 9.1. **STATUS TRACKING**: Update workflow status to "phase_9_in_progress"
- 9.2. **ACTION**: BP? - "template compliance and marker removal best practices"
- 9.3. **ACTION**: FC? - "template structure accuracy and factual correctness verification"
- 9.4. **ACTION**: Compare workflow structure against template
- 9.5. **CHECK**: Workflow follows template structure (mandatory sections included)
- 9.6. **CHECK**: No [**MANDATED**] or [**SUGGESTED**] markers remain in workflow
- 9.7. **CHECK**: Workflow uses proper phase structure (numbered phases with steps)
- 9.8. **CHECK**: Workflow includes Load Governance Rules (mandated)
- 9.9. **CHECK**: Workflow includes Select Execution Mode (mandated)
- 9.10. **CHECK**: Workflow includes appropriate suggested sections based on workflow needs
- 9.11. **CHECK**: Section content aligns with template requirements
- 9.12. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 9.13. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 9.14. **VALIDATION**: Validate that template integrity validation completed successfully
- 9.15. **STATUS TRACKING**: Update workflow status to "phase_9_complete"

### Phase 10. Schema Compliance Validation
**Best Practice**: Schema validation - ensure workflow complies with JSON schema

- 10.1. **STATUS TRACKING**: Update workflow status to "phase_10_in_progress"
- 10.2. **ACTION**: Run workflow validation script against selected workflow
- 10.3. **ACTION**: python Scripts/Schema/validate_schemas.py <workflow-file>
- 10.4. **CHECK**: Schema validation passes
- 10.5. **CHECK**: All required fields present
- 10.6. **CHECK**: Field formats are correct
- 10.7. **IF VALIDATION FAILS**: STOP - Report validation errors with specific fixes needed
- 10.8. **AWAIT USER APPROVAL**: Wait for user to approve fixes before proceeding
- 10.9. **VALIDATION**: Validate that schema compliance validation completed successfully
- 10.10. **STATUS TRACKING**: Update workflow status to "phase_10_complete"

### Phase 11. Cross-Reference Validation
**Best Practice**: Reference integrity - ensure all referenced documents exist and are accurate

- 11.1. **STATUS TRACKING**: Update workflow status to "phase_11_in_progress"
- 11.2. **ACTION**: BP? - "cross-reference validation best practices"
- 11.3. **ACTION**: FC? - "cross-reference accuracy and factual correctness verification"
- 11.4. **ACTION**: Extract all references from workflow
- 11.5. **ACTION**: Validate each reference systematically
- 11.6. **CHECK**: All referenced documents exist and are accessible
- 11.7. **CHECK**: Reference document content aligns with workflow usage
- 11.8. **CHECK**: Reference document versions are compatible
- 11.9. **CHECK**: Cross-references to other files are accurate
- 11.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 11.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 11.12. **VALIDATION**: Validate that cross-reference validation completed successfully
- 11.13. **STATUS TRACKING**: Update workflow status to "phase_11_complete"

### Phase 12. Terminology Consistency Validation
**Best Practice**: SSOT compliance - ensure all CAPITALIZED terms reference SSOT

- 12.1. **STATUS TRACKING**: Update workflow status to "phase_12_in_progress"
- 12.2. **ACTION**: BP? - "terminology consistency and SSOT compliance best practices"
- 12.3. **ACTION**: FC? - "terminology accuracy and factual correctness verification"
- 12.4. **ACTION**: Extract all CAPITALIZED terms from workflow
- 12.5. **ACTION**: Reference Workflow/Workflow_Reference/Terminology_Glossary.md
- 12.6. **CHECK**: All CAPITALIZED terms are defined in Terminology_Glossary.md
- 12.7. **CHECK**: Terminology usage is consistent across workflow
- 12.8. **CHECK**: No undefined CAPITALIZED terms
- 12.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 12.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 12.11. **VALIDATION**: Validate that terminology consistency validation completed successfully
- 12.12. **STATUS TRACKING**: Update workflow status to "phase_12_complete"

### Phase 13. Atemporal Language Validation
**Best Practice**: Timeless documentation - ensure no temporal references

- 13.1. **STATUS TRACKING**: Update workflow status to "phase_13_in_progress"
- 13.2. **ACTION**: BP? - "atemporal language documentation best practices"
- 13.3. **ACTION**: FC? - "atemporal language accuracy and factual correctness verification"
- 13.4. **ACTION**: Scan workflow for temporal references (dates, "currently", "now", etc.)
- 13.5. **CHECK**: No temporal references in header
- 13.6. **CHECK**: No temporal references in purpose section
- 13.7. **CHECK**: No temporal references in workflow steps
- 13.8. **CHECK**: Language remains atemporal and timeless
- 13.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 13.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 13.11. **VALIDATION**: Validate that atemporal language validation completed successfully
- 13.12. **STATUS TRACKING**: Update workflow status to "phase_13_complete"

### Phase 14. SSOT Compliance Validation
**Best Practice**: Single source of truth - ensure no contradictions

- 14.1. **STATUS TRACKING**: Update workflow status to "phase_14_in_progress"
- 14.2. **ACTION**: BP? - "SSOT compliance and consistency best practices"
- 14.3. **ACTION**: FC? - "SSOT compliance accuracy and factual correctness verification"
- 14.4. **ACTION**: Cross-reference with PRINCIPLES.md
- 14.5. **CHECK**: No contradictions with PRINCIPLES.md
- 14.6. **CHECK**: No multiple conflicting sources of truth
- 14.7. **CHECK**: Terminology references SSOT (Terminology_Glossary.md)
- 14.8. **CHECK**: Workflow principles align with architectural principles
- 14.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 14.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 14.11. **VALIDATION**: Validate that SSOT compliance validation completed successfully
- 14.12. **STATUS TRACKING**: Update workflow status to "phase_14_complete"

### Phase 15. Best Practice Alignment Validation
**Best Practice**: Industry standards - ensure workflow follows best practices

- 15.1. **STATUS TRACKING**: Update workflow status to "phase_15_in_progress"
- 15.2. **ACTION**: BP? - "workflow design and structure best practices"
- 15.3. **ACTION**: FC? - "best practice alignment accuracy and factual correctness verification"
- 15.4. **ACTION**: Web search for current workflow design best practices
- 15.5. **CHECK**: Workflow follows industry best practices for workflow design
- 15.6. **CHECK**: Template structure follows workflow template best practices
- 15.7. **CHECK**: Validation approach follows systematic validation best practices
- 15.8. **CHECK**: No anti-patterns detected
- 15.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 15.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 15.11. **VALIDATION**: Validate that best practice alignment validation completed successfully
- 15.12. **STATUS TRACKING**: Update workflow status to "phase_15_complete"

### Phase 16. Reference Document Integrity Validation
**Best Practice**: Reference integrity - ensure all referenced documents are valid

- 16.1. **STATUS TRACKING**: Update workflow status to "phase_16_in_progress"
- 16.2. **ACTION**: BP? - "reference document integrity best practices"
- 16.3. **ACTION**: FC? - "reference document integrity accuracy and factual correctness verification"
- 16.4. **ACTION**: Validate all referenced documents
- 16.5. **CHECK**: All referenced documents are accessible
- 16.6. **CHECK**: Reference document integrity maintained
- 16.7. **CHECK**: No broken references or missing documents
- 16.8. **CHECK**: Reference paths are relative and consistent
- 16.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 16.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 16.11. **VALIDATION**: Validate that reference document integrity validation completed successfully
- 16.12. **STATUS TRACKING**: Update workflow status to "phase_16_complete"

### Phase 17. Final Consistency Validation
**Best Practice**: Final consistency check - ensure all validation phases completed successfully

- 17.1. **STATUS TRACKING**: Update workflow status to "phase_17_in_progress"
- 17.2. **ACTION**: BP? - "document consistency validation best practices"
- 17.3. **ACTION**: FC? - "document consistency accuracy and factual correctness verification"
- 17.4. **ACTION**: Cross-reference with Workflow/Workflow_Reference/Terminology_Glossary.md
- 17.5. **ACTION**: Final consistency check across all validation phases
- 17.6. **CHECK**: All validation phases completed successfully
- 17.7. **CHECK**: No inconsistencies remain unresolved
- 17.8. **CHECK**: Workflow meets all validation criteria
- 17.9. **CHECK**: Workflow validation process completed successfully
- 17.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 17.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 17.12. **VALIDATION**: Validate that final consistency validation completed successfully
- 17.13. **STATUS TRACKING**: Update workflow status to "phase_17_complete"

### Phase 18. Quality Gate Validation
**Best Practice**: Quality gate enforcement - ensure workflow meets quality standards

- 18.1. **STATUS TRACKING**: Update workflow status to "phase_18_in_progress"
- 18.2. **ACTION**: BP? - "quality gate enforcement best practices"
- 18.3. **ACTION**: FC? - "quality gate accuracy and factual correctness verification"
- 18.4. **ACTION**: Execute quality gate checks across all validation phases
- 18.5. **CHECK**: All quality gates passed
- 18.6. **CHECK**: No critical issues found
- 18.7. **CHECK**: No blockers identified
- 18.8. **CHECK**: Workflow ready for production use
- 18.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 18.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 18.11. **VALIDATION**: Validate that quality gate validation completed successfully
- 18.12. **STATUS TRACKING**: Update workflow status to "phase_18_complete"

### Phase 19. Early-Exit Pattern Validation
**Best Practice**: Early-exit validation - ensure workflow stops appropriately on errors

- 19.1. **STATUS TRACKING**: Update workflow status to "phase_19_in_progress"
- 19.2. **ACTION**: BP? - "early-exit pattern validation best practices"
- 19.3. **ACTION**: FC? - "early-exit pattern accuracy and factual correctness verification"
- 19.4. **ACTION**: Validate early-exit conditions throughout workflow
- 19.5. **CHECK**: Workflow implements early-exit on critical errors
- 19.6. **CHECK**: Early-exit conditions clearly defined
- 19.7. **CHECK**: Early-exit doesn't compromise validation quality
- 19.8. **CHECK**: User approval process intact
- 19.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 19.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 19.11. **VALIDATION**: Validate that early-exit pattern validation completed successfully
- 19.12. **STATUS TRACKING**: Update workflow status to "phase_19_complete"

### Phase 20. User Communication Validation
**Best Practice**: User interaction - ensure clear communication throughout validation

- 20.1. **STATUS TRACKING**: Update workflow status to "phase_20_in_progress"
- 20.2. **ACTION**: BP? - "user communication and interaction best practices"
- 20.3. **ACTION**: FC? - "user communication accuracy and factual correctness verification"
- 20.4. **ACTION**: Validate user communication patterns throughout workflow
- 20.5. **CHECK**: User selections are clearly presented
- 20.6. **CHECK**: User approval points are appropriate
- 20.7. **CHECK**: Error messages are clear and actionable
- 20.8. **CHECK**: Status updates are informative
- 20.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 20.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 20.11. **VALIDATION**: Validate that user communication validation completed successfully
- 20.12. **STATUS TRACKING**: Update workflow status to "phase_20_complete"

### Phase 21. Final Validation Summary
**Best Practice**: Final summary - provide comprehensive validation results

- 21.1. **STATUS TRACKING**: Update workflow status to "phase_21_in_progress"
- 21.2. **ACTION**: Compile comprehensive validation summary
- 21.3. **ACTION**: **PRINT**: "=== WORKFLOW VALIDATION SUMMARY ==="
- 21.4. **ACTION**: **PRINT**: "Workflow: [selected workflow path]"
- 21.5. **ACTION**: **PRINT**: "Validation Date: [current date]"
- 21.6. **ACTION**: **PRINT**: "Total Phases: 22 (Phase 0-21)"
- 21.7. **ACTION**: **PRINT**: "Phases Passed: [count]"
- 21.8. **ACTION**: **PRINT**: "Phases Failed: [count]"
- 21.9. **ACTION**: **PRINT**: "Workflow Execution Simulation: [PASSED/FAILED]"
- 21.10. **ACTION**: **PRINT**: "Schema Compliance: [PASSED/FAILED]"
- 21.11. **ACTION**: **PRINT**: "Template Compliance: [PASSED/FAILED]"
- 21.12. **ACTION**: **PRINT**: "KISS Principles: [PASSED/FAILED]"
- 21.13. **ACTION**: **PRINT**: "SSOT Compliance: [PASSED/FAILED]"
- 21.14. **ACTION**: **PRINT**: "Reference Integrity: [PASSED/FAILED]"
- 21.15. **ACTION**: **PRINT**: "Best Practice Alignment: [PASSED/FAILED]"
- 21.16. **ACTION**: **PRINT**: "Terminology Consistency: [PASSED/FAILED]"
- 21.17. **ACTION**: **PRINT**: "Atemporal Language: [PASSED/FAILED]"
- 21.18. **ACTION**: **PRINT**: "=========================="
- 21.19. **CHECK**: All validation summary data is accurate
- 21.20. **VALIDATION**: Validate that final validation summary completed successfully
- 21.21. **STATUS TRACKING**: Update workflow status to "phase_21_complete"
- 21.22. **PRINT**: "Workflow validation complete - summary provided above"

### Workflow Termination (Single-Execution)
- **PRINT** "Workflow execution complete - workflow validation terminated"
- **PRINT** "Architect agent ready - awaiting next user request"
- **TERMINATE**: End workflow execution (do not return to Phase 0)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Agent Customization**: Workflow validation quality criteria within universal framework
- **Usage**: Reference universal framework for consistency

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Agent Customization**: Workflow validation enforcement patterns
- **Usage**: Reference universal framework for consistency

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Agent Customization**: Workflow validation template customization
- **Usage**: Reference universal framework for consistency