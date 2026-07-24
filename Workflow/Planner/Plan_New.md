# Planner Workflow

**Purpose**: Step-by-step workflow for Planner agent to create plans for Executor execution with internal and external Round Table review and incremental validation.

**Version**: 2.0  
**Last Updated**: 2026-07-24 01:30 (UTC)  
**Status**: Active with Incremental Validation

**Attestation**: This workflow is gated with incremental validation and dual-gate governance per best practices.

---

## Workflow Overview

This workflow follows AI planning best practices with:
- **Incremental verification**: Validation after each phase to catch errors close to source
- **Dual-gate governance**: Early gate validation (Phase 2) + final gate validation (Phase 6)
- **Convergence-based iteration**: Internal and external Round Table loops until convergence
- **Incremental logging**: Save reviews as received for audit trail and Reviewer analysis
- **Role separation**: Planner creates plans, Reviewer analyzes quality (separate agent workflow)
- **Domain-split personas**: Panelists adopt specific domain expertise for focused review
- **Web search verification**: All panelists must verify findings against current best practices

**Phase Structure**:
1. **Phase 1**: Read Governance + Validate
2. **Phase 2**: Plan Creation + Early Gate Validation
3. **Phase 3**: Internal Round Table + Incremental Logging + Validate
4. **Phase 5**: Apply Findings + Validate
5. **[Loop 3→5 until Internal passes]**
6. **Phase 4**: External Round Table + Incremental Logging + Validate
7. **Phase 5**: Apply Findings + Validate
8. **[Loop 4→5 until External passes]**
9. **Phase 6**: Final Gate Delivery + Validate
10. **Phase 7**: Session Logging + Validation

**Template References**:
- **Plan Creation**: Plans/Plan_Template.md (plan structure and format)
- **Brief Creation**: Workflow/Planner/Plan_Brief_Template.md (review brief structure)
- **Prompt Instructions**: Workflow/Planner/Plan_Prompt_Template.md (persona adoption instructions)
- **Quality Assessment**: Plans/Quality_Rubric.md (dimension scoring criteria)
- **Gate System**: Scripts/Planner/Gates/run-all-planner-gates.sh (automated validation)

**Logging Structure**:
- Round Table reviews: Incremental logging as received (Logs/Roundtable/Devin/ and Logs/Roundtable/External/)
- Plan iterations: Incremental logging (Logs/Planner/)
- Gate results: JSON logging (Logs/Planner/gate-completions/ and Logs/Planner/gate-failures/)
- Session: Final consolidated logging at Phase 7

---

## Phase 1 — Read Governance + Validate

Read current governance documents to ensure up-to-date context for infrastructure planning.

**Validation**: Governance document reading verification with phase completion validation.

### Step 1.1: Read Planner Rules
Read Rules/Planner/Planner_Rules.md to understand operational rules, scope boundaries, and best practices.

### Step 1.2: Read Plan Template  
Read Plans/Plan_Template.md to understand required plan structure and format.

### Step 1.3: Phase Validation
Validate that governance documents were read successfully and context is established.

**Validation Criteria**:
- [ ] Planner_Rules.md read and understood
- [ ] Plan_Template.md read and understood  
- [ ] Current planning context established

**Phase 1 PASS**: Governance context established, planning rules understood, ready for plan creation.

**Phase 1 FAIL**: Re-read governance documents and establish context before proceeding.

---

## Phase 2 — Plan Creation + Early Gate Validation

Create plan draft following Plan_Template.md format and run early gate validation to catch issues before review cycles.

**Validation**: Plan structure validation + early gate validation (decision-time governance).

### Step 2.1: Understand User Requirements
Understand the user's request and what changes are needed for SovereignAI implementation.

### Step 2.2: Assess Current State
Assess the current system state and dependencies relevant to the planned changes.

### Step 2.3: Create Plan Draft
Create plan draft following Plans/Plan_Template.md format exactly:
- Required sections: Context, Steps, Dependencies
- Metadata: Revision, Date, Goal
- Planning language only (no implementation details)
- Clear dependencies and execution order

### Step 2.4: Save Plan Draft
Save plan draft to Plans/plan-{N}.{rev}.md with incrementing revision numbers.

