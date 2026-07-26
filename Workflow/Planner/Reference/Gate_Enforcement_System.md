# Planner Gate System Specifications

**Purpose**: Planner-specific gate definitions and implementation details for plan quality control and compliance enforcement.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md for universal gate enforcement patterns including:
- Universal gating rules and compliance requirements
- Universal gate pattern (perform → document → verify → proceed)
- Universal gate enforcement framework

## Planner Gate Specifications

### All 6 Gates Must Pass

1. **Gate 1**: Plan Structure Validation - Required sections and metadata present
2. **Gate 2**: Scope Compliance Validation - Planning content only, no implementation details
3. **Gate 3**: Dependency Analysis Validation - Dependency graph valid, no circular dependencies
4. **Gate 4**: Quality Assessment - Plan quality rubric evaluation
5. **Gate 5**: Landmine Screening Verification - No blocking landmines (passes with warning if file not found)
6. **Gate 6**: Infrastructure Scope Validation - Infrastructure scope compliance verified

## Gate System Execution

### Early Gate Validation (Phase 3)
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev}.md phase3-early-validation
```

### Revision Gate Validation (Phase 5)
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev+1}.md phase5-revision-validation
```

### Final Gate Validation (Phase 7)
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{final-rev}.md phase7-final-validation
```

## Gate System Reference

- **Universal Pattern**: Workflow/Workflow_Reference/Gate_Enforcement_Patterns.md (universal gate enforcement framework)
- **Gate System**: Scripts/Planner/Gates/run-all-planner-gates.sh (automated validation)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (universal framework)
- **Compliance**: Rules/Planner/Planner_Rules.md (planning rules and constraints)
- **Delivery Authorization**: Workflow/Planner/Reference/Delivery_Authorization_Specifications.md (delivery process)