# Planner Scanner Workflow

**ID**: WF-PLAN-SCAN-001  
**Owner**: Planner Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual, Automatic

## Purpose
Comprehensive line-by-line scan of all governance-related files to verify compliance with infrastructure standards, governance quality, and architectural consistency. Unlike the Reviewer scanner which focuses on code quality, this workflow focuses on infrastructure quality: workflow structure compliance, governance rules accuracy, configuration validity, and cross-reference integrity. Every governance file must be checked against infrastructure-specific best practices without exception, with mandatory **{BP}** web search for each file.

**Plan Output**: Workflow findings are structured as planning-focused recommendations following Plan Template format (≤120 lines, planning language only, infrastructure scope) for plan creation with appropriate revision splitting to respect Plan Template best practices. Plan number is determined by reading Plans/PLAN_TRACKING.md to identify next available sequential plan number.

## Scope
**Governance Files Only**: All files in Workflow/, Rules/, .devin/, AGENTS.md, INDEX.md (excludes Docs/, Logs/, Plans/, App/ folders)

**Report Location**: Logs/Planner/Scanner/governance-scan-[YYYY-MM-DD_HH-MM-SS].md

**SCAN-REPORT**: Logs/Planner/Scanner/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md

**Plan Output**: Plans/plan-{N}.md (with appropriate revision splitting as needed: {N}, {N}.1, {N}.2, etc.)

## Reference Files (SSOT)
- **Plan Template**: Workflow/Planner/Templates/Plan_Template.md (adapted for scan planning)
- **Plan Tracking**: Plans/PLAN_TRACKING.md (single source of truth for plan numbering and history)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality assessment criteria)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (validation patterns)
- **Terminology Glossary**: Workflow/Workflow_Reference/Terminology_Glossary.md (terminology definitions)

## Roles and Owners
- **Planner Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests governance scanning, approves findings and recommendations
- **Governance System**: Validation against infrastructure standards and architectural consistency

## Trigger and End State
- **Trigger**: User requests governance compliance scan of governance files
- **End State**: Comprehensive compliance report with findings, severity ratings, and actionable recommendations for governance improvements, plus plan creation (with appropriate revision splitting) following Plan Template format for implementation planning, using next available sequential plan number from PLAN_TRACKING.md

## Workflow Steps (77 steps)

### Phase 0. Read Planner Rules + Governance
- 1. Read Rules/Planner/Planner_Rules.md to understand planning criteria and infrastructure compliance requirements
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Read Workflow/Planner/Templates/Plan_Template.md to understand planning structure and format
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context, planning structure, and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Planner rules and infrastructure compliance criteria loaded"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)
  - **Automatic**: Process files one by one in alphabetical order automatically without user confirmation for maximum efficiency
- 9. Store selected execution mode for file processing strategy throughout workflow
- 10. **PRINT** "Execution mode selected - [Manual/Automatic] will govern file processing strategy"

### Phase 2. Scan Scope Definition
- 11. Define scan scope: Governance files (Workflow/, Rules/, .devin/, AGENTS.md, INDEX.md)
- 12. Define exclusion scope: Docs/, Logs/, Plans/, App/ folders (excluded from scan)
- 13. Determine scanning strategy based on file count and complexity:
  - Small scale (<50 files): Direct scanning by Planner agent
  - Medium scale (50-150 files): Chunked scanning with subagents
  - Large scale (>150 files): Parallel subagent scanning by directory
- 14. **CRITICAL REQUIREMENT**: Every single governance file must be checked against infrastructure best practices - no file may be skipped or excluded
- 15. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 16. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 17. **PRINT** "Scan scope defined - Governance comprehensive compliance verification - every governance file will be examined"

### Phase 3. File Discovery + Categorization (Alphabetical Order)
- 18. **PRE-FLIGHT VALIDATION**: Run file discovery validation script to ensure comprehensive governance coverage:
  - Execute: `python Scripts/Infrastructure/file_discovery_validation.py C:/SovereignAI --baseline Scripts/Infrastructure/harness_directory_baseline.json`
  - **CRITICAL**: If validation fails (non-zero exit code), halt workflow and report missing directories
  - **CRITICAL**: Only proceed with scanning if validation passes (exit code 0)
