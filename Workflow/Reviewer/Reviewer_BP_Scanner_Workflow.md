---
id: wf-rev-bp-scanner
status: active
owner: reviewer-agent
updated: 2026-07-28
version: "1.1"
purpose: Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency
expected_agent_type: reviewer-agent
persona:
  role: "Best Practice Compliance Scanner"
  expertise: "Line-by-line file scanning, best practice research, governance compliance verification, architectural consistency checking"
  process: "Systematic file-by-file scanning with mandatory web search for each file, findings documentation to comprehensive report"
  output: "Comprehensive SCAN-REPORT with findings, severity ratings, and actionable recommendations"
  constraints: "Mandatory {BP} web search for each file, no file may be skipped, line-by-line examination required"
---

# Reviewer BP Scanner Workflow (Unified)

**ID**: wf-rev-bp-scanner  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual, Manual Batched, Automatic, Automatic Batched

## Purpose
Comprehensive line-by-line scan of files to verify compliance with best practices, governance standards, and architectural consistency. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against best practices without exception, with mandatory **{BP}** web search for each file to ensure compliance with industry standards. This process is designed to be comprehensive and token-intensive, prioritizing thoroughness over speed.

## Scope
**Two Scanning Modes**:
- **App Mode**: All files in App/ directory (application code scanning)
- **Harness Mode**: All files in project directory EXCLUDING App/, Logs/, Plans/, Docs/ folders (governance scanning)

**SCAN-REPORT Locations**:
- **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
- **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md

## Reference Files (SSOT)
- **Compliance Criteria**: Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md (detailed compliance requirements by file type)
- **Subagent Prompting**: Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (subagent prompt templates and patterns)
- **Web Search Implementation**: Workflow/Reviewer/Reference/Web_Search_Implementation_Guide.md (robust web search infrastructure)

## Roles and Owners
- **Reviewer Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests scanning, selects scanning mode, approves findings and recommendations
- **Governance System**: Validation against governance best practices and architectural standards

## Trigger and End State
- **Trigger**: User requests best practice compliance scan
- **End State**: Single comprehensive SCAN-REPORT with findings, severity ratings, and actionable recommendations

## Workflow Steps (97 steps)

### Phase 0. Load Governance Rules
- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on agent type
- 2. **STATUS TRACKING**: Update workflow status to "phase_0_in_progress"
- 3. **PRINT** "Governance rules loaded dynamically based on agent type"
- 4. **VALIDATION**: Validate that governance rules loaded successfully before proceeding to Phase 1
- 5. **STATUS TRACKING**: Update workflow status to "phase_0_complete"

### Phase 1. Select Execution Mode
- 1. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at each inconsistency for user oversight
  - **Manual Batched**: Process files in batches with confirmation between batches
  - **Automatic**: Process automatically until failure, then ask user
  - **Automatic Batched**: Process batches automatically until failure, then ask user
- 2. Store selected execution mode for failure handling throughout workflow
- 3. **STATUS TRACKING**: Update workflow status to "phase_1_in_progress"
- 4. **PRINT** "Execution mode selected - [Manual/Manual Batched/Automatic/Automatic Batched] will govern failure handling"
- 5. **VALIDATION**: Validate that execution mode was selected and stored correctly before proceeding to Phase 2
- 6. **STATUS TRACKING**: Update workflow status to "phase_1_complete"

### Phase 2. Select Scanning Mode
- 1. Ask user to select scanning mode using popup menu:
  - **App Mode**: Scan App/ directory only (application code scanning)
  - **Harness Mode**: Scan harness governance files (excludes App/, Logs/, Plans/, Docs/)
- 2. Store selected scanning mode for scope definition throughout workflow
- 3. **STATUS TRACKING**: Update workflow status to "phase_2_in_progress"
- 4. **PRINT** "Scanning mode selected - [App Mode/Harness Mode] will govern scan scope and log locations"
- 5. **VALIDATION**: Validate that scanning mode was selected and stored correctly before proceeding to Phase 3
- 6. **STATUS TRACKING**: Update workflow status to "phase_2_complete"

### Phase 3. Scan Scope Definition
- 1. **IF App Mode**: Define scan scope as App/ directory (every single file - no exceptions)
- 2. **IF Harness Mode**: Define scan scope as all files in project directory (excluding App/, Logs/, Plans/, Docs/ folders)
- 3. **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
- 4. **PRINT** "Scan scope defined - scanning mode will govern which files are examined"
- 5. **VALIDATION**: Validate that scan scope was defined correctly before proceeding to Phase 4
- 6. **STATUS TRACKING**: Update workflow status to "phase_3_complete"

### Phase 4. File Discovery + Categorization (Alphabetical Order)
- 1. **STATUS TRACKING**: Update workflow status to "phase_4_in_progress"
- 2. Discover every single file based on scanning mode:
  - **App Mode**: Execute `find App -type f` to discover every single file in App/ directory (209 files expected) - verify no files are missed
  - **Harness Mode**: Execute `find . -type f ! -path "*/App/*" ! -path "*/Logs/*" ! -path "*/Plans/*" ! -path "*/Docs/*" ! -path "*/.git/*"` to discover every single file in project directory excluding specified folders (173 files expected)
