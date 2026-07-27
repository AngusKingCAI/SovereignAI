# SovereignAI Harness Terminology Glossary

**Purpose**: Single source of truth (SSOT) for all capitalized terminology used across the SovereignAI harness architecture. This glossary ensures consistent understanding of governance terminology across all agents and workflows.

**Governance**: This document is maintained by the Architect agent and serves as the authoritative source for terminology definitions. All agents must reference this glossary for terminology understanding.

---

## Core Workflow Commands

### **SCAN**
**Definition**: Examine all documents within scope line by line without skipping anything - comprehensive examination required for governance compliance.

**Usage**: Used when comprehensive examination of documents is required for governance compliance, quality assurance, or consistency verification. This is the primary scanning method and cannot be replaced by pattern matching tools like grep.

**Examples**:
- **SCAN** all harness architecture files for consistency checks
- **SCAN** App/ directory line by line for compliance verification
- **SCAN** workflow files to validate template compliance

---

### **PRINT**
**Definition**: Output text to chat interface for user visibility (not to files or logs).

**Usage**: Used to communicate workflow status, progress updates, and important information to the user during workflow execution. This command does not write to files or logs.

**Examples**:
- **PRINT** "Workflow initialization complete"
- **PRINT** "Scan strategy selected - Full Comprehensive"
- **PRINT** "Consistency check complete - 0 issues found"

---

### **VALIDATION**
**Definition**: Validate step completion before proceeding to next phase.

**Usage**: Used to ensure that workflow steps have completed successfully and meet quality criteria before moving to the next phase. This is a quality validation mechanism.

**Examples**:
- **VALIDATION**: Validate file reference extraction completed successfully
- **VALIDATION**: Validate workflow structure check completed successfully
- **VALIDATION**: Validate that all referenced files exist

---

### **STATUS TRACKING**
**Definition**: Update workflow status for monitoring and recovery.

**Usage**: Used to track workflow progress, enable recovery from failures, and provide visibility into workflow execution state. Status updates are typically written to workflow_state.json or similar tracking mechanisms.

**Examples**:
- **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- **STATUS TRACKING**: Update workflow status to "phase_7_complete"

---

### **TERMINATE**
**Definition**: End workflow execution (do not return to step 1).

**Usage**: Used in single-execution workflows to signal completion and prevent automatic looping. This is the workflow termination command for utility workflows.

**Examples**:
- **TERMINATE**: End workflow execution (do not return to step 1)
- **TERMINATE**: Workflow execution complete - workflow terminated

---

## Workflow-Specific Commands

### **EXECUTION MODE HANDLING**
**Definition**: Apply execution mode handling patterns based on selected mode (Manual/Auto/Complete).

**Usage**: Used to determine how the workflow should respond to failures based on the user-selected execution mode.

**Modes**:
- **Manual**: Stop at failures for human oversight
- **Auto**: Don't continue on failures (auto-stop on errors)
- **Complete**: Continue past failures (ignore all errors)

**Examples**:
- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- **EXECUTION MODE HANDLING**: Apply review mode handling patterns

---

### **CONVERGENCE CHECK**
**Definition**: Verify panelist scores against quality thresholds.

**Usage**: Used in Round Table review processes to determine if panelists have reached agreement on quality assessments.

**Thresholds**:
- Clean pass: ≥4.5 score
- Acceptable pass: 3.5-4.4 score with documented rationale
- Fail: <3.5 score

**Examples**:
- **CONVERGENCE CHECK**: Check if all panelists chose PASS (≥4.5 score or 3.5-4.4 with rationale)
- **CONVERGENCE CHECK**: Verify convergence criteria met

---

### **QUOTA AWARENESS**
**Definition**: Monitor internal subagent quota usage for recovery tracking.

**Usage**: Used to track subagent resource consumption and enable recovery if quota limits are approached or exceeded.

**Examples**:
- **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress
- **QUOTA AWARENESS**: Track quota usage for recovery if needed

---

### **LOOP DECISION**
**Definition**: Determine workflow continuation based on conditions.

**Usage**: Used to control workflow flow and determine whether to loop back to previous phases or proceed forward.

**Examples**:
- **LOOP DECISION**: If more plan steps remain → Return to step 25 with next step
- **LOOP BACK**: Return to Phase 4 for next iteration

---

### **HANDOFF VALIDATION**
**Definition**: Verify handoff file integrity and completeness.

**Usage**: Used when transferring work between agents to ensure all required information is present and accessible.

**Examples**:
- **HANDOFF VALIDATION**: Verify handoff file integrity per template requirements
- **HANDOFF VALIDATION**: Validate all required fields are present

---

## Decision and Planning Commands

### **ARCHITECT OPINION**
**Definition**: Provide analysis and recommendation BEFORE user selection.

**Usage**: Used by Architect agent to provide expert analysis and recommendations when presenting implementation options to users.

**Examples**:
- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- **ARCHITECT OPINION**: Recommend optimal approach based on analysis

---

### **PRESENTATION PATTERN**
**Definition**: Present options with metrics, provide architect opinion, use popup menu for selection.

**Usage**: Used to standardize how options are presented to users, ensuring consistent format and decision-making process.

**Examples**:
- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu
- **PRESENTATION PATTERN**: Use popup menu for selection

---

### **RULE ENFORCEMENT**
**Definition**: Ensure options comply with agent rules.

