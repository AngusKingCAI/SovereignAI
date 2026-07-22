# External AI Review Prompt: Planner Workflow Completeness & Functionality

## Review Objective
Evaluate the SovereignAI Planner workflow to determine if it is **100% complete and working** as intended. You will analyze the workflow design, implementation, and execution readiness from a technical and operational perspective.

## Setup Instructions
1. **Clone the repository**: 
   ```bash
   git clone git@github.com:AngusKingCAI/SovereignAI.git
   cd SovereignAI
   ```
2. **Navigate to workflow directory**:
   ```bash
   cd .Planner/workflows
   ```

## Review Scope

### 1. Workflow Design Analysis
**File to examine**: `.Planner/workflows/PLAN_WORKFLOW.md`

**Evaluation Criteria**:
- [ ] Workflow rule index is complete (W1-W4 properly defined)
- [ ] Workflow overview clearly shows the complete process flow
- [ ] All phases (0-7) are properly defined with clear triggers and goals
- [ ] Each phase has detailed steps with exit gates
- [ ] Hard gates are properly defined and mapped to phases
- [ ] Soft gates are properly defined for Round Table evaluation
- [ ] Gate enforcement mechanisms are clearly specified
- [ ] Compliance posting requirements are defined for each gate
- [ ] Universal rules compliance is clearly specified
- [ ] Stop conditions are properly defined
- [ ] Evolution conditions are documented

### 2. Implementation Analysis
**Directories to examine**:
- `.Planner/scripts/hard_gates/` (validation scripts)
- `.Planner/scripts/soft_gates/` (soft gate scripts)
- `.Planner/roundtable/` (Round Table infrastructure)
- `.Planner/rules/` (Planner rules)
- `Agents/reviewer/workflows/` (Reviewer workflows)

**Evaluation Criteria**:
- [ ] All hard gate scripts (HG-1 through HG-13) are implemented
- [ ] All soft gate scripts (SG-1 through SG-3) are implemented
- [ ] Round Table templates are complete (panelist profiles, rubrics, briefs, prompts)
- [ ] Database schema is properly defined (SQLITE_SCHEMA.md)
- [ ] Database manager is implemented (database_manager.py)
- [ ] JSON exporter is implemented (json_exporter.py)
- [ ] Reviewer workflows are properly defined (pattern analysis, rule integration)
- [ ] All scripts follow the enforcement mechanisms defined in AGENTS.md

### 3. Consistency Analysis
**Files to examine**:
- `AGENTS.md` (architect session governance)
- `.Planner/workflows/PLAN_WORKFLOW.md` (workflow design)
- `.Planner/rules/PLANNER_RULES.md` (planner rules)
- `Agents/reviewer/workflows/*.md` (reviewer workflows)

**Evaluation Criteria**:
- [ ] Rule references are consistent across all files (W1-W4, not A1-A4)
- [ ] Gate numbering is consistent (PLAN-0 through PLAN-7)
- [ ] Hard gate references match actual script implementations
- [ ] Soft gate references match actual script implementations
- [ ] Agent responsibilities are properly separated (Planner vs Reviewer)
- [ ] Handoff boundaries are clearly defined
- [ ] Gate A10 (git push confirmation) is properly enforced
- [ ] No conflicting rules or gate definitions

### 4. Functionality Simulation
**Task**: Simulate a complete plan creation and Round Table review workflow

**Scenario**: User requests "Create a plan to implement user authentication"

**Steps to simulate**:
1. Walk through Phase 1-5 (plan creation phases)
2. Verify hard gates would pass at each phase
3. Walk through Phase 6 (Round Table review)
4. Verify soft gates would function correctly
5. Verify hard gates would pass in Phase 6.4
6. Walk through Phase 7 (handoff to Reviewer)
7. Verify all compliance gates would be posted correctly

**Evaluation Criteria**:
- [ ] Each phase can be executed without missing steps
- [ ] Hard gates would properly block execution if conditions not met
- [ ] Soft gates would provide non-blocking recommendations
- [ ] Compliance gates would be posted at each step
- [ ] Workflow can complete end-to-end without gaps
- [ ] Database operations would function correctly
- [ ] JSON export would work properly
- [ ] Git operations would respect Gate A10