### Step 2.5: Early Gate Validation
Run Planner gate system to validate plan structure and scope before review cycles:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev}.md phase2-early-validation
```

**Early Gate Focus**: Catch structural and scope issues before wasting review cycles.

**All 6 Gates Must Pass**:
1. **Gate 1**: Plan Structure Validation - Required sections and metadata present
2. **Gate 2**: Scope Compliance Validation - Planning content only, no implementation details
3. **Gate 3**: Dependency Analysis Validation - Dependency graph valid, no circular dependencies
4. **Gate 4**: Quality Assessment - Plan quality rubric evaluation
5. **Gate 5**: Landmine Screening Verification - No blocking landmines (passes with warning if file not found)
6. **Gate 6**: Infrastructure Scope Validation - Infrastructure scope compliance verified

### Step 2.6: Phase Validation
Validate that plan creation completed successfully and early gates passed.

**Validation Criteria**:
- [ ] User requirements understood
- [ ] Current state assessed
- [ ] Plan follows Plan_Template.md format
- [ ] Plan saved to correct location
- [ ] Early gate validation passed (Gates 1-6)
- [ ] Plan is ready for review process

**Phase 2 PASS**: Plan created with valid structure and scope, early gates passed, ready for internal review.

**Phase 2 FAIL**: Fix plan issues and re-run early gate validation before proceeding.

---

## Phase 3 — Internal Round Table + Incremental Logging + Validate

Run internal Round Table review with domain-split panelists based on best practices for committee review patterns.

**Validation**: Internal review completion validation + incremental logging validation.

### Step 3.1: Create Plan Brief and Prompt (Rev 1)
Create plan brief and review prompt for initial internal review using templates:
- **Use Template**: Workflow/Planner/Plan_Brief_Template.md
- **Brief Content**: Summarize context, goals, steps, dependencies, assign panelist personas
- **Prompt Content**: Include explicit persona adoption instructions from Workflow/Planner/Plan_Prompt_Template.md
- **Web Search Requirement**: Each panelist must use web search to verify findings against current best practices
- **Persona Assignment**: Assign specific domain-split personas to each panelist
- Save to: Logs/Roundtable/Devin/brief-rev1.md

**Brief Must Include**:
- Plan overview and context summary
- Steps and dependencies summary  
- Quality dimensions to evaluate
- Specific persona assignment for each panelist
- Web search requirement explicitly stated
- Quality rubric reference (Plans/Quality_Rubric.md)
- Structured output format requirements

**Prompt Must Include**:
- Explicit persona adoption instructions
- Domain-specific mental models and expertise
- Web search requirements for each persona
- Quality rubric usage instructions
- Output format requirements with JSON schema
- Review quality standards and common mistakes to avoid

### Step 3.2: Launch Internal Panelists
Launch internal subagent panelists with domain-split personas (4-6 panelists based on plan complexity):

**Panelist Personas (Domain-Split Reviewers with Web Search)**:
- **Panelist 1**: Structure and Dependencies Expert
  - Focus: Plan structure, step dependencies, execution order
  - Web Search: Must verify dependency patterns against current planning best practices
  - Checks: No circular dependencies, clear relationships, executable sequence
  
- **Panelist 2**: Scope Compliance Expert  
  - Focus: Planning language only, no implementation details
  - Web Search: Must verify scope boundaries against current agent governance research
  - Checks: Infrastructure scope, planning vs implementation boundaries
  
- **Panelist 3**: Quality and Clarity Expert
  - Focus: Plan clarity, completeness, user-focused language
  - Web Search: Must verify clarity and communication best practices for technical plans
  - Checks: Clear goal statement, well-defined steps, quality rubric assessment
  
- **Panelist 4**: Risk Assessment Expert
  - Focus: Implementation risks, edge cases, dependencies
  - Web Search: Must verify risk assessment methodologies against current practices
  - Checks: Risk identification, mitigation strategies, feasibility
  
- **Panelist 5**: Alternative Approaches Expert (optional for complex plans)
  - Focus: Alternative planning approaches, optimizations
  - Web Search: Must research current planning patterns and optimization techniques
  - Checks: Better alternatives, simplification opportunities, trade-offs

- **Panelist 6**: Infrastructure Alignment Expert (optional for infrastructure changes)
  - Focus: Infrastructure principles, architectural constraints
  - Web Search: Must verify infrastructure principles against current research
  - Checks: Compliance with infrastructure rules, architectural alignment

**Panelist Capabilities**: All panelists must use web_search tool to verify findings against current best practices and research.

**Panelist Selection**: Based on plan complexity and scope (4 panelists for simple plans, 6 for complex)

### Step 3.3: Collect Panelist Reviews
Collect panelist reviews with structured findings:
- Each panelist must use web search to verify findings and current best practices
- Each panelist provides findings with severity (CRITICAL, HIGH, MEDIUM, LOW)
- Panelists rate plan quality on relevant dimensions (accuracy, completeness, clarity, structure, context)
- Panelists provide specific improvement suggestions grounded in current research
- Structured output format: {"verdict": "PASS|FAIL", "issues": [...], "notes": [...], "web_sources": [...]}

### Step 3.4: Incremental Logging
Save each panelist review incrementally as received:
```bash
# Save individual panelist review
Logs/Roundtable/Devin/iteration-{N}-panelist-{M}.md
```

**Incremental Logging Metadata**:
- Timestamp
- Panelist ID and persona (domain expertise)
- Plan revision reviewed
- Findings with severity ratings
- Quality rubric scores
- Improvement suggestions
- Web search results and sources used
- Structured verdict (PASS/FAIL)

### Step 3.5: Aggregate Findings
Aggregate all panelist findings and generate consolidated feedback:
- Count findings by severity
- Identify common themes and patterns
- Generate improvement recommendations
- Calculate quality scores across dimensions

### Step 3.6: Phase Validation
Validate that internal review completed successfully and findings were logged.

**Validation Criteria**:
- [ ] Panelists launched (4-6 based on complexity)
- [ ] All panelist reviews collected
- [ ] Each review incrementally logged with metadata
- [ ] Findings aggregated and consolidated
- [ ] Convergence criteria established (findings decreasing, similarity increasing)

**Phase 3 PASS**: Internal review completed, findings logged, ready for application.

**Phase 3 FAIL**: Re-launch panelists or fix logging issues before proceeding.

---

## Phase 5 — Apply Findings + Validate

Apply Round Table findings to improve plan quality and create new revision.

**Validation**: Findings application validation + plan revision validation.

### Step 5.1: Review Findings
Review aggregated findings from internal or external Round Table:
- CRITICAL findings: Must address before proceeding
- HIGH findings: Must address before proceeding
- MEDIUM findings: Address or document rationale
- LOW findings: Consider for improvement

### Step 5.2: Apply Findings to Plan
Apply findings to plan and create new revision:
- Increment revision number (plan-{N}.{rev+1}.md)
- Address CRITICAL and HIGH findings
- Address or document MEDIUM findings
- Consider LOW findings for improvement
- Maintain plan structure and scope compliance

### Step 5.3: Validate Revised Plan
Run gate validation on revised plan to ensure changes maintain quality:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{rev+1}.md phase5-revision-validation
```

