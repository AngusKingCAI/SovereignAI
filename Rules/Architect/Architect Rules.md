# Architect Rules

Always-on negative constraints for the Architect agent.

## Constitutional Constraints
- Do not build SovereignAI before Phase 12
- Do not skip phases or begin Phase N+1 before Phase N is complete
- Do not implement without a specification
- Do not complete implementation without tests

## Architectural Constraints
- Do not mix authority and intelligence in the same component
- Do not trust AI models for decision-making
- Do not rely on voluntary compliance
- Do not proceed when uncertain without verification
- Do not make decisions without constitutional compliance check

## IDE Architecture Constraints
- Do not deviate from the directory structure defined in `Rules/Architect/IDE_Architecture_Rules.md`
- Do not place files outside their designated directories (Agents/, Rules/, Workflow/, Scripts/, Logs/, Docs/)
- Do not use non-standard naming conventions for files or directories
- Do not create agent folders without proper AGENTS.md documentation
- Do not place scripts outside the Scripts/ directory
- Do not place logs outside the Logs/ directory
- Do not create logs outside Logs/{AgentName}/ for agent-specific operations
- Do not skip gate system validation for directory structure compliance

## Process Constraints
- Do not proceed to implementation without user review of specification
- Do not make architectural decisions without web search for best practices
- Do not present options without Quality/Token Cost/Efficiency metrics
- Do not skip constitutional compliance verification
- Do not start development without verifying global architecture compliance