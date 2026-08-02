---
id: wf-arch-cons-check
status: active
owner: architect-agent
updated: 2026-07-28
version: "1.1"
purpose: Workflow for Architect agent to perform comprehensive consistency checks on governance systems
expected_agent_type: architect-agent
persona:
  role: "Consistency Validation Architect"
  expertise: "Architecture consistency validation, governance compliance, structural analysis, reference integrity verification"
  process: "Systematic scanning and validation of harness architecture with comprehensive reporting"
  output: "Consistency reports with findings classified by severity and actionable recommendations"
  constraints: "Harness architecture scope only (excludes /app folder), informational failure handling for comprehensive coverage"
---

# Architect Consistency Check Workflow

**ID**: WF-ARCH-CONS-CHECK  
**Owner**: Architect Agent  
**Frequency**: On-demand (recommended: weekly basic, monthly comprehensive)  
**Duration**: Variable (30-90 minutes depending on scope)  
**Priority**: High
**Workflow Type**: Single-Execution (Utility/Tool Workflow)
**Execution Modes**: Full Comprehensive, Basic Essential, Targeted, Quick Check

## Purpose
Systematic validation of harness architecture consistency across the entire project to identify structural issues, broken references, terminology inconsistencies, governance gaps, and architectural health using advanced fitness functions and multi-agent validation. The workflow continues through all phases even if individual validation steps fail, treating failures as informational for the final report rather than blocking progress.

## Reference Documents
- **Universal Framework References**: Workflow/Workflow_Reference/ (referenced frameworks based on workflow relevance)
- **Agent Rules**: .devin/rules/architect.md (Architect-specific governance rules)
- **Terminology**: Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for governance terminology)
- **Execution Mode Patterns**: Workflow/Architect/.Reference/Execution_Mode_Patterns.md (Architect-specific execution mode definitions)
- **Validation Enforcement**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (universal validation patterns)

## Scope
**Harness Architecture Only**: Governance files, workflows, rules, documentation (excludes /app folder)

**Report Location**: Logs/Architect/Consistency Review/Scan_{YYYY-MM-DD_HH-MM-SS}.md

## Roles and Owners
- **Architect Agent**: Executes consistency check, generates report, analyzes findings
- **User**: Reviews findings, decides on fix strategy, approves architectural changes
- **Governance System**: Validation and compliance enforcement

## Trigger and End State
- **Trigger**: User requests consistency check OR before/after major architectural changes
- **End State**: Comprehensive consistency report generated in Logs/Architect/Consistency Review/

## Workflow Steps (180 steps)

**IMPORTANT**: All phases execute sequentially. Phase validation failures are treated as informational warnings and do not block workflow progression. All findings are aggregated in the final report for comprehensive review.

### Load Governance Rules
- 1. **OPEN** WorkflowOpen skill to dynamically load agent-specific rules based on agent type
- 2. **STATUS TRACKING**: Update workflow status to "governance_rules_loaded"
- 3. **PRINT** "Governance rules loaded dynamically based on agent type"

### Select Execution Mode
- 1. Ask user to select execution mode for this workflow using popup menu:
  - **Manual**: Stop at each inconsistency for user oversight
  - **Automatic**: Process automatically until failure, then ask user
- 2. Store selected execution mode for failure handling throughout workflow
- 3. **STATUS TRACKING**: Update workflow status to "execution_mode_selected"
- 4. **PRINT** "Execution mode selected - [Manual/Automatic] will govern failure handling"

### Phase 1. Select Scan Strategy
- 1. Determine scan scope (full harness vs specific components)
- 3. Store governance context for reference throughout scan
- 4. **STATUS TRACKING**: Update workflow status to "phase_0_complete"
- 5. **PRINT**: "Governance rules loaded dynamically - initiating harness architecture consistency scan"

### Phase 1. Select Scan Strategy
- 1. Ask user to select scan strategy using popup menu:
  - **Full Comprehensive**: All consistency variables (recommended monthly)
  - **Basic Essential**: File references + terminology + workflow structure (recommended weekly)
  - **Targeted**: User selects specific consistency variables
  - **Quick Check**: File references only (recommended before changes)
- 2. Store selected scan strategy for execution
- 3. **EXECUTION MODE HANDLING**: Apply execution mode handling patterns (see Workflow/Architect/Reference/Execution_Mode_Patterns.md)
- 4. **PRINT**: "Scan strategy selected - {Strategy} will govern consistency check scope"

### Phase 2. Harness Architecture File Discovery
- 1. Use `find` to enumerate all harness architecture files:
  - `find . -name "*.md" \( -path "*/Workflow/*" -o -path "*/.devin/rules/*" -o -path "*/.devin/*" -o -path "*/STRUCTURE.md" \)`