### Step 5.4: Log Plan Iteration
Log plan iteration with changes made:
```bash
Logs/Planner/iteration-{N}-rev-{rev+1}.md
```

**Iteration Log Content**:
- Previous revision vs current revision
- Findings applied
- Changes made
- Gate validation results

### Step 5.5: Phase Validation
Validate that findings were applied correctly and plan quality improved.

**Validation Criteria**:
- [ ] CRITICAL findings addressed
- [ ] HIGH findings addressed
- [ ] MEDIUM findings addressed or documented
- [ ] Plan follows template structure
- [ ] Gate validation passed
- [ ] Iteration logged with metadata

**Phase 5 PASS**: Findings applied, plan improved, ready for next review iteration.

**Phase 5 FAIL**: Fix application issues and re-validate before proceeding.

---

## Internal Convergence Loop

**Loop Structure**: Phase 3 → Phase 5 → Phase 3 (repeat until Internal Round Table passes)

**Convergence Logic**:
1. Run Phase 3 (Internal Round Table)
2. If Phase 3 PASSES → Proceed to Phase 4 (External Round Table)
3. If Phase 3 FAILS → Proceed to Phase 5 (Apply Findings)
4. At end of Phase 5 → Return to Phase 3
5. Repeat until Internal Round Table achieves convergence

