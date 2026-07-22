# Plan Workflow

**Version**: 1.2  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Create original plans for the SovereignAI project based on Researcher design documents and requirements. Plans are executed by the Executor agent.

## Workflow Rule Index

| Rule ID | Trigger | Section | Line |
|---------|---------|---------|------|
| W1 | Workflow integration vs separation | §1 | 26 |
| W2 | Round Table quality gates and panelist scoring | §2 | 41 |
| W3 | Panelist web search integration | §3 | 59 |
| W4 | Soft vs hard gate implementation | §4 | 76 |
| W5 | Context budgeting for token limits | §5 | 93 |
| W6 | Spec-first validation pattern | §6 | 111 |
| W7 | Hierarchical goal decomposition | §7 | 129 |
| W8 | Runtime guardrail hooks | §8 | 148 |
| W9 | Durable execution & checkpointing | §9 | 167 |

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

### §5 - Context Budgeting for Token Limits (W5)

**Trigger**: Creating briefs, panelist prompts, or plans  
**Situation**: Determining appropriate token limits for workflow components to prevent context rot  
**Judgment**: Implement token budget limits per Anthropic research for context window optimization

**Detailed Rule**:
- **Brief Token Budget**: 13,000 tokens (~9,750 words) - prevents briefs from becoming full plans
- **Panelist Prompt Budget**: 6,500 tokens per prompt (~4,875 words) - prevents prompts from becoming overwhelming
- **Plan Token Budget**: 70,000 tokens (~52,500 words) - prevents plans from becoming comprehensive documentation
- **Context Budget Enforcement**: Hard gates (HG-16, HG-17) + soft gates (SG-6, SG-7) for budget validation
- **Token Counting Method**: Approximate token counting (1 token ≈ 4 characters) sufficient for budget validation
- **Budget Rationale**: Context treated as finite resource with diminishing returns per Anthropic research
- **Model Compatibility**: Based on 256K context window (Kimi K2.7 Code) for cross-model support
- **Compliance**: Post `✅ Gate W5 PASS: Context budgeting follows research limits for model compatibility`

**Evidence**: Anthropic research shows context budgeting is the single most important factor for agent reliability, with optimal context windows at 50-70% of maximum capacity for best results

### §6 - Spec-First Validation Pattern (W6)

**Trigger**: Plan structure design and plan drafting phases  
**Situation**: Validating plan structure before detailed drafting to catch structural defects early  
**Judgment**: Implement spec-first validation pattern (Kerno-inspired) to separate plan spec from plan body

**Detailed Rule**:
- **Spec Generation**: Generate plan spec (header + Executor Manifest shell + phase list + deliverable names + gate names) before detailed drafting
- **Spec Review Gate**: Add Phase 2.5 between structure design and drafting for spec validation
- **Spec Approval**: Architect/Reviewer validates spec against PR1, PR2, PR5, PR6 rules before proceeding
- **Spec-Diff Validation**: Add Phase 4.5 after quality gates to compare final plan against approved spec
- **Drift Detection**: Identify structural changes (phases added/removed, deliverables changed, gates modified)
- **Drift Resolution**: Either get approval for changes or revert to approved spec
- **Early Defect Detection**: Catches structural defects at cheapest intervention point (before body drafting)
- **Compliance**: Post `✅ Gate W6 PASS: Spec-first validation pattern implemented, structural drift prevented`

**Evidence**: Kerno research shows spec-first validation catches abstraction leaks in 2 minutes of review that would have cost hours to fix post-implementation

### §7 - Hierarchical Goal Decomposition (W7)

**Trigger**: Plan batch creation and dependency mapping  
**Situation**: Plan batches must use hierarchical goal decomposition instead of flat dependency graphs  
**Judgment**: Implement hierarchical goal trees with inheritance and blocking propagation per Galileo research