- 3. **CRITICAL REQUIREMENT**: Verify file count matches expected values:
  - **App Mode**: Should discover exactly 209 files
  - **Harness Mode**: Should discover exactly 173 files
  - **CRITICAL**: If file count doesn't match expected values, halt workflow and investigate discrepancy
- 3. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
- 4. Categorize each file by module and complexity with detailed analysis:
  - **App Mode**: Memory components, Agent system components, Messaging/event system, Model registry components, Orchestrator components, Skills/adapters integration, Configuration files, Documentation files
  - **Harness Mode**: Workflow files, Rules files, Configuration files, Governance files, Script files, Data files, Documentation files
- 5. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope
- 6. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception
- 7. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 8. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
- 9. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 10. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 11. **IF App Mode**: **PRINT** "File discovery complete - [N] files categorized by module and sorted alphabetically - file count verification passed - every file will be examined against best practices in chronological order"
- 12. **IF Harness Mode**: **PRINT** "File discovery complete - [N] governance files categorized by type and sorted alphabetically - file count verification passed - every governance file will be examined against best practices in chronological order"

### Phase 5. Compliance Scanning Execution (Execution Mode Dependent)
- 1. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
- 2. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
- 3. **IF Automatic mode**: Process files one by one in alphabetical order automatically without user confirmation
- 4. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
- 5. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against best practices - no file may be skipped
- 6. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for best practices - this is mandatory for every file
- 7. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 4
- 8. **INFRASTRUCTURE SETUP**: Initialize efficient report writer based on scanning mode:
  - **App Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/App SCAN-REPORT
  - **Harness Mode**: Scripts/Infrastructure/efficient_report_writer.py Logs/Reviewer/BP/Harness SCAN-REPORT
- 9. **WEB SEARCH ROBUSTNESS**: Use robust web search with caching and rate limiting based on scanning mode:
  - **App Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/App/Cache/WebSearch
  - **Harness Mode**: Scripts/Infrastructure/robust_web_search.py Logs/Reviewer/BP/Harness/Cache/WebSearch
- 10. **VERBOSE OUTPUT**: Use **PRINT** commands after each file scan to maintain user visibility into progress, and explicitly output web search results to chat (not just to report) for maximum transparency
- 11. **EXECUTION MODE SPECIFIC PROCESS**:
  - **Manual**: For each file individually: **SCAN** → **{BP}** web search → output web search results to chat → document findings → **PRINT** progress → user confirmation → next file
  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → output web search results to chat → document findings → **PRINT** progress → user confirmation → next batch
  - **Automatic**: For each file individually: **SCAN** → **{BP}** web search → output web search results to chat → document findings → **PRINT** progress → next file (auto-stop on errors)
  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → output web search results to chat → document findings → **PRINT** progress → next batch (auto-stop on errors)
- 12. For each file, verify compliance criteria based on file type using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md as SSOT for detailed requirements
- 13. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to report file
- 14. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format using Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md as SSOT for prompting patterns
- 15. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single file without exception
- 16. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 17. **VALIDATION**: Validate that **{BP}** web search was performed for every single file without exception
- 18. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 19. **VALIDATION**: Validate that findings were documented to report file after each file/batch scan
- 20. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 21. **VALIDATION**: Validate that files were processed in alphabetical order
- 22. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 23. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
- 24. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 25. **IF App Mode**: **PRINT** "Compliance scanning complete - [N] files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"
- 26. **IF Harness Mode**: **PRINT** "Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"

### Phase 6. Findings Consolidation (Scan Report Processing)
- 1. Collect all scanning results from SCAN-REPORT file based on scanning mode:
  - **App Mode**: Logs/Reviewer/BP/App/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
  - **Harness Mode**: Logs/Reviewer/BP/Harness/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md
- 2. Consolidate findings by category and severity using Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md severity classifications
- 3. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file in SCAN-REPORT - no file may be left unexamined or unreported
- 4. Cross-validate findings to eliminate duplicates and ensure consistency across all files
- 5. **VALIDATION**: Validate that findings consolidation completed successfully for every single file
- 6. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 7. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 8. **IF App Mode**: **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] files - every file examined"
- 9. **IF Harness Mode**: **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] governance files - every governance file examined"

### Phase 7. Compliance Report Generation
- 1. Consolidate SCAN-REPORT to include comprehensive compliance analysis:
  - Executive summary (overall compliance score, critical findings count, files examined)
  - Detailed findings by file with line numbers and specific violations for each file
  - Severity ratings with context for why each issue matters per file
  - Actionable recommendations with clear improvement paths per file
  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file
- 2. **CRITICAL REQUIREMENT**: Ensure SCAN-REPORT includes analysis for every single file - no file may be omitted from the report
- 3. **CRITICAL REQUIREMENT**: SCAN-REPORT is the single comprehensive report - no separate files needed
- 4. **VALIDATION**: Validate that SCAN-REPORT consolidation completed successfully and every file is included
- 5. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 6. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 7. **IF App Mode**: **PRINT** "SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/App/ - includes detailed analysis for every single file"
- 8. **IF Harness Mode**: **PRINT** "SCAN-REPORT consolidated with comprehensive compliance analysis - saved to Logs/Reviewer/BP/Harness/ - includes detailed analysis for every single governance file"

