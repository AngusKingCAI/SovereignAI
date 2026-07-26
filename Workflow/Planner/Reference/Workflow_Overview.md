# Planner Workflow Overview

## Best Practices

This workflow follows AI planning best practices with:
- **Incremental verification**: Validation after each phase to catch errors close to source
- **Dual-gate governance**: Early gate validation (Phase 3) + final gate validation (Phase 7)
- **Convergence-based iteration**: Internal and external Round Table loops until convergence
- **Incremental logging**: Save reviews as received for audit trail and Reviewer analysis
- **Role separation**: Planner creates plans, Reviewer analyzes quality (separate agent workflow)
- **Domain-split personas**: Panelists adopt specific domain expertise for focused review
- **Web search verification**: All panelists must verify findings against current best practices

## Phase Structure

1. **Phase 0**: Read Planner Rules + Validate
2. **Phase 1**: Select Execution Strategy
3. **Phase 2**: Read Governance + Validate
4. **Phase 3**: Plan Creation + Early Gate Validation
5. **Phase 4**: Internal Round Table + Incremental Logging + Validate
6. **Phase 5**: Apply Findings + Validate
7. **[Loop 4→5 until Internal passes]**
8. **Phase 6**: External Round Table + Incremental Logging + Validate
9. **Phase 5**: Apply Findings + Validate
10. **[Loop 6→5 until External passes]**
11. **Phase 7**: Final Gate Delivery + Validate
12. **Phase 8**: Session Logging + Validate
13. **Phase 9**: Return to Phase 0

## Template References

- **Plan Creation**: Workflow/Planner/Templates/Plan_Template.md (plan structure and format)
- **Brief Creation**: Workflow/Planner/Templates/Plan_Brief_Template.md (review brief structure)
- **Prompt Instructions**: Workflow/Planner/Templates/Plan_Prompt_Template.md (persona adoption instructions)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (universal framework)
- **Gate System**: Workflow/Planner/Reference/Gate_Enforcement_System.md (planner-specific gate definitions)
- **Convergence Loops**: Workflow/Workflow_Reference/Convergence_Loop_Patterns.md (universal pattern) and Workflow/Planner/Reference/Convergence_Loop_Specifications.md (planner-specific implementation)
- **Delivery Authorization**: Workflow/Planner/Reference/Delivery_Authorization_Specifications.md (planner-specific)
- **Role Responsibilities**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md (universal framework) and Workflow/Planner/Reference/Role_Responsibilities.md (planner-specific)
- **Quality Metrics**: Workflow/Workflow_Reference/Quality_Metrics_Framework.md (universal framework)
- **State Management**: Workflow/Workflow_Reference/State_Management_Guidelines.md (universal framework)

## Logging Structure

- Round Table reviews: Incremental logging as received (Logs/Roundtable/Devin/ and Logs/Roundtable/External/)
- Plan iterations: Incremental logging (Logs/Planner/)
- Gate results: JSON logging (Logs/Planner/gate-completions/ and Logs/Planner/gate-failures/)
- Session: Final consolidated logging at Phase 8