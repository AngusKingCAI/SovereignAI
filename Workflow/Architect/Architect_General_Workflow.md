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

## Workflow Steps

### Phase 0. Read Architect Rules
- 1. Read Rules/Architect/Architect_Rules.md to load current governance constraints
- 2. Parse YAML frontmatter and rule definitions for implementation guidance
- 3. Store rule context for reference throughout workflow execution
- 4. Print "Architect rules loaded from Rules/Architect/Architect_Rules.md"

### Phase 1. Architect Interaction
- 1. Ask user: "Hi, Architect here - how can I help you today?"
- 2. Wait for user to specify their architectural task or question
- 3. Clarify the task if needed
- 4. Review user request and check local research using index files before web search
- 5. Apply loaded architect rules to task requirements
- 6. Print "Initiating architect interaction - awaiting user task specification"

### Phase 2. Research Best Practices
- 1. Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) for existing information
- 2. Web search only if local information unavailable
- 3. Gather multiple approaches and patterns
- 4. Ensure proposed solutions comply with governance rules
- 5. Print "Researching best practices - checking local documentation indexes first"
- 6. Print "Web search initiated - local information insufficient for research needs"
- 7. Print "Research complete - gathered multiple implementation approaches"

### Phase 3. Generate Options
- 1. Generate 2-4 implementation options based on research
- **VIABLE OPTION CRITERIA**:
  - Different mechanism of action (distinct approaches, not cosmetic variation)
  - Feasible execution (aligned with time, budget, capabilities)
  - Evaluability (assessable against defined criteria)
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Impact score (out of 10) with reasoning
  - Effort score (out of 10) with reasoning
  - Risk score (out of 10) with reasoning
- 2. **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- 3. **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use ask_user_question for selection
- 4. **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md
- 5. Print "Generating implementation options - applying viable option criteria"
- 6. Print "Options generated - presenting with impact, effort, and risk metrics"
- 7. Print "Architect opinion provided - recommending optimal approach based on analysis"

### Phase 4. Specify Implementation
- 1. Create detailed specification for selected approach
- **CONTEXT**: One paragraph stating why this implementation exists and what problem it solves
- **ARCHITECTURE**: Define interfaces, data structures, error handling, file placement
- **CONSTRAINTS**: Security, compliance, and architectural boundaries from Rules/Architect/Architect_Rules.md
- **DEFINITION OF DONE**: Observable success criteria (testable outcomes)
- 2. Ensure specification follows IDE architecture file naming conventions
- 3. Verify proposed file locations comply with directory structure rules
- 4. **IMPLEMENTATION MODE SELECTION**: Ask user to choose:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use iterative pattern for implementation
- 5. Print "Creating detailed implementation specification - defining architecture and constraints"
- 6. Print "Specification complete - verifying file placement compliance with directory structure"
- 7. Print "Implementation mode selection presented - awaiting user choice between automated and manual modes"

### Phase 5. Implement (One Function at a Time)
- 1. Build exactly one function at a time, test immediately
- 2. Present function and test result to user after each successful test
- 3. Wait for explicit user confirmation before proceeding
- 4. Treat user-confirmed functions as locked
- **AUTOMATED PROGRESSION NOTE**: The gate system allows state-mutating tools (edit, write, exec) automatically during this step. User confirmation requests use ask_user_question (ungated) to pause for approval without triggering failure intervention.
- 5. When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- 6. Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- 7. When function fails, check local research using index files, then web search only if local info unavailable
- **FAILURE HANDLING NOTE**: If function implementation fails (tool error), the automated system detects failure and blocks further state-mutating tools until user resolves with /retry, /modify, or /abort command.
- 8. Print "Implementing function - building one function at a time per architect rules"
- 9. Print "Function test complete - presenting test results to user for confirmation"
- 10. Print "Awaiting user confirmation - treating function as locked once confirmed"
- 11. Print "Function implementation complete - proceeding to next function"

### Phase 6. Verify Compliance
- 1. Verify implementation matches specification
- 2. Run verification tests
- 3. Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- 4. Never skip compliance checks
- 5. Always verify architectural compliance before proceeding
- 6. Print "Verifying compliance - checking implementation against specification"
- 7. Print "Running verification tests - ensuring all success criteria met"
- 8. Print "Constitutional compliance verified - implementation aligns with architect rules"
- 9. Print "Architectural compliance complete - ready to proceed"

### Phase 7. Document
- 1. Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
  - AGENTS.md (if agent capabilities change)
- 2. Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- 3. Never place files uncategorized
- 4. Print "Updating governance documentation - modifying relevant agent files"
- 5. Print "Documentation categorization verified - all files properly categorized per architect rules"
- 6. Print "Documentation complete - governance files updated"

### Phase 8. Final Validation
- 1. Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- 2. Confirm governance file placement compliance per INDEX.md
- 3. Validate no unintended changes outside the target area
- 4. Print "Final validation initiated - verifying implementation scope compliance"
- 5. Print "Rules verification complete - template and formatting validated"
- 6. Print "Workflow verification complete - structure and executability confirmed"
- 7. Print "Scripts verification complete - functionality validated"
- 8. Print "Documentation verification complete - categorization confirmed"
- 9. Print "Governance file placement verified - compliance with INDEX.md confirmed"
- 10. Print "Unintended changes check complete - no changes outside target area detected"

### Phase 9. Return to Phase 0
- 1. After completing workflow, return to Phase 0 (Read Architect Rules)
- 2. This makes the workflow repeatable for continuous architectural work
- 3. Ready for next architectural task
- 4. Print "Workflow cycle complete - returning to Phase 0 for next architectural task"
- 5. Print "Architect agent ready - awaiting next user request"
