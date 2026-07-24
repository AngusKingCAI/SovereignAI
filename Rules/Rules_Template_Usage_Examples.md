# Rules Template Usage Examples

**Purpose**: Examples demonstrating how to use the Hybrid Warm-Rules Template for different agent scenarios  
**Template Reference**: `Rules/Rules_Template.md`  
**Created**: 2026-07-24  

---

## Example 1: Creating Rules for a New Agent

### Scenario
You need to create rules for a new "SecurityAuditor" agent.

### Steps

1. **Copy the Template**:
   ```bash
   cp Rules/Rules_Template.md Rules/SecurityAuditor/SecurityAuditor_Rules.md
   ```

2. **Customize Warm Rules** (First 50 lines):
   ```markdown
   ## Warm Rules (Critical - First 50 Lines)
   
   ### 1. Security Compliance
   - ALWAYS verify security compliance before conducting audits
   - NEVER skip security checks for convenience
   - BEFORE any audit, verify security framework alignment
   - AFTER audits, document security compliance rationale
   
   ### 2. Audit Scope Boundaries  
   - NEVER audit systems outside defined audit scope
   - ALWAYS reference audit boundaries when uncertain
   - BEFORE starting audit, verify target is within scope
   - IF scope unclear, STOP and request clarification
   
   ### 3. Security Authority Separation
   - NEVER mix security assessment with remediation in same operation
   - ALWAYS maintain separation between audit and fix operations
   - BEFORE audit design, verify assessment/remediation separation
   - DURING audit, check for separation violations
   ```

3. **Update Metadata**:
   ```markdown
   **Purpose**: Operational rules for SecurityAuditor agent following security audit best practices  
   **Status**: Active  
   **Agent Type**: SecurityAuditor  
   **Template Based On**: Rules/Rules_Template.md v1.0
   ```

4. **Customize Appendices**:
   - Add security-specific constraint categories
   - Include audit procedure rules
   - Add vulnerability assessment standards
   - Include security reporting requirements

### Result
The new SecurityAuditor agent has rules optimized for persistent security auditing with warm-rules caching for critical security constraints.

---

## Example 2: Refactoring Existing Agent Rules

### Scenario
You want to refactor existing Executor_Rules.md to use the warm-rules format.

### Steps

1. **Analyze Current Rules**:
   - Identify most frequently violated rules
   - Determine critical safety constraints
   - Find rules that should be cached separately

2. **Extract Warm Rules** (First 50 lines):
   ```markdown
   ## Warm Rules (Critical - First 50 Lines)
   
   ### 1. Plan Fidelity
   - ALWAYS follow approved plans exactly as specified
   - NEVER deviate from plan specifications without approval
   - BEFORE implementation, verify plan alignment
   - DURING implementation, check for plan deviations
   
   ### 2. Scope Compliance
   - NEVER implement features outside approved scope
   - ALWAYS reference plan when scope questions arise
   - BEFORE coding, verify task is within plan scope
   - IF scope unclear, STOP and request clarification
   ```

3. **Reorganize Detailed Rules**:
   - Move remaining rules to Structured Appendices
   - Maintain DO/DON'T format
   - Add evolution procedures for rule updates

4. **Update Caching Directives**:
   ```markdown
   ### Caching Directives
   - **Warm Rules Cache**: HIGH PRIORITY - Cache first 50 lines separately
     - Cache file: `Logs/Executor/Cache/warm_rules_cache.json`
     - Re-read triggers: File modification, session start, context compaction
   ```

### Result
Executor agent now has optimized rule structure with critical plan fidelity and scope compliance rules cached separately for improved enforcement.

---

## Example 3: Implementing Rule Caching

### Scenario
You want to implement the caching mechanism described in the template.

### Implementation

1. **Create Cache Directory Structure**:
   ```bash
   mkdir -p Logs/{AgentName}/Cache
   ```

2. **Implement Cache Loader** (Python example):
   ```python
   import json
   import hashlib
   from pathlib import Path
   
   class RuleCache:
       def __init__(self, agent_name):
           self.agent_name = agent_name
           self.cache_dir = Path(f"Logs/{agent_name}/Cache")
           self.warm_cache_file = self.cache_dir / "warm_rules_cache.json"
           
       def load_warm_rules(self, template_path):
           """Load and cache warm rules section"""
           with open(template_path, 'r') as f:
               lines = f.readlines()[:50]  # First 50 lines
               
           cache_data = {
               "content": "".join(lines),
               "hash": hashlib.sha256("".join(lines).encode()).hexdigest(),
               "last_modified": Path(template_path).stat().st_mtime
           }
           
           self.warm_cache_file.parent.mkdir(parents=True, exist_ok=True)
           with open(self.warm_cache_file, 'w') as f:
               json.dump(cache_data, f)
               
           return cache_data["content"]
           
       def should_refresh(self, template_path):
           """Check if cache needs refresh"""
           if not self.warm_cache_file.exists():
               return True
               
           with open(self.warm_cache_file, 'r') as f:
               cache_data = json.load(f)
               
           current_mtime = Path(template_path).stat().st_mtime
           return current_mtime > cache_data["last_modified"]
   ```