- 2. Exclude /app folder from scan results
- 3. Generate file inventory with paths and types
- 4. **STATUS TRACKING**: Update workflow status to "phase_2_complete"
- 5. **PRINT**: "File discovery complete - {N} harness architecture files identified"

### Phase 3. Schema and Categorization Validation (if full scan)
- 1. **AUTOMATED**: Run schema validation script: `python Scripts/Schema/validate_schemas.py`
- 2. Schema Validation: Validate YAML frontmatter structure against JSON schemas for workflow, rules, agents, skill, reference, and template files
- 3. Categorization Validation: Validate file placement and directory structure against categorization rules in Scripts/Schema/validate_schemas.py
- 4. Parse validation output to extract schema validation failures and categorization violations
- 5. **WARNING HANDLING**: Continue workflow even if schema validation fails - treat issues as informational for report generation
- 6. **STATUS TRACKING**: Update workflow status to "phase_3_complete"
- 7. **PRINT**: "Schema and categorization validation complete - {N} schema issues, {N} categorization issues found (will be included in final report)"

### Phase 4. File Reference Consistency Check
- 1. **SCAN**: Read each harness architecture file line by line to extract all file references
- 2. Extract all file references using `grep -r "Workflow/[A-Za-z/]*\.md" ./Workflow/` as supplemental check
- 3. Extract all .devin/rules/ references using `grep -r "\.devin/rules/[a-z]*\.md" ./Workflow/` as supplemental check
- 4. Validate each referenced file exists at specified path
- 5. Log broken references with file locations
- 6. **WARNING HANDLING**: Continue workflow even if file reference extraction fails - treat issues as informational for report generation
- 7. **STATUS TRACKING**: Update workflow status to "phase_4_complete"
- 8. **PRINT**: "File reference check complete - {N} broken references found"

### Phase 5. Terminology Consistency Check
- 1. **SCAN**: Read each harness architecture file line by line to check for outdated terminology
- 2. Search for outdated terminology: `grep -r "gate" ./Workflow/` (should return no results if cleanup complete, except in meta-references like this line) as supplemental check
- 3. Check agent naming convention consistency
- 4. **WARNING HANDLING**: Continue workflow even if terminology check fails - treat issues as informational for report generation
- 5. **STATUS TRACKING**: Update workflow status to "phase_5_complete"
- 6. **PRINT**: "Terminology check complete - {N} terminology inconsistencies found"

### Phase 6. Workflow Structure Consistency Check
- 1. **SCAN**: Read each workflow file line by line to validate workflow structure
- 2. Check for mandated sections: Workflow Header, Universal Framework References
- 3. Validate workflow follows header structure requirements (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State)
- 4. Check Universal Framework References section presence and completeness
- 5. Note any missing suggested phases (Phase 0, Phase 3, Phase 7) as informational, not as issues
- 6. Validate step numbering sequential consistency (if steps are used)
- 7. **EXECUTION MODES VALIDATION**: Validate that workflow defines its specific execution mode options in header and Phase 1 (accept workflow-specific mode definitions)
- 8. **WARNING HANDLING**: Continue workflow even if workflow structure check fails - treat issues as informational for report generation
- 9. **STATUS TRACKING**: Update workflow status to "phase_6_complete"
- 10. **PRINT**: "Workflow structure check complete - {N} structure issues found"

### Phase 7. Markdown Structure Validation (if full scan)
- 1. **SCAN**: Validate markdown document structure using mdsmith/mdschema patterns
- 2. Heading Consistency: Check heading hierarchy and markdown heading levels
- 3. Section Completeness: Validate required sections are present in documents
- 4. Frontmatter Validation: Ensure YAML frontmatter follows proper structure
- 5. Link Validation: Check internal and external links are valid
- 6. Code Block Validation: Ensure code blocks have proper language tags
- 7. **WARNING HANDLING**: Continue workflow even if markdown structure checks fail - treat issues as informational for report generation
- 8. **STATUS TRACKING**: Update workflow status to "phase_7_complete"
- 9. **PRINT**: "Markdown structure validation complete - {N} structure issues found"

### Phase 8. Basic Governance Validation (if full scan)
- 1. **SCAN**: Read each .devin/rules/ file line by line to check structure and patterns
- 2. Governance Rule Consistency: Check .devin/rules/ files structure and patterns
- 3. **SCAN**: Read STRUCTURE.md and documentation files line by line to validate conventions
- 4. Documentation Structure: Validate STRUCTURE.md and documentation conventions
- 5. **SCAN**: Validate Logs/ directory structure follows agent-specific organization (Logs/{Agent}/BP/{App/Harness}/)
- 6. Directory Structure Consistency: Validate Logs/ directory structure matches workflow output locations
- 7. **WARNING HANDLING**: Continue workflow even if basic governance checks fail - treat issues as informational for report generation
- 8. **STATUS TRACKING**: Update workflow status to "phase_8_complete"
- 9. **PRINT**: "Basic governance validation complete - {N} governance issues found"

