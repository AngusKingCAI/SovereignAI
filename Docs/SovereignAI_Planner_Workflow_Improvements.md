# SovereignAI Planner Workflow — Improvement Recommendations

**Based on**: Web research across 7 search queries and 5 deep-dive articles (Anthropic multi-agent research, Kerno validation gates, Augment async workflows, Anthropic context engineering, Galileo coordination strategies)
**Date**: 2026-07-22
**Scope**: Concrete improvements to the Planner workflow grounded in current (2025-2026) industry best practices

---

## Executive Summary

After researching current best practices in multi-agent orchestration, validation gates, context engineering, and failure recovery, the SovereignAI Planner workflow has **5 high-leverage improvement areas** that go beyond the 5 critical blockers I identified earlier. These improvements would bring the workflow in line with how production-grade agent systems are actually built in 2025-2026.

The BP literature consistently emphasizes five things your current workflow underweights:
1. **Spec-first validation** (Kerno) — separate API/surface definition from implementation, validate the surface before any code exists
2. **Durable execution with checkpoints** (Augment, Anthropic) — every phase transition is a recovery point, not just a gate
3. **Tool-design as a first-class concern** (Anthropic) — bad tool descriptions send agents down wrong paths; tool ergonomics is 40% of agent performance
4. **Context budgeting** (Anthropic) — context is a finite resource with diminishing returns; treat it like memory, not storage
5. **Consensus + confidence scoring** (Galileo) — majority voting is weak; weight votes by confidence and panelist history

---

## Source Articles