**Convergence Criteria**:
- Findings count decreasing across iterations
- Panelist similarity increasing across iterations
- CRITICAL and HIGH findings resolved
- Plan quality rubric scores improving

**Loop Exit Condition**: Internal Round Table achieves convergence (findings ≤5, panelist agreement ≥80%).

**Loop Cap**: Maximum 5 internal iterations.

**On Convergence**: Proceed to Phase 4 (External Round Table).

**On Loop Cap Reached**: Stop and escalate to user decision.

---

## Phase 4 — External Round Table + Incremental Logging + Validate

Run external Round Table review with Chathub.gg panelists for final validation and broader perspective.

**Validation**: External review completion validation + incremental logging validation.

### Step 4.1: Create External Review Brief and Prompt
Create external review brief and prompt for Chathub.gg panelists using templates:
- **Use Template**: Workflow/Planner/Plan_Brief_Template.md
- **Brief Content**: Updated brief with internal iteration context, assign external panelist personas
- **Prompt Content**: Include explicit persona adoption instructions from Workflow/Planner/Plan_Prompt_Template.md
- **Web Search Requirement**: Each external panelist must use web search to verify findings against current best practices
- **Persona Assignment**: Assign specific domain-split personas to each external panelist
- Save to: Logs/Roundtable/External/brief-rev1.md

**Brief Must Include**:
- Internal iteration context and findings summary
- Plan overview and context summary
- Steps and dependencies summary
- Quality dimensions to evaluate
- Specific persona assignment for each external panelist
- Web search requirement explicitly stated
- Quality rubric reference (Plans/Quality_Rubric.md)
- Structured output format requirements

**Prompt Must Include**:
- Explicit persona adoption instructions
- Domain-specific mental models and expertise
- Web search requirements for each persona
- Quality rubric usage instructions
- Output format requirements with JSON schema
- Review quality standards and common mistakes to avoid

### Step 4.2: Launch External Panelists
Launch external Chathub.gg panelists with domain-split personas (4-6 panelists based on plan complexity):

**External Panelist Personas (Domain-Split Reviewers with Web Search)**:
- **Panelist 1**: Structure and Dependencies Expert
  - Focus: Plan structure, step dependencies, execution order
  - Web Search: Must verify dependency patterns against current planning best practices
  - Checks: No circular dependencies, clear relationships, executable sequence
  
- **Panelist 2**: Scope Compliance Expert  
  - Focus: Planning language only, no implementation details
  - Web Search: Must verify scope boundaries against current agent governance research
  - Checks: Infrastructure scope, planning vs implementation boundaries
  
- **Panelist 3**: Quality and Clarity Expert
  - Focus: Plan clarity, completeness, user-focused language
  - Web Search: Must verify clarity and communication best practices for technical plans
  - Checks: Clear goal statement, well-defined steps, quality rubric assessment
  
- **Panelist 4**: Risk Assessment Expert
  - Focus: Implementation risks, edge cases, dependencies
  - Web Search: Must verify risk assessment methodologies against current practices
  - Checks: Risk identification, mitigation strategies, feasibility
  
- **Panelist 5**: Alternative Approaches Expert (optional for complex plans)
  - Focus: Alternative planning approaches, optimizations
  - Web Search: Must research current planning patterns and optimization techniques
  - Checks: Better alternatives, simplification opportunities, trade-offs

- **Panelist 6**: Infrastructure Alignment Expert (optional for infrastructure changes)
  - Focus: Infrastructure principles, architectural constraints
  - Web Search: Must verify infrastructure principles against current research
  - Checks: Compliance with infrastructure rules, architectural alignment

**Panelist Capabilities**: All external panelists must use web search to verify findings against current best practices and research.

**Panelist Selection**: Based on plan complexity and scope (4 panelists for simple plans, 6 for complex)

### Step 4.3: Collect External Reviews
Collect external panelist reviews with structured findings:
- Each panelist must use web search to verify findings and current best practices
- Each panelist provides findings with severity (CRITICAL, HIGH, MEDIUM, LOW)
- Panelists rate plan quality on relevant dimensions (accuracy, completeness, clarity, structure, context)
- Panelists provide specific improvement suggestions grounded in current research
- Panelists provide overall quality score (0-100)
- Structured output format: {"verdict": "PASS|FAIL", "issues": [...], "notes": [...], "score": 0-100, "web_sources": [...]}

