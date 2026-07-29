---
id: wf-arch-workflow-validation
status: active
owner: architect-agent
updated: 2026-07-29
version: 2.0
purpose: Architect workflow for comprehensive consistency validation of workflow documents with KISS principles and systematic template validation
expected_agent_type: architect-agent
persona:
  role: "Validation Architect"
  expertise: "Document validation, consistency checking, best practice alignment, governance compliance, interactive fix guidance, KISS principle validation, template integrity validation, SSOT compliance enforcement, reference document integrity validation"
  process: "Interactive phase-by-phase validation with stop-and-fix approach, web search integration, SSOT compliance, early-exit patterns, systematic template validation, and comprehensive cross-reference validation"
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
**Phase Structure**: 20 modular phases (Phase 0-19) following KISS principles with comprehensive quality gates - including KISS compliance, systematic template validation, comprehensive cross-reference validation, SSOT compliance checks, early-exit patterns, reference document integrity validation, and template integrity validation

## Purpose
Comprehensive workflow validation for Architect agents to ensure all workflow documents meet consistency standards, align with industry best practices, maintain SSOT compliance, and follow KISS principles. This workflow implements 20 modular validation phases (Phase 0-19) including KISS compliance, systematic template validation, comprehensive cross-reference validation, SSOT compliance checks, early-exit patterns, reference document integrity validation, and template integrity validation. This workflow stops at each inconsistency found, suggests immediate fixes to the user, and awaits approval before proceeding. This is an interactive validation process, not a batch report generator.

## Reference Documents
- **Best Practice Integration**: Web search points (BP?) for current industry standards
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

## Workflow Steps (20 phases: Phase 0-19)

### Phase 0. Persona Validation and Workflow Initialization
- 0.1. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 0.2. **VALIDATE PERSONA**: Verify expected_agent_type matches current agent (architect-agent)
- 0.3. **LOAD PERSONA**: Load Validation Architect persona from workflow YAML frontmatter
- 0.4. **VALIDATE PERSONA STRUCTURE**: Ensure persona contains all required elements (role, expertise, process, output, constraints)
- 0.5. **PRINT**: "Validation Architect persona loaded - ready for systematic workflow validation"
- 0.6. **VALIDATION**: Validate that persona loading completed successfully before proceeding to Phase 1
- 0.7. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Document Header Analysis
**Best Practice**: Document control standards - verify metadata accuracy and version control

- 1.1. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 1.2. **ACTION**: BP? - "workflow document structure and metadata best practices"
- 1.3. **ACTION**: Read workflow YAML frontmatter
- 1.4. **CHECK**: Document type (workflow vs template) is identified
- 1.5. **CHECK**: If template: expected_agent_type and persona fields should specify they are required for created workflows, not for the template itself
- 1.6. **CHECK**: If workflow: expected_agent_type field is present and valid
- 1.7. **CHECK**: If workflow: persona field is present and contains required elements
- 1.8. **CHECK**: Version number consistency with changes made (for workflows)
- 1.9. **CHECK**: Workflow type matches actual implementation
- 1.10. **CHECK**: Phase/step structure count matches actual implementation
- 1.11. **CHECK**: Status field is accurate
- 1.12. **CHECK**: Owner information is current
- 1.13. **CHECK**: Last updated date is accurate
- 1.14. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 1.15. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 1.16. **VALIDATION**: Validate that header analysis completed successfully
- 1.17. **STATUS TRACKING**: Update workflow status to "phase_1_complete"

### Phase 2. Purpose Section Analysis
**Best Practice**: Process documentation standards - ensure purpose is clear and accurate

- 2.1. **STATUS TRACKING**: Update workflow status to "phase_2_in_progress"
- 2.2. **ACTION**: Read Purpose section
- 2.3. **CHECK**: Purpose description matches actual workflow behavior
- 2.4. **CHECK**: Scope boundaries are clearly defined
- 2.5. **CHECK**: Mode/type descriptions are accurate (if applicable)
- 2.6. **CHECK**: Purpose aligns with documented trigger conditions
- 2.7. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 2.8. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 2.9. **VALIDATION**: Validate that purpose analysis completed successfully
- 2.10. **STATUS TRACKING**: Update workflow status to "phase_2_complete"

### Phase 3. Reference Documents Section Analysis
**Best Practice**: Cross-reference validation - verify all references exist and are accurate

