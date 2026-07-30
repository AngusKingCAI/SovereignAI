# Harness Infrastructure Optimization Prompt for Kimi (Comprehensive Analysis)

**REPOSITORY INFORMATION**:
- **Repository**: https://github.com/AngusKingCAI/SovereignAI.git
- **Clone Command**: `git clone https://github.com/AngusKingCAI/SovereignAI.git`

**KIMI INSTRUCTIONS - READ CAREFULLY**:

**STEP 0: CLONE REPOSITORY**
Before starting analysis, you MUST clone the SovereignAI repository:
- **Repository**: https://github.com/AngusKingCAI/SovereignAI.git
- **Clone Command**: `git clone https://github.com/AngusKingCAI/SovereignAI.git`
- **Navigate to repository**: `cd SovereignAI`
- **Confirm repository structure** before proceeding with analysis

You are performing a comprehensive harness infrastructure optimization analysis of the SovereignAI project. You will analyze the entire project yourself without subagents, using section-by-section analysis with targeted web search.

**MANDATORY REQUIREMENTS**:

1. **SCAN EVERYTHING LINE BY LINE**: You must SCAN every file line by line without skipping anything. This is mandatory and applies to ALL files including:
   - Governance files (Agents/, Rules/, Workflow/)
   - Implementation scripts (Scripts/)
   - Log files (Logs/)
   - Configuration files (.devin/, .claude/)
   - Template files
   - Documentation files
   - NO EXCEPTIONS - scanning is mandatory for all file types

2. **SECTION-BY-SECTION WEB SEARCH**: For each section in each document, you MUST:
   - Read and understand the section content
   - Perform web search for current best practices specific to that section's topic
   - Verify technical claims against authoritative sources
   - Provide specific web sources for each section analysis

3. **FACT CHECKING**: For every finding and suggestion, you MUST:
   - Verify technical claims against authoritative sources
   - Cross-check assertions against actual code/log files
   - Validate assumptions about current architecture
   - Provide specific evidence for all recommendations

4. **DEVIN CLI COMPATIBILITY**: All suggestions must work with Devin CLI architecture:
   - Use existing Devin CLI tools (read, write, edit, exec, etc.)
   - Follow Devin CLI patterns for agent workflows
   - Align with Devin CLI subagent patterns
   - Respect Devin CLI validation and governance systems

5. **COMPREHENSIVE SCOPE**: Analyze the entire project:
   - Agents/ folder (agent governance, agent definitions, agent capabilities)
   - Rules/ folder (rule definitions, rule enforcement, rule consistency)
   - Workflow/ folder (workflow definitions, workflow patterns, workflow execution)
   - Scripts/ folder (script organization, script functionality, script quality)
   - Logs/ folder (logging patterns, log organization, log completeness)

6. **IMPROVEMENT FOCUS**: Look for optimization opportunities in:
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

**Folder-Specific Analysis**:

### Agents Folder Analysis
**Target**: C:/SovereignAI/Agents/ and all agent-specific subdirectories
**Focus**: Agent governance, agent definitions, agent capabilities, agent boundaries
**SCAN Requirement**: SCAN every .md file line by line in Agents/ and all subdirectories
**Section-by-Section Search**: For each section in each agent file, search for "[section topic] best practices 2024"
**Improvement Areas**: Agent boundary clarity, capability definition accuracy, governance enforcement, agent coordination patterns

### Rules Folder Analysis  
**Target**: C:/SovereignAI/Rules/ and all rule-specific subdirectories
**Focus**: Rule definitions, rule enforcement, rule consistency, rule coverage
**SCAN Requirement**: SCAN every .md file line by line in Rules/ and all subdirectories
**Section-by-Section Search**: For each section in each rule file, search for "[section topic] governance patterns 2024"
**Improvement Areas**: Rule clarity, enforcement mechanisms, rule coverage gaps, consistency across agents, rule duplication

### Workflow Folder Analysis
**Target**: C:/SovereignAI/Workflow/ and all workflow-specific subdirectories
**Focus**: Workflow definitions, workflow patterns, workflow execution, workflow validation
**SCAN Requirement**: SCAN every .md file line by line in Workflow/ and all subdirectories
**Section-by-Section Search**: For each section in each workflow file, search for "[section topic] workflow automation 2024"
**Improvement Areas**: Workflow structure, phase definitions, execution efficiency, validation integration, error handling, iteration patterns

### Scripts Folder Analysis
**Target**: C:/SovereignAI/Scripts/ and all script subdirectories
**Focus**: Script organization, script functionality, script dependencies, script quality
**SCAN Requirement**: SCAN every .py file line by line in Scripts/ and all subdirectories
**Section-by-Section Search**: For each section in each script file, search for "[section topic] Python best practices 2024"
**Improvement Areas**: Code quality, organization structure, naming conventions, error handling, documentation, test coverage, dependencies

### Logs Folder Analysis
**Target**: C:/SovereignAI/Logs/ and all log subdirectories
**Focus**: Logging patterns, log organization, log utility, log completeness
**SCAN Requirement**: SCAN every .md, .json, .txt file line by line in Logs/ and all subdirectories
**Section-by-Section Search**: For each section in each log file, search for "[section topic] logging best practices 2024"
**Improvement Areas**: Log completeness, log structure, information density, queryability, retention policies, audit trail quality