- 19. Discover every single file in governance using find command - verify no files are missed:
  - `find /c/SovereignAI -path "*/Workflow/*" -o -path "*/Rules/*" -o -path "*/.devin/*" -o -path "*/INDEX.md" -o -path "*/AGENTS.md"`
- 20. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
- 21. Categorize each file by type and complexity with detailed analysis:
  - Workflow files (Agent workflows, Reference files, Templates)
  - Rules files (Agent rules, governance rules)
  - Configuration files (.devin configuration, skills, hooks)
  - Governance files (AGENTS.md, INDEX.md)
  - Script files (Python scripts, shell scripts)
  - Data files (JSON, YAML, TOML, etc.)
  - Documentation files (Markdown, text, etc.)
- 22. **CRITICAL REQUIREMENT**: Verify that all governance files are accounted for and no files are excluded from scanning scope
- 23. **VALIDATION**: Validate that file discovery completed successfully and every single governance file is categorized without exception
- 24. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
- 25. **CROSS-CHECK VALIDATION**: Compare discovered files against validation baseline to ensure no governance directories were missed
- 26. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 27. **PRINT** "File discovery complete - [N] governance files categorized by type and sorted alphabetically - pre-flight validation passed - every governance file will be examined against infrastructure best practices in chronological order"

### Phase 4. Compliance Scanning Execution (Execution Mode Dependent)
- 28. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
- 29. **IF Automatic mode**: Process files one by one in alphabetical order automatically without user confirmation
- 30. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against infrastructure best practices - no file may be skipped
- 31. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
- 32. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 3
- 33. **EXECUTION MODE SPECIFIC PROCESS**:
  - **Manual**: For each file individually: **SCAN** → **{BP}** web search → document findings → user confirmation → next file
  - **Automatic**: For each file individually: **SCAN** → **{BP}** web search → document findings → next file (auto-stop on errors)
- 34. For each file, verify infrastructure-specific compliance criteria based on file type:
  - **Workflow Files (.md)**: Template compliance (header structure, mandated sections), execution mode definition consistency, phase organization, universal framework references relevance, step numbering, terminology glossary references
  - **Rules Files (.md)**: YAML frontmatter validity, rule categorization patterns, enforcement logic clarity, dependency documentation, behavioral rule consistency with AGENTS.md
  - **Configuration Files (.json, .yaml, .toml)**: JSON/YAML syntax validity, schema compliance, hook configuration patterns, skill definition completeness, cross-reference accuracy
  - **Script Files (.py, .sh, .bash)**: Code quality standards, modularity, error handling, security practices, documentation completeness
  - **Documentation Files (.md, .txt, .rst)**: Heading hierarchy (H1-H6 consistency), list formatting (bullet/numbered), link validity (all links resolve), code block syntax (language specification), table structure correctness
  - **Markdown Standards**: Clear purpose statements, role definitions completeness, trigger/end state specificity, step actionability, PRINT command clarity
  - **Cross-Reference Integrity**: File path accuracy, workflow-to-rule reference validity, universal framework reference relevance, agent-specific reference alignment
  - **Terminology Consistency**: Alignment with Workflow/Workflow_Reference/Terminology_Glossary.md, consistent capitalization of {CAPITALIZED} terms, no outdated terminology
  - **Infrastructure Best Practices**: Separation of universal vs agent-specific content, relevance requirement compliance, architectural consistency, DRY principles in governance
- 35. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to SCAN-REPORT file
- 36. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format (see Planner_Rules.md subagent usage section)
- 37. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single governance file without exception
- 38. **VALIDATION**: Validate that **{BP}** web search was performed for every single governance file without exception
- 39. **VALIDATION**: Validate that findings were documented to SCAN-REPORT file after each file/batch scan
- 40. **VALIDATION**: Validate that files were processed in alphabetical order
- 41. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Workflow_Reference/Execution_Mode_Patterns.md)
- 42. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 43. **PRINT** "Compliance scanning complete - [N] governance files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented to SCAN-REPORT"

