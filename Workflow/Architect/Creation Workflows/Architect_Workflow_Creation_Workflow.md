---
id: wf-arch-workflow-creation
status: active
owner: architect-agent
updated: 2026-07-29
version: "1.0"
purpose: Architect workflow for creating new agent workflows by extracting user intent and applying it to the workflow template
expected_agent_type: architect-agent
persona:
  role: "Workflow Creation Architect"
  expertise: "Workflow design, template application, intent extraction, workflow validation, schema compliance"
  process: "Interactive workflow creation with user intent extraction, template application, and validation"
  output: "Complete workflow files validated against schema and template requirements"
  constraints: "Template compliance required, schema validation mandatory, user approval before completion"
---

# Architect Workflow Creation Workflow

**ID**: WF-ARCH-WORKFLOW-CREATION  
**Owner**: Architect Agent  
**Frequency**: Per workflow creation request  
**Duration**: Variable (workflow complexity dependent)  
**Priority**: High
**Workflow Type**: Single-Execution (create one workflow per execution)
**Execution Modes**: Manual, Template-Assisted
**Phase Structure**: 10 phases (0-10) for workflow creation: Load Governance Rules, Select Execution Mode, Extract User Intent, Load Workflow Template, Design Workflow Structure, Create Workflow Components, Validate Workflow Schema, Validate Template Compliance, User Review and Approval, Save Workflow File, Workflow Termination

## Purpose
Create new agent workflows by extracting user intent, applying it to the workflow template, and validating the resulting workflow against schema and template requirements. This workflow ensures all created workflows follow proper structure, comply with governance standards, and are ready for agent use.

## Reference Documents
- **Workflow Template**: Workflow/Architect/Creation Workflows/Templates/Workflow_Template.md (template structure with [**MANDATED**] and [**SUGGESTED**] markers)
- **Workflow Schema**: Scripts/Schema/workflow-schema.json (JSON schema for workflow validation)
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)
- **Project Rules**: Rules/Architect/Architect_Rules.md (Architect-specific governance rules)
- **Validation Script**: Scripts/Infrastructure/workflow-validation.py (workflow validation automation)

## Roles and Owners
- **Architect Agent**: Executes workflow creation, applies template, validates result
- **User**: Provides workflow intent, approves creation decisions
- **Governance System**: Template compliance enforcement, schema validation

## Trigger and End State
- **Trigger**: User requests creation of a new workflow for an agent
- **End State**: New workflow file created, validated against schema and template, ready for agent use

## Workflow Steps (10 phases)

### Phase 0. Load Governance Rules
- 0.1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 0.2. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 0.3. **PRINT** "Governance rules loaded dynamically based on agent type"

### Phase 1. Select Execution Mode
- 1.1. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Interactive workflow creation with step-by-step user guidance
  - **Template-Assisted**: Semi-automated creation using template structure
- 1.2. Store selected execution mode for failure handling throughout workflow
- 1.3. **STATUS TRACKING**: Update workflow status to "phase_1_complete"
- 1.4. **PRINT** "Execution mode selected - [mode] will govern workflow creation approach"

### Phase 2. Extract User Intent
- 2.1. Ask user: "What workflow do you want to create? Please describe the workflow purpose, target agent, and key functionality."
- 2.2. Wait for user to specify their workflow requirements
- 2.3. Clarify the workflow intent if needed:
  - Target agent (e.g., Planner, Executor, Architect)
  - Workflow type (e.g., Plan Creation, Implementation Cycle, Validation)
  - Primary purpose and scope
  - Key phases or sections needed
  - Special requirements or constraints
- 2.4. Document user intent for workflow creation
- 2.5. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 2.6. **PRINT** "User intent extracted - workflow requirements documented"

### Phase 3. Load Workflow Template
- 3.1. **ACTION**: Read Workflow/Architect/Creation Workflows/Templates/Workflow_Template.md
- 3.2. **ACTION**: Parse template structure to understand mandated and suggested sections
- 3.3. **CHECK**: Template structure matches expected format
- 3.4. **ACTION**: Extract template header structure for YAML frontmatter
- 3.5. **ACTION**: Extract workflow step structure (excluding [**MANDATED**]/[**SUGGESTED**] markers)
- 3.6. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 3.7. **PRINT** "Workflow template loaded - structure parsed for application"

### Phase 4. Design Workflow Structure
- 4.1. Based on user intent, design the workflow structure:
  - Determine workflow ID format (WF-{AGENT}-{XXX})
  - Define workflow header metadata (owner, frequency, duration, priority)
  - Select workflow type (Continuous Operation vs Single-Execution)
  - Define execution modes appropriate for the workflow
  - Identify which suggested sections to include based on workflow needs
- 4.2. **ACTION**: BP? - "workflow design and structure best practices"
- 4.3. **ACTION**: FC? - "workflow structure accuracy and factual correctness verification"
- 4.4. **CHECK**: Workflow structure aligns with user intent
- 4.5. **CHECK**: Workflow structure includes all mandated sections from template
- 4.6. **CHECK**: Workflow structure includes appropriate suggested sections from template
- 4.7. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 4.8. **PRINT** "Workflow structure designed - aligns with user intent and template requirements"

### Phase 5. Create Workflow Components
- 5.1. **ACTION**: Create YAML frontmatter based on template structure:
  - id: wf-{agent}-{workflow-type}
  - status: active
  - owner: {agent}-agent
  - updated: {current date}
  - version: "1.0"
  - purpose: {workflow purpose from user intent}
  - expected_agent_type: {target agent}
  - persona: {role, expertise, process, output, constraints}