3. **Usage in Agent**:
   ```python
   # Initialize cache
   cache = RuleCache("Executor")
   
   # Load warm rules with caching
   if cache.should_refresh("Rules/Executor/Executor_Rules.md"):
       warm_rules = cache.load_warm_rules("Rules/Executor/Executor_Rules.md")
   else:
       # Load from cache
       with open(cache.warm_cache_file, 'r') as f:
           cache_data = json.load(f)
           warm_rules = cache_data["content"]
   ```

### Result
Warm rules are cached separately and automatically refreshed when the template file changes, implementing the O(1) rule propagation pattern.

---

## Example 4: Rule Evolution and Updates

### Scenario
You need to add a new rule based on repeated violations.

### Process

1. **Identify Pattern**:
   - Issue: Agents frequently skip documentation updates
   - Pattern: 3 violations in past week
   - Impact: Documentation becomes outdated

2. **Determine Rule Placement**:
   - First violation: Add to Structured Appendices
   - Second violation: Add to Warm Rules section
   - Third violation: Implement automated hook

3. **Add Rule to Appendices** (First occurrence):
   ```markdown
   ### 5. Documentation Standards Rules
   
   **DO**:
   - Update documentation when implementation changes
   - Keep documentation current with code changes
   
   **DON'T**:
   - Skip documentation updates for convenience
   - Leave documentation outdated
   ```

4. **Promote to Warm Rules** (Second occurrence):
   ```markdown
   ### 8. Documentation Compliance
   - NEVER skip documentation updates for convenience
   - ALWAYS update docs when implementation changes
   - BEFORE completion, ensure documentation is current
   - AFTER changes, update relevant documentation
   ```

5. **Implement Automated Hook** (Third occurrence):
   ```python
   def pre_commit_hook(file_changes):
       """Check if documentation was updated"""
       code_files = [f for f in file_changes if f.endswith('.py')]
       doc_files = [f for f in file_changes if f.endswith('.md')]
       
       if code_files and not doc_files:
           raise Exception("Documentation update required for code changes")
   ```

### Result
Rule evolution follows the research-based pattern: inline rules → warm rules → automated enforcement, achieving 99% compliance.

---

## Example 5: Cross-Agent Rule Consistency

### Scenario
You need to ensure consistent rule application across multiple agents.

### Approach

1. **Use Template as Base**:
   - All agents reference `Rules/Rules_Template.md`
   - Customize warm rules for agent-specific needs
   - Maintain consistent appendices structure

2. **Common Warm Rules** (in all agents):
   ```markdown
   ### 1. Constitutional Compliance
   - ALWAYS verify constitutional compliance before making decisions
   - NEVER skip constitutional compliance checks for convenience
   ```

3. **Agent-Specific Warm Rules**:
   - Architect: Infrastructure-first principles
   - Executor: Plan fidelity requirements
   - Planner: Gate enforcement rules
   - SecurityAuditor: Security compliance checks

4. **Consistency Verification**:
   ```python
   def verify_rule_consistency():
       """Check that all agents follow template structure"""
       agents = ['Architect', 'Executor', 'Planner', 'SecurityAuditor']
       
       for agent in agents:
           rules_file = f"Rules/{agent}/{agent}_Rules.md"
           with open(rules_file, 'r') as f:
               content = f.read()
               
           # Verify warm rules section exists
           if "## Warm Rules" not in content:
               print(f"WARNING: {agent} missing warm rules section")
               
           # Verify constitutional compliance rule
           if "Constitutional Compliance" not in content:
               print(f"WARNING: {agent} missing constitutional compliance rule")
   ```

### Result
All agents maintain consistent rule structure while allowing agent-specific customization, ensuring governance consistency across the system.

---

## Best Practices Summary

1. **Always keep warm rules within first 50 lines** for optimal caching
2. **Follow trigger-action-verification pattern** for each warm rule
3. **Implement cache validation** using hash-based verification
4. **Evolve rules based on violation patterns** following the 3-strike approach
5. **Maintain consistent structure** across all agents using the template
6. **Test rule changes** before deployment to avoid compliance issues
7. **Document rule evolution** with rationale and impact analysis
8. **Use automated hooks** for critical rules that reach third violation

---

**Template Version**: 1.0  
**Last Updated**: 2026-07-24  
**Constitutional Status**: COMPLIANT