---
id: wf-plan-ref-batch-specs
status: active
owner: planner-agent
updated: 2026-07-29
purpose: Planner-specific plan batch execution patterns and scan plan categorization
---

# Planner Plan Batch Specifications

**Purpose**: Planner-specific plan batch execution patterns and scan plan categorization.

## Plan Batch Structure

### Batch Execution Pattern
Plans are organized in batches of 5 plans per batch for systematic processing and issue resolution. For parallel Round Table review processing, batches are limited to 4 plans to optimize subagent efficiency and resource utilization.

### Plan Numbering Pattern
- **Standard Plans**: Plans 1-4, 6-9, 11-14, 16-19, 21-24, 26-29, 31-34, 36-39 (regular planning tasks)
- **Scan Plans**: Plans 5, 10, 15, 20, 25, 30, 35, 40 (every 5th plan is a scan plan)

### Scan Plan Purpose
Scan plans (5, 10, 15, 20, 25, 30, 35, 40) are specifically designed to:
- Identify and fix issues discovered in previous plans
- Perform systematic system scans for problems
- Address accumulated issues from previous batch execution
- Provide quality control and system health checks

## Batch Processing Workflow

### Batch Structure
```
Batch 1: Plans 1, 2, 3, 4, 5 (Plan 5 = Scan Plan)
Batch 2: Plans 6, 7, 8, 9, 10 (Plan 10 = Scan Plan)
Batch 3: Plans 11, 12, 13, 14, 15 (Plan 15 = Scan Plan)
Batch 4: Plans 16, 17, 18, 19, 20 (Plan 20 = Scan Plan)
Batch 5: Plans 21, 22, 23, 24, 25 (Plan 25 = Scan Plan)
Batch 6: Plans 26, 27, 28, 29, 30 (Plan 30 = Scan Plan)
Batch 7: Plans 31, 32, 33, 34, 35 (Plan 35 = Scan Plan)
Batch 8: Plans 36, 37, 38, 39, 40 (Plan 40 = Scan Plan)
```

### Standard Plan Characteristics
- **Purpose**: Implement specific features or changes
- **Content**: Regular planning tasks following standard template
- **Execution**: Direct implementation by executor
- **Validation**: Standard validation and delivery process

### Scan Plan Characteristics
- **Purpose**: Fix issues from previous plans, system health checks
- **Content**: Issue identification, problem resolution, system scans
- **Execution**: Issue-fixing and system maintenance
- **Validation**: Enhanced validation focusing on issue resolution

## Workflow Integration

### Planner Workflow Modification
The Planner workflow should:
1. **Batch Mode**: Process plans sequentially through batch (return to Phase 0 after each plan for next plan in sequence)
2. **Single Plan Mode**: Process single plan and terminate (no return to Phase 0)
3. **Follow batch sequence**: Process plans in numerical order when in batch mode
4. **Identify scan plans**: Recognize plan numbers 5, 10, 15, 20, 25, 30, 35, 40
5. **Apply scan plan logic**: Use different approach for scan plans
6. **Track batch progress**: Monitor batch completion status
7. **Use consolidated batch approach**: When processing multiple plans, use Batch_Brief.md and Batch_Prompt.md for review materials
8. **Use single plan approach**: When processing single plan, use plan-specific brief and prompt files
9. **Reuse batch review materials**: External Round Table reuses batch brief and prompt from Internal Round Table for efficiency

### Scan Plan Detection Logic
```python
def is_scan_plan(plan_number):
    return plan_number % 5 == 0

def get_plan_type(plan_number):
    if is_scan_plan(plan_number):
        return "scan_plan"
    else:
        return "standard_plan"
```

### Execution Pattern
1. **Standard Plan**: Follow normal workflow → Save to Plans/ → Execute
2. **Scan Plan**: Enhanced workflow → Scan for issues → Fix problems → Save to Plans/ → Execute
3. **Batch Completion**: After each 5th plan, batch is complete
4. **Next Batch**: Continue with next batch sequence

