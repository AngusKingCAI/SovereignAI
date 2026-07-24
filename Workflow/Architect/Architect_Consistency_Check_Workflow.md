# Architect Consistency Check Workflow

**File**: Architect_Consistency_Check_Workflow.md  
**Workflow Name**: Architect Consistency Check Workflow  
**Description**: Systematic consistency checking across SovereignAI infrastructure with validation and compliance enforcement  
**Status**: Architect Agent Standard  
**Authority**: Enforced by Architect agent and gate system  
**Created**: 2026-07-24  
**Constitutional Compliance**: Verified

## Purpose

Systematic workflow for consistency checking across the SovereignAI infrastructure, ensuring architectural compliance and structural integrity according to IDE architecture rules and constitutional requirements.

## Workflow Overview

### Objectives
- Validate directory structure compliance against IDE architecture rules
- Verify file naming conventions across all project artifacts
- Ensure agent documentation completeness and validity
- Check rules and workflow folder structure compliance
- Validate Scripts/ and Logs/ directory organization
- Provide comprehensive violation reporting and remediation guidance

### Target Artifacts
- Directory structure: Agents/, Rules/, Workflow/, Scripts/, Logs/, Docs/
- Agent folders and AGENTS.md documentation
- Rules folders and rule files
- Workflow folders and workflow files
- Source code organization in Scripts/src/
- Configuration files in Scripts/config/
- Test suites in Scripts/tests/
- Log files in Logs/{AgentName}/ structure

### Integration with Existing Architect Implementation Cycle
- Can be invoked as standalone consistency check
- Integrates with main Architect Implementation Cycle as verification step
- Supports gate system integration for phase progression validation
- Feeds results into Logs/Architect/Conversations/ for tracking

### Trigger Conditions
- Manual invocation by Architect agent
- Automatic execution before phase progression
- Post-implementation verification after structural changes
- On-demand consistency validation

## Workflow Steps

### Step 1: Initialize Consistency Check
- Load IDE architecture rules from `Rules/Architect/IDE_Architecture_Rules.md`
- Load Architect-specific rules from `Rules/Architect/Architect_Rules.md`
- Initialize validation context and scan scope
- Set up logging destination: `Logs/Architect/Conversations/`
- Create session ID for traceability

**Gate 1 Verification**: Post "✅ Gate 1 PASS: Consistency check initialized, rules loaded"

### Step 2: Load Validation Rules
- Parse directory structure rules from IDE architecture rules
- Extract naming conventions for directories and files
- Load mandatory directory requirements (Agents/, Rules/, Workflow/, Scripts/, Logs/, Docs/)
- Load agent-specific structure requirements
- Parse compliance thresholds and violation categories

**Gate 2 Verification**: Post "✅ Gate 2 PASS: Validation rules loaded, thresholds defined"

### Step 3: Scan Target Artifacts
- Scan directory structure against mandatory requirements
- Catalog all files with their locations and naming patterns
- Identify agent folders and verify AGENTS.md presence
- Identify rule folders and verify rule file presence
- Identify workflow folders and verify workflow file presence
- Scan Scripts/ directory structure (src/, config/, tests/)
- Scan Logs/ directory structure (agent-specific folders)

**Gate 3 Verification**: Post "✅ Gate 3 PASS: Target artifacts scanned, inventory complete"

### Step 4: Apply Validation Rules
- Validate directory structure compliance against mandatory requirements
- Check file naming conventions across all artifacts
- Verify agent folder structure (AGENTS.md exists and is valid)
- Verify rules folder structure (rule files exist and are valid)
- Verify workflow folder structure (workflow files exist and are valid)
- Verify Scripts/ directory structure compliance
- Verify Logs/ directory structure compliance
- Apply content pattern validation where applicable

**Gate 4 Verification**: Post "✅ Gate 4 PASS: Validation rules applied, violations classified"

### Step 5: Generate Violations Report
- Compile all violations by category (critical, warning, informational)
- Generate violation paths with specific rule references
- Create compliance summary statistics
- Format report for human review and machine processing
- Store report in `Logs/Architect/Conversations/{session-id}.json`

**Gate 5 Verification**: Post "✅ Gate 5 PASS: Violations report generated, documented"

