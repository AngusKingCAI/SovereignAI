# Code Execution Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Execute plans created by the Planner agent in strict order with verification after each step.

## Workflow Overview
```
Plan File → Step Execution → Verification → Next Step → Completion
```

## Phase 1: Plan Loading

**Trigger**: Plan file provided by Planner agent  
**Goal**: Load and understand the plan to be executed

**Steps**:
1. **Read Plan File**: Read the plan file from Plans/ directory
2. **Parse Manifest**: Parse the Executor Manifest to understand phases and deliverables
3. **Understand Scope**: Understand in-scope and out-of-scope paths
4. **Check Requirements**: Verify all prerequisites are met
5. **Compliance**: Post `✅ Gate EXEC-1 PASS: Plan loaded, manifest parsed`

**Exit Gate**: Plan fully understood and ready for execution

---

## Phase 2: Step Execution

**Trigger**: Plan loaded successfully  
**Goal**: Execute plan steps in strict order as defined

**Steps**:
1. **Execute Next Step**: Execute the next step in the plan sequence
2. **Follow Instructions**: Follow step instructions exactly as written
3. **Use Universal Rules**: Apply ER1-ER5 editing rules for any file operations
4. **Record Results**: Record step execution results
5. **Compliance**: Post `✅ Gate EXEC-2 PASS: Step {step_number} executed`

**Exit Gate**: Step completed successfully

---

## Phase 3: Step Verification

**Trigger**: Step execution complete  
**Goal**: Verify step execution was successful

**Steps**:
1. **Check Results**: Verify step execution produced expected results
2. **Verify Changes**: Verify file changes match plan expectations
3. **Run Tests**: Run relevant tests if applicable
4. **Document Verification**: Document verification results
5. **Compliance**: Post `✅ Gate EXEC-3 PASS: Step {step_number} verified`

**Exit Gate**: Step verification passed

---

## Phase 4: Next Step or Completion

**Trigger**: Step verification complete  
**Goal**: Move to next step or complete plan execution

**Steps**:
1. **Check Completion**: Check if all plan steps are complete
2. **Continue or Finish**: If steps remain, return to Phase 2. If complete, proceed to Phase 5
3. **Compliance**: Post `✅ Gate EXEC-4 PASS: Plan {percentage}% complete`

**Exit Gate**: Either continue to next step or proceed to completion

---

## Phase 5: Plan Completion

**Trigger**: All plan steps completed  
**Goal**: Finalize plan execution and produce completion artifacts

**Steps**:
1. **Final Verification**: Conduct final verification of all changes
2. **Generate Attestation**: Generate execution attestation document
3. **Cleanup**: Clean up temporary files if needed
4. **Report Completion**: Report plan completion status
5. **Compliance**: Post `✅ Gate EXEC-5 PASS: Plan execution complete`

**Exit Gate**: Plan execution finalized and documented

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)

---

## Stop Conditions

**Halt execution if**:
- Step execution fails
- Step verification fails
- Missing compliance line for any gate
- Plan instructions are unclear or impossible to follow
- Governance rules are violated during execution

---

## Evolution

**This workflow evolves when**:
- Plan structure changes
- Verification requirements change
- Execution patterns change
- Governance rules are updated