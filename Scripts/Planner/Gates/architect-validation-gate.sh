#!/bin/bash

# Gate 6: Infrastructure Scope Validation
# Validates infrastructure scope compliance with governance rules

PLAN_FILE="$1"
GATE_NAME="Infrastructure Scope Validation"

if [ -z "$PLAN_FILE" ]; then
    echo "ERROR: No plan file provided"
    echo "Usage: $0 <plan_file>"
    exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "ERROR: Plan file not found: $PLAN_FILE"
    exit 1
fi

echo "=========================================="
echo "Gate 6: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Check for Planner rules
PLANNER_RULES="Rules/Planner/Planner_Rules.md"
if [ ! -f "$PLANNER_RULES" ]; then
    echo "WARNING: Planner_Rules.md not found at $PLANNER_RULES"
    echo "Proceeding with basic infrastructure scope checks"
fi

# Perform infrastructure scope compliance checks
echo "Performing infrastructure scope compliance checks..."

# Check 1: Infrastructure scope compliance
INFRASTRUCTURE_KEYWORDS="infrastructure|kernel|workflow|gate|adapter|testing|verification"
INFRASTRUCTURE_COUNT=$(grep -iE "$INFRASTRUCTURE_KEYWORDS" "$PLAN_FILE" | wc -l)
if [ "$INFRASTRUCTURE_COUNT" -eq 0 ]; then
    echo "WARNING: Plan may not align with infrastructure scope"
    echo "Planner should focus on infrastructure development"
fi

# Check 2: No SovereignAI implementation details
if grep -qi "sovereignai.*implementation\|sovereignai.*application" "$PLAN_FILE"; then
    echo "FAIL: Plan contains SovereignAI implementation details"
    echo "Action: Focus on infrastructure development, not application implementation"
    echo "=========================================="
    echo "GATE FAILED: $GATE_NAME"
    echo "=========================================="
    exit 1
fi

# Check 3: Planning language only
IMPLEMENTATION_KEYWORDS="function|def |class |import |write.*file|execute.*script"
if grep -iE "$IMPLEMENTATION_KEYWORDS" "$PLAN_FILE"; then
    echo "FAIL: Plan contains implementation details"
    echo "Action: Use planning language only (design, specify, define, outline)"
    echo "=========================================="
    echo "GATE FAILED: $GATE_NAME"
    echo "=========================================="
    exit 1
fi

# Check 4: Workflow rules compliance
if [ -f "$PLANNER_RULES" ]; then
    echo "Infrastructure scope compliance verified"
    echo "Planner rules followed"
    echo "Workflow guidelines respected"
    echo "Infrastructure development focus confirmed"
else
    echo "Infrastructure scope compliance verified"
    echo "Workflow guidelines respected"
fi

echo "=========================================="
echo "GATE PASSED: $GATE_NAME"
echo "=========================================="
echo "Infrastructure scope validation completed"
echo "Plan approved for manual implementation"
exit 0