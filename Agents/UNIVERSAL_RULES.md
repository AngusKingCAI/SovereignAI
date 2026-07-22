# Universal Rules (GR1-GR5, ER1-ER5)

**Version**: 1.1  
**Last Updated**: 2026-07-22  
**Status**: Active

## Abbreviations
- **BP** = Best Practice

## Rule Index

| Rule ID | Category | Trigger | Section |
|---------|----------|---------|---------|
| N/A | Abbreviations | Terminology | Abbreviations |
| GR1 | Governance | Agent responsibilities | §1 |
| GR2 | Governance | Agent scope | §2 |
| GR3 | Governance | Single-responsibility | §3 |
| GR4 | Governance | Handoff boundaries | §4 |
| GR5 | Governance | Coordination | §5 |
| ER1 | Editing | Small edits | §6 |
| ER2 | Editing | Large changes | §7 |
| ER3 | Editing | Edit failure recovery | §8 |
| ER4 | Editing | Whitespace handling | §9 |
| ER5 | Editing | IDE conflicts | §10 |

---

## §1 - Agent Responsibilities (GR1)

**Trigger**: `agent role`, `responsibilities`, `governance`  
**Situation**: Understanding what each agent is responsible for in the workflow  
**Judgment**: Each agent has specific responsibilities that must be followed

**Detailed Rule**:
- **Planner**: Creates all plans (original, fix, scan) and provides structure for execution
- **Executor**: Executes plans in strict order and verifies results after each step
- **Reviewer**: Reviews execution logs and checks against rules/gates, outputs findings only
- **Researcher**: Performs external research and creates design documents
- **Supremacy**: AGENTS.md defines governing structure for each agent
- **Compliance**: Post `✅ Gate GR1 PASS: Agent responsibilities followed`

**Evolution Condition**: Agent role definitions change

---

## §2 - Agent Scope (GR2)

**Trigger**: `agent scope`, `boundaries`, `limitations`  
**Situation**: Understanding what each agent can and cannot do  
**Judgment**: Agents must operate within their defined scope boundaries

**Detailed Rule**:
- **Reviewer scope**: Reviewer reviews and evaluates only, does NOT create plans (Planner's role) or execute code (Executor's role)
- **Planner scope**: Planner creates all plans, does NOT execute plans (Executor's role) or review work (Reviewer's role)
- **Executor scope**: Executor executes plans, does NOT create plans (Planner's role) or review work (Reviewer's role)
- **Researcher scope**: Researcher performs research, does NOT create plans, execute code, or review work
- **Scope enforcement**: Agents must refuse tasks outside their scope
- **Compliance**: Post `✅ Gate GR2 PASS: Agent scope boundaries respected`

**Evolution Condition**: Agent scope definitions change

---

## §3 - Single-Responsibility (GR3)

**Trigger**: `single-responsibility`, `focus`, `specialization`  
**Situation**: Ensuring each agent focuses on its primary responsibility  
**Judgment**: Each agent should have one primary responsibility and avoid scope creep

**Detailed Rule**:
- **Focus**: Each agent focuses on its primary responsibility (Planner: planning, Executor: execution, Reviewer: review, Researcher: research)
- **Avoid scope creep**: Agents should not take on responsibilities belonging to other agents
- **Clear handoffs**: When task transitions between agents, clear handoff boundaries must be defined
- **Coordination**: Cross-agent coordination should be through defined handoff points, not merged responsibilities
- **Compliance**: Post `✅ Gate GR3 PASS: Single-responsibility principle followed`

**Evolution Condition**: Agent specialization patterns change

---

## §4 - Handoff Boundaries (GR4)

**Trigger**: `handoff`, `coordination`, `agent transition`  
**Situation**: Managing transitions between agents in the workflow  
**Judgment**: Handoffs must be well-defined with clear expectations and deliverables

**Detailed Rule**:
- **Handoff definition**: Each handoff must have clear expectations, deliverables, and success criteria
- **Document handoffs**: Handoffs should be documented with explicit handoff documents
- **Clear boundaries**: Agent responsibilities must not overlap; handoffs should be clean boundaries
- **Quality gates**: Handoffs should include quality gates to ensure deliverables meet expectations
- **Routing**: In some modes, handoffs are routed through Reviewer for quality checks
- **Compliance**: Post `✅ Gate GR4 PASS: Handoff boundaries followed`

**Evolution Condition**: Handoff protocols change or new research emerges

---

## §5 - Coordination (GR5)