**Detailed Rule**:
- **Goal tree per batch**: Create hierarchical goal tree with main goal, sub-goals, and sub-tasks
- **Tree structure**: Main goal → Sub-goals → Sub-tasks with parent-child relationships
- **Inheritance**: Each sub-goal inherits vision principles, AR rules, and OR rules from its parent
- **Goal tree artifact**: Generate goal tree artifact in `plans/goal-tree-batch{N}.md` during Phase 0
- **Blocking propagation**: If parent plan STOPs, all descendant plans in goal tree also STOP (binary blocking)
- **Coverage tracking per goal**: Each sub-goal has its own coverage target (≥90%), batch coverage is weighted average
- **Goal tree JSON**: Store goal tree structure in `batches.goal_tree_json` column for programmatic access
- **Dependency mapping**: Map dependencies between plans in goal tree (parent-child relationships)
- **Compliance**: Post `✅ Gate W7 PASS: Hierarchical goal decomposition completed, {N} sub-goals, {N} levels`

**Evidence**: Galileo's Strategy #2 emphasizes hierarchical goal decomposition for complex task coordination and blocking propagation for cascade failure prevention

### §8 - Runtime Guardrail Hooks (W8)

**Trigger**: Plan file modifications, session lifecycle events  
**Situation**: Hard gates must be unbypassable via runtime hooks instead of manual invocation  
**Judgment**: Implement Devin hooks for automatic enforcement of validation gates per AWS and Galileo research

**Detailed Rule**:
- **PreToolUse hook**: Before any file write to `plans/`, automatically run validation gates (HG-7, HG-8, HG-9). If any fails, block the write.
- **PostToolUse hook**: After any plan file modification, automatically update workflow state and re-run phase gates for current phase.
- **SessionStart hook**: On session start, query workflow state and print "Resuming from Phase X.Y" for state awareness.
- **SessionEnd hook**: On session end, write checkpoint with current phase, pending items, and unposted compliance lines.
- **Unbypassable enforcement**: Hooks execute deterministically on every matching tool call - agent cannot skip validation.
- **Hook configuration**: Configure in `.devin/hooks.v1.json` following Claude Code compatible format.
- **Exit code blocking**: Exit code 0 = allow, exit code 2 = block, exit code 1 = warn but allow.
- **Hook scripts**: Create hook scripts in `.Planner/scripts/hooks/` for PreToolUse, PostToolUse, SessionStart, SessionEnd.
- **Compliance**: Post `✅ Gate W8 PASS: Runtime guardrail hooks configured and active`

**Evidence**: AWS prescriptive guidance and Galileo's Strategy #8 both emphasize runtime guardrails that cannot be bypassed by agents

### §9 - Durable Execution & Checkpointing (W9)

**Trigger**: Phase completion, session end, on-demand checkpointing  
**Situation**: Long-running plan execution may be interrupted and must be resumable from last checkpoint  
**Judgment**: Implement checkpointing system that saves workflow state, phase progress, and pending items for session resumption

**Detailed Rule**:
- **Checkpoint format**: JSON checkpoint file with current phase, pending items, compliance lines, and execution state
- **Checkpoint location**: `.Planner/checkpoints/checkpoint-{timestamp}.json` in project directory
- **Checkpoint triggers**: Automatic checkpoint after each phase completion, session end, and on demand
- **State restoration**: SessionStart hook reads latest checkpoint and prints "Resuming from Phase X.Y"
- **Checkpoint content**: Include phase progress, pending items, compliance lines, plan file references, and execution metadata
- **Recovery validation**: On resumption, validate checkpoint integrity and consistency with current file state
- **Rollback support**: Support rollback to previous checkpoint if execution state is corrupted
- **Compliance**: Post `✅ Gate W9 PASS: Checkpoint created at Phase X.Y, state persisted for recovery`

**Evidence**: Galileo's Strategy #8 emphasizes durable execution with checkpointing for reliability and recovery

