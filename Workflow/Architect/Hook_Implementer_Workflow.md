# Architect Hook Implementer Workflow

**ID**: WF-ARCH-HOOK-IMPL  
**Owner**: Architect Agent  
**Frequency**: On-demand (per hook implementation)  
**Duration**: Variable (30-120 minutes per hook depending on complexity)  
**Priority**: High
**Workflow Type**: Continuous Operation

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
- **End State**: Hook implemented, tested, documented, and integrated with SovereignAI workflows (workflow loops for next hook)

## Workflow Steps (75 steps)

### Phase 0. Read Architect Rules + Hook Context
- 1. Read Rules/Architect/Architect_Rules.md to understand governance constraints
- 2. Read Docs/Devin Local IDE Documents/Hooks-Guide.md for Devin CLI hook implementation patterns
- 3. Store hook implementation context for reference throughout workflow
- 4. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 5. **PRINT**: "Architect rules loaded - hook implementation context established including Devin CLI hooks guide"

### Phase 1. Select Execution Mode
- 6. Ask user to select execution mode for this workflow using popup menu (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md for execution mode definitions)
- 7. Store selected execution mode for failure handling throughout workflow
- 8. **PRINT**: "Execution mode selected - [Manual/Auto/Complete] will govern failure handling"

### Phase 2. Architect Interaction
- 9. Ask user: "Hi, Architect here - what type of hook would you like to implement?"
- 10. Wait for user to specify hook type and requirements
- 11. Ask user to provide any relevant implementation plan documents or context
- 12. Clarify hook requirements, expected behavior, and integration points
- 13. Document user's hook requirements and rationale
- 14. Apply loaded architect rules to hook implementation requirements
- 15. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
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
- 25. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
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
- 35. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 36. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 37. **PRINT**: "Hook implementation created - script and configuration files updated"

### Phase 5. Restart Devin CLI
- 38. **CRITICAL**: Hook file changes in .devin/ require Devin CLI restart before testing can proceed
- 39. **PRINT**: "CRITICAL: Devin CLI restart required - hook files in .devin/ only load on session start"
- 40. Ask user to restart Devin CLI completely
- 41. Wait for user confirmation of restart completion
- 42. **VALIDATION**: Verify Devin CLI has restarted and hooks are loaded
- 43. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 44. **PRINT**: "Devin CLI restarted - hooks should be loaded and active"

### Phase 6. Test and Validate Hook
- 45. Test hook with real SovereignAI workflows (Architect/Planner workflows) - NOT in isolation
- 46. Test hook with basic operations to verify functionality
- 47. Verify hook achieves expected behavior and performance goals in real scenarios
- 48. Test error handling and edge cases in real workflow contexts
- 49. Verify hook doesn't break existing SovereignAI workflows
- 50. Check compatibility with existing hooks in .devin/hooks.v1.json
- 51. **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing
- 52. **VALIDATION**: Validate hook functionality, integration, and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 53. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 54. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 55. **PRINT**: "Hook testing complete - functionality validated in real SovereignAI workflow scenarios"

### Phase 7. Document Implementation
- 56. Create hook-specific documentation in Docs/Hooks/ or appropriate location
- 57. Document hook behavior, configuration, and integration points
- 58. Update workflow integration notes and known limitations
- 59. Update relevant governance files if hook behavior changes agent capabilities
- 60. **VALIDATION**: Validate documentation completeness and accuracy (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 61. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 62. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 63. **PRINT**: "Documentation complete - hook implementation results documented"

### Phase 8. Final Validation
- 64. Verify implementation matches intended scope from Phase 2
- 65. Ensure no unintended changes outside hook implementation scope
- 66. Validate hook performance in real SovereignAI workflow scenarios
- 67. Review documentation completeness and accuracy
- 68. Ensure compliance with all Architect rules and constraints
- 69. **VALIDATION**: Validate final implementation quality and compliance (see Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md)
- 70. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 71. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 72. **PRINT**: "Final validation complete - hook implementation ready for production use"

### Phase 9. Return to Phase 0 (CONTINUOUS OPERATION)
- 73. **PRINT** "Hook implementation workflow complete - returning to Phase 0 for next hook implementation"
- 74. **PRINT** "Architect agent ready - awaiting next hook implementation request"
- 75. Return to step 1

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
- **Focus**: Execution strategy for systematic hook implementation with validation points

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Hook implementation runtime requirements (Devin CLI restart, hook file locations)
- **Focus**: Runtime infrastructure requirements for hook implementation and testing

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Architect Customization**: Hook implementation validation patterns (functionality testing, integration testing, governance compliance)
- **Focus**: Validation enforcement patterns for hook implementation quality checks