- 3.1. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- 3.2. **ACTION**: BP? - "reference document management and documentation control standards"
- 3.3. **ACTION**: Read Reference Documents section (if present)
- 3.4. **CHECK**: All listed reference documents exist
- 3.5. **CHECK**: Reference descriptions are accurate
- 3.6. **ACTION**: Read each reference document to verify it contains relevant content
- 3.7. **CHECK**: Reference document content aligns with workflow usage
- 3.8. **CHECK**: Reference document versions are compatible
- 3.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 3.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 3.11. **VALIDATION**: Validate that reference document analysis completed successfully
- 3.12. **STATUS TRACKING**: Update workflow status to "phase_3_complete"

### Phase 4. Roles and Owners Section Analysis
**Best Practice**: Documentation control standards - verify ownership and accountability

- 4.1. **STATUS TRACKING**: Update workflow status to "phase_4_in_progress"
- 4.2. **ACTION**: Read Roles and Owners section (if present)
- 4.3. **CHECK**: Role descriptions match actual workflow responsibilities
- 4.4. **CHECK**: Owner assignments are current and accurate
- 4.5. **CHECK**: Role boundaries are clearly defined
- 4.6. **CHECK**: Accountability structures are clear
- 4.7. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 4.8. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 4.9. **VALIDATION**: Validate that roles and owners analysis completed successfully
- 4.10. **STATUS TRACKING**: Update workflow status to "phase_4_complete"

### Phase 5. Trigger and End State Section Analysis
**Best Practice**: Process coherence - ensure entry and exit conditions are consistent

- 5.1. **STATUS TRACKING**: Update workflow status to "phase_5_in_progress"
- 5.2. **ACTION**: Read Trigger and End State section (if present)
- 5.3. **CHECK**: Trigger conditions match workflow entry points
- 5.4. **CHECK**: End states match actual workflow termination conditions
- 5.5. **CHECK**: Mode-specific end states match workflow behavior (if applicable)
- 5.6. **CHECK**: Trigger conditions are logically complete
- 5.7. **CHECK**: End state conditions cover all possible execution paths
- 5.8. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 5.9. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 5.10. **VALIDATION**: Validate that trigger and end state analysis completed successfully
- 5.11. **STATUS TRACKING**: Update workflow status to "phase_5_complete"

### Phase 6. KISS/Minimal Complexity Validation
**Best Practice**: Minimal viable validation - ensure workflow follows KISS principles

- 6.1. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress"
- 6.2. **ACTION**: BP? - "KISS principle document validation workflow minimal complexity"
- 6.3. **CHECK**: Workflow avoids redundant validation layers
- 6.4. **CHECK**: Workflow uses deterministic rule-based validation (not AI reasoning)
- 6.5. **CHECK**: Workflow structure is linear without unnecessary branching
- 6.6. **CHECK**: Workflow implements early-exit on critical errors
- 6.7. **CHECK**: Workflow eliminates duplicate validation steps
- 6.8. **CHECK**: Workflow phases are essential (no bloat)
- 6.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 6.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 6.11. **VALIDATION**: Validate that KISS compliance validation completed successfully
- 6.12. **STATUS TRACKING**: Update workflow status to "phase_6_complete"

### Phase 7. Systematic Template Validation
**Best Practice**: Template integrity - ensure all referenced templates are valid and SSOT-compliant

- 7.1. **STATUS TRACKING**: Update workflow status to "phase_7_in_progress"
- 7.2. **ACTION**: BP? - "template validation best practices minimal checks"
- 7.3. **ACTION**: Identify all template references in workflow
- 7.4. **ACTION**: Read each referenced template file
- 7.5. **CHECK**: Template files exist and are accessible
- 7.6. **CHECK**: Template structure matches expected schema
- 7.7. **CHECK**: Template contains required fields (identity, name, description, etc.)
- 7.8. **CHECK**: Template has no unused parameters or undefined variables
- 7.9. **CHECK**: Template default values are present for optional fields
- 7.10. **CHECK**: Template maintains SSOT compliance (no content duplication)
- 7.11. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 7.12. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 7.13. **VALIDATION**: Validate that template validation completed successfully
- 7.14. **STATUS TRACKING**: Update workflow status to "phase_7_complete"

### Phase 8. Comprehensive Cross-Reference Validation
**Best Practice**: Reference integrity - ensure all internal/external references resolve correctly