### Phase 5. Findings Consolidation (SCAN-REPORT Processing)
- 44. Collect all scanning results from SCAN-REPORT file (Logs/Planner/Scanner/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md)
- 45. Consolidate findings by category and severity with detailed file-specific analysis:
  - **CRITICAL**: Infrastructure violations that must be fixed (broken file references, missing mandated sections, invalid JSON/YAML syntax, missing execution modes definition) per file
  - **HIGH**: Major infrastructure quality issues (template non-compliance, inconsistent execution modes, missing terminology glossary references, invalid cross-references) per file
  - **MEDIUM**: Documentation best practices improvements (markdown formatting, heading hierarchy, link validity, terminology consistency) per file
  - **LOW**: Minor infrastructure suggestions (PRINT command clarity, step description improvements, formatting enhancements) per file
- 46. **CRITICAL REQUIREMENT**: Verify that findings exist for every single governance file in SCAN-REPORT - no file may be left unexamined or unreported
- 47. Cross-validate findings to eliminate duplicates and ensure consistency across all governance files
- 48. **VALIDATION**: Validate that findings consolidation completed successfully for every single governance file
- 49. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 50. **PRINT** "Findings consolidated from SCAN-REPORT - [N] issues categorized by severity across [N] governance files - every governance file examined"

### Phase 6. Compliance Report Generation
- 51. Generate comprehensive compliance report with detailed findings for every single governance file:
  - Executive summary (overall compliance score, critical findings count, governance files examined)
  - Detailed findings by file with line numbers and specific violations for each governance file
  - Severity ratings with context for why each issue matters per governance file
  - Actionable recommendations with clear improvement paths per governance file
  - Compliance statistics (workflows compliant, rules properly structured, configuration valid) per governance file
- 52. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single governance file - no governance file may be omitted from the report
- 53. Save report to Logs/Planner/Scanner/governance-scan-[YYYY-MM-DD_HH-MM-SS].md
- 54. **VALIDATION**: Validate that report generation completed successfully and every governance file is included
- 55. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 56. **PRINT** "Compliance report generated - saved to Logs/Planner/Scanner/ - includes detailed analysis for every single governance file"

### Phase 7. Plan Creation for Findings
- 57. **PLAN NUMBER ASSIGNMENT**: Read Plans/PLAN_TRACKING.md to determine next available sequential plan number
- 58. **PLAN TEMPLATE COMPLIANCE**: Apply Plan Template format (Workflow/Planner/Templates/Plan_Template.md) to scan findings:
  - Plan structure: Context, Steps, Dependencies sections
  - Planning language only (no implementation details)
  - ≤120 lines total when possible (split into {N}.1, {N}.2 if exceeds)
  - Infrastructure scope focus (not application scope)
- 59. **PLAN SPLITTING STRATEGY**: Determine appropriate plan revision structure based on findings complexity:
  - If findings fit within ≤120 lines: Create single plan-{N}.md
  - If findings exceed ≤120 lines: Split into plan-{N}.1.md, plan-{N}.2.md, etc.
  - If findings are highly complex: Use granular splitting ({N}.0.1, {N}.0.2, etc.)
  - **CRITICAL**: Each plan revision must be standalone and executable independently
- 60. **PLAN STRUCTURE**: Create plan-{N}.md (or appropriate revisions) following template:
  - Header: Revision, Date, Goal (clear user-focused goal statement)
  - Context: Why governance improvements matter, expected outcomes, background
  - Steps: High-level planning actions (design, specify, define, outline, structure)
  - Dependencies: Clear dependency relationships, no circular dependencies
- 61. **VALIDATION**: Validate plan against Plan Template quality checks:
  - All required sections present (Context, Steps, Dependencies)
  - Metadata complete (Revision, Date, Goal)
  - Steps use planning language only (no implementation details)
  - Dependencies are clear and executable
  - No circular dependencies
  - Plan follows Planner_Rules.md format
  - Plan follows Planner scope (changes for manual implementation)
  - Plan ≤120 lines when possible