### Phase 9. Advanced Content Validation (if full scan)
- 1. **SCAN**: Read AGENTS.md line by line to compare with actual capabilities
- 2. Agent Capability Alignment: Compare AGENTS.md with actual capabilities
- 3. **SCAN**: Read framework files line by line to check proper separation and references with relevance requirement
- 4. Universal Framework Coverage: Check proper separation and references with relevance requirement
- 5. **SCAN**: Read each workflow file line by line to ensure either WorkflowOpen skill is used in Phase 0 OR Workflow/Workflow_Reference/Terminology_Glossary.md is referenced in Phase 0
- 6. Terminology Glossary Reference Consistency: Ensure all workflows reference either WorkflowOpen skill or Workflow/Workflow_Reference/Terminology_Glossary.md in Phase 0
- 7. **WARNING HANDLING**: Continue workflow even if advanced content checks fail - treat issues as informational for report generation
- 8. **STATUS TRACKING**: Update workflow status to "phase_9_complete"
- 9. **PRINT**: "Advanced content validation complete - {N} content issues found"

### Phase 10. Dependency Graph Analysis (if full scan)
- 1. **ANALYZE**: Build dependency graph for harness architecture files
- 2. Circular Dependency Detection: Identify circular dependencies in architecture
- 3. Layer Violation Check: Validate layer boundaries and dependency direction
- 4. Dependency Depth Analysis: Measure depth of dependency chains
- 5. Coupling Analysis: Calculate coupling metrics between components
- 6. Dependency Visualization: Generate dependency graph for review
- 7. **WARNING HANDLING**: Continue workflow even if dependency graph analysis fails - treat issues as informational for report generation
- 8. **STATUS TRACKING**: Update workflow status to "phase_10_complete"
- 9. **PRINT**: "Dependency graph analysis complete - {N} circular dependencies, {N} layer violations"

### Phase 11. Architecture as Code Validation (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires deterministic compiler infrastructure not yet implemented
- 2. **COMPILE**: Compile architecture specifications using deterministic compiler
- 3. Intent Validation: Verify structural constraints against codebase using static analysis
- 4. Behavioral Specifications: Compile behavioral specs to TLA+ for model verification
- 5. Design Rationale: Capture and validate design rationale in machine-readable format
- 6. Architecture Lint: Validate architecture structure and lint rules
- 7. **WARNING HANDLING**: Continue workflow even if architecture compilation fails - treat issues as informational for report generation
- 8. **STATUS TRACKING**: Update workflow status to "phase_11_complete"
- 9. **PRINT**: "Architecture as code validation complete - {N} structural issues, {N} behavioral issues (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 12. Architecture Fitness Functions (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires fitness function calculation infrastructure not yet implemented
- 2. **ANALYZE**: Calculate architectural health metrics using fitness functions
- 3. Cohesion Analysis: Measure module cohesion within agent-specific directories
- 4. Coupling Analysis: Calculate coupling between different agent components
- 5. Complexity Metrics: Assess complexity of workflow and rule structures
- 6. Dependency Depth: Measure depth of dependency chains across architecture
- 7. Baseline Comparison: Compare against previous fitness function results
- 8. **WARNING HANDLING**: Continue workflow even if fitness function calculations fail - treat issues as informational for report generation
- 9. **STATUS TRACKING**: Update workflow status to "phase_12_complete"
- 10. **PRINT**: "Architecture fitness functions complete - cohesion: {X}%, coupling: {X}%, complexity: {X}% (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 13. Continuous Conformance Tracking (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires conformance tracking infrastructure not yet implemented
- 2. **ANALYZE**: Calculate distance-based conformance metrics against reference architecture
- 3. Baseline Comparison: Compare current architecture against established baseline
- 4. Drift Detection: Identify architectural drift since last consistency check
- 5. Trend Analysis: Track conformance trends over time
- 6. Distance Metrics: Calculate architectural distance using conformance functions
- 7. Conformance Thresholds: Check against acceptable deviation limits
- 8. **WARNING HANDLING**: Continue workflow even if conformance tracking fails - treat issues as informational for report generation
- 9. **STATUS TRACKING**: Update workflow status to "phase_13_complete"
- 10. **PRINT**: "Conformance tracking complete - distance: {X}, drift: {X}, trend: {X} (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 14. Runtime and Execution Validation (if full scan)
- 1. **SCAN**: Read workflow files line by line to validate execution patterns across agents
- 2. Execution Strategy Consistency: Validate execution patterns across agents
- 3. **SCAN**: Read workflow files line by line to check state schemas and tracking patterns
- 4. State Management Consistency: Check state schemas and tracking patterns
- 5. **SCAN**: Read configuration files line by line to validate runtime infrastructure documentation
- 6. Runtime Prerequisites: Validate runtime infrastructure documentation
- 7. **SCAN**: Read quality assessment files line by line to validate 1-5 scoring scale consistency
- 8. Scoring Scale Consistency: Validate 1-5 scoring scale consistency across quality assessments
- 9. **SCAN**: Read AGENTS.md line by line to validate behavior rules are properly defined
- 10. Agent Behavior Rules Consistency: Validate AGENTS.md behavior rules are properly defined
- 11. **WARNING HANDLING**: Continue workflow even if runtime and execution checks fail - treat issues as informational for report generation
- 12. **STATUS TRACKING**: Update workflow status to "phase_14_complete"
- 13. **PRINT**: "Runtime and execution validation complete - {N} runtime issues found"

