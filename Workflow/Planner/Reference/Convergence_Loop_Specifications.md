# Planner Convergence Loop Specifications

**Purpose**: Planner-specific implementation of universal convergence loop patterns for Round Table review cycles.

## Universal Pattern Reference

See Workflow/Workflow_Reference/Convergence_Loop_Patterns.md for universal convergence loop patterns including:
- Universal convergence loop pattern and logic
- Universal convergence criteria definitions
- Universal loop caps and escalation procedures

## Internal Convergence Loop

**Loop Structure**: Phase 4 → Phase 5 → Phase 4 (repeat until Internal Round Table passes)

**Convergence Logic**:
1. Run Phase 4 (Internal Round Table)
2. If Phase 4 PASSES → Proceed to Phase 6 (External Round Table)
3. If Phase 4 FAILS → Proceed to Phase 5 (Apply Findings)
4. At end of Phase 5 → Return to Phase 4
5. Repeat until Internal Round Table achieves convergence

**Convergence Criteria**:
- Findings count decreasing across iterations
- Panelist similarity increasing across iterations
- CRITICAL and HIGH findings resolved
- Plan quality rubric scores improving

**Loop Exit Condition**: Internal Round Table achieves convergence (findings ≤5, panelist agreement ≥80%).

**Loop Cap**: Maximum 5 internal iterations.

**On Convergence**: Proceed to Phase 6 (External Round Table).

**On Loop Cap Reached**: Stop and escalate to user decision.

## External Convergence Loop

**Loop Structure**: Phase 6 → Phase 5 → Phase 6 (repeat until External Round Table passes)

**Convergence Logic**:
1. Run Phase 6 (External Round Table)
2. If Phase 6 PASSES (≥90 score or 70-89 with rationale) → Proceed to Phase 7 (Final Validation)
3. If Phase 6 FAILS (<70 score) → Proceed to Phase 5 (Apply Findings)
4. At end of Phase 5 → Return to Phase 6
5. Repeat until External Round Table achieves convergence

**Convergence Criteria**:
- Quality score ≥90 (clean pass) OR 70-89 with documented rationale
- Findings count decreasing across iterations
- Panelist similarity increasing across iterations
- CRITICAL and HIGH findings resolved

**Loop Exit Condition**: External Round Table achieves clean pass (≥90) or acceptable pass (70-89 with rationale).

**Loop Cap**: Maximum 3 external iterations.

**On Convergence**: Proceed to Phase 7 (Final Validation).

**On Loop Cap Reached**: Stop and escalate to user decision.