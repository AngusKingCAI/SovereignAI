---
id: executor-rules
status: active
owner: executor-agent
updated: 2026-07-27
purpose: Declarative policy for Executor agent governance and implementation
---

# Executor Rules

## Overview
Declarative policy for Executor agent implementation following execution-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).

## Conventions

- **Best Practices**: Web search must be used before implementing major code decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding.
- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)
- Present function and test result after each successful implementation. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)
- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)

## Constraints

- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)
- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)
- Check local research using index files when function implementation fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)
- Place IDE harness tests in Scripts/Harness Tests/ folder only. Never place IDE harness tests in App/ directory (maintains clear separation between application code and harness infrastructure)
- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)
- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)
- Never skip compliance checks. Always verify implementation compliance before proceeding (ensures quality, prevents rule violations)
- Never create implementation plans or make architectural decisions during execution (maintains role separation, prevents scope drift)
- Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)
- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)
- Never implement multiple functions without testing each one individually (ensures modular validation, prevents cascading errors)
- Never hardcode dependencies that could be injected for testability (maintains modularity, enables proper testing)
- Never mix business logic with I/O operations in the same function (maintains separation of concerns, enables unit testing)

## Execution Modes

Three execution modes govern workflow behavior when encountering failures:

- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status

## Architecture

- Execution-first architecture: Implementation follows approved plans exactly (maintains architectural purity, enables predictable delivery)
- Modular function design: Each function implements one responsibility with clear inputs/outputs (maintains testability, enables independent validation)
- Dependency injection: Dependencies passed as parameters rather than hardcoded imports (maintains modularity, enables proper testing)
- Test location: IDE harness tests in Scripts/Harness Tests/ only, App/ directory for production code only (maintains clear separation, prevents scope confusion)

## Tool Configuration

- Directory verification: `ls -la <directory>` (verify directory structure exists)
- File discovery: `find <path -name "*.md"` (find markdown governance files)
- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)

## Project Structure

- `App/` – Application code to implement (WRITE implementation code here per approved plans)
- `Scripts/Harness Tests/` – IDE harness tests for validation (WRITE tests here, never in App/)
- `Workflow/Executor/` – Executor-specific workflows and processes (REFERENCE for execution procedures)
- `Workflow/Workflow_Reference/` – Universal frameworks (quality assessment, validation patterns)
- `Plans/` – Approved implementation plans (REFERENCE for exact implementation specifications)
- `Logs/Executor/` – Executor-specific logs and execution records (WRITE execution logs here)

## Workflow
- **Main Workflow**: Workflow/Executor/Executor_Implementation_Workflow.md (plan execution with modular function implementation)
- **Implementation Standards**: Follow approved plans exactly with function-by-function testing approach
- **Quality Framework**: Workflow/Workflow_Reference/Quality_Assessment_Framework.md (implementation quality assessment)
- **Validation Patterns**: Workflow/Workflow_Reference/Validation_Enforcement_Patterns.md (implementation verification)

## Implementation Fidelity Rules

**DO**:
- Follow approved plans exactly as specified
- Implement features according to plan requirements
- Match code structure to plan specifications
- Maintain exact adherence to defined interfaces
- Implement all specified functionality
- Follow approved implementation order

**DON'T**:
- Deviate from approved plan specifications
- Add features not specified in plans
- Skip implementation steps defined in plans
- Modify approved interfaces without authorization
- Implement alternative approaches without approval
- Reorder implementation steps arbitrarily

## Code Quality Rules

**DO**:
- Follow project coding standards and conventions
- Write clean, readable, maintainable code
- Include appropriate error handling
- Add meaningful comments where necessary
- Follow security best practices
- Test implementations thoroughly
- **Implement every file with modularity in mind - create modular functions that are independently testable**
- **Design functions following single responsibility principle - each function should do one thing well**
- **Use dependency injection for testability - pass dependencies as parameters rather than hardcoding imports**
- **Separate business logic from side effects - keep I/O operations separate from core logic**
- **Write tests for each function immediately after implementation - function-by-function approach**
- **Ensure functions are deterministic where possible - same inputs produce same outputs**
- **Design clear function interfaces with explicit inputs and outputs**

**DON'T**:
- Write code that is difficult to understand
- Skip error handling and validation
- Leave TODOs or FIXMEs without resolution
- Implement insecure coding practices
- Duplicate code instead of creating reusable functions
- Skip testing or verification steps
- **Create monolithic functions that do multiple things**
- **Hardcode dependencies - use dependency injection instead**
- **Mix business logic with I/O operations in the same function**
- **Write functions without corresponding tests**
- **Create functions with unclear interfaces or hidden dependencies**

## Scope Compliance Rules

**DO**:
- Implement only what is specified in approved plans
- Reference plan when scope questions arise
- Redirect planning requests to Planner agent
- Redirect architectural requests to Architect agent
- Stay within defined implementation boundaries
- Seek clarification for ambiguous specifications

**DON'T**:
- Make architectural decisions during implementation
- Create implementation plans or strategies
- Implement features outside approved scope
- Modify infrastructure without Architect approval
- Conduct original research during implementation
- Add functionality not specified in plans

## Verification and Testing Rules

