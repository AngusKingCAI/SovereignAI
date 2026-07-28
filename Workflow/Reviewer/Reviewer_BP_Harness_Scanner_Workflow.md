---
id: wf-rev-bp-harness-scanner
status: active
owner: reviewer-agent
updated: 2026-07-28
purpose: Comprehensive line-by-line scan of harness governance files to verify compliance with governance best practices and architectural consistency
---

# Reviewer BP Harness Scanner Workflow

**ID**: WF-REV-HARNESS-001  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual, Manual Batched, Automatic, Automatic Batched

## Purpose
Comprehensive line-by-line scan of all harness governance files to verify compliance with governance best practices, documentation standards, and architectural consistency. Unlike the App scanner (Reviewer_BP_App_Scanner_Workflow) which focuses on code quality and modularity, this workflow focuses on governance quality: workflow structure compliance, rule definition standards, configuration validity, markdown consistency, and cross-reference accuracy. Every governance file must be checked against governance-specific best practices without exception, with mandatory **{BP}** web search for documentation and governance best practices.

## Scope
**Harness Governance Only**: All files in project directory EXCEPT App/, Logs/, Plans/, Docs/ folders (comprehensive harness governance scan excluding application code, logs, plans, and documentation)

**Report Location**: Logs/Reviewer/BP/Harness/harness-best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md

**SCAN-REPORT**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md

## Reference Files (SSOT)
- **Compliance Criteria**: Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md (detailed compliance requirements by file type)
- **Subagent Prompting**: Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (subagent prompt templates and patterns)
- **Web Search Implementation**: Workflow/Reviewer/Reference/Web_Search_Implementation_Guide.md (robust web search infrastructure)

## Roles and Owners
- **Reviewer Agent**: Executes harness scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests harness scanning, approves findings and recommendations
- **Governance System**: Validation against governance best practices and architectural standards

## Trigger and End State
- **Trigger**: User requests best practice compliance scan of harness governance files
- **End State**: Comprehensive compliance report with findings, severity ratings, and actionable recommendations for governance improvements

## Workflow Steps (78 steps)

### Phase 0. Read Reviewer Rules + Governance
- 1. Read Rules/Reviewer/Reviewer_Rules.md to understand review criteria and governance compliance requirements
- 2. Read PRINCIPLES.md to understand constitutional framework and architectural principles
- 3. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Reviewer rules, constitutional principles, and governance compliance criteria loaded"

### Phase 1. Select Execution Mode
- 1. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)
  - **Manual Batched**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches for balanced efficiency with oversight
  - **Automatic**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency
  - **Automatic Batched**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation for maximum efficiency
- 2. Store selected execution mode for file processing strategy throughout workflow
- 3. **PRINT** "Execution mode selected - [Manual/Manual Batched/Automatic/Automatic Batched] will govern file processing strategy"

### Phase 2. Scan Scope Definition
- 1. Define scan scope: All files in project directory (excluding App/, Logs/, Plans/, Docs/ folders)
- 2. Ask user to select subagent strategy using popup menu:
  - **Use Subagents**: Delegate scanning to subagents for large-scale processing
  - **Direct Scanning**: Reviewer agent scans all files directly (recommended for smaller file counts)
- 3. Store selected subagent strategy for file processing throughout workflow
- 4. **CRITICAL REQUIREMENT**: Every single governance file must be checked against best practices - no file may be skipped
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Reviewer/Reference/Execution_Mode_Patterns.md)
- 6. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 7. **PRINT** "Scan scope defined - Harness governance comprehensive compliance verification - every governance file will be examined"

### Phase 3. File Discovery + Categorization (Alphabetical Order)
- 1. **PRE-FLIGHT VALIDATION**: Run file discovery validation script to ensure comprehensive harness coverage:
  - Execute: `python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI --baseline Scripts/Infrastructure/harness_directory_baseline.json`
  - **CRITICAL**: If validation fails (non-zero exit code), halt workflow and report missing directories
  - **CRITICAL**: Only proceed with scanning if validation passes (exit code 0)
- 2. Discover every single file in project directory excluding App/, Logs/, Plans/, Docs/ folders:
  - `find /c/SovereignAI -type f ! -path "*/App/*" ! -path "*/Logs/*" ! -path "*/Plans/*" ! -path "*/Docs/*"`
- 3. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
- 4. Categorize each file by type and complexity with detailed analysis:
  - Workflow files (Agent workflows, Reference files, Templates)
  - Rules files (Agent rules, governance rules)
  - Configuration files (.devin configuration, skills, hooks)
  - Governance files (AGENTS.md, INDEX.md)
  - Script files (Python scripts, shell scripts)
  - Data files (JSON, YAML, TOML, etc.)
  - Documentation files (Markdown, text, etc.)
