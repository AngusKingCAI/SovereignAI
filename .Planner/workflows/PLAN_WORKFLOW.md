# Plan Workflow

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Create original plans for the SovereignAI project based on Researcher design documents and requirements. Plans are executed by the Executor agent.

## Workflow Rule Index

| Rule ID | Trigger | Section |
|---------|---------|---------|
| W1 | Workflow integration vs separation | §1 |
| W2 | Round Table quality gates and panelist scoring | §2 |
| W3 | Panelist web search integration | §3 |
| W4 | Soft vs hard gate implementation | §4 |

## Workflow Design Rules

### §1 - Workflow Integration vs Separation (W1)

**Trigger**: Deciding whether to create separate workflow files vs integrating processes into main workflow  
**Situation**: Workflow design decisions affecting system structure and maintainability  
**Judgment**: Integrate coordination processes directly into main workflows rather than creating separate workflow files, unless the process has clear independent ownership and reuse across multiple workflows

**Detailed Rule**:
- **Centralized Coordination**: Integration and coordination processes should be centralized in the owning workflow to avoid scattered logic
- **Clear Ownership Boundaries**: Each workflow should remain authoritative in its domain without leaking logic into separate integration files
- **Bridge Not Merger**: Integration processes should act as coordination bridges within the workflow, not as separate merging points
- **Single Responsibility**: Each workflow file should handle its own coordination rather than delegating to separate workflow files
- **Compliance**: Post `✅ Gate W1 PASS: Workflow integration decision follows centralized coordination principle`

**Evidence**: BP findings support centralized workflow coordination over scattered integration logic to maintain clear ownership boundaries and prevent circular dependencies

### §2 - Round Table Quality Gates and Panelist Scoring (W2)

**Trigger**: Round Table workflow design and evaluation process  
**Situation**: Designing panelist evaluation, scoring, and quality gate mechanisms  
**Judgment**: Implement BP-based panelist scoring, independent evaluation, and threshold-based quality gates

**Detailed Rule**:
- **Independent Panelist Scoring**: Panelists must score independently (1-4 on rubric) before group discussion to prevent groupthink and anchoring bias
- **Competency-Based Assignment**: Map 3-5 core competencies to individual panelists with topic-based (not time-based) evaluation
- **4-Point Rubric**: Use structured 4-point rubrics with concrete behavioral indicators for each competency
- **Threshold-Based Quality Gates**: Clear pass/fail criteria (90-100 clean pass, 70-89 review with rationale, <70 block)
- **Evidence-First Debriefing**: Discuss evidence before scores to reduce anchoring bias
- **Performance Tracking**: Track panelist performance over time for optimization
- **Divergence Analysis**: Monitor feedback divergence to ensure independent thinking vs artificial convergence
- **Compliance**: Post `✅ Gate W2 PASS: Round Table evaluation follows BP scoring and quality gate principles`

**Evidence**: BP research shows structured panels reach r = .57 predictive validity with .74 interrater reliability when using independent scoring and clear rubrics

### §3 - Panelist Web Search Integration (W3)

**Trigger**: Round Table panelist evaluation process  
**Situation**: Deciding whether panelists should use web search for grounding their evaluations  
**Judgment**: Integrate web search for panelists to improve grounding, accuracy, and citation quality per BP

**Detailed Rule**:
- **Grounding Benefits**: Panelists use web search to ground evaluations in real-time, citable sources, replacing stale training knowledge
- **Source Accuracy**: Web search APIs provide 92% F-score on SimpleQA for improved accuracy
- **Citation Quality**: Structured, verifiable URLs enable panelists to cite evidence for findings
- **Context Engineering**: Ranked, LLM-optimized excerpts deliver relevant tokens efficiently
- **Cost-Value Tradeoff**: Accept web search cost per query for improved evaluation quality
- **Integration Pattern**: Search + answer pattern - panelists search when relevant evidence needed
- **Compliance**: Post `✅ Gate W3 PASS: Panelist web search integration improves grounding and accuracy`

**Evidence**: BP research shows web search improves source accuracy (92% F-score) and citation quality, with community consensus supporting Tavily for entry-level integration

### §4 - Soft vs Hard Gate Implementation (W4)

**Trigger**: Designing gate mechanisms for different agent roles  
**Situation**: Determining gate types for review (Round Table) vs execution (Planner) processes  
**Judgment**: Implement soft gates for Round Table review and hard gates for Planner execution per BP

