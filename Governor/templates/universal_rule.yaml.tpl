# Universal Governor Rule Template
# Template: rule_name.yaml
# Use this as a template for both universal and agent-specific rules
# Replace placeholders with actual values, uncomment optional fields you use

id: rule_name
version: "1.0.0"
tier: warning  # OPTIONS: blocking, warning
# agent: architect  # OPTIONAL: for agent-specific rules (e.g., architect, executor, planner, researcher, reviewer)
name: rule_name
description: description
trigger:
  hook: SessionStart  # OPTIONS: SessionStart, SessionEnd, UserPromptSubmit, PreToolUse, PostToolUse, PermissionRequest, Stop, PostCompaction
  # tool: exec  # OPTIONAL: for tool-specific rules (e.g., exec, edit, read)
  # tools: [exec, edit]  # OPTIONAL: for multiple tools (list format)
action: action_name  # The action name from Governor/actions/
params:
  reason: reason
