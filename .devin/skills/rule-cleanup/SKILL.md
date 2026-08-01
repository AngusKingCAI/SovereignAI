---
name: rule-cleanup
description: Propose and implement rule cleanup operations such as deduplication, consolidation, and removal of redundant rules.
triggers:
  - type: model
    pattern: "rule-cleanup|dedup|consolidate rules|remove redundant"
allowed-tools:
  - exec
  - read
  - write
  - edit
---

# Rule Cleanup Skill

## When to use
- You want to remove duplicate rule statements (SSOT violations)
- You need to consolidate similar rules
- You want to remove rules that never fire
- You need to refactor rule organization

## How to use
1. Run SSOT deduplication check:
   ```bash
   python scripts/validation/lint_ssot_duplicates.py
   ```
2. Identify rules to consolidate
3. Use `refines:` field to reference shared rules instead of duplicating
4. Update Policy Cards to use references
5. Validate changes:
   ```bash
   python scripts/validation/validate_policy_cards.py
   ```

## Best practices
- Never duplicate rule statements - use `refines:` instead
- Place shared rules in `governance/policy-cards/shared/`
- Agent-specific rules can refine shared rules with agent context
- Always run validators after cleanup
