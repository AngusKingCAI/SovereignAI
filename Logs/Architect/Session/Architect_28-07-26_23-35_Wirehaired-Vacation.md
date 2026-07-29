### SESSION_START
**Timestamp**: 2026-07-28T23:35:32.200917
**Session**: wirehaired-vacation
**Agent**: Architect
**Working Directory**: C:\SovereignAI

---
### USER_PROMPT
**Timestamp**: 2026-07-28T23:35:32.200917
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b

**Prompt**:
```
/architect
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:35:34.933388
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/AGENTS.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/AGENTS.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:35:34.934393
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: skill
**Status**: attempt

**Input**:
```
{
  "command": "invoke",
  "skill": "WorkflowOpen"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:35:35.184103
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: skill
**Status**: success
**Agent**: Architect

**Input**:
```
{
  "command": "invoke",
  "skill": "WorkflowOpen"
}
```

**Output**:
```
The "WorkflowOpen" skill is already running. Complete the current skill's task before invoking it again.
```

**Success**: True
**Tool Use ID**: call_1e718c78df13487680aeb1fb
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "skill",
  "tool_input": {
    "command": "invoke",
    "skill": "WorkflowOpen"
  },
  "tool_use_id": "call_1e718c78df13487680aeb1fb",
  "tool_response": {
    "success": true,
    "output": "The \"WorkflowOpen\" skill is already running. Complete the current skill's task before invoking it again.",
    "error": null
  },
  "session_id": "wirehaired-vacation",
  "prompt_id": "08a0bb9c-98b7-4508-a275-372caee5196b"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:35:37.668936
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/PRINCIPLES.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/PRINCIPLES.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:35:37.669441
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
}
```

---
### TOOL_ATTEMPT
**Timestamp**: 2026-07-28T23:35:37.669441
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: attempt

**Input Summary**: File: C:/SovereignAI/Rules/Architect/Architect_Rules.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Rules/Architect/Architect_Rules.md"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:35:37.841765
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: success
**Agent**: Architect

**Input Summary**: File: C:/SovereignAI/PRINCIPLES.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/PRINCIPLES.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/PRINCIPLES.md" start_line="1" end_line="165" total_lines="165">
  1|# Principles â€” SovereignAI
  2|
  3|**Version**: 3.0  
  4|**Last Updated**: 2026-07-28  
  5|**Maintained By**: Architect Agent  
  6|**Purpose**: Architectural and operational principles that guide SovereignAI development decisions and implementation patterns
  7|
  8|---
  9|
 10|## Overview
 11|
 12|These principles govern the design, implementation, and operation of the SovereignAI system. They serve as the foundation for architectural decisions, development practices, and operational procedures. All agents and developers should reference these principles when making decisions about system changes or implementations.
 13|
 14|## Core Architecture Principles (CA)
 15|
 16|### CA-1. Core is Sacred
 17|**Rule**: The system has exactly 12 core modules. All other functionality must be pluggable.
 18|**Implementation**: Core modules provide essential system services. Any feature outside the core must be implemented as a pluggable component.
 19|**Agent Guidance**: When adding new functionality, always implement as a pluggable component rather than modifying core modules.
 20|
 21|### CA-2. Everything Pluggable
 22|**Rule**: All components are equal and interchangeable: adapters, skills, memory backends, models, UIs.
 23|**Implementation**: Use consistent interfaces and dependency injection. No component should have special privileges or hardcoded dependencies.
 24|**Agent Guidance**: Design new components with standardized interfaces that can be swapped without affecting system operation.
 25|
 26|### CA-3. No Provider Lock-in
 27|**Rule**: System must continue operating if any single component is removed.
 28|**Implementation**: Design for graceful degradation. Components should be hot-swappable without system restart.
 29|**Agent Guidance**: Never create hard dependencies on specific providers. Always allow alternative implementations.
 30|
 31|### CA-4. Local-First
 32|**Rule**: System runs fully offline. Cloud services are optional enhancements, not requirements.
 33|**Implementation**: All core functionality must work without internet connectivity. Cloud features are opt-in escalations.
 34|**Scope**: v1 supports Windows only.
 35|**Agent Guidance**: Implement offline-first. Cloud features should be optional add-ons, not core dependencies.
 36|
 37|### CA-5. Wire as You Go
 38|**Rule**: No speculative contracts or empty placeholder directories.
 39|**Implementation**: Create components only when needed. Avoid premature abstraction or framework code.
 40|**Agent Guidance**: Implement concrete functionality first. Add abstractions only when multiple implementations exist.
 41|
 42|### CA-6. One User, One System
 43|**Rule**: Single user system accessible from anywhere. All UIs connect to the same core.
 44|**Implementation**: Core is user-scoped. Multiple UI clients can connect to the same user's core instance.
 45|**Deferred**: Phone/relay support.
 46|**Agent Guidance**: Design for single-user multi-device access. Core state is per-user, not shared across users.
 47|
 48|### CA-7. Modular Over Simple
 49|**Rule**: Prefer modular, flexible design over simple, monolithic approaches.
 50|**Implementation**: Components should fail independently. System degradation should be graceful, not catastrophic.
 51|**Agent Guidance**: Design for failure isolation. When one component fails, others should continue operating.
 52|
 53|### CA-8. UI Process Separation
 54|**Rule**: UIs are separate processes consuming the capability API via a standardized interface.
 55|**Implementation**: 10-section sidebar structure: Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options.
 56|**Agent Guidance**: UI components must communicate via API. No direct core access from UI processes.
 57|
 58|### CA-9. Observability by Default
 59|**Rule**: No silent failures. All traces must be logged locally via TraceEmitter.
 60|**Implementation**: Every operation must emit trace data. Failures must be visible and actionable.
 61|**Agent Guidance**: Add trace emission to all new operations. Ensure failure modes are observable.
 62|
 63|### CA-10. Dependency Injection Only
 64|**Rule**: No global state or context bags. Maximum 15 constructor arguments per component.
 65|**Implementation**: Use constructor injection for all dependencies. Avoid static state or global variables.
 66|**Agent Guidance**: Pass dependencies explicitly via constructors. Keep constructor signatures focused.
 67|
 68|### CA-11. Strong and Robust
 69|**Rule**: Fail gracefully, isolate faults, recover without manual intervention.
 70|**Implementation**: Implement fault isolation, automatic recovery, and graceful degradation patterns.
 71|**Agent Guidance**: Design for failure scenarios. Implement automatic recovery where possible.
 72|
 73|## Development Principles (DP)
 74|
 75|### DP-1. Test-File Creation
 76|**Rule**: Every code file must have accompanying test files created simultaneously.
 77|**Implementation**: When creating implementation files, immediately create corresponding test files with initial test structure.
 78|**Agent Guidance**: Never create implementation files without test files. Test structure should mirror implementation structure.
 79|
 80|### DP-2. Modular Functionality
 81|**Rule**: Functions must be modular so that updates to one function don't break others.
 82|**Implementation**: Follow single responsibility principle. Minimize coupling between functions. Use clear interfaces.
 83|**Agent Guidance**: Design functions to be independent. Changes to one function should not require changes to others.
 84|
 85|### DP-3. Best Practices Compliance
 86|**Rule**: All code must follow established best practices for the language and framework.
 87|**Implementation**: Reference project-specific style guides and industry standards. Use linting and formatting tools.
 88|**Agent Guidance**: Check existing code patterns before implementing new code. Follow established conventions.
 89|
 90|### DP-4. Internal Implementation
 91|**Rule**: Create functionality internally rather than relying on external programs.
 92|**Implementation**: Prefer native implementation over shell commands or external process execution.
 93|**Agent Guidance**: Implement functionality directly in the codebase rather than calling external programs.
 94|
 95|## Operational Principles (OP)
 96|
 97|### OP-1. Comprehensive Logging
 98|**Rule**: Everything within execution must be logged and categorized.
 99|**Implementation**: Use structured logging with consistent categories. All operations must emit log events.
100|**Agent Guidance**: Add logging to all operations. Use standardized log categories for consistency.
101|
102|### OP-2. Best Practices Enforcement
103|**Rule**: Application must ensure best practices are followed for all components.
104|**Implementation**: Implement validation and compliance checking. Use automated tools where possible.
105|**Agent Guidance**: Include validation logic in the application layer. Prevent non-compliant code from executing.
106|
107|## Deferred Principles (DF)
108|
109|### DF-1. Security via Reasoning
110|**Rule**: Security Guard is a user-invoked tool, not an automatic gate.
111|**Status**: Deferred for future implementation.
112|**Implementation**: Security analysis should be available on-demand, not blocking normal operations.
113|
114|### DF-2. Provenance Enforcement
115|**Rule**: External components must have verifiable provenance.
116|**Status**: Deferred for future implementation.
117|**Implementation**: Implement component signing and verification for external plugins and extensions.
118|
119|---
120|
121|## Principle Reference Guide
122|
123|### Quick Reference by Category
124|- **Core Architecture (CA)**: CA-1 through CA-11 - System design and architecture
125|- **Development (DP)**: DP-1 through DP-4 - Coding practices and standards  
126|- **Operational (OP)**: OP-1 through OP-2 - Runtime behavior and logging
127|- **Deferred (DF)**: DF-1 through DF-2 - Future implementations
128|
129|### Agent-Specific Reference Mapping
130|- **Architect Agent**: Focus on CA-1 through CA-11 (Core Architecture)
131|- **Planner Agent**: Reference all principles for plan alignment
132|- **Executor Agent**: Focus on DP-1 through DP-4 (Development Principles)
133|- **Reviewer Agent**: Reference all principles for compliance verification
134|- **Researcher Agent**: Reference all principles for research context
135|
136|---
137|
138|## Principle Maintenance
139|
140|### Adding New Principles
141|1. Identify the appropriate category (CA, DP, OP, DF)
142|2. Assign next sequential number within that category
143|3. Write clear, agent-understandable language
144|4. Include implementation guidance for agents
145|5. Update version number and date
146|6. Maintain consistent formatting
147|
148|### Modifying Existing Principles
149|1. Update version number
150|2. Document rationale for changes
151|3. Ensure agent guidance remains clear
152|4. Update implementation examples if needed
153|5. Update reference mappings if category changes
154|
155|### Principle Review
156|Review principles quarterly for:
157|- Relevance to current system state
158|- Clarity for agent understanding
159|- Completeness of implementation guidance
160|- Consistency with actual system behavior
161|- Proper category assignment
162|
163|---
164|
165|**Note**: These principles are maintained by the Architect agent and serve as the single source of truth for SovereignAI architectural and operational decisions.
</file-view>
```

