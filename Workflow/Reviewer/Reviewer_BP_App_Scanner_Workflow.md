# Reviewer BP App Scanner Workflow

**ID**: WF-REV-APP-001  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)
**Execution Modes**: Manual, Manual Batched, Automatic Batched

## Purpose
Comprehensive line-by-line scan of every single file in the App/ directory to verify compliance with Executor rules for modularity, testing, and best practices. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against current best practices without exception, with mandatory **{BP}** web search for each file to ensure compliance with the latest industry standards. This process is designed to be comprehensive and token-intensive, prioritizing thoroughness over speed.

## Scope
**App/ Directory Only**: All Python files in App/ directory (no exceptions)

**Report Location**: Logs/Reviewer/BP/App/best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md

**Incremental Report**: Logs/Reviewer/BP/App/incremental-scan-report.md

## Roles and Owners
- **Reviewer Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests scanning, approves findings and recommendations
- **Governance System**: Validation against Executor rules and quality standards

## Trigger and End State
- **Trigger**: User requests best practice compliance scan of App/ directory
- **End State**: Comprehensive compliance report with findings, severity ratings, and actionable recommendations; planner-ready document for implementation planning

## Workflow Steps (65 steps)

### Phase 0. Read Reviewer Rules + Governance
- 1. Read Rules/Reviewer/Reviewer_Rules.md to understand review criteria and modular compliance requirements
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Read Rules/Executor/Executor_Rules.md to understand modularity and testing requirements to verify
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Reviewer rules and Executor compliance criteria loaded"

### Phase 1. Select Execution Mode
- 8. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Process files one by one in alphabetical order, requiring user confirmation at each file for maximum oversight (recommended for first comprehensive scan)
  - **Manual Batched**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches for balanced efficiency with oversight
  - **Automatic Batched**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation for maximum efficiency
- 9. Store selected execution mode for file processing strategy throughout workflow
- 10. **PRINT** "Execution mode selected - [Manual/Manual Batched/Automatic Batched] will govern file processing strategy"

### Phase 2. Scan Scope Definition
- 11. Define scan scope: App/ directory (every single Python file - no exceptions)
- 12. Determine scanning strategy based on file count and complexity:
  - Small scale (<50 files): Direct scanning by Reviewer agent
  - Medium scale (50-150 files): Chunked scanning with subagents
  - Large scale (>150 files): Parallel subagent scanning by module
- 13. **CRITICAL REQUIREMENT**: Every single file must be checked against best practices - no file may be skipped or excluded
- 14. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
- 15. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 16. **PRINT** "Scan scope defined - App/ directory comprehensive compliance verification - every file will be examined"

### Phase 3. File Discovery + Categorization (Alphabetical Order)
- 17. Discover every single Python file in App/ directory using find command - verify no files are missed
- 18. **CRITICAL REQUIREMENT**: Sort files alphabetically by full path from first folder to last folder (chronological scanning order)
- 19. Categorize each file by module and complexity with detailed analysis:
  - Memory components (episodic_backend.py, persistent_graph.py, etc.)
  - Agent system components (react.py, factory.py, etc.)
  - Messaging/event system (event_bus.py, trace_emitter.py, etc.)
  - Model registry components (sync.py, database.py, etc.)
  - Orchestrator components (facade.py, dispatcher.py, etc.)
  - Skills/adapters integration (various adapter and skill files)
- 20. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope
- 21. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception
- 22. **VALIDATION**: Validate that files are sorted alphabetically by full path for consistent scanning order
- 23. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 24. **PRINT** "File discovery complete - [N] Python files categorized by module and sorted alphabetically - every file will be examined against best practices in chronological order"

### Phase 4. Compliance Scanning Execution (Execution Mode Dependent)
- 25. **IF Manual mode**: Process files one by one in alphabetical order, requiring user confirmation at each file before proceeding
- 26. **IF Manual Batched mode**: Process files in batches of 5-10 files in alphabetical order, requiring user confirmation between batches
- 27. **IF Automatic Batched mode**: Process files in batches of 5-10 files in alphabetical order automatically without user confirmation
- 28. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against Executor rules and best practices - no file may be skipped
- 29. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
- 30. **CRITICAL REQUIREMENT**: Process files in alphabetical order by full path as discovered in Phase 3
- 31. **EXECUTION MODE SPECIFIC PROCESS**:
  - **Manual**: For each file individually: **SCAN** → **{BP}** web search → document findings → user confirmation → next file
  - **Manual Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → document findings → user confirmation → next batch
  - **Automatic Batched**: For each batch of 5-10 files: **SCAN** all files in batch → **{BP}** web search for all files → document findings → next batch (auto-stop on errors)
