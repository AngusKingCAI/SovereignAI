# Planner Rules (PR1-PR22)

**Version**: 1.3  
**Last Updated**: 2026-07-22  
**Status**: Active

## Rule Index

| Rule ID | Trigger | Section | Line |
|---------|---------|---------|------|
| PR1 | Plan creation | §1 | 36 |
| PR2 | Path convention | §2 | 53 |
| PR3 | Design doc integration | §3 | 70 |
| PR4 | Devin integration | §4 | 87 |
| PR5 | Executor Manifest | §5 | 104 |
| PR6 | Plan structure | §6 | 122 |
| PR7 | Quality gates | §7 | 140 |
| PR8 | Landmine screening | §8 | 158 |
| PR9 | Reviewer integration | §9 | 176 |
| PR10 | Workflow integration | §10 | 194 |
| PR11 | Compliance posting | §11 | 212 |
| PR12 | Rule creation | §12 | 230 |
| PR13 | Rule lifecycle | §13 | 248 |
| PR14 | Stop conditions | §14 | 266 |
| PR15 | Token awareness | §15 | 284 |
| PR16 | Universal rules | §16 | 302 |
| PR17 | Spec-first plan creation | §17 | 320 |
| PR18 | Confidence-weighted consensus | §18 | 339 |
| PR19 | Hierarchical goal decomposition | §19 | 365 |
| PR20 | Runtime guardrail hooks | §20 | 386 |
| PR21 | Durable execution & checkpointing | §21 | 406 |
| PR22 | Competency-based subagent validation | §22 | 428 |

---

## §1 - Plan Creation (PR1)

**Trigger**: `plan creation`, `draft plan`, `create plan`  
**Situation**: Creating a new plan for the SovereignAI project  
**Judgment**: Plan header must include Vision principles, PR rules, and Open questions resolved

**Detailed Rule**:
- **Header requirements**: Every plan must include Vision principles section
- **PR rules reference**: Plan must reference applicable PR rules
- **Open questions**: All open questions must be resolved before plan delivery
- **Structure compliance**: Follow plan structure defined in PR6
- **Compliance**: Post `✅ Gate PR1 PASS: Plan header includes Vision principles, PR rules, and Open questions resolved`

**Evolution Condition**: Plan structure requirements change

---

## §2 - Path Convention (PR2)

**Trigger**: `path reference`, `file path`, `directory`  
**Situation**: Referencing file paths in plans  
**Judgment**: Use repo-relative paths only, no host-local paths in plans

**Detailed Rule**:
- **Repo-relative only**: All paths must be relative to repository root
- **No host-local paths**: Never use paths like `/Users/username/...` or `C:\Users\...`
- **Path format**: Use forward slashes, consistent with repository structure
- **Path validation**: Verify all referenced paths exist before plan delivery
- **Compliance**: Post `✅ Gate PR2 PASS: All paths are repo-relative, no host-local paths`

**Evolution Condition**: Path handling patterns change

---

## §3 - Design Doc Integration (PR3)

**Trigger**: `design document`, `researcher`, `design spec`  
**Situation**: Integrating Researcher design documents into plans  
**Judgment**: Plans must reference Researcher design documents as primary source

**Detailed Rule**:
- **Primary source**: Researcher design documents are the primary source for plan requirements
- **Reference format**: Include design document path and relevant sections
- **Design alignment**: Plan must align with design document specifications
- **Gap identification**: Identify any gaps between design document and plan requirements
- **Compliance**: Post `✅ Gate PR3 PASS: Plan references Researcher design documents as primary source`

**Evolution Condition**: Design document format changes

---

## §4 - Devin Integration (PR4)

**Trigger**: `Devin`, `interactive planning`, `workflow`  
**Situation**: Plans must work with Devin Interactive Planning workflow  
**Judgment**: Plans must be compatible with Devin's Interactive Planning features