## Workflow Overview
```
Requirements → Plan Batch Creation → Individual Plan Creation → Brief Assembly → Panelist Prompt Creation → Round Table Review → Reviewer Pattern Analysis → Executor
```

**Note**: Phase 0 (Plan Batch Creation) is optional - only triggered when user provides requirements for multiple related plans. Single plans skip Phase 0 and start at Phase 1.

**Runtime Guardrail Integration**: 
- **Hook-based enforcement**: Hard gates are enforced via `.devin/hooks.v1.json` hooks (PreToolUse, PostToolUse)
- **Unbypassable validation**: Plan file modifications automatically trigger validation gates (HG-7, HG-8, HG-9) before write
- **State tracking**: SessionStart/SessionEnd hooks provide state awareness and checkpointing
- **Manual invocation still supported**: Agents can still manually run `python .Planner/scripts/hard_gates/run_phase_gates.py --phase {N}` for explicit validation

**Gate Design Note**: Phase 0 is deliberately un-gated (no hard gates) because it is an optional batch optimization phase rather than a core plan creation phase. Quality gates are applied in subsequent phases (Phase 1-6) where actual plan validation occurs.

## Phase 0: Plan Batch Creation

**Trigger**: User provides requirements for multiple related plans  
**Goal**: Create plan batch with grouped plans for efficient Round Table review

**Gate Design**: Phase 0 is deliberately un-gated (no hard gates) because it is an optional batch optimization phase rather than a core plan creation phase. Quality gates are applied in subsequent phases (Phase 1-6) where actual plan validation occurs.

**Steps**:
1. **Batch Requirements Analysis**: Analyze requirements to identify related plans that can be batched
2. **Hierarchical Goal Decomposition**: Create goal tree with main goal, sub-goals, sub-tasks (per PR19)
3. **Goal Tree Artifact**: Generate goal tree artifact in `plans/goal-tree-batch{N}.md` with hierarchical structure
4. **Inheritance Mapping**: Map vision principles, AR rules, and OR rules inheritance from parent to sub-goals
5. **Dependency Mapping**: Map dependencies between plans in goal tree (parent-child relationships)
6. **Batch Structure Design**: Design batch structure with parent plans and sub-plans
7. **Vision Principles Assignment**: Assign vision principles to each plan in batch (inherited from parent)
8. **Rule Mapping**: Map AR and OR rules to each plan in batch (inherited from parent)
9. **Context Budget Validation**: Run brief token budget validation per CONTEXT_BUDGET_POLICY.md
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 0
   ```
10. **Compliance**: Post `✅ Gate PLAN-0 PASS: Plan batch created, {N} plans in batch, goal tree hierarchical, context budget validated`

**Hard Gates Enforcement**:
- **HG-16**: Brief token budget violation (≤13,000 tokens) BLOCKS brief creation (enforced by validation script)
- **HG-20**: Goal tree missing or incomplete BLOCKS batch execution (enforced by validation script)

**Soft Gates Enforcement**:
- **SG-6**: Brief token budget warning (≤13,000 tokens) - warns if budget exceeded, non-blocking

**Exit Gate**: Plan batch structure defined with dependencies and rule mappings

---

## Phase 1: Input Assessment

**Trigger**: User provides requirements or Researcher provides design documents (single plan) OR Phase 0 complete (batch plan)  
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

**Note**: For batch plans, this phase is executed for each individual plan in the batch after Phase 0 completes.

---

## Phase 2: Plan Structure Design

**Trigger**: Input assessment complete  
**Goal**: Design plan structure following PR1-PR21 and GR1-GR5

**Steps**:
1. **Header Design**: Create plan header with Vision principles, PR rules reference
2. **Manifest Design**: Design Executor Manifest with phases, deliverables, gates
3. **Phase Planning**: Break down work into executable phases
4. **Quality Gates**: Define verification gates for each phase
5. **Runtime Guardrail**: PreToolUse hook automatically validates plan structure (HG-14) on file write
6. **Compliance**: Post `✅ Gate PLAN-2 PASS: Plan structure designed, gates defined, runtime guardrail active`

**Exit Gate**: Plan structure follows PR1-PR21 requirements

---

## Phase 2.5: Spec Review Gate (Spec-First Validation)

**Trigger**: Plan structure design complete
**Goal**: Validate plan spec before detailed drafting (Kerno-inspired spec-first validation)

**Steps**:
1. **Spec Generation**: Generate plan spec (header + Executor Manifest shell + phase list + deliverable names + gate names)
2. **Spec Validation**: Architect/Reviewer validates spec against PR1, PR2, PR5, PR6 rules
3. **Spec Approval**: Get spec approval before proceeding to detailed drafting
4. **Hard Gate Validation**: Run validation script per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 2.5
   ```
