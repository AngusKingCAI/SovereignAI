# {Title}

**File**: {FileName}.md  
**Workflow Name**: {WorkflowName}  
**Description**: {Description}  
**Status**: {Agent} Agent Standard  
**Template Compliance**: Verified

{Brief one-line description}

## Purpose

{What this workflow accomplishes and why it exists}

## Scope

### Included
{What is included in this workflow}

### Excluded
{What is explicitly not covered by this workflow}

## Gate Enforcement

**EVERY STEP HAS A GATE REQUIREMENT**: Each workflow step includes a mandatory gate that must pass before proceeding to the next step.

**GATING RULES**:
- Gate verification must be explicit and actionable
- Gates must have clear PASS/FAIL criteria
- Gate failures must stop progression until resolved
- Gate results must be documented in conversation log
- Gates should validate completion, quality, and compliance of the step

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
- Template compliance requires gate enforcement rules to be defined

## Workflow Steps

### 1. {Step Name}
-{action bullets}

**Gate 1 Verification**: Post "✅ Gate 1 PASS: {gate description}"

### 2. {Step Name}
-{action bullets}

**Gate 2 Verification**: Post "✅ Gate 2 PASS: {gate description}"

## Workflow Logging

**Script-Based Logging:**
-Call Scripts/Governance/log_conversation.py at workflow or cycle completion
-Script automatically generates structured JSON log entry with full conversation details
-For workflows with cycles/repeats, call script at the end of each cycle iteration
-Each cycle gets its own session_id and log file

**Script Usage:**
```bash
python Scripts/Governance/log_conversation.py {agent_name} {session_id} "{summary}" "{task}" "{workflow}" {phase}
```

**Script Output Location:**
-Logs/{AgentName}/Conversations/{session-id}.json
-Script automatically includes conversation, steps, gates, actions, context in structured JSON format

## Workflow Closure
To properly close the {Agent} workflow session, invoke the global `close` skill.
This will:
-Finalize the conversation log with session end time
-Record session summary and accomplishments
-Clear workflow state
-Return to normal chat mode

**Closure can be triggered by:**
-User request: "close workflow", "/close"
-Task completion
-Error or interruption

## Quality Metrics

### Quality (10 points)
-Determinism (3): Predictable, reproducible behavior
-Observability (3): Audit trails, logging, state visibility  
-Testability (2): Isolated testing, clear interfaces
-Architectural soundness (2): Single responsibility, minimal coupling

### Token Cost (10 points)
-Context efficiency (3): Targeted information retrieval
-Model selection (3): Appropriate model choices
-Caching strategy (2): Repeated query optimization
-Reasoning overhead (2): Efficient prompt design

### Efficiency (10 points)
-Parallelization (4): Independent task identification
-Latency optimization (3): Critical path analysis
-Resource utilization (3): Computational overhead, data structure efficiency

## Conversation Logging
Maintain conversation logs in `Logs/{AgentName}/Conversations/` for each session with:
-Session ID and trace ID
-Timestamp for each step
-{Agent-specific context} being executed
-Gate verification results
-Actions taken and results
-Metadata for tracking