**Detailed Rule**:
- **Round Table Soft Gates**: Review recommendations with documented rationale, not blocking - allows flexible evaluation
- **Planner Hard Gates**: Blocking tool-level constraints that cannot be overridden - ensures execution safety
- **Hard Gate Benefits**: Catch 100% of corrupt episodes vs 0% for soft-only, with minimal latency overhead (~23ms)
- **Soft Gate Use Cases**: Appropriate for evaluation, recommendations, and quality guidance where human judgment needed
- **Hard Gate Use Cases**: Appropriate for execution, state changes, and system modifications where safety critical
- **Dual-Gate Governance**: Policy enforcement at both decision-time (authority, scope) and commit-time (parameters, runtime state)
- **Compliance**: Post `✅ Gate W4 PASS: Soft/hard gate implementation follows BP principles`

**Evidence**: BP research shows hard-gated verification catches 100% of corrupt episodes with zero false positives, while soft-only approach has 100% false positive rate

## Workflow Overview
```
Requirements → Plan Batch Creation → Individual Plan Creation → Brief Assembly → Panelist Prompt Creation → Round Table Review → Reviewer Pattern Analysis → Executor
```

## Phase 0: Plan Batch Creation

**Trigger**: User provides requirements for multiple related plans  
**Goal**: Create plan batch with grouped plans for efficient Round Table review

**Steps**:
1. **Batch Requirements Analysis**: Analyze requirements to identify related plans that can be batched
2. **Dependency Mapping**: Map dependencies between plans to determine optimal batch order
3. **Batch Structure Design**: Design batch structure with parent plans and sub-plans
4. **Vision Principles Assignment**: Assign vision principles to each plan in batch
5. **Rule Mapping**: Map AR and OR rules to each plan in batch
6. **Compliance**: Post `✅ Gate PLAN-0 PASS: Plan batch created, {N} plans in batch`

**Exit Gate**: Plan batch structure defined with dependencies and rule mappings

---

## Phase 1: Input Assessment

**Trigger**: User provides requirements or Researcher provides design documents  
**Goal**: Understand the scope and requirements for the plan

**Steps**:
1. **Read Design Documents**: Read Researcher design documents (if available)
2. **Assess Requirements**: Understand user requirements and constraints
3. **Scope Definition**: Define in-scope and out-of-scope deliverables
4. **Dependencies**: Identify dependencies and integration points
5. **Hard Gate Validation**: Run validation scripts per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1
   ```
6. **Compliance**: Post `✅ Gate PLAN-1 PASS: Requirements assessed, scope defined, hard gates validated`

**Hard Gates Enforcement**:
- **HG-1**: Incomplete or ambiguous requirements BLOCK plan creation (enforced by validation script)
- **HG-2**: Undefined scope boundaries BLOCK plan creation (enforced by validation script)
- **HG-3**: Infeasible dependencies BLOCK plan creation (enforced by validation script)

**Exit Gate**: Requirements fully understood and documented, hard gates passed

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
**Goal**: Verify plan passes all quality gates (PR7) with hard gate enforcement

**Steps**:
1. **Completeness Check**: Verify all required sections are present
2. **Clarity Check**: Verify plan language is clear and unambiguous
3. **Specificity Check**: Verify plan steps are specific and actionable
4. **Landmine Screening**: Screen plan against governance landmines (PR8)
5. **Hard Gate Validation**: Run validation scripts per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 4
   ```
6. **Compliance**: Post `✅ Gate PLAN-4 PASS: Quality gates verified, landmines screened, hard gates validated`

**Hard Gates Enforcement**:
- **HG-4**: Missing required sections BLOCK plan delivery (enforced by validation script)
- **HG-5**: Ambiguous or unclear language BLOCK plan delivery (enforced by validation script)
- **HG-6**: Blocking landmines BLOCK plan delivery (enforced by validation script)

**Exit Gate**: Plan passes all quality gates and hard gates

---

## Phase 5: Plan Finalization

**Trigger**: Quality gates verified  
**Goal**: Finalize plan for delivery to Round Table

