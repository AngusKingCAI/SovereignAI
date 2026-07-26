# Token Optimization Hooks Implementation Plan

## Overview
Systematic implementation of token optimization hooks for SovereignAI harness using Devin CLI. Focus on proven implementations with extensive testing before moving to next hook.

## Implementation Philosophy
- **One hook at a time**: Implement, test, validate, then proceed
- **Extensive testing**: Each hook must work correctly before proceeding
- **Restart requirement**: Hook file changes in `.devin/` require Devin CLI restart
- **Proven technology**: Prioritize implementations with real-world examples
- **Governance compliance**: Follow Architect workflow scope and rules

## Implementation Priority

### Phase 1: Proven Implementations (No-Brainer)

#### 1. RTK Integration (Highest Priority)
- **Status**: ✅ CONFIRMED WORKING
- **Implementation**: PreToolUse hook with command rewriting
- **Expected Savings**: 60-90% command output reduction
- **Real Example**: RTK Devin CLI integration (PR #3144)
- **Risk Level**: Low - proven technology with documentation
- **Implementation Steps**:
  1. Install RTK globally: `rtk init --agent devin`
  2. Verify hook installation in `~/.config/devin/config.json`
  3. Test with command: `git status` → should be rewritten to `rtk git status`
  4. Verify output compression works correctly
  5. Test with SovereignAI Architect workflow
  6. Document results and token savings

#### 2. TokenJuice Integration (Second Priority)
- **Status**: ✅ CONFIRMED WORKING (Beta)
- **Implementation**: PreToolUse hook with command wrapping
- **Expected Savings**: Variable content-aware compression
- **Real Example**: TokenJuice Devin integration
- **Risk Level**: Medium - beta status but functional
- **Implementation Steps**:
  1. Install TokenJuice: `tokenjuice install devin`
  2. Verify hook installation in `.devin/hooks.v1.json`
  3. Test with various command types
  4. Verify content-aware compression
  5. Test with SovereignAI workflows
  6. Document results and token savings

### Phase 2: Adaptable Patterns (Test Required)

#### 3. File Read Caching (Third Priority)
- **Status**: ⚠️ ADAPTATION REQUIRED
- **Implementation**: Port Cache-Cow logic to Devin CLI
- **Expected Savings**: 30-50% file read reduction
- **Real Example**: Cache-Cow for Claude Code
- **Risk Level**: Medium - requires adaptation and testing
- **Implementation Steps**:
  1. Study Cache-Cow implementation for Claude Code
  2. Adapt to Devin CLI hook format
  3. Create custom hook script for file read caching
  4. Test with SovereignAI workflow file reads
  5. Verify cache invalidation on file edits
  6. Document results and token savings

#### 4. PostToolUse Output Compression (Fourth Priority)
- **Status**: ⚠️ DEVIN SUPPORT UNCERTAIN
- **Implementation**: Test PostToolUse output replacement
- **Expected Savings**: 50-80% tool output reduction
- **Real Example**: Claude Code PostToolUse compression
- **Risk Level**: High - Devin CLI PostToolUse capabilities unclear
- **Implementation Steps**:
  1. Test basic PostToolUse hook with Devin CLI
  2. Verify output replacement capabilities
  3. If supported, implement compression logic
  4. Test with various tool outputs
  5. Document results and limitations

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
- RTK Integration: Proven technology
- TokenJuice: Beta but functional
- Basic command rewriting

### Medium Risk Hooks
- File read caching: Requires adaptation
- Output compression: Devin support uncertain
- Custom hook scripts

### High Risk Hooks
- Session management hooks: Devin support unclear
- MCP integration: Complex architecture
- Multiple hook coordination

### Risk Mitigation Strategies
- Implement one hook at a time
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
1. Create Hook_Implementer_Workflow.md in Workflow/Architect/
2. Implement RTK integration (Phase 1, Hook #1)
3. Test extensively with SovereignAI workflows
4. Document results and lessons learned

### Short-term Actions
1. Implement TokenJuice integration (Phase 1, Hook #2)
2. Test extensively with SovereignAI workflows
3. Document results and lessons learned
4. Evaluate Phase 2 hook adaptations

### Long-term Actions
1. Adapt file read caching from Cache-Cow
2. Test PostToolUse capabilities in Devin CLI
3. Evaluate advanced hook patterns
4. Continuous optimization based on results

## Context and References

### SovereignAI Architecture
- Primary workflows: Architect_General_Workflow, Planner_Plan_Workflow
- Governance: Architect_Rules.md, AGENTS.md
- Hook location: .devin/hooks.v1.json
- Script location: Scripts/TokenOptimization/

### External References
- RTK: https://github.com/rtk-ai/rtk
- TokenJuice: https://github.com/vincentkoc/tokenjuice
- Cache-Cow: https://github.com/soonswan-study/claude-code-thrifty
- Devin CLI Hooks: https://docs.devin.ai/cli/extensibility/hooks/overview

### Implementation Notes
- This plan prioritizes proven implementations over theoretical patterns
- Each hook requires extensive testing before proceeding
- Hook file changes require Devin CLI restart
- Governance compliance must be maintained throughout
- Documentation is critical for long-term maintenance