## Plan Storage and Organization

### Directory Structure
```
Plans/
├── plan-1.md
├── plan-2.md
├── plan-3.md
├── plan-4.md
├── plan-5.md (scan plan)
├── plan-6.md
├── plan-7.md
├── plan-8.md
├── plan-9.md
├── plan-10.md (scan plan)
└── ...

Plans/Queued/
├── plan-1.rev1.md
├── plan-2.rev1.md
├── plan-3.rev1.md
├── plan-4.rev1.md
├── Batch_Brief.md (consolidated brief for batch review)
├── Batch_Prompt.md (consolidated prompt for batch review)
└── ...
```

---

## Batch Review File Structure

### Consolidated Batch Approach

**Overview**: When processing plans in batches (multiple plans simultaneously), a consolidated file structure is used for Round Table review materials to optimize efficiency and maintain consistency.

**File Structure**:
- **Batch Brief**: Single `Plans/Queued/Batch_Brief.md` file contains overview, dependencies, and review focus for all plans in batch
- **Batch Prompt**: Single `Plans/Queued/Batch_Prompt.md` file contains consolidated review instructions for all panelist personas
- **Individual Plan Files**: Each plan still has its own `Plans/Queued/plan-{N}.{rev}.md` file
- **Sub Agent Distribution**: Each sub agent receives their specific plan file + shared batch brief + shared batch prompt

**Templates**:
- **Batch Brief Template**: `Workflow/Planner/Templates/Batch_Brief_Template.md`
- **Batch Prompt Template**: `Workflow/Planner/Templates/Batch_Prompt_Template.md`

**Single Plan Approach**:
- **Plan Brief**: `Plans/Queued/plan-{N}.{rev}_Brief.md` (individual plan brief)
- **Plan Prompt**: `Plans/Queued/plan-{N}.{rev}_Prompt.md` (individual plan prompt)
- **Templates**: Use existing `Plan_Brief_Template.md` and `Plan_Prompt_Template.md`

**Batch Review Logging**:
- **Internal Reviews**: `Logs/Planner/Round Table/Internal/Batch{N}_Roundtable.md` (consolidated logging for entire batch)
- **External Reviews**: `Logs/Planner/Round Table/External/Batch{N}_Roundtable.md` (consolidated logging for entire batch)

**Single Plan Review Logging**:
- **Internal Reviews**: `Logs/Planner/Round Table/Internal/Plan{N}_Roundtable.md` (individual plan logging)
- **External Reviews**: `Logs/Planner/Round Table/External/Plan{N}_Roundtable.md` (individual plan logging)

**File Reuse**:
- Batch brief and prompt created in Phase 6 (Internal Round Table) are reused in Phase 8 (External Round Table) for Plan Mode
- No need to recreate batch review materials for external review when processing batches
- This ensures consistency between internal and external review processes

---

## Plan Metadata

Each plan should include:
- **Plan Number**: Sequential number in batch sequence
- **Plan Type**: Standard or Scan
- **Batch Number**: Which batch this plan belongs to
- **Previous Issues**: Issues found in previous plans (for scan plans)
- **Issue Resolution**: How scan plan addresses issues

## Usage Guidelines

### When Creating Standard Plans
1. Follow standard planning workflow
2. Use standard plan template
3. Focus on feature implementation
4. Save with sequential numbering
5. Mark as standard plan type

### When Creating Scan Plans
1. Review previous plans in batch for issues
2. Perform system scan for problems
3. Create issue-fixing plan
4. Use enhanced validation for issue resolution
5. Mark as scan plan type
6. Document issue resolution approach

### Batch Management
1. Track which plans have been completed
2. Monitor batch progress
3. Ensure scan plans address relevant issues
4. Validate batch completion before proceeding
5. Maintain plan sequence integrity