- 8.1. **STATUS TRACKING**: Update workflow status to "phase_8_in_progress"
- 8.2. **ACTION**: BP? - "document reference cross-validation minimal requirements"
- 8.3. **ACTION**: Extract all references from workflow (internal step refs, external docs, templates)
- 8.4. **ACTION**: Validate each reference type systematically
- 8.5. **CHECK**: All internal step number references point to existing steps
- 8.6. **CHECK**: All internal phase number references point to existing phases
- 8.7. **CHECK**: All external document references exist and are accessible
- 8.8. **CHECK**: All template references resolve to valid template files
- 8.9. **CHECK**: Reference descriptions match target content
- 8.10. **CHECK**: No circular references exist
- 8.11. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 8.12. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 8.13. **VALIDATION**: Validate that cross-reference validation completed successfully
- 8.14. **STATUS TRACKING**: Update workflow status to "phase_8_complete"

### Phase 9. SSOT Compliance Validation
**Best Practice**: Single source of truth - ensure no content duplication and proper references

- 9.1. **STATUS TRACKING**: Update workflow status to "phase_9_in_progress"
- 9.2. **ACTION**: BP? - "single source of truth document validation essential checks"
- 9.3. **ACTION**: Identify all data elements and their sources in workflow
- 9.4. **ACTION**: Check for content duplication across workflow and references
- 9.5. **CHECK**: Workflow does not duplicate template/reference content
- 9.6. **CHECK**: Each data element has one canonical source
- 9.7. **CHECK**: Template references are used instead of content copying
- 9.8. **CHECK**: Cross-references match canonical sources
- 9.9. **CHECK**: Workflow maintains single source of truth principles
- 9.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 9.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 9.12. **VALIDATION**: Validate that SSOT compliance validation completed successfully
- 9.13. **STATUS TRACKING**: Update workflow status to "phase_9_complete"

### Phase 10. Early-Exit Pattern Validation
**Best Practice**: Early-exit on failure - ensure workflow stops immediately on critical errors

- 10.1. **STATUS TRACKING**: Update workflow status to "phase_10_in_progress"
- 10.2. **ACTION**: BP? - "minimal viable document validation quality gates"
- 10.3. **ACTION**: Review all conditional logic for early-exit patterns
- 10.4. **CHECK**: Workflow implements early-exit on critical errors
- 10.5. **CHECK**: Critical error conditions are clearly defined
- 10.6. **CHECK**: Early-exit logic prevents cascading failures
- 10.7. **CHECK**: Error messages provide specific location and fix guidance
- 10.8. **CHECK**: Workflow does not continue past critical errors
- 10.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 10.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 10.11. **VALIDATION**: Validate that early-exit pattern validation completed successfully
- 10.12. **STATUS TRACKING**: Update workflow status to "phase_10_complete"

### Phase 11. Reference Document Integrity Validation
**Best Practice**: Reference document validation - ensure all referenced documents are valid and current

- 11.1. **STATUS TRACKING**: Update workflow status to "phase_11_in_progress"
- 11.2. **ACTION**: BP? - "reference document integrity validation standards"
- 11.3. **ACTION**: Load all referenced documents
- 11.4. **ACTION**: Validate each reference document for structural integrity
- 11.5. **CHECK**: All referenced documents exist and are accessible
- 11.6. **CHECK**: Reference document paths are accurate
- 11.7. **CHECK**: Reference document versions are compatible
- 11.8. **CHECK**: Reference document content aligns with workflow usage
- 11.9. **CHECK**: Reference documents maintain their own SSOT compliance
- 11.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 11.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 11.12. **VALIDATION**: Validate that reference document integrity validation completed successfully
- 11.13. **STATUS TRACKING**: Update workflow status to "phase_11_complete"

### Phase 12. Template Integrity Validation
**Best Practice**: Template validation - ensure template structure and content are valid

- 12.1. **STATUS TRACKING**: Update workflow status to "phase_12_in_progress"
- 12.2. **ACTION**: BP? - "template integrity validation complete framework"
- 12.3. **ACTION**: Load all template files referenced in workflow
- 12.4. **ACTION**: Validate template structure against schema
- 12.5. **CHECK**: Template files have valid structure
- 12.6. **CHECK**: Template required fields are present
- 12.7. **CHECK**: Template parameter definitions are valid
- 12.8. **CHECK**: Template default values are appropriate
- 12.9. **CHECK**: Template maintains consistency with workflow requirements
- 12.10. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 12.11. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 12.12. **VALIDATION**: Validate that template integrity validation completed successfully
- 12.13. **STATUS TRACKING**: Update workflow status to "phase_12_complete"

### Phase 13. Sequential Phase/Step Analysis
**Best Practice**: Stage transition verification - ensure logical flow between stages

For each phase/step in sequential order:

- 12.1. **STATUS TRACKING**: Update workflow status to "phase_12_in_progress"
- 12.2. **ACTION**: BP? - "workflow step validation and conditional logic best practices"
- 12.3. **ACTION**: Read current phase/step content
- 12.4. **CHECK**: Status tracking pattern matches other phases/steps
- 12.5. **CHECK**: Validation steps are consistent with reference patterns
- 12.6. **CHECK**: Phase/step transitions are correct
- 12.7. **ACTION**: Read all referenced documents for this phase/step
- 12.8. **CHECK**: Referenced document content aligns with workflow usage
- 12.9. **CHECK**: Conditional logic (IF/ELSE) is complete and accurate
- 12.10. **CHECK**: Cross-references to other steps are accurate
- 12.11. **CHECK**: File paths and directory references are correct
- 12.12. **CHECK**: Template references (if applicable) are accurate
- 12.13. **CHECK**: Action verbs are clear and actionable
- 12.14. **CHECK**: Step numbering is sequential and logical
- 12.15. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 12.16. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 12.17. **VALIDATION**: Validate that phase/step analysis completed successfully
- 12.18. **STATUS TRACKING**: Update workflow status to "phase_12_complete"

### Phase 14. Conditional Logic Validation
**Best Practice**: Process coherence - ensure all logical branches are complete

- 14.1. **STATUS TRACKING**: Update workflow status to "phase_14_in_progress"
- 14.2. **ACTION**: Review all IF statements throughout workflow
- 14.3. **CHECK**: IF conditions are clear and unambiguous
- 14.4. **CHECK**: ELSE/ELSE IF logic covers all possible cases
- 14.5. **CHECK**: Mode-specific conditions are properly scoped
- 14.6. **CHECK**: Nested conditionals are properly structured
- 14.7. **CHECK**: Conditional branching leads to correct next steps
- 14.8. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 14.9. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 14.10. **VALIDATION**: Validate that conditional logic validation completed successfully
- 14.11. **STATUS TRACKING**: Update workflow status to "phase_14_complete"

### Phase 15. Status Tracking Pattern Validation
**Best Practice**: Operational consistency - ensure consistent status tracking

- 15.1. **STATUS TRACKING**: Update workflow status to "phase_15_in_progress"
- 15.2. **ACTION**: BP? - "status tracking and workflow state management best practices"
- 15.3. **ACTION**: Review all status tracking steps throughout workflow
- 15.4. **CHECK**: All phases/steps follow consistent status pattern (e.g., in_progress → complete)
- 15.5. **CHECK**: Status naming conventions are consistent
- 15.6. **CHECK**: Sub-status tracking (e.g., phase_4a vs phase_4b) is properly differentiated
- 15.7. **CHECK**: Status transitions are logical and complete
- 15.8. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 15.9. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 15.10. **VALIDATION**: Validate that status tracking validation completed successfully
- 15.11. **STATUS TRACKING**: Update workflow status to "phase_15_complete"

### Phase 16. File System & Path Validation
**Best Practice**: Documentation control - verify all file system references are accurate

- 16.1. **STATUS TRACKING**: Update workflow status to "phase_16_in_progress"
- 16.2. **ACTION**: BP? - "cross-reference validation and document integrity best practices"
- 16.3. **ACTION**: Verify all referenced template files exist
- 16.4. **ACTION**: Verify all referenced configuration files exist
- 16.5. **CHECK**: Template file paths are correct
- 16.6. **CHECK**: Directory references are consistent
- 16.7. **CHECK**: File naming conventions are consistent
- 16.8. **CHECK**: Directory structure matches documented specifications
- 16.9. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 16.10. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 16.11. **VALIDATION**: Validate that file system validation completed successfully
- 16.12. **STATUS TRACKING**: Update workflow status to "phase_16_complete"

### Phase 17. Universal Framework Alignment
**Best Practice**: Process coherence - ensure alignment with universal standards

- 17.1. **STATUS TRACKING**: Update workflow status to "phase_17_in_progress"
- 17.2. **ACTION**: Read universal framework references (if present)
- 17.3. **CHECK**: Workflow aligns with universal framework concepts
- 17.4. **CHECK**: Agent-specific customizations are properly documented
- 17.5. **CHECK**: Universal framework references are current
- 17.6. **CHECK**: Customizations don't violate universal principles
- 17.7. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 17.8. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 17.9. **VALIDATION**: Validate that framework alignment validation completed successfully
- 17.10. **STATUS TRACKING**: Update workflow status to "phase_17_complete"

### Phase 18. Metadata and Structure Validation
**Best Practice**: Documentation control - ensure structural integrity