### Step 6: Gate Verification
- Apply compliance thresholds (e.g., zero critical violations allowed)
- Compare violation counts against acceptable thresholds
- Determine overall compliance status (pass/fail)
- Generate gate pass/fail determination
- Document gate decision with reasoning

**Gate 6 Verification**: Post "✅ Gate 6 PASS: Compliance threshold verification completed"

### Step 7: Remedy Planning (Conditional)
*Executed only if violations found and gate check fails*

- For each violation, identify required remediation steps
- Classify violations by complexity and urgency
- Generate remediation plan with prioritized actions
- Estimate remediation effort and timeline
- Map violations to specific IDE architecture rule references

**Gate 7 Verification**: Post "✅ Gate 7 PASS: Remedy plan generated, violations addressed"

### Step 8: Re-verification Loop (Conditional)
*Executed only after remediation implementation*

- Allow user to implement remediation steps
- Re-run consistency check after remediation
- Verify previous violations are resolved
- Check for new violations introduced by changes
- Update compliance status and statistics

**Gate 8 Verification**: Post "✅ Gate 8 PASS: Re-verification completed, compliance improved"

### Step 9: Final Compliance Certification
- Generate final compliance certification
- Document compliance status with timestamp
- Create compliance log entry in `Logs/Architect/Conversations/`
- Provide summary of checks performed and results
- Update project compliance state

**Gate 9 Verification**: Post "✅ Gate 9 PASS: Final compliance certification completed"

## Quality Metrics

### Quality (10 points)

**Determinism (3 points)**
- Predictable validation results across multiple runs
- Reproducible violation detection with identical inputs
- Consistent rule application regardless of execution context
- *Validation*: Run consistency check twice on same state, verify identical results

**Observability (3 points)**
- Complete audit trail of all validation steps performed
- Detailed logging of rule applications and violations found
- Clear visibility into scan scope and coverage
- State visibility through intermediate results and reports
- *Validation*: Verify log completeness and report granularity

**Testability (2 points)**
- Isolated testing of individual validation rules
- Clear interfaces for rule definition and application
- Ability to test with mock directory structures
- *Validation*: Create test scenarios with known violations, verify detection

**Architectural Soundness (2 points)**
- Single responsibility: consistency checking only
- Minimal coupling with other Architect workflows
- Clear separation between validation logic and remediation
- *Validation*: Review workflow for scope boundaries and dependencies

### Token Cost (10 points)

**Context Efficiency (3 points)**
- Targeted information retrieval from rule files
- Efficient directory scanning without unnecessary file reads
- Optimized rule application logic
- *Validation*: Measure context usage for typical consistency checks

**Model Selection (3 points)**
- Appropriate model choices for different validation tasks
- Smaller models for simple pattern matching
- Larger models only for complex reasoning tasks
- *Validation*: Profile model usage across workflow steps

**Caching Strategy (2 points)**
- Rule parsing results cached between runs
- Directory structure caching for incremental checks
- *Validation*: Test caching effectiveness with repeated runs

**Reasoning Overhead (2 points)**
- Efficient prompt design for validation tasks
- Minimal reasoning required for rule application
- Clear decision criteria without ambiguity
- *Validation*: Analyze prompt complexity and decision paths

### Efficiency (10 points)

**Parallelization (4 points)**
- Independent rule applications can run in parallel
- Directory scanning can be parallelized across branches
- Violation classification can run concurrently
- *Validation*: Identify parallelization opportunities and implement

**Latency Optimization (3 points)**
- Critical path analysis for workflow steps
- Early termination on critical violations
- Incremental checking for focused validation
- *Validation*: Measure end-to-end latency and optimize critical path

**Resource Utilization (3 points)**
- Computational overhead minimized
- Efficient data structures for rule storage
- Memory management for large directory scans
- *Validation*: Profile resource usage during validation

## Validation Categories

### Directory Structure Compliance
- Mandatory directories exist (Agents/, Rules/, Workflow/, Scripts/, Logs/, Docs/)
- Agent-specific folders in correct locations
- Proper nesting and hierarchy
- No unauthorized directories at root level

### File Naming Convention Validation
- Agent files: `AGENTS.md` (always uppercase)
- Rule files: `{Agent}_Rules.md` (e.g., `Architect_Rules.md`)
- Workflow files: `{Agent}_Workflow.md` (e.g., `Architect_Workflow.md`)
- Log files: `{component}-{YYYY-MM-DD}.jsonl`
- State files: `phase-{N}-state.json`
- Directory naming: PascalCase

