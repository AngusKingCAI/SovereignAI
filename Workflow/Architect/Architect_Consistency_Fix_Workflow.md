---
id: wf-arch-cons-fix
status: active
owner: architect-agent
updated: 2026-07-28
version: "1.0"
purpose: Workflow for Architect agent to systematically fix consistency issues identified in consistency checks
expected_agent_type: architect-agent
persona:
  role: "Consistency Fix Architect"
  expertise: "Architecture consistency validation, governance compliance, structural analysis, reference integrity verification"
  process: "Systematic scanning and validation of harness architecture with comprehensive reporting"
  output: "Consistency reports with findings classified by severity and actionable recommendations"
  constraints: "Harness architecture scope only (excludes /app folder), informational failure handling for comprehensive coverage"
---

# Architect Consistency Fix Workflow

**ID**: wf-arch-cons-fix  
**owner**: architect agent  
**Frequency**: On-demand (triggered after consistency check identifies issues)  
**Duration**: Variable (30-120 minutes depending on issue count and complexity)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility/Tool Workflow)
**Execution Modes**: Manual, Automatic
**Workflow Steps**: 72 steps

## Purpose
Systematic resolution of consistency issues identified by the Consistency Check Workflow. This workflow processes the consistency report and implements fixes for broken references, terminology inconsistencies, workflow structure issues, and schema validation problems. The workflow supports both Manual mode (user confirmation for each fix) and Automatic mode (batch processing of non-critical fixes).

## Reference Documents
- **Agent Rules**: Rules/Architect/Architect_Rules.md (Architect-specific governance rules)
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)
- **Execution Mode Patterns**: Workflow/Architect/.Reference/Execution_Mode_Patterns.md (Architect-specific execution mode definitions)
- **Universal Framework References**: Workflow/Workflow_Reference/ (referenced frameworks based on workflow relevance)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns)

## Scope
**Harness Architecture Only**: Governance files, workflows, rules, documentation (excludes /app folder)

**Input**: Consistency report from Logs/Architect/Consistency Review/

**Output**: Fixed governance files and updated consistency report with (FIXED) prefix

## Roles and Owners
- **Architect Agent**: Executes fixes, validates changes, updates governance files
- **User**: Reviews proposed fixes (Manual mode), approves critical changes, validates results
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: Consistency check identifies issues requiring fixes
- **End State**: All identified consistency issues resolved, schema validation passing

## Workflow Steps (72 steps)

### Phase 0. Load Governance Rules + Consistency Report
- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on current agent type
- 2. Read most recent consistency report from Logs/Architect/Consistency Review/
- 3. Parse consistency report to identify issues by severity (CRITICAL, HIGH, MEDIUM, LOW)
- 4. Store governance context and issue list for reference throughout workflow execution
- 5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 6. **PRINT**: "Governance rules loaded dynamically - consistency report loaded - {N} issues identified"

### Phase 1. Select Execution Mode
- 1. Ask user to select execution mode using popup menu:
  - **Manual**: Review and approve each fix individually (recommended for CRITICAL issues)
  - **Automatic**: Apply all non-critical fixes automatically, CRITICAL fixes require approval
- 2. Store selected execution mode for failure handling throughout workflow
- 3. **PRINT**: "Execution mode selected - [Manual/Automatic] will govern fix application"

### Phase 2. Issue Categorization and Prioritization
- 1. Categorize identified issues by type:
  - File reference issues (broken paths, missing files)
  - Terminology inconsistencies (outdated terms)
  - Workflow structure issues (missing sections, incorrect formatting)
  - Schema validation issues (categorization rule violations)
- 2. Prioritize issues by severity: CRITICAL > HIGH > MEDIUM > LOW
- 3. Group related issues for batch processing (e.g., all file reference fixes together)
- 4. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 5. **PRINT**: "Issues categorized and prioritized - {N} CRITICAL, {N} HIGH, {N} MEDIUM, {N} LOW"

### Phase 3. File Reference Fixes (CRITICAL)
- 1. **SCAN**: For each file reference issue:
  - **Manual Mode**: Present issue details and proposed fix to user via popup menu
  - **Automatic Mode**: Apply fix automatically if LOW/MEDIUM, CRITICAL requires approval
- 2. Fix missing or incorrectly named workflow files (rename or create)
- 3. Remove workflow references from rules files (architectural principle compliance)
- 4. Remove references to non-existent rules files
- 5. **VALIDATION**: Validate each fix using file existence checks
- 6. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 7. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 8. **PRINT**: "File reference fixes complete - {N} references updated"

