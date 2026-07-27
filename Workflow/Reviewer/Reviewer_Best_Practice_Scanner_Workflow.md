# Reviewer Best Practice Scanner Workflow

**ID**: WF-REV-001  
**Owner**: Reviewer Agent  
**Frequency**: On-demand  
**Duration**: Extended (comprehensive per-file analysis with mandatory **{BP}** web search for each file)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility Workflow)

## Purpose
Comprehensive line-by-line scan of every single file in the App/ directory to verify compliance with Executor rules for modularity, testing, and best practices. This is an extremely detailed task requiring thorough examination of each file individually against established quality standards. Every file must be checked against current best practices without exception, with mandatory **{BP}** web search for each file to ensure compliance with the latest industry standards. This process is designed to be comprehensive and token-intensive, prioritizing thoroughness over speed.

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
  - **Manual**: Require user confirmation at every single step for maximum oversight (recommended for first comprehensive scan)
  - **Auto**: Don't continue on failures (auto-stop on errors, proceed automatically through successes)
  - **Complete**: Continue past failures (ignore all errors for maximum coverage)
- 9. Store selected execution mode for failure handling throughout workflow
- 10. **PRINT** "Execution mode selected - [Manual/Auto/Complete] will govern step-by-step progression"

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

### Phase 3. File Discovery + Categorization
- 17. Discover every single Python file in App/ directory using find command - verify no files are missed
- 18. Categorize each file by module and complexity with detailed analysis:
  - Memory components (episodic_backend.py, persistent_graph.py, etc.)
  - Agent system components (react.py, factory.py, etc.)
  - Messaging/event system (event_bus.py, trace_emitter.py, etc.)
  - Model registry components (sync.py, database.py, etc.)
  - Orchestrator components (facade.py, dispatcher.py, etc.)
  - Skills/adapters integration (various adapter and skill files)
- 19. **CRITICAL REQUIREMENT**: Verify that all files are accounted for and no files are excluded from scanning scope
- 20. **VALIDATION**: Validate that file discovery completed successfully and every single file is categorized without exception
- 21. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 22. **PRINT** "File discovery complete - [N] Python files categorized by module - every file will be examined against best practices"

### Phase 4. Compliance Scanning Execution
- 23. **IF direct scanning**: Reviewer agent performs **SCAN** of each file individually - line-by-line examination without skipping anything
- 24. **IF chunked scanning**: Reviewer agent launches subagents for each category chunk, ensuring every file is **SCAN**ned
- 25. **IF parallel scanning**: Reviewer agent launches parallel subagents for independent modules, covering every single file with **SCAN**
- 26. **CRITICAL REQUIREMENT**: For each file, **SCAN** line by line for compliance against Executor rules and best practices - no file may be skipped
- 27. **CRITICAL REQUIREMENT**: For each file, perform **{BP}** web search for current best practices - this is mandatory for every file
- 28. For each file, perform detailed examination:
  - **SCAN** each file line by line without skipping anything
  - **{BP}** web search for current best practices specific to file type and functionality (MANDATORY for every file)
  - Function-by-function modularity (single responsibility, clear interfaces, independent testability)
  - Testing requirements (tests exist in Scripts/Tests/, dependency injection, mocking, coverage ≥90%)
  - Code quality standards (error handling, readability, security practices, maintainability)
  - Best practices adherence (SOLID principles, design patterns, separation of concerns, industry standards)
- 29. Document specific changes needed for each file based on **SCAN** results and **{BP}** best practice research
- 30. **SUBAGENT PROMPTING**: Provide precise prompts with exact scope, criteria, and output format (see Reviewer_Rules.md subagent usage section)
- 31. **VALIDATION**: Validate that **SCAN**ning completed successfully for every single file without exception
- 32. **VALIDATION**: Validate that **{BP}** web search was performed for every single file without exception
- 33. **EXECUTION MODE HANDLING**: Apply review mode handling patterns (see Workflow/Reviewer/Reference/Review_Mode_Patterns.md)
- 34. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 35. **PRINT** "Compliance scanning complete - [N] files **SCAN**ned line by line with **{BP}** best practice research for each file"