- 5. **CRITICAL REQUIREMENT**: Verify that all governance files are accounted for and no files are excluded from scanning scope
- 6. **VALIDATION**: Validate that file discovery completed successfully and every single governance file is categorized without exception
- 7. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
- 8. **CROSS-CHECK VALIDATION**: Compare discovered files against validation baseline to ensure no governance directories were missed
- 9. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 10. **PRINT** "File discovery complete - [N] governance files categorized by type and sorted alphabetically - pre-flight validation passed - every governance file will be examined against best practices in chronological order"

### Phase 4. Compliance Scanning Execution (Execution Mode Dependent)
- 1. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
- 2. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
- 3. **IF Automatic mode**: Process files one by one in alphabetical order automatically without user confirmation
- 4. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
- 5. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against governance best practices - no file may be skipped
- 6. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
- 7. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 3
- 8. **INFRASTRUCTURE SETUP**: Initialize efficient report writer using Scripts/Infrastructure/efficient_report_writer.py for better performance
- 9. **WEB SEARCH ROBUSTNESS**: Use robust web search with caching and rate limiting (Scripts/Infrastructure/robust_web_search.py) to prevent failures
- 10. **VERBOSE OUTPUT**: Use **PRINT** commands after each file scan to maintain user visibility into progress, and explicitly output web search results to chat (not just to report) for maximum transparency
- 11. **EXECUTION MODE SPECIFIC PROCESS**:
  - **Manual**: For each file individually: **SCAN** → **{BP}** web search → output web search results to chat → document findings → **PRINT** progress → user confirmation → next file
  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → output web search results to chat → document findings → **PRINT** progress → user confirmation → next batch
  - **Automatic**: For each file individually: **SCAN** → **{BP}** web search → output web search results to chat → document findings → **PRINT** progress → next file (auto-stop on errors)
  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → output web search results to chat → document findings → **PRINT** progress → next batch (auto-stop on errors)
- 12. For each file, verify governance-specific compliance criteria based on file type:
  - **Workflow Files (.md)**: Template compliance (header structure, mandated sections), execution mode definition consistency, phase organization, universal framework references relevance, step numbering, terminology glossary references
  - **Rules Files (.md)**: YAML frontmatter validity, rule categorization patterns, enforcement logic clarity, dependency documentation, behavioral rule consistency with AGENTS.md
  - **Configuration Files (.json, .yaml, .toml)**: JSON/YAML syntax validity, schema compliance, hook configuration patterns, skill definition completeness, cross-reference accuracy
  - **Script Files (.py, .sh, .bash)**: Code quality standards, modularity, error handling, security practices, documentation completeness
  - **Documentation Files (.md, .txt, .rst)**: Heading hierarchy (H1-H6 consistency), list formatting (bullet/numbered), link validity (all links resolve), code block syntax (language specification), table structure correctness
  - **Markdown Standards**: Clear purpose statements, role definitions completeness, trigger/end state specificity, step actionability, PRINT command clarity
  - **Cross-Reference Integrity**: File path accuracy, workflow-to-rule reference validity, universal framework reference relevance, agent-specific reference alignment
  - **Terminology Consistency**: Alignment with Workflow/Workflow_Reference/Terminology_Glossary.md, consistent capitalization of {CAPITALIZED} terms, no outdated terminology
  - **Governance Best Practices**: Separation of universal vs agent-specific content, relevance requirement compliance, architectural consistency, DRY principles in governance
- 13. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to SCAN-REPORT file
- 14. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format using Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md as SSOT for prompting patterns
- 15. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single governance file without exception
- 16. **VALIDATION**: Validate that **{BP}** web search was performed for every single governance file without exception
- 17. **VALIDATION**: Validate that findings were documented to SCAN-REPORT file after each file/batch scan
- 18. **VALIDATION**: Validate that files were processed in alphabetical order
- 19. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Reviewer/Reference/Execution_Mode_Patterns.md)
- 20. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 21. **PRINT** "Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"

### Phase 5. Findings Consolidation (Scan Report Processing)
- 1. Collect all scanning results from SCAN-REPORT file (Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md)
- 2. Consolidate findings by category and severity using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md severity classifications
- 3. **CRITICAL REQUIREMENT**: Verify that findings exist for every single governance file in SCAN-REPORT - no file may be left unexamined or unreported
- 4. Cross-validate findings to eliminate duplicates and ensure consistency across all governance files
- 5. **VALIDATION**: Validate that findings consolidation completed successfully for every single governance file
- 6. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 7. **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] governance files - every governance file examined"

