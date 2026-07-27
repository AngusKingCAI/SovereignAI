# Reviewer Best Practice Scanner Workflow

**ID**: WF-REV-001  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Variable (highly detailed task-dependent)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)

## Purpose
Comprehensive line-by-line scan of every single file in the App/ directory to verify compliance with Executor rules for modularity, testing, and best practices. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against best practices without exception.

## Roles and Owners
- **Reviewer Agent**: Executes scanning workflow, coordinates subagents for large-scale scanning, consolidates findings
- **User**: Requests scanning, approves findings and recommendations
- **Governance System**: Validation against Executor rules and quality standards

## Trigger and End State
- **Trigger**: User requests best practice compliance scan of App/ directory
- **End State**: Comprehensive compliance report with findings, severity ratings, and actionable recommendations

## Workflow Steps (23 steps)

### Phase 0. Read Reviewer Rules + Governance
- 1. Read Rules/Reviewer/Reviewer_Rules.md to understand review criteria and modular compliance requirements
- 2. Read Workflow/Workflow_Reference/Terminology_Glossary.md to understand terminology definitions
- 3. Read Rules/Executor/Executor_Rules.md to understand modularity and testing requirements to verify
- 4. Parse YAML frontmatter and rule definitions for compliance verification guidance
- 5. Store rule context and compliance criteria for reference throughout workflow execution
- 6. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 7. **PRINT** "Reviewer rules and Executor compliance criteria loaded"

### Phase 1. Select Execution Mode
- 7. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Require user confirmation at every single step for maximum oversight (recommended for first comprehensive scan)
  - **Auto**: Don't continue on failures (auto-stop on errors, proceed automatically through successes)
  - **Complete**: Continue past failures (ignore all errors for maximum coverage)
- 8. Store selected execution mode for failure handling throughout workflow
- 9. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern step-by-step progression"

### Phase 2. Scan Scope Definition
- 10. Define scan scope: App/ directory (every single Python file - no exceptions)
- 11. Determine scanning strategy based on file count and complexity:
  - Small scale (<50 files): Direct scanning by Reviewer agent
  - Medium scale (50-150 files): Chunked scanning with subagents
  - Large scale (>150 files): Parallel subagent scanning by module
- 12. **CRITICAL REQUIREMENT**: Every single file must be checked against best practices - no file may be skipped or excluded
- 13. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
- 14. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 15. **PRINT** "Scan scope defined - App/ directory comprehensive compliance verification - every file will be examined"

### Phase 3. File Discovery + Categorization
- 15. Discover every single Python file in App/ directory using find command - verify no files are missed
- 16. Categorize each file by module and complexity with detailed analysis:
  - Memory components (episodic_backend.py, persistent_graph.py, etc.)
  - Agent system components (react.py, factory.py, etc.)
  - Messaging/event system (event_bus.py, trace_emitter.py, etc.)
  - Model registry components (sync.py, database.py, etc.)
  - Orchestrator components (facade.py, dispatcher.py, etc.)
  - Skills/adapters integration (various adapter and skill files)
- 17. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope
- 18. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception
- 19. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 20. **PRINT** "File discovery complete - [N] Python files categorized by module - every file will be examined against best practices"

### Phase 4. Compliance Scanning Execution
- 20. **IF direct scanning**: Reviewer agent performs line-by-line scan of each file individually against best practices
- 21. **IF chunked scanning**: Reviewer agent launches subagents for each category chunk, ensuring every file is examined
- 22. **IF parallel scanning**: Reviewer agent launches parallel subagents for independent modules, covering every single file
- 23. **CRITICAL REQUIREMENT**: For each file, verify compliance against Executor rules and best practices - no file may be skipped
- 24. For each file, perform detailed examination:
  - Function-by-function modularity (single responsibility, clear interfaces, independent testability)
  - Testing requirements (tests exist in Scripts/Tests/, dependency injection, mocking, coverage ≥90%)
  - Code quality standards (error handling, readability, security practices, maintainability)
  - Best practices adherence (SOLID principles, design patterns, separation of concerns, industry standards)
- 25. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format (see Reviewer_Rules.md subagent usage section)
- 26. **VALIDATION**: Validate that scanning completed successfully for every single file without exception
- 27. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
- 28. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 29. **PRINT** "Compliance scanning complete - [N] files individually examined against Executor rules and best practices"

### Phase 5. Findings Consolidation
- 29. Collect all scanning results from direct review or subagents for every single file examined
- 30. Consolidate findings by category and severity with detailed file-specific analysis:
  - **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies, mixed concerns) per file
  - **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity) per file
  - **MEDIUM**: Best practices improvements (code readability, maintainability) per file
  - **LOW**: Minor suggestions (comments, formatting) per file