- 5.2. **ACTION**: Create workflow header section with ID, Owner, Frequency, Duration, Priority, Workflow Type, Execution Modes, Phase Structure
- 5.3. **ACTION**: Create Purpose section based on user intent
- 5.4. **ACTION**: Create Reference Documents section with relevant universal framework references, agent rules, best practice integration, terminology glossary
- 5.5. **ACTION**: Create Roles and Owners section defining agent, user, and governance system responsibilities
- 5.6. **ACTION**: Create Trigger and End State section defining workflow entry and exit conditions
- 5.7. **ACTION**: Create Workflow Steps section based on template structure:
  - Include Load Governance Rules section (mandated by template)
  - Include Select Execution Mode section (mandated by template)
  - Include relevant suggested sections based on workflow design
  - Customize each section based on user intent and agent requirements
  - Remove [**MANDATED**] and [**SUGGESTED**] markers from section names
- 5.8. **ACTION**: Create Universal Framework References section with only relevant frameworks
- 5.9. **CHECK**: Header matches template structure
- 5.10. **CHECK**: All required header fields present
- 5.11. **CHECK**: Purpose aligns with user intent
- 5.12. **CHECK**: All relevant references included
- 5.13. **CHECK**: Role definitions are clear and complete
- 5.14. **CHECK**: Trigger conditions are clear and specific
- 5.15. **CHECK**: All mandated sections from template included
- 5.16. **CHECK**: Suggested sections appropriate for workflow type
- 5.17. **CHECK**: Section content aligns with user intent
- 5.18. **CHECK**: No template markers remain in final workflow
- 5.19. **CHECK**: Universal framework references are relevant
- 5.20. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 5.21. **PRINT** "Workflow components created - template structure applied without markers"

### Phase 6. Validate Workflow Schema
- 6.1. **ACTION**: Run workflow validation script against created workflow
- 6.2. **ACTION**: python Scripts/Schema/workflow-validation.py <workflow-file>
- 6.3. **CHECK**: Schema validation passes
- 6.4. **CHECK**: All required fields present
- 6.5. **CHECK**: Field formats are correct
- 6.6. **IF VALIDATION FAILS**: STOP - Report validation errors with specific fixes needed
- 6.7. **AWAIT USER APPROVAL**: Wait for user to approve fixes before proceeding
- 6.8. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 6.9. **PRINT** "Workflow schema validated - compliant with workflow-schema.json"

### Phase 7. Validate Template Compliance
- 7.1. **ACTION**: Validate workflow against template requirements
- 7.2. **CHECK**: All mandated sections from template present
- 7.3. **CHECK**: Suggested sections appropriately included/excluded
- 7.4. **CHECK**: Section structure matches template format
- 7.5. **CHECK**: YAML frontmatter structure matches template
- 7.6. **CHECK**: No [**MANDATED**] or [**SUGGESTED**] markers remain in workflow
- 7.7. **IF COMPLIANCE FAILS**: STOP - Report compliance errors with specific fixes needed
- 7.8. **AWAIT USER APPROVAL**: Wait for user to approve fixes before proceeding
- 7.9. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 7.10. **PRINT** "Template compliance validated - workflow follows template structure"

### Phase 8. User Review and Approval
- 8.1. **ACTION**: Present completed workflow to user for review
- 8.2. **ACTION**: Highlight key sections and design decisions
- 8.3. **ASK USER**: "Does this workflow meet your requirements? Any changes needed?"
- 8.4. **AWAIT USER APPROVAL**: Wait for user approval before finalizing
- 8.5. **IF CHANGES REQUESTED**: Make requested changes and re-validate
- 8.6. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 8.7. **PRINT** "User review complete - workflow approved for delivery"

### Phase 9. Save Workflow File
- 9.1. **ACTION**: Determine appropriate file location:
  - Agent-specific workflows: Workflow/{Agent}/{Agent}_Workflow.md
  - Architect workflows: Workflow/Architect/{Workflow_Name}_Workflow.md
  - Creation workflows: Workflow/Architect/Creation Workflows/{Workflow_Name}_Workflow.md
  - Validation workflows: Workflow/Architect/Validation Workflows/{Workflow_Name}_Workflow.md
- 9.2. **ACTION**: Save workflow file to appropriate location
- 9.3. **ACTION**: Verify file saved successfully
- 9.4. **CHECK**: File path follows naming convention
- 9.5. **CHECK**: File is accessible and readable
- 9.6. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 9.7. **PRINT** "Workflow file saved - ready for agent use"

### Phase 10. Workflow Termination (Single-Execution)
- 10.1. **ACTION**: Perform final validation of complete workflow
- 10.2. **CHECK**: Workflow file is complete and valid
- 10.3. **CHECK**: All validations passed successfully
- 10.4. **CHECK**: User approval obtained
- 10.5. **CHECK**: File saved to correct location
- 10.6. **VALIDATION**: Validate that workflow creation completed successfully
- 10.7. **STATUS TRACKING**: Update workflow status to "phase_10_complete"
- 10.8. **PRINT** "Final validation complete - workflow creation successful"
- 10.9. **PRINT** "Workflow execution complete - workflow creation terminated"
- 10.10. **PRINT** "Architect agent ready - awaiting next user request"
- 10.11. **TERMINATE**: End workflow execution (do not return to Phase 0)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Agent Customization**: Workflow creation quality criteria within universal framework
- **Usage**: Reference universal framework for consistency

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Agent Customization**: Workflow creation template customization
- **Usage**: Reference universal framework for consistency

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Agent Customization**: Workflow creation validation patterns
- **Usage**: Reference universal framework for consistency