---
name: harness-audit
description: Run audit checks on the harness to identify rule violations, drift, and coverage gaps.
triggers:
  - type: model
    pattern: "harness-audit|audit|harness review"
allowed-tools:
  - exec
  - read
---

# Harness Audit Skill

## When to use
- You want to check the current state of rule enforcement
- You need to identify which rules are firing most often
- You want to detect drift between declared rules and actual enforcement

## How to use
1. Run the weekly review report:
   ```bash
   python "Governance/Audit/weekly_review_report.py"
   ```
2. Run drift detection:
   ```bash
   python "Governance/Audit/drift_detection.py"
   ```
3. Check the audit log:
   ```bash
   cat "Governance/Audit/violations.jsonl"
   ```

## What it checks
- Most-violated rules (top denials)
- Rules that never fire (candidates for removal)
- Drift between documented behavior and actual enforcement
- Tool call distribution