- 31. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file - no file may be left unexamined or unreported
- 32. Cross-validate findings to eliminate duplicates and ensure consistency across all files
- 33. **VALIDATION**: Validate that findings consolidation completed successfully for every single file
- 34. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 35. **PRINT** "Findings consolidated - [N] issues categorized by severity across [N] files - every file examined"

### Phase 6. Compliance Report Generation
- 35. Generate comprehensive compliance report with detailed findings for every single file:
  - Executive summary (overall compliance score, critical findings count, files examined)
  - Detailed findings by file with line numbers and specific violations for each file
  - Severity ratings with context for why each issue matters per file
  - Actionable recommendations with clear improvement paths per file
  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file
- 36. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single file - no file may be omitted from the report
- 37. Save report to Logs/Reviewer/best-practice-scan-[timestamp].md
- 38. **VALIDATION**: Validate that report generation completed successfully and every file is included
- 39. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 40. **PRINT** "Compliance report generated - saved to Logs/Reviewer/ - includes detailed analysis for every single file"

### Phase 7. Final Validation + User Review
- 40. Verify report completeness and accuracy
- 41. Ensure all findings are properly documented with specific references
- 42. Check that recommendations are actionable and clear
- 43. **VALIDATION**: Validate that final validation completed successfully
- 44. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 45. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 46. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 8. Session Logging + Validate
- 47. Consolidate all scanning iterations into session log to Logs/Reviewer/
- 48. Generate session attestation hash for verification from all session logs
- 49. **VALIDATION**: Validate that session logging completed successfully and audit trail is complete
- 50. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 51. **PRINT** "Session logging complete - audit trail validated, Reviewer workflow complete"

### Phase 10. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 52. **PRINT** "Best Practice Scanner workflow execution complete - workflow terminated"
- 53. **PRINT** "Compliance report available in Logs/Reviewer/ for review and action"
- 54. **TERMINATE**: End workflow execution (do not return to step 1)

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
SCAN the following memory component files in App/sovereignai/memory/ directory line by line:
- episodic_backend.py, persistent_graph.py, procedural_backend.py, trace_backend.py, working_backend.py, graph_backend.py, gateway.py, episodic_consumer.py

For each file, verify compliance with Executor rules:
1. Function-by-function modularity (single responsibility, clear inputs/outputs)
2. Testing requirements (tests exist in Scripts/Tests/, dependency injection, mocking)
3. Code quality (error handling, readability, security practices)
4. Best practices (SOLID principles, separation of concerns)

Output format for each file:
- File path
- Function count and complexity assessment
- Testing compliance status (PASS/FAIL with details)
- Modularity violations found (with line numbers)
- Best practices issues found (with line numbers)
- Severity rating (CRITICAL/HIGH/MEDIUM/LOW)
- Specific actionable recommendations
```

**Agent System Components Subagent Prompt:**
```
SCAN the following agent system files in App/sovereignai/agent/ directory line by line:
- react.py, factory.py, history.py, prompts.py, structured_output.py, tool_session.py, types.py, config.py, protocols.py

[Same compliance verification and output format as memory components]
```

**Messaging/Event System Subagent Prompt:**
```
SCAN the following messaging/event files in App/sovereignai/shared/ and App/sovereignai/messaging/ directories line by line:
- event_bus.py, trace_emitter.py, event_registry.py, bus.py, security.py, adapter.py, schema.py

[Same compliance verification and output format as memory components]
```

**Other Modules Subagent Prompt:**
```
SCAN the remaining files in App/sovereignai/ (model_registry/, orchestrator/, librarian/, lifecycle/, managers/, options/, etc.) line by line.

[Same compliance verification and output format as memory components]
```

### Subagent Coordination
- Launch 4-5 parallel subagents for independent module categories
- Each subagent receives precise scope with specific file list
- Define exact output format for consistent consolidation
- Validate subagent results against Executor rules
- Consolidate findings into comprehensive report

## Scan Complexity Assessment

Based on previous App/ directory scan:
- **Total Python Files**: 74 files
- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module category
- **Estimated Duration**: Variable based on findings and complexity
- **Coverage**: Line-by-line comprehensive examination per SCAN definition

## Execution Mode Recommendations

- **Manual Mode**: Recommended for first comprehensive scan to review each step as it completes for maximum oversight
- **Auto Mode**: Suitable for subsequent scans when process is established and automatic progression is desired
- **Complete Mode**: Only use when maximum coverage is desired regardless of issues found