**Detailed Rule**:
- **Devin compatibility**: Plans must work with Devin Interactive Planning workflow
- **Format alignment**: Plan structure must align with Devin's expectations
- **Tool integration**: Plan must reference appropriate Devin tools where applicable
- **Session compatibility**: Plan must be executable in a Devin session
- **Compliance**: Post `✅ Gate PR4 PASS: Plan works with Devin Interactive Planning workflow`

**Evolution Condition**: Devin workflow features change

---

## §5 - Executor Manifest (PR5)

**Trigger**: `Executor Manifest`, `manifest`, `deliverables`  
**Situation**: Every plan must include complete Executor Manifest section  
**Judgment**: Plan must include complete Executor Manifest with phases, deliverables, and gates

**Detailed Rule**:
- **Manifest required**: Every plan must include complete Executor Manifest section
- **Phase structure**: Manifest must define phases with clear deliverables
- **Gate definitions**: Each phase must have explicit verification gates
- **Scope definition**: Manifest must define in-scope and out-of-scope paths
- **Coverage targets**: Manifest must include test coverage targets
- **Compliance**: Post `✅ Gate PR5 PASS: Plan includes complete Executor Manifest section`

**Evolution Condition**: Manifest format requirements change

---

## §6 - Plan Structure (PR6)

**Trigger**: `plan structure`, `format`, `template`  
**Situation**: Plans must follow defined structure: header, manifest, phases, deliverables  
**Judgment**: Plans must follow standardized structure for consistency

**Detailed Rule**:
- **Standard structure**: Plans must follow defined structure: header, manifest, phases, deliverables
- **Section ordering**: Must maintain proper section ordering as defined
- **Content requirements**: Each section must include required content
- **Formatting consistency**: Use consistent formatting throughout plan
- **Completeness check**: All required sections must be present
- **Compliance**: Post `✅ Gate PR6 PASS: Plan follows defined structure`

**Evolution Condition**: Plan structure template changes

---

## §7 - Quality Gates (PR7)

**Trigger**: `quality gate`, `verification`, `completeness check`  
**Situation**: Plans must pass completeness, clarity, and specificity checks  
**Judgment**: Plans must pass defined quality gates before delivery

**Detailed Rule**:
- **Completeness check**: Plan must include all required sections and information
- **Clarity check**: Plan language must be clear and unambiguous
- **Specificity check**: Plan steps must be specific and actionable
- **Validation**: Plan must pass all defined quality gates
- **Issue resolution**: All quality gate issues must be resolved before delivery
- **Compliance**: Post `✅ Gate PR7 PASS: Plan passes completeness, clarity, and specificity checks`

**Evolution Condition**: Quality gate criteria change

---

## §8 - Landmine Screening (PR8)

**Trigger**: `landmine`, `governance violation`, `risk check`  
**Situation**: Plans must be screened against governance landmines before delivery  
**Judgment**: Plans must not contain governance landmines or violations

**Detailed Rule**:
- **Landmine check**: Screen plan against known governance landmines
- **Governance compliance**: Plan must not violate established governance rules
- **Risk assessment**: Identify potential governance risks in plan
- **Risk mitigation**: Address or mitigate identified governance risks
- **Screening completeness**: Complete landmine screening before delivery
- **Compliance**: Post `✅ Gate PR8 PASS: Plan screened against governance landmines`

**Evolution Condition**: Landmine definition changes

---

## §9 - Reviewer Integration (PR9)

**Trigger**: `reviewer findings`, `fix plan`, `review feedback`  
**Situation**: Fix plans must address all Reviewer findings before delivery  
**Judgment**: Plans must comprehensively address Reviewer findings

**Detailed Rule**:
- **Finding coverage**: Fix plans must address all Reviewer findings
- **Action mapping**: Each finding must have corresponding action in plan
- **Verification gates**: Include verification gates for each fix action
- **Evidence requirements**: Include evidence that fixes will resolve findings
- **Completeness check**: All findings must be addressed before plan delivery
- **Compliance**: Post `✅ Gate PR9 PASS: Fix plan addresses all Reviewer findings`