5. **Compliance**: Post `✅ Gate PLAN-2.5 PASS: Plan spec approved, {N} phases, {N} deliverables`

**Hard Gates Enforcement**:
- **HG-18**: Plan spec not approved (Phase 2.5 compliance line missing) BLOCKS plan drafting (enforced by validation script)

**Exit Gate**: Plan spec approved, ready for detailed drafting

**Note**: This catches structural defects at the cheapest intervention point (before body drafting), per Kerno research.

---

## Phase 3: Plan Drafting

**Trigger**: Plan structure designed  
**Goal**: Draft complete plan with detailed steps

**Steps**:
1. **Header Completion**: Complete plan header with all required sections
2. **Manifest Completion**: Complete Executor Manifest with all required information
3. **Phase Details**: Fill in detailed steps for each phase
4. **Path Verification**: Ensure all paths are repo-relative (PR2)
5. **Runtime Guardrail**: PreToolUse hook automatically validates path requirements (HG-15) on file write
6. **Compliance**: Post `✅ Gate PLAN-3 PASS: Plan drafted, paths verified, runtime guardrail active`

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

## Phase 4.5: Spec-Diff Validation (Spec-First Validation)

**Trigger**: Quality gates verified
**Goal**: Validate final plan structure matches approved spec (catches structural drift)

**Steps**:
1. **Spec Regeneration**: Regenerate spec from final plan (header + Executor Manifest + phase list + deliverables + gates)
2. **Spec Comparison**: Compare regenerated spec against approved spec from Phase 2.5
3. **Drift Detection**: Identify structural changes (phases added/removed, deliverables changed, gates modified)
4. **Drift Resolution**: Either get approval for changes or revert to approved spec
5. **Hard Gate Validation**: Run validation script per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 4.5
   ```
6. **Compliance**: Post `✅ Gate PLAN-4.5 PASS: Spec diff clean, no structural drift detected`

**Hard Gates Enforcement**:
- **HG-19**: Spec diff violations (structural drift detected) BLOCKS plan finalization (enforced by validation script)

**Exit Gate**: Final plan structure matches approved spec, ready for finalization

**Note**: This catches drift that occurred during drafting (e.g., phases added that weren't in approved spec), per Kerno research.

---

## Phase 5: Plan Finalization

**Trigger**: Quality gates verified  
**Goal**: Finalize plan for delivery to Round Table

**Steps**:
1. **Final Review**: Conduct final review of complete plan
2. **Compliance Check**: Verify all compliance lines are present
3. **Path Validation**: Final validation of all referenced paths
4. **Manifest Validation**: Verify Executor Manifest is complete (PR5)
5. **Runtime Guardrail**: PreToolUse hook automatically validates compliance lines (HG-7), paths (HG-8), and manifest (HG-9) on file write
6. **Hard Gate Validation**: Run validation scripts per AGENTS.md enforcement mechanism
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 5
   ```
7. **Compliance**: Post `✅ Gate PLAN-5 PASS: Plan finalized, ready for Round Table, hard gates validated, runtime guardrail active`

