# Reviewer BP Harness Scanner Workflow

**ID**: WF-REV-HARNESS-001  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual, Manual Batched, Automatic Batched

## Purpose
Comprehensive line-by-line scan of all harness governance files to verify compliance with governance best practices, documentation standards, and architectural consistency. Unlike the App scanner (Reviewer_BP_App_Scanner_Workflow) which focuses on code quality and modularity, this workflow focuses on governance quality: workflow structure compliance, rule definition standards, configuration validity, markdown consistency, and cross-reference accuracy. Every governance file must be checked against governance-specific best practices without exception, with mandatory **{BP}** web search for documentation and governance best practices.

## Scope
**Harness Governance Only**: Workflow/, Rules/, .devin/, AGENTS.md, INDEX.md (excludes Docs/, Logs/, Plans/, App/ folders)

**Report Location**: Logs/Reviewer/BP/Harness/harness-best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md

**Incremental Report**: Logs/Reviewer/BP/Harness/incremental-scan-report.md

## Roles and Owners
- **Reviewer Agent**: Executes harness scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests harness scanning, approves findings and recommendations
- **Governance System**: Validation against governance best practices and architectural standards

## Trigger and End State
- **Trigger**: User requests best practice compliance scan of harness governance files
- **End State**: Comprehensive compliance report with findings, severity ratings, and actionable recommendations for governance improvements

## Workflow Steps (68 steps)

### Phase 0. Read Reviewer Rules + Governance
- 1. Read Rules/Reviewer/Reviewer_Rules.md to understand review criteria and governance compliance requirements
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Read Workflow/Workflow_Reference/Workflow_Template.md to understand workflow structure patterns
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Reviewer rules and governance compliance criteria loaded"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)
  - **Manual Batched**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches for balanced efficiency with oversight
  - **Automatic Batched**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation for maximum efficiency
- 9. Store selected execution mode for file processing strategy throughout workflow
- 10. **PRINT** "Execution mode selected - [Manual/Manual Batched/Automatic Batched] will govern file processing strategy"

### Phase 2. Scan Scope Definition
- 11. Define scan scope: Harness governance files (Workflow/, Rules/, .devin/, AGENTS.md, INDEX.md)
- 12. Define exclusion scope: Docs/, Logs/, Plans/, App/ folders (excluded from scan)
- 13. Determine scanning strategy based on file count and complexity:
  - Small scale (<50 files): Direct scanning by Reviewer agent
  - Medium scale (50-150 files): Chunked scanning with subagents
  - Large scale (>150 files): Parallel subagent scanning by directory
- 14. **CRITICAL REQUIREMENT**: Every single governance file must be checked against best practices - no file may be skipped or excluded
- 15. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Reviewer/Reference/Execution_Mode_Patterns.md)
- 16. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 17. **PRINT** "Scan scope defined - Harness governance comprehensive compliance verification - every governance file will be examined"

### Phase 3. File Discovery + Categorization (Alphabetical Order)
- 18. Discover every single markdown file in harness using find command - verify no files are missed:
  - `find /c/SovereignAI -name "*.md" -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md" -o -path "*/AGENTS.md"`
- 19. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
- 20. Categorize each file by type and complexity with detailed analysis:
  - Workflow files (Agent workflows, Reference files, Templates)
  - Rules files (Agent rules, governance rules)
  - Configuration files (.devin configuration, skills, hooks)
  - Governance files (AGENTS.md, INDEX.md)
- 21. **CRITICAL REQUIREMENT**: Verify that all governance files are accounted for and no files are excluded from scanning scope
- 22. **VALIDATION**: Validate that file discovery completed successfully and every single governance file is categorized without exception
- 23. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
- 24. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 25. **PRINT** "File discovery complete - [N] governance files categorized by type and sorted alphabetically - every governance file will be examined against best practices in chronological order"

