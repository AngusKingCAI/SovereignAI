# Planner-Specific Rule Template
# Template: planner_rule.yaml.tpl
# Use this as a template for planner-specific rules

id: planner_{{ rule_name }}
version: "1.0.0"
tier: {{ tier }}
agent: planner
domain: planning
name: {{ rule_name }}
description: {{ description }}
triggers:
  - UserPromptSubmit
  - PreToolUse
check:
  params:
    actions:
      - name: block_command
        reason: {{ reason }}