### Phase 8. Final Validation + User Review
- 1. Verify report completeness and accuracy
- 2. Ensure all findings are properly documented with specific references
- 3. Check that recommendations are actionable and clear
- 4. **VALIDATION**: Validate that final validation completed successfully
- 5. **IF VALIDATION FAILS**: STOP - Report validation failure with specific details and await user intervention based on execution mode
- 6. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 7. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 8. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 1. **PRINT** "Best Practice Scanner workflow execution complete - workflow terminated"
- 2. **IF App Mode**: **PRINT** "Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/App/ for review and action"
- 3. **IF Harness Mode**: **PRINT** "Comprehensive SCAN-REPORT available in Logs/Reviewer/BP/Harness/ for review and action"
- 4. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Reviewer Customization**: Reviewer-specific quality criteria for compliance verification
- **Focus**: Compliance quality assessment with governance verification

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Reviewer Customization**: Reviewer-specific validation patterns for scanning verification
- **Focus**: Scanning validation and findings verification

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Reviewer Customization**: Reviewer-specific execution patterns for large-scale scanning
- **Focus**: Subagent coordination and failure handling during comprehensive scanning

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Reviewer Customization**: Reviewer-specific state tracking for scanning progress
- **Focus**: Scanning progress tracking and findings consolidation state management

### Review Mode Patterns
- **Reviewer-Specific Framework**: Workflow/Reviewer/Reference/Review_Mode_Patterns.md
- **Reviewer Customization**: Reviewer-specific execution mode patterns for comprehensive code review
- **Focus**: Step-by-step review oversight, file-by-file review patterns, subagent coordination

## Subagent Prompting Strategy

### Large-Scale Scanning Approach
For large-scale scanning (>150 files), use parallel subagents by module/category following the prompting patterns and templates defined in Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md (SSOT for subagent prompting).

### Subagent Coordination
- Launch 4-5 parallel subagents for independent module/categories
- Each subagent receives precise scope with specific file list
- Define exact output format for consistent consolidation
- Validate subagent results against compliance standards
- Consolidate findings into comprehensive report

## Scan Complexity Assessment

Based on scanning mode:
- **App Mode**: 209 files expected (application code scanning)
- **Harness Mode**: 173 files expected (governance files scanning)
- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module/category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per file
- **Process**: **SCAN** file (alphabetical order) → **{BP}** web search → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) → Next file (repeat for all files)
- **Final Output**: Single comprehensive SCAN-REPORT containing all findings, analysis, and recommendations
- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive scan to review each **{BP}** web search result and file analysis as it completes for maximum oversight
- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 files at a time with confirmation between batches
- **Automatic Batched Mode**: Maximum efficiency for large codebases - processes 5-10 files at a time automatically without confirmation

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for best practices) → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (based on scanning mode) → Next file. The final SCAN-REPORT serves as the single comprehensive report containing all findings, analysis, and recommendations. This process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.

## Context Management Strategy

### PostCompaction Hook Configuration
- **Hook File**: .devin/hooks.v1.json
- **Purpose**: Reload governance files when context is compressed
- **Configuration**: Ensure PostCompaction hook is configured to reload:
  - Rules/Reviewer/Reviewer_Rules.md
  - PRINCIPLES.md
  - Workflow/Workflow_Reference/Terminology_Glossary.md
  - Workflow/Reviewer/Reference/Compliance_Criteria_Reference.md
  - Workflow/Reviewer/Reference/Subagent_Prompting_Reference.md

### Context Preservation
- **Governance State**: Compliance criteria and terminology definitions preserved through hook reload
- **Scanning Progress**: File discovery and categorization results preserved
- **Findings State**: Incremental report preserves findings through context compression
- **Web Search Context**: Best practices research cache preserved across context boundaries

## Infrastructure Requirements

### Required Scripts
- **Efficient Report Writer**: Scripts/Infrastructure/efficient_report_writer.py (for performance optimization)
- **Robust Web Search**: Scripts/Infrastructure/robust_web_search.py (for web search with caching and rate limiting)

## Changelog

**2026-07-30**: YAML frontmatter fixes + early-exit patterns + temporal language fixes + step count correction
- Added missing YAML frontmatter fields (version, expected_agent_type, persona)
- Fixed ID consistency (standardized to wf-rev-bp-scanner)
- Added early-exit patterns in all validation phases
- Fixed temporal language (removed "current" references)
- Added Load Governance Rules and Select Execution Mode sections
- Fixed step count (81 → 97 steps)
- Updated version to 1.1

### Contextual Web Search
- **Script**: Scripts/Infrastructure/contextual_web_search.py (for intelligent best practice search based on document context)
- **Purpose**: Generate contextual search queries based on document type, content, and governance context
- **Integration**: Use during Phase 5 for each file to determine relevant best practice search patterns