### Phase 4. Terminology Fixes (HIGH)
- 1. **SCAN**: For each terminology inconsistency:
  - **Manual Mode**: Present term and proposed replacement via popup menu
  - **Automatic Mode**: Apply standard terminology replacements automatically
- 2. Replace outdated "gate" terminology with "validation" (excluding tool names)
- 3. Standardize agent naming conventions
- 4. Ensure consistent framework naming
- 5. **VALIDATION**: Validate terminology fixes using grep to confirm replacements
- 6. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 7. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 8. **PRINT**: "Terminology fixes complete - {N} terms standardized"

### Phase 5. Workflow Structure Fixes (MEDIUM)
- 1. **SCAN**: For each workflow structure issue:
  - **Manual Mode**: Present structure issue and proposed fix via popup menu
  - **Automatic Mode**: Apply template compliance fixes automatically
- 2. Add missing "Execution Modes" to workflow headers
- 3. Fix step numbering inconsistencies
- 4. Ensure all workflows have mandated sections (header, universal framework references)
- 5. Validate workflow follows template structure
- 6. **VALIDATION**: Validate structure fixes using template comparison
- 7. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 8. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 9. **PRINT**: "Workflow structure fixes complete - {N} workflows updated"

### Phase 6. Schema Validation Fixes (MEDIUM)
- 1. **SCAN**: For each schema validation issue:
  - **Manual Mode**: Present categorization rule violation and proposed fix via popup menu
  - **Automatic Mode**: Apply categorization rule updates automatically
- 2. Update categorization rules in Scripts/Schema/validate_schemas.py
- 3. Remove index.md exceptions if not required by architecture
- 4. Update rule files to reference correct documentation paths
- 5. **VALIDATION**: Run schema validation script to confirm all fixes
- 6. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 7. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 8. **PRINT**: "Schema validation fixes complete - validation passing"

### Phase 7. Final Validation and Report Update
- 1. Run comprehensive schema validation: `python Scripts/Schema/validate_schemas.py`
- 2. Run consistency check workflow to verify all issues resolved
- 3. Rename original consistency report with (FIXED) prefix
- 4. Generate summary of fixes applied with before/after comparison
- 5. **VALIDATION**: Validate all fixes completed successfully
- 6. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 7. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 8. **PRINT**: "Final validation complete - all consistency issues resolved"

### Phase 8. Documentation
- 1. Update AGENTS.md if agent capabilities changed during fixes
- 2. Update INDEX.md if governance structure changed
- 3. Document architectural decisions made during fix process
- 4. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 5. **PRINT**: "Documentation complete - governance files updated"

### Phase 9. Final Validation
- 1. Verify all fixes comply with Rules/Architect/Architect_Rules.md
- 2. Verify schema validation passes (645/645 files)
- 3. Verify no unintended changes outside target files
- 4. **VALIDATION**: Validate that final validation completed successfully
- 5. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 6. **PRINT**: "Final validation complete - architecture fully compliant"

### Phase 10. Terminate
- 1. **PRINT**: "Consistency fix workflow complete - {N} issues resolved, schema validation passing"
- 2. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Consistency fix quality criteria
- **Focus**: Fix accuracy and architectural compliance

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific consistency management responsibilities
- **Focus**: Issue resolution and governance compliance

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Fix completion metrics and time tracking
- **Focus**: Issue resolution efficiency and accuracy

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Consistency fix state tracking
- **Focus**: Fix progress state and validation tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Manual vs Automatic fix execution patterns
- **Focus**: Prioritized issue resolution and user approval handling

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Architect Customization**: Fix validation patterns
- **Focus**: Schema validation and architectural compliance verification

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Consistency fix runtime requirements
- **Focus**: Runtime paths and infrastructure requirements for fix execution

## File Placement Compliance
- Create Workflow/Architect/ directory if it doesn't exist
- Place workflow file in Workflow/Architect/Architect_Consistency_Fix_Workflow.md
- Follow naming convention: {Agent}_{WorkflowType}_Workflow.md
- Check INDEX.md for folder structure compliance

## Changelog

**2026-07-30**: YAML frontmatter fixes + step count correction
- Added missing YAML frontmatter fields (version, expected_agent_type, persona)
- Fixed step count inconsistency (63 → 72 steps)
- Added Reference Documents section with proper references
- Added early-exit patterns in all validation phases
- Fixed ID consistency (standardized to wf-arch-cons-fix)
- Updated version to 1.0