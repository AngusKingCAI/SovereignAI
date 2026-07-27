# Planner Workflow Overview

## Best Practices

This workflow follows AI planning best practices with:
- **Incremental verification**: Validation after each phase to catch errors close to source
- **Dual-validation governance**: Early validation (Phase 3) + final validation (Phase 7)
- **Convergence-based iteration**: Internal and external Round Table loops until convergence
- **Incremental logging**: Save reviews as received for audit trail and Reviewer analysis
- **Role separation**: Planner creates plans, Reviewer analyzes quality (separate agent workflow)
- **Domain-split personas**: Panelists adopt specific domain expertise for focused review
- **Web search verification**: All panelists must verify findings against current best practices
- **Quota handling**: State persistence + resume pattern for handling quota exhaustion
- **Plan delivery**: Final plans saved to Plans/ directory for executor execution
- **Batch processing**: Plans organized in batches of 5 with scan plans for issue resolution

## Phase Structure

1. **Phase 0**: Read Planner Rules + Governance + Validate
2. **Phase 1**: Select Execution Mode
3. **Phase 2**: Planner Interaction
4. **Phase 3**: Plan Creation + Validate (includes plan type determination)
5. **Phase 4**: Internal Round Table + Validate (Convergence Loop)
6. **Phase 5**: Apply Findings + Validate (Loop Back to Phase 4)
7. **[Loop 4→5 until Internal passes - max 5 iterations]**
8. **Phase 6**: External Round Table + Validate (Convergence Loop)
9. **Phase 5**: Apply Findings + Validate (Loop Back to Phase 6)
10. **[Loop 6→5 until External passes - max 3 iterations]**
11. **Phase 7**: Final Validation + Save Plan to Plans/ + Delivery Authorization
12. **Phase 8**: Session Logging + Validate
13. **Next Plan**: Continue to next plan in batch sequence

## Template References

- **Plan Creation**: Workflow/Planner/Templates/Plan_Template.md (plan structure and format)
- **Brief Creation**: Workflow/Planner/Templates/Plan_Brief_Template.md (review brief structure)
- **Prompt Instructions**: Workflow/Planner/Templates/Plan_Prompt_Template.md (persona adoption instructions)
- **Plan Batch Specifications**: Workflow/Planner/Reference/Plan_Batch_Specifications.md (batch processing and scan plan patterns)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (universal framework)
- **Validation System**: Workflow/Planner/Reference/Validation_System_Specifications.md (planner-specific validation definitions)
- **Convergence Loops**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md (universal pattern) and Workflow/Planner/Reference/Convergence_Loop_Specifications.md (planner-specific implementation)
- **Delivery Authorization**: Workflow/Planner/Reference/Delivery_Authorization_Specifications.md (planner-specific)
- **Role Responsibilities**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md (universal framework) and Workflow/Planner/Reference/Role_Responsibilities.md (planner-specific)
- **Performance Metrics**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md (universal framework)
- **State Management**: Workflow/Workflow_Reference/State_Management_Guidelines.md (universal framework)
- **Quota Handling**: Workflow/Workflow_Reference/Quota_Handling_Patterns.md (universal framework)

## Logging Structure

- Round Table reviews: Incremental logging as received (Logs/Planner/Roundtable/Internal/ and Logs/Planner/Roundtable/External/)
- Plan iterations: Incremental logging (Logs/Planner/)
- Validation results: JSON logging (Logs/Planner/validation-completions/ and Logs/Planner/validation-failures/)
- Session: Final consolidated logging at Phase 8