**Steps**:
1. **Final Review**: Conduct final review of complete plan
2. **Compliance Check**: Verify all compliance lines are present
3. **Path Validation**: Final validation of all referenced paths
4. **Manifest Validation**: Verify Executor Manifest is complete (PR5)
5. **Hard Gate Validation**: Run validation scripts per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 5
   ```
6. **Compliance**: Post `✅ Gate PLAN-5 PASS: Plan finalized, ready for Round Table, hard gates validated`

**Hard Gates Enforcement**:
- **HG-7**: Missing compliance lines BLOCK plan delivery (enforced by validation script)
- **HG-8**: Invalid or non-repo-relative paths BLOCK plan delivery (enforced by validation script)
- **HG-9**: Incomplete Executor Manifest BLOCK plan delivery (enforced by validation script)

**Exit Gate**: Plan ready for Round Table review

---

## Phase 6: Round Table Review

**Trigger**: Plan finalized  
**Goal**: Conduct Round Table review with 6 Chathub panelists following BP-based evaluation process

### Phase 6.1: Pre-Round Table Preparation (BP-Based)

**Steps**:
1. **Governance Document Re-Reading**: Re-read governance documents to ensure up-to-date context
   - Read UNIVERSAL_RULES.md, PLANNER_RULES.md
   - Post: `✅ Gate PLAN-6.1 PASS: Governance documents re-read`
2. **Plan Screening**: Screen plan against governance landmines and quality criteria
   - Check for blocking issues that must be fixed before Round Table
   - Post: `✅ Gate PLAN-6.2 PASS: Plan screened, {N} blocking issues found/none`
3. **Competency Definition**: Define 3-5 core competencies for panelist evaluation (per BP)
   - Identify key evaluation dimensions: technical skill, domain knowledge, communication, cross-team impact, governance compliance
   - Map competencies to plan-specific requirements
   - Post: `✅ Gate PLAN-6.3 PASS: Competencies defined, {N} core competencies identified`
4. **Panelist Profile Assembly**: Create panelist profiles with competency assignments (per BP)
   - Panelist metadata: name, model, expertise areas, assigned competencies
   - Topic-based assignment: each panelist owns specific competency areas
   - Post: `✅ Gate PLAN-6.4 PASS: Panelist profiles assembled, {N} panelists with competency assignments`
5. **Scoring Rubric Preparation**: Prepare 4-point scoring rubric with concrete descriptors (per BP)
   - Define 1-4 scale for each competency with specific behavioral indicators
   - Ensure rubric eliminates subjective "gut-feel" scores
   - Post: `✅ Gate PLAN-6.5 PASS: Scoring rubric prepared, 4-point scale with concrete descriptors`
6. **Brief Assembly**: Assemble comprehensive brief with 12-section structure (Rev 1 only, unless user requests for Rev 2+)
   - Context, Plans in batch, Rules carried forward, Questions for Round Table, Open questions resolved, Risks flagged, Coverage target, Round Table protocol reminder, Superseded rules, Panelist profiles, Scoring rubric
   - Post: `✅ Gate PLAN-6.6 PASS: Brief assembled, {N} sections, {lines} lines`
7. **Panelist Prompt Creation**: Create explicit prompts for each panelist (per BP)
   - Competency-specific prompts for each panelist's assigned areas
   - Web search integration instructions
   - Scoring guidelines with rubric references
   - Independent scoring instructions (score before seeing others' feedback)
   - Post: `✅ Gate PLAN-6.7 PASS: Panelist prompts created, {N} competency-specific prompts`

**Exit Gate**: Plan screened, competencies defined, panelists profiled, rubric prepared, brief assembled, prompts created

### Phase 6.2: Panelist Evaluation (BP-Based with Web Search)

**Steps**:
1. **Panelist Intake**: User provides panelist metadata (name, model) and review text for each of 6 panelists
2. **Competency Verification**: Verify panelists are evaluating their assigned competencies per brief
3. **Web Search Integration**: Panelists use web search when relevant evidence needed (per Rule W3)
   - Panelists can search for current best practices, similar implementations, or technical context
   - Search results provide grounding, citations, and real-time accuracy (92% F-score on SimpleQA)
   - Structured, verifiable URLs enable evidence-based findings
4. **Independent Scoring**: Panelists score independently (1-4 on rubric) before group discussion to prevent groupthink
5. **Text Preparation**: Parse and normalize panelist replies (extract signatures, clean headers, extract web search citations)
6. **Schema-Based Extraction**: Extract structured findings using predefined schema (category, severity, description, context, plan_impact, citations)
7. **Rule-Based Validation**: Validate extracted findings against schema rules (valid categories, severities, confidence ranges)
8. **Confidence Scoring**: Score extraction quality based on completeness, consistency, text coverage, and citation quality
9. **Database Storage**: Store validated findings in SQLite with automatic audit trail via triggers (include web search citations)
10. **Verdict Collection**: Collect Pass/Conditional/Block verdicts from panelists (soft gates per Rule W4)
11. **Panelist Performance Tracking**: Score each panelist 1-100 with weighted acceptance criteria
12. **Compliance**: Post `✅ Gate PLAN-6.8 PASS: Round Table review completed, findings captured, panelists scored with web search integration`

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
      "confidence": 0.0-1.0,
      "competency": "technical|domain|communication|impact|governance",
      "citations": ["url1", "url2"] (optional, from web search)
    }
  ],
  "verdict": "Pass|Conditional|Block",
  "overall_confidence": 1-10,
  "panelist_score": 1-100,
  "web_search_used": true/false,
  "rubric_score": 1-4,
  "summary": "string"
}
```

