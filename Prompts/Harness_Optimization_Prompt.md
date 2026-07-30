# Harness Infrastructure Optimization Prompt for Architect Agent (Subagent-Based Analysis)

**ARCHITECT AGENT INSTRUCTIONS - READ CAREFULLY**:

You are the Architect Agent executing a comprehensive harness infrastructure optimization analysis. You will coordinate multiple subagents to analyze different folders of the SovereignAI project.

**MANDATORY REQUIREMENTS**:

1. **SCAN EVERYTHING LINE BY LINE**: All subagents must SCAN every file line by line without skipping anything. This is mandatory and applies to ALL files including:
   - Governance files (Agents/, Rules/, Workflow/)
   - Implementation scripts (Scripts/)
   - Log files (Logs/)
   - Configuration files (.devin/, .claude/)
   - Template files
   - Documentation files
   - NO EXCEPTIONS - scanning is mandatory for all file types

2. **WEB SEARCH AND FACT CHECKING**: For every finding and suggestion, subagents MUST:
   - Perform web search for current best practices
   - Verify technical claims against authoritative sources
   - Use fact checking to validate assumptions
   - Provide specific web sources for all recommendations

3. **DEVIN CLI COMPATIBILITY**: All suggestions must work with Devin CLI architecture:
   - Use existing Devin CLI tools (read, write, edit, exec, etc.)
   - Follow Devin CLI patterns for agent workflows
   - Align with Devin CLI subagent patterns
   - Respect Devin CLI validation and governance systems

4. **SUBAGENT COORDINATION**: You will launch 5 subagents using run_subagent tool for focused analysis:
   - Subagent 1: Agents folder analysis
   - Subagent 2: Rules folder analysis  
   - Subagent 3: Workflow folder analysis
   - Subagent 4: Scripts folder analysis
   - Subagent 5: Logs folder analysis

5. **IMPROVEMENT FOCUS**: Look for optimization opportunities in:
   - Code organization and structure
   - Process efficiency
   - Tool usage patterns
   - Error handling and recovery
   - Validation and governance patterns
   - Subagent coordination
   - Resource management
   - Documentation clarity

---

## Analysis Scope

**Target Directory**: C:/SovereignAI/ (entire project)

**Folder-Specific Subagent Assignments**:

### Subagent 1: Agents Folder Analysis
**Target**: C:/SovereignAI/Agents/ and all agent-specific subdirectories
**Focus**: Agent governance, agent definitions, agent capabilities, agent boundaries
**SCAN Requirement**: SCAN every .md file line by line in Agents/ and all subdirectories
**Web Search Focus**: Agent architecture patterns, multi-agent systems best practices, agent governance frameworks
**Improvement Areas**: Agent boundary clarity, capability definition accuracy, governance enforcement, agent coordination patterns

### Subagent 2: Rules Folder Analysis  
**Target**: C:/SovereignAI/Rules/ and all rule-specific subdirectories
**Focus**: Rule definitions, rule enforcement, rule consistency, rule coverage
**SCAN Requirement**: SCAN every .md file line by line in Rules/ and all subdirectories
**Web Search Focus**: Governance frameworks, rule-based systems, compliance automation, validation patterns
**Improvement Areas**: Rule clarity, enforcement mechanisms, rule coverage gaps, consistency across agents, rule duplication

### Subagent 3: Workflow Folder Analysis
**Target**: C:/SovereignAI/Workflow/ and all workflow-specific subdirectories
**Focus**: Workflow definitions, workflow patterns, workflow execution, workflow validation
**SCAN Requirement**: SCAN every .md file line by line in Workflow/ and all subdirectories
**Web Search Focus**: Workflow automation patterns, process orchestration, CI/CD workflows, validation pipelines
**Improvement Areas**: Workflow structure, phase definitions, execution efficiency, validation integration, error handling, iteration patterns

### Subagent 4: Scripts Folder Analysis
**Target**: C:/SovereignAI/Scripts/ and all script subdirectories
**Focus**: Script organization, script functionality, script dependencies, script quality
**SCAN Requirement**: SCAN every .py file line by line in Scripts/ and all subdirectories
**Web Search Focus**: Python best practices, script organization patterns, automation scripts, tooling patterns
**Improvement Areas**: Code quality, organization structure, naming conventions, error handling, documentation, test coverage, dependencies