### Phase 5. Findings Consolidation
- 36. Collect all scanning results from direct review or subagents for every single file examined
- 37. Consolidate findings by category and severity with detailed file-specific analysis:
  - **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies, mixed concerns) per file
  - **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity) per file
  - **MEDIUM**: Best practices improvements (code readability, maintainability) per file
  - **LOW**: Minor suggestions (comments, formatting) per file
- 38. **CRITICAL REQUIREMENT**: Verify that findings exist for every single file - no file may be left unexamined or unreported
- 39. Cross-validate findings to eliminate duplicates and ensure consistency across all files
- 40. **VALIDATION**: Validate that findings consolidation completed successfully for every single file
- 41. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 42. **PRINT** "Findings consolidated - [N] issues categorized by severity across [N] files - every file examined"

### Phase 6. Compliance Report Generation
- 43. Generate comprehensive compliance report with detailed findings for every single file:
  - Executive summary (overall compliance score, critical findings count, files examined)
  - Detailed findings by file with line numbers and specific violations for each file
  - Severity ratings with context for why each issue matters per file
  - Actionable recommendations with clear improvement paths per file
  - Compliance statistics (modules compliant, functions reviewed, test coverage) per file
- 44. **CRITICAL REQUIREMENT**: Ensure report includes analysis for every single file - no file may be omitted from the report
- 45. Save report to Logs/Reviewer/best-practice-scan-[timestamp].md
- 46. **VALIDATION**: Validate that report generation completed successfully and every file is included
- 47. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 48. **PRINT** "Compliance report generated - saved to Logs/Reviewer/ - includes detailed analysis for every single file"

### Phase 7. Final Validation + User Review
- 49. Verify report completeness and accuracy
- 50. Ensure all findings are properly documented with specific references
- 51. Check that recommendations are actionable and clear
- 52. **VALIDATION**: Validate that final validation completed successfully
- 53. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
- 54. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 55. **PRINT** "Final validation complete - compliance report ready for user review"

### Phase 8. Planner-Ready Document Generation
- 56. Generate planner-ready implementation document structured for Planner agent consumption from consolidated findings:
  - Implementation requirements organized by priority and dependency
  - Specific code changes needed with file paths and line references
  - Test requirements and coverage gaps to address
  - Modularity improvements with refactoring guidance
  - Best practices implementations with specific recommendations
- 57. Structure document for Planner workflow compatibility:
  - Clear implementation phases with logical sequencing
  - Dependency mappings between changes
  - Risk assessment for each implementation block
  - Resource requirements and complexity estimates
- 58. Save planner-ready document to Plans/Reviewer/reviewer-implementation-plan-[timestamp].md
- 59. **VALIDATION**: Validate that planner-ready document is complete and actionable
- 60. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 61. **PRINT** "Planner-ready document generated - saved to Plans/Reviewer/ - ready for Planner agent consumption"

### Phase 9. Workflow Termination (SINGLE-EXECUTION WORKFLOW)
- 62. **PRINT** "Best Practice Scanner workflow execution complete - workflow terminated"
- 63. **PRINT** "Compliance report available in Logs/Reviewer/ for review and action"
- 64. **PRINT** "Planner-ready document available in Plans/Reviewer/ for implementation planning"
- 65. **TERMINATE**: End workflow execution (do not return to step 1)

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
- **Recommended Strategy**: Chunked scanning with 4-5 subagents by module category
- **Estimated Duration**: Extended (mandatory **{BP}** web search for each file)
- **Token Usage**: High (comprehensive **SCAN** + **{BP}** research per file)
- **Coverage**: Line-by-line comprehensive examination per **SCAN** definition with mandatory best practices research per file
- **Process**: **SCAN** file → **{BP}** web search → Document changes → Next file (repeat for all files)

## Execution Mode Recommendations

- **Manual Mode**: Recommended for comprehensive scan to review each **{BP}** web search result and file analysis as it completes for maximum oversight
- **Auto Mode**: Suitable for subsequent scans when process is established and automatic progression is desired
- **Complete Mode**: Only use when maximum coverage is desired regardless of issues found

**Important Note**: This workflow is designed to be comprehensive and token-intensive. Each file undergoes: **SCAN** (line-by-line examination) → **{BP}** (mandatory web search for current best practices) → Document changes. This process prioritizes thoroughness over speed and will consume significant tokens and time.