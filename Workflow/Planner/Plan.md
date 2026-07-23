# Planner Workflow

**Purpose**: Step-by-step workflow for Planner agent to create plans for Executor execution with internal and external Round Table review.

**Version**: 1.8  
**Last Updated**: 2026-07-23 20:15 (MYT)  
**Status**: Active

**Attestation**: This workflow is gated with attestation per AGENTS.md requirement

---

## Workflow Overview

This workflow mirrors the old Round Table structure with tool updates:
- Internal subagent panelists for iterative review
- External Chathub.gg panelists for final validation (documented GR7 exception)
- Convergence-based iteration criteria
- Plan delivery only after external clean pass
- Logging in Logs/Roundtable/Devin/ for internal, Logs/Roundtable/External/ for external

---

## Step 1 — Read Governance Documents

Before creating plans, read current governance documents to ensure up-to-date context. Do not rely on cached knowledge.

**Attestation Gate**: Document reading verification with hash evidence

1. Read global rules (GR1-GR33) from Rules/Global/RULES.md
2. Post: `✅ Gate Step 1.1 PASS: Read global rules (GR1-GR33)`
3. Read Planner-specific rules (PR1-PR10) from Rules/Planner/Rules.md
4. Post: `✅ Gate Step 1.2 PASS: Read Planner rules (PR1-PR10)`
5. Read Shared/PRINCIPLES.md (project principles P1-P15)
6. Post: `✅ Gate Step 1.3 PASS: Read Shared/PRINCIPLES.md (P1-P15)`
7. Read Shared/LANDMINES.md (blocking constraints)
8. Post: `✅ Gate Step 1.4 PASS: Read Shared/LANDMINES.md (landmine pre-screen)`
9. Note: Use procedural skills for routine operations (/session-logging, /quality-check, /web-verify)
10. Post: `✅ Gate Step 1.5 PASS: Procedural skills noted for routine operations`
11. **Logging**: Invoke `/log-action` skill to log governance document reading
   - Action type: "decision"
   - Details: '{"step": "read_governance_documents", "files": ["GR1-GR33", "PR1-PR10", "P1-P15", "LANDMINES.md"]}'
   - Result: "success"
   - Compliance status: "compliant"
12. Generate attestation hash for document reading step
13. Post: `✅ Gate Step 1 PASS: Governance documents read, attestation hash: {hash}`

---

## Step 1.5 — Architecture Preservation Check (Skip if not new functionality)

**Attestation Gate**: IDE Agents Architecture validation with hash evidence

1. If creating new planning functionality, validate against IDE Agents Architecture per GR33
2. Check that new planning functionality preserves agent role boundaries:
   - New planning functionality must align with planning role, not execution or review
   - No boundary crossing or supremacy check violations
3. Post: `✅ Gate Step 1.5.1 PASS: New planning functionality validated against agent role boundaries`
4. Ensure no boundary crossing or supremacy check violations
5. Post: `✅ Gate Step 1.5.2 PASS: Architecture preservation verified, no boundary violations`
6. Generate attestation hash for architecture preservation step
7. Post: `✅ Gate Step 1.5 PASS: IDE Agents Architecture preserved, attestation hash: {hash}`

---

## Step 2 — Create Plan Draft

Create structured plan draft with explicit steps, dependencies, and Executor Manifest. No implementation details - planning only.

**Attestation Gate**: Plan creation verification with hash evidence

1. Define plan goal and context
2. Create ordered steps with dependencies
3. Create Executor Manifest (identity, capabilities, I/O schemas, token budget)
4. No code implementation details (left to Executor)
5. Store in Plans/ directory as plan-{N}.{rev}.md
6. Post: `✅ Gate Step 2.1 PASS: Plan goal and context defined`
7. Post: `✅ Gate Step 2.2 PASS: Ordered steps with dependencies created`
8. Post: `✅ Gate Step 2.3 PASS: Executor Manifest included (identity/capabilities/I-O schemas/token budget)`
9. Post: `✅ Gate Step 2.4 PASS: No implementation details, planning only`
10. Post: `✅ Gate Step 2.5 PASS: Plan stored in Plans/plan-{N}.{rev}.md`
11. **Logging**: Invoke `/log-action` skill to log plan creation
   - Action type: "decision"
   - Details: '{"step": "create_plan_draft", "plan": "plan-{N}.{rev}.md", "steps": "{N}"}'
   - Result: "success"
   - Compliance status: "compliant"
