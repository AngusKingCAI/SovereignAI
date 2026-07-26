# Token Optimization Hooks Implementation Plan

## Overview
This document provides comprehensive context and implementation guidance for token optimization hooks for the SovereignAI harness using Devin CLI. When the Hook Implementer Workflow asks for implementation plan documents or context, provide this document to supply all necessary information.

## Implementation Philosophy
- **One hook at a time**: Implement, test, validate, then proceed
- **Extensive testing**: Each hook must work correctly before proceeding
- **Restart requirement**: Hook file changes in `.devin/` require Devin CLI restart
- **Proven technology**: Prioritize implementations with real-world examples
- **Governance compliance**: Follow Architect workflow scope and rules

## Implementation Priority

### Phase 1: SovereignAI Workflow-Specific Optimizations (Highest Impact)

#### 1. File Read Caching (Highest Priority)
- **Status**: ⚠️ ADAPTATION REQUIRED
- **Relevance**: **HIGH** - SovereignAI workflows repeatedly read governance files (Architect_Rules.md, AGENTS.md, workflows)
- **Implementation**: Port Cache-Cow logic to Devin CLI for markdown governance files
- **Expected Savings**: 30-50% file read reduction for repeated governance file access
- **Real Example**: Cache-Cow for Claude Code
- **Risk Level**: Medium - requires adaptation and testing
- **SovereignAI Impact**: Very High (Architect/Planner workflows read governance files repeatedly)
- **Implementation Steps**:
  1. Study Cache-Cow implementation for Claude Code
  2. Adapt to Devin CLI hook format for markdown files
  3. Create custom hook script for governance file caching
  4. Test with SovereignAI workflow file reads (Rules/, Workflow/, AGENTS.md)
  5. Verify cache invalidation on file edits
  6. Document results and token savings

#### 2. Partial Read Optimization (Second Priority)
- **Status**: ✅ DEVIN CLI NATIVE SUPPORT
- **Relevance**: **HIGH** - SovereignAI workflows often need specific sections of large files
- **Implementation**: Use Devin CLI's native offset/limit parameters for read tool
- **Expected Savings**: 40-70% reduction for large file reads
- **Real Example**: Devin CLI read tool with offset/limit parameters
- **Risk Level**: Low - native feature, no custom implementation needed
- **SovereignAI Impact**: High (large workflow files, comprehensive governance documents)
- **Implementation Steps**:
  1. Analyze SovereignAI workflow file access patterns
  2. Identify files >500 lines that could benefit from partial reads
  3. Update workflows to use offset/limit for targeted reads
  4. Test with Architect/Planner workflows
  5. Document results and token savings

#### 3. Grep Result Limiting (Third Priority)
- **Status**: ✅ DEVIN CLI NATIVE SUPPORT
- **Relevance**: **MEDIUM** - SovereignAI workflows use grep for pattern matching
- **Implementation**: Use Devin CLI's native max_results parameter for grep tool
- **Expected Savings**: 30-50% reduction for pattern search operations
- **Real Example**: Devin CLI grep tool with max_results parameter
- **Risk Level**: Low - native feature, no custom implementation needed
- **SovereignAI Impact**: Medium (pattern searching in governance files)
- **Implementation Steps**:
  1. Analyze SovereignAI workflow grep usage patterns
  2. Add max_results parameter to grep operations
  3. Test with Architect/Planner workflows
  4. Document results and token savings

### Phase 2: Advanced Optimizations (Test Required)

#### 4. Markdown Compression Hook (Fourth Priority)
- **Status**: ⚠️ CUSTOM IMPLEMENTATION REQUIRED
- **Relevance**: **MEDIUM** - SovereignAI governance files are markdown-heavy
- **Implementation**: PreToolUse hook to compress markdown file reads by removing non-essential content
- **Expected Savings**: 20-40% markdown file read reduction
- **Real Example**: squeez markdown compression for memory files
- **Risk Level**: Medium - requires custom implementation and testing
- **SovereignAI Impact**: Medium (governance files, workflow documentation)
- **Implementation Steps**:
  1. Research markdown compression techniques
  2. Create hook script for intelligent markdown compression
  3. Test with SovereignAI governance files
  4. Verify essential content preservation
  5. Document results and token savings