---

## Analysis Process

### Section-by-Section Analysis Method
For each file in each folder:
1. **SCAN** line by line without skipping anything - MANDATORY
2. **SECTION-BY-SECTION ANALYSIS**: For each section in the document:
   a. Read and understand the section content
   b. **{BP}** web search for current best practices specific to that section's topic (MANDATORY for every section)
   c. **FC?** fact check technical claims specific to that section (MANDATORY)
   d. Document improvement opportunities specific to that section
3. Verify Devin CLI compatibility for all findings
4. Document specific improvement opportunities based on SCAN results and section-specific BP research
5. Rate improvement priority (CRITICAL/HIGH/MEDIUM/LOW) based on impact

### Web Search Requirements
- For each section in each document, search for "[section topic] best practices 2024"
- Search for "DevIn CLI patterns for [section-specific component]"
- Search for "[section-specific domain] optimization"
- Verify all technical claims against authoritative sources with section-specific research
- Provide specific URLs for all research findings tied to each section analysis

### Fact Checking Requirements
- For each section, verify assumptions about current architecture specific to that section
- Cross-check assertions against actual code/log files relevant to that section
- Validate technical feasibility of suggestions for each section-specific improvement
- Confirm compatibility with existing systems for each section
- Never proceed with potentially incorrect information without section-specific verification

### Devin CLI Compatibility Check
For each recommendation, verify:
- Can this be implemented using existing Devin CLI tools?
- Does this align with existing Devin CLI patterns?
- Will this work with current agent workflow structure?
- Does this respect existing governance and validation systems?

---

## Output Format

Provide comprehensive optimization report in this structure:

```markdown
# SovereignAI Harness Infrastructure Optimization Report

**Date**: [Date]
**Analysis Type**: Comprehensive line-by-line SCAN with section-by-section web search and fact checking
**Scope**: Agents/, Rules/, Workflow/, Scripts/, Logs/ folders
**Analysis Method**: Direct comprehensive analysis (no subagents)

## Executive Summary
[Brief summary of key findings and optimization opportunities]

## Folder-Specific Analysis

### Agents Folder Analysis
[Section-by-section analysis with web search sources and fact checking]

### Rules Folder Analysis  
[Section-by-section analysis with web search sources and fact checking]

### Workflow Folder Analysis
[Section-by-section analysis with web search sources and fact checking]

### Scripts Folder Analysis
[Section-by-section analysis with web search sources and fact checking]

### Logs Folder Analysis
[Section-by-section analysis with web search sources and fact checking]

## Prioritized Action Items

### CRITICAL Priority
[High-impact, high-urgency improvements with section-specific references]

### HIGH Priority  
[High-impact, medium-urgency improvements with section-specific references]

### MEDIUM Priority
[Medium-impact improvements with section-specific references]

### LOW Priority
[Low-impact or nice-to-have improvements with section-specific references]

## Devin CLI Compatibility Verification
[For each recommendation, confirm Devin CLI compatibility]

## Implementation Roadmap
[Sequenced implementation plan with dependencies]

## Web Search Sources
[All web search URLs used for verification, organized by section]

## Fact-Checking Validation
[Results of fact-checking for all technical claims, organized by section]
```

---

## Success Criteria

Analysis is complete when:
1. ✅ Repository cloned successfully and structure confirmed
2. ✅ All 5 folders have been analyzed line by line (mandatory SCAN requirement met)
3. ✅ All sections have been analyzed with targeted web search research
4. ✅ All findings are web-search verified with authoritative sources
5. ✅ All technical claims have been fact-checked with section-specific evidence
6. ✅ All recommendations are Devin CLI compatible
7. ✅ Comprehensive optimization report generated with prioritized action items
8. ✅ Implementation roadmap provided with proper sequencing

---

## Constraints and Guardrails

**Do not**:
- Skip SCAN requirement for any file type (mandatory line-by-line scanning)
- Skip section-by-section analysis (must analyze each section separately)
- Make recommendations without section-specific web search verification
- Propose changes incompatible with Devin CLI architecture
- Suggest modifications that break existing governance systems
- Make assumptions without section-specific fact-checking
- Provide recommendations without specific file references and line numbers

**Always**:
- SCAN every file line by line without exceptions
- Perform section-by-section analysis with targeted web search for each section
- Use web search for all technical claims and best practices with section-specific research
- Fact-check all assumptions and assertions with section-specific evidence
- Verify Devin CLI compatibility for all suggestions
- Provide specific file references and line numbers for all findings
- Prioritize improvements based on impact and feasibility
- Consider existing governance and validation systems

---

**Remember**: You are performing comprehensive harness infrastructure optimization analysis for SovereignAI. You must SCAN everything line by line (mandatory), perform section-by-section analysis with targeted web search, ensure all recommendations work with Devin CLI, and provide comprehensive analysis covering all 5 folders without using subagents.