### Content Pattern Verification
- AGENTS.md contains required sections (purpose, philosophy, scope)
- Rule files follow proper structure and constraints
- Workflow files contain step-by-step procedures
- Markdown formatting consistency
- Required metadata present

### Cross-Reference Integrity
- References between files are valid
- No orphaned file references
- Consistent agent naming across all artifacts
- Proper linkage between rules and workflows

### Documentation Completeness
- All agents have AGENTS.md documentation
- All agents have corresponding rules and workflows
- Change logs and amendment records where applicable
- Compliance checklists completed

## Error Handling

### Violation Classification

**Critical Violations**
- Missing mandatory directories
- Missing AGENTS.md files for agents
- Critical structural violations that break architecture
- Zero tolerance - must block progression

**Warning Violations**
- Naming convention deviations
- Minor structural inconsistencies
- Documentation completeness issues
- Should be addressed but may not block progression

**Informational Violations**
- Style inconsistencies
- Optional metadata missing
- Suggestions for improvement
- For awareness and tracking

### Remedy Pathways

**Critical Violations**
- Immediate remediation required
- Architect agent approval needed for workaround
- Must be resolved before phase progression
- Escalation to project lead if persistent

**Warning Violations**
- Remediation planned within current iteration
- Can be tracked as technical debt
- May require timeline adjustment
- Documented in project backlog

**Informational Violations**
- Address during natural maintenance windows
- Incorporated into best practices updates
- No immediate action required
- Monitored for trends

### Escalation Procedures
- Critical violations: Immediate escalation to Architect agent
- Persistent warnings: Escalation after 3 iterations
- Pattern violations: Root cause analysis initiation
- Documentation gaps: Technical writer assignment

### Exception Handling
- Document exceptions with justification
- Architect approval required for exceptions
- Migration plan for resolving exceptions
- Exception expiration deadlines

## Integration Points

### Connection to Existing Architect Implementation Cycle
- Can be invoked as Step 9 (Verify) in main Architect Implementation Cycle
- Results feed into gate system for phase progression
- Supports both manual and automatic invocation modes
- Integrates with conversation logging system

### Gate System Integration
- Each workflow step has corresponding gate verification
- Gate results determine progression through workflow
- Critical violations trigger automatic gate failure
- Gate results logged for audit trail

### Logging and Conversation Tracking
- Session-based logging in `Logs/Architect/Conversations/`
- JSON format for machine-readable results
- Human-readable reports for review
- Timestamp tracking for all operations

### Reporting to Logs/Architect/
- Violation reports stored in Conversations/ subdirectory
- Gate verification logs in Gates/ subdirectory
- Component-specific logs in respective subdirectories
- Compliance certification in project root

## Implementation Mode Selection

*This section is a placeholder for future implementation planning*

### Mode 1: Automated (Future)
- Agent implements everything automatically
- Scripts handle validation logic
- Fully automated consistency checking
- Integration with CI/CD pipeline

### Mode 2: Manual (Current)
- User and agent use workflow steps iteratively
- Manual validation against documented procedures
- Human-in-the-loop for violation review
- Guided remediation process

### Tool Requirements (Future)
- File system scanning tools
- Pattern matching and validation logic
- Report generation capabilities
- Gate system integration

### Dependencies (Future)
- Rule file parsing libraries
- Directory traversal utilities
- JSON report generation
- Logging infrastructure

## Constitutional Compliance

This workflow enforces constitutional requirements:

- **Deterministic**: Predictable validation with consistent results
- **Observable**: Complete audit trail and violation reporting
- **Minimal Coupling**: Clear scope boundaries and integration points
- **Architecture First**: Structural validation before implementation
- **Explicit Interfaces**: Clear workflow steps and gate requirements

## Amendment Log

| Date | Amendment | Rationale |
|------|-----------|-----------|
| 2026-07-24 | Initial consistency check workflow | Establish systematic validation workflow for Architect agent based on IDE architecture rules |

**Current Constitutional Status**: COMPLIANT

This consistency check workflow ensures the Architect agent maintains deterministic, observable, and structured project organization for the SovereignAI Harness infrastructure through systematic validation and enforcement of IDE architecture rules.