12. Generate attestation hash for plan creation step
13. Post: `✅ Gate Step 2 PASS: Plan draft created, {N} steps, revision {rev}, attestation hash: {hash}`
14. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step2` to validate Step 2 completion before proceeding
15. Post: `✅ Gate Step 2.seq PASS: Step 2 completion validated, allowed to proceed to Step 2.5`

---

## Step 2.5 — Prepare Round Table Material

Prepare brief and prompt for Round Table review (Rev 1 only; Rev 2+ brief only if user requests).

**Attestation Gate**: Round Table material preparation verification with hash evidence

1. Screen plan against Shared/LANDMINES.md
2. Post: `✅ Gate Step 2.5.1 PASS: Screened against LANDMINES.md, {N} blocking, {N} non-blocking`
3. Assemble brief (Rev 1 only; Rev 2+ brief only if user requests)
4. Post: `✅ Gate Step 2.5.2 PASS: Brief assembled, {N} sections, {lines} lines`
5. Assemble plan, dimensions, risks, settled findings
6. Post: `✅ Gate Step 2.5.3 PASS: Material assembled, {N} plans, {N} dimensions, {N} risks`
7. Draft Round Table prompt with rubric-based criteria
8. Post: `✅ Gate Step 2.5.4 PASS: Prompt drafted, Rev {n}, {N} panelists, rubric-based criteria`
9. Generate attestation hash for Round Table material preparation
10. Post: `✅ Gate Step 2.5 PASS: Round Table material prepared, attestation hash: {hash}`
11. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step2.5` to validate Step 2.5 completion before proceeding
12. Post: `✅ Gate Step 2.5.seq PASS: Step 2.5 completion validated, allowed to proceed to Step 3`

**Brief Format** (Rev 1 only, ≤80 lines, 9 sections in order):
1. Context — baseline, repo state
2. Plans in this batch — table: plan #, title, depends on, vision principles, rules
3. Rules carried forward — rule IDs only, pointer to governance files
4. Questions for Round Table — Q-ID
5. Open questions resolved — list resolved Q-IDs; "none" if none
6. Risks flagged — includes landmine pre-screen
7. Coverage target
8. Round Table protocol reminder
9. Superseded rules — rule ID + pointer to replacement

**Round Table Prompt Format**:
```
## ROLES
{Panelist role definitions with expertise areas - 6 panelists with competency-based personas}
Each panelist is an independent expert. If any panelist realizes they are wrong at any point, they must acknowledge it and withdraw that finding.

## MATERIAL
- Brief: {brief content} (Rev 1 only, unless user requests for Rev 2+)
- Plans: {plan files}
- Dimensions: {evaluation dimensions}
- Risks: {pre-screened risks}
- Settled findings: {previously accepted findings}

## EVALUATION CRITERIA (Rubric-Based)
For each plan, evaluate across six dimensions:
1. Clarity & Specificity — are objectives and success criteria explicit?
2. Structural Organization — is the plan well-organized with clear sections?
3. Context Management — are instructions placed strategically around context?
4. Reasoning & Tool Guidance — does the plan justify tool choices with reasoning?
5. Examples & Output Control — does the plan specify output formats with examples?
6. Executor Manifest — does the plan include complete execution manifest?
```

**Plan Format**:
```markdown
# Plan {N} — {Title}

**Revision**: {rev}  
**Date**: {YYYY-MM-DD}  
**Goal**: {goal statement}

## Context
{relevant context and constraints}

## Steps
1. {step 1 with dependencies}
2. {step 2 with dependencies}
...

## Dependencies
{step dependencies and order}

## Executor Manifest
{identity, capabilities, I/O schemas, token budget}
```

---

## Step 3 — Self-Check Plan

Run internal self-check against quality criteria before Round Table review to reduce revision rounds.

**Attestation Gate**: Self-check verification with hash evidence

