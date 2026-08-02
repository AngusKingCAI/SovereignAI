---
id: wf-ref-quota-handling
status: active
owner: architect-agent
updated: 2026-07-28
purpose: Universal quota handling patterns for agent workflows
---

# Quota Handling Patterns

**Purpose**: Universal quota handling patterns for agent workflows.

**Status**: ✅ **IMPLEMENTED** - Basic quota tracking for internal subagents

## Overview

This document describes patterns for handling quota exhaustion during agent execution, with specific focus on internal subagents that are used in Round Table reviews and other multi-agent coordination scenarios.

## Implementation Scope

**Implemented**:
- Basic quota tracking for internal subagents
- Step progress tracking for quota awareness
- Simple recovery patterns for quota exhaustion

**Not Implemented**:
- Full state persistence layer (deferred)
- Automated quota exhaustion detection (deferred)
- Agent-to-agent state synchronization (deferred)

## Context

**External Agents**: External services (e.g., Chathub.gg) are not subject to quota limitations for this system.

**Internal Subagents**: Internal subagents used in Round Table reviews and other multi-agent operations are subject to quota limitations and require tracking and recovery mechanisms.

## Basic Quota Tracking Pattern

### Internal Subagent Quota Awareness
- **Step Tracking**: Track step progress for internal subagents to understand quota consumption
- **Quota Estimation**: Estimate quota usage per step based on typical token consumption
- **Quota Monitoring**: Monitor quota status before launching internal subagents
- **Fallback Planning**: Have backup plans if quota exhaustion occurs

### Recovery Pattern for Internal Subagents
- **Quota Exhaustion Detection**: Monitor for quota exhaustion signals during subagent execution
- **Step Recovery**: Resume from last completed step if quota exhaustion occurs
- **Partial Results**: Use partial results from completed steps if full execution fails
- **Escalation**: Escalate to user if quota exhaustion prevents completion

## Implementation Requirements (Basic)

### Workflow Integration
- Add quota awareness checks before launching internal subagents
- Track step progress for internal subagents
- Implement fallback mechanisms for quota exhaustion
- Add quota status reporting in workflow logs

### Subagent Guidelines
- Internal subagents should be designed for efficient quota usage
- Implement step-by-step progress reporting
- Provide checkpoint-style output for recovery
- Design for graceful degradation on quota exhaustion

## Implementation Status

**Currently Implemented**:
- Basic quota tracking in Planner workflow for internal Round Table reviews
- Step progress tracking for internal subagents
- Manual quota monitoring and fallback patterns

**Requires Future Implementation**:
- Automated quota exhaustion detection
- Full state persistence for subagent sessions
- Agent-to-agent state synchronization protocols
- Audit trail for quota events

## Current Practice

**For internal subagents**:
- Plan work within quota limits for subagent operations
- Implement manual checkpoint strategies for long-running tasks
- Monitor quota usage during execution
- Use step progress tracking for recovery

**For external agents**:
- External agents (Chathub.gg) are not subject to quota limitations
- Use external agents for quota-intensive operations when available

## Architectural Recommendation

Until the infrastructure for stateful subagent recovery is implemented:
1. **Design subagent tasks** to complete within quota limits
2. **Implement manual recovery** strategies as needed
3. **Use external agents** for quota-intensive operations
4. **Track step progress** for internal subagent recovery
5. **Monitor quota usage** proactively

## Next Steps

This framework should be revisited when:
- State persistence infrastructure is available
- Subagent communication protocols are implemented
- Recovery trigger mechanisms are in place
- Audit requirements for quota events are defined