**Success**: True
**Tool Use ID**: call_0e625fcbdf31427d9a7f04de
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/PRINCIPLES.md"
  },
  "tool_use_id": "call_0e625fcbdf31427d9a7f04de",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/PRINCIPLES.md\" start_line=\"1\" end_line=\"165\" total_lines=\"165\">\n  1|# Principles \u00e2\u20ac\u201d SovereignAI\n  2|\n  3|**Version**: 3.0  \n  4|**Last Updated**: 2026-07-28  \n  5|**Maintained By**: Architect Agent  \n  6|**Purpose**: Architectural and operational principles that guide SovereignAI development decisions and implementation patterns\n  7|\n  8|---\n  9|\n 10|## Overview\n 11|\n 12|These principles govern the design, implementation, and operation of the SovereignAI system. They serve as the foundation for architectural decisions, development practices, and operational procedures. All agents and developers should reference these principles when making decisions about system changes or implementations.\n 13|\n 14|## Core Architecture Principles (CA)\n 15|\n 16|### CA-1. Core is Sacred\n 17|**Rule**: The system has exactly 12 core modules. All other functionality must be pluggable.\n 18|**Implementation**: Core modules provide essential system services. Any feature outside the core must be implemented as a pluggable component.\n 19|**Agent Guidance**: When adding new functionality, always implement as a pluggable component rather than modifying core modules.\n 20|\n 21|### CA-2. Everything Pluggable\n 22|**Rule**: All components are equal and interchangeable: adapters, skills, memory backends, models, UIs.\n 23|**Implementation**: Use consistent interfaces and dependency injection. No component should have special privileges or hardcoded dependencies.\n 24|**Agent Guidance**: Design new components with standardized interfaces that can be swapped without affecting system operation.\n 25|\n 26|### CA-3. No Provider Lock-in\n 27|**Rule**: System must continue operating if any single component is removed.\n 28|**Implementation**: Design for graceful degradation. Components should be hot-swappable without system restart.\n 29|**Agent Guidance**: Never create hard dependencies on specific providers. Always allow alternative implementations.\n 30|\n 31|### CA-4. Local-First\n 32|**Rule**: System runs fully offline. Cloud services are optional enhancements, not requirements.\n 33|**Implementation**: All core functionality must work without internet connectivity. Cloud features are opt-in escalations.\n 34|**Scope**: v1 supports Windows only.\n 35|**Agent Guidance**: Implement offline-first. Cloud features should be optional add-ons, not core dependencies.\n 36|\n 37|### CA-5. Wire as You Go\n 38|**Rule**: No speculative contracts or empty placeholder directories.\n 39|**Implementation**: Create components only when needed. Avoid premature abstraction or framework code.\n 40|**Agent Guidance**: Implement concrete functionality first. Add abstractions only when multiple implementations exist.\n 41|\n 42|### CA-6. One User, One System\n 43|**Rule**: Single user system accessible from anywhere. All UIs connect to the same core.\n 44|**Implementation**: Core is user-scoped. Multiple UI clients can connect to the same user's core instance.\n 45|**Deferred**: Phone/relay support.\n 46|**Agent Guidance**: Design for single-user multi-device access. Core state is per-user, not shared across users.\n 47|\n 48|### CA-7. Modular Over Simple\n 49|**Rule**: Prefer modular, flexible design over simple, monolithic approaches.\n 50|**Implementation**: Components should fail independently. System degradation should be graceful, not catastrophic.\n 51|**Agent Guidance**: Design for failure isolation. When one component fails, others should continue operating.\n 52|\n 53|### CA-8. UI Process Separation\n 54|**Rule**: UIs are separate processes consuming the capability API via a standardized interface.\n 55|**Implementation**: 10-section sidebar structure: Orchestrator, Workers, Tasks, Skills, Memory, Models, Adapters, Hardware, Logs, Options.\n 56|**Agent Guidance**: UI components must communicate via API. No direct core access from UI processes.\n 57|\n 58|### CA-9. Observability by Default\n 59|**Rule**: No silent failures. All traces must be logged locally via TraceEmitter.\n 60|**Implementation**: Every operation must emit trace data. Failures must be visible and actionable.\n 61|**Agent Guidance**: Add trace emission to all new operations. Ensure failure modes are observable.\n 62|\n 63|### CA-10. Dependency Injection Only\n 64|**Rule**: No global state or context bags. Maximum 15 constructor arguments per component.\n 65|**Implementation**: Use constructor injection for all dependencies. Avoid static state or global variables.\n 66|**Agent Guidance**: Pass dependencies explicitly via constructors. Keep constructor signatures focused.\n 67|\n 68|### CA-11. Strong and Robust\n 69|**Rule**: Fail gracefully, isolate faults, recover without manual intervention.\n 70|**Implementation**: Implement fault isolation, automatic recovery, and graceful degradation patterns.\n 71|**Agent Guidance**: Design for failure scenarios. Implement automatic recovery where possible.\n 72|\n 73|## Development Principles (DP)\n 74|\n 75|### DP-1. Test-File Creation\n 76|**Rule**: Every code file must have accompanying test files created simultaneously.\n 77|**Implementation**: When creating implementation files, immediately create corresponding test files with initial test structure.\n 78|**Agent Guidance**: Never create implementation files without test files. Test structure should mirror implementation structure.\n 79|\n 80|### DP-2. Modular Functionality\n 81|**Rule**: Functions must be modular so that updates to one function don't break others.\n 82|**Implementation**: Follow single responsibility principle. Minimize coupling between functions. Use clear interfaces.\n 83|**Agent Guidance**: Design functions to be independent. Changes to one function should not require changes to others.\n 84|\n 85|### DP-3. Best Practices Compliance\n 86|**Rule**: All code must follow established best practices for the language and framework.\n 87|**Implementation**: Reference project-specific style guides and industry standards. Use linting and formatting tools.\n 88|**Agent Guidance**: Check existing code patterns before implementing new code. Follow established conventions.\n 89|\n 90|### DP-4. Internal Implementation\n 91|**Rule**: Create functionality internally rather than relying on external programs.\n 92|**Implementation**: Prefer native implementation over shell commands or external process execution.\n 93|**Agent Guidance**: Implement functionality directly in the codebase rather than calling external programs.\n 94|\n 95|## Operational Principles (OP)\n 96|\n 97|### OP-1. Comprehensive Logging\n 98|**Rule**: Everything within execution must be logged and categorized.\n 99|**Implementation**: Use structured logging with consistent categories. All operations must emit log events.\n100|**Agent Guidance**: Add logging to all operations. Use standardized log categories for consistency.\n101|\n102|### OP-2. Best Practices Enforcement\n103|**Rule**: Application must ensure best practices are followed for all components.\n104|**Implementation**: Implement validation and compliance checking. Use automated tools where possible.\n105|**Agent Guidance**: Include validation logic in the application layer. Prevent non-compliant code from executing.\n106|\n107|## Deferred Principles (DF)\n108|\n109|### DF-1. Security via Reasoning\n110|**Rule**: Security Guard is a user-invoked tool, not an automatic gate.\n111|**Status**: Deferred for future implementation.\n112|**Implementation**: Security analysis should be available on-demand, not blocking normal operations.\n113|\n114|### DF-2. Provenance Enforcement\n115|**Rule**: External components must have verifiable provenance.\n116|**Status**: Deferred for future implementation.\n117|**Implementation**: Implement component signing and verification for external plugins and extensions.\n118|\n119|---\n120|\n121|## Principle Reference Guide\n122|\n123|### Quick Reference by Category\n124|- **Core Architecture (CA)**: CA-1 through CA-11 - System design and architecture\n125|- **Development (DP)**: DP-1 through DP-4 - Coding practices and standards  \n126|- **Operational (OP)**: OP-1 through OP-2 - Runtime behavior and logging\n127|- **Deferred (DF)**: DF-1 through DF-2 - Future implementations\n128|\n129|### Agent-Specific Reference Mapping\n130|- **Architect Agent**: Focus on CA-1 through CA-11 (Core Architecture)\n131|- **Planner Agent**: Reference all principles for plan alignment\n132|- **Executor Agent**: Focus on DP-1 through DP-4 (Development Principles)\n133|- **Reviewer Agent**: Reference all principles for compliance verification\n134|- **Researcher Agent**: Reference all principles for research context\n135|\n136|---\n137|\n138|## Principle Maintenance\n139|\n140|### Adding New Principles\n141|1. Identify the appropriate category (CA, DP, OP, DF)\n142|2. Assign next sequential number within that category\n143|3. Write clear, agent-understandable language\n144|4. Include implementation guidance for agents\n145|5. Update version number and date\n146|6. Maintain consistent formatting\n147|\n148|### Modifying Existing Principles\n149|1. Update version number\n150|2. Document rationale for changes\n151|3. Ensure agent guidance remains clear\n152|4. Update implementation examples if needed\n153|5. Update reference mappings if category changes\n154|\n155|### Principle Review\n156|Review principles quarterly for:\n157|- Relevance to current system state\n158|- Clarity for agent understanding\n159|- Completeness of implementation guidance\n160|- Consistency with actual system behavior\n161|- Proper category assignment\n162|\n163|---\n164|\n165|**Note**: These principles are maintained by the Architect agent and serve as the single source of truth for SovereignAI architectural and operational decisions.\n</file-view>",
    "error": null
  },
  "session_id": "wirehaired-vacation",
  "prompt_id": "08a0bb9c-98b7-4508-a275-372caee5196b"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:35:37.958575
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: success
**Agent**: Architect