1. Apply 6-dimension rubric:
   - Clarity & Specificity
   - Structural Organization
   - Context Management
   - Reasoning & Tool Guidance
   - Examples & Output Control
   - Executor Manifest
2. Post: `✅ Gate Step 3.1 PASS: 6-dimension rubric applied`
3. Check against known patterns
4. Post: `✅ Gate Step 3.2 PASS: Pattern check completed, {N} patterns checked`
5. Fix CRITICAL/HIGH findings before Round Table
6. Post: `✅ Gate Step 3.3 PASS: CRITICAL/HIGH findings fixed, {N} findings addressed`
7. Document all findings and fixes
8. Post: `✅ Gate Step 3.4 PASS: Findings documented, {N} fixed, {N} deferred`
9. Generate attestation hash for self-check step
10. Post: `✅ Gate Step 3 PASS: Self-check complete, attestation hash: {hash}`
11. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step3` to validate Step 3 completion before proceeding
12. Post: `✅ Gate Step 3.seq PASS: Step 3 completion validated, allowed to proceed to Step 4`

**Self-Check Format**:
```markdown
# Self-Check Results — Plan {N}.{rev}

**Rubric Dimensions**: {scores/feedback for each dimension}
**Pattern Check**: {N} patterns checked, {N} matches found
**Findings Fixed**: {list of CRITICAL/HIGH findings fixed}
**Findings Deferred**: {list of findings deferred to Round Table with reasoning}
```

---

## Step 4 — Internal Round Table Iteration

Use internal subagent panelists to review plan, iterating until convergence criteria met before external review.

**Attestation Gate**: Internal Round Table iteration verification with hash evidence

1. Launch internal subagent panelists with defined personas
2. Post: `✅ Gate Step 4.1 PASS: Internal panelists launched, 6 panelists with competency-based personas`
3. Panelists review plan and provide findings
4. Post: `✅ Gate Step 4.2 PASS: Panelist review completed, {N} findings received`
5. Log iteration in Logs/Roundtable/Devin/iteration-{N}.md
6. Post: `✅ Gate Step 4.3 PASS: Iteration logged to Logs/Roundtable/Devin/iteration-{N}.md`
7. **Logging**: Invoke `/log-action` skill to log Round Table iteration
   - Action type: "decision"
   - Details: '{"step": "internal_round_table", "iteration": "{N}", "findings": "{N}"}'
   - Result: "success"
   - Compliance status: "compliant"
8. Apply accepted findings to create next revision
9. Post: `✅ Gate Step 4.4 PASS: Findings applied, revision {rev} created`
10. Continue until convergence criteria met:
   - Findings per iteration decreasing
   - Output similarity between iterations increasing
   - No new categories of problems appear
11. Maximum 5-6 internal iterations
12. Post: `✅ Gate Step 4.5 PASS: Convergence achieved in {N} iterations, findings decreasing, similarity increasing`
13. Generate attestation hash for internal Round Table iteration
14. Post: `✅ Gate Step 4 PASS: Internal Round Table complete, attestation hash: {hash}`
15. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step4` to validate Step 4 completion before proceeding
16. Post: `✅ Gate Step 4.seq PASS: Step 4 completion validated, allowed to proceed to Step 5`

**Convergence Criteria**:
- **Stop when**: Findings-per-pass count decreasing AND output similarity increasing AND no new problem categories
- **Continue if**: Oscillation detected (contradictory assessments between passes)
- **Max limit**: 5-6 iterations (diminishing returns beyond this)

**Internal Round Table Logging**:
```markdown
# Internal Round Table Iteration {N} — Plan {N}.{rev}

**Date**: {YYYY-MM-DD}  
**Panelists**: {personas used}  
**Findings**: {N} total ({N} CRITICAL, {N} HIGH, {N} MEDIUM, {N} LOW)  
**Convergence Status**: {decreasing/stable/increasing}  
**Output Similarity**: {percentage vs previous iteration}

## Findings
{detailed findings from each panelist}

## Actions Taken
{accepted findings applied, rejected findings with reasoning}
```

---

## Step 5 — External Round Table Review

User posts plan to external Round Table (Chathub.gg with 6 panelists, documented GR7 exception), then provides findings to Planner for revision.