**Evolution Condition**: Reviewer feedback format changes

---

## §10 - Workflow Integration (PR10)

**Trigger**: `workflow`, `process`, `coordination`  
**Situation**: Plans must follow workflow order: Researcher → Planner → Round Table → Executor  
**Judgment**: Plans must respect the defined workflow order and coordination

**Detailed Rule**:
- **Workflow order**: Plans must follow workflow order: Researcher → Planner → Round Table → Executor
- **Coordination points**: Plan must include coordination points between agents
- **Handoff definition**: Define clear handoff points and expectations
- **Process compliance**: Plan must respect defined workflow processes
- **Integration requirements**: Plan must integrate with other agent workflows
- **Compliance**: Post `✅ Gate PR10 PASS: Plan follows workflow order`

**Evolution Condition**: Workflow structure changes

---

## §11 - Compliance Posting (PR11)

**Trigger**: `compliance`, `gate posting`, `verification`  
**Situation**: Post compliance line after each gate: `✅ Gate PR{n} PASS: {details}`  
**Judgment**: Post compliance line after each rule gate to provide audit trail

**Detailed Rule**:
- **Compliance posting**: Post compliance line after each gate: `✅ Gate PR{n} PASS: {details}`
- **Details inclusion**: Include relevant details in compliance posting
- **Audit trail**: Compliance lines provide audit trail of gate passes
- **Format consistency**: Use consistent format for all compliance postings
- **Completeness**: All gates must have corresponding compliance postings
- **Compliance**: Post `✅ Gate PR11 PASS: Compliance posting complete`

**Evolution Condition**: Compliance posting format changes

---

## §12 - Rule Creation (PR12)

**Trigger**: `new rule`, `rule creation`, `governance update`  
**Situation**: New PR rules follow pattern: rule + rejected alternative + consequence  
**Judgment**: New rules must follow established pattern with rationale

**Detailed Rule**:
- **Rule definition**: Define the rule clearly with trigger and judgment
- **Rejected alternative**: Document rejected alternative approaches and reasoning
- **Consequence analysis**: Include consequence analysis for rule adoption
- **Rationale**: Provide clear rationale for rule necessity
- **Pattern compliance**: Follow established rule creation pattern
- **Compliance**: Post `✅ Gate PR12 PASS: New rule follows established pattern`

**Evolution Condition**: Rule creation pattern changes

---

## §13 - Rule Lifecycle (PR13)

**Trigger**: `rule lifecycle`, `rule status`, `rule evolution`  
**Situation**: Rules have stable IDs (PR{n}) and status: Proposed/Accepted/Rejected/Superseded  
**Judgment**: Rules must follow defined lifecycle management

**Detailed Rule**:
- **Stable IDs**: Rules have stable IDs (PR{n}) for reference
- **Status tracking**: Track rule status: Proposed/Accepted/Rejected/Superseded
- **Evolution management**: Manage rule evolution through status changes
- **Version control**: Maintain version history for rule changes
- **Transition criteria**: Define clear criteria for status transitions
- **Compliance**: Post `✅ Gate PR13 PASS: Rule lifecycle properly managed`

**Evolution Condition**: Lifecycle management process changes

---

## §14 - Stop Conditions (PR14)

**Trigger**: `stop condition`, `halt`, `error condition`  
**Situation**: Missing compliance line = HALT execution. Plan without valid manifest = INVALID  
**Judgment**: Defined stop conditions must halt execution immediately

**Detailed Rule**:
- **Missing compliance**: Missing compliance line = HALT execution
- **Invalid manifest**: Plan without valid manifest = INVALID
- **Error conditions**: Defined error conditions must halt execution
- **Stop authority**: Only authorized agents can override stop conditions
- **Error reporting**: Report stop condition clearly with reasoning
- **Compliance**: Post `✅ Gate PR14 PASS: Stop conditions properly enforced`

**Evolution Condition**: Stop condition criteria change

