# Architect-Specific Rule Template
# Template: architect_block_destructive.yaml
# Use this as a template for architect-specific blocking rules

id: architect_{{ rule_name }}
version: "1.0.0"
tier: blocking
agent: architect
domain: {{ domain }}
name: {{ rule_name }}
description: {{ description }}
triggers:
  - PreToolUse
check:
  params:
    actions:
      - name: block_command
        reason: {{ reason }}