### Subagent 5: Logs Folder Analysis
**Target**: C:/SovereignAI/Logs/ and all log subdirectories
**Focus**: Logging patterns, log organization, log utility, log completeness
**SCAN Requirement**: SCAN every .md, .json, .txt file line by line in Logs/ and all subdirectories
**Web Search Focus**: Logging best practices, observability patterns, audit trails, log analysis
**Improvement Areas**: Log completeness, log structure, information density, queryability, retention policies, audit trail quality

---

## Subagent Coordination Instructions

### Parallel Execution Strategy
- Launch all 5 subagents in parallel for independent folder analysis
- Each subagent receives precise scope with specific folder assignment
- Define exact output format for consistent consolidation
- Validate subagent results against Devin CLI compatibility
- Consolidate findings into comprehensive optimization report

### Scope Definition Rules
- No overlapping scopes between subagents (prevents redundancy)
- Complete coverage - all relevant files must be assigned to exactly one subagent
- Clear boundaries - explicit folder assignments for each subagent
- Consistent criteria - all subagents use same improvement evaluation criteria

### Output Format Standardization
Each subagent must provide:
- Folder analyzed and file count
- Files SCANNED (line-by-line mandatory)
- Issues found with line numbers and severity ratings
- Improvement opportunities with Devin CLI compatibility verification
- Web search sources for all recommendations
- Specific actionable recommendations
- Fact-checked technical claims

---

## Subagent Prompt Template

### Subagent Prompt Template (Use for each subagent with folder-specific context)

```
You are an infrastructure optimization specialist analyzing [FOLDER NAME] for the SovereignAI project harness infrastructure.

**MANDATORY SCAN REQUIREMENT**: You must SCAN every file in [FOLDER PATH] line by line without skipping anything. This is mandatory and applies to ALL file types.

**FOLDER TO ANALYZE**: [Specific folder path]
**FILE TYPES**: [Specific file types for this folder]
**ANALYSIS FOCUS**: [Specific focus area for this folder]

**SCAN Process**:
For each file in the folder:
1. **SCAN** line by line without skipping anything - MANDATORY
2. **SECTION-BY-SECTION ANALYSIS**: For each section in the document:
   a. Read and understand the section content
   b. **{BP}** web search for current best practices specific to that section's topic (MANDATORY for every section)
   c. **FC?** fact check technical claims specific to that section (MANDATORY)
   d. Document improvement opportunities specific to that section
3. Verify Devin CLI compatibility for all findings
4. Document specific improvement opportunities based on SCAN results and section-specific BP research
5. Rate improvement priority (CRITICAL/HIGH/MEDIUM/LOW) based on impact

**Output Format**:
- Folder path and file count
- Files SCANNED (list all files processed)
- Issues found with line numbers and severity
- Improvement opportunities with Devin CLI compatibility check
- Specific actionable recommendations
- Best practices research findings with web sources
- Fact-checking validation results
- Priority ratings for each improvement

**DevIn CLI Compatibility Check**:
For each recommendation, verify:
- Can this be implemented using existing Devin CLI tools?
- Does this align with existing Devin CLI patterns?
- Will this work with current agent workflow structure?
- Does this respect existing governance and validation systems?

**Web Search Requirements**:
- For each section in each document, search for "[section topic] best practices" (current, not year-specific)
- Search for "DevIn CLI patterns for [section-specific component]"
- Search for "[section-specific domain] optimization"
- Verify all technical claims against authoritative sources with section-specific research
- Provide specific URLs for all research findings tied to each section analysis

**Fact Checking Requirements**:
- For each section, verify assumptions about current architecture specific to that section
- Cross-check assertions against actual code/log files relevant to that section
- Validate technical feasibility of suggestions for each section-specific improvement
- Confirm compatibility with existing systems for each section
- Never proceed with potentially incorrect information without section-specific verification
```

---

## Main Coordination Instructions

