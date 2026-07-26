# Architect Hook Implementer Workflow

**ID**: WF-ARCH-HOOK-IMPL  
**Owner**: Architect Agent  
**Frequency**: On-demand (per hook implementation)  
**Duration**: Variable (30-120 minutes per hook depending on complexity)  
**Priority**: High
**Workflow Type**: Single-Execution (executes once and terminates)

## Purpose
Systematic implementation and testing of token optimization hooks for SovereignAI harness using Devin CLI, ensuring each hook is implemented, tested extensively, and validated before proceeding to the next hook.

## Scope
**Token Optimization Hooks Only**: Implementation of hooks in .devin/hooks.v1.json and Scripts/TokenOptimization/ for Devin CLI token reduction

## Roles and Owners
- **Architect Agent**: Executes hook implementation, testing, validation, and documentation
- **User**: Approves implementation plan, performs Devin CLI restart, validates results
- **Governance System**: Validation and compliance enforcement with Architect rules

## Trigger and End State
- **Trigger**: User requests hook implementation OR Architect initiates token optimization project
- **End State**: Hook implemented, tested, documented, and integrated with SovereignAI workflows

## Workflow Steps (72 steps)

### Phase 0. Read Architect Rules + Hook Context
- 1. Read Rules/Architect/Architect_Rules.md to understand governance constraints
- 2. Read Workflow/Architect/Reference/Workflow_Template.md for workflow structure patterns
- 3. Read Docs/Token_Optimization_Hooks_Implementation_Plan.md for implementation priority
- 4. Read Docs/Devin Local IDE Documents/Hooks-Guide.md for Devin CLI hook implementation patterns
- 5. Store hook implementation context for reference throughout workflow
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT**: "Architect rules loaded - hook implementation context established including Devin CLI hooks guide"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at failures for human oversight
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- 9. Store selected execution mode for failure handling throughout workflow
- 10. **PRINT**: "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 11. Ask user: "Hi, Architect here - which hook would you like to implement for token optimization?"
- 12. Wait for user to specify hook or ask for implementation plan review
- 13. Present hook options from Docs/Token_Optimization_Hooks_Implementation_Plan.md using popup menu:
  - **RTK Integration** (Phase 1, Hook #1 - proven, 60-90% savings)
  - **TokenJuice Integration** (Phase 1, Hook #2 - beta, variable savings)
  - **File Read Caching** (Phase 2, Hook #3 - adaptation required, 30-50% savings)
  - **PostToolUse Compression** (Phase 2, Hook #4 - uncertain support, 50-80% savings)
- 14. Clarify hook selection if needed
- 15. Document user's hook selection and rationale
- 16. Apply loaded architect rules to hook implementation requirements
- 17. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 18. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 19. **PRINT**: "Hook selection complete - {Hook Name} selected for implementation"

### Phase 3. Research Best Practices
- 20. Check Docs/Code/ for relevant hook implementation examples
- 21. **BEST PRACTICES WEB SEARCH**: Web search for selected hook implementation patterns and real-world examples (per Architect_Rules.md)
- 22. Research Devin CLI hook compatibility and requirements for selected hook
- 23. Analyze SovereignAI workflow requirements and integration points
- 24. Gather multiple implementation approaches from web search and local research
- 25. Ensure proposed solutions comply with governance rules
- 26. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 27. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 28. **PRINT**: "Researching best practices - checking code documentation for hook examples"
- 29. **PRINT**: "Best practices web search initiated - required before hook implementation"
- 30. **PRINT**: "Research complete - gathered implementation approaches and compatibility analysis"

### Phase 4. Create Hook Implementation
- 31. Create hook script in Scripts/TokenOptimization/ following script categorization rules
- 32. Update .devin/hooks.v1.json with hook configuration using proper JSON format (per Hooks-Guide.md)
- 33. Ensure proper error handling and logging in hook script
- 34. Follow Architect rules for script placement and categorization
- 35. **VALIDATION**: Validate hook script syntax and hook configuration format (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 36. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 37. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 38. **PRINT**: "Hook implementation created - script and configuration files updated"

### Phase 5. Test and Validate Hook
- 39. **PRINT**: "CRITICAL: Hook file changes in .devin/ require Devin CLI restart (per Hooks-Guide.md)"
- 40. Ask user to restart Devin CLI completely
- 41. Wait for user confirmation of restart completion
- 42. Test hook with basic operations (simple commands, file operations)
- 43. Test hook with SovereignAI workflows (Architect/Planner workflows)
- 44. Verify token savings are achieved through measurement
- 45. Test error handling and edge cases
- 46. Verify hook doesn't break existing SovereignAI workflows
- 47. Check compatibility with existing hooks in .devin/hooks.v1.json
- 48. **VALIDATION**: Validate hook functionality, integration, and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 49. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 50. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 51. **PRINT**: "Hook testing complete - functionality validated and token savings measured"

### Phase 6. Document Implementation
- 52. Update Docs/Token_Optimization_Hooks_Implementation_Plan.md with implementation status
- 53. Document token savings achieved with measurements
- 54. Update workflow integration notes and known limitations
- 55. Create hook-specific documentation in Docs/TokenOptimization/
- 56. Update relevant governance files if hook behavior changes agent capabilities
- 57. **VALIDATION**: Validate documentation completeness and accuracy (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 58. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 59. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 60. **PRINT**: "Documentation complete - implementation results and savings documented"

### Phase 7. Final Validation
- 61. Verify implementation matches intended scope from Phase 2
- 62. Ensure no unintended changes outside hook implementation scope
- 63. Validate hook performance in real SovereignAI workflow scenarios
- 64. Review documentation completeness and accuracy
- 65. Ensure compliance with all Architect rules and constraints
- 66. **VALIDATION**: Validate final implementation quality and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 67. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 68. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 69. **PRINT**: "Final validation complete - hook implementation ready for production use"

### Phase 8. Workflow Termination
- 70. **PRINT** "Hook implementation workflow complete - workflow terminated"
- 71. **PRINT** "Architect agent ready - awaiting next hook implementation request"
- 72. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Hook implementation quality criteria (functionality, performance, compliance)
- **Focus**: Hook implementation quality assessment with token savings metrics

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific hook implementation responsibilities
- **Focus**: Architect agent responsibilities for systematic hook implementation and testing

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Hook performance metrics (token savings, execution overhead, compatibility)
- **Focus**: Performance measurement of token optimization hooks with specific savings metrics

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Hook implementation state tracking (implementation status, test results, validation status)
- **Focus**: State management for hook implementation progress and restart coordination

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Hook implementation execution patterns (one-hook-at-a-time, extensive testing)
- **Focus**: Execution strategy for systematic hook implementation with validation gates

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Hook implementation runtime requirements (Devin CLI restart, hook file locations)
- **Focus**: Runtime infrastructure requirements for hook implementation and testing

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Architect Customization**: Hook implementation validation patterns (functionality testing, integration testing, governance compliance)
- **Focus**: Validation enforcement patterns for hook implementation quality gates

### Convergence Loops
- **Universal Framework**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md
- **Architect Customization**: Hook implementation iteration patterns (test-fix-retest cycles)
- **Focus**: Convergence patterns for hook implementation testing and validation iterations

### Quota Handling
- **Universal Framework**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md
- **Architect Customization**: Hook implementation quota patterns (token budget monitoring, savings measurement)
- **Focus**: Quota handling patterns for measuring and optimizing token savings from hooks

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Architect Customization**: Hook implementation template customization (workflow type selection, phase adaptation)
- **Focus**: Template usage patterns for single-execution utility workflows with systematic implementation phases