# Executor-Specific Rule Template
# Template: executor_rule.yaml.tpl
# Use this as a template for executor-specific rules

id: executor_{{ rule_name }}
version: "1.0.0"
tier: blocking
agent: executor
domain: execution
name: {{ rule_name }}
description: {{ description }}
triggers:
  - PreToolUse
  - PostToolUse
check:
  params:
    actions:
      - name: block_command
        reason: {{ reason }}