### 5. Best Practices Compliance
**Evaluation Criteria**:
- [ ] Workflow follows best practices for panelist evaluation (independent scoring, evidence-first debriefing)
- [ ] Round Table evaluation uses BP-based quality gates
- [ ] Web search integration is properly specified
- [ ] Template structures are comprehensive and usable
- [ ] Database schema supports all required operations
- [ ] JSON export format is properly structured
- [ ] Git operations follow safety protocols (Gate A10)
- [ ] Error handling and recovery are defined

### 6. Missing Components Check
**Evaluation Criteria**:
- [ ] No missing phase definitions
- [ ] No missing gate definitions
- [ ] No missing script implementations
- [ ] No missing template files
- [ ] No missing database components
- [ ] No missing integration points
- [ ] No undefined references or broken links
- [ ] No incomplete rule definitions

## Review Report Format

### Executive Summary
- **Overall Assessment**: [COMPLETE/INCOMPLETE/NEEDS REVISION]
- **Critical Issues**: [Number of critical issues found]
- **Recommendation**: [APPROVE/REJECT/REQUEST CHANGES]

### Detailed Findings

#### 1. Workflow Design Status
- [ ] PASS/FAIL: Workflow rule index completeness
- [ ] PASS/FAIL: Phase definitions completeness
- [ ] PASS/FAIL: Gate definitions completeness
- [ ] PASS/FAIL: Enforcement mechanisms clarity
- **Issues Found**: [List any issues]

#### 2. Implementation Status
- [ ] PASS/FAIL: Hard gate scripts implementation
- [ ] PASS/FAIL: Soft gate scripts implementation
- [ ] PASS/FAIL: Round Table infrastructure
- [ ] PASS/FAIL: Database components
- [ ] PASS/FAIL: Reviewer workflows
- **Issues Found**: [List any issues]

#### 3. Consistency Status
- [ ] PASS/FAIL: Rule reference consistency
- [ ] PASS/FAIL: Gate numbering consistency
- [ ] PASS/FAIL: Agent responsibility separation
- [ ] PASS/FAIL: Handoff boundary clarity
- **Issues Found**: [List any issues]

#### 4. Functionality Status
- [ ] PASS/FAIL: End-to-end workflow simulation
- [ ] PASS/FAIL: Hard gate blocking behavior
- [ ] PASS/FAIL: Soft gate recommendation behavior
- [ ] PASS/FAIL: Database operations
- [ ] PASS/FAIL: JSON export functionality
- **Issues Found**: [List any issues]

#### 5. Best Practices Status
- [ ] PASS/FAIL: BP-based evaluation implementation
- [ ] PASS/FAIL: Web search integration
- [ ] PASS/FAIL: Template usability
- [ ] PASS/FAIL: Git safety protocols
- **Issues Found**: [List any issues]

#### 6. Missing Components Status
- [ ] PASS/FAIL: No missing phases
- [ ] PASS/FAIL: No missing gates
- [ ] PASS/FAIL: No missing scripts
- [ ] PASS/FAIL: No missing templates
- **Issues Found**: [List any issues]

### Critical Issues (Blockers)
List any issues that would prevent the workflow from functioning correctly:
1. [Issue description]
2. [Issue description]
...

### Recommendations
List specific recommendations for improvement:
1. [Recommendation]
2. [Recommendation]
...

### Final Determination
**Is the workflow 100% complete and working?**: [YES/NO]

If NO, specify what needs to be fixed to achieve 100% completion.

## Submission Instructions
1. Complete the review using the criteria above
2. Provide detailed findings for each section
3. Clearly state whether the workflow is 100% complete and working
4. If not 100%, specify exactly what needs to be fixed
5. Submit your review report as a markdown file

## Reviewer Qualifications
This review requires:
- Experience with workflow design and implementation
- Understanding of hard/soft gate mechanisms
- Knowledge of Python scripting for validation
- Familiarity with database operations (SQLite)
- Understanding of git operations and safety protocols
- Ability to simulate complex multi-phase workflows

## Expected Review Duration
- **Setup**: 15 minutes (clone and examine structure)
- **Design Analysis**: 30 minutes
- **Implementation Analysis**: 45 minutes
- **Consistency Analysis**: 30 minutes
- **Functionality Simulation**: 45 minutes
- **Best Practices Review**: 30 minutes
- **Missing Components Check**: 15 minutes
- **Report Generation**: 30 minutes
- **Total**: ~4 hours

## Contact for Questions
If clarification is needed on any aspect of the workflow or review criteria, contact the SovereignAI development team.