- 62. Save plan to Plans/plan-{N}.md (or appropriate revision numbers)
- 63. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 64. **PRINT** "Plan {N} created from scan findings - respects Plan Template format with appropriate revision splitting"
- **NOTE**: PLAN_TRACKING.md update (plan completion status, dependency updates) is Executor responsibility upon plan implementation completion

### Phase 8. Final Validation + User Review
- 65. Verify report completeness and accuracy
- 66. Ensure all findings are properly documented with specific references
- 67. Check that recommendations are actionable and clear
- 68. Verify plan structure compliance with Plan Template
- 69. **VALIDATION**: Validate that final validation completed successfully
- 70. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 71. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 72. **PRINT** "Final validation complete - compliance report and plan {N} ready for user review"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 73. **PRINT** "Planner Scanner workflow execution complete - workflow terminated"
- 74. **PRINT** "Compliance report available in Logs/Planner/Scanner/ for review and action"
- 75. **PRINT** "Plan {N} available in Plans/ directory for implementation planning"
- 76. **PRINT** "Note: PLAN_TRACKING.md will be updated by Executor upon plan implementation completion"
- 77. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Planner Customization**: Planner-specific quality criteria for infrastructure compliance verification
- **Focus**: Infrastructure quality assessment with architectural compliance

### Validation Enforcement
- **Universal Framework**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md
- **Planner Customization**: Planner-specific validation patterns for governance scanning verification
- **Focus**: Governance scanning validation and findings verification

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Planner Customization**: Planner-specific execution patterns for large-scale governance scanning
- **Focus**: Subagent coordination and failure handling during comprehensive governance scanning

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Planner Customization**: Planner-specific state tracking for governance scanning progress
- **Focus**: Governance scanning progress tracking and findings consolidation state management

## Subagent Prompting Strategy

### Large-Scale Governance Scanning Approach
For governance scanning (>150 files), use parallel subagents by directory:

**Workflow Files Subagent Prompt:**
```
**SCAN** the following workflow files in Workflow/ directory line by line without skipping anything:
- All files in Workflow/Architect/, Workflow/Planner/, Workflow/Executor/, Workflow/Reviewer/, Workflow/Researcher/
- All files in Workflow/Workflow_Reference/

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for workflow documentation and governance patterns (MANDATORY for every file)
3. Verify compliance with infrastructure best practices based on file type:
   - Markdown files: Header structure (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State), Phase organization and step numbering, Universal Framework References presence and completeness, Execution Modes definition in header and Phase 1, Cross-reference accuracy to other governance files, Markdown quality and formatting standards
   - Script files: Code quality standards, modularity, error handling, security practices, documentation completeness
   - Configuration files: JSON/YAML syntax validity, schema compliance, cross-reference accuracy
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- File type and complexity assessment
- Compliance status based on file type (PASS/FAIL with details)
- Header/structure compliance status (for markdown files)
- Cross-reference validation (PASS/FAIL with details)
- Quality issues found (with line numbers)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW)
- Specific actionable recommendations
- Best practices research findings with sources
```

**Rules Files Subagent Prompt:**
```
**SCAN** the following rules files in Rules/ directory line by line without skipping anything:
- All files in Rules/Architect/, Rules/Planner/, Rules/Executor/, Rules/Reviewer/, Rules/Researcher/

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for rule documentation and governance patterns (MANDATORY for every file)
3. Verify compliance with infrastructure best practices based on file type:
   - Markdown files: YAML frontmatter structure and completeness, Rule categorization and naming conventions, Rule enforcement patterns and dependencies, Cross-reference accuracy to workflows and other rules, Markdown quality and formatting standards
   - Script files: Code quality standards, modularity, error handling, security practices, documentation completeness
   - Configuration files: JSON/YAML syntax validity, schema compliance, cross-reference accuracy
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as workflow files]
```