---

## §15 - Token Awareness (PR15)

**Trigger**: `token cost`, `efficiency`, `context window`  
**Situation**: Plans must consider token efficiency while prioritizing code quality  
**Judgment**: Balance token cost considerations with code quality requirements

**Detailed Rule**:
- **Quality priority**: Code quality takes priority over token cost reduction
- **Efficiency consideration**: Consider token efficiency within quality constraints
- **Context awareness**: Be aware of Devin's context window when planning
- **Token optimization**: Optimize token usage without sacrificing quality
- **Balance approach**: Balance conciseness with necessary detail for Executor
- **Compliance**: Post `✅ Gate PR15 PASS: Token awareness balanced with quality`

**Evolution Condition**: Token economics change or priorities shift

---

## §16 - Universal Rules (PR16)

**Trigger**: `universal rules`, `governance`, `editing`  
**Situation**: Apply universal governance and editing rules across all agents  
**Judgment**: Follow Agents/UNIVERSAL_RULES.md (GR1-GR5, ER1-ER5) for all operations

**Detailed Rule**:
- **Reference**: See `Agents/UNIVERSAL_RULES.md` for universal rules (GR1-GR5, ER1-ER5)
- **Scope**: These rules apply to all agents (Planner, Executor, Reviewer, Researcher)
- **Supremacy**: Universal rules have supremacy over agent-specific approaches
- **Integration**: Planner must follow GR1-GR5 (governance) and ER1-ER5 (editing) when creating or modifying plan files
- **Compliance**: Post `✅ Gate PR16 PASS: Followed GR{rule ID} or ER{rule ID} for operation`
- **Override**: Agent-specific rules may add to but not override universal rules

**Evolution Condition**: Universal rules change or new universal patterns emerge

---

## §17 - Spec-First Plan Creation (PR17)

**Trigger**: `plan structure`, `spec validation`, `spec approval`  
**Situation**: Plan creation must follow spec-first validation pattern (Kerno-inspired)  
**Judgment**: Plan structure must be validated before detailed drafting to catch structural defects early

**Detailed Rule**:
- **Spec generation**: Generate plan spec (header + Executor Manifest shell + phase list + deliverable names + gate names) before detailed drafting
- **Spec validation**: Architect/Reviewer validates spec against PR1, PR2, PR5, PR6 rules before proceeding
- **Spec approval**: Get spec approval before detailed drafting (Phase 2.5 compliance line required)
- **Spec-diff validation**: After drafting, regenerate spec from final plan and diff against approved spec (Phase 4.5)
- **Drift detection**: Identify structural changes (phases added/removed, deliverables changed, gates modified)
- **Drift resolution**: Either get approval for changes or revert to approved spec
- **Compliance**: Post `✅ Gate PR17 PASS: Spec-first validation completed, no structural drift`

**Evolution Condition**: Spec validation process changes or Kerno pattern evolves

---

## §18 - Confidence-Weighted Consensus (PR18)

**Trigger**: `panelist consensus`, `weighted voting`, `confidence scoring`  
**Situation**: Round Table consensus must use confidence-weighted voting, not binary majority  
**Judgment**: Replace binary majority with confidence-weighted consensus (Galileo-inspired)

**Security Principle**: All panelist scoring and consensus calculation is INTERNAL-ONLY. Panelists never see their own scores, other panelists' scores, or consensus results. This prevents gaming the system and ensures honest evaluation.