**Usage**: Used to validate that proposed options or approaches comply with the relevant agent's governance rules.

**Examples**:
- **RULE ENFORCEMENT**: Ensure options comply with Architect rules
- **RULE ENFORCEMENT**: Validate compliance with governance constraints

---

### **SPECIFICATION CONFIRMATION**
**Definition**: Ask user to confirm specification or request modifications using popup menu.

**Usage**: Used to get user approval on detailed specifications before proceeding with implementation.

**Examples**:
- **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications
- **SPECIFICATION CONFIRMATION**: Use popup menu with [Confirm/Modify] options

---

### **IMPLEMENTATION MODE SELECTION**
**Definition**: Ask user to choose implementation mode using popup menu.

**Usage**: Used to determine whether implementation should be automated or manual based on user preference.

**Examples**:
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu
- **IMPLEMENTATION MODE SELECTION**: Select automated vs manual implementation

---

## Information and Notes

### **AUTOMATED PROGRESSION NOTE**
**Definition**: Validation system behavior notes for context.

**Usage**: Used to provide explanatory notes about how the validation system behaves in specific situations.

**Examples**:
- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools automatically during this step
- **AUTOMATED PROGRESSION NOTE**: User confirmation requests use ask_user_question for approval without triggering failure intervention

---

### **IMPORTANT**
**Definition**: Important notes that require attention but are not critical failures.

**Usage**: Used to highlight important information that users should be aware of during workflow execution.

**Examples**:
- **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing
- **IMPORTANT**: Hook file changes require Devin CLI restart

---

## Severity and Priority Markers

### **CRITICAL**
**Definition**: Critical issues or required actions that must be addressed immediately.

**Usage**: Used to mark issues that require immediate attention or actions that are mandatory for workflow success.

**Examples**:
- **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies)
- **CRITICAL**: Hook file changes require Devin CLI restart before testing

---

### **HIGH**
**Definition**: High priority issues that should be addressed soon.

**Usage**: Used to mark significant issues that should be resolved but are not immediately blocking.

**Examples**:
- **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity)
- **HIGH**: High priority issues requiring attention

---

### **MEDIUM**
**Definition**: Medium priority issues for improvement.

**Usage**: Used to mark issues that represent improvements but are not urgent.

**Examples**:
- **MEDIUM**: Best practices improvements (code readability, maintainability)
- **MEDIUM**: Medium priority issues for improvement

---

### **LOW**
**Definition**: Low priority minor suggestions.

**Usage**: Used to mark minor suggestions or improvements that are optional.

**Examples**:
- **LOW**: Minor suggestions (comments, formatting)
- **LOW**: Low priority issues for consideration

---

## Governance Terms

### **BP** (Best Practice)
**Definition**: Established industry standards that must be researched before proceeding with major decisions.

**Usage**: Used to indicate when web search for current best practices is required before making architectural or implementation decisions.

**Examples**:
- **BP**: Web search for best practices before major architectural decisions
- **BP**: Research industry standards before implementation

**Implementation**: When user input is "BP?" (Best Practice?), perform web search for current best practices relevant to the task at hand.

---

### **SSOT** (Single Source of Truth)
**Definition**: Centralized repository for authoritative information that eliminates duplication and inconsistencies.

**Usage**: Used to indicate the authoritative source for specific information, ensuring all agents reference the same accurate data.

**Examples**:
- **SSOT**: Workflow/Terminology_Glossary.md is the SSOT for terminology definitions
- **SSOT**: INDEX.md is the SSOT for directory structure information

**Best Practice**: Establish SSOT for critical information to prevent inconsistencies and ensure all stakeholders work from the same data.

---

## Standard Terms

### **ID**
**Definition**: Unique identifier for workflows, documents, or entities.

**Usage**: Used to provide unique identification for workflows, documents, and other entities within the harness architecture.

**Examples**:
- **ID**: WF-ARCH-001
- **ID**: WF-PLAN-001

---

### **DO**
**Definition**: Required actions that must be performed according to rules.

**Usage**: Used in rule files to specify mandatory actions that agents must perform.

**Examples**:
- **DO**: Verify each function follows single responsibility principle
- **DO**: Check that functions have clear inputs and outputs

---

## Terminology Governance

### Glossary Maintenance
- **Owner**: Architect Agent
- **Update Process**: Architect agent reviews and updates glossary based on new terminology needs
- **Version Control**: All changes tracked with version history
- **Approval**: Architect agent approval required for new terms or definition changes

### Term Addition Process
1. Identify new terminology need from workflow or rule updates
2. Research standard definitions and best practices
3. Draft definition with clear usage examples
4. Add to appropriate section in glossary
5. Update AGENTS.md to reference glossary if needed
6. Update workflows to reference new terms via glossary

### Reference Pattern
All workflows and rules should reference this glossary for terminology understanding:
```markdown
For definition of **{TERM}**, see Workflow/Terminology_Glossary.md
```

---

## Best Practices for Terminology Usage

1. **Consistency**: Always use terminology as defined in this glossary
2. **Reference**: When introducing new terms, reference this glossary
3. **Clarity**: Use defined terms consistently across all harness documents
4. **Updates**: Propagate terminology changes through Architect agent
5. **SSOT**: This glossary is the single source of truth for all terminology

---

**Last Updated**: 2026-07-27
**Version**: 1.0
**Maintained By**: Architect Agent