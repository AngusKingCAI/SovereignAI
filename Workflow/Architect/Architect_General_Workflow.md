# Architect General Workflow

**ID**: WF-ARCH-001  
**Owner**: Architect Agent  
**Frequency**: Per architectural task  
**Duration**: Variable (task-dependent)  
**Priority**: High

## Purpose
Systematic architectural decision-making ensuring infrastructure design follows best practices and maintains compliance with governance rules.

## Roles and Owners
- **Architect Agent**: Executes workflow steps, enforces governance rules
- **User**: Provides task requirements, approves decisions
- **Governance System**: Automatic enforcement via hooks (non-manual)

## Trigger and End State
- **Trigger**: User requests architectural work or agent initiates task
- **End State**: Implementation complete, documented, verified for compliance

## Workflow Steps

### 1. Architect Interaction
- Ask user: "Hi, Architect here - how can I help you today?"
- Wait for user to specify their architectural task or question
- Clarify the task if needed
- Review user request and check local research using index files before web search
- Review applicable rules from `Rules/Architect/Architect_Rules.md`

### 2. Research Best Practices
- Check index files (Docs/index.md, Docs/Research/index.md, Docs/Websites/index.md, Docs/Code/index.md) for existing information
- Web search only if local information unavailable
- Gather multiple approaches and patterns
- Ensure proposed solutions comply with governance rules

### 3. Generate Options
- Generate 2-4 implementation options based on research
- **VIABLE OPTION CRITERIA**:
  - Different mechanism of action (distinct approaches, not cosmetic variation)
  - Feasible execution (aligned with time, budget, capabilities)
  - Evaluability (assessable against defined criteria)
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Impact score (out of 10) with reasoning
  - Effort score (out of 10) with reasoning
  - Risk score (out of 10) with reasoning
- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use ask_user_question for selection
- **RULE ENFORCEMENT**: Ensure options comply with Rules/Architect/Architect_Rules.md

### 4. Specify Implementation
- Create detailed specification for selected approach
- **CONTEXT**: One paragraph stating why this implementation exists and what problem it solves
- **ARCHITECTURE**: Define interfaces, data structures, error handling, file placement
- **CONSTRAINTS**: Security, compliance, and architectural boundaries from Rules/Architect/Architect_Rules.md
- **DEFINITION OF DONE**: Observable success criteria (testable outcomes)
- Ensure specification follows IDE architecture file naming conventions
- Verify proposed file locations comply with directory structure rules
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use iterative pattern for implementation

### 5. Implement (One Function at a Time)
- Build exactly one function at a time, test immediately
- Present function and test result to user after each successful test
- Wait for explicit user confirmation before proceeding
- Treat user-confirmed functions as locked
- When placing files, check INDEX.md for folder structure (token-efficient vs loading full directory)
- Load Rules/Architect/Architect_Rules.md only when specific constraints are needed
- When function fails, check local research using index files, then web search only if local info unavailable

### 6. Verify Compliance
- Verify implementation matches specification
- Run verification tests
- Ensure constitutional compliance per Rules/Architect/Architect_Rules.md
- Never skip compliance checks
- Always verify architectural compliance before proceeding

### 7. Document
- Update relevant governance files for the agent being worked on:
  - INDEX.md (if new folders are created)
  - Rules/{Agent}/{Agent}_Rules.md (if new rules are added)
  - Workflow/{Agent}/{Agent}_Workflow.md (if workflow changes)
  - AGENTS.md (if agent capabilities change)
- Always categorize files when adding to documentation directories per Rules/Architect/Architect_Rules.md
- Never place files uncategorized

### 8. Final Validation
- Verify implementation matches intended scope for the specific area:
  - Rules: Follow template and proper formatting
  - Workflow: Follow structure and is executable
  - Scripts: Function as intended
  - Documentation: Properly categorized
- Confirm governance file placement compliance per INDEX.md
- Validate no unintended changes outside the target area

### 9. Return to Step 1
- After completing workflow, return to Step 1 (Architect Interaction)
- This makes the workflow repeatable for continuous architectural work
- Ready for next architectural task