**Input Summary**: File: C:/SovereignAI/Rules/Architect/Architect_Rules.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Rules/Architect/Architect_Rules.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Rules/Architect/Architect_Rules.md" start_line="1" end_line="137" total_lines="137">
  1|---
  2|id: architect-rules
  3|status: active
  4|owner: architect-agent
  5|updated: 2026-07-28
  6|purpose: Declarative policy for Architect agent governance and implementation
  7|---
  8|
  9|# Architect Agent Rules
 10|
 11|## Overview
 12|Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).
 13|
 14|## Conventions
 15|
 16|- **Best Practices**: Web search must be used before implementing major architectural decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding.
 17|- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)
 18|- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)
 19|- Answer questions first when user requests end with "?". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)
 20|- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)
 21|- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)
 22|
 23|## Execution Modes
 24|
 25|Three execution modes govern workflow behavior when encountering failures:
 26|
 27|- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort
 28|- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored
 29|- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status
 30|
 31|## Constraints
 32|
 33|- **Consistency Prevention**: Never create index.md files or manual navigation files. Rely on STRUCTURE.md as the single source of truth for structure and schema validation for automated enforcement (prevents maintenance overhead, eliminates index drift, aligns with SSOT principles)
 34|- **Consistency Prevention**: Never add YAML frontmatter patterns to schema validation rules that create redundant sources of truth. Files themselves should be the source of truth, not separate index files (prevents dual maintenance, aligns with principle of locality)
 35|- **Consistency Prevention**: When updating schema validation rules, always check for consistency with existing file patterns. Never add patterns that would allow files to be placed in multiple locations without clear purpose (prevents ambiguity, maintains clear ownership boundaries)
 36|- **Consistency Prevention**: Always run schema validation script after making structural changes. Never assume changes are correct without verification (ensures architectural integrity, prevents introducing validation failures)
 37|- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)
 38|- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)
 39|- Check local research using index files when function fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)
 40|- Place scripts in Scripts/<Category>/ folder matching primary function. Never create ad-hoc folders or place outside established categories (maintains organization, prevents file chaos)
 41|- Place IDE harness tests in Scripts/Tests/ folder only. Never place IDE harness tests in App/ directory (maintains clear separation between application code and harness infrastructure)
 42|- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)
 43|- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)
 44|- Never place files directly in Docs/ root directory. Always use agent-specific subdirectories (Docs/{Agent}/) or universal categories (Docs/{Category}/) (maintains documentation organization, prevents file chaos)
 45|- Never skip compliance checks. Always verify architectural compliance before proceeding (ensures quality, prevents rule violations)
 46|- Never reference or modify App/ directory (reference only for application context, prevents scope creep into implementation)
 47|- Never test governance systems in isolated environments. Always test in actual project context with real tool executions (ensures real-world functionality, prevents false confidence)
 48|- Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)
 49|- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)
 50|- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)
 51|- When creating new directories or subdirectories in Scripts/, Workflow/, Rules/, or .devin/, immediately update Scripts/Schema/validate_schemas.py to include the new directory structure in CATEGORIZATION_RULES (maintains schema validation accuracy, prevents false positive validation failures)
 52|- When creating new governance files (Workflow/, Rules/, .devin/), add appropriate YAML frontmatter with required fields (id, status, owner, updated, purpose) to enable automated schema validation (enables governance automation, prevents validation noise)
 53|- Always create appropriate category subdirectories when adding files to Scripts/, Workflow/, Rules/, Docs/, or .devin/ (follows universal categorization principle, prevents file chaos)
 54|- Always place logs in their relevant Agent folder (Logs/{Agent}/) first, then create category subdirectories within agent folders (maintains log organization, prevents log chaos)
 55|- Never create log folders at Logs/ root level without agent context (strict log placement rule, maintains architectural boundaries)
 56|- When archiving logs, use Logs/.Archived/{Category}/ with appropriate subdirectories (maintains archive organization, enables proper log lifecycle management)
 57|
 58|## Architecture
 59|
 60|- Infrastructure-first architecture: Authority lives in deterministic software, intelligence lives in agents (maintains architectural purity, enables predictable governance)
 61|- Default script categories: Schema/, Infrastructure/, Testing/, Build/, Deployment/, Maintenance/, Utilities/, Logging/, Analysis/, Misc/, Tests/. Create new categories when no existing category matches the script's primary function or intent (maintains organizational clarity while allowing necessary evolution, aligns with intent-first categorization)
 62|- Governance file locations: Agents/ for other agents' governance files, Rules/ for rule definitions, Workflow/ for workflow definitions, Scripts/ for implementation scripts, Docs/ for documentation (maintains SSOT, enables clear ownership boundaries)
 63|- Universal categorization principle: Every file must be placed in an appropriate category subdirectory matching its purpose (prevents file chaos, enables efficient navigation)
 64|- Log placement governance: All logs must be in their relevant Agent folder (Logs/{Agent}/) with category subdirectories within (maintains log organization, prevents log chaos)
 65|
 66|## Tool Configuration
 67|
 68|- Directory verification: `ls -la <directory>` (verify directory structure exists)
 69|- File discovery: `find <path> -name "*.md"` (find markdown governance files)
 70|- Pattern search: `grep -r "pattern" <directory>` (search for patterns in rule files)
 71|- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)
 72|- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)
 73|- Schema validation: `python Scripts/Schema/validate_schemas.py` (validate governance file schemas and categorization, exit code indicates success/failure)
 74|
 75|## Project Structure
 76|
 77|- `Agents/` â€“ Other agents' governance files (EDIT these to enforce standards)
 78|  - `Agents/Architect/` â€“ Architect agent governance
 79|  - `Agents/Planner/` â€“ Planner agent governance
 80|  - `Agents/Executor/` â€“ Executor agent governance
 81|  - `Agents/Researcher/` â€“ Researcher agent governance
 82|  - `Agents/Reviewer/` â€“ Reviewer agent governance
 83|- `Rules/` â€“ Rule definitions for all agents (EDIT these to maintain compliance)
 84|  - `Rules/Architect/` â€“ Architect rules
 85|  - `Rules/Planner/` â€“ Planner rules
 86|  - `Rules/Executor/` â€“ Executor rules
 87|  - `Rules/Researcher/` â€“ Researcher rules
 88|  - `Rules/Reviewer/` â€“ Reviewer rules
 89|- `Workflow/` â€“ Workflow definitions for all agents (EDIT these to enforce processes)
 90|  - `Workflow/Architect/` â€“ Architect workflows
 91|  - `Workflow/Planner/` â€“ Planner workflows
 92|  - `Workflow/Executor/` â€“ Executor workflows
 93|  - `Workflow/Researcher/` â€“ Researcher workflows
 94|  - `Workflow/Reviewer/` â€“ Reviewer workflows
 95|  - `Workflow/Workflow_Reference/` â€“ Universal frameworks
 96|- `Scripts/` â€“ Implementation scripts organized by category (WRITE scripts here)
 97|  - `Schema/` â€“ Schema validation scripts
 98|  - `Infrastructure/` â€“ Infrastructure automation scripts
 99|  - `Testing/` â€“ Testing scripts