#### 5. Context Management Hook (Fifth Priority)
- **Status**: ⚠️ DEVIN SUPPORT UNCERTAIN
- **Relevance**: **MEDIUM** - Better context management for long SovereignAI sessions
- **Implementation**: PostCompaction hook to re-inject critical governance context
- **Expected Savings**: 15-25% context reduction across compaction events
- **Real Example**: squeez PostCompaction re-injection
- **Risk Level**: High - Devin CLI PostCompaction support unclear
- **SovereignAI Impact**: Medium (long architectural planning sessions)
- **Implementation Steps**:
  1. Test PostCompaction hook support in Devin CLI
  2. If supported, implement context re-injection logic
  3. Test with long SovereignAI workflow sessions
  4. Document results and limitations

## Restart Requirement

**CRITICAL**: When editing hook files in `.devin/` directory, Devin CLI must be restarted for changes to take effect.

### Restart Procedure
1. Complete hook file changes
2. Commit changes to git (optional but recommended)
3. Restart Devin CLI completely
4. Verify hooks are loaded using `/hooks` command (if available)
5. Test hook functionality
6. Proceed with validation

### Files Requiring Restart
- `.devin/hooks.v1.json`
- `.devin/config.json`
- `.devin/config.local.json`

### Files NOT Requiring Restart
- Hook script files (Python scripts, shell scripts)
- Changes to hook script logic (scripts are executed fresh each time)

## Hook Implementer Workflow Proposal

### Workflow Name: Hook_Implementer_Workflow
**Purpose**: Systematic implementation and testing of token optimization hooks for SovereignAI harness
**Trigger**: User requests hook implementation or Architect initiates hook optimization
**End State**: Hook implemented, tested, documented, and integrated with SovereignAI workflows

### Workflow Structure

#### Phase 0: Read Hook Implementation Rules
- Read existing Architect rules for workflow scope
- Read hook implementation guidelines
- Store hook context for implementation

#### Phase 1: Select Hook for Implementation
- Review implementation priority list
- Select next hook to implement
- User confirmation of selection
- Document selection rationale

#### Phase 2: Research Hook Implementation
- Research real-world examples of selected hook
- Analyze compatibility with Devin CLI
- Review SovereignAI workflow requirements
- Document implementation approach

#### Phase 3: Create Hook Implementation
- Create hook script in Scripts/TokenOptimization/
- Create/update .devin/hooks.v1.json
- Follow SovereignAI script categorization
- Ensure governance compliance

#### Phase 4: Restart Devin CLI
- Inform user of restart requirement
- Wait for user to restart Devin CLI
- Verify hooks are loaded correctly
- Test basic hook functionality

#### Phase 5: Test Hook Functionality
- Test hook with basic operations
- Test hook with SovereignAI workflows
- Verify token savings achieved
- Document test results

#### Phase 6: Validate Integration
- Verify hook doesn't break existing workflows
- Check compatibility with existing hooks
- Validate compliance with Architect rules
- Document validation results

#### Phase 7: Document Implementation
- Update hook implementation documentation
- Document token savings achieved
- Update workflow integration notes
- Create hook-specific documentation

#### Phase 8: Governance Update
- Update relevant governance files if needed
- Update Architect rules if hook behavior changes
- Update AGENTS.md if agent capabilities change
- Commit changes with proper documentation

#### Phase 9: Final Validation
- Verify implementation matches intended scope
- Ensure no unintended changes
- Validate hook performance in real workflow
- Document final validation results

#### Phase 10: Return to Phase 0
- Complete hook implementation cycle
- Ready for next hook implementation
- Return to Phase 0 for next hook

## Implementation Template

### Hook Implementation Checklist

#### Pre-Implementation
- [ ] Research real-world examples
- [ ] Verify Devin CLI compatibility
- [ ] Review SovereignAI workflow requirements
- [ ] Document implementation approach
- [ ] User approval of implementation plan

#### Implementation
- [ ] Create hook script in Scripts/TokenOptimization/
- [ ] Update .devin/hooks.v1.json
- [ ] Follow script categorization rules
- [ ] Ensure proper error handling
- [ ] Add logging for debugging

