# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules, enforced through the hook-based gate system for automatic permission validation and audit logging.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via hooks (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps (72 steps)
### Phase 0. Read Architect Rules
- 1. Read Rules/Architect/Architect_Rules.md to load current governance constraints
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. Print "Architect rules loaded from Rules/Architect/Architect_Rules.md"

### Phase 1. Architect Interaction
- 5. Ask user: "Hi, Architect here - how can I help you today?"
- 6. Wait for user to specify their architectural task or question
- 7. Clarify the task if needed
- 8. Review user request and check local research using index files before web search
- 9. Apply loaded architect rules to task requirements
- 10. Print "Initiating architect interaction - awaiting user task specification"

### Phase 2. Research Best Practices
- 11. Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) for existing information
- 12. Web search only if local information unavailable
- 13. Gather multiple approaches and patterns
- 14. Ensure proposed solutions comply with governance rules
- 15. Print "Researching best practices - checking local documentation indexes first"
- 16. Print "Web search initiated - local information insufficient for research needs"
- 17. Print "Research complete - gathered multiple implementation approaches"

### Phase 3. Generate Options
- 18. Generate 2-4 implementation options based on research
- **VIABLE OPTION CRITERIA**:
  - Different mechanism of action (distinct approaches, not cosmetic variation)
  - Feasible execution (aligned with time, budget, capabilities)
  - Evaluability (assessable against defined criteria)
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Impact score (out of 10) with reasoning
  - Effort score (out of 10) with reasoning
  - Risk score (out of 10) with reasoning
- 19. **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- 20. **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use ask_user_question for selection
- 21. **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md
- 22. Print "Generating implementation options - applying viable option criteria"
- 23. Print "Options generated - presenting with impact, effort, and risk metrics"
- 24. Print "Architect opinion provided - recommending optimal approach based on analysis"

### Phase 4. Specify Implementation
- 25. Create detailed specification for selected approach
- **CONTEXT**: One paragraph stating why this implementation exists and what problem it solves
- **ARCHITECTURE**: Define interfaces, data structures, error handling, file placement
- **CONSTRAINTS**: Security, compliance, and architectural boundaries from Rules/Architect/Architect_Rules.md
- **DEFINITION OF DONE**: Observable success criteria (testable outcomes)
- 26. Ensure specification follows IDE architecture file naming conventions
- 27. Verify proposed file locations comply with directory structure rules
- 28. **IMPLEMENTATION MODE SELECTION**: Ask user to choose:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use iterative pattern for implementation
- 29. Print "Creating detailed implementation specification - defining architecture and constraints"
- 30. Print "Specification complete - verifying file placement compliance with directory structure"
- 31. Print "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### Phase 5. Implement (One Function at a Time)
- 32. Build exactly one function at a time, test immediately
- 33. Present function and test result to user after each successful test
- 34. Wait for explicit user confirmation before proceeding
- 35. Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The gate system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (ungated) to pause for approval without triggering failure intervention.
- 36. When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- 37. Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- 38. When function fails, check local research using index files, then web search only if local info unavailable
- **FAILURE HANDLING NOTE**: If function implementation fails (tool error), the automated system detects failure and blocks further state-mutating tools until user resolves with /retry, /modify, or /abort command.
- 39. Print "Implementing function - building one function at a time per architect rules"
- 40. Print "Function test complete - presenting test results to user for confirmation"
- 41. Print "Awaiting user confirmation - treating function as locked once confirmed"
- 42. Print "Function implementation complete - proceeding to next function"

### Phase 6. Verify Compliance
- 43. Verify implementation matches specification
- 44. Run verification tests
- 45. Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- 46. Never skip compliance checks
- 47. Always verify architectural compliance before proceeding
- 48. Print "Verifying compliance - checking implementation against specification"
- 49. Print "Running verification tests - ensuring all success criteria met"
- 50. Print "Constitutional compliance verified - implementation aligns with architect rules"
- 51. Print "Architectural compliance complete - ready to proceed"

### Phase 7. Document
- 52. Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
  - AGENTS.md (if agent capabilities change)
- 53. Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- 54. Never place files uncategorized
- 55. Print "Updating governance documentation - modifying relevant agent files"
- 56. Print "Documentation categorization verified - all files properly categorized per architect rules"
- 57. Print "Documentation complete - governance files updated"

### Phase 8. Final Validation
- 58. Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- 59. Confirm governance file placement compliance per INDEX.md
- 60. Validate no unintended changes outside the target area
- 61. Print "Final validation initiated - verifying implementation scope compliance"
- 62. Print "Rules verification complete - template and formatting validated"
- 63. Print "Workflow verification complete - structure and executability confirmed"
- 64. Print "Scripts verification complete - functionality validated"
- 65. Print "Documentation verification complete - categorization confirmed"
- 66. Print "Governance file placement verified - compliance with INDEX.md confirmed"
- 67. Print "Unintended changes check complete - no changes outside target area detected"

### Phase 9. Return to Phase 0
- 68. After completing workflow, return to Phase 0 (Read Architect Rules)
- 69. This makes the workflow repeatable for continuous architectural work
- 70. Ready for next architectural task
- 71. Print "Workflow cycle complete - returning to Phase 0 for next architectural task"
- 72. Print "Architect agent ready - awaiting next user request"