100|  - `Build/` â€“ Build scripts
101|  - `Deployment/` â€“ Deployment scripts
102|  - `Maintenance/` â€“ Maintenance scripts
103|  - `Utilities/` â€“ Utilities scripts
104|  - `Logging/` â€“ Logging scripts
105|  - `Analysis/` â€“ Analysis scripts
106|  - `Misc/` â€“ Miscellaneous scripts
107|  - `Tests/` â€“ Test files
108|- `Docs/` â€“ Documentation and research (organize by agent type and category)
109|  - `Docs/Architect/` â€“ Architect documentation
110|  - `Docs/Planner/` â€“ Planner documentation
111|  - `Docs/Executor/` â€“ Executor documentation
112|  - `Docs/Researcher/` â€“ Researcher documentation
113|  - `Docs/Reviewer/` â€“ Reviewer documentation
114|  - Universal categories:
115|    - `Code/` â€“ Code documentation
116|    - `Research/` â€“ Research documentation
117|    - `Architecture/` â€“ Architecture documentation
118|    - `Governance/` â€“ Governance documentation
119|    - `Repository/` â€“ Repository documentation
120|    - `Devin Local IDE Documents/` â€“ Devin CLI documentation
121|    - `External AI Reviews/` â€“ External AI review documentation
122|    - `Sovereign AI Design Docs/` â€“ Sovereign AI design documentation
123|- `.devin/` â€“ Devin CLI configuration, skills, and hooks (EDIT to maintain harness)
124|  - `skills/architect/` â€“ Architect skill
125|  - `skills/planner/` â€“ Planner skill
126|  - `skills/executor/` â€“ Executor skill
127|  - `skills/researcher/` â€“ Researcher skill
128|  - `skills/reviewer/` â€“ Reviewer skill
129|- `Logs/` â€“ Agent logs and conversation history (organize by agent)
130|  - `Logs/Architect/` â€“ Architect logs
131|  - `Logs/Planner/` â€“ Planner logs
132|  - `Logs/Executor/` â€“ Executor logs
133|  - `Logs/Researcher/` â€“ Researcher logs
134|  - `Logs/Reviewer/` â€“ Reviewer logs
135|  - `Logs/.Archived/` â€“ Archived logs
136|- `Plans/` â€“ Project planning documents
137|- `App/` â€“ SovereignAI application code (reference only)
</file-view>
```

**Success**: True
**Tool Use ID**: call_d6236cf84ebf4814a03eaa33
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Rules/Architect/Architect_Rules.md"
  },
  "tool_use_id": "call_d6236cf84ebf4814a03eaa33",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Rules/Architect/Architect_Rules.md\" start_line=\"1\" end_line=\"137\" total_lines=\"137\">\n  1|---\n  2|id: architect-rules\n  3|status: active\n  4|owner: architect-agent\n  5|updated: 2026-07-28\n  6|purpose: Declarative policy for Architect agent governance and implementation\n  7|---\n  8|\n  9|# Architect Agent Rules\n 10|\n 11|## Overview\n 12|Declarative policy for Architect agent implementation following infrastructure-first principles. Rules are organized into Conventions (behavioral guidance) and Constraints (hard boundaries).\n 13|\n 14|## Conventions\n 15|\n 16|- **Best Practices**: Web search must be used before implementing major architectural decisions or when uncertain about implementation approaches. Best practices are established industry standards that must be researched before proceeding.\n 17|- Check code documentation (Docs/Code/) before web searching (reduces token cost, prioritizes local knowledge)\n 18|- Present function and test result after each successful test. Wait for user confirmation before proceeding (ensures quality control, prevents cascading errors)\n 19|- Answer questions first when user requests end with \"?\". Ask for permission before making changes after answering (ensures user understanding, prevents unintended modifications)\n 20|- Use capital letters at the start of items unless lowercase is needed (maintains consistency, improves readability)\n 21|- All **{CAPITALIZED}** commands and terms are defined in Workflow/Workflow_Reference/Terminology_Glossary.md (SSOT for terminology)\n 22|\n 23|## Execution Modes\n 24|\n 25|Three execution modes govern workflow behavior when encountering failures:\n 26|\n 27|- **Manual**: Stop at failures for human oversight - workflow halts at any failure point and awaits user intervention to decide on retry, modification, or abort\n 28|- **Auto**: Don't continue on failures - workflow automatically stops on any failure without requiring human intervention, ensuring errors are not silently ignored\n 29|- **Complete**: Continue past failures - workflow automatically continues through all failures, ignoring errors to reach completion regardless of success/failure status\n 30|\n 31|## Constraints\n 32|\n 33|- **Consistency Prevention**: Never create index.md files or manual navigation files. Rely on STRUCTURE.md as the single source of truth for structure and schema validation for automated enforcement (prevents maintenance overhead, eliminates index drift, aligns with SSOT principles)\n 34|- **Consistency Prevention**: Never add YAML frontmatter patterns to schema validation rules that create redundant sources of truth. Files themselves should be the source of truth, not separate index files (prevents dual maintenance, aligns with principle of locality)\n 35|- **Consistency Prevention**: When updating schema validation rules, always check for consistency with existing file patterns. Never add patterns that would allow files to be placed in multiple locations without clear purpose (prevents ambiguity, maintains clear ownership boundaries)\n 36|- **Consistency Prevention**: Always run schema validation script after making structural changes. Never assume changes are correct without verification (ensures architectural integrity, prevents introducing validation failures)\n 37|- Build exactly one function at a time. Test immediately. Never write a second function before first is tested (ensures modular validation, prevents hidden bugs)\n 38|- Treat user-confirmed functions as locked. Never modify without explicit user permission (maintains stability, prevents unintended changes)\n 39|- Check local research using index files when function fails. Web search only if local info unavailable. Never retry blindly without research (reduces token cost, ensures correct implementation)\n 40|- Place scripts in Scripts/<Category>/ folder matching primary function. Never create ad-hoc folders or place outside established categories (maintains organization, prevents file chaos)\n 41|- Place IDE harness tests in Scripts/Tests/ folder only. Never place IDE harness tests in App/ directory (maintains clear separation between application code and harness infrastructure)\n 42|- Always use popups for yes/no questions. Never use text-only confirmations (ensures clear user intent, prevents miscommunication)\n 43|- Always categorize files when adding to documentation directories. Never place files uncategorized (maintains organization, enables efficient navigation)\n 44|- Never place files directly in Docs/ root directory. Always use agent-specific subdirectories (Docs/{Agent}/) or universal categories (Docs/{Category}/) (maintains documentation organization, prevents file chaos)\n 45|- Never skip compliance checks. Always verify architectural compliance before proceeding (ensures quality, prevents rule violations)\n 46|- Never reference or modify App/ directory (reference only for application context, prevents scope creep into implementation)\n 47|- Never test governance systems in isolated environments. Always test in actual project context with real tool executions (ensures real-world functionality, prevents false confidence)\n 48|- Never perform actions outside workflow scope. Always follow defined workflow processes and never perform tasks outside the current workflow scope unless explicitly requested by the user (prevents token waste, ensures focused execution)\n 49|- Never create documentation files unless specifically requested. Never create README.md, CHANGELOG.md, or other documentation files unless specifically requested by the user (prevents token waste, maintains workflow scope discipline)\n 50|- Never run subagents unless explicitly requested by the user. Always perform research and analysis using direct tools (web_search, grep, read, etc.) unless user specifically requests subagent delegation (prevents unexpected subagent usage, maintains user control over execution)\n 51|- When creating new directories or subdirectories in Scripts/, Workflow/, Rules/, or .devin/, immediately update Scripts/Schema/validate_schemas.py to include the new directory structure in CATEGORIZATION_RULES (maintains schema validation accuracy, prevents false positive validation failures)\n 52|- When creating new governance files (Workflow/, Rules/, .devin/), add appropriate YAML frontmatter with required fields (id, status, owner, updated, purpose) to enable automated schema validation (enables governance automation, prevents validation noise)\n 53|- Always create appropriate category subdirectories when adding files to Scripts/, Workflow/, Rules/, Docs/, or .devin/ (follows universal categorization principle, prevents file chaos)\n 54|- Always place logs in their relevant Agent folder (Logs/{Agent}/) first, then create category subdirectories within agent folders (maintains log organization, prevents log chaos)\n 55|- Never create log folders at Logs/ root level without agent context (strict log placement rule, maintains architectural boundaries)\n 56|- When archiving logs, use Logs/.Archived/{Category}/ with appropriate subdirectories (maintains archive organization, enables proper log lifecycle management)\n 57|\n 58|## Architecture\n 59|\n 60|- Infrastructure-first architecture: Authority lives in deterministic software, intelligence lives in agents (maintains architectural purity, enables predictable governance)\n 61|- Default script categories: Schema/, Infrastructure/, Testing/, Build/, Deployment/, Maintenance/, Utilities/, Logging/, Analysis/, Misc/, Tests/. Create new categories when no existing category matches the script's primary function or intent (maintains organizational clarity while allowing necessary evolution, aligns with intent-first categorization)\n 62|- Governance file locations: Agents/ for other agents' governance files, Rules/ for rule definitions, Workflow/ for workflow definitions, Scripts/ for implementation scripts, Docs/ for documentation (maintains SSOT, enables clear ownership boundaries)\n 63|- Universal categorization principle: Every file must be placed in an appropriate category subdirectory matching its purpose (prevents file chaos, enables efficient navigation)\n 64|- Log placement governance: All logs must be in their relevant Agent folder (Logs/{Agent}/) with category subdirectories within (maintains log organization, prevents log chaos)\n 65|\n 66|## Tool Configuration\n 67|\n 68|- Directory verification: `ls -la <directory>` (verify directory structure exists)\n 69|- File discovery: `find <path> -name \"*.md\"` (find markdown governance files)\n 70|- Pattern search: `grep -r \"pattern\" <directory>` (search for patterns in rule files)\n 71|- JSON validation: `python -m json.tool <file>` (validate JSON syntax, exit code indicates success/failure)\n 72|- File comparison: `diff <file1> <file2>` (compare files before changes, exit code 0 = identical)\n 73|- Schema validation: `python Scripts/Schema/validate_schemas.py` (validate governance file schemas and categorization, exit code indicates success/failure)\n 74|\n 75|## Project Structure\n 76|\n 77|- `Agents/` \u00e2\u20ac\u201c Other agents' governance files (EDIT these to enforce standards)\n 78|  - `Agents/Architect/` \u00e2\u20ac\u201c Architect agent governance\n 79|  - `Agents/Planner/` \u00e2\u20ac\u201c Planner agent governance\n 80|  - `Agents/Executor/` \u00e2\u20ac\u201c Executor agent governance\n 81|  - `Agents/Researcher/` \u00e2\u20ac\u201c Researcher agent governance\n 82|  - `Agents/Reviewer/` \u00e2\u20ac\u201c Reviewer agent governance\n 83|- `Rules/` \u00e2\u20ac\u201c Rule definitions for all agents (EDIT these to maintain compliance)\n 84|  - `Rules/Architect/` \u00e2\u20ac\u201c Architect rules\n 85|  - `Rules/Planner/` \u00e2\u20ac\u201c Planner rules\n 86|  - `Rules/Executor/` \u00e2\u20ac\u201c Executor rules\n 87|  - `Rules/Researcher/` \u00e2\u20ac\u201c Researcher rules\n 88|  - `Rules/Reviewer/` \u00e2\u20ac\u201c Reviewer rules\n 89|- `Workflow/` \u00e2\u20ac\u201c Workflow definitions for all agents (EDIT these to enforce processes)\n 90|  - `Workflow/Architect/` \u00e2\u20ac\u201c Architect workflows\n 91|  - `Workflow/Planner/` \u00e2\u20ac\u201c Planner workflows\n 92|  - `Workflow/Executor/` \u00e2\u20ac\u201c Executor workflows\n 93|  - `Workflow/Researcher/` \u00e2\u20ac\u201c Researcher workflows\n 94|  - `Workflow/Reviewer/` \u00e2\u20ac\u201c Reviewer workflows\n 95|  - `Workflow/Workflow_Reference/` \u00e2\u20ac\u201c Universal frameworks\n 96|- `Scripts/` \u00e2\u20ac\u201c Implementation scripts organized by category (WRITE scripts here)\n 97|  - `Schema/` \u00e2\u20ac\u201c Schema validation scripts\n 98|  - `Infrastructure/` \u00e2\u20ac\u201c Infrastructure automation scripts\n 99|  - `Testing/` \u00e2\u20ac\u201c Testing scripts\n100|  - `Build/` \u00e2\u20ac\u201c Build scripts\n101|  - `Deployment/` \u00e2\u20ac\u201c Deployment scripts\n102|  - `Maintenance/` \u00e2\u20ac\u201c Maintenance scripts\n103|  - `Utilities/` \u00e2\u20ac\u201c Utilities scripts\n104|  - `Logging/` \u00e2\u20ac\u201c Logging scripts\n105|  - `Analysis/` \u00e2\u20ac\u201c Analysis scripts\n106|  - `Misc/` \u00e2\u20ac\u201c Miscellaneous scripts\n107|  - `Tests/` \u00e2\u20ac\u201c Test files\n108|- `Docs/` \u00e2\u20ac\u201c Documentation and research (organize by agent type and category)\n109|  - `Docs/Architect/` \u00e2\u20ac\u201c Architect documentation\n110|  - `Docs/Planner/` \u00e2\u20ac\u201c Planner documentation\n111|  - `Docs/Executor/` \u00e2\u20ac\u201c Executor documentation\n112|  - `Docs/Researcher/` \u00e2\u20ac\u201c Researcher documentation\n113|  - `Docs/Reviewer/` \u00e2\u20ac\u201c Reviewer documentation\n114|  - Universal categories:\n115|    - `Code/` \u00e2\u20ac\u201c Code documentation\n116|    - `Research/` \u00e2\u20ac\u201c Research documentation\n117|    - `Architecture/` \u00e2\u20ac\u201c Architecture documentation\n118|    - `Governance/` \u00e2\u20ac\u201c Governance documentation\n119|    - `Repository/` \u00e2\u20ac\u201c Repository documentation\n120|    - `Devin Local IDE Documents/` \u00e2\u20ac\u201c Devin CLI documentation\n121|    - `External AI Reviews/` \u00e2\u20ac\u201c External AI review documentation\n122|    - `Sovereign AI Design Docs/` \u00e2\u20ac\u201c Sovereign AI design documentation\n123|- `.devin/` \u00e2\u20ac\u201c Devin CLI configuration, skills, and hooks (EDIT to maintain harness)\n124|  - `skills/architect/` \u00e2\u20ac\u201c Architect skill\n125|  - `skills/planner/` \u00e2\u20ac\u201c Planner skill\n126|  - `skills/executor/` \u00e2\u20ac\u201c Executor skill\n127|  - `skills/researcher/` \u00e2\u20ac\u201c Researcher skill\n128|  - `skills/reviewer/` \u00e2\u20ac\u201c Reviewer skill\n129|- `Logs/` \u00e2\u20ac\u201c Agent logs and conversation history (organize by agent)\n130|  - `Logs/Architect/` \u00e2\u20ac\u201c Architect logs\n131|  - `Logs/Planner/` \u00e2\u20ac\u201c Planner logs\n132|  - `Logs/Executor/` \u00e2\u20ac\u201c Executor logs\n133|  - `Logs/Researcher/` \u00e2\u20ac\u201c Researcher logs\n134|  - `Logs/Reviewer/` \u00e2\u20ac\u201c Reviewer logs\n135|  - `Logs/.Archived/` \u00e2\u20ac\u201c Archived logs\n136|- `Plans/` \u00e2\u20ac\u201c Project planning documents\n137|- `App/` \u00e2\u20ac\u201c SovereignAI application code (reference only)\n</file-view>",
    "error": null
  },
  "session_id": "wirehaired-vacation",
  "prompt_id": "08a0bb9c-98b7-4508-a275-372caee5196b"
}
```

---
### TOOL_ACTION
**Timestamp**: 2026-07-28T23:35:38.078336
**Session**: wirehaired-vacation
**Prompt ID**: 08a0bb9c-98b7-4508-a275-372caee5196b
**Tool**: read
**Status**: success
**Agent**: Architect

**Input Summary**: File: C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md
**Input**:
```
{
  "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
}
```

**Output**:
```
<file-view path="C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md" start_line="1" end_line="360" total_lines="360">
  1|---
  2|id: wf-ref-terminology
  3|status: active
  4|owner: architect-agent
  5|updated: 2026-07-28
  6|purpose: Single source of truth for all capitalized terminology used across the SovereignAI harness architecture
  7|---
  8|
  9|# SovereignAI Harness Terminology Glossary
 10|
 11|**Purpose**: Single source of truth (SSOT) for all capitalized terminology used across the SovereignAI harness architecture. This glossary ensures consistent understanding of governance terminology across all agents and workflows.
 12|
 13|**Governance**: This document is maintained by the Architect agent and serves as the authoritative source for terminology definitions. All agents must reference this glossary for terminology understanding.
 14|
 15|---
 16|
 17|## Core Workflow Commands
 18|
 19|### **SCAN**
 20|**Definition**: Examine all documents within scope line by line without skipping anything - comprehensive examination required for governance compliance.
 21|
 22|**Usage**: Used when comprehensive examination of documents is required for governance compliance, quality assurance, or consistency verification. This is the primary scanning method and cannot be replaced by pattern matching tools like grep.
 23|
 24|**Examples**:
 25|- **SCAN** all harness architecture files for consistency checks
 26|- **SCAN** App/ directory line by line for compliance verification
 27|- **SCAN** workflow files to validate template compliance
 28|
 29|---
 30|
 31|### **PRINT**
 32|**Definition**: Output text to chat interface for user visibility (not to files or logs).
 33|
 34|**Usage**: Used to communicate workflow status, progress updates, and important information to the user during workflow execution. This command does not write to files or logs.
 35|
 36|**Examples**:
 37|- **PRINT** "Workflow initialization complete"
 38|- **PRINT** "Scan strategy selected - Full Comprehensive"
 39|- **PRINT** "Consistency check complete - 0 issues found"
 40|
 41|---
 42|
 43|### **VALIDATION**
 44|**Definition**: Validate step completion before proceeding to next phase.
 45|
 46|**Usage**: Used to ensure that workflow steps have completed successfully and meet quality criteria before moving to the next phase. This is a quality validation mechanism.
 47|
 48|**Examples**:
 49|- **VALIDATION**: Validate file reference extraction completed successfully
 50|- **VALIDATION**: Validate workflow structure check completed successfully
 51|- **VALIDATION**: Validate that all referenced files exist
 52|
 53|---
 54|
 55|### **STATUS TRACKING**
 56|**Definition**: Update workflow status for monitoring and recovery.
 57|
 58|**Usage**: Used to track workflow progress, enable recovery from failures, and provide visibility into workflow execution state. Status updates are typically written to workflow_state.json or similar tracking mechanisms.
 59|
 60|**Examples**:
 61|- **STATUS TRACKING**: Update workflow status to "phase_0_complete"
 62|- **STATUS TRACKING**: Update workflow status to "phase_3_in_progress"
 63|- **STATUS TRACKING**: Update workflow status to "phase_7_complete"
 64|
 65|---
 66|
 67|### **TERMINATE**
 68|**Definition**: End workflow execution (do not return to step 1).
 69|
 70|**Usage**: Used in single-execution workflows to signal completion and prevent automatic looping. This is the workflow termination command for utility workflows.
 71|
 72|**Examples**:
 73|- **TERMINATE**: End workflow execution (do not return to step 1)
 74|- **TERMINATE**: Workflow execution complete - workflow terminated
 75|
 76|---
 77|
 78|## Workflow-Specific Commands
 79|
 80|### **EXECUTION MODE HANDLING**
 81|**Definition**: Apply execution mode handling patterns based on selected mode (Manual/Auto/Complete).
 82|
 83|**Usage**: Used to determine how the workflow should respond to failures based on the user-selected execution mode.
 84|
 85|**Modes**:
 86|- **Manual**: Stop at failures for human oversight
 87|- **Auto**: Don't continue on failures (auto-stop on errors)
 88|- **Complete**: Continue past failures (ignore all errors)
 89|
 90|**Examples**:
 91|- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns
 92|- **EXECUTION MODE HANDLING**: Apply review mode handling patterns
 93|
 94|---
 95|
 96|### **CONVERGENCE CHECK**
 97|**Definition**: Verify panelist scores against quality thresholds.
 98|
 99|**Usage**: Used in Round Table review processes to determine if panelists have reached agreement on quality assessments.