### Phase 15. ADR Enforcement Integration (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires ADR enforcement infrastructure (archgate/adr-kit) not yet implemented
- 2. **ENFORCE**: Validate code against documented architectural decision records
- 3. ADR Validation: Check that code complies with accepted ADRs using archgate/adr-kit patterns
- 4. Rule Generation: Generate lint rules from ADRs for automated enforcement
- 5. Context Injection: Ensure relevant ADRs are available to AI agents during implementation
- 6. Anti-Rationalization Guards: Check for excuses that skip ADR documentation
- 7. Verification Validations: Run ADR quality validations (Completeness, Evidence, Clarity, Consistency)
- 8. Enforcement Hooks: Validate ADR compliance in pre-commit and CI pipelines
- 9. **WARNING HANDLING**: Continue workflow even if ADR enforcement fails - treat issues as informational for report generation
- 10. **STATUS TRACKING**: Update workflow status to "phase_15_complete"
- 11. **PRINT**: "ADR enforcement complete - {N} ADR violations detected (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 16. Multi-Agent Architecture Validation (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires multi-agent council infrastructure not yet implemented
- 2. **COUNCIL**: Execute multi-agent validation using council approach for complex decisions
- 3. Specialized Agents: Security, Performance, Structure agents analyze architecture
- 4. AST-Aware RAG: Bridge semantic-structural gap using AST-aware retrieval
- 5. LangGraph Orchestration: 5-node state machine for comprehensive validation
- 6. Council Synthesis: Specialized agents synthesize comprehensive verdict
- 7. Formal Verification: Optional Z3 formal verification for critical constraints
- 8. **WARNING HANDLING**: Continue workflow even if multi-agent validation fails - treat issues as informational for report generation
- 9. **STATUS TRACKING**: Update workflow status to "phase_16_complete"
- 10. **PRINT**: "Multi-agent validation complete - {N} critical issues identified (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 17. Production Readiness Scoring (FUTURE IMPLEMENTATION)
- 1. **FUTURE**: This phase requires production readiness scoring infrastructure not yet implemented
- 2. **SCORE**: Calculate 0-100 production readiness score across dimensions
- 3. Auth Coverage: Measure route auth coverage and security enforcement
- 4. Secrets Hygiene: Validate secrets management and token storage practices
- 5. Test Footprint: Assess test coverage and quality metrics
- 6. Migration Discipline: Check database migration practices and data layer discipline
- 7. Ops Readiness: Validate Docker, CI, and .env contract compliance
- 8. Documentation/API Contract: Check API documentation completeness
- 9. **WARNING HANDLING**: Continue workflow even if production readiness scoring fails - treat issues as informational for report generation
- 10. **STATUS TRACKING**: Update workflow status to "phase_17_complete"
- 11. **PRINT**: "Production readiness scoring complete - score: {X}/100, top issues prioritized (FUTURE IMPLEMENTATION - infrastructure not available)"

### Phase 18. Report Generation
- 1. Create Logs/Architect/Consistency Review/ directory if not exists
- 2. Generate report with timestamp: Scan_{YYYY-MM-DD_HH-MM-SS}.md
- 3. Include executive summary with overall consistency score
- 4. Document findings for each consistency variable checked
- 5. Classify issues by severity (Critical/High/Medium/Low)
- 6. Provide actionable recommendations with timeline
- 7. Include infrastructure gap analysis for FUTURE IMPLEMENTATION phases
- 8. **WARNING HANDLING**: Continue workflow even if report generation fails - attempt manual report creation
- 9. **STATUS TRACKING**: Update workflow status to "phase_18_complete"
- 10. **PRINT**: "Report generation complete - workflow terminated"