### Phase 6. Compliance Report Generation
- 1. Generate comprehensive compliance report with detailed findings for every single governance file:
  - Executive summary (overall compliance score, critical findings count, governance files examined)
  - Detailed findings by file with line numbers and specific violations for each governance file
  - Severity ratings with context for why each issue matters per governance file
  - Actionable recommendations with clear improvement paths per governance file
  - Compliance statistics (workflows compliant, rules properly structured, configuration valid) per governance file
- 2. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single governance file - no governance file may be omitted from the report
- 3. Save report to Logs/Reviewer/BP/Harness/harness-best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md
- 4. **VALIDATION**: Validate that report generation completed successfully and every governance file is included
- 5. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 6. **PRINT** "Compliance report generated - saved to Logs/Reviewer/BP/Harness/ - includes detailed analysis for every single governance file"

### Phase 7. Final Validation + User Review
- 1. Verify report completeness and accuracy
- 2. Ensure all findings are properly documented with specific references
- 3. Check that recommendations are actionable and clear
- 4. **VALIDATION**: Validate that final validation completed successfully
- 5. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 6. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 7. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 8. Planner-Ready Document Generation
- 1. Generate planner-ready implementation document structured for Planner agent consumption from consolidated findings:
  - Implementation requirements organized by priority and dependency
  - Specific governance changes needed with file paths and line references
  - Template compliance improvements with refactoring guidance
  - Best practices implementations with specific recommendations
  - Cross-reference validation improvements
  - Distinguished from code-focused improvements in Reviewer_BP_App_Scanner_Workflow
- 2. Structure document for Planner workflow compatibility:
  - Clear implementation phases with logical sequencing
  - Dependency mappings between governance changes
  - Risk assessment for each implementation block
  - Resource requirements and complexity estimates
- 3. Save planner-ready document to Plans/Reviewer/harness-reviewer-implementation-plan-[timestamp].md
- 4. **VALIDATION**: Validate that planner-ready document is complete and actionable
- 5. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 6. **PRINT** "Planner-ready document generated - saved to Plans/Reviewer/ - ready for Planner agent consumption"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 1. **PRINT** "Harness Best Practice Scanner workflow execution complete - workflow terminated"
- 2. **PRINT** "Compliance report available in Logs/Reviewer/BP/Harness/ for review and action"
- 3. **PRINT** "Planner-ready document available in Plans/Reviewer/ for implementation planning"
- 4. **TERMINATE**: End workflow execution (do not return to step 1)

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
For harness governance scanning (>150 files), use parallel subagents by directory following the prompting patterns and templates defined in Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (SSOT for subagent prompting).

### Subagent Coordination
- Launch 4-5 parallel subagents for independent governance categories
- Each subagent receives precise scope with specific file list
- Define exact output format for consistent consolidation
- Validate subagent results against governance best practices
- Consolidate findings into comprehensive report

## Scan Complexity Assessment

Based on harness governance scan:
- **Total Files**: [Determined at runtime via file discovery]
- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
- **Recommended Strategy**: Chunked scanning with 4-5 subagents by governance category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each governance file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per governance file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per governance file
- **Process**: **SCAN** governance file (alphabetical order) → **{BP}** web search → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md) → Next governance file (repeat for all governance files)
- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive harness scan to review each **{BP}** web search result and governance file analysis as it completes for maximum oversight
- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 files at a time with confirmation between batches
- **Automatic Batched Mode**: Maximum efficiency for large governance codebases - processes 5-10 files at a time automatically without confirmation

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each governance file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for current best practices) → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md) → Next governance file. This process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.

## Context Management Strategy

### PostCompaction Hook Configuration
- **Hook File**: .devin/hooks.v1.json
- **Purpose**: Reload governance files when context is compressed
- **Configuration**: Ensure PostCompaction hook is configured to reload:
  - Rules/Reviewer/Reviewer_Rules.md
  - Workflow/Workflow_Reference/Terminology_Glossary.md
  - Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
  - Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md

### Context Preservation
- **Governance State**: Compliance criteria and terminology definitions preserved through hook reload
- **Scanning Progress**: File discovery and categorization results preserved
- **Findings State**: SCAN-REPORT preserves findings through context compression
- **Web Search Context**: Best practices research cache preserved across context boundaries

## Infrastructure Requirements

### Required Scripts
- **File Discovery Validation**: Scripts/Infrastructure/file_discovery_validation.py (for pre-flight directory coverage validation)
- **Harness Baseline**: Scripts/Infrastructure/harness_directory_baseline.json (for expected harness directory structure)
- **Efficient Report Writer**: Scripts/Infrastructure/efficient_report_writer.py (for fast file writing)
- **Robust Web Search**: Scripts/Infrastructure/robust_web_search.py (for web search with caching and rate limiting)