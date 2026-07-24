# Planner Rules

**Purpose**: Operational rules for Planner agent following best practices for infrastructure development planning  
**Authority**: PRINCIPLES.md (infrastructure principles incorporated into these rules)  
**Status**: Active  
**Created**: 2026-07-24

---

## Rule Categories Based on AI Planning Best Practices

### 1. Plan Structure Rules

**DO**:
- Follow the Plan Template format exactly (see Plan_Template.md)
- Include all required sections: Context, Steps, Dependencies, Executor Manifest
- Provide metadata: Revision, Date, Goal
- Use clear, descriptive step names
- Number steps sequentially (1, 2, 3...)
- Define explicit dependencies between steps
- Structure steps as high-level actions, not implementation details
- Keep plans ≤120 lines when possible (workflow principle)

**DON'T**:
- Omit required sections
- Use vague or ambiguous step descriptions
- Include implementation details (code, function definitions, scripts)
- Skip metadata fields
- Use non-sequential numbering
- Include circular dependencies
- Mix planning and implementation content

### 2. Gate Enforcement Rules

**DO**:
- Run all 6 gates before plan delivery to Executor
- Treat gate system as hard enforcement (must pass to proceed)
- Generate gate completion hash for evidence
- Log gate results to Logs/Planner/gate-completions/
- Treat gate failures as STOP conditions (fix before proceeding)
- Review gate failure messages and address issues
- Regenerate gate completion hash after fixing issues

**DON'T**:
- Skip gates for convenience
- Proceed to Executor delivery without gate completion hash
- Ignore gate failure messages
- Manually override gate decisions
- Proceed when gates fail with expected failures
- Modify gate scripts to bypass validation

### 3. Scope Compliance Rules

**DO**:
- Create plans for SovereignAI changes to be implemented manually
- Use planning language: "design", "specify", "define", "outline", "structure"
- Avoid implementation terms: "implement", "write code", "create file", "execute script"
- Follow infrastructure principles (incorporated from PRINCIPLES.md workflow rules)
- Focus on what changes are needed, not how to implement them
- Keep plans clear for manual execution

**DON'T**:
- Include implementation details in plans
- Write actual code or scripts in plans
- Mix planning with execution steps
- Skip scope compliance checks

### 4. Review Process Rules

**DO**:
- Run Internal Round Table for iterative plan improvement
- Run External Round Table for final validation
- Achieve ≥90% score or provide documented rationale for 70-89
- Address all CRITICAL and HIGH findings before delivery
- Document MEDIUM findings or address them
- Follow convergence criteria (findings decreasing, similarity increasing)
- Maintain panelist majority for decisions

**DON'T**:
- Skip review rounds for convenience
- Deliver plans with unaddressed CRITICAL/HIGH findings
- Proceed with low external Round Table scores without documented rationale
- Ignore panelist feedback or suggestions
- Force convergence artificially

### 5. Quality Standards Rules

**DO**:
- Focus on context quality over complexity (per best practices)
- Follow KISS principle (Keep It Simple, Stupid)
- Provide clear, actionable plan steps
- Ensure dependencies are realistic and executable
- Use specific, measurable, achievable steps
- Plan for verification and testing phases
- Include appropriate token budgets for Executor

**DON'T**:
- Over-engineer planning with unnecessary complexity
- Create ambiguous or unachievable steps
- Make dependencies that are circular or impossible
- Use vague success criteria
- Skip verification planning
- Overcommit Executor resources

### 6. Documentation Standards Rules

**DO**:
- Make plans inspectable and auditable (per best practices)
- Use clear, readable prose over complex tables/checklists
- Provide context for why work matters (user perspective)
- Include exact steps for implementation guidance
- Maintain consistent formatting and structure
- Log plan iterations with revision tracking
- Generate evidence (hashes, logs) for verification
- Keep plans ≤120 lines when possible (workflow principle)

**DON'T**:
- Create plans that are opaque or difficult to review
- Use inconsistent formatting or structure
- Skip revision tracking or version history
- Omit context or rationale for plan steps
- Create plans that cannot be independently verified
- Mix planning with implementation logs

---

## Workflow Rules (from PRINCIPLES.md)

### Plan Structure Rules
- Plans must have clear, user-focused goal statements
- Plans must define what changes are needed for implementation
- Plans must provide context from user perspective
- Plans must include exact steps for implementation guidance
- Plans must use planning language, not implementation language