### Phase 4. Compliance Scanning Execution (Execution Mode Dependent)
- 26. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
- 27. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
- 28. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
- 29. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against governance best practices - no file may be skipped
- 30. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
- 31. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 3
- 32. **EXECUTION MODE SPECIFIC PROCESS**:
  - **Manual**: For each file individually: **SCAN** → **{BP}** web search → document findings → user confirmation → next file
  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → document findings → user confirmation → next batch
  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → document findings → next batch (auto-stop on errors)
- 33. For each file, verify governance-specific compliance criteria:
  - **Workflow Files**: Template compliance (header structure, mandated sections), execution mode definition consistency, phase organization, universal framework references relevance, step numbering, terminology glossary references
  - **Rules Files**: YAML frontmatter validity, rule categorization patterns, enforcement logic clarity, dependency documentation, behavioral rule consistency with AGENTS.md
  - **Configuration Files**: JSON/YAML syntax validity, schema compliance, hook configuration patterns, skill definition completeness, cross-reference accuracy
  - **Markdown Standards**: Heading hierarchy (H1-H6 consistency), list formatting (bullet/numbered), link validity (all links resolve), code block syntax (language specification), table structure correctness
  - **Documentation Quality**: Clear purpose statements, role definitions completeness, trigger/end state specificity, step actionability, PRINT command clarity
  - **Cross-Reference Integrity**: File path accuracy, workflow-to-rule reference validity, universal framework reference relevance, agent-specific reference alignment
  - **Terminology Consistency**: Alignment with Workflow/Workflow_Reference/Terminology_Glossary.md, consistent capitalization of {CAPITALIZED} terms, no outdated terminology
  - **Governance Best Practices**: Separation of universal vs agent-specific content, relevance requirement compliance, architectural consistency, DRY principles in governance
- 34. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to report file
- 35. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format (see Reviewer_Rules.md subagent usage section)
- 36. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single governance file without exception
- 37. **VALIDATION**: Validate that **{BP}** web search was performed for every single governance file without exception
- 38. **VALIDATION**: Validate that findings were documented to report file after each file/batch scan
- 39. **VALIDATION**: Validate that files were processed in alphabetical order
- 40. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Reviewer/Reference/Execution_Mode_Patterns.md)
- 41. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 42. **PRINT** "Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented incrementally"

### Phase 5. Findings Consolidation (Incremental Report Processing)
- 43. Collect all scanning results from incremental report file (Logs/Reviewer/BP/Harness/incremental-scan-report.md)
- 44. Consolidate findings by category and severity with detailed file-specific analysis:
  - **CRITICAL**: Governance violations that must be fixed (broken file references, missing mandated sections, invalid JSON/YAML syntax, missing execution modes definition) per file
  - **HIGH**: Major governance quality issues (template non-compliance, inconsistent execution modes, missing terminology glossary references, invalid cross-references) per file
  - **MEDIUM**: Documentation best practices improvements (markdown formatting, heading hierarchy, link validity, terminology consistency) per file
  - **LOW**: Minor governance suggestions (PRINT command clarity, step description improvements, formatting enhancements) per file
- 45. **CRITICAL REQUIREMENT**: Verify that findings exist for every single governance file in incremental report - no file may be left unexamined or unreported
- 46. Cross-validate findings to eliminate duplicates and ensure consistency across all governance files
- 47. **VALIDATION**: Validate that findings consolidation completed successfully for every single governance file
- 48. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 49. **PRINT** "Findings consolidated from incremental report - [N] issues categorized by severity across [N] governance files - every governance file examined"

### Phase 6. Compliance Report Generation
- 50. Generate comprehensive compliance report with detailed findings for every single governance file:
  - Executive summary (overall compliance score, critical findings count, governance files examined)
  - Detailed findings by file with line numbers and specific violations for each governance file
  - Severity ratings with context for why each issue matters per governance file
  - Actionable recommendations with clear improvement paths per governance file
  - Compliance statistics (workflows compliant, rules properly structured, configuration valid) per governance file
- 51. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single governance file - no governance file may be omitted from the report
- 52. Save report to Logs/Reviewer/BP/Harness/harness-best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md
- 53. **VALIDATION**: Validate that report generation completed successfully and every governance file is included
- 54. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 55. **PRINT** "Compliance report generated - saved to Logs/Reviewer/BP/Harness/ - includes detailed analysis for every single governance file"