| # | Source | Key takeaway applied to SovereignAI |
|---|--------|-------------------------------------|
| 1 | [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Token budget explains 80% of performance variance; subagents with separate context windows outperform single agents by 90%; lead agent must delegate with detailed task descriptions |
| 2 | [Kerno — Multi-Agent Validation Gates](https://www.kerno.io/blog/multi-agent-validation-gates-for-agentic-coding) | Spec-first 5-phase validation: API spec → human review → implementation → spec-diff → tech-lead gate. Catches errors at cheapest intervention point |
| 3 | [Augment Code — Async AI agent workflows](https://www.augmentcode.com/guides/async-ai-agent-workflows) | Durable execution + checkpointing > restart-from-scratch. Event history replay avoids re-issuing LLM calls on recovery |
| 4 | [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Context rot: as tokens increase, recall accuracy decreases. Curate what enters the context window each turn |
| 5 | [Galileo — Multi-agent coordination strategies](https://galileo.ai/blog/multi-agent-coordination-strategies) | 10 strategies: deterministic task allocation, hierarchical goal decomposition, token boundaries, shared memory with ACL, runtime guardrails, fail-safe rollbacks |

---

## Improvement Area 1: Spec-First Validation (Inspired by Kerno)

### Current State
Your Phase 2 (Plan Structure Design) and Phase 3 (Plan Drafting) have no automated enforcement. The plan header and Executor Manifest are written directly in the plan file. By the time Phase 4 (Quality Gates) runs, the entire plan already exists — fixing structural defects means rewriting.

### BP Recommendation (Kerno's 5-Phase Pattern)
Separate plan creation into two artifacts:
- **Plan Spec** (the surface): header, Executor Manifest shell, phase list, deliverable names, gate names — no implementation detail
- **Plan Body** (the implementation): detailed steps, paths, code references

Add a **Phase 2.5: Spec Review Gate** between structure design and drafting:
1. Generate only the Plan Spec (header + manifest skeleton + phase names)
2. Architect/Reviewer validates spec against PR1, PR2, PR5, PR6 rules
3. Only after spec approval does the Planner draft the full plan body
4. **Phase 4.5: Spec-Diff Validation** — after drafting, regenerate spec from final plan and diff against approved spec. Catches drift (e.g., a phase added during drafting that wasn't in the approved structure)

### Concrete Implementation
- Add `PR17: Spec-First Plan Creation` to PLANNER_RULES.md
- Add HG-14 (spec present and approved) and HG-15 (spec-diff clean) to hard gates
- New script: `hg14_spec_approved.py` — checks for `✅ Gate PLAN-2.5 PASS` in plan file
- New script: `hg15_spec_diff_clean.py` — extracts header+manifest from final plan and diffs against spec file
- Phase 2.5 compliance: `✅ Gate PLAN-2.5 PASS: Plan spec approved, {N} phases, {N} deliverables`

### Why This Works
Kerno reports this pattern caught abstraction leaks in 2 minutes of review that would have cost hours to fix post-implementation. Your current workflow catches the equivalent (a plan with wrong structure) only at Phase 4 — by which point the entire body has been written against the wrong structure.

---

## Improvement Area 2: Durable Execution & Checkpointing (Inspired by Augment + Anthropic)

### Current State
Your workflow is a sequence of phases with compliance lines. If a session crashes mid-Phase-6 (Round Table), there's no formal mechanism to resume from where you left off. The old AI_HANDOFF.md v1.6 had a "Session Continuity Rule" (paste transcript between sessions) but the new workflow dropped it entirely.

### BP Recommendation
**Treat each phase transition as a durable checkpoint**, not just a gate. Concretely:

1. **Persist phase state to SQLite** (you already have the database — extend it). Add a `workflow_state` table:
   ```sql
   CREATE TABLE workflow_state (
     plan_id INTEGER,
     phase TEXT,          -- 'phase_1', 'phase_2', ... 'phase_7'
     status TEXT,         -- 'pending', 'in_progress', 'completed', 'blocked'
     started_at INTEGER,
     completed_at INTEGER,
     compliance_line TEXT,
     retry_count INTEGER DEFAULT 0,
     checkpoint_data TEXT, -- JSON: any intermediate state
     PRIMARY KEY (plan_id, phase)
   );
   ```

2. **Idempotent phase transitions**: each phase can be re-run without side effects. If Phase 6.2 (Panelist Evaluation) crashes after 3 of 6 panelists are stored, re-running should detect the 3 existing reviews and only fetch the missing 3.

3. **Event-sourced recovery**: instead of restarting from Phase 1, query `workflow_state` for the last completed phase and resume from there. This is what Temporal/Augment do — replay the event history, not the work.

4. **Approval-gate timeouts**: if Phase 6.4 (Clean Pass Gate) requires user approval and the user doesn't respond within a configurable SLA (e.g., 24 hours), treat as denial and escalate. Encode this in the workflow definition.

### Concrete Implementation
- Add `PR18: Durable Phase Checkpointing` to PLANNER_RULES.md
- Extend `database_manager.py` with `workflow_state` table and methods: `get_phase_state(plan_id, phase)`, `update_phase_state(plan_id, phase, status, checkpoint_data)`, `resume_from_checkpoint(plan_id)`
- New script: `resume_workflow.py --plan-id {N}` — reads workflow_state and prints "Resume from Phase X.Y (last completed: Phase X.Y-1)"
- Add to each phase in PLAN_WORKFLOW.md: "On resumption: query workflow_state for this plan and resume from last completed phase"

### Why This Works
Anthropic's research system explicitly states: "Without effective mitigations, minor system failures can be catastrophic for agents. When errors occur, we can't just restart from the beginning: restarts are expensive and frustrating for users." The old AI_HANDOFF.md's session-continuity rule was a manual version of this — the new workflow needs an automated version.

---

## Improvement Area 3: Context Budgeting (Inspired by Anthropic Context Engineering)

### Current State
Your 12-section brief is comprehensive but has no token budget. The brief template says "1000-2000 words (approximately 2-4 pages)" but doesn't enforce it. Panelist prompts include the full brief plus plan plus rubric plus web search instructions — easily 5-10K tokens per panelist.

### BP Recommendation
**Treat context as a finite resource with diminishing returns.** Anthropic's research shows context rot sets in as tokens increase — model recall accuracy degrades. Apply this to your brief and panelist prompts:

1. **Token budget per artifact** (not just word count):
   - Brief: ≤3000 tokens (≈2200 words, your current "2000 words" is close)
   - Panelist prompt: ≤1500 tokens (rubric + competency assignment + web search instructions)
   - Plan file shown to panelist: ≤4000 tokens (header + manifest + phases only, not full body)
   - Total panelist context: ≤8500 tokens

2. **Context triage per phase**: each phase gets a "context budget" and a "context checklist" specifying exactly what must be in context for that phase. Phase 6.2 (Panelist Evaluation) doesn't need the full governance docs — it needs the brief, the plan, the rubric, and the panelist's assigned competency.

3. **Just-in-time context loading**: instead of loading all governance docs at Phase 6.1, load only what each panelist needs based on their competency. The Technical Architecture panelist doesn't need the Domain Relevance rubric.

4. **Context compression**: between phases, compress the prior phase's output. Phase 1 (Input Assessment) produces a scope document — Phase 2 doesn't need the raw user requirements, just the scope summary.

### Concrete Implementation
- Add `PR19: Context Budget per Phase` to PLANNER_RULES.md
- Add token-count validation to hard gates: HG-16 (brief token budget), HG-17 (panelist prompt token budget)
- New script: `hg16_brief_token_budget.py` — counts tokens in latest brief file, fails if >3000
- Update BRIEF_TEMPLATE.md with explicit token budgets per section (not just "1000-2000 words")
- Add a "Context Checklist" subsection to each phase in PLAN_WORKFLOW.md listing exactly what must be loaded

### Why This Works
Anthropic: "Context, therefore, must be treated as a finite resource with diminishing marginal returns... every new token introduced depletes this budget by some amount." Your current workflow treats context as infinite — load everything, all the time. Token budgets force discipline.

---

## Improvement Area 4: Confidence-Weighted Consensus (Inspired by Galileo)

### Current State
Your Round Table uses simple majority: "At least 4 out of 6 panelists must provide valid reviews (BP: majority >50%)". All panelist votes count equally regardless of confidence, expertise match, or historical accuracy.

### BP Recommendation
**Replace binary majority with confidence-weighted consensus.** Galileo's coordination research identifies consensus voting as Strategy #7, but the implementation matters:

1. **Weighted vote per panelist**:
   ```
   panelist_weight = (confidence_score / 10) × (expertise_match_score / 4) × (historical_accuracy / 100)
   ```
   - `confidence_score`: panelist self-reports 1-10 (already in your schema)
   - `expertise_match_score`: 1-4 from competency rubric (already in your schema)
   - `historical_accuracy`: 1-100 from past Round Table scorecard (need to track this — your `panelist_reviews.panelist_score` field already captures it)

2. **Consensus threshold**:
   - Pass: weighted support ≥70% of total possible weight AND no CRITICAL finding with confidence ≥8 from any panelist
   - Conditional: weighted support 50-70%
   - Block: weighted support <50% OR any CRITICAL finding with confidence ≥8

3. **Dissent surfacing**: when panelists diverge significantly (e.g., one gives score 4, another gives score 1 on same competency), automatically flag for evidence-first debriefing (your Phase 6.3 already does this — make it trigger-based, not manual)

4. **Panelist calibration tracking**: maintain a rolling 10-evaluation window per panelist. If a panelist's scores consistently diverge from consensus by >2 points, flag for recalibration. Your `panelists.specialty` field could be extended to include calibration metadata.

### Concrete Implementation
- Add `W5: Confidence-Weighted Consensus` to PLAN_WORKFLOW.md workflow rules
- New script: `sg4_panelist_calibration.py` — warns if any panelist's last-10-evaluation divergence >2 points
- Update Phase 6.4 Clean Pass Gate to use weighted consensus instead of binary majority
- Extend `panelist_reviews` table with `weighted_vote REAL` column (computed on insert)
- New view: `v_panelist_calibration` — shows each panelist's last-10 divergence from consensus

### Why This Works
Galileo: "Dissent surfacing" and "consensus voting" are listed as separate strategies because naive majority voting hides disagreement. A 4-2 split where the 2 dissenters are highly confident and expert-matched should trigger deeper review, not be overridden by the 4 who may be guessing.

---

## Improvement Area 5: Tool-Design Discipline (Inspired by Anthropic)

### Current State
Your hard gate scripts and database_manager.py are tools the Planner/Reviewer agents invoke. But the tool descriptions are minimal — `hg1_requirements_complete.py` has a docstring but no formal "tool description" for the agent that invokes it. Agents don't know when to use which tool, what failure looks like, or how to recover.

### BP Recommendation
Anthropic's research found that tool description quality accounts for ~40% of task completion time variance. Bad tool descriptions "send agents down completely wrong paths." Apply this to your hard gate scripts:

1. **Standardized tool description format** for every script:
   ```python
   """
   Tool: HG-1 Requirements Complete Validation
   
   WHEN TO USE: Phase 1, after requirements are assessed, before plan drafting
   
   WHAT IT CHECKS: Latest plan file has dependencies, vision principles, 
   context section, no vague terms (TBD/TBA/TODO), specific step sections (S1, S2...), 
   and compliance indicators.
   
   INPUTS: None (auto-discovers latest plan in plans/ directory)
   
   OUTPUTS:
   - Exit 0: ✅ Gate HG-1 PASS: {plan_name} requirements complete
   - Exit 1: ❌ Gate HG-1 FAIL: {list of specific issues}
   
   FAILURE RECOVERY: Fix listed issues in plan file, re-run this script.
   Do NOT proceed to Phase 2 until exit 0.
   
   DEPENDENCIES: plans/ directory must exist with at least one plan-*.md file
   """
   ```

2. **Tool-testing loop**: Anthropic created a "tool-testing agent" that attempts to use each tool and rewrites the description based on observed failures. You can do this manually: for each hard gate script, simulate 5 different plan states (valid, missing dependencies, missing manifest, etc.) and verify the script produces the right exit code and a helpful message.

3. **Tool registry**: create `.Planner/scripts/TOOL_REGISTRY.md` listing every script with its trigger, inputs, outputs, and failure recovery. Agents read this file at Phase 0 to know what tools are available.

4. **Distinct purpose per tool**: Anthropic warns against tools with overlapping purposes. Your HG-9 (manifest complete) and HG-13 (manifest present) overlap — clarify: HG-13 checks the section exists; HG-9 checks the section is complete. Document this distinction in both scripts.

### Concrete Implementation
- Add `PR20: Tool Description Standard` to PLANNER_RULES.md
- Update every hard gate and soft gate script with the standardized docstring format above
- Create `.Planner/scripts/TOOL_REGISTRY.md` with one row per script
- Add tool-testing to the workflow: Phase 0 includes "verify all gate scripts run correctly against test fixtures"

### Why This Works
Anthropic: "Bad tool descriptions can send agents down completely wrong paths, so each tool needs a distinct purpose and a clear description." Your current scripts have one-line docstrings. An agent invoking `hg7_compliance_lines_present.py` has no idea what compliance format is expected, what failure looks like, or how to recover.

---

## Improvement Area 6: Self-Check Phase (Restore from Old Workflow)

### Current State
The old AI_HANDOFF.md v1.6 §6 Step 2.5 had an "Architect Self-Check" — before handing material to Round Table panelists, the Architect ran its own draft against the same rubric. This was a zero-cost internal pass that caught issues the Architect could catch itself, reducing the number of findings the real panel needed to surface.

The new workflow **dropped this entirely**. This is a regression — panelist rounds are expensive (each panelist uses web search, takes time, costs tokens). Wasting rounds on issues the Planner could have caught itself is pure waste.

### BP Recommendation
**Restore the self-check as Phase 6.0 (Architect Self-Check)**, before Phase 6.1 (Pre-Round Table Preparation):

1. Planner applies the 4-point rubric to its own draft, per competency
2. Planner checks draft against known patterns (your `ARCHITECT_PATTERNS.md` was removed in the redesign — restore it as `PATTERN_LIBRARY.md`)
3. Planner fixes any self-identified CRITICAL/HIGH findings before delivering to Round Table
4. Document deferred findings with reasoning ("self-identified but kept for panel validation because...")

### Concrete Implementation
- Add Phase 6.0 to PLAN_WORKFLOW.md with 4 steps: rubric self-check, pattern self-check, self-fix, defer-with-reasoning
- Compliance: `✅ Gate PLAN-6.0 PASS: Self-check complete, {N} findings self-fixed, {N} deferred to Round Table`
- Restore `ARCHITECT_PATTERNS.md` (it was deleted in commit 2c4ecdd) as `.Planner/rules/PATTERN_LIBRARY.md`
- New soft gate: `sg5_self_check_complete.py` — warns if Phase 6.0 compliance line missing

### Why This Works
The old workflow had this for a reason. The new workflow's omission means every defect the Planner could have caught itself becomes a panelist finding — wasting panelist rounds and increasing the odds of needing Rev 2+. This is a direct cost saving.

---

## Improvement Area 7: Hierarchical Goal Decomposition (Inspired by Galileo)

### Current State
Your Phase 0 (Plan Batch Creation) groups related plans but doesn't formally decompose goals hierarchically. A batch of 4 plans shares a brief, but the dependency graph is flat — "Plan 35.1 depends on Plan 35" is the only relationship type.

### BP Recommendation
Galileo's Strategy #2 is hierarchical goal decomposition. Apply this to batch creation:

1. **Goal tree per batch**:
   ```
   Batch Goal: Implement user authentication
   ├── Sub-goal 1: Authentication infrastructure (Plan 35.1)
   │   ├── Sub-task 1a: Session management
   │   └── Sub-task 1b: Token validation
   ├── Sub-goal 2: User registration flow (Plan 35.2)
   ├── Sub-goal 3: Login UI (Plan 35.3)
   └── Sub-goal 4: Integration tests (Plan 35.4)
   ```

2. **Inheritance**: each sub-goal inherits vision principles, AR rules, and OR rules from its parent. Currently this is done manually in the plan header — formalize it.

3. **Blocking propagation**: if Plan 35.1 (infrastructure) STOPs, all descendants in the goal tree STOP. Your old AI_HANDOFF.md v1.6 had this ("If Plan {Xn} STOPs, all plans with `Depends on: {Xn}` also STOP. Binary.") — restore it formally.

4. **Coverage tracking per goal**: each sub-goal has its own coverage target (≥90%), and the batch coverage is the weighted average.

### Concrete Implementation
- Add `PR21: Hierarchical Goal Decomposition` to PLANNER_RULES.md
- Extend `batches` table with `goal_tree_json TEXT` column
- Update Phase 0 to produce a goal tree artifact (`plans/goal-tree-batch{N}.md`)
- New hard gate: `hg18_goal_tree_present.py` — checks for goal tree file before batch execution

---

## Improvement Area 8: Runtime Guardrails via Hooks (Inspired by Galileo + AWS)

### Current State
Your hard gates run as standalone Python scripts invoked manually (`python .Planner/scripts/hard_gates/run_phase_gates.py --phase 1`). Nothing prevents an agent from skipping the invocation and posting a fake compliance line.

### BP Recommendation
Galileo's Strategy #8 and AWS prescriptive guidance both emphasize **runtime guardrails** — validation that runs automatically as part of the tool call, not as a separate manual step. The old AI_HANDOFF.md v1.6 actually had Devin hooks (`hooks.v1.json`) for PreToolUse, PostToolUse, SessionStart, SessionEnd — but the new workflow doesn't reference them.

1. **PreToolUse hook**: before any file write to `plans/`, automatically run HG-7 (compliance lines), HG-8 (paths valid), HG-9 (manifest complete). If any fails, block the write.

2. **PostToolUse hook**: after any plan file modification, automatically update `workflow_state` table with new mtime and re-run phase gates for the current phase.

3. **SessionStart hook**: on session start, query `workflow_state` and print "Resuming from Phase X.Y" — the agent doesn't need to remember where it was.

4. **SessionEnd hook**: on session end, write a checkpoint with current phase, pending items, and any unposted compliance lines.

### Concrete Implementation
- Restore and update `.devin/hooks.v1.json` (referenced in plan-35.1-Rev1.md but not present in current repo)
- Create hook scripts in `.Planner/scripts/hooks/`: `pretooluse_plan_write.py`, `posttooluse_plan_write.py`, `session_start.py`, `session_end.py`
- Add `PR22: Runtime Guardrail Hooks` to PLANNER_RULES.md

### Why This Works
Manual gate invocation is bypassable. Hooks are not — they run on every tool call regardless of agent intent. This is the difference between "the agent should validate" and "the agent cannot avoid validating."

---

## Prioritized Implementation Roadmap

### Tier 1 — Highest leverage, lowest effort (do first)

| # | Improvement | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 6 | Restore Self-Check Phase (Phase 6.0) | Low (1 workflow section + 1 script) | High (saves panelist rounds) | None |
| 3 | Context Budget per Phase | Medium (rule + 2 scripts + template update) | High (panelist focus) | None |
| 5 | Tool Description Standard | Medium (update 16 scripts + create registry) | High (agent reliability) | None |

### Tier 2 — High leverage, medium effort

| # | Improvement | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 1 | Spec-First Validation (Phase 2.5 + 4.5) | Medium (2 new phases + 2 scripts) | High (catches structural defects early) | None |
| 4 | Confidence-Weighted Consensus | Medium (rule + 1 script + schema extension) | Medium (better Round Table decisions) | Track panelist history |
| 7 | Hierarchical Goal Decomposition | Medium (rule + schema + Phase 0 update) | Medium (batch clarity) | None |

### Tier 3 — High leverage, high effort (do last)

| # | Improvement | Effort | Impact | Dependencies |
|---|-------------|--------|--------|--------------|
| 2 | Durable Execution & Checkpointing | High (schema + 5 scripts + workflow rewrite) | Very high (failure recovery) | workflow_state table |
| 8 | Runtime Guardrail Hooks | High (4 hook scripts + Devin integration) | Very high (unbypassable enforcement) | Restore hooks.v1.json |

---

## How This Maps to the 5 Critical Blockers from My Earlier Review

The 5 blockers I identified are **prerequisites** for these improvements — none of the improvements above will work if the gates don't actually validate:

| Blocker | Fixes required before improvements can land |
|---------|---------------------------------------------|
| 8 placeholder hard gates | Must implement real validation logic — improvements 1, 3, 5 depend on gates that work |
| `Plans` vs `plans` path bug | Must fix path — every gate script depends on finding the plan file |
| JSON exporter import bug | Must fix import — improvement 2 (durable execution) depends on working exports |
| `Agents/shared/` broken path | Must fix reference — agents can't follow supremacy check |
| Soft gate runner path mismatch | Must fix runner — improvement 4 (weighted consensus) depends on soft gates running |

**Recommended sequence**:
1. Fix the 5 blockers (1-2 days)
2. Implement Tier 1 improvements (3-5 days)
3. Implement Tier 2 improvements (1-2 weeks)
4. Implement Tier 3 improvements (2-4 weeks)

After all of the above, the workflow would be at or above the level of production-grade multi-agent systems documented in the 2025-2026 BP literature.

---

## Sources Cited

1. Anthropic Engineering — "How we built our multi-agent research system" (Jun 2025) — https://www.anthropic.com/engineering/multi-agent-research-system
2. Kerno Blog — "Multi-Agent Validation Gates: Why Claude Can't Break Our Architecture" (Feb 2026) — https://www.kerno.io/blog/multi-agent-validation-gates-for-agentic-coding
3. Augment Code Guides — "How Async AI Agent Workflows Survive Failures" (Jun 2026) — https://www.augmentcode.com/guides/async-ai-agent-workflows
4. Anthropic Engineering — "Effective context engineering for AI agents" (Sep 2025) — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
5. Galileo AI Blog — "Multi-Agent Coordination Gone Wrong? Fix With 10 Strategies" — https://galileo.ai/blog/multi-agent-coordination-strategies
6. arXiv — "U-Define: Designing User Workflows for Hard and Soft Constraints in LLM-based Planning" (May 2026) — https://arxiv.org/html/2605.02765v1
7. arXiv — "LLMs Can't Plan, But Can Help Planning in LLM-Modulo" (Feb 2024) — https://arxiv.org/html/2402.01817v2
8. AWS Prescriptive Guidance — "Input validation and guardrails for agentic AI systems" — https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-security/best-practices-input-validation.html
9. Praetorian — "Deterministic AI Orchestration: A Platform Architecture for Autonomous Development" (Feb 2026) — https://www.praetorian.com/blog/deterministic-ai-orchestration-a-platform-architecture-for-autonomous-development
10. BuildMVPFast — "Idempotent AI Agents: Retry-Safe Patterns for Production" (2026) — https://www.buildmvpfast.com/blog/idempotent-ai-agent-retry-safe-patterns-production-workflow-2026

---

*End of recommendations.*