- 32. For each file, verify compliance criteria:
  - Function-by-function modularity (single responsibility, clear interfaces, independent testability)
  - Testing requirements (tests exist in Scripts/Tests/, dependency injection, mocking, coverage ≥90%)
  - Code quality standards (error handling, readability, security practices, maintainability)
  - Best practices adherence (SOLID principles, design patterns, separation of concerns, industry standards)
- 33. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research directly to report file
- 34. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format (see Reviewer_Rules.md subagent usage section)
- 35. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single file without exception
- 36. **VALIDATION**: Validate that **{BP}** web search was performed for every single file without exception
- 37. **VALIDATION**: Validate that findings were documented to report file after each file/batch scan
- 38. **VALIDATION**: Validate that files were processed in alphabetical order
- 39. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Reviewer/Reference/Execution_Mode_Patterns.md)
- 40. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 41. **PRINT** "Compliance scanning complete - [N] files **SCAN**ned line by line with **{BP}** best practice research for each file in alphabetical order - findings documented incrementally"

### Phase 5. Findings Consolidation (Incremental Report Processing)
- 42. Collect all scanning results from incremental report file (Logs/Reviewer/BP/App/incremental-scan-report.md)
- 43. Consolidate findings by category and severity with detailed file-specific analysis:
  - **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies, mixed concerns) per file
  - **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity) per file
  - **MEDIUM**: Best practices improvements (code readability, maintainability) per file
  - **LOW**: Minor suggestions (comments, formatting) per file
- 44. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file in incremental report - no file may be left unexamined or unreported
- 45. Cross-validate findings to eliminate duplicates and ensure consistency across all files
- 46. **VALIDATION**: Validate that findings consolidation completed successfully for every single file
- 47. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 48. **PRINT** "Findings consolidated from incremental report - [N] issues categorized by severity across [N] files - every file examined"

### Phase 6. Compliance Report Generation
- 49. Generate comprehensive compliance report with detailed findings for every single file:
  - Executive summary (overall compliance score, critical findings count, files examined)
  - Detailed findings by file with line numbers and specific violations for each file
  - Severity ratings with context for why each issue matters per file
  - Actionable recommendations with clear improvement paths per file
  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file
- 50. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single file - no file may be omitted from the report
- 51. Save report to Logs/Reviewer/BP/App/best-practice-scan-[YYYY-MM-DD_HH-MM-SS].md
- 52. **VALIDATION**: Validate that report generation completed successfully and every file is included
- 53. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 54. **PRINT** "Compliance report generated - saved to Logs/Reviewer/BP/App/ - includes detailed analysis for every single file"

### Phase 7. Final Validation + User Review
- 55. Verify report completeness and accuracy
- 56. Ensure all findings are properly documented with specific references
- 57. Check that recommendations are actionable and clear
- 58. **VALIDATION**: Validate that final validation completed successfully
- 59. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 60. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 61. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 8. Planner-Ready Document Generation
- 62. Generate planner-ready implementation document structured for Planner agent consumption from consolidated findings:
  - Implementation requirements organized by priority and dependency
  - Specific code changes needed with file paths and line references
  - Test requirements and coverage gaps to address
  - Modularity improvements with refactoring guidance
  - Best practices implementations with specific recommendations
- 63. Structure document for Planner workflow compatibility:
  - Clear implementation phases with logical sequencing
  - Dependency mappings between changes
  - Risk assessment for each implementation block
  - Resource requirements and complexity estimates
- 64. Save planner-ready document to Plans/Reviewer/reviewer-implementation-plan-[timestamp].md
- 65. **VALIDATION**: Validate that planner-ready document is complete and actionable
- 66. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 67. **PRINT** "Planner-ready document generated - saved to Plans/Reviewer/ - ready for Planner agent consumption"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 68. **PRINT** "Best Practice Scanner workflow execution complete - workflow terminated"
- 69. **PRINT** "Compliance report available in Logs/Reviewer/BP/App/ for review and action"
- 70. **PRINT** "Planner-ready document available in Plans/Reviewer/ for implementation planning"
- 71. **TERMINATE**: End workflow execution (do not return to step 1)

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Reviewer Customization**: Reviewer-specific quality criteria for compliance verification
- **Focus**: Compliance quality assessment with Executor rule verification

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
For App/ directory scanning (>150 files), use parallel subagents by module:

**Memory Components Subagent Prompt:**
```
**SCAN** the following memory component files in App/sovereignai/memory/ directory line by line without skipping anything:
- episodic_backend.py, persistent_graph.py, procedural_backend.py, trace_backend.py, working_backend.py, graph_backend.py, gateway.py, episodic_consumer.py

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for memory component patterns (MANDATORY for every file)
3. Verify compliance with Executor rules:
   - Function-by-function modularity (single responsibility, clear inputs/outputs)
   - Testing requirements (tests exist in Scripts/Tests/, dependency injection, mocking)
   - Code quality (error handling, readability, security practices)
   - Best practices (SOLID principles, separation of concerns)
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

Output format for each file:
- File path
- Function count and complexity assessment
- Testing compliance status (PASS/FAIL with details)
- Modularity violations found (with line numbers)
- Best practices issues found (with line numbers)
- Specific changes needed with line references
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW)
- Specific actionable recommendations
- Best practices research findings with sources
```

**Agent System Components Subagent Prompt:**
```
**SCAN** the following agent system files in App/sovereignai/agent/ directory line by line without skipping anything:
- react.py, factory.py, history.py, prompts.py, structured_output.py, tool_session.py, types.py, config.py, protocols.py

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for agent system patterns (MANDATORY for every file)
3. Verify compliance with Executor rules
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as memory components]
```

**Messaging/Event System Subagent Prompt:**
```
**SCAN** the following messaging/event files in App/sovereignai/shared/ and App/sovereignai/messaging/ directories line by line without skipping anything:
- event_bus.py, trace_emitter.py, event_registry.py, bus.py, security.py, adapter.py, schema.py

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for messaging/event patterns (MANDATORY for every file)
3. Verify compliance with Executor rules
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as memory components]
```

**Other Modules Subagent Prompt:**
```
**SCAN** the remaining files in App/sovereignai/ (model_registry/, orchestrator/, librarian/, lifecycle/, managers/, options/, etc.) line by line without skipping anything.

For each file:
1. **SCAN** line by line without skipping anything
2. **{BP}** web search for current best practices for specific module types (MANDATORY for every file)
3. Verify compliance with Executor rules
4. Document specific changes needed based on **SCAN** results and **{BP}** best practice research

[Same output format as memory components]
```

### Subagent Coordination
- Launch 4-5 parallel subagents for independent module categories
- Each subagent receives precise scope with specific file list
- Define exact output format for consistent consolidation
- Validate subagent results against Executor rules
- Consolidate findings into comprehensive report

## Scan Complexity Assessment

Based on App/ directory scan:
- **Total Python Files**: [Determined at runtime via file discovery]
- **Scanning Order**: Alphabetical by full path from first folder to last folder (chronological scanning order)
- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per file
- **Process**: **SCAN** file (alphabetical order) → **{BP}** web search → **IMMEDIATELY DOCUMENT** to incremental report (Logs/Reviewer/BP/App/incremental-scan-report.md) → Next file (repeat for all files)
- **Context Management**: PostCompaction hook reloads governance files when context is compressed, maintaining scanning capability throughout process

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive scan to review each **{BP}** web search result and file analysis as it completes for maximum oversight
- **Manual Batched Mode**: Balanced approach for efficiency with oversight - processes 5-10 files at a time with confirmation between batches
- **Automatic Batched Mode**: Maximum efficiency for large codebases - processes 5-10 files at a time automatically without confirmation

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for current best practices) → **IMMEDIATELY DOCUMENT** to incremental report (Logs/Reviewer/BP/App/incremental-scan-report.md) → Next file. This incremental process prioritizes thoroughness over speed while maintaining robustness through PostCompaction hook context management. The 200k context budget allows for substantial scanning before context compression occurs.

## Context Management Strategy

### PostCompaction Hook Configuration
- **Global Hook**: PostCompaction hook configured in user-level Devin CLI config (~/.config/devin/hooks.v1.json)
- **Purpose**: Reload governance files when context is compressed to maintain compliance verification capability
- **Files Reloaded**: 
  - Agents/Reviewer/AGENTS.md (Reviewer agent configuration)
  - Rules/Reviewer/Reviewer_Rules.md (Review criteria and compliance requirements)
  - Workflow/Reviewer/Reviewer_Best_Practice_Scanner_Workflow.md (Current workflow)
  - Workflow/Workflow_Reference/Terminology_Glossary.md (Terminology definitions)
- **Trigger**: Automatically fires when Devin CLI compresses context during long scanning sessions
- **Benefit**: Ensures scanning workflow remains robust even with very large codebases and extended context usage