**Scoring System Clarification**:
- **Rubric Score (1-4)**: Panelist scores each assigned competency using 4-point rubric with behavioral indicators
- **Panelist Score (1-100)**: Overall panelist performance tracking for optimization across multiple evaluations

**Quality Gates**:
- Minimum confidence score of 70/100 required for each panelist extraction
- At least 4 out of 6 panelists must provide valid reviews (BP: majority >50%)
- Severity levels must follow CRITICAL > HIGH > MEDIUM > LOW hierarchy
- Independent scoring enforced (panelists score before seeing others' feedback)
- **Soft Gates**: Round Table recommendations are non-blocking (per Rule W4) - allow flexible evaluation with documented rationale
- **Web Search Quality**: Citations must be structured, verifiable URLs (per Rule W3) - ensures evidence-based findings

**Exit Gate**: All panelist reviews captured, scored, and stored in database

### Phase 6.3: Evidence-First Debriefing (BP-Based)

**Steps**:
1. **Evidence Review**: Review panelist findings focusing on evidence before scores
2. **Divergence Analysis**: Analyze feedback divergence to ensure independent thinking vs artificial convergence
3. **Score Discussion**: Discuss score divergences with evidence-based reasoning
4. **Compliance**: Post `✅ Gate PLAN-6.9 PASS: Evidence-first debriefing completed, divergence analyzed`

**Exit Gate**: Panelist findings reviewed with evidence-first approach

### Phase 6.4: Clean Pass Gate (BP-Based Soft Gates with Hard Gate Enforcement)

**Steps**:
1. **Quality Gate Evaluation**: Apply threshold-based quality gates per BP (soft gates per Rule W4)
   - **90-100**: Clean pass — proceed to delivery (soft recommendation)
   - **70-89**: Review findings — proceed with documented rationale (soft recommendation)
   - **<70**: Recommend additional Round Table round (soft recommendation)
2. **Verification Checklist**: Verify critical criteria met
   - Panelist majority achieved (>50%)
   - All CRITICAL and HIGH findings addressed
   - MEDIUM findings addressed or documented
   - Clean pass score ≥90 OR documented rationale for 70-89
   - Executor Manifest present in plan
   - No blocking landmines
3. **Soft Gate Documentation**: Document rationale for any score <90 (soft gate allows override with reasoning)
4. **Soft Gate Validation**: Run soft gate validation scripts (non-blocking, output warnings)
   ```bash
   python .Planner/scripts/soft_gates/sg1_score_below_70.py
   python .Planner/scripts/soft_gates/sg2_score_70_89.py
   python .Planner/scripts/soft_gates/sg3_panelist_majority.py
   ```
5. **Hard Gate Validation**: Run hard gate validation scripts (blocking, enforces exit conditions)
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 6
   ```
6. **Compliance**: Post `✅ Gate PLAN-6.10 PASS: Clean pass soft gate achieved, hard gates validated, score: {score}/100, rationale: {if applicable}`

**Soft Gates Enforcement** (Non-Blocking):
- **SG-1**: Score <70 with documented rationale may proceed with user approval (enforced by `.Planner/scripts/soft_gates/sg1_score_below_70.py`)
- **SG-2**: Score 70-89 with documented rationale may proceed (enforced by `.Planner/scripts/soft_gates/sg2_score_70_89.py`)
- **SG-3**: Panelist majority not achieved may proceed with documented rationale (enforced by `.Planner/scripts/soft_gates/sg3_panelist_majority.py`)

**Soft Gate Behavior**:
- **Always Return 0**: Soft gate scripts always return exit code 0 (non-blocking)
- **Warning Output**: Soft gates output warnings when violated with rationale requirements
- **User Decision**: Soft gates provide recommendations but allow user override with proper documentation
- **Monitoring**: Track soft gate violations for pattern analysis and potential hard gate conversion
- **Per AGENTS.md G6**: Soft gate enforcement defined in AGENTS.md with script-based implementation

**Hard Gates Enforcement** (Blocking):
- **HG-10**: Unaddressed CRITICAL findings BLOCK plan delivery (enforced by validation script)
- **HG-11**: Unaddressed HIGH findings BLOCK plan delivery (enforced by validation script)
- **HG-12**: Blocking landmines present BLOCK plan delivery (enforced by validation script)
- **HG-13**: Executor Manifest missing BLOCK plan delivery (enforced by validation script)

**Exit Gate**: Clean pass soft gate achieved, hard blocking conditions validated via scripts, plan ready for pattern analysis

---

## Brief Structure and Panelist Prompts (BP-Based)

**Brief Structure (12 Sections)**:
1. **Context**: Project background and batch objectives
2. **Plans in Batch**: List of all plans in batch with dependencies
3. **Rules Carried Forward**: AR and OR rules applicable to batch
4. **Questions for Round Table**: Specific questions for panelists to address
5. **Open Questions Resolved**: Previously open questions now resolved
6. **Risks Flagged**: Known risks and mitigation strategies
7. **Coverage Target**: Expected coverage targets for each plan
8. **Round Table Protocol Reminder**: Evaluation format and expectations
9. **Superseded Rules**: Rules that have been superseded in this batch
10. **Panelist Profiles**: Panelist metadata, expertise areas, competency assignments
11. **Scoring Rubric**: 4-point scale with concrete descriptors for each competency
12. **Panelist Prompts**: Competency-specific prompts for each panelist

**Panelist Prompt Template**:
```markdown
## Panelist {Name} - {Model} Evaluation Prompt

**Assigned Competencies**: {competency1}, {competency2}
**Expertise Area**: {domain expertise}

**Evaluation Instructions**:
1. Review the plan focusing on your assigned competencies: {competency1}, {competency2}
2. Use web search to validate technical assumptions and best practices when relevant
3. Score the plan on your assigned competencies using the 4-point rubric provided
4. Submit your score independently before seeing other panelists' feedback
5. Provide specific findings with severity levels (CRITICAL, HIGH, MEDIUM, LOW)
6. Include citations from web search to support your findings

**Scoring Rubric - {Competency}**:
- **4 (Excellent)**: {specific behavioral indicators}
- **3 (Good)**: {specific behavioral indicators}
- **2 (Fair)**: {specific behavioral indicators}
- **1 (Poor)**: {specific behavioral indicators}

**Web Search Integration**:
- Use web search for: {specific search topics relevant to competency}
- Include citations in format: [Title](URL)
- Prioritize authoritative sources (documentation, official guides, best practices)

**Independent Scoring Requirement**:
Submit your scores (1-4 for each assigned competency) before reviewing other panelists' feedback to prevent groupthink.
```

---

---

## Phase 7: Reviewer Pattern Analysis

**Trigger**: Round Table review complete  
**Goal**: Handoff findings database to Reviewer for pattern analysis and rule integration (per GR3 single-responsibility)

**Steps**:
1. **Handoff to Reviewer**: Transfer findings database to Reviewer for pattern analysis
2. **Findings Export**: Export findings to JSON for Reviewer analysis
3. **Handoff Notification**: Notify Reviewer that findings are ready for analysis
4. **Compliance**: Post `✅ Gate PLAN-7 PASS: Findings handed off to Reviewer for pattern analysis and rule integration`

**Exit Gate**: Findings transferred to Reviewer for analysis

---

## Universal Rules Compliance

**All phases must follow**:
- **GR1-GR5**: Universal governance rules (agent responsibilities, single-responsibility, handoff boundaries)
- **ER1-ER5**: Universal editing rules (file editing best practices, large changes, failure recovery)
- **PR1-PR15**: Planner-specific rules (plan creation, structure, quality gates)
- **PR16**: Universal rules integration
- **W1-W4**: Plan workflow design rules (workflow integration, panelist scoring, web search, soft/hard gates)

## Planner Hard Gates (Blocking Constraints per Rule W4)

**Phase-Level Hard Gates**:
- **HG-1**: Incomplete or ambiguous requirements BLOCK plan creation
- **HG-2**: Undefined scope boundaries BLOCK plan creation
- **HG-3**: Infeasible dependencies BLOCK plan creation
- **HG-4**: Missing required sections BLOCK plan delivery
- **HG-5**: Ambiguous or unclear language BLOCK plan delivery
- **HG-6**: Blocking landmines BLOCK plan delivery
- **HG-7**: Missing compliance lines BLOCK plan delivery
- **HG-8**: Invalid or non-repo-relative paths BLOCK plan delivery
- **HG-9**: Incomplete Executor Manifest BLOCK plan delivery
- **HG-10**: Unaddressed CRITICAL findings BLOCK plan delivery
- **HG-11**: Unaddressed HIGH findings BLOCK plan delivery
- **HG-12**: Blocking landmines present BLOCK plan delivery
- **HG-13**: Executor Manifest missing BLOCK plan delivery

## Round Table Soft Gates (Non-Blocking Recommendations per Rule W4)

**Evaluation-Level Soft Gates** (Non-Blocking):
- **SG-1**: Score <70 with documented rationale may proceed with user approval (enforced by sg1_score_below_70.py)
- **SG-2**: Score 70-89 with documented rationale may proceed (enforced by sg2_score_70_89.py)
- **SG-3**: Panelist majority not achieved may proceed with documented rationale (enforced by sg3_panelist_majority.py)

**Soft Gate Enforcement Mechanism**:
- **Non-Blocking**: Soft gate scripts always return exit code 0 (never block execution)
- **Warning Output**: Soft gates output warnings when violated with rationale requirements
- **User Decision**: Soft gates provide recommendations but allow user override with proper documentation
- **Validation Scripts**: Soft gates enforced by Python scripts in `.Planner/scripts/soft_gates/`
- **Monitoring**: Track soft gate violations for pattern analysis and potential hard gate conversion
- **A1-A4**: Architect workflow design rules (workflow integration, panelist scoring, web search, soft/hard gates)

## Hard Gates Summary

**Planner Hard Gates** (blocking constraints per Rule A4):
- **HG-1**: Incomplete or ambiguous requirements BLOCK plan creation
- **HG-2**: Undefined scope boundaries BLOCK plan creation
- **HG-3**: Infeasible dependencies BLOCK plan creation
- **HG-4**: Missing required sections BLOCK plan delivery
- **HG-5**: Ambiguous or unclear language BLOCK plan delivery
- **HG-6**: Blocking landmines BLOCK plan delivery
- **HG-7**: Missing compliance lines BLOCK plan delivery
- **HG-8**: Invalid or non-repo-relative paths BLOCK plan delivery
- **HG-9**: Incomplete Executor Manifest BLOCK plan delivery
- **HG-10**: Unaddressed CRITICAL findings BLOCK plan delivery
- **HG-11**: Unaddressed HIGH findings BLOCK plan delivery
- **HG-12**: Blocking landmines present BLOCK plan delivery
- **HG-13**: Executor Manifest missing BLOCK plan delivery

**Round Table Soft Gates** (non-blocking recommendations per Rule A4):
- **SG-1**: Score <70 with documented rationale may proceed with user approval (enforced by `.Planner/scripts/soft_gates/sg1_score_below_70.py`)
- **SG-2**: Score 70-89 with documented rationale may proceed (enforced by `.Planner/scripts/soft_gates/sg2_score_70_89.py`)
- **SG-3**: Panelist majority not achieved may proceed with documented rationale (enforced by `.Planner/scripts/soft_gates/sg3_panelist_majority.py`)

**Soft Gate Enforcement Mechanism**:
- **Non-Blocking**: Soft gate scripts always return exit code 0 (never block execution)
- **Warning Output**: Soft gates output warnings when violated with rationale requirements
- **User Decision**: Soft gates provide recommendations but allow user override with proper documentation
- **Validation Scripts**: Soft gates enforced by Python scripts in `.Planner/scripts/soft_gates/`
- **Monitoring**: Track soft gate violations for pattern analysis and potential hard gate conversion

---

## Stop Conditions

**Halt execution if** (Hard Gates Only):
- Missing compliance line for any gate
- Plan fails quality gates (PR7)
- Plan contains governance landmines (PR8)
- Plan has invalid manifest (PR5)
- Paths are not repo-relative (PR2)

**Soft Gate Warnings** (Non-Blocking):
- Score <70 with documented rationale may proceed
- Score 70-89 with documented rationale may proceed
- Panelist majority not achieved may proceed with documented rationale
- Soft gates never halt execution per AGENTS.md G6

---

## Evolution

**This workflow evolves when**:
- Plan structure requirements change
- Quality gate criteria change
- Workflow integration points change
- Governance rules are updated