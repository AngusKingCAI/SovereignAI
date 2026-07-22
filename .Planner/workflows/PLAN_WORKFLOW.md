# Plan Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Create original plans for the SovereignAI project based on Researcher design documents and requirements. Plans are executed by the Executor agent.

## Workflow Overview
```
Researcher Design Documents → Plan Creation → Round Table Review → Reviewer Pattern Analysis → Planner Rule Integration → Executor
```

## Phase 1: Input Assessment

**Trigger**: User provides requirements or Researcher provides design documents  
**Goal**: Understand the scope and requirements for the plan

**Steps**:
1. **Read Design Documents**: Read Researcher design documents (if available)
2. **Assess Requirements**: Understand user requirements and constraints
3. **Scope Definition**: Define in-scope and out-of-scope deliverables
4. **Dependencies**: Identify dependencies and integration points
5. **Compliance**: Post `✅ Gate PLAN-1 PASS: Requirements assessed, scope defined`

**Exit Gate**: Requirements fully understood and documented

---

## Phase 2: Plan Structure Design

**Trigger**: Input assessment complete  
**Goal**: Design plan structure following PR1-PR15 and GR1-GR5

**Steps**:
1. **Header Design**: Create plan header with Vision principles, PR rules reference
2. **Manifest Design**: Design Executor Manifest with phases, deliverables, gates
3. **Phase Planning**: Break down work into executable phases
4. **Quality Gates**: Define verification gates for each phase
5. **Compliance**: Post `✅ Gate PLAN-2 PASS: Plan structure designed, gates defined`

**Exit Gate**: Plan structure follows PR1-PR15 requirements

---

## Phase 3: Plan Drafting

**Trigger**: Plan structure designed  
**Goal**: Draft complete plan with detailed steps

**Steps**:
1. **Header Completion**: Complete plan header with all required sections
2. **Manifest Completion**: Complete Executor Manifest with all required information
3. **Phase Details**: Fill in detailed steps for each phase
4. **Path Verification**: Ensure all paths are repo-relative (PR2)
5. **Compliance**: Post `✅ Gate PLAN-3 PASS: Plan drafted, paths verified`

**Exit Gate**: Plan draft complete with all required sections

---

## Phase 4: Quality Gates Verification

**Trigger**: Plan draft complete  
**Goal**: Verify plan passes all quality gates (PR7)

**Steps**:
1. **Completeness Check**: Verify all required sections are present
2. **Clarity Check**: Verify plan language is clear and unambiguous
3. **Specificity Check**: Verify plan steps are specific and actionable
4. **Landmine Screening**: Screen plan against governance landmines (PR8)
5. **Compliance**: Post `✅ Gate PLAN-4 PASS: Quality gates verified, landmines screened`

**Exit Gate**: Plan passes all quality gates

---

## Phase 5: Plan Finalization

**Trigger**: Quality gates verified  
**Goal**: Finalize plan for delivery to Round Table

**Steps**:
1. **Final Review**: Conduct final review of complete plan
2. **Compliance Check**: Verify all compliance lines are present
3. **Path Validation**: Final validation of all referenced paths
4. **Manifest Validation**: Verify Executor Manifest is complete (PR5)
5. **Compliance**: Post `✅ Gate PLAN-5 PASS: Plan finalized, ready for Round Table`

**Exit Gate**: Plan ready for Round Table review

---

## Phase 6: Round Table Review

**Trigger**: Plan finalized  
**Goal**: Conduct Round Table review with 6 Chathub panelists and capture findings

**Steps**:
1. **Panelist Intake**: User provides panelist metadata (name, model) and review text for each of 6 panelists
2. **Text Preparation**: Parse and normalize panelist replies (extract signatures, clean headers)
3. **Schema-Based Extraction**: Extract structured findings using predefined schema (category, severity, description, context, plan_impact)
4. **Rule-Based Validation**: Validate extracted findings against schema rules (valid categories, severities, confidence ranges)
5. **Confidence Scoring**: Score extraction quality based on completeness, consistency, and text coverage
6. **Database Storage**: Store validated findings in SQLite with automatic audit trail via triggers
7. **Verdict Collection**: Collect Pass/Conditional/Block verdicts from panelists
8. **Compliance**: Post `✅ Gate PLAN-6 PASS: Round Table review completed, findings captured`

**Extraction Schema**:
```json
{
  "findings": [
    {
      "category": "architecture|database|api-contract|security|implementation",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "description": "string",
      "context": "string (optional)",
      "plan_impact": "string (optional)",
      "confidence": 0.0-1.0
    }
  ],
  "verdict": "Pass|Conditional|Block",
  "overall_confidence": 1-10,
  "summary": "string"
}
```

**Quality Gates**:
- Minimum confidence score of 70/100 required for each panelist extraction
- At least 4 out of 6 panelists must provide valid reviews
- Severity levels must follow CRITICAL > HIGH > MEDIUM > LOW hierarchy

**Exit Gate**: All panelist reviews captured and stored in database

---

## Phase 7: Reviewer Pattern Analysis

**Trigger**: Round Table review complete  
**Goal**: Reviewer analyzes findings patterns and suggests rule creation (per GR3 single-responsibility)

**Steps**:
1. **Handoff to Reviewer**: Transfer findings database to Reviewer for pattern analysis
2. **Pattern Detection**: Reviewer analyzes findings for repeated patterns across recent batches
3. **Frequency Analysis**: Reviewer groups findings by category/severity to identify high-frequency issues
4. **Rule Suggestions**: Reviewer generates rule proposals from repeated patterns
5. **Findings Report**: Reviewer provides findings analysis and rule suggestions report
6. **Compliance**: Post `✅ Gate PLAN-7 PASS: Reviewer pattern analysis completed, rule suggestions received`

**Exit Gate**: Reviewer provides findings analysis and rule suggestions

---

## Phase 8: Planner Rule Integration

**Trigger**: Reviewer pattern analysis complete  
**Goal**: Planner integrates validated rule suggestions into PLANNER_RULES.md

**Steps**:
1. **Use Integration Workflow**: Use RULE_INTEGRATION_WORKFLOW.md for rule integration process
2. **Rule Review**: Review rule suggestions from Reviewer
3. **User Approval**: Get user approval for rule integration
4. **Rule Formatting**: Format rules according to PLANNER_RULES.md structure
5. **Rule Insertion**: Insert new rules into PLANNER_RULES.md
6. **Index Update**: Update rule index in PLANNER_RULES.md
7. **JSON Export**: Export findings and rules to JSON for git persistence
8. **Compliance**: Post `✅ Gate PLAN-8 PASS: Rule suggestions integrated into PLANNER_RULES.md`

**Exit Gate**: New rules integrated and exported to git

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)
- **PR1-PR15**: Planner-specific rules (plan creation, structure, quality gates)
- **PR16**: Universal rules integration

---

## Stop Conditions

**Halt execution if**:
- Missing compliance line for any gate
- Plan fails quality gates (PR7)
- Plan contains governance landmines (PR8)
- Plan has invalid manifest (PR5)
- Paths are not repo-relative (PR2)

---

## Evolution

**This workflow evolves when**:
- Plan structure requirements change
- Quality gate criteria change
- Workflow integration points change
- Governance rules are updated