- 18.1. **STATUS TRACKING**: Update workflow status to "phase_18_in_progress"
- 18.2. **ACTION**: BP? - "file system organization and path management best practices"
- 18.3. **ACTION**: Review all metadata sections throughout document
- 18.4. **CHECK**: Section headers are properly formatted
- 18.5. **CHECK**: Table of contents (if present) matches actual structure
- 18.6. **CHECK**: Section numbering is sequential and logical
- 18.7. **CHECK**: Section hierarchy is consistent
- 18.8. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 18.9. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 18.10. **VALIDATION**: Validate that metadata and structure validation completed successfully
- 18.11. **STATUS TRACKING**: Update workflow status to "phase_18_complete"

### Phase 19. Integration and Compatibility Check
**Best Practice**: Process coherence - ensure all components work together

- 19.1. **STATUS TRACKING**: Update workflow status to "phase_19_in_progress"
- 19.2. **ACTION**: Verify workflow properly references external components
- 19.3. **CHECK**: Template references avoid content duplication (SSOT compliance)
- 19.4. **CHECK**: External system integrations are properly documented
- 19.5. **CHECK**: API/service references are accurate
- 19.6. **CHECK**: Dependencies are clearly documented
- 19.7. **IF INCONSISTENCY FOUND**: STOP - Report inconsistency with specific location and suggested fix
- 19.8. **AWAIT USER APPROVAL**: Wait for user to approve fix before proceeding
- 19.9. **VALIDATION**: Validate that integration and compatibility check completed successfully
- 19.10. **STATUS TRACKING**: Update workflow status to "phase_19_complete"

### Phase 19. Final Consistency Validation
**Best Practice**: Document control - final quality assurance check

- 19.1. **STATUS TRACKING**: Update workflow status to "phase_19_in_progress"
- 19.2. **ACTION**: BP? - "final workflow validation and quality assurance best practices"
- 19.3. **ACTION**: Perform comprehensive review of all fixes applied during validation
- 19.4. **CHECK**: All inconsistencies found during validation were resolved
- 19.5. **CHECK**: Workflow is ready for deployment/use
- 19.6. **IF REMAINING ISSUES**: STOP - Report remaining issues with suggested fixes
- 19.7. **AWAIT USER APPROVAL**: Wait for user to approve final state
- 19.8. **VALIDATION**: Validate that final consistency validation completed successfully
- 19.9. **STATUS TRACKING**: Update workflow status to "phase_19_complete"
- 19.10. **PRINT**: "Architect Workflow Validation workflow execution complete - workflow validated"

---

## Execution Guidelines

### Process
1. Execute phases in sequential order
2. Stop at each inconsistency found
3. Report inconsistency with specific location and suggested fix
4. Await user approval before proceeding
5. Apply fix and continue validation
6. Repeat until all phases are complete

### Best Practice Application
- **Multi-stage review**: Each phase checks different aspects (structural, logical, referential)
- **Cross-reference validation**: Systematic verification of all internal and external references
- **Stage transition verification**: Ensure logical flow between all workflow stages
- **Process coherence**: Maintain semantic consistency across all documentation levels
- **Documentation control**: Verify version accuracy, ownership, and audit trail integrity
- **Web search integration**: Use "BP?" web searches at designated points to validate against current industry best practices
- **Persona compliance**: Validate workflow-defined personas meet best practice standards

### Quality Standards
- All critical issues must be resolved before deployment
- Important issues should be resolved with documented rationale if deferred
- Minor issues can be deferred to next revision cycle
- All changes must maintain SSOT compliance
- All changes must be documented with audit trail
- All personas must meet five-element best practice standards

## Usage Instructions

### For Workflow Validation
1. Specify target workflow document path
2. Execute systematic validation process in sequential order
3. Stop at each inconsistency found and report with suggested fix
4. Await user approval for each fix before proceeding
5. Continue until all phases are complete and workflow is validated

### For Architect Agent Use
1. Architect agent loads Validation Architect persona from workflow
2. Execute interactive validation of target workflow
3. Maintain SSOT compliance throughout validation process
4. Apply fixes interactively with user approval

### Maintenance
- Update best practices section annually based on industry research
- Customize reference document checks based on workflow requirements
- Maintain systematic sequential structure for consistency
- Document workflow changes with version control
- Keep persona definitions aligned with agent-specific requirements

---

**Last Updated**: 2026-07-29
**Version**: 1.0 (Initial Architect workflow with persona validation)
**Maintained By**: Architect Agent