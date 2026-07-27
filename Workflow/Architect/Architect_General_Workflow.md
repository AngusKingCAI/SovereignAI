# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High
**Workflow Type**: Continuous Operation

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules, enforced through the validation-based governance system for automatic permission validation and audit logging.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via validation system (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps (92 steps)
### Phase 0. Read Architect Rules
- 1. Read Rules/Architect/Architect_Rules.md to load current governance constraints
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Parse YAML frontmatter and rule definitions for implementation guidance
- 4. Store rule context for reference throughout workflow execution
- 5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 6. **PRINT** "Architect rules loaded from Rules/Architect/Architect_Rules.md"

### Phase 1. Select Execution Mode
- 6. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 9. Ask user: "Hi, Architect here - how can I help you today?"
- 10. Wait for user to specify their architectural task or question
- 11. Clarify the task if needed
- 12. Review user request and check local research using index files before web search
- 13. Apply loaded architect rules to task requirements
- 14. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT** "Initiating architect interaction - awaiting user task specification"

### Phase 3. Research Best Practices
- 17. Check code documentation (Docs/Code/) for examples relevant to the specific type of code being implemented (Python, JSON, YAML, Bash, etc.)
- 18. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major architectural decisions (per Rules/Architect/Architect_Rules.md). Research industry standards and established patterns for the architectural approach being considered.
- 19. Gather multiple approaches and patterns from web search and local research
- 20. Ensure proposed solutions comply with governance rules
- 21. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 22. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 23. **PRINT** "Researching best practices - checking code documentation for relevant examples"
- 24. **PRINT** "Best practices web search initiated - required before major architectural decisions"
- 25. **PRINT** "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. Generate Options
- 26. Generate 2-4 implementation options based on research
- 27. **VALIDATION**: Validate options against viable option criteria (see Workflow/Architect/Reference/Option_Evaluation_Framework.md)
- 28. **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- 29. **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu for selection
- 30. **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md
- 31. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 32. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 33. **PRINT**: "Generating implementation options - applying viable option criteria"
- 34. **PRINT**: "Options generated - presenting with impact, effort, and risk metrics"
- 35. **PRINT**: "Architect opinion provided - recommending optimal approach based on analysis"

### Phase 5. Specify Implementation
- 36. Create detailed specification for selected approach
- 37. **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications using popup menu with [Confirm/Modify] options
- 38. **VALIDATION**: Validate specification completeness and compliance (see Workflow/Architect/Reference/Option_Evaluation_Framework.md)
- 39. **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu (see Workflow/Architect/Reference/Implementation_Mode_Patterns.md)
- 40. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 41. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 42. **PRINT** "Creating detailed implementation specification - defining architecture and constraints"
- 43. **PRINT** "Specification complete - verifying file placement compliance with directory structure"
- 44. **PRINT** "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### Phase 6. Implement (One Function at a Time)
- 45. Build exactly one function at a time, test immediately
- 46. Present function and test result to user after each successful test
- 47. Wait for explicit user confirmation before proceeding
- 48. Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (unvalidated) to pause for approval without triggering failure intervention.
- 49. When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- 50. Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- 51. When function fails, apply selected execution mode (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 52. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress" during implementation, "phase_6_complete" when finished
- 53. **PRINT**: "Implementing function - building one function at a time per architect rules"
- 54. **PRINT**: "Function test complete - presenting test results to user for confirmation"
- 55. **PRINT**: "Awaiting user confirmation - treating function as locked once confirmed"
- 56. **PRINT**: "Function implementation complete - proceeding to next function"

### Phase 7. Verify Compliance
- 57. Verify implementation matches specification
- 58. Run verification tests
- 59. Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- 60. Never skip compliance checks
- 61. Always verify architectural compliance before proceeding
- 62. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 63. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 64. **PRINT**: "Verifying compliance - checking implementation against specification"
- 65. **PRINT**: "Running verification tests - ensuring all success criteria met"
- 66. **PRINT**: "Constitutional compliance verified - implementation aligns with architect rules"
- 67. **PRINT**: "Architectural compliance complete - ready to proceed"

### Phase 8. Document
- 68. Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/Workflow_Reference/Workflow_Template.md (if template changes)
  - AGENTS.md (if agent capabilities change)
- 69. Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- 70. Never place files uncategorized
- 71. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 72. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 73. **PRINT**: "Updating governance documentation - modifying relevant agent files"
- 74. **PRINT**: "Documentation categorization verified - all files properly categorized per architect rules"
- 75. **PRINT**: "Documentation complete - governance files updated"

### Phase 9. Final Validation
- 76. Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- 77. Confirm governance file placement compliance per INDEX.md
- 78. Validate no unintended changes outside the target area
  - Run git status to check for changes
  - If unintended changes detected, present popup menu with [Accept Changes/Restore Files] options
  - Only attempt restore after user explicitly selects "Restore Files" option
- 79. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 80. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 81. **PRINT**: "Final validation initiated - verifying implementation scope compliance"
- 82. **PRINT**: "Rules verification complete - template and formatting validated"
- 83. **PRINT**: "Workflow verification complete - structure and executability confirmed"
- 84. **PRINT**: "Scripts verification complete - functionality validated"
- 85. **PRINT**: "Documentation verification complete - categorization confirmed"
- 86. **PRINT**: "Governance file placement verified - compliance with INDEX.md confirmed"
- 87. **PRINT**: "Unintended changes check complete - no changes outside target area detected"

### Phase 10. Return to Phase 0
- 89. **PRINT** "Workflow cycle complete - returning to Phase 0 for next architectural task"
- 90. **PRINT** "Architect agent ready - awaiting next user request"
- 91. Return to step 1

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Architect-specific infrastructure design quality criteria
- **Focus**: Infrastructure design quality assessment with architectural-specific criteria

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific role definitions for infrastructure design
- **Focus**: Infrastructure creation, governance framework implementation, compliance enforcement

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Infrastructure design efficiency, architectural compliance rate, governance system reliability
- **Focus**: Architectural efficiency metrics and compliance assessment

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Hook system status and runtime directory requirements
- **Focus**: Runtime paths and infrastructure requirements for workflow execution

### Workflow Template
- **Architect Tool**: Workflow/Workflow_Reference/Workflow_Template.md
- **Architect Customization**: Architect's template for creating workflows
- **Focus**: Template usage for workflow creation and maintenance