100|
101|**Thresholds**:
102|- Clean pass: â‰¥4.5 score
103|- Acceptable pass: 3.5-4.4 score with documented rationale
104|- Fail: <3.5 score
105|
106|**Examples**:
107|- **CONVERGENCE CHECK**: Check if all panelists chose PASS (â‰¥4.5 score or 3.5-4.4 with rationale)
108|- **CONVERGENCE CHECK**: Verify convergence criteria met
109|
110|---
111|
112|### **QUOTA AWARENESS**
113|**Definition**: Monitor internal subagent quota usage for recovery tracking.
114|
115|**Usage**: Used to track subagent resource consumption and enable recovery if quota limits are approached or exceeded.
116|
117|**Examples**:
118|- **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress
119|- **QUOTA AWARENESS**: Track quota usage for recovery if needed
120|
121|---
122|
123|### **LOOP DECISION**
124|**Definition**: Determine workflow continuation based on conditions.
125|
126|**Usage**: Used to control workflow flow and determine whether to loop back to previous phases or proceed forward.
127|
128|**Examples**:
129|- **LOOP DECISION**: If more plan steps remain â†’ Return to step 25 with next step
130|- **LOOP BACK**: Return to Phase 4 for next iteration
131|
132|---
133|
134|### **HANDOFF VALIDATION**
135|**Definition**: Verify handoff file integrity and completeness.
136|
137|**Usage**: Used when transferring work between agents to ensure all required information is present and accessible.
138|
139|**Examples**:
140|- **HANDOFF VALIDATION**: Verify handoff file integrity per template requirements
141|- **HANDOFF VALIDATION**: Validate all required fields are present
142|
143|---
144|
145|## Decision and Planning Commands
146|
147|### **ARCHITECT OPINION**
148|**Definition**: Provide analysis and recommendation BEFORE user selection.
149|
150|**Usage**: Used by Architect agent to provide expert analysis and recommendations when presenting implementation options to users.
151|
152|**Examples**:
153|- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection
154|- **ARCHITECT OPINION**: Recommend optimal approach based on analysis
155|
156|---
157|
158|### **PRESENTATION PATTERN**
159|**Definition**: Present options with metrics, provide architect opinion, use popup menu for selection.
160|
161|**Usage**: Used to standardize how options are presented to users, ensuring consistent format and decision-making process.
162|
163|**Examples**:
164|- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu
165|- **PRESENTATION PATTERN**: Use popup menu for selection
166|
167|---
168|
169|### **RULE ENFORCEMENT**
170|**Definition**: Ensure options comply with agent rules.
171|
172|**Usage**: Used to validate that proposed options or approaches comply with the relevant agent's governance rules.
173|
174|**Examples**:
175|- **RULE ENFORCEMENT**: Ensure options comply with Architect rules
176|- **RULE ENFORCEMENT**: Validate compliance with governance constraints
177|
178|---
179|
180|### **SPECIFICATION CONFIRMATION**
181|**Definition**: Ask user to confirm specification or request modifications using popup menu.
182|
183|**Usage**: Used to get user approval on detailed specifications before proceeding with implementation.
184|
185|**Examples**:
186|- **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications
187|- **SPECIFICATION CONFIRMATION**: Use popup menu with [Confirm/Modify] options
188|
189|---
190|
191|### **IMPLEMENTATION MODE SELECTION**
192|**Definition**: Ask user to choose implementation mode using popup menu.
193|
194|**Usage**: Used to determine whether implementation should be automated or manual based on user preference.
195|
196|**Examples**:
197|- **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu
198|- **IMPLEMENTATION MODE SELECTION**: Select automated vs manual implementation
199|
200|---
201|
202|## Information and Notes
203|
204|### **AUTOMATED PROGRESSION NOTE**
205|**Definition**: Validation system behavior notes for context.
206|
207|**Usage**: Used to provide explanatory notes about how the validation system behaves in specific situations.
208|
209|**Examples**:
210|- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools automatically during this step
211|- **AUTOMATED PROGRESSION NOTE**: User confirmation requests use ask_user_question for approval without triggering failure intervention
212|
213|---
214|
215|### **IMPORTANT**
216|**Definition**: Important notes that require attention but are not critical failures.
217|
218|**Usage**: Used to highlight important information that users should be aware of during workflow execution.
219|
220|**Examples**:
221|- **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing
222|- **IMPORTANT**: Hook file changes require Devin CLI restart
223|
224|---
225|
226|## Severity and Priority Markers
227|
228|### **CRITICAL**
229|**Definition**: Critical issues or required actions that must be addressed immediately.
230|
231|**Usage**: Used to mark issues that require immediate attention or actions that are mandatory for workflow success.
232|
233|**Examples**:
234|- **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies)
235|- **CRITICAL**: Hook file changes require Devin CLI restart before testing
236|
237|---
238|
239|### **HIGH**
240|**Definition**: High priority issues that should be addressed soon.
241|
242|**Usage**: Used to mark significant issues that should be resolved but are not immediately blocking.
243|
244|**Examples**:
245|- **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity)
246|- **HIGH**: High priority issues requiring attention
247|
248|---
249|
250|### **MEDIUM**
251|**Definition**: Medium priority issues for improvement.
252|
253|**Usage**: Used to mark issues that represent improvements but are not urgent.
254|
255|**Examples**:
256|- **MEDIUM**: Best practices improvements (code readability, maintainability)
257|- **MEDIUM**: Medium priority issues for improvement
258|
259|---
260|
261|### **LOW**
262|**Definition**: Low priority minor suggestions.
263|
264|**Usage**: Used to mark minor suggestions or improvements that are optional.
265|
266|**Examples**:
267|- **LOW**: Minor suggestions (comments, formatting)
268|- **LOW**: Low priority issues for consideration
269|
270|---
271|
272|## Governance Terms
273|
274|### **BP** (Best Practice)
275|**Definition**: Established industry standards that must be researched before proceeding with major decisions.
276|
277|**Usage**: Used to indicate when web search for current best practices is required before making architectural or implementation decisions.
278|
279|**Examples**:
280|- **BP**: Web search for best practices before major architectural decisions
281|- **BP**: Research industry standards before implementation
282|
283|**Implementation**: When user input is "BP?" (Best Practice?), perform web search for current best practices relevant to the task at hand.
284|
285|---
286|
287|### **SSOT** (Single Source of Truth)
288|**Definition**: Centralized repository for authoritative information that eliminates duplication and inconsistencies.
289|
290|**Usage**: Used to indicate the authoritative source for specific information, ensuring all agents reference the same accurate data.
291|
292|**Examples**:
293|- **SSOT**: Workflow/Terminology_Glossary.md is the SSOT for terminology definitions
294|- **SSOT**: INDEX.md is the SSOT for directory structure information
295|
296|**Best Practice**: Establish SSOT for critical information to prevent inconsistencies and ensure all stakeholders work from the same data.
297|
298|---
299|
300|## Standard Terms
301|
302|### **ID**
303|**Definition**: Unique identifier for workflows, documents, or entities.
304|
305|**Usage**: Used to provide unique identification for workflows, documents, and other entities within the harness architecture.
306|
307|**Examples**:
308|- **ID**: WF-ARCH-001
309|- **ID**: WF-PLAN-001
310|
311|---
312|
313|### **DO**
314|**Definition**: Required actions that must be performed according to rules.
315|
316|**Usage**: Used in rule files to specify mandatory actions that agents must perform.
317|
318|**Examples**:
319|- **DO**: Verify each function follows single responsibility principle
320|- **DO**: Check that functions have clear inputs and outputs
321|
322|---
323|
324|## Terminology Governance
325|
326|### Glossary Maintenance
327|- **Owner**: Architect Agent
328|- **Update Process**: Architect agent reviews and updates glossary based on new terminology needs
329|- **Version Control**: All changes tracked with version history
330|- **Approval**: Architect agent approval required for new terms or definition changes
331|
332|### Term Addition Process
333|1. Identify new terminology need from workflow or rule updates
334|2. Research standard definitions and best practices
335|3. Draft definition with clear usage examples
336|4. Add to appropriate section in glossary
337|5. Update AGENTS.md to reference glossary if needed
338|6. Update workflows to reference new terms via glossary
339|
340|### Reference Pattern
341|All workflows and rules should reference this glossary for terminology understanding:
342|```markdown
343|For definition of **{TERM}**, see Workflow/Terminology_Glossary.md
344|```
345|
346|---
347|
348|## Best Practices for Terminology Usage
349|
350|1. **Consistency**: Always use terminology as defined in this glossary
351|2. **Reference**: When introducing new terms, reference this glossary
352|3. **Clarity**: Use defined terms consistently across all harness documents
353|4. **Updates**: Propagate terminology changes through Architect agent
354|5. **SSOT**: This glossary is the single source of truth for all terminology
355|
356|---
357|
358|**Last Updated**: 2026-07-27
359|**Version**: 1.0
360|**Maintained By**: Architect Agent
</file-view>
```

**Success**: True
**Tool Use ID**: call_993c50c1694446ac93135e55
**Hook Data**:
```
{
  "hook_event_name": "PostToolUse",
  "tool_name": "read",
  "tool_input": {
    "file_path": "C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md"
  },
  "tool_use_id": "call_993c50c1694446ac93135e55",
  "tool_response": {
    "success": true,
    "output": "<file-view path=\"C:/SovereignAI/Workflow/Workflow_Reference/Terminology_Glossary.md\" start_line=\"1\" end_line=\"360\" total_lines=\"360\">\n  1|---\n  2|id: wf-ref-terminology\n  3|status: active\n  4|owner: architect-agent\n  5|updated: 2026-07-28\n  6|purpose: Single source of truth for all capitalized terminology used across the SovereignAI harness architecture\n  7|---\n  8|\n  9|# SovereignAI Harness Terminology Glossary\n 10|\n 11|**Purpose**: Single source of truth (SSOT) for all capitalized terminology used across the SovereignAI harness architecture. This glossary ensures consistent understanding of governance terminology across all agents and workflows.\n 12|\n 13|**Governance**: This document is maintained by the Architect agent and serves as the authoritative source for terminology definitions. All agents must reference this glossary for terminology understanding.\n 14|\n 15|---\n 16|\n 17|## Core Workflow Commands\n 18|\n 19|### **SCAN**\n 20|**Definition**: Examine all documents within scope line by line without skipping anything - comprehensive examination required for governance compliance.\n 21|\n 22|**Usage**: Used when comprehensive examination of documents is required for governance compliance, quality assurance, or consistency verification. This is the primary scanning method and cannot be replaced by pattern matching tools like grep.\n 23|\n 24|**Examples**:\n 25|- **SCAN** all harness architecture files for consistency checks\n 26|- **SCAN** App/ directory line by line for compliance verification\n 27|- **SCAN** workflow files to validate template compliance\n 28|\n 29|---\n 30|\n 31|### **PRINT**\n 32|**Definition**: Output text to chat interface for user visibility (not to files or logs).\n 33|\n 34|**Usage**: Used to communicate workflow status, progress updates, and important information to the user during workflow execution. This command does not write to files or logs.\n 35|\n 36|**Examples**:\n 37|- **PRINT** \"Workflow initialization complete\"\n 38|- **PRINT** \"Scan strategy selected - Full Comprehensive\"\n 39|- **PRINT** \"Consistency check complete - 0 issues found\"\n 40|\n 41|---\n 42|\n 43|### **VALIDATION**\n 44|**Definition**: Validate step completion before proceeding to next phase.\n 45|\n 46|**Usage**: Used to ensure that workflow steps have completed successfully and meet quality criteria before moving to the next phase. This is a quality validation mechanism.\n 47|\n 48|**Examples**:\n 49|- **VALIDATION**: Validate file reference extraction completed successfully\n 50|- **VALIDATION**: Validate workflow structure check completed successfully\n 51|- **VALIDATION**: Validate that all referenced files exist\n 52|\n 53|---\n 54|\n 55|### **STATUS TRACKING**\n 56|**Definition**: Update workflow status for monitoring and recovery.\n 57|\n 58|**Usage**: Used to track workflow progress, enable recovery from failures, and provide visibility into workflow execution state. Status updates are typically written to workflow_state.json or similar tracking mechanisms.\n 59|\n 60|**Examples**:\n 61|- **STATUS TRACKING**: Update workflow status to \"phase_0_complete\"\n 62|- **STATUS TRACKING**: Update workflow status to \"phase_3_in_progress\"\n 63|- **STATUS TRACKING**: Update workflow status to \"phase_7_complete\"\n 64|\n 65|---\n 66|\n 67|### **TERMINATE**\n 68|**Definition**: End workflow execution (do not return to step 1).\n 69|\n 70|**Usage**: Used in single-execution workflows to signal completion and prevent automatic looping. This is the workflow termination command for utility workflows.\n 71|\n 72|**Examples**:\n 73|- **TERMINATE**: End workflow execution (do not return to step 1)\n 74|- **TERMINATE**: Workflow execution complete - workflow terminated\n 75|\n 76|---\n 77|\n 78|## Workflow-Specific Commands\n 79|\n 80|### **EXECUTION MODE HANDLING**\n 81|**Definition**: Apply execution mode handling patterns based on selected mode (Manual/Auto/Complete).\n 82|\n 83|**Usage**: Used to determine how the workflow should respond to failures based on the user-selected execution mode.\n 84|\n 85|**Modes**:\n 86|- **Manual**: Stop at failures for human oversight\n 87|- **Auto**: Don't continue on failures (auto-stop on errors)\n 88|- **Complete**: Continue past failures (ignore all errors)\n 89|\n 90|**Examples**:\n 91|- **EXECUTION MODE HANDLING**: Apply execution mode handling patterns\n 92|- **EXECUTION MODE HANDLING**: Apply review mode handling patterns\n 93|\n 94|---\n 95|\n 96|### **CONVERGENCE CHECK**\n 97|**Definition**: Verify panelist scores against quality thresholds.\n 98|\n 99|**Usage**: Used in Round Table review processes to determine if panelists have reached agreement on quality assessments.\n100|\n101|**Thresholds**:\n102|- Clean pass: \u00e2\u2030\u00a54.5 score\n103|- Acceptable pass: 3.5-4.4 score with documented rationale\n104|- Fail: <3.5 score\n105|\n106|**Examples**:\n107|- **CONVERGENCE CHECK**: Check if all panelists chose PASS (\u00e2\u2030\u00a54.5 score or 3.5-4.4 with rationale)\n108|- **CONVERGENCE CHECK**: Verify convergence criteria met\n109|\n110|---\n111|\n112|### **QUOTA AWARENESS**\n113|**Definition**: Monitor internal subagent quota usage for recovery tracking.\n114|\n115|**Usage**: Used to track subagent resource consumption and enable recovery if quota limits are approached or exceeded.\n116|\n117|**Examples**:\n118|- **QUOTA AWARENESS**: Monitor internal subagent quota usage and track step progress\n119|- **QUOTA AWARENESS**: Track quota usage for recovery if needed\n120|\n121|---\n122|\n123|### **LOOP DECISION**\n124|**Definition**: Determine workflow continuation based on conditions.\n125|\n126|**Usage**: Used to control workflow flow and determine whether to loop back to previous phases or proceed forward.\n127|\n128|**Examples**:\n129|- **LOOP DECISION**: If more plan steps remain \u00e2\u2020\u2019 Return to step 25 with next step\n130|- **LOOP BACK**: Return to Phase 4 for next iteration\n131|\n132|---\n133|\n134|### **HANDOFF VALIDATION**\n135|**Definition**: Verify handoff file integrity and completeness.\n136|\n137|**Usage**: Used when transferring work between agents to ensure all required information is present and accessible.\n138|\n139|**Examples**:\n140|- **HANDOFF VALIDATION**: Verify handoff file integrity per template requirements\n141|- **HANDOFF VALIDATION**: Validate all required fields are present\n142|\n143|---\n144|\n145|## Decision and Planning Commands\n146|\n147|### **ARCHITECT OPINION**\n148|**Definition**: Provide analysis and recommendation BEFORE user selection.\n149|\n150|**Usage**: Used by Architect agent to provide expert analysis and recommendations when presenting implementation options to users.\n151|\n152|**Examples**:\n153|- **ARCHITECT OPINION**: Provide analysis and recommendation BEFORE user selection\n154|- **ARCHITECT OPINION**: Recommend optimal approach based on analysis\n155|\n156|---\n157|\n158|### **PRESENTATION PATTERN**\n159|**Definition**: Present options with metrics, provide architect opinion, use popup menu for selection.\n160|\n161|**Usage**: Used to standardize how options are presented to users, ensuring consistent format and decision-making process.\n162|\n163|**Examples**:\n164|- **PRESENTATION PATTERN**: Present options with metrics, provide architect opinion, use popup menu\n165|- **PRESENTATION PATTERN**: Use popup menu for selection\n166|\n167|---\n168|\n169|### **RULE ENFORCEMENT**\n170|**Definition**: Ensure options comply with agent rules.\n171|\n172|**Usage**: Used to validate that proposed options or approaches comply with the relevant agent's governance rules.\n173|\n174|**Examples**:\n175|- **RULE ENFORCEMENT**: Ensure options comply with Architect rules\n176|- **RULE ENFORCEMENT**: Validate compliance with governance constraints\n177|\n178|---\n179|\n180|### **SPECIFICATION CONFIRMATION**\n181|**Definition**: Ask user to confirm specification or request modifications using popup menu.\n182|\n183|**Usage**: Used to get user approval on detailed specifications before proceeding with implementation.\n184|\n185|**Examples**:\n186|- **SPECIFICATION CONFIRMATION**: Ask user to confirm specification or request modifications\n187|- **SPECIFICATION CONFIRMATION**: Use popup menu with [Confirm/Modify] options\n188|\n189|---\n190|\n191|### **IMPLEMENTATION MODE SELECTION**\n192|**Definition**: Ask user to choose implementation mode using popup menu.\n193|\n194|**Usage**: Used to determine whether implementation should be automated or manual based on user preference.\n195|\n196|**Examples**:\n197|- **IMPLEMENTATION MODE SELECTION**: Ask user to choose using popup menu\n198|- **IMPLEMENTATION MODE SELECTION**: Select automated vs manual implementation\n199|\n200|---\n201|\n202|## Information and Notes\n203|\n204|### **AUTOMATED PROGRESSION NOTE**\n205|**Definition**: Validation system behavior notes for context.\n206|\n207|**Usage**: Used to provide explanatory notes about how the validation system behaves in specific situations.\n208|\n209|**Examples**:\n210|- **AUTOMATED PROGRESSION NOTE**: The validation system allows state-mutating tools automatically during this step\n211|- **AUTOMATED PROGRESSION NOTE**: User confirmation requests use ask_user_question for approval without triggering failure intervention\n212|\n213|---\n214|\n215|### **IMPORTANT**\n216|**Definition**: Important notes that require attention but are not critical failures.\n217|\n218|**Usage**: Used to highlight important information that users should be aware of during workflow execution.\n219|\n220|**Examples**:\n221|- **IMPORTANT**: Real-world testing required to avoid fake passes from isolated testing\n222|- **IMPORTANT**: Hook file changes require Devin CLI restart\n223|\n224|---\n225|\n226|## Severity and Priority Markers\n227|\n228|### **CRITICAL**\n229|**Definition**: Critical issues or required actions that must be addressed immediately.\n230|\n231|**Usage**: Used to mark issues that require immediate attention or actions that are mandatory for workflow success.\n232|\n233|**Examples**:\n234|- **CRITICAL**: Violations that must be fixed (missing tests, hardcoded dependencies)\n235|- **CRITICAL**: Hook file changes require Devin CLI restart before testing\n236|\n237|---\n238|\n239|### **HIGH**\n240|**Definition**: High priority issues that should be addressed soon.\n241|\n242|**Usage**: Used to mark significant issues that should be resolved but are not immediately blocking.\n243|\n244|**Examples**:\n245|- **HIGH**: Major quality issues that should be fixed (monolithic functions, poor modularity)\n246|- **HIGH**: High priority issues requiring attention\n247|\n248|---\n249|\n250|### **MEDIUM**\n251|**Definition**: Medium priority issues for improvement.\n252|\n253|**Usage**: Used to mark issues that represent improvements but are not urgent.\n254|\n255|**Examples**:\n256|- **MEDIUM**: Best practices improvements (code readability, maintainability)\n257|- **MEDIUM**: Medium priority issues for improvement\n258|\n259|---\n260|\n261|### **LOW**\n262|**Definition**: Low priority minor suggestions.\n263|\n264|**Usage**: Used to mark minor suggestions or improvements that are optional.\n265|\n266|**Examples**:\n267|- **LOW**: Minor suggestions (comments, formatting)\n268|- **LOW**: Low priority issues for consideration\n269|\n270|---\n271|\n272|## Governance Terms\n273|\n274|### **BP** (Best Practice)\n275|**Definition**: Established industry standards that must be researched before proceeding with major decisions.\n276|\n277|**Usage**: Used to indicate when web search for current best practices is required before making architectural or implementation decisions.\n278|\n279|**Examples**:\n280|- **BP**: Web search for best practices before major architectural decisions\n281|- **BP**: Research industry standards before implementation\n282|\n283|**Implementation**: When user input is \"BP?\" (Best Practice?), perform web search for current best practices relevant to the task at hand.\n284|\n285|---\n286|\n287|### **SSOT** (Single Source of Truth)\n288|**Definition**: Centralized repository for authoritative information that eliminates duplication and inconsistencies.\n289|\n290|**Usage**: Used to indicate the authoritative source for specific information, ensuring all agents reference the same accurate data.\n291|\n292|**Examples**:\n293|- **SSOT**: Workflow/Terminology_Glossary.md is the SSOT for terminology definitions\n294|- **SSOT**: INDEX.md is the SSOT for directory structure information\n295|\n296|**Best Practice**: Establish SSOT for critical information to prevent inconsistencies and ensure all stakeholders work from the same data.\n297|\n298|---\n299|\n300|## Standard Terms\n301|\n302|### **ID**\n303|**Definition**: Unique identifier for workflows, documents, or entities.\n304|\n305|**Usage**: Used to provide unique identification for workflows, documents, and other entities within the harness architecture.\n306|\n307|**Examples**:\n308|- **ID**: WF-ARCH-001\n309|- **ID**: WF-PLAN-001\n310|\n311|---\n312|\n313|### **DO**\n314|**Definition**: Required actions that must be performed according to rules.\n315|\n316|**Usage**: Used in rule files to specify mandatory actions that agents must perform.\n317|\n318|**Examples**:\n319|- **DO**: Verify each function follows single responsibility principle\n320|- **DO**: Check that functions have clear inputs and outputs\n321|\n322|---\n323|\n324|## Terminology Governance\n325|\n326|### Glossary Maintenance\n327|- **Owner**: Architect Agent\n328|- **Update Process**: Architect agent reviews and updates glossary based on new terminology needs\n329|- **Version Control**: All changes tracked with version history\n330|- **Approval**: Architect agent approval required for new terms or definition changes\n331|\n332|### Term Addition Process\n333|1. Identify new terminology need from workflow or rule updates\n334|2. Research standard definitions and best practices\n335|3. Draft definition with clear usage examples\n336|4. Add to appropriate section in glossary\n337|5. Update AGENTS.md to reference glossary if needed\n338|6. Update workflows to reference new terms via glossary\n339|\n340|### Reference Pattern\n341|All workflows and rules should reference this glossary for terminology understanding:\n342|```markdown\n343|For definition of **{TERM}**, see Workflow/Terminology_Glossary.md\n344|```\n345|\n346|---\n347|\n348|## Best Practices for Terminology Usage\n349|\n350|1. **Consistency**: Always use terminology as defined in this glossary\n351|2. **Reference**: When introducing new terms, reference this glossary\n352|3. **Clarity**: Use defined terms consistently across all harness documents\n353|4. **Updates**: Propagate terminology changes through Architect agent\n354|5. **SSOT**: This glossary is the single source of truth for all terminology\n355|\n356|---\n357|\n358|**Last Updated**: 2026-07-27\n359|**Version**: 1.0\n360|**Maintained By**: Architect Agent\n</file-view>",
    "error": null
  },
  "session_id": "wirehaired-vacation",
  "prompt_id": "08a0bb9c-98b7-4508-a275-372caee5196b"
}
```

---
### USER_PROMPT
**Timestamp**: 2026-07-28T23:36:13.899128
**Session**: wirehaired-vacation
**Prompt ID**: 6e673094-4b49-454d-a939-91013da7bd4d

**Prompt**:
```
How are the agents knowing to use the skill workflowopen straight away when I clear the conversation?
```

---
### USER_PROMPT
**Timestamp**: 2026-07-28T23:37:53.514878
**Session**: wirehaired-vacation
**Prompt ID**: 84d9f289-8c30-4e82-bf0e-ae6514de778b

**Prompt**:
```
so it will 100% detect which agent I am using when its initialied in workflows?
```

---