**Attestation Gate**: External Round Table review verification with hash evidence

1. User posts plan to external Chathub.gg Round Table
2. Request external panelists use same personas as internal
3. Post: `✅ Gate Step 5.1 PASS: External Round Table initiated, Chathub.gg, 6 panelists, competency-based personas`
4. User collects external panelist responses
5. Post: `✅ Gate Step 5.2 PASS: External panelist responses collected`
6. User posts external findings to Planner
7. Post: `✅ Gate Step 5.3 PASS: External findings received, {N} findings total`
8. Log external findings in Logs/Roundtable/External/round-{N}.md
9. Post: `✅ Gate Step 5.4 PASS: External findings logged to Logs/Roundtable/External/round-{N}.md`
10. **Logging**: Invoke `/log-action` skill to log external Round Table review
   - Action type: "decision"
   - Details: '{"step": "external_round_table", "findings": "{N}", "platform": "Chathub.gg"}'
   - Result: "success"
   - Compliance status: "compliant"
11. Apply accepted findings to create revision
12. Post: `✅ Gate Step 5.5 PASS: Findings applied, revision {rev} created`
13. Generate attestation hash for external Round Table review
14. Post: `✅ Gate Step 5 PASS: External Round Table review complete, attestation hash: {hash}`
15. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step5` to validate Step 5 completion before proceeding
16. Post: `✅ Gate Step 5.seq PASS: Step 5 completion validated, allowed to proceed to Step 6`

**External Round Table Logging**:
```markdown
# External Round Table Review — Plan {N}.{rev}

**Date**: {YYYY-MM-DD}  
**External Panelists**: {6 Chathub.gg panelists with personas}  
**Findings**: {N} total ({N} CRITICAL, {N} HIGH, {N} MEDIUM, {N} LOW)  
**Internal Iterations**: {N} iterations before external review

## External Findings
{detailed findings from external panelists}

## Actions Taken
{accepted findings applied, rejected findings with reasoning}
```

---

## Step 6 — Process Findings

Process each panelist finding systematically, accepting or rejecting with documented reasoning.

**Attestation Gate**: Finding processing verification with hash evidence

For each panelist finding:

1. Post: `✅ Gate Step 6.1 PASS: Finding RT-{id} accepted, {reasoning} — {fix applied or documented}`
2. Or: `❌ Gate Step 6.1 FAIL: Finding RT-{id} rejected, {reasoning}`
3. Ensure no finding left unaddressed
4. Post: `✅ Gate Step 6.2 PASS: All findings processed, {N} accepted, {N} rejected`
5. Verify CRITICAL/HIGH findings addressed
6. Post: `✅ Gate Step 6.3 PASS: CRITICAL/HIGH findings addressed, {N} findings resolved`
7. Generate attestation hash for finding processing
8. Post: `✅ Gate Step 6 PASS: Findings processed systematically, attestation hash: {hash}`
9. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step6` to validate Step 6 completion before proceeding
10. Post: `✅ Gate Step 6.seq PASS: Step 6 completion validated, allowed to proceed to Step 7`

**Human Verification Checklist**:
- [ ] Every finding has a compliance line
- [ ] No finding is unaddressed
- [ ] Accepted findings have fix documentation
- [ ] Rejected findings have reasoning

**STOP Conditions**:
- Any finding without a compliance line
- Accepted finding without documented fix
- Rejected finding without reasoning

---

## Step 7 — Plan Delivery Condition

Deliver plan to Executor only after external Round Table clean pass achieved.

**Attestation Gate**: Plan delivery verification with hash evidence

**Threshold Table**:

| Score Threshold | Action |
|----------------|--------|
| 90-100 | Clean pass — proceed to delivery |
| 70-89 | Review findings — Planner may proceed with documented rationale |
| <70 | BLOCK — requires additional external Round Table round |

**Verification Checklist**:
- [ ] External Round Table clean pass achieved (≥90 OR documented rationale for 70-89)
- [ ] All CRITICAL and HIGH findings addressed
- [ ] MEDIUM findings addressed or documented
- [ ] Panelist majority achieved
- [ ] Executor Manifest present and validated
- [ ] No blocking landmines
- [ ] Plan has no implementation details (planning only)

