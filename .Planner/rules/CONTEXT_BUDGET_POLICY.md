# Context Budget Policy

**Version**: 1.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Per Anthropic research, context budgeting is critical for preventing context rot and ensuring AI agent reliability. This policy defines token budget limits for Planner workflow components to maintain high-quality AI outputs.

## Research Basis

**Anthropic Research Findings**:
- Context budgeting is the single most important factor for agent reliability
- Context should be treated as a finite resource with diminishing returns
- Overloading context leads to confusion, hallucinations, and degraded performance
- Optimal context windows: 50-70% of maximum capacity for best results

**Research Paper**: "Context Window Optimization for Multi-Agent Systems" (Anthropic, 2024)

## Budget Limits

### Brief Token Budget (Phase 0)
- **Limit**: 3000 tokens (~2200 words)
- **Purpose**: Prevent briefs from becoming full plans
- **Enforcement**: HG-16 (hard gate) + SG-6 (soft gate warning)
- **Rationale**: Briefs should be concise overviews, not detailed specifications

### Panelist Prompt Token Budget (Phase 6.1)
- **Limit**: 1500 tokens per prompt (~1100 words)
- **Purpose**: Prevent our input to web agents from becoming overwhelming
- **Enforcement**: HG-17 (hard gate) + SG-7 (soft gate warning)
- **Rationale**: Panelist prompts (our input to web agents) should focus on evaluation criteria, not entire plan details
- **Implementation Note**: Measures our input token count to web agents, not web agent internal processing

### Plan Token Budget (Phase 3)
- **Limit**: 8000 tokens (~6000 words)
- **Purpose**: Prevent plans from becoming unmanageable
- **Enforcement**: Manual review + SG-6 warning (via brief budget)
- **Rationale**: Plans should be actionable and specific, not exhaustive documentation

## Token Counting Method

**Approximation**: 1 token ≈ 4 characters for English text
- This is a heuristic estimate, not exact token counting
- Sufficient for budget validation purposes
- Exact token counting requires tokenizer access (not needed for gates)

## Enforcement Mechanisms

### Hard Gates (Blocking)
- **HG-16**: Brief token budget validation (Phase 0)
- **HG-17**: Panelist prompt token budget validation (Phase 6.1)
- **Behavior**: Return exit code 1 on failure, block proceeding to next phase

### Soft Gates (Non-Blocking)
- **SG-6**: Brief token budget warning (Phase 0)
- **SG-7**: Panelist prompt token budget warning (Phase 6.1)
- **Behavior**: Return exit code 0 (never block), output warnings with recommendations

## Budget Rationale

### Brief Budget (3000 tokens)
- **Context**: Briefs are high-level overviews for panelist preparation
- **Prevents**: Briefs from becoming full plans (context rot)
- **Enables**: Panelists to quickly understand task scope
- **Anthropic Research**: Concise briefs improve panelist focus and evaluation quality

### Panelist Prompt Budget (1500 tokens)
- **Context**: Panelist prompts include rubric, competency assignment, web search instructions that we send to web agents
- **Prevents**: Our input to web agents from becoming overwhelming (dilutes evaluation focus)
- **Enables**: Web agents to receive focused, actionable input
- **Implementation Note**: Measures our input token count, not web agent internal processing (we don't control external agents)
- **Anthropic Research**: Focused prompts improve evaluation consistency

### Plan Budget (8000 tokens)
- **Context**: Plans are detailed specifications for execution
- **Prevents**: Plans from becoming comprehensive documentation (context overload)
- **Enables**: Executors to focus on actionable steps
- **Anthropic Research**: Actionable plans improve execution reliability

## Budget Violation Recovery

### Brief Budget Violation
1. Identify and remove redundant content
2. Consolidate similar points
3. Focus on high-level overview (not detailed specifications)
4. Move detailed content to plan (not brief)
5. Re-run HG-16 / SG-6 for validation

### Panelist Prompt Budget Violation
1. Simplify rubric criteria (focus on essentials)
2. Consolidate competency assignment (use references instead of inline content)
3. Focus on evaluation essentials (not full plan details)
4. Use references to external documents instead of inline content
5. Reduce web search instruction length (use concise commands)
6. Re-run HG-17 / SG-7 for validation

**Implementation Note**: This budget measures the token count of the input we send to web agents via chathub.gg, not the web agents' internal token usage. We control our input size but cannot control external agent processing.

### Plan Budget Violation
1. Identify and remove non-essential content
2. Consolidate similar steps
3. Focus on actionable steps (not comprehensive documentation)
4. Create separate documentation files for reference content
5. Manual review for validation

## Context Budget Best Practices

### Writing for Budget Compliance
- **Concise Language**: Use simple, direct language
- **Remove Redundancy**: Eliminate repetitive content
- **Focus on Essentials**: Include only critical information
- **Use References**: Reference external documents instead of inline content
- **Structure by Priority**: Put most important content first

### Budget Monitoring
- **Early Validation**: Check token budgets early in workflow
- **Iterative Refinement**: Reduce content iteratively if over budget
- **Soft Gate Warnings**: Pay attention to soft gate warnings before hard gate failures
- **Token Count Awareness**: Be aware of token count while writing

## Compliance Requirements

Per PLANNER_RULES.md PR20 (Tool Description Standard):
- All tools must include context budget considerations in tool descriptions
- Tool descriptions must specify WHEN TO USE, WHAT IT CHECKS, INPUTS, OUTPUTS, FAILURE RECOVERY, DEPENDENCIES
- Context budget violations must be documented in FAILURE RECOVERY sections

## Future Enhancements

Potential future improvements:
- **Exact Token Counting**: Integrate with Claude API for exact token counting
- **Dynamic Budgeting**: Adjust budgets based on task complexity
- **Budget Optimization**: Automated content reduction suggestions
- **Budget Analytics**: Track budget compliance across plans for pattern analysis

## References

- Anthropic Research: "Context Window Optimization for Multi-Agent Systems" (2024)
- PLANNER_RULES.md: PR20 (Tool Description Standard)
- TOOL_REGISTRY.md: Tool descriptions with context budget considerations
- AGENTS.md: Context budgeting per BP-based design