---

## Universal Framework References

### Quality Assessment
- **Universal Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md
- **Architect Customization**: Harness architecture quality assessment
- **Focus**: Governance file quality and architectural compliance

### Role Responsibilities
- **Universal Framework**: Workflow/Workflow_Reference/Role_Responsibilities_Framework.md
- **Architect Customization**: Architect-specific consistency management responsibilities
- **Focus**: Architecture integrity maintenance and governance compliance

### Performance Metrics
- **Universal Framework**: Workflow/Workflow_Reference/Performance_Metrics_Framework.md
- **Architect Customization**: Consistency score metrics and improvement tracking
- **Focus**: Architecture consistency metrics and baseline tracking

### State Management
- **Universal Framework**: Workflow/Workflow_Reference/State_Management_Guidelines.md
- **Architect Customization**: Consistency check state tracking
- **Focus**: Scan progress state and report generation tracking

### Execution Strategy
- **Universal Framework**: Workflow/Workflow_Reference/Execution_Strategy_Guidelines.md
- **Architect Customization**: Scan strategy selection and execution patterns
- **Focus**: Prioritized consistency checking and analysis execution

### Runtime Prerequisites
- **Universal Framework**: Workflow/Workflow_Reference/Runtime_Prerequisites.md
- **Architect Customization**: Consistency check runtime requirements
- **Focus**: Scan execution environment and report generation infrastructure

---

## Consistency Variables

### 1. File Reference Consistency
- **Check**: All referenced files exist at specified paths
- **Scope**: Workflow files, rule files, reference documents
- **Variables**: 
  - `Workflow/` path references in workflow files
  - `.devin/rules/` path references in workflow files  
  - `Workflow_Reference/` path references
  - Agent-specific Reference/ path references
  - Template path references
  - External file references (STRUCTURE.md, AGENTS.md)

### 2. Terminology Consistency
- **Check**: Consistent terminology across all governance files
- **Scope**: All markdown files in harness architecture
- **Variables**:
  - "gate" terminology (should be eliminated in favor of "validation", except in meta-references describing the check itself)
  - Framework naming (removed - naming issue resolved)
  - Agent naming conventions
  - Phase naming conventions

### 3. Workflow Structure Consistency
- **Check**: All workflows follow basic structure requirements
- **Scope**: All workflow files in Workflow/ directory
- **Variables**:
  - Mandated sections: Workflow Header, Universal Framework References
  - Header metadata completeness (ID, Owner, Frequency, Duration, Priority, Execution Modes, Purpose, Roles, Trigger and End State)
  - Universal framework coverage (relevant frameworks)
  - Execution Modes definition in header and Phase 1 (workflow-specific options accepted)
  - Suggested phases (Phase 0, Phase 3, Phase 7) - informational only
  - STATUS TRACKING entries presence (informational)
  - VALIDATION entries presence (informational)
  - PRINT commands presence (informational)
  - **Phase 0 Governance**: Either WorkflowOpen skill usage OR direct rule file references (both accepted patterns)
  - Step numbering sequential consistency (if steps are used)

### 4. Governance Rule Consistency
- **Check**: Rules files are properly structured and consistent
- **Scope**: All .devin/rules/{agent}.md files
- **Variables**:
  - YAML frontmatter structure
  - Rule naming conventions
  - Rule categorization patterns
  - Rule enforcement patterns
  - Dependencies between rules

### 5. Documentation Structure Consistency
- **Check**: Documentation follows architectural conventions
- **Scope**: STRUCTURE.md, Docs/ directory structure
- **Variables**:
  - STRUCTURE.md references accuracy
  - File categorization compliance
  - Directory structure adherence
  - Documentation placement conventions
  - Categorization rules compliance

### 6. Agent Capability Consistency
- **Check**: Agent descriptions match actual capabilities
- **Scope**: AGENTS.md, workflow files, rule files
- **Variables**:
  - AGENTS.md agent descriptions
  - Workflow capabilities vs AGENTS.md
  - Role responsibilities vs actual work
  - Rule files vs agent scope
  - Cross-agent dependencies

### 7. Universal Framework Coverage
- **Check**: Proper separation of universal vs agent-specific content with relevance requirement
- **Scope**: Workflow_Reference/ and agent Reference/ folders
- **Variables**:
  - Universal framework references in agent workflows (relevance requirement: only include frameworks relevant to agent purpose)
  - No agent-specific content in Workflow_Reference/
  - No universal content in agent Reference/
  - Universal Pattern Reference sections presence
  - Cross-reference patterns consistency
  - Framework reference count appropriateness (Architect: ~5, Planner: ~9, Executor: ~8 based on agent purpose)