**Detailed Rule**:
- **Weighted vote per panelist**: panelist_weight = (confidence_score / 10) × (expertise_match_score / 4) × (historical_accuracy / 100)
- **Confidence score**: panelist self-reports 1-10 (already in schema)
- **Expertise match score**: 1-4 from competency rubric (already in schema)
- **Historical accuracy**: 1-100 from past Round Table scorecard (tracked in panelist_reviews.panelist_score)
- **Consensus threshold**: weighted support ≥70% of total possible weight AND no CRITICAL finding with confidence ≥8 from any panelist
- **Conditional threshold**: weighted support 50-70%
- **Block threshold**: weighted support <50% OR any CRITICAL finding with confidence ≥8
- **Internal calculation**: All consensus calculations are internal-only, post-hoc by Planner after panelists submit reviews
- **Panelist visibility**: Panelists only see Planner's responses (updated plans), never their own scores or other panelists' scores
- **Dissent surfacing**: when panelists diverge significantly (e.g., one gives score 4, another gives score 1), automatically flag for internal review
- **Panelist calibration tracking**: maintain rolling 10-evaluation window per panelist. If divergence >2 points, flag for recalibration (internal-only)
- **Compliance**: Post `✅ Gate PR18 PASS: Confidence-weighted consensus achieved, weighted support {percentage}% (internal calculation)`

**Evolution Condition**: Consensus algorithm changes or panelist scoring system evolves

---

## §19 - Hierarchical Goal Decomposition (PR19)

**Trigger**: `batch creation`, `goal tree`, `sub-goal`, `hierarchical planning`  
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
- **Compliance**: Post `✅ Gate PR19 PASS: Hierarchical goal decomposition completed, {N} sub-goals, {N} levels`

**Evolution Condition**: Goal decomposition patterns change or Galileo strategy evolves

---

## §20 - Runtime Guardrail Hooks (PR20)

**Trigger**: `hook`, `guardrail`, `enforcement`, `automatic validation`  
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
- **Compliance**: Post `✅ Gate PR20 PASS: Runtime guardrail hooks configured and active`

**Evolution Condition**: Hook system changes or platform requirements evolve

---

## §21 - Durable Execution & Checkpointing (PR21)

**Trigger**: `checkpoint`, `recovery`, `state persistence`, `resumption`  
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
- **Compliance**: Post `✅ Gate PR21 PASS: Checkpoint created at Phase X.Y, state persisted for recovery`

**Evidence**: Galileo's Strategy #8 emphasizes durable execution with checkpointing for reliability and recovery

**Evolution Condition**: Checkpointing requirements change or recovery patterns evolve

---

## §22 - Competency-Based Subagent Validation (PR22)

**Trigger**: `subagent`, `competency validation`, `domain expertise`, `specialized evaluation`  
**Situation**: Plans require domain expertise validation beyond Planner self-check to catch 80% of issues before expensive Round Table  
**Judgment**: Implement 5 specialized competency subagents for parallel domain expert validation before Round Table

**Detailed Rule**:
- **Specialized Subagents**: 5 domain expert subagents (Technical Architecture, Domain Relevance, Communication Quality, Cross-Team Impact, Governance Compliance)
- **Competency Framework**: Each subagent evaluates per COMPETENCY_ASSIGNMENT_FRAMEWORK.md with specific criteria and scoring
- **Parallel Execution**: All 5 subagents run simultaneously with isolated context windows for efficiency
- **Model Strategy**: All 5 subagents use SWE-1.6 (desktop IDE built-in model) for consistency; domain expertise comes from specialized prompts, not model diversity
- **Phase Integration**: Run as Phase 5.5 between Phase 5 (Plan Finalization) and Phase 6 (Round Table Review)
- **Findings Collection**: Planner collects JSON evaluations from all subagents with scored criteria and severity-ranked findings
- **Self-Fix Priority**: Fix CRITICAL/HIGH findings before Round Table, defer MEDIUM/LOW strategic issues to panelists
- **Round Table Efficiency**: Makes Round Table more efficient by focusing on strategic issues rather than obvious defects
- **Compliance**: Post `✅ Gate PR22 PASS: Competency self-check complete, {N} findings fixed, {N} findings deferred to Round Table`

**Evidence**: Anthropic's multi-agent research shows subagents with separate context windows outperform single agents by 90% on breadth-first queries; AWS prescriptive guidance recommends domain expertise validation before stakeholder review

**Evolution Condition**: Subagent capabilities evolve or competency framework changes