### Phase 7. Final Validation + User Review
- 56. Verify report completeness and accuracy
- 57. Ensure all findings are properly documented with specific references
- 58. Check that recommendations are actionable and clear
- 59. **VALIDATION**: Validate that final validation completed successfully
- 60. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 61. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 62. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 8. Planner-Ready Document Generation
- 63. Generate planner-ready implementation document structured for Planner agent consumption from consolidated findings:
  - Implementation requirements organized by priority and dependency
  - Specific governance changes needed with file paths and line references
  - Template compliance improvements with refactoring guidance
  - Best practices implementations with specific recommendations
  - Cross-reference validation improvements
  - Distinguished from code-focused improvements in Reviewer_BP_App_Scanner_Workflow
- 64. Structure document for Planner workflow compatibility:
  - Clear implementation phases with logical sequencing
  - Dependency mappings between governance changes
  - Risk assessment for each implementation block
  - Resource requirements and complexity estimates
- 65. Save planner-ready document to Plans/Reviewer/harness-reviewer-implementation-plan-[timestamp].md
- 66. **VALIDATION**: Validate that planner-ready document is complete and actionable
- 67. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 68. **PRINT** "Planner-ready document generated - saved to Plans/Reviewer/ - ready for Planner agent consumption"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 69. **PRINT** "Harness Best Practice Scanner workflow execution complete - workflow terminated"
- 70. **PRINT** "Compliance report available in Logs/Reviewer/BP/Harness/ for review and action"
- 71. **PRINT** "Planner-ready document available in Plans/Reviewer/ for implementation planning"
- 72. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Reviewer Customization**: Reviewer-specific quality criteria for governance compliance verification
- **Focus**: Governance quality assessment with architectural compliance

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Reviewer Customization**: Reviewer-specific validation patterns for governance scanning verification
- **Focus**: Governance scanning validation and findings verification

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Reviewer Customization**: Reviewer-specific execution patterns for large-scale governance scanning
- **Focus**: Subagent coordination and failure handling during comprehensive governance scanning

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Reviewer Customization**: Reviewer-specific state tracking for governance scanning progress
- **Focus**: Governance scanning progress tracking and findings consolidation state management

### Review Mode Patterns
- **Reviewer-Specific Framework**: Workflow/Reviewer/Reference/Execution_Mode_Patterns.md
- **Reviewer Customization**: Reviewer-specific execution mode patterns for comprehensive governance review
- **Focus**: Step-by-step review oversight, file-by-file review patterns, subagent coordination

## Subagent Prompting Strategy

### Large-Scale Governance Scanning Approach
For harness governance scanning (>150 files), use parallel subagents by directory:

**Workflow Files Subagent Prompt:**
```
**SCAN** the following workflow files in Workflow/ directory line by line without skipping anything:
- All .md files in Workflow/Architect/, Workflow/Planner/, Workflow/Executor/, Workflow/Reviewer/, Workflow/Researcher/
- All .md files in Workflow/Workflow_Reference/

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for workflow documentation and governance patterns (MANDATORY for every file)
3. Verify compliance with governance best practices:
   - Header structure (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State)
   - Phase organization and step numbering
   - Universal Framework References presence and completeness
   - Execution Modes definition in header and Phase 1
   - Cross-reference accuracy to other governance files
   - Markdown quality and formatting standards
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- Workflow type and complexity assessment
- Header compliance status (PASS/FAIL with details)
- Structure compliance status (PASS/FAIL with details)
- Cross-reference validation (PASS/FAIL with details)
- Markdown quality issues found (with line numbers)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW)
- Specific actionable recommendations
- Best practices research findings with sources
```