### 8. Execution Strategy Consistency
- **Check**: Execution patterns are consistent across agents
- **Scope**: Execution mode patterns, implementation modes
- **Variables**:
  - Execution mode definitions (agent-specific options accepted)
  - Implementation mode patterns
  - Quota handling references
  - Execution strategy guidelines references
  - Cross-agent execution pattern alignment
  - Each agent has execution mode patterns in their Reference/ folder
  - Workflows reference their agent-specific Execution_Mode_Patterns.md
  - Universal patterns in Workflow/Workflow_Reference/Execution_Mode_Patterns.md provide general guidance

### 9. State Management Consistency
- **Check**: State schemas and tracking patterns are consistent
- **Scope**: State schemas, state tracking in workflows
- **Variables**:
  - State schema definitions for each agent
  - State tracking patterns in workflows
  - State persistence mechanisms
  - State variable naming conventions
  - State management guidelines references

### 10. Runtime Prerequisites Consistency
- **Check**: Runtime infrastructure documentation is accurate
- **Scope**: Runtime paths, Scripts/, .devin/, Logs/ directories
- **Variables**:
  - Referenced runtime paths existence
  - Scripts/ directory structure
  - .devin/ configuration files
  - Logs/ directory structure
  - Runtime prerequisites documentation accuracy

### 11. Scoring Scale Consistency
- **Check**: Quality assessment uses consistent scoring scales
- **Scope**: Quality assessment references, template scoring, workflow convergence checks
- **Variables**:
  - Quality assessment framework uses 1-5 scale consistently
  - Template scoring examples match 1-5 scale
  - Workflow convergence checks use 1-5 scale thresholds
  - No mixed scoring scales (0-100 vs 1-5)
  - Quality threshold consistency across workflows

### 12. Agent Behavior Rules Consistency
- **Check**: AGENTS.md behavior rules are properly defined and consistent
- **Scope**: AGENTS.md, agent workflows, agent rules
- **Variables**:
  - AGENTS.md contains current behavior rules (direct question answering, BP? search)
  - Behavior rules are consistent across all agents
  - Behavior rules are actionable and clear
  - Behavior rules align with actual agent behavior in workflows
  - No conflicting behavior rules

### 13. Directory Structure Consistency
- **Check**: Logs/ directory structure follows agent-specific organization patterns
- **Scope**: Logs/ directory structure across all agents
- **Variables**:
  - Logs/{Agent}/BP/{App/Harness}/ structure exists for relevant agents
  - Workflow output locations match actual directory structure
  - Timestamp formatting consistency (YYYY-MM-DD_HH-MM-SS)
  - Incremental report locations match workflow specifications
  - Directory structure supports workflow separation (App vs Harness outputs)

### 14. Schema and Categorization Consistency
- **Check**: File placement and YAML frontmatter structure comply with governance rules
- **Scope**: All repository files, especially governance files
- **Variables**:
  - YAML frontmatter structure compliance with JSON schemas
  - File placement compliance with categorization rules
  - Directory structure adherence to Scripts/, Workflow/, .devin/rules/, Docs/, Logs/, Agents/, .devin/ categories
  - Subdirectory structure compliance with categorization system
  - Naming convention adherence (workflow, rules, agents, skill, reference, template files)
  - Root directory file placement compliance (only approved files at root)
  - Schema validation errors and missing frontmatter
  - Categorization violations (wrong directory, wrong subdirectory, naming violations)

### 15. Architecture Fitness Functions (FUTURE IMPLEMENTATION)
- **Check**: Architectural health metrics using fitness functions for quantitative assessment
- **Scope**: Harness architecture structure and dependencies
- **Variables**:
  - Cohesion metrics (how well-related components are grouped together)
  - Coupling metrics (interdependencies between components)
  - Complexity metrics (structural complexity of workflows and rules)
  - Dependency depth metrics (depth of dependency chains)
  - Architectural health score (aggregated fitness function results)
  - Trend analysis over time (baseline comparison)
  - Fitness function thresholds and alerts

### 16. Continuous Conformance Tracking (FUTURE IMPLEMENTATION)
- **Check**: Distance-based conformance metrics against reference architecture
- **Scope**: Overall architecture alignment with reference standards
- **Variables**:
  - Baseline conformance metrics (established reference architecture baseline)
  - Architectural distance metrics (quantitative distance from reference)
  - Drift detection (changes since last consistency check)
  - Trend analysis (conformance improvement/degradation over time)
  - Conformance thresholds (acceptable deviation limits)
  - Alert conditions (when conformance falls below thresholds)
  - Multi-level checking (incremental and non-blocking validation)

