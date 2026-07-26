# Architect Hook Implementer Workflow

**ID**: WF-ARCH-HOOK-IMPL  
**Owner**: Architect Agent  
**Frequency**: On-demand (per hook implementation)  
**Duration**: Variable (30-120 minutes per hook depending on complexity)  
**Priority**: High
**Workflow Type**: Single-Execution (executes once and terminates)

## Purpose
Systematic implementation and testing of hooks for SovereignAI harness using Devin CLI, ensuring each hook is implemented, tested extensively, and validated before proceeding to the next hook. This workflow is generalized for any hook implementation type (token optimization, governance enforcement, logging, automation, etc.).

## Scope
**Devin CLI Hooks Only**: Implementation of hooks in .devin/hooks.v1.json and Scripts/ for various purposes (token optimization, governance enforcement, logging, automation, etc.)

## Roles and Owners
- **Architect Agent**: Executes hook implementation, testing, validation, and documentation
- **User**: Approves implementation plan, performs Devin CLI restart, validates results
- **Governance System**: Validation and compliance enforcement with Architect rules

## Trigger and End State
- **Trigger**: User requests hook implementation OR Architect initiates hook development project
- **End State**: Hook implemented, tested, documented, and integrated with SovereignAI workflows

## Workflow Steps (70 steps)

### Phase 0. Read Architect Rules + Hook Context
- 1. Read Rules/Architect/Architect_Rules.md to understand governance constraints
- 2. Read Docs/Devin Local IDE Documents/Hooks-Guide.md for Devin CLI hook implementation patterns
- 3. Store hook implementation context for reference throughout workflow
- 4. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 5. **PRINT**: "Architect rules loaded - hook implementation context established including Devin CLI hooks guide"

### Phase 1. Select Execution Mode
- 6. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at failures for human oversight
  - **Auto**: Don't continue on failures (auto-stop on errors)
  - **Complete**: Continue past failures (ignore all errors)
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT**: "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 9. Ask user: "Hi, Architect here - what type of hook would you like to implement?"
- 10. Wait for user to specify hook type and requirements
- 11. Ask user to provide any relevant implementation plan documents or context
- 12. Clarify hook requirements, expected behavior, and integration points
- 13. Document user's hook requirements and rationale
- 14. Apply loaded architect rules to hook implementation requirements
- 15. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 16. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 17. **PRINT**: "Hook requirements defined - {Hook Type} specified for implementation"

### Phase 3. Research Best Practices
- 18. Check Docs/Code/ for relevant hook implementation examples
- 19. **BEST PRACTICES WEB SEARCH**: Web search for selected hook implementation patterns with complete working examples (per Architect_Rules.md)
- 20. **Search Focus**: Look for examples that include both Python script implementation AND hooks.v1.json configuration files
- 21. Research Devin CLI hook compatibility and requirements for selected hook type
- 22. Analyze SovereignAI workflow requirements and integration points
- 23. Gather multiple implementation approaches from web search and local research
- 24. Ensure proposed solutions comply with governance rules
- 25. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 26. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 27. **PRINT**: "Researching best practices - checking code documentation for hook examples"
- 28. **PRINT**: "Best practices web search initiated - required before hook implementation"
- 29. **PRINT**: "Research complete - gathered complete working examples with Python scripts and hooks.v1.json configurations"

### Phase 4. Create Hook Implementation
- 30. Create hook script in Scripts/ following script categorization rules
- 31. Update .devin/hooks.v1.json with hook configuration using proper JSON format (per Hooks-Guide.md)
- 32. Ensure proper error handling and logging in hook script
- 33. Follow Architect rules for script placement and categorization
- 34. **VALIDATION**: Validate hook script syntax and hook configuration format (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 35. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 36. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 37. **PRINT**: "Hook implementation created - script and configuration files updated"

### Phase 5. Test and Validate Hook
- 38. **PRINT**: "CRITICAL: Hook file changes in .devin/ require Devin CLI restart (per Hooks-Guide.md)"
- 39. Ask user to restart Devin CLI completely
- 40. Wait for user confirmation of restart completion
- 41. Test hook with basic operations (simple commands, file operations)
- 42. Test hook with SovereignAI workflows (Architect/Planner workflows)
- 43. Verify hook achieves expected behavior and performance goals
- 44. Test error handling and edge cases
- 45. Verify hook doesn't break existing SovereignAI workflows
- 46. Check compatibility with existing hooks in .devin/hooks.v1.json
- 47. **VALIDATION**: Validate hook functionality, integration, and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 48. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 49. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 50. **PRINT**: "Hook testing complete - functionality validated and performance verified"

### Phase 6. Document Implementation
- 51. Create hook-specific documentation in Docs/Hooks/ or appropriate location
- 52. Document hook behavior, configuration, and integration points
- 53. Update workflow integration notes and known limitations
- 54. Update relevant governance files if hook behavior changes agent capabilities
- 55. **VALIDATION**: Validate documentation completeness and accuracy (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 56. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 57. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 58. **PRINT**: "Documentation complete - hook implementation results documented"

### Phase 7. Final Validation
- 59. Verify implementation matches intended scope from Phase 2
- 60. Ensure no unintended changes outside hook implementation scope
- 61. Validate hook performance in real SovereignAI workflow scenarios
- 62. Review documentation completeness and accuracy
- 63. Ensure compliance with all Architect rules and constraints
- 64. **VALIDATION**: Validate final implementation quality and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 65. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 66. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 67. **PRINT**: "Final validation complete - hook implementation ready for production use"

### Phase 8. Workflow Termination
- 68. **PRINT** "Hook implementation workflow complete - workflow terminated"
- 69. **PRINT** "Architect agent ready - awaiting next hook implementation request"
- 70. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Hook implementation quality criteria (functionality, performance, compliance)
- **Focus**: Hook implementation quality assessment with behavior verification metrics

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific hook implementation responsibilities
- **Focus**: Architect agent responsibilities for systematic hook implementation and testing

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Hook performance metrics (behavior accuracy, execution overhead, compatibility)
- **Focus**: Performance measurement of hook implementations with specific behavior metrics

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
- **Architect Customization**: Hook implementation quota patterns (resource monitoring, performance budgeting)
- **Focus**: Quota handling patterns for measuring and optimizing hook performance

### Template Usage
- **Universal Framework**: Workflow/Workflow_Reference/Template_Usage_Guidelines.md
- **Architect Customization**: Hook implementation template customization (workflow type selection, phase adaptation)
- **Focus**: Template usage patterns for single-execution utility workflows with systematic implementation phases