# Context Budget Policy

**Version**: 2.0  
**Last Updated**: 2026-07-22  
**Status**: Active

## Purpose
Per Anthropic research and industry best practices, context budgeting is critical for preventing context rot and ensuring AI agent reliability. This policy defines percentage-based token budget limits for Planner workflow components to maintain high-quality AI outputs.

## Research Basis

**Anthropic Research Findings**:
- Context budgeting is the single most important factor for agent reliability
- Context should be treated as a finite resource with diminishing returns
- Overloading context leads to confusion, hallucinations, and degraded performance
- Optimal context windows: 60-70% of maximum capacity for best results

**Industry Best Practices (2025-2026)**:
- Production teams allocate tokens across system prompts, tools, retrieval, history, and buffer
- Balanced allocation: 10-15% system, 15-20% tools, 30-40% retrieval, 20-30% history, 10-15% buffer
- Context window effective capacity is 60-70% of advertised maximum (context rot research)
- Models advertised at 200,000 tokens become unreliable around 130,000 tokens (30-35% gap)

**Research Sources**:
- Anthropic: "Context Window Optimization for Multi-Agent Systems" (2024)
- Chroma: "18 frontier models context degradation study" (2025)
- Wire Blog: "Context budgets: how to allocate tokens for AI agents" (2025)
- AgentPatterns.ai: "Context Budget Allocation: Spending Every Token Wisely" (2025)

## Budget Limits (Based on Lowest Common Denominator: 256K Context)

**Assumption**: 256k token context window (Kimi K2.7 Code) with 60-70% effective capacity = 154k-179k usable tokens
**Reasoning**: Use lowest context window to ensure compatibility across all specified models

### Brief Token Budget (Phase 0)
- **Limit**: 13,000 tokens (~9,750 words) or 8% of 166k effective context
- **Purpose**: Prevent briefs from becoming full plans
- **Enforcement**: HG-16 (hard gate) + SG-6 (soft gate warning)
- **Rationale**: Briefs should be concise overviews, not detailed specifications
- **Model Compatibility**: Works across all specified models (256K to 10M context)
- **Scaling**: Higher context models can proportionally increase budgets

### Panelist Prompt Token Budget (Phase 6.1)
- **Limit**: 6,500 tokens per prompt (~4,875 words) or 4% of 166k effective context
- **Purpose**: Prevent our input to web agents from becoming overwhelming
- **Enforcement**: HG-17 (hard gate) + SG-7 (soft gate warning)
- **Rationale**: Panelist prompts (our input to web agents) should focus on evaluation criteria, not entire plan details
- **Implementation Note**: Measures our input token count to web agents, not web agent internal processing
- **Model Compatibility**: Works across all specified models (256K to 10M context)
- **Scaling**: Higher context models can proportionally increase budgets

### Plan Token Budget (Phase 3)
- **Limit**: 70,000 tokens (~52,500 words) or 42% of 166k effective context
- **Purpose**: Prevent plans from becoming unmanageable
- **Enforcement**: Manual review + soft gate warnings
- **Rationale**: Plans should be actionable and specific, not exhaustive documentation
- **Model Compatibility**: Works across all specified models (256K to 10M context)
- **Scaling**: Higher context models can proportionally increase budgets

### Total Panelist Context Budget (Phase 6.2)
- **Limit**: 32,000 tokens (~24,000 words) or 19% of 166k effective context
- **Components**: Brief (13k) + Panelist prompt (6.5k) + Plan for panelists (12.5k)
- **Purpose**: Ensure panelists have sufficient context without overwhelming attention mechanisms
- **Enforcement**: Component-level budget enforcement (HG-16, HG-17)
- **Rationale**: Panelists need focused context, not entire codebase or governance docs
- **Model Compatibility**: Works across all specified models (256K to 10M context)
- **Scaling**: Higher context models can proportionally increase budgets

## Token Counting Method

**Approximation**: 1 token ≈ 4 characters for English text
- This is a heuristic estimate, not exact token counting
- Sufficient for budget validation purposes
- Exact token counting requires tokenizer access (not needed for gates)
- For production: Consider implementing exact token counting via API calls

## Percentage-Based Budgeting Formula

**Formula**: `Budget = Context Window × Effective Percentage × Component Percentage`

**Example (200k context)**:
- Effective capacity: 200k × 0.65 = 130k tokens
- Brief budget: 130k × 0.08 = 10,400 tokens (rounded to 10k)
- Panelist prompt budget: 130k × 0.04 = 5,200 tokens (rounded to 5k)
- Plan budget: 130k × 0.42 = 54,600 tokens (rounded to 50k)

**Scaling Table** (Based on 65% effective capacity):

| Context Window | Effective (65%) | Brief (8%) | Panelist Prompt (4%) | Plan (42%) | Total Panelist (19%) |
|----------------|-----------------|-----------|---------------------|------------|---------------------|
| 256K (Kimi K2.7) | 166,400 | 13,312 → 13k | 6,656 → 6.5k | 69,888 → 70k | 31,616 → 32k |
| 1M (Most models) | 650,000 | 52,000 → 52k | 26,000 → 26k | 273,000 → 273k | 123,500 → 124k |
| 10M (Llama 4) | 6,500,000 | 520,000 → 520k | 260,000 → 260k | 2,730,000 → 2.7M | 1,235,000 → 1.2M |

**Model-Specific Context Windows**:
- **GPT-5.6 Luna**: 1,050,000 tokens (1.05M)
- **MiniMax M3**: 1,000,000 tokens (1M)
- **Gemini 3.5 Flash**: 1,048,576 tokens (1M)
- **Llama 4 Scout**: 10,000,000 tokens (10M)
- **Llama 4 Maverick**: 1,000,000 tokens (1M)
- **Qwen3.7 Plus**: 1,000,000 tokens (1M)
- **Kimi K2.7 Code**: 262,144 tokens (256K) ← **Baseline for compatibility**

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

### Brief Budget (10,000 tokens for 200k context)
- **Context**: Briefs are high-level overviews for panelist preparation
- **Prevents**: Briefs from becoming full plans (context rot)
- **Enables**: Panelists to quickly understand task scope
- **Percentage-Based**: 8% of effective context (120k tokens for 200k window)
- **Scaling**: Adapts to model context windows (2k for 32k, 50k for 1M)
- **Anthropic Research**: Concise briefs improve panelist focus and evaluation quality

### Panelist Prompt Budget (5,000 tokens for 200k context)
- **Context**: Panelist prompts include rubric, competency assignment, web search instructions that we send to web agents
- **Prevents**: Our input to web agents from becoming overwhelming (dilutes evaluation focus)
- **Enables**: Web agents to receive focused, actionable input
- **Percentage-Based**: 4% of effective context (120k tokens for 200k window)
- **Scaling**: Adapts to model context windows (1k for 32k, 25k for 1M)
- **Implementation Note**: Measures our input token count, not web agent internal processing (we don't control external agents)
- **Anthropic Research**: Focused prompts improve evaluation consistency

### Plan Budget (50,000 tokens for 200k context)
- **Context**: Plans are detailed specifications for execution
- **Prevents**: Plans from becoming comprehensive documentation (context overload)
- **Enables**: Executors to focus on actionable steps
- **Percentage-Based**: 42% of effective context (120k tokens for 200k window)
- **Scaling**: Adapts to model context windows (9k for 32k, 250k for 1M)
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