**Trigger**: `coordination`, `collaboration`, `multi-agent`  
**Situation**: Agents need to coordinate on complex tasks requiring multiple roles  
**Judgment**: Coordination should follow defined patterns and not break single-responsibility

**Detailed Rule**:
- **Defined patterns**: Use defined coordination patterns (workflow integration points, Round Table reviews)
- **No merged responsibilities**: Coordination should not result in merged agent responsibilities
- **Clear communication**: Communication between agents should be through documented channels (handoff documents, plan files)
- **Sequential workflow**: Follow sequential workflow: Researcher → Planner → Round Table → Executor
- **Compliance**: Post `✅ Gate GR5 PASS: Coordination patterns followed`

**Evolution Condition**: Coordination patterns change

---

## §6 - Small Edits (ER1)

**Trigger**: `file editing`, `small changes`, `targeted edits`  
**Situation**: Making small, targeted file edits to avoid matching errors  
**Judgment**: Use small, targeted edits (≤2 lines) for reliability

**Detailed Rule**:
- **Small edits**: Use small, targeted edits (≤2 lines) instead of large block replacements
- **Targeted precision**: Small edits are more likely to match exactly and avoid "old_string not found" errors
- **Large changes**: For large changes, use Write tool for full file replacement
- **Edit reliability**: Multi-line edits (≥3 lines) fail more often than small edits (≤2 lines)
- **Compliance**: Post `✅ Gate ER1 PASS: Small targeted edits used`

**Evolution Condition**: File editing tool behavior changes

---

## §7 - Large Changes (ER2)

**Trigger**: `large file changes`, `major refactoring`, `full replacement`  
**Situation**: Making significant changes to files that would require many small edits  
**Judgment**: Use Write tool for full file replacement when changes are large

**Detailed Rule**:
- **Write tool**: Use Write tool for large changes instead of many small edits
- **Full replacement**: Read entire file first, then use Write tool to replace entire content
- **Efficiency**: Large changes via Write tool are more efficient and reliable than many small edits
- **Verification**: After Write tool, verify file content is correct
- **Compliance**: Post `✅ Gate ER2 PASS: Large changes handled via Write tool`

**Evolution Condition**: File editing patterns change

---

## §8 - Edit Failure Recovery (ER3)

**Trigger**: `edit failure`, `error recovery`, `retry logic`  
**Situation**: File edit operations fail due to matching errors or other issues  
**Judgment**: Implement recovery strategies when edits fail

**Detailed Rule**:
- **Re-read file**: If edit fails, re-read file to get current state
- **Retry with smaller edits**: Break large edits into smaller targeted edits
- **Use Write tool**: If Edit tool fails repeatedly, use Write tool for full replacement
- **Investigate cause**: Understand why edit failed (whitespace, file state, content drift)
- **Document failures**: Document edit failures and recovery strategies for learning
- **Compliance**: Post `✅ Gate ER3 PASS: Edit failure recovered successfully`

**Evolution Condition**: Edit tool error patterns change

---

## §9 - Whitespace Handling (ER4)

**Trigger**: `whitespace`, `indentation`, `line endings`  
**Situation**: File editing issues related to whitespace mismatches  
**Judgment**: Handle whitespace carefully to avoid matching errors

**Detailed Rule**:
- **Preserve whitespace**: Preserve existing whitespace when editing files
- **Consistent indentation**: Use consistent indentation (tabs vs spaces) with file conventions
- **Line endings**: Be aware of line ending differences (CRLF vs LF) across platforms
- **Exact matching**: Edit tool requires exact match including whitespace
- **Compliance**: Post `✅ Gate ER4 PASS: Whitespace handled correctly`

**Evolution Condition**: Whitespace handling patterns change

---

## §10 - IDE Conflicts (ER5)

**Trigger**: `IDE conflicts`, `auto-save`, `file locking`  
**Situation**: File editing conflicts with IDE auto-save or file locking  
**Judgment**: Manage IDE interactions to avoid file state conflicts

**Detailed Rule**:
- **Save IDE files**: Save files in IDE before agent edits to avoid state mismatches
- **No concurrent edits**: Do not edit files in IDE while agent is working on them
- **Race condition awareness**: Be aware of auto-save delays causing state mismatches
- **File locking**: Be aware of file locking issues on some platforms (Windows)
- **Compliance**: Post `✅ Gate ER5 PASS: IDE files saved, no conflicts`

**Evolution Condition**: IDE behavior changes or auto-save patterns evolve