### Step 4.4: Incremental Logging
Save each external panelist review incrementally as received:
```bash
# Save individual external panelist review
Logs/Roundtable/External/round-{N}-panelist-{M}.md
```

**Incremental Logging Metadata**:
- Timestamp
- Panelist ID and persona (domain expertise)
- Plan revision reviewed
- Findings with severity ratings
- Quality rubric scores
- Overall quality score
- Improvement suggestions
- Web search results and sources used
- Structured verdict (PASS/FAIL)

### Step 4.5: Aggregate External Findings
Aggregate all external panelist findings and generate consolidated feedback:
- Count findings by severity
- Calculate average quality score
- Identify common themes and patterns
- Generate improvement recommendations

### Step 4.6: Phase Validation
Validate that external review completed successfully and findings were logged.

**Validation Criteria**:
- [ ] External panelists launched (4-6 based on complexity)
- [ ] All external reviews collected
- [ ] Each review incrementally logged with metadata
- [ ] Findings aggregated and consolidated
- [ ] Quality score calculated (≥90 for clean pass, 70-89 with rationale, <70 fails)

**Phase 4 PASS**: External review completed, findings logged, quality score achieved.

**Phase 4 FAIL**: Re-launch external panelists or fix logging issues before proceeding.

---

## External Convergence Loop

**Loop Structure**: Phase 4 → Phase 5 → Phase 4 (repeat until External Round Table passes)

**Convergence Logic**:
1. Run Phase 4 (External Round Table)
2. If Phase 4 PASSES (≥90 score or 70-89 with rationale) → Proceed to Phase 6 (Final Gate Delivery)
3. If Phase 4 FAILS (<70 score) → Proceed to Phase 5 (Apply Findings)
4. At end of Phase 5 → Return to Phase 4
5. Repeat until External Round Table achieves convergence

**Convergence Criteria**:
- Quality score ≥90 (clean pass) OR 70-89 with documented rationale
- Findings count decreasing across iterations
- Panelist similarity increasing across iterations
- CRITICAL and HIGH findings resolved

**Loop Exit Condition**: External Round Table achieves clean pass (≥90) or acceptable pass (70-89 with rationale).

**Loop Cap**: Maximum 3 external iterations.

**On Convergence**: Proceed to Phase 6 (Final Gate Delivery).

**On Loop Cap Reached**: Stop and escalate to user decision.

---

## Phase 6 — Final Gate Delivery + Validate

Run final Planner gate system validation before plan delivery for manual implementation.

**Validation**: Full gate system validation + delivery authorization.

### Step 6.1: Run Final Gate Validation
Run full Planner gate system on final plan revision:
```bash
bash Scripts/Planner/Gates/run-all-planner-gates.sh Plans/plan-{N}.{final-rev}.md phase6-final-validation
```

**All 6 Gates Must Pass**:
1. **Gate 1**: Plan Structure Validation - Required sections and metadata present
2. **Gate 2**: Scope Compliance Validation - Planning content only, no implementation details
3. **Gate 3**: Dependency Analysis Validation - Dependency graph valid, no circular dependencies
4. **Gate 4**: Quality Assessment - Plan quality rubric evaluation
5. **Gate 5**: Landmine Screening Verification - No blocking landmines (passes with warning if file not found)
6. **Gate 6**: Infrastructure Scope Validation - Infrastructure scope compliance verified

### Step 6.2: Validate Gate Results
Validate that all gates passed and gate completion hash was generated.

**Validation Criteria**:
- [ ] All 6 gates passed
- [ ] Gate completion hash generated
- [ ] Gate results logged to Logs/Planner/gate-completions/
- [ ] No critical gate failures

### Step 6.3: Delivery Authorization
Authorize plan delivery for manual implementation based on gate validation.

**Delivery Authorization**:
- Gate completion hash: {hash}
- Gate validation timestamp: {timestamp}
- Delivery authorized: Yes/No
- Delivery conditions: All gates passed
- Implementation target: Manual execution by user

### Step 6.4: Phase Validation
Validate that final gate validation completed successfully and delivery is authorized.

**Validation Criteria**:
- [ ] All 6 gates passed
- [ ] Gate completion hash generated
- [ ] Gate results logged
- [ ] Delivery authorized for manual implementation
- [ ] Plan ready for user execution