### 17. Markdown Structure Validation
- **Check**: Markdown document structure using mdsmith/mdschema patterns
- **Scope**: All markdown files in harness architecture
- **Variables**:
  - Heading hierarchy consistency (proper markdown heading levels)
  - Section completeness (required sections present)
  - Frontmatter structure (YAML frontmatter compliance)
  - Link validity (internal and external links work)
  - Code block formatting (proper language tags)
  - Table structure (markdown table formatting)
  - List formatting (consistent list markers)
  - Document schema compliance (matches defined schemas)

### 18. Dependency Graph Analysis
- **Check**: Dependency graph analysis for harness architecture files
- **Scope**: All architectural dependencies and relationships
- **Variables**:
  - Circular dependencies (modules that depend on each other)
  - Layer violations (dependencies crossing layer boundaries)
  - Dependency depth (depth of dependency chains)
  - Coupling metrics (interdependencies between components)
  - Dependency graph structure (overall dependency topology)
  - Fan-in/fan-out metrics (incoming/outgoing dependencies)
  - Critical paths (dependencies that affect multiple components)
  - Dependency violations (forbidden or unexpected dependencies)

### 19. Architecture as Code Validation (FUTURE IMPLEMENTATION)
- **Check**: Architecture compilation and verification using deterministic patterns
- **Scope**: Architecture specifications and structural constraints
- **Variables**:
  - Structural constraints verification (layering, dependency boundaries, module containment)
  - Behavioral specifications (TLA+ compilation and model verification)
  - Design rationale capture (machine-readable decision records)
  - Architecture lint validation (structural rule compliance)
  - Deterministic verification (same inputs always produce same outputs)
  - Contract validation (architecture contract compliance)

### 20. ADR Enforcement Integration (FUTURE IMPLEMENTATION)
- **Check**: Architectural decision records enforcement against implementation
- **Scope**: ADR files, code changes, AI agent outputs
- **Variables**:
  - ADR compliance (code matches documented decisions)
  - Rule generation (ADR-based lint rules)
  - Context injection (relevant ADRs available to agents)
  - Anti-rationalization guards (prevent ADR documentation skipping)
  - Verification validations (ADR quality: Completeness, Evidence, Clarity, Consistency)
  - Enforcement hooks (pre-commit and CI pipeline integration)
  - ADR lifecycle management (supersession, retirement)

### 21. Multi-Agent Architecture Validation (FUTURE IMPLEMENTATION)
- **Check**: Multi-agent council approach for complex architectural decisions
- **Scope**: Complex architectural decisions requiring multiple perspectives
- **Variables**:
  - Specialized agent analysis (Security, Performance, Structure)
  - AST-aware RAG (semantic-structural gap bridging)
  - LangGraph orchestration (multi-agent state machine)
  - Council synthesis (specialized agent verdict integration)
  - Formal verification (Z3 constraint solving)
  - Confidence scoring (validation confidence levels)
  - Multi-agent consensus (agreement on architectural issues)

### 22. Production Readiness Scoring (FUTURE IMPLEMENTATION)
- **Check**: Production readiness score across multiple dimensions
- **Scope**: Overall system readiness for production deployment
- **Variables**:
  - Auth coverage (route auth coverage and security enforcement)
  - Secrets hygiene (secrets management and token storage)
  - Test footprint (test coverage and quality metrics)
  - Migration discipline (database migration practices)
  - Ops readiness (Docker, CI, .env contract compliance)
  - Documentation/API contract (API documentation completeness)
  - Production readiness score (0-100 overall score)
  - Top issues prioritization (highest-impact fixes ranked)

## Consistency Check Process

### Process Step 1: Harness Architecture Scan
1. **File Discovery**: Use `find` to enumerate all harness architecture files
2. **Comprehensive Line-by-Line Scanning**: **SCAN** each file line by line to examine all documents within scope without skipping anything - comprehensive examination required for governance compliance
3. **Pattern Matching**: Use `grep` to extract specific patterns from files as supplemental checks only
4. **Cross-Reference Analysis**: Verify all file references exist
5. **Structure Validation**: Validate workflow structure compliance
6. **Terminology Analysis**: Check for inconsistent terminology

### Process Step 2: Detailed Variable Analysis
1. **File Reference Validation**: Check each referenced file exists
2. **Workflow Structure Validation**: Compare workflows against template for mandated sections only
3. **Governance Rule Validation**: Check rule file structure consistency
4. **Documentation Validation**: Verify STRUCTURE.md and documentation structure
5. **Framework Coverage Validation**: Check universal framework usage

### Process Step 3: Issue Aggregation
1. **Severity Classification**: Classify issues as Critical/High/Medium/Low
2. **Categorization**: Group issues by consistency variable
3. **Impact Analysis**: Assess impact on harness functionality
4. **Recommendation Generation**: Generate fix recommendations