**Hard Gates Enforcement**:
- **HG-7**: Missing compliance lines BLOCK plan delivery (enforced by validation script)
- **HG-8**: Invalid or non-repo-relative paths BLOCK plan delivery (enforced by validation script)
- **HG-9**: Incomplete Executor Manifest BLOCK plan delivery (enforced by validation script)

**Exit Gate**: Plan ready for Round Table review

---

## Phase 6: Round Table Review

**Trigger**: Plan finalized  
**Goal**: Conduct Round Table review with 6 Chathub panelists following BP-based evaluation process

### Phase 6.0: Architect Self-Check (Restored from Old Workflow)

**Trigger**: Plan finalized, before Round Table preparation  
**Goal**: Self-identify and fix issues the Planner can catch itself before expensive panelist rounds

**Gate Design**: Self-check is a zero-cost internal pass that catches issues the Planner could catch itself, reducing the number of findings the real panel needs to surface. This saves panelist resources and reduces Rev 2+ rounds.

**Steps**:
1. **Rubric Self-Check**: Planner applies the 4-point rubric to its own draft, per competency
   - Self-evaluate plan against the same rubric used by panelists
   - Identify areas where plan falls below 3/4 on any competency
   - Post: `✅ Gate PLAN-6.0-RUBRIC PASS: Rubric self-check complete, {N} competencies below threshold`
2. **Pattern Self-Check**: Planner checks draft against known patterns from PATTERN_LIBRARY.md
   - Compare plan structure and content against known anti-patterns
   - Identify common issues that have been flagged in previous reviews
   - Post: `✅ Gate PLAN-6.0-PATTERN PASS: Pattern self-check complete, {N} anti-patterns detected`
3. **Self-Fix**: Planner fixes any self-identified CRITICAL/HIGH findings before delivering to Round Table
   - Fix structural issues, missing sections, compliance violations
   - Update plan with fixes and re-validate against hard gates
   - Post: `✅ Gate PLAN-6.0-FIX PASS: Self-fix complete, {N} findings self-fixed`
4. **Defer-with-Reasoning**: Document deferred findings with reasoning for panel validation
   - Findings that are self-identified but kept for panel validation with reasoning
   - Example: "Self-identified but kept for panel validation because complexity requires expert review"
   - Post: `Gate PLAN-6.0 PASS: Self-check complete, {N} findings self-fixed, {N} deferred to Round Table`

**Soft Gate Enforcement**:
- **SG-5**: Warn if Phase 6.0 compliance line missing (non-blocking but alerts to skipped self-check)

**Exit Gate**: Plan with self-identified issues resolved, ready for Round Table preparation

