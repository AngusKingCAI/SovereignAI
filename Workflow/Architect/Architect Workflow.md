# Architect Workflow

Step-by-step process for architectural decisions with best practice validation and enforced gates.

## Workflow Steps

### 1. Understand
- Read FOUNDING_ARCHITECTURE.md for constitutional requirements
- Read Rules/Architect/IDE_Architecture_Rules.md for IDE architecture standards
- Identify current phase and dependencies
- Clarify the architectural question or decision needed
- Verify directory structure compliance with IDE rules

### 2. Research
- Use web search to find industry best practices
- Cross-reference with Devin Local documentation for implementation feasibility
- Gather multiple approaches and patterns
- Ensure proposed solutions comply with IDE architecture rules

### 3. Options
- Generate 2-4 implementation options based on research
- Evaluate each option across Quality, Token Cost, Efficiency metrics
- Use ask_user_question to present options with ratings

### 4. Decide
- User selects the preferred option
- Architect agent validates constitutional compliance of selection
- Proceed with selected approach

### 5. Specify
- Create detailed specification for selected approach
- Define interfaces, data structures, error handling
- Specify testing and documentation requirements
- Ensure specification follows IDE architecture file naming conventions
- Verify proposed file locations comply with directory structure rules

### 6. Implement
- Implement according to specification
- Follow IDE architecture rules for file placement
- Maintain conversation logging during implementation
- Follow gate system integration requirements

### 7. Test
- Run unit tests
- Run integration tests
- Verify all tests pass
- Log test results using conversation logger

### 8. Verify
- Verify implementation matches specification
- Run verification tests
- Log verification results
- Ensure constitutional compliance

### 9. Document
- Update agent documentation
- Create usage examples
- Log documentation completion

### 10. Complete
- **MANDATORY**: Log complete conversation session with summary
- **MANDATORY**: Verify conversation log file created in Logs/Architect/Conversations/
- **MANDATORY**: Record phase completion using gate system
- **MANDATORY**: Verify gate system recorded completion successfully

## Manual Compliance System

The workflow is enforced through manual compliance with gate verification scripts. The Architect agent must:

1. **Manually follow workflow steps** in the prescribed order
2. **Manually run gate scripts** at appropriate points
3. **Manually verify conversation logging** before completion
4. **Manually record phase completion** using gate system

### Manual Gate Verification

**Before Phase Progression**:
- Run `Scripts/Architect/Gates/verify-phase-complete.sh <previous_phase_number>`
- Verify hash-based phase completion
- Do not proceed if verification fails

**After Phase Completion**:
- Run `Scripts/Architect/Gates/record-phase-complete.sh <phase_number> architect-approved`
- Record completion hash and signature
- Verify conversation logging before recording

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