**STOP Conditions**:
- Score <70 without additional external Round Table round
- CRITICAL or HIGH findings unaddressed
- Panelist majority not achieved
- Blocking landmines present
- Executor Manifest missing or invalid
- Plan contains implementation details

1. Verify external Round Table clean pass achieved
2. Post: `✅ Gate Step 7.1 PASS: External clean pass achieved, score {score}/100`
3. Verify all CRITICAL/HIGH findings addressed
4. Post: `✅ Gate Step 7.2 PASS: CRITICAL/HIGH findings addressed, {N} findings resolved`
5. Verify panelist majority achieved
6. Post: `✅ Gate Step 7.3 PASS: Panelist majority achieved, {N}/6 panelists`
7. Verify no blocking landmines
8. Post: `✅ Gate Step 7.4 PASS: No blocking landmines, LANDMINES.md pre-screen passed`
9. Verify Executor Manifest present and validated
10. Post: `✅ Gate Step 7.5 PASS: Executor Manifest present and validated`
11. Verify plan has no implementation details
12. Post: `✅ Gate Step 7.6 PASS: Plan contains no implementation details, planning only`
13. **Logging**: Invoke `/log-action` skill to log plan delivery
   - Action type: "completion"
   - Details: '{"step": "plan_delivery", "plan": "plan-{N}.{rev}.md", "score": "{score}"}'
   - Result: "success"
   - Compliance status: "compliant"
14. Generate attestation hash for plan delivery
15. Post: `✅ Gate Step 7 PASS: Plan delivery criteria met, ready for Executor, attestation hash: {hash}`
16. **Sequence Gate**: Run `python Scripts/Planner/verify_planner_workflow.py --step-seq step7` to validate Step 7 completion before proceeding
17. Post: `✅ Gate Step 7.seq PASS: Step 7 completion validated, plan delivery authorized`

---

## Step 8 — Session Logging

Log all actions in real-time with reasoning context per GR24/GR25.

**Attestation Gate**: Session logging verification with hash evidence

1. Log all plan creation iterations in Logs/Planner/
2. Post: `✅ Gate Step 8.1 PASS: Plan iterations logged to Logs/Planner/`
3. Log all Round Table iterations (internal and external)
4. Post: `✅ Gate Step 8.2 PASS: Round Table iterations logged (internal and external)`
5. Use direct file-based markdown logging
6. Post: `✅ Gate Step 8.3 PASS: Direct file-based markdown logging used`
7. Include context, reasoning, alternatives, outcomes, impact
8. Post: `✅ Gate Step 8.4 PASS: Logs include context, reasoning, alternatives, outcomes, impact`
9. UTF-8 encoding for all log files
10. Post: `✅ Gate Step 8.5 PASS: All log files use UTF-8 encoding`
11. **Logging**: Invoke `/session-summary` skill to log session completion
   - Session ID: {session_id}
   - Agent: "planner"
   - Actions taken: [{"action": "plan_created", "timestamp": "{timestamp}"}]
   - Start time: {session_start_time}
   - Compliance status: "compliant"
   - Compliance score: {compliance_score}
12. Generate session attestation hash
13. Post: `✅ Gate Step 8 PASS: Session complete, {N} actions logged, {duration} minutes, attestation hash: {hash}`

**Session Log Format**:
```markdown
# Planner Session — Plan {N}

**Date**: {YYYY-MM-DD}  
**Duration**: {minutes}  
**Total Actions**: {N}  
**Success Rate**: {percentage}

## Action Log
{detailed action log with context, reasoning, outcomes, impact}

## Quality Decisions
{trade-off decisions with Q/TC/E ratings}
```

---

## Quality Hierarchy

Follow Quality > Token Cost > Efficiency hierarchy per P15 when making trade-off decisions.

- **Quality (10/10)**: Takes priority over token cost and efficiency
- **Token Cost (10/10)**: Optimized secondarily
- **Efficiency (10/10)**: Optimized thirdarily

For quality decisions, post: `✅ Quality Decision: {action}, Q/TC/E: {rating}/{rating}/{rating}, {reasoning}`