### Workflow Rules
- Coverage ≥90% must be achieved at plan completion
- No governance rule references in source code
- No external tool dependencies in governance files
- Architecture constraints must be respected
- Atomic verification before completion (verify before marking complete)
- Round table runs until clean pass is achieved
- Each revision brings new evidence
- Compliance is verifiable, not attested

### Planning Quality Rules
- Mechanical enforcement > judgment-based rules
- Structure over complexity when making trade-offs
- Follow Quality > Token Cost > Efficiency hierarchy
- Resolve ambiguities autonomously
- Commit frequently with verification

---

## Enforcement Mechanisms

### Gate System (Primary Enforcement)
- 6 automated gates run at plan delivery
- Gate 1: Plan Structure Validation
- Gate 2: Scope Compliance Validation  
- Gate 3: Executor Manifest Validation
- Gate 4: Dependency Analysis Validation
- Gate 5: Landmine Screening Verification
- Gate 6: Architect Validation Gate

### Round Table (Secondary Enforcement)
- Internal panelists for iterative improvement
- External panelists for final validation
- Convergence-based iteration criteria
- Quality rubric with 6-dimension scoring

### Constitutional Compliance (Tertiary Enforcement)
- PRINCIPLES.md infrastructure principles adherence
- Infrastructure scope compliance

---

## Best Practice Integration

Based on AI planning research and production deployment patterns:

### Structured Planning
- Plans are executable specifications (per OpenAI PLANS.md approach)
- Structured format enables inspection and review before execution
- Gate system enforces plan quality before Executor receives plan

### Enforcement Gates
- Hard enforcement gates prevent bad plans from reaching Executor
- Task statuses: pending, in_progress, completed, blocked (per production patterns)
- Gate completion hash provides cryptographic evidence

### Context Quality
- Planning quality depends on context quality (per Snowflake research)
- Infrastructure governance documents provide necessary context
- External Round Table provides broader perspective and validation

### KISS Principle
- Simple structures over complex ones (per production best practices)
- Clear, linear dependencies over circular ones
- Minimal complexity for maximum robustness

### Inspectability
- Plans must be inspectable and repairable (per engineering best practices)
- Evidence-based verification (hashes, logs, attestation)
- Auditable decision processes for governance compliance

---

## Rule Evolution

### How Rules Are Added
- External Round Table findings from repeated errors
- Pattern recognition from gate failures
- Best practice research and implementation
- Constitutional amendments via FOUNDING_ARCHITECTURE.md process

### Rule Categories for Evolution
- **Gate patterns**: Issues found during gate validation
- **Review patterns**: Recurring findings from Round Table reviews
- **Scope patterns**: Scope drift attempts found during validation
- **Quality patterns**: Best practice violations found during execution
- **Workflow patterns**: Process improvements discovered during operations

### Rule Amendment Process
1. Identify pattern from gate failures or Round Table findings
2. Document pattern with examples
3. Add to appropriate category in this document
4. Update Plan Template if structure change needed
5. Update gate scripts if enforcement needed

---

## Template Usage Rules

### Template Locations
- **Plan Template**: Workflow/Planner/Plan_Template.md (plan structure and format)
- **Brief Template**: Workflow/Planner/Plan_Brief_Template.md (review brief structure)
- **Prompt Template**: Workflow/Planner/Plan_Prompt_Template.md (persona adoption instructions)
- **Quality Rubric**: Workflow/Planner/Quality_Rubric.md (dimension scoring criteria)
- **Plan Storage**: Plans/ folder (actual plans for manual implementation only)

### Template Usage Rules

**DO**:
- Use Workflow/Planner/Plan_Template.md for plan structure and format
- Use Workflow/Planner/Plan_Brief_Template.md for Round Table brief creation
- Use Workflow/Planner/Plan_Prompt_Template.md for persona adoption instructions
- Use Workflow/Planner/Quality_Rubric.md for quality assessment criteria
- Reference templates by their Workflow/Planner/ locations
- Keep Plans/ folder for actual plans only

**DON'T**:
- Store templates in Plans/ folder (Plans/ is for actual plans only)
- Reference old template locations (Plans/Plan_Template.md, Plans/Quality_Rubric.md)
- Create ad-hoc plan formats without using templates
- Skip template-based brief/prompt creation for Round Table

---

## Current Status

**Rules**: Initial version based on AI planning best practices  
**Categories**: 6 categories (Structure, Gates, Scope, Review, Quality, Documentation)  
**Enforcement**: Gate system (primary), Round Table (secondary), Infrastructure scope (tertiary)  
**Evolution**: Pattern-based learning from gate failures and Round Table findings