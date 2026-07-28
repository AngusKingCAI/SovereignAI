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
- **Large-Scale Scanning**: When scanning >150 files in target directory
- **Module-Based Analysis**: When analyzing distinct module categories independently
- **Parallel Processing**: When multiple independent analysis tasks can run concurrently
- **Specialized Expertise**: When specific domain knowledge is required

### When NOT to Use Subagents
- **Small-Scale Tasks**: Fewer than 50 files - use direct tools
- **Simple Analysis**: Straightforward compliance checks
- **User Control**: When user explicitly requested direct agent analysis
- **Unclear Scope**: When task boundaries are not well-defined

## Subagent Prompt Templates

### Generic Subagent Prompt Template

**Purpose**: Scan specified files for compliance with governance best practices

**Scope**: Target directory as specified in workflow

**Files**: [File list as specified in workflow] (all file types)

**Prompt Template**:
```
**SCAN** the following files in [target directory] line by line without skipping anything:
- [file list as specified in workflow] (all file types)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for [file type/directory type] patterns (MANDATORY for every file)
3. Verify compliance with compliance criteria based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Violations found (with line numbers for code files)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Code-Specific Subagent Prompt Template

**Purpose**: Scan code files for modularity and testing compliance

**Scope**: Target directory containing code files

**Files**: [code file list] (.py, .js, .ts, etc.)

**Prompt Template**:
```
**SCAN** the following code files in [target directory] line by line without skipping anything:
- [code file list] (.py, .js, .ts, etc.)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for [language] modularity and testing (MANDATORY for every file)
3. Verify compliance with modularity and testing requirements using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on modularity requirements (PASS/FAIL with details)
- Modularity violations found (with line numbers)
- Testing violations found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Configuration-Specific Subagent Prompt Template

**Purpose**: Scan configuration files for structure and security compliance

**Scope**: Target directory containing configuration files

**Files**: [configuration file list] (.json, .yaml, .toml, .ini, etc.)

**Prompt Template**:
```
**SCAN** the following configuration files in [target directory] line by line without skipping anything:
- [configuration file list] (.json, .yaml, .toml, .ini, etc.)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for [file type] configuration (MANDATORY for every file)
3. Verify compliance with configuration requirements using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on configuration requirements (PASS/FAIL with details)
- Structure violations found (with line numbers)
- Security violations found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW) per Compliance_Criteria_Reference.md
- Specific actionable recommendations
- Best practices research findings with sources
```

### Documentation-Specific Subagent Prompt Template

**Purpose**: Scan documentation files for structure and content compliance

**Scope**: Target directory containing documentation files

**Files**: [documentation file list] (.md, .txt, .rst, etc.)

**Prompt Template**:
```
**SCAN** the following documentation files in [target directory] line by line without skipping anything:
- [documentation file list] (.md, .txt, .rst, etc.)

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for [file type] documentation (MANDATORY for every file)
3. Verify compliance with documentation requirements using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on documentation requirements (PASS/FAIL with details)
- Structure violations found (with line numbers)
- Content violations found (with line numbers)
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