# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules, enforced through the hook-based gate system for automatic permission validation and audit logging.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via hooks (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps (91 steps)
### Phase 0. Read Architect Rules
- 1. Read Rules/Architect/Architect_Rules.md to load current governance constraints
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 5. **PRINT** "Architect rules loaded from Rules/Architect/Architect_Rules.md"

### Phase 1. Select Execution Mode
- 6. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at failures for human oversight
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 9. Ask user: "Hi, Architect here - how can I help you today?"
- 10. Wait for user to specify their architectural task or question
- 11. Clarify the task if needed
- 12. Review user request and check local research using index files before web search
- 13. Apply loaded architect rules to task requirements
- 14. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT** "Initiating architect interaction - awaiting user task specification"

### Phase 3. Research Best Practices
- 17. Check code documentation (Docs/Code/) for examples relevant to the specific type of code being implemented (Python, JSON, YAML, Bash, etc.)
- 18. **BEST PRACTICES WEB SEARCH**: Web search must be performed before major architectural decisions (per Architect_Rules.md). Research industry standards and established patterns for the architectural approach being considered.
- 19. Gather multiple approaches and patterns from web search and local research
- 20. Ensure proposed solutions comply with governance rules
- 21. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 22. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 23. **PRINT** "Researching best practices - checking code documentation for relevant examples"
- 24. **PRINT** "Best practices web search initiated - required before major architectural decisions"
- 25. **PRINT** "Research complete - gathered multiple implementation approaches from industry standards"

### Phase 4. Generate Options
- 27. Generate 2-4 implementation options based on research
- 28. **VALIDATION**: Validate options against viable option criteria (see Workflow/Architect/Reference/Option_Evaluation_Framework.md)
- 29. **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- 30. **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu for selection
- 31. **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md
- 32. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 33. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 34. **PRINT**: "Generating implementation options - applying viable option criteria"
- 35. **PRINT**: "Options generated - presenting with impact, effort, and risk metrics"
- 36. **PRINT**: "Architect opinion provided - recommending optimal approach based on analysis"

### Phase 5. Specify Implementation
- 37. Create detailed specification for selected approach
- 37. **VALIDATION**: Validate specification completeness and compliance (see Workflow/Architect/Reference/Option_Evaluation_Framework.md)
- 38. **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu (see Workflow/Architect/Reference/Implementation_Mode_Patterns.md)
- 39. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 40. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 41. **PRINT** "Creating detailed implementation specification - defining architecture and constraints"
- 42. **PRINT** "Specification complete - verifying file placement compliance with directory structure"
- 43. **PRINT** "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### Phase 6. Implement (One Function at a Time)
- 45. Build exactly one function at a time, test immediately
- 46. Present function and test result to user after each successful test
- 47. Wait for explicit user confirmation before proceeding
- 48. Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The gate system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (ungated) to pause for approval without triggering failure intervention.
- 49. When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- 50. Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- 51. When function fails, apply selected execution mode (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 52. **RETRY LOGIC**: For Auto and Complete modes, implement configurable retry with exponential backoff (max 3 retries)
- 53. **STATUS TRACKING**: Update workflow status to "phase_6_in_progress" during implementation, "phase_6_complete" when finished
- 54. **PRINT**: "Implementing function - building one function at a time per architect rules"
- 55. **PRINT**: "Function test complete - presenting test results to user for confirmation"
- 56. **PRINT**: "Awaiting user confirmation - treating function as locked once confirmed"
- 57. **PRINT**: "Function implementation complete - proceeding to next function"

### Phase 7. Verify Compliance
- 58. Verify implementation matches specification
- 59. Run verification tests
- 60. Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- 61. Never skip compliance checks
- 62. Always verify architectural compliance before proceeding
- 63. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 64. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 65. **PRINT**: "Verifying compliance - checking implementation against specification"
- 66. **PRINT**: "Running verification tests - ensuring all success criteria met"
- 67. **PRINT**: "Constitutional compliance verified - implementation aligns with architect rules"
- 68. **PRINT**: "Architectural compliance complete - ready to proceed"

### Phase 8. Document
- 69. Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
  - AGENTS.md (if agent capabilities change)
- 70. Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- 71. Never place files uncategorized
- 72. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 73. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 74. **PRINT**: "Updating governance documentation - modifying relevant agent files"
- 75. **PRINT**: "Documentation categorization verified - all files properly categorized per architect rules"
- 76. **PRINT**: "Documentation complete - governance files updated"

### Phase 9. Final Validation
- 77. Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- 78. Confirm governance file placement compliance per INDEX.md
- 79. Validate no unintended changes outside the target area
- 80. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 81. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 82. **PRINT**: "Final validation initiated - verifying implementation scope compliance"
- 83. **PRINT**: "Rules verification complete - template and formatting validated"
- 84. **PRINT**: "Workflow verification complete - structure and executability confirmed"
- 85. **PRINT**: "Scripts verification complete - functionality validated"
- 86. **PRINT**: "Documentation verification complete - categorization confirmed"
- 87. **PRINT**: "Governance file placement verified - compliance with INDEX.md confirmed"
- 88. **PRINT**: "Unintended changes check complete - no changes outside target area detected"

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

### Quality Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Metrics_Framework.md
- **Architect Customization**: Infrastructure design efficiency, architectural compliance rate, governance system reliability
- **Focus**: Architectural efficiency metrics and compliance assessment

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Implementation state tracking, execution mode state, compliance validation results
- **Focus**: Implementation progress, gate validation results, execution mode tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Hook-based validation, execution mode handling patterns
- **Focus**: Architectural strategies and execution mode-based iteration