**Phase 6 PASS**: Final gate validation passed, delivery authorized, plan ready for manual implementation.

**Phase 6 FAIL**: Fix gate failures and re-validate before delivery authorization.

---

## Phase 7 — Session Logging + Validate

Complete session logging with comprehensive audit trail and validate logging completeness.

**Validation**: Session logging validation + audit trail completeness validation.

### Step 7.1: Log Plan Iterations
Consolidate all plan iterations into session log:
```bash
Logs/Planner/session-plan-{N}.md
```

**Session Log Content**:
- Plan creation timeline
- All plan revisions with changes
- Gate validation results for each revision
- Total iterations and convergence metrics

### Step 7.2: Log Round Table Iterations
Consolidate all Round Table reviews into session summary:
```bash
Logs/Roundtable/session-roundtable-{N}.md
```

**Round Table Session Content**:
- Internal iteration timeline with panelist counts
- External iteration timeline with panelist counts
- Quality score progression
- Findings count progression
- Convergence metrics

### Step 7.3: Log Gate System Results
Consolidate all gate validation results:
```bash
Logs/Planner/session-gates-{N}.md
```

**Gate Session Content**:
- Early gate validation results (Phase 2)
- Revision gate validation results (Phase 5)
- Final gate validation results (Phase 6)
- Gate completion hashes
- Gate failure resolution history

### Step 7.4: Validate Logging Completeness
Validate that all logging completed successfully and audit trail is complete.

**Validation Criteria**:
- [ ] Plan iterations logged
- [ ] Round Table reviews logged (internal and external)
- [ ] Gate validation results logged
- [ ] Incremental reviews preserved
- [ ] Session metadata complete
- [ ] Audit trail complete

### Step 7.5: Generate Session Attestation
Generate session attestation hash for verification:
```bash
# Generate hash from all session logs
attestation_hash = hash(plan_log + roundtable_log + gate_log)
```

### Step 7.6: Phase Validation
Validate that session logging completed successfully and audit trail is complete.

**Validation Criteria**:
- [ ] All session logs created
- [ ] Logging completeness validated
- [ ] Session attestation hash generated
- [ ] Audit trail complete
- [ ] Session ready for handoff

**Phase 7 PASS**: Session logging complete, audit trail validated, Planner workflow complete.

**Phase 7 FAIL**: Fix logging issues and re-validate before session completion.

---

## Planner Workflow Completion

**Workflow Complete When**:
- All 7 phases passed validation
- Internal and external Round Table achieved convergence
- Final gate validation passed
- Session logging complete and validated
- Plan delivered for manual implementation with delivery authorization

**Planner Responsibilities**:
- Create plans following Planner_Rules.md and Plan_Template.md
- Run dual-gate validation (early and final)
- Execute convergence-based review process
- Maintain incremental logging for audit trail
- Ensure infrastructure scope compliance

**Reviewer Responsibilities** (Separate Workflow):
- Analyze Round Table quality and patterns
- Identify recurring issues and governance gaps
- Recommend improvements to Planner_Rules.md and Plan_Template.md
- Suggest governance improvements for AGENTS.md

**User Responsibilities** (Manual Execution):
- Implement plans according to structure and dependencies
- Follow planning steps in proper order
- Report implementation results back to Planner/Reviewer
- Provide feedback on plan quality and execution experience

---

## Quality Hierarchy

Follow Quality > Token Cost > Efficiency hierarchy per PRINCIPLES.md when making trade-off decisions.

---

## Continuous Improvement

**Pattern Recognition**:
- Round Table analysis by Reviewer identifies recurring patterns
- Findings that repeat across multiple plans
- Gate failures that indicate template or rules issues
- Scope compliance violations that need clarification

**Rules Evolution**:
- Patterns from gate failures → Updates to Planner_Rules.md
- Patterns from Round Table findings → Updates to Plan_Template.md
- Recurring issues → Workflow improvements
- Best practice research → Governance enhancements

**Review Packet Generation**:
- Planner generates structured review packet for Reviewer
- Contains: plan metadata, Round Table results, gate results, quality metrics
- Enables Reviewer to analyze patterns and recommend improvements
- Separate from Planner workflow completion