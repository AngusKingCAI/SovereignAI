# Principles — SovereignAI

**Version**: 3.0  
**Last Updated**: 2026-07-28  
**Maintained By**: Architect Agent  
**Purpose**: Architectural and operational principles that guide SovereignAI development decisions and implementation patterns

---

## Overview

These principles govern the design, implementation, and operation of the SovereignAI system. They serve as the foundation for architectural decisions, development practices, and operational procedures. All agents and developers should reference these principles when making decisions about system changes or implementations.

## Core Architecture Principles (CA)

### CA-1. Core is Sacred
**Rule**: The system has exactly 12 core modules. All other functionality must be pluggable.
**Implementation**: Core modules provide essential system services. Any feature outside the core must be implemented as a pluggable component.
**Agent Guidance**: When adding new functionality, always implement as a pluggable component rather than modifying core modules.

### CA-2. Everything Pluggable
**Rule**: All components are equal and interchangeable: adapters, skills, memory backends, models, UIs.
**Implementation**: Use consistent interfaces and dependency injection. No component should have special privileges or hardcoded dependencies.
**Agent Guidance**: Design new components with standardized interfaces that can be swapped without affecting system operation.

### CA-3. No Provider Lock-in
**Rule**: System must continue operating if any single component is removed.
**Implementation**: Design for graceful degradation. Components should be hot-swappable without system restart.
**Agent Guidance**: Never create hard dependencies on specific providers. Always allow alternative implementations.

### CA-4. Local-First
**Rule**: System runs fully offline. Cloud services are optional enhancements, not requirements.
**Implementation**: All core functionality must work without internet connectivity. Cloud features are opt-in escalations.
**Scope**: v1 supports Windows only.
**Agent Guidance**: Implement offline-first. Cloud features should be optional add-ons, not core dependencies.

### CA-5. Wire as You Go
**Rule**: No speculative contracts or empty placeholder directories.
**Implementation**: Create components only when needed. Avoid premature abstraction or framework code.
**Agent Guidance**: Implement concrete functionality first. Add abstractions only when multiple implementations exist.

### CA-6. One User, One System
**Rule**: Single user system accessible from anywhere. All UIs connect to the same core.
**Implementation**: Core is user-scoped. Multiple UI clients can connect to the same user's core instance.
**Deferred**: Phone/relay support.
**Agent Guidance**: Design for single-user multi-device access. Core state is per-user, not shared across users.

### CA-7. Modular Over Simple
**Rule**: Prefer modular, flexible design over simple, monolithic approaches.
**Implementation**: Components should fail independently. System degradation should be graceful, not catastrophic.
**Agent Guidance**: Design for failure isolation. When one component fails, others should continue operating.

### CA-8. UI Process Separation
**Rule**: UIs are separate processes consuming the capability API via a standardized interface.
**Implementation**: 10-section sidebar structure: Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options.
**Agent Guidance**: UI components must communicate via API. No direct core access from UI processes.

### CA-9. Observability by Default
**Rule**: No silent failures. All traces must be logged locally via TraceEmitter.
**Implementation**: Every operation must emit trace data. Failures must be visible and actionable.
**Agent Guidance**: Add trace emission to all new operations. Ensure failure modes are observable.

### CA-10. Dependency Injection Only
**Rule**: No global state or context bags. Maximum 15 constructor arguments per component.
**Implementation**: Use constructor injection for all dependencies. Avoid static state or global variables.
**Agent Guidance**: Pass dependencies explicitly via constructors. Keep constructor signatures focused.

### CA-11. Strong and Robust
**Rule**: Fail gracefully, isolate faults, recover without manual intervention.
**Implementation**: Implement fault isolation, automatic recovery, and graceful degradation patterns.
**Agent Guidance**: Design for failure scenarios. Implement automatic recovery where possible.

## Development Principles (DP)

### DP-1. Test-File Creation
**Rule**: Every code file must have accompanying test files created simultaneously.
**Implementation**: When creating implementation files, immediately create corresponding test files with initial test structure.
**Agent Guidance**: Never create implementation files without test files. Test structure should mirror implementation structure.

### DP-2. Modular Functionality
**Rule**: Functions must be modular so that updates to one function don't break others.
**Implementation**: Follow single responsibility principle. Minimize coupling between functions. Use clear interfaces.
**Agent Guidance**: Design functions to be independent. Changes to one function should not require changes to others.

### DP-3. Best Practices Compliance
**Rule**: All code must follow established best practices for the language and framework.
**Implementation**: Reference project-specific style guides and industry standards. Use linting and formatting tools.
**Agent Guidance**: Check existing code patterns before implementing new code. Follow established conventions.

### DP-4. Internal Implementation
**Rule**: Create functionality internally rather than relying on external programs.
**Implementation**: Prefer native implementation over shell commands or external process execution.
**Agent Guidance**: Implement functionality directly in the codebase rather than calling external programs.

## Operational Principles (OP)

### OP-1. Comprehensive Logging
**Rule**: Everything within execution must be logged and categorized.
**Implementation**: Use structured logging with consistent categories. All operations must emit log events.
**Agent Guidance**: Add logging to all operations. Use standardized log categories for consistency.

### OP-2. Best Practices Enforcement
**Rule**: Application must ensure best practices are followed for all components.
**Implementation**: Implement validation and compliance checking. Use automated tools where possible.
**Agent Guidance**: Include validation logic in the application layer. Prevent non-compliant code from executing.

## Deferred Principles (DF)

### DF-1. Security via Reasoning
**Rule**: Security Guard is a user-invoked tool, not an automatic gate.
**Status**: Deferred for future implementation.
**Implementation**: Security analysis should be available on-demand, not blocking normal operations.

### DF-2. Provenance Enforcement
**Rule**: External components must have verifiable provenance.
**Status**: Deferred for future implementation.
**Implementation**: Implement component signing and verification for external plugins and extensions.

---

## Principle Reference Guide

### Quick Reference by Category
- **Core Architecture (CA)**: CA-1 through CA-11 - System design and architecture
- **Development (DP)**: DP-1 through DP-4 - Coding practices and standards  
- **Operational (OP)**: OP-1 through OP-2 - Runtime behavior and logging
- **Deferred (DF)**: DF-1 through DF-2 - Future implementations

### Agent-Specific Reference Mapping
- **Architect Agent**: Focus on CA-1 through CA-11 (Core Architecture)
- **Planner Agent**: Reference all principles for plan alignment
- **Executor Agent**: Focus on DP-1 through DP-4 (Development Principles)
- **Reviewer Agent**: Reference all principles for compliance verification
- **Researcher Agent**: Reference all principles for research context

---

## Principle Maintenance

### Adding New Principles
1. Identify the appropriate category (CA, DP, OP, DF)
2. Assign next sequential number within that category
3. Write clear, agent-understandable language
4. Include implementation guidance for agents
5. Update version number and date
6. Maintain consistent formatting

### Modifying Existing Principles
1. Update version number
2. Document rationale for changes
3. Ensure agent guidance remains clear
4. Update implementation examples if needed
5. Update reference mappings if category changes

### Principle Review
Review principles quarterly for:
- Relevance to current system state
- Clarity for agent understanding
- Completeness of implementation guidance
- Consistency with actual system behavior
- Proper category assignment

---

**Note**: These principles are maintained by the Architect agent and serve as the single source of truth for SovereignAI architectural and operational decisions.
