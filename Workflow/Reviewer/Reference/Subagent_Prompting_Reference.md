---
id: wf-rev-ref-subagent-prompting
status: active
owner: reviewer-agent
updated: 2026-07-28
purpose: Single source of truth for subagent prompting patterns and templates used in review workflows
---

# Subagent Prompting Reference for Reviewer Agent

## Purpose
Single source of truth (SSOT) for subagent prompting patterns and templates used in review workflows. This document contains the specific prompts and criteria that workflows reference when delegating to subagents.

## Subagent Usage Guidelines

### When to Use Subagents
- **Large-Scale Scanning**: When scanning >150 files in App/ directory
- **Module-Based Analysis**: When analyzing distinct module categories independently
- **Parallel Processing**: When multiple independent analysis tasks can run concurrently
- **Specialized Expertise**: When specific domain knowledge is required

### When NOT to Use Subagents
- **Small-Scale Tasks**: Fewer than 50 files - use direct tools
- **Simple Analysis**: Straightforward compliance checks
- **User Control**: When user explicitly requested direct agent analysis
- **Unclear Scope**: When task boundaries are not well-defined

## Subagent Prompt Templates

### Memory Components Subagent Prompt

**Purpose**: Scan memory backend components for compliance

**Scope**: App/sovereignai/memory/ directory

**Files**: episodic_backend, persistent_graph, procedural_backend, trace_backend, working_backend, graph_backend, gateway, episodic_consumer (all file types)

**Prompt Template**:
```
**SCAN** the following memory component files in App/sovereignai/memory/ directory line by line without skipping anything:
- episodic_backend, persistent_graph, procedural_backend, trace_backend, working_backend, graph_backend, gateway, episodic_consumer (all file types)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for memory component patterns (MANDATORY for every file)
3. Verify compliance with Executor rules based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Modularity violations found (with line numbers for code files)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Agent System Components Subagent Prompt

**Purpose**: Scan agent system components for compliance

**Scope**: App/sovereignai/agent/ directory

**Files**: react, factory, history, prompts, structured_output, tool_session, types, config, protocols (all file types)

**Prompt Template**:
```
**SCAN** the following agent system files in App/sovereignai/agent/ directory line by line without skipping anything:
- react, factory, history, prompts, structured_output, tool_session, types, config, protocols (all file types)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for agent system patterns (MANDATORY for every file)
3. Verify compliance with Executor rules based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Modularity violations found (with line numbers for code files)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Messaging/Event System Subagent Prompt

**Purpose**: Scan messaging and event system components for compliance

**Scope**: App/sovereignai/shared/ and App/sovereignai/messaging/ directories

**Files**: event_bus, trace_emitter, event_registry, bus, security, adapter, schema (all file types)

**Prompt Template**:
```
**SCAN** the following messaging/event files in App/sovereignai/shared/ and App/sovereignai/messaging/ directories line by line without skipping anything:
- event_bus, trace_emitter, event_registry, bus, security, adapter, schema (all file types)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for messaging/event patterns (MANDATORY for every file)
3. Verify compliance with Executor rules based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Modularity violations found (with line numbers for code files)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Other Modules Subagent Prompt

**Purpose**: Scan remaining modules not covered by specialized subagents

**Scope**: App/sovereignai/ (excluding memory, agent, messaging directories)

**Files**: model_registry/, orchestrator/, librarian/, lifecycle/, managers/, options/, skills/, etc. (all file types)

**Prompt Template**:
```
**SCAN** the remaining files in App/sovereignai/ (model_registry/, orchestrator/, librarian/, lifecycle/, managers/, options/, skills/, etc.) line by line without skipping anything (all file types).

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for specific module types (MANDATORY for every file)
3. Verify compliance with Executor rules based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Modularity violations found (with line numbers for code files)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

## Subagent Coordination Guidelines

### Parallel Execution Strategy
- **Launch 4-5 parallel subagents** for independent module categories
- **Each subagent receives precise scope** with specific file list
- **Define exact output format** for consistent consolidation
- **Validate subagent results** against established criteria
- **Consolidate findings** into comprehensive report

### Scope Definition Rules
- **No overlapping scopes** between subagents (prevents redundancy)
- **Complete coverage** - all files must be assigned to exactly one subagent
- **Clear boundaries** - explicit file lists for each subagent
- **Consistent criteria** - all subagents use same compliance reference

### Output Format Standardization
- **Uniform structure** across all subagent outputs
- **Consistent severity ratings** using Compliance_Criteria_Reference.md
- **Specific line references** for all findings
- **Actionable recommendations** with clear improvement paths
- **Best practices sources** documented for all research

### Quality Validation
- **Cross-validate findings** to eliminate duplicates
- **Ensure consistency** across subagent results
- **Verify completeness** - all files in scope must be analyzed
- **Check accuracy** of severity classifications
- **Validate best practices research** quality and relevance

## Failure Handling

### Subagent Failure Scenarios
- **Scope confusion**: Reclarify scope and relaunch subagent
- **Quality issues**: Provide feedback and request refinement
- **Technical failures**: Investigate and retry with adjusted parameters
- **Timeout**: Break into smaller chunks and retry

### Recovery Strategies
- **Partial results**: Salvage completed work and reassign remaining
- **Quality concerns**: Manual review of questionable findings
- **Consolidation failures**: Manual intervention for report generation
- **Validation failures**: targeted re-analysis of problematic files

## Performance Optimization

### Chunking Strategy
- **Small modules (< 20 files)**: Single subagent
- **Medium modules (20-50 files)**: 2-3 subagents
- **Large modules (> 50 files)**: 4-5 subagents
- **Adjust based on complexity** and analysis depth required

### Resource Management
- **Monitor subagent quota** usage for recovery tracking
- **Balance parallel execution** with system resources
- **Implement progressive backoff** if rate limiting occurs
- **Cache best practices research** across subagents where applicable