**Configuration Files Subagent Prompt:**
```
**SCAN** the following configuration files in .devin/ directory line by line without skipping anything:
- All files in .devin/skills/
- All files in .devin/ (hooks, config)
- AGENTS.md and INDEX.md in project root

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for configuration management and documentation (MANDATORY for every file)
3. Verify compliance with infrastructure best practices based on file type:
   - JSON/YAML files: Syntax validity and schema compliance, Hook configuration structure and patterns, Skill definition completeness and patterns, Cross-reference accuracy to workflows and rules
   - Markdown files: Governance file documentation standards, cross-reference accuracy, markdown quality and formatting
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as workflow files]
```

## Scan Complexity Assessment

Based on governance scan:
- **Total Governance Files**: [Determined at runtime via file discovery]
- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
- **Recommended Strategy**: Chunked scanning with 3 subagents by governance category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each governance file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per governance file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per governance file
- **Process**: **SCAN** governance file (alphabetical order) → **{BP}** web search → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (Logs/Planner/Scanner/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md) → Next governance file (repeat for all governance files)
- **Plan Creation**: After scan completion, determine next available plan number from PLAN_TRACKING.md, structure findings into plan format with appropriate revision splitting ({N}, {N}.1, {N}.2, etc.) to respect Plan Template constraints (≤120 lines, planning language only)
- **Plan Tracking**: PLAN_TRACKING.md update (completion status, dependency updates) is Executor responsibility upon plan implementation completion
- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive governance scan to review each **{BP}** web search result and governance file analysis as it completes for maximum oversight
- **Automatic Mode**: Maximum efficiency for large governance - processes files automatically without confirmation

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each governance file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for current best practices) → **IMMEDIATELY DOCUMENT** to SCAN-REPORT (Logs/Planner/Scanner/SCAN-REPORT-[YYYY-MM-DD_HH-MM-SS].md) → Next governance file. After scan completion, plan number is determined from PLAN_TRACKING.md and findings are structured into plan format with appropriate revision splitting to respect Plan Template constraints (≤120 lines, planning language only). This incremental process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.

## Infrastructure Requirements

### Required Scripts
- **File Discovery Validation**: Scripts/Infrastructure/file_discovery_validation.py (for pre-flight directory coverage validation)
- **Harness Baseline**: Scripts/Infrastructure/harness_directory_baseline.json (for expected governance directory structure)
- **Efficient Report Writer**: Scripts/Infrastructure/efficient_report_writer.py (for fast file writing)
- **Robust Web Search**: Scripts/Infrastructure/robust_web_search.py (for reliable web search with caching)
- **Web Search Diagnostic**: Scripts/Infrastructure/test_web_search.py (for pre-flight testing)

### Required Reference Files
- **Plan Template**: Workflow/Planner/Templates/Plan_Template.md (structure reference)
- **Quality Assessment**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (quality criteria)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (validation patterns)
- **Terminology Glossary**: Workflow/Workflow_Reference/Terminology_Glossary.md (terminology definitions)

### Required Directory Structure
- **Reports**: Logs/Planner/Scanner/ (for scan reports and final reports)
- **Cache**: Logs/Planner/Cache/WebSearch/ (for web search caching)
- **Plans**: Plans/ (for Plan 35 output with appropriate revision splitting)
- **Baselines**: Scripts/Infrastructure/ (for directory validation baselines)

### Pre-Flight Validation Requirements
- **File Discovery Validation**: Must run validation script before scanning (Phase 3, Step 18)
- **Baseline Comparison**: Must use harness_directory_baseline.json for expected structure
- **Fail-Fast Enforcement**: Workflow must halt if validation fails (non-zero exit code)
- **Cross-Check Validation**: Must compare discovered files against baseline (Phase 3, Step 25)

### Plan Template Compliance Requirements
- **Structure Compliance**: Plans must follow Workflow/Planner/Templates/Plan_Template.md format exactly
- **Length Constraint**: ≤120 lines total when possible (split into 35.1, 35.2 if exceeds)
- **Planning Language**: Steps must use planning language only (design, specify, define, outline, structure)
- **No Implementation Details**: Plans are for manual implementation, not direct execution
- **Standalone Executability**: Each plan revision must be independently executable
- **Dependency Clarity**: Clear dependency relationships with no circular dependencies
- **Quality Checks**: All Plan Template quality checks must pass before delivery

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
- Cross-reference integrity validation