### Phase 1: Launch Subagents
- Use run_subagent tool to launch 5 subagents in parallel using subagent_general profile
- Assign each subagent to their specific folder with the subagent prompt template:
  - Subagent 1: C:/SovereignAI/Agents/ (Agents folder analysis)
  - Subagent 2: C:/SovereignAI/Rules/ (Rules folder analysis)
  - Subagent 3: C:/SovereignAI/Workflow/ (Workflow folder analysis)
  - Subagent 4: C:/SovereignAI/Scripts/ (Scripts folder analysis)
  - Subagent 5: C:/SovereignAI/Logs/ (Logs folder analysis)
- Wait for all subagents to complete their analysis

### Phase 2: Consolidate Results
- Collect all subagent outputs using read_subagent tool
- Cross-validate findings to eliminate duplicates
- Ensure consistency across subagent results
- Verify completeness - all folders must be analyzed
- Check accuracy of priority classifications

### Phase 3: Generate Optimization Report
- Create comprehensive optimization report with:
  - Executive summary of findings
  - Folder-specific improvement opportunities
  - Prioritized action items (CRITICAL/HIGH/MEDIUM/LOW)
  - Devin CLI compatibility verification for each recommendation
  - Web search sources for all recommendations
  - Fact-checking validation results
  - Implementation roadmap with sequencing

### Phase 4: Validation and Verification
- Verify all recommendations are technically feasible
- Ensure compatibility with existing Devin CLI patterns
- Check for conflicts between recommendations
- Validate that improvements won't break existing functionality
- Confirm all suggestions align with project goals

---

## Success Criteria

Analysis is complete when:
1. ✅ All 5 folders have been analyzed line by line (mandatory SCAN requirement met)
2. ✅ All findings are web-search verified with authoritative sources
3. ✅ All technical claims have been fact-checked
4. ✅ All recommendations are Devin CLI compatible
5. ✅ Comprehensive optimization report generated with prioritized action items
6. ✅ Implementation roadmap provided with proper sequencing

---

## Constraints and Guardrails

**Do not**:
- Skip SCAN requirement for any file type (mandatory line-by-line scanning)
- Make recommendations without web search verification
- Propose changes incompatible with Devin CLI architecture
- Suggest modifications that break existing governance systems
- Make assumptions without fact-checking
- Provide recommendations without specific file references and line numbers

**Always**:
- SCAN every file line by line without exceptions
- Use web search for all technical claims and best practices
- Fact-check all assumptions and assertions
- Verify Devin CLI compatibility for all suggestions
- Provide specific file references and line numbers for all findings
- Prioritize improvements based on impact and feasibility
- Consider existing governance and validation systems

---

## Output Format

Architect Agent should generate final optimization report in this structure:

```markdown
# SovereignAI Harness Infrastructure Optimization Report

**Date**: [Date]
**Analysis Type**: Comprehensive line-by-line SCAN with web search and fact checking
**Scope**: Agents/, Rules/, Workflow/, Scripts/, Logs/ folders
**Subagents Launched**: 5 (one per folder)

## Executive Summary
[Brief summary of key findings and optimization opportunities]

## Folder-Specific Analysis

### Agents Folder Analysis
[Subagent 1 findings]

### Rules Folder Analysis  
[Subagent 2 findings]

### Workflow Folder Analysis
[Subagent 3 findings]

### Scripts Folder Analysis
[Subagent 4 findings]

### Logs Folder Analysis
[Subagent 5 findings]

## Prioritized Action Items

### CRITICAL Priority
[High-impact, high-urgency improvements]

### HIGH Priority  
[High-impact, medium-urgency improvements]

### MEDIUM Priority
[Medium-impact improvements]

### LOW Priority
[Low-impact or nice-to-have improvements]

## Devin CLI Compatibility Verification
[For each recommendation, confirm Devin CLI compatibility]

## Implementation Roadmap
[Sequenced implementation plan with dependencies]

## Web Search Sources
[All web search URLs used for verification]

## Fact-Checking Validation
[Results of fact-checking for all technical claims]
```

---

**Remember**: As Architect Agent, you are analyzing the SovereignAI harness infrastructure for optimization opportunities. You must ensure all subagents SCAN everything line by line (mandatory), use web search and fact checking extensively with section-specific research, ensure all recommendations work with Devin CLI, and coordinate 5 subagents using run_subagent tool for comprehensive folder-specific analysis.
