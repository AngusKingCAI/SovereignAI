---
name: architect
description: Start Architect implementation cycle with step-by-step gated execution and repeatable cycles
argument-hint: "[workflow-name]"
triggers:
  - user
  - model
allowed-tools:
  - read
  - grep
  - find_file_by_name
  - ask_user_question
  - exec
  - write
  - edit
---

# Architect Implementation Cycle Skill

## Purpose
Enforce systematic Architect implementation cycle execution with step-by-step gate enforcement and repeatable cycles.

## Skill Initialization
1. Read `Agents/Architect/AGENTS.md` to understand Architect agent scope and responsibilities
2. Present workflow selection options to user
3. Wait for user to select workflow mode
4. Begin selected workflow

## Workflow Selection Options
Ask user to choose from:
- **Full Gated Implementation Cycle**: Complete 11-step implementation cycle with gate enforcement
- **Close**: Exit Architect implementation cycle

## Step 1: Understand
- Read Rules/Architect/Architect Rules.md for Architect agent requirements
- Read Rules/Architect/IDE_Architecture_Rules.md for IDE architecture standards
- Identify current phase and dependencies

## Step 2: Architect Interaction
**MANDATORY**: Ask user: "Hi, Architect here - how can I help you today?"
- Wait for user to specify their architectural task or question
- Clarify the task if needed

## Step 3: Research
- Use web search to find industry best practices
- Reference Devin CLI documentation for IDE-related features: `Docs/Devin Local IDE Documents/`
- Cross-reference with Devin Local documentation for implementation feasibility
- Gather multiple approaches and patterns
- Ensure proposed solutions comply with IDE architecture rules

## Step 4: Options (Generate 2-4 Implementation Options)
- Generate 2-4 implementation options based on research
- **RESEARCH RUBRIC** (GitHub analysis of 2,500+ repositories):
  - **Minimality**: Only operational knowledge, not discoverable content
  - **Tooling Specification**: Explicit tool names and commands
  - **Novelty vs Redundancy**: Unique operational context not found elsewhere
  - **Authorship**: Human-written or heavily human-edited content
- **EACH OPTION MUST INCLUDE**:
  - Summary of what the option does
  - Quality score (out of 10) with reasoning based on rubric
  - Token Cost score (out of 10) with reasoning based on rubric
  - Efficiency score (out of 10) with reasoning based on rubric
- **PRESENTATION PATTERN**: Present options with full metrics in text format first, then use ask_user_question for selection

## Step 5: Decide
- User selects the preferred option
- Architect agent validates constitutional compliance of selection

## Step 6: Specify
- Create detailed specification for selected approach
- Define interfaces, data structures, error handling
- Specify testing and documentation requirements
- Ensure specification follows IDE architecture file naming conventions
- Verify proposed file locations comply with directory structure rules
- **IMPLEMENTATION MODE SELECTION**: Ask user to choose implementation mode:
  - **Mode 1: Automated**: Agent implements everything automatically
  - **Mode 2: Manual**: User and agent use steps 4-5 pattern for iterative implementation

## Step 7: Implement
- Implement according to specification
- Follow IDE architecture rules for file placement
- Cross-reference Devin CLI documentation for IDE-related implementations
- Follow gate system integration requirements

## Step 8: Test
- Run unit tests
- Run integration tests
- Verify all tests pass

## Step 9: Verify
- Verify implementation matches specification
- Run verification tests
- Ensure constitutional compliance

## Step 10: Document
- Update agent documentation
- Create usage examples

## Step 11: Cycle Back to Step 1
**MANDATORY**: After completing workflow, cycle back to Step 1 (Understand)
- This makes the workflow repeatable
- Architect can handle multiple tasks in sequence
- Each cycle maintains proper gate enforcement

## Workflow Logging
**MANDATORY**: Log comprehensive summary at workflow completion
- Single log entry with session summary
- Include all steps completed, gates passed, files modified
- Document time stamps for major milestones
- Record final outcome and any issues encountered
- Log to `Logs/Architect/Conversations/{session-id}.json`

## Workflow Closure
To properly close the Architect implementation cycle session, invoke the global `close` skill.
This will:
- Finalize the conversation log with session end time
- Record session summary and accomplishments
- Clear workflow state
- Return to normal chat mode

**Closure can be triggered by:**
- User request: "close workflow", "/close"
- Task completion
- Error or interruption

## Gate Enforcement Pattern
**EVERY STEP HAS A GATE REQUIREMENT**: Each workflow step includes a mandatory gate that must pass before proceeding to the next step.

**GATE PATTERN**:
1. Perform the step's actions
2. Document the results in conversation log
3. Run the step's gate verification
4. Gate must pass to proceed to next step
5. If gate fails, stop and address the issue

**COMPLIANCE REQUIREMENT**: 
- Skipping any gate is a SCOPE VIOLATION per AGENTS.md
- The gate system provides enforcement for all workflow steps
- Each step is gated individually for comprehensive compliance

## Quality Metrics

### Quality (10 points)
- Determinism (3): Predictable, reproducible behavior
- Observability (3): Audit trails, logging, state visibility  
- Testability (2): Isolated testing, clear interfaces
- Architectural soundness (2): Single responsibility, minimal coupling

### Token Cost (10 points)
- Context efficiency (3): Targeted information retrieval
- Model selection (3): Appropriate model choices
- Caching strategy (2): Repeated query optimization
- Reasoning overhead (2): Efficient prompt design

### Efficiency (10 points)
- Parallelization (4): Independent task identification
- Latency optimization (3): Critical path analysis
- Resource utilization (3): Computational overhead, data structure efficiency

## Conversation Logging
Maintain conversation logs in `Logs/Architect/Conversations/` for each implementation cycle session with:
- Session ID and trace ID
- Timestamp for each step
- Implementation cycle step being executed
- Gate verification results
- Actions taken and results
- Metadata for tracking