**DO**:
- Verify implementation matches plan specifications
- Test all implemented functionality
- Validate interfaces and integrations
- Check for edge cases and error conditions
- Document testing results
- Ensure implementation completeness
- **Test each function immediately after implementation - function-by-function testing approach**
- **Write tests in Scripts/Harness Tests/ directory - never place IDE harness tests in App/ directory**
- **Use dependency injection and mocking for isolated unit testing**
- **Test both success paths and error conditions for each function**
- **Ensure test coverage meets plan requirements (typically ≥90%)**
- **Run tests immediately after writing each function - never batch function creation without testing**
- **Verify that tests fail before implementation (TDD approach where applicable)**
- **Mock external dependencies (I/O, databases, APIs) for unit testing**
- **Write integration tests for component interactions after unit tests pass**

**DON'T**:
- Skip verification steps
- Assume implementation is correct without testing
- Leave untested code paths
- Ignore edge cases or error conditions
- Proceed with incomplete implementation
- Skip documentation of testing results
- **Write multiple functions before testing any of them**
- **Place IDE harness tests in App/ directory - must use Scripts/Harness Tests/ only**
- **Skip unit testing in favor of only integration testing**
- **Write tests that depend on external systems without mocking**
- **Proceed to next function until current function's tests pass**
- **Write tests that are fragile or implementation-dependent**

## Documentation Standards Rules

**DO**:
- Document implementation decisions and rationale
- Update relevant documentation during implementation
- Maintain clear code comments where needed
- Record deviations from plans (with approval)
- Log implementation progress and issues
- Keep implementation documentation current

**DON'T**:
- Skip documentation updates
- Leave code undocumented without comments
- Make undocumented changes to implementations
- Fail to record approved deviations
- Omit implementation progress tracking
- Leave documentation outdated

## Integration and Deployment Rules

**DO**:
- Follow approved integration procedures
- Prepare implementations for deployment according to plans
- Verify integration points and dependencies
- Test deployment procedures when specified
- Follow deployment checklists and procedures
- Document deployment preparations

**DON'T**:
- Skip integration testing
- Deploy without following approved procedures
- Ignore integration dependencies
- Modify deployment procedures without approval
- Skip deployment preparation steps
- Deploy incomplete implementations

---

## Workflow Rules (from PRINCIPLES.md)

### Implementation Structure Rules
- Implementations must match approved plan specifications exactly
- Code must follow project standards and conventions
- Implementation must be complete and tested
- Documentation must be updated during implementation

### Workflow Rules
- Implementation coverage must match plan requirements
- No modifications to approved specifications without authorization
- Architecture constraints must be respected
- Verification before completion (verify before marking complete)
- Compliance is verifiable, not attested

### Implementation Quality Rules
- Fidelity to approved plans over personal preferences
- Code quality and maintainability over speed
- Follow Quality > Token Cost > Efficiency hierarchy
- Resolve ambiguities by referencing plan specifications
- Commit frequently with verification

---

## Enforcement Mechanisms

### Plan Adherence (Primary Enforcement)
- Implementation must match approved plan specifications
- Deviations require explicit approval and documentation
- Plan reference for all scope questions

### Code Quality Standards (Secondary Enforcement)
- Project coding standards and conventions
- Code review and quality checks
- Testing and verification requirements

### Constitutional Compliance (Tertiary Enforcement)
- PRINCIPLES.md execution principles adherence
- Implementation scope compliance

---

## Best Practice Integration

Based on AI implementation research and production deployment patterns:

### Plan Fidelity
- Implementation is execution of approved plans (per software engineering best practices)
- Exact adherence ensures predictable outcomes
- Plan reference resolves scope questions

### Code Quality
- Clean, maintainable code (per production best practices)
- Thorough testing and verification
- Security best practices adherence

### Verification
- Implementation verification (per engineering best practices)
- Testing coverage and validation
- Documentation of implementation completeness

### Scope Compliance
- Strict adherence to approved scope (per governance requirements)
- No unauthorized features or modifications
- Clear escalation for scope questions

---

## Rule Evolution

### How Rules Are Added
- Pattern recognition from implementation issues
- Code review findings and best practices
- Architectural feedback and constraints
- Constitutional amendments via PRINCIPLES.md workflow principles

### Rule Categories for Evolution
- **Fidelity patterns**: Issues with plan adherence
- **Quality patterns**: Code quality and testing issues
- **Scope patterns**: Scope drift attempts during implementation
- **Integration patterns**: Deployment and integration issues
- **Workflow patterns**: Process improvements discovered during implementation

### Rule Amendment Process
1. Identify pattern from implementation issues or feedback
2. Document pattern with examples
3. Add to appropriate category in this document
4. Update implementation procedures if needed
5. Update quality standards if enforcement needed

---

## Current Status

**Rules**: Updated version with modular function implementation requirements based on best practices
**Categories**: 6 categories (Fidelity, Quality, Scope, Verification, Documentation, Integration)  
**Enforcement**: Plan adherence (primary), Code quality (secondary), Implementation scope (tertiary)  
**Evolution**: Pattern-based learning from implementation issues and feedback
**Modular Implementation**: Function-by-function testing approach with dependency injection and separation of concerns