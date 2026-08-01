---
name: rule-lookup
description: Load the full definition of a specific Policy Card by ID. Use when you need to understand exactly what a rule checks, what patterns it denies, or what exemptions it has.
triggers:
  - type: model
    pattern: "rule-lookup"
allowed-tools:
  - read
---

# Rule Lookup Skill

## When to use
- You need the full check definition for a rule ID you saw in the rule index
- You want to understand why a tool call was denied
- You need to verify whether a specific action is allowed before taking it

## How to use
1. Identify the rule ID (e.g., ARCH-014) from the rule index or a denial message
2. Read the corresponding Policy Card file:
   - Shared rules: `governance/policy-cards/shared/<domain>.yaml`
   - Agent rules: `governance/policy-cards/<agent>/<domain>.yaml`
3. The Policy Card contains: rule statement, check definition, test cases, exemptions

## Example
If the rule index shows `ARCH-014: "Architect uses Manual execution mode by default"`:
- Read `governance/policy-cards/architect/execution-modes.yaml`
- The card's `check` field tells you exactly what the hook evaluates