**Rules Files Subagent Prompt:**
```
**SCAN** the following rules files in Rules/ directory line by line without skipping anything:
- All .md files in Rules/Architect/, Rules/Planner/, Rules/Executor/, Rules/Reviewer/, Rules/Researcher/

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for rule documentation and governance patterns (MANDATORY for every file)
3. Verify compliance with governance best practices:
   - YAML frontmatter structure and completeness
   - Rule categorization and naming conventions
   - Rule enforcement patterns and dependencies
   - Cross-reference accuracy to workflows and other rules
   - Markdown quality and formatting standards
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as workflow files]
```

**Configuration Files Subagent Prompt:**
```
**SCAN** the following configuration files in .devin/ directory line by line without skipping anything:
- All .md files in .devin/skills/
- All .json files in .devin/ (hooks, config)
- AGENTS.md and INDEX.md in project root

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for configuration management and documentation (MANDATORY for every file)
3. Verify compliance with governance best practices:
   - JSON/YAML syntax validity and schema compliance
   - Hook configuration structure and patterns
   - Skill definition completeness and patterns
   - Governance file documentation standards
   - Cross-reference accuracy to workflows and rules
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as workflow files]
```

### Subagent Coordination
- Launch 3 parallel subagents for independent governance categories
- Each subagent receives precise scope with specific file list
- Define exact output format for consistent consolidation
- Validate subagent results against governance best practices
- Consolidate findings into comprehensive report

## Scan Complexity Assessment

Based on harness governance scan:
- **Total Governance Files**: [Determined at runtime via file discovery]
- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
- **Recommended Strategy**: Chunked scanning with 3 subagents by governance category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each governance file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per governance file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per governance file
- **Process**: **SCAN** governance file (alphabetical order) → **{BP}** web search → **IMMEDIATELY DOCUMENT** to incremental report (Logs/Reviewer/BP/Harness/incremental-scan-report.md) → Next governance file (repeat for all governance files)
- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive harness scan to review each **{BP}** web search result and governance file analysis as it completes for maximum oversight
- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 governance files at a time with confirmation between batches
- **Automatic Batched Mode**: Maximum efficiency for large harness - processes 5-10 governance files at a time automatically without confirmation

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each governance file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for current best practices) → **IMMEDIATELY DOCUMENT** to incremental report (Logs/Reviewer/BP/Harness/incremental-scan-report.md) → Next governance file. This incremental process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.

## Context Management Strategy

### PostCompaction Hook Configuration
- **Global Hook**: PostCompaction hook configured in user-level Devin CLI config (~/.config/devin/hooks.v1.json)
- **Purpose**: Reload governance files when context is compressed to maintain compliance verification capability
- **Files Reloaded**: 
  - Agents/Reviewer/AGENTS.md (Reviewer agent configuration)
  - Rules/Reviewer/Reviewer_Rules.md (Review criteria and compliance requirements)
  - Workflow/Reviewer/Reviewer_Harness_Best_Practice_Scanner_Workflow.md (Current workflow)
  - Workflow/Workflow_Reference/Terminology_Glossary.md (Terminology definitions)
- **Trigger**: Automatically fires when Devin CLI compresses context during long scanning sessions
- **Benefit**: Ensures governance scanning workflow remains robust even with very large harness and extended context usage

## Governance-Specific Best Practice Categories

### Workflow Best Practices
- Header structure completeness and accuracy
- Phase organization and logical flow
- Step numbering consistency
- Universal Framework References relevance
- Execution Modes definition and alignment
- Cross-reference accuracy to other governance files

### Rules Best Practices
- YAML frontmatter structure and completeness
- Rule categorization and naming conventions
- Rule enforcement patterns clarity
- Dependency documentation accuracy
- Cross-reference validity to workflows

### Configuration Best Practices
- JSON/YAML syntax validity
- Schema compliance and structure
- Hook configuration patterns
- Skill definition completeness
- Documentation standards

### Documentation Best Practices
- Markdown formatting consistency
- Heading hierarchy structure
- Link validity and accuracy
- Code block syntax correctness
- Table structure validity
- Terminology consistency

### Cross-Reference Best Practices
- File reference accuracy
- Workflow reference consistency
- Rule reference validity
- Universal framework reference relevance
- Agent-specific reference alignment