### Process Step 4: Report Generation
1. **Report Structure**: Create comprehensive report with findings
2. **Issue Prioritization**: Order issues by severity and impact
3. **Fix Recommendations**: Provide specific fix suggestions
4. **Metrics Summary**: Provide consistency metrics

## Report Structure

```markdown
# Architect Consistency Check Report

**Scan Date**: {YYYY-MM-DD HH:MM:SS}
**Scan Scope**: Harness Architecture (excludes /app folder)
**Report Location**: Logs/Architect/Consistency Review/Scan_{YYYY-MM-DD_HH-MM-SS}.md

## Executive Summary

**Overall Consistency Score**: {X/100}
**Critical Issues**: {N}
**High Issues**: {N}
**Medium Issues**: {N}
**Low Issues**: {N}

## Infrastructure Gap Analysis

**Future Implementation Phases**: {N}
**Missing Infrastructure**: {List of required tools/scripts}
**Recommended Actions**: {Infrastructure implementation priorities}

## Consistency Variable Results

### 1. File Reference Consistency
**Status**: {PASS/FAIL/WARNING}
**Issues Found**: {N}
**Critical Issues**: {N}

{Detailed findings}

[... continue for all 22 variables]

## Critical Issues Summary

[Critical issues requiring immediate attention]

## High Priority Issues

[High priority issues]

## Medium Priority Issues

[Medium priority issues]

## Low Priority Issues

[Low priority issues]

## Consistency Metrics

**File Reference Accuracy**: {X}%
**Terminology Consistency**: {X}%
**Workflow Structure Compliance**: {X}%
**Governance Rule Consistency**: {X}%
**Documentation Structure Accuracy**: {X}%
**Agent Capability Alignment**: {X}%
**Universal Framework Coverage**: {X}%
**Execution Strategy Consistency**: {X}%
**State Management Consistency**: {X}%
**Runtime Prerequisites Accuracy**: {X}%
**Scoring Scale Consistency**: {X}%
**Agent Behavior Rules Consistency**: {X}%
**Directory Structure Consistency**: {X}%
**Schema and Categorization Compliance**: {X}%
**Architecture Fitness Functions**: {X}% (FUTURE IMPLEMENTATION)
**Continuous Conformance Tracking**: {X}% (FUTURE IMPLEMENTATION)
**Markdown Structure Validation**: {X}%
**Dependency Graph Analysis**: {X}%
**Architecture as Code Validation**: {X}% (FUTURE IMPLEMENTATION)
**ADR Enforcement Integration**: {X}% (FUTURE IMPLEMENTATION)
**Multi-Agent Architecture Validation**: {X}% (FUTURE IMPLEMENTATION)
**Production Readiness Scoring**: {X}% (FUTURE IMPLEMENTATION)

## Recommendations

### Immediate Actions (Critical Issues)
[Recommendations for critical issues]

### Short-term Actions (High Priority)
[Recommendations for high priority issues]

### Long-term Improvements (Medium/Low Priority)
[Recommendations for medium/low priority issues]

### Infrastructure Implementation Priorities
[Recommendations for enabling future implementation phases]
```

---

**Current Status**: Active  
**Last Updated**: 2026-07-28  
**Maintained By**: Architect Agent  
**Review Frequency**: Monthly or when consistency needs change

## Changelog

**2026-07-30**: Version bump to 1.1 + YAML frontmatter fixes
- Updated version from 1.0 to 1.1 to reflect structural changes
- Added missing YAML frontmatter fields (expected_agent_type, persona)
- Fixed step count in header (167 → 180 steps)
- Added Reference Documents section with proper references
- Fixed hardcoded paths (replaced /c/SovereignAI with relative paths)
- Fixed reference path (Workflow/Architect/Reference → Workflow/Architect/.Reference)
- Added Load Governance Rules and Select Execution Mode sections

**2026-07-28**: Workflow restructured for logical phase ordering
- Reordered phases to follow logical progression: Setup → Basic Structure → Content Validation → Dependency Analysis → Advanced Analysis
- Moved File Reference Consistency (Phase 7 → Phase 4)
- Moved Terminology Consistency (Phase 9 → Phase 5)
- Moved Workflow Structure Consistency (Phase 11 → Phase 6)
- Extracted and reorganized Phase 12 into logical sub-phases (Phase 8, Phase 9, Phase 14)
- Marked infrastructure-missing phases as FUTURE IMPLEMENTATION (Phases 11, 12, 13, 15, 16, 17)
- Updated workflow step count from 159 to 180 steps
- Added infrastructure gap analysis to report structure
- Detailed consistency variables maintained at 22 total variables
