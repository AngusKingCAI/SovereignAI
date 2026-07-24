#!/bin/bash

# Gate 1: Plan Structure Validation
# Validates plan format against specification and checks required sections

PLAN_FILE="$1"
GATE_NAME="Plan Structure Validation"

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
echo "Gate 1: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Simple validation without Python for now
# Check for required sections
REQUIRED_SECTIONS=("Context" "Steps")
MISSING_SECTIONS=()

for section in "${REQUIRED_SECTIONS[@]}"; do
    if ! grep -q "^## $section" "$PLAN_FILE"; then
        MISSING_SECTIONS+=("$section")
    fi
done

# Check for metadata (looking for patterns with asterisks)
if ! grep -q "\*\*Revision\*\*:" "$PLAN_FILE"; then
    MISSING_SECTIONS+=("Revision")
fi

if ! grep -q "\*\*Date\*\*:" "$PLAN_FILE"; then
    MISSING_SECTIONS+=("Date")
fi

if ! grep -q "\*\*Goal\*\*:" "$PLAN_FILE"; then
    MISSING_SECTIONS+=("Goal")
fi

if [ ${#MISSING_SECTIONS[@]} -eq 0 ]; then
    echo "PASS: Plan structure validated"
    echo "All required sections present"
    echo "=========================================="
    echo "GATE PASSED: $GATE_NAME"
    echo "=========================================="
    exit 0
else
    echo "FAIL: Plan structure validation failed"
    echo "Missing items:"
    for item in "${MISSING_SECTIONS[@]}"; do
        echo "  - $item"
    done
    echo "=========================================="
    echo "GATE FAILED: $GATE_NAME"
    echo "=========================================="
    echo "Action: Fix plan structure before proceeding"
    echo "Reference: Workflow/Planner/Plan.md - Plan Format section"
    exit 1
fi