#### Testing
- [ ] Restart Devin CLI
- [ ] Test basic hook functionality
- [ ] Test with SovereignAI workflows
- [ ] Verify token savings
- [ ] Test error handling
- [ ] Document test results

#### Validation
- [ ] Verify no workflow breakage
- [ ] Check hook compatibility
- [ ] Validate governance compliance
- [ ] Performance validation
- [ ] User acceptance testing

#### Documentation
- [ ] Update implementation documentation
- [ ] Document token savings
- [ ] Update workflow integration notes
- [ ] Create hook-specific documentation
- [ ] Update governance files if needed

## Testing Strategy

### Unit Testing
- Test hook script independently
- Test with mock hook inputs
- Verify output format compliance
- Test error handling

### Integration Testing
- Test with Devin CLI hook system
- Test with SovereignAI workflows
- Test with existing hooks
- Test restart behavior

### Performance Testing
- Measure token savings
- Measure execution overhead
- Test with large files/outputs
- Test with repetitive operations

### User Acceptance Testing
- Test with real SovereignAI tasks
- Verify user experience impact
- Validate no workflow disruption
- Document user feedback

## Risk Mitigation

### Low Risk Hooks
- Partial Read Optimization: Native Devin CLI feature
- Grep Result Limiting: Native Devin CLI feature
- No custom implementation required

### Medium Risk Hooks
- File Read Caching: Requires adaptation from Cache-Cow
- Markdown Compression Hook: Custom implementation needed
- Testing required for SovereignAI governance files

### High Risk Hooks
- Context Management Hook: Devin CLI PostCompaction support unclear
- MCP integration: Complex architecture
- Multiple hook coordination

### Risk Mitigation Strategies
- Implement one hook at a time
- Start with native features (no risk)
- Extensive testing before proceeding
- Rollback procedures for each hook
- Documentation of known issues
- User approval at each stage

## Success Criteria

### Functional Success
- Hook executes without errors
- Hook achieves expected token savings
- Hook doesn't break existing workflows
- Hook integrates with existing systems

### Performance Success
- Measurable token reduction (>20%)
- Minimal execution overhead (<100ms)
- No workflow performance degradation
- Scalable to SovereignAI workflow sizes

### Governance Success
- Complies with Architect rules
- Follows SovereignAI governance patterns
- Properly documented and categorized
- Maintains workflow scope discipline

## Next Steps

### Immediate Actions
1. Implement Partial Read Optimization (Phase 1, Hook #2) - native feature, no risk
2. Implement Grep Result Limiting (Phase 1, Hook #3) - native feature, no risk
3. Test extensively with SovereignAI workflows
4. Document results and lessons learned

### Short-term Actions
1. Implement File Read Caching (Phase 1, Hook #1) - adaptation from Cache-Cow
2. Test extensively with SovereignAI workflows
3. Document results and lessons learned
4. Evaluate Phase 2 hook adaptations

### Long-term Actions
1. Implement Markdown Compression Hook (Phase 2, Hook #4)
2. Test Context Management Hook (Phase 2, Hook #5)
3. Evaluate advanced hook patterns
4. Continuous optimization based on results

## Context and References

### SovereignAI Architecture
- Primary workflows: Architect_General_Workflow, Planner_Plan_Workflow
- Governance: Architect_Rules.md, AGENTS.md
- Hook location: .devin/hooks.v1.json
- Script location: Scripts/ (following script categorization rules)

### External References
- Cache-Cow: https://github.com/soonswan-study/claude-code-thrifty
- squeez: https://github.com/claudioemmanuel/squeez
- Devin CLI Hooks: https://docs.devin.ai/cli/extensibility/hooks/overview
- Devin CLI Read Tool: https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks
- Devin CLI Grep Tool: https://docs.devin.ai/cli/extensibility/hooks/lifecycle-hooks

### Implementation Notes
- This plan prioritizes proven implementations over theoretical patterns
- Each hook requires extensive testing before proceeding
- Hook file changes require Devin CLI restart
- Governance compliance must be maintained throughout
- Documentation is critical for long-term maintenance