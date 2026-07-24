# Plan Template

**Purpose**: Standard format for infrastructure development plans  
**Authority**: Rules/Planner/Planner_Rules.md  
**Status**: Active Template  
**Version**: 1.0

---

## Plan Format Template

```markdown
# Plan {N} — {Brief Plan Title}

**Revision**: {N}.{rev}  
**Date**: {YYYY-MM-DD}  
**Goal**: {Clear, user-focused goal statement}

## Context
{Why this work matters from a user perspective}
{What someone can do after this change that they could not do before}
{Background context and dependencies}

## Steps
1. {High-level action 1}
2. {High-level action 2}
3. {High-level action 3}
{Additional steps as needed, numbered sequentially}

## Dependencies
step_1: []
step_2: [step_1]
step_3: [step_1, step_2]
{Clear dependency relationships, no circular dependencies}
```

---

## Section Guidelines

### Header Information
- **Revision**: Follow format {plan_number}.{revision_number} (e.g., 1.0, 1.1, 2.0)
- **Date**: ISO format YYYY-MM-DD
- **Goal**: One-sentence user-focused goal statement

### Context Section
- **Purpose-first**: Explain why this work matters from user perspective
- **Outcome-focused**: What can someone do after this change they couldn't do before
- **Context-rich**: Background information and existing dependencies
- **Format**: Plain prose, prefer sentences over lists
- **Length**: 2-4 paragraphs typically
- **Round Table Use**: Will be summarized in Plan Brief (Workflow/Planner/Plan_Brief_Template.md) for panelist review

### Steps Section
- **High-level actions**: Planning language, not implementation details
- **Sequential numbering**: 1, 2, 3... no gaps
- **Action-oriented**: Clear verbs (design, specify, define, outline, structure)
- **Scope-appropriate**: Infrastructure-focused (Phase 0-11), not application (Phase 12)
- **Quality-focused**: Each step should be achievable and verifiable
- **Length**: ≤120 lines total for entire plan when possible

### Dependencies Section
- **Format**: step_N: [list of step dependencies]
- **Sequential**: Use step_1, step_2, step_3 format
- **Clear relationships**: No circular dependencies
- **Complete**: All steps should have dependency information
- **Executable**: Dependencies should be realistic for manual execution

---

## Planning Language Examples

### ✅ Appropriate Planning Language
- "Design the workflow structure for..."
- "Specify the interface requirements for..."
- "Define the test coverage strategy for..."
- "Outline the implementation approach for..."
- "Structure the configuration for..."

### ❌ Inappropriate Implementation Language
- "Write the code for..."
- "Create file X with content Y"
- "Execute script to implement..."
- "Install package and configure..."
- "Run command to build..."

---

## Scope Boundaries

### ✅ Planner Scope (What Planner Does)
- Create plans for SovereignAI changes to be implemented manually
- Define what changes are needed
- Outline the structure and approach for implementation
- Specify dependencies and execution order
- Provide context and rationale for changes

### ❌ Planner Limitations (What Planner Doesn't Do)
- Write actual implementation code
- Execute scripts or commands
- Create files directly
- Perform implementation steps
- Mix planning with execution

---

## Quality Checks

### Before Plan Delivery
- [ ] All required sections present (Context, Steps, Dependencies)
- [ ] Metadata complete (Revision, Date, Goal)
- [ ] Steps use planning language only (no implementation details)
- [ ] Dependencies are clear and executable
- [ ] No circular dependencies
- [ ] Plan follows Planner_Rules.md format
- [ ] Plan follows Planner scope (changes for manual implementation)
- [ ] Plan ≤120 lines when possible

### Gate System Verification
- [ ] Gate 1 (Structure): All required sections and metadata present
- [ ] Gate 2 (Scope): Planning content only, no implementation details
- [ ] Gate 3 (Dependencies): Dependency graph valid, no circular dependencies
- [ ] Gate 4 (Quality): Plan quality rubric assessment (Workflow/Planner/Quality_Rubric.md)
- [ ] Gate 5 (Landmines): No blocking landmines (passes with warning if file not found)
- [ ] Gate 6 (Infrastructure): Infrastructure scope compliance verified

---

## Round Table Review Process

After plan creation and gate validation, plans undergo Round Table review for quality assessment:

### Review Process
1. **Plan Brief Creation**: Planner creates brief using Workflow/Planner/Plan_Brief_Template.md
2. **Panelist Assignment**: Domain-split personas assigned to panelists (Structure Expert, Scope Expert, etc.)
3. **Panelist Instructions**: Panelists receive persona instructions from Workflow/Planner/Plan_Prompt_Template.md
4. **Quality Evaluation**: Panelists evaluate using Workflow/Planner/Quality_Rubric.md with web search verification
5. **Findings Application**: Planner applies findings to improve plan quality
6. **Convergence Loops**: Internal and external review until convergence achieved

### Quality Dimensions
- **Accuracy**: Factual correctness and alignment with requirements
- **Completeness**: Inclusion of all necessary elements
- **Clarity**: Readability and understandability
- **Structure**: Organization and logical flow
- **Context**: Background information and rationale

### Review Output
Panelists provide structured JSON output with dimension scores, findings with severity ratings, and web search citations per Workflow/Planner/Plan_Prompt_Template.md specifications.

---

## Example Plan

```markdown
# Plan 1 — Test Planner Template Format

**Revision**: 1.0  
**Date**: 2026-07-24  
**Goal**: Test the new plan template format with valid plan structure for SovereignAI changes

## Context
This plan tests the new plan template format to ensure Planner agents can follow the standardized structure. The goal is to verify that the template produces plans that pass all gates and can be implemented manually. This template replaces the previous ad-hoc plan formats and ensures consistency across SovereignAI development planning.

## Steps
1. Define the changes needed for the SovereignAI system
2. Specify the structure and approach for implementation
3. Outline dependencies and execution order
4. Provide context and rationale for the changes
5. Verify gate system compliance before manual implementation

## Dependencies
step_1: []
step_2: [step_1]
step_3: [step_1, step_2]
step_4: [step_3]
step_5: [step_4]
```

---

## Template Evolution

This template will evolve based on:
- Gate system pattern recognition
- Round Table findings on plan quality
- Best practice research updates
- Infrastructure development phase requirements

Template changes will be documented in the revision history and coordinated with Planner_Rules.md updates.