---

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
8. **Context Budget Validation**: Run panelist prompt token budget validation per CONTEXT_BUDGET_POLICY.md
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 6
   ```
   - Post: `✅ Gate PLAN-6.8 PASS: Context budget validated, all prompts within token limits`

**Hard Gates Enforcement**:
- **HG-17**: Panelist prompt token budget violation (≤6,500 tokens) BLOCKS Round Table execution (enforced by validation script)

**Soft Gates Enforcement**:
- **SG-7**: Panelist prompt token budget warning (≤6,500 tokens) - warns if budget exceeded, non-blocking

**Exit Gate**: Plan screened, competencies defined, panelists profiled, rubric prepared, brief assembled, prompts created, context budget validated

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
12. **Compliance**: Post `✅ Gate PLAN-6.9 PASS: Round Table review completed, findings captured, panelists scored with web search integration`

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
- **Context Budget**: Panelist prompts must respect token budget (≤6,500 tokens) per CONTEXT_BUDGET_POLICY.md (HG-17 + SG-7)
- **Evaluation Integrity**: Panelists never see their own scores or other panelists' scores (security principle)

**Exit Gate**: All panelist reviews captured, scored, and stored in database

### Phase 6.3: Evidence-First Debriefing (BP-Based)

**Steps**:
1. **Evidence Review**: Review panelist findings focusing on evidence before scores
2. **Divergence Analysis**: Analyze feedback divergence to ensure independent thinking vs artificial convergence
3. **Score Discussion**: Discuss score divergences with evidence-based reasoning
4. **Compliance**: Post `✅ Gate PLAN-6.10 PASS: Evidence-first debriefing completed, divergence analyzed`

**Exit Gate**: Panelist findings reviewed with evidence-first approach

### Phase 6.4: Clean Pass Gate (BP-Based Soft Gates with Hard Gate Enforcement)

**Evaluation Integrity Principle**: Panelists never see their own scores or other panelists' scores. All scoring is internal-only to prevent gaming the system and ensure honest evaluation.

**Steps**:
1. **Consensus Calculation**: Calculate confidence-weighted consensus from individual panelist reviews (internal, post-hoc by Planner)
   - **Weighted vote per panelist**: panelist_weight = (confidence_score / 10) × (expertise_match_score / 4) × (historical_accuracy / 100)
   - **Consensus threshold**: weighted support ≥70% of total possible weight AND no CRITICAL finding with confidence ≥8
   - **Conditional threshold**: weighted support 50-70%
   - **Block threshold**: weighted support <50% OR any CRITICAL finding with confidence ≥8
   - **Security**: All calculations are internal - panelists never see scores or consensus results
2. **Quality Gate Evaluation**: Apply threshold-based quality gates per BP (soft gates per Rule W4)
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
   python .Planner/scripts/soft_gates/sg7_panelist_prompt_token_budget.py
   ```
5. **Hard Gate Validation**: Run hard gate validation scripts (blocking, enforces exit conditions)
   ```bash
   python .Planner/scripts/hard_gates/run_phase_gates.py --phase 6
   ```
6. **Compliance**: Post `✅ Gate PLAN-6.11 PASS: Clean pass soft gate achieved, hard gates validated, score: {score}/100, rationale: {if applicable}`

**Soft Gates Enforcement** (Non-Blocking):
- **SG-1**: Score <70 with documented rationale may proceed with user approval (enforced by `.Planner/scripts/soft_gates/sg1_score_below_70.py`)
- **SG-2**: Score 70-89 with documented rationale may proceed (enforced by `.Planner/scripts/soft_gates/sg2_score_70_89.py`)
- **SG-3**: Panelist majority not achieved may proceed with documented rationale (enforced by `.Planner/scripts/soft_gates/sg3_panelist_majority.py`)
- **SG-7**: Panelist prompt token budget warning (≤6,500 tokens) - warns if budget exceeded, non-blocking (enforced by `.Planner/scripts/soft_gates/sg7_panelist_prompt_token_budget.py`)

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
- **HG-17**: Panelist prompt token budget violation (≤6,500 tokens) BLOCKS Round Table execution (enforced by validation script)

**Exit Gate**: Clean pass soft gate achieved, hard blocking conditions validated via scripts, context budget validated, plan ready for pattern analysis

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
- **PR1-PR21**: Planner-specific rules (plan creation, structure, quality gates, runtime guardrails, checkpointing)
- **PR16**: Universal rules integration
- **PR17**: Spec-first plan creation
- **PR18**: Confidence-weighted consensus
- **PR19**: Hierarchical goal decomposition
- **PR20**: Runtime guardrail hooks
- **PR21**: Durable execution & checkpointing
- **W1-W9**: Plan workflow design rules (workflow integration, panelist scoring, web search, soft/hard gates, context budgeting, spec-first validation, hierarchical decomposition, runtime guardrails, checkpointing)

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
- **W1-W4**: Workflow design rules (workflow integration, panelist scoring, web search, soft/hard gates)

## Hard Gates Summary

**Planner Hard Gates** (blocking constraints per Rule W4):
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

**Round Table Soft Gates** (non-blocking recommendations per Rule W4):
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