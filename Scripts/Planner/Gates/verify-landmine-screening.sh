#!/bin/bash

# Gate 5: Landmine Screening Verification
# Verifies that LANDMINES.md screening was performed and no blocking landmines present

PLAN_FILE="$1"
GATE_NAME="Landmine Screening Verification"

if [ -z "$PLAN_FILE" ]; then
    echo "❌ GATE FAILED: No plan file provided"
    echo "Usage: $0 <plan_file>"
    exit 1
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "❌ GATE FAILED: Plan file not found: $PLAN_FILE"
    exit 1
fi

echo "=========================================="
echo "Gate 5: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Check for LANDMINES.md file
LANDMINES_FILE="Rules/Architect/LANDMINES.md"
if [ ! -f "$LANDMINES_FILE" ]; then
    LANDMINES_FILE="Rules/LANDMINES.md"
fi

if [ ! -f "$LANDMINES_FILE" ]; then
    echo "WARNING: LANDMINES.md not found in expected locations"
    echo "Expected locations: Rules/Architect/LANDMINES.md or Rules/LANDMINES.md"
    echo "Proceeding without landmine verification"
    echo "=========================================="
    echo "GATE PASSED WITH WARNING: $GATE_NAME"
    echo "=========================================="
    exit 0
fi

# Check if plan contains landmine screening documentation
SCREENING_DOCUMENTED=$(grep -i "landmine" "$PLAN_FILE" | wc -l)

if [ "$SCREENING_DOCUMENTED" -eq 0 ]; then
    echo "❌ GATE FAILED: No landmine screening documentation found in plan"
    echo "Action: Document LANDMINES.md screening results in plan"
    echo "Reference: Workflow/Planner/Planner_Plan_Workflow.md - Step 2.5"
    exit 1
fi

# Check for blocking landmines mentioned
BLOCKING_KEYWORDS="blocking|block|critical|stop|prohibit"
BLOCKING_FOUND=$(grep -iE "$BLOCKING_KEYWORDS" "$PLAN_FILE" | grep -i "landmine" | wc -l)

if [ "$BLOCKING_FOUND" -gt 0 ]; then
    echo "❌ GATE FAILED: Potential blocking landmines detected"
    echo "Plan contains references to blocking landmines"
    echo "Action: Address blocking landmines before plan delivery"
    echo "Reference: Rules/Architect/LANDMINES.md"
    exit 1
fi

# Extract screening results if present
SCREENING_RESULTS=$(grep -A 5 -i "landmine" "$PLAN_FILE" | head -10)

echo "✅ Landmine screening documented in plan"
echo "Screening references found: $SCREENING_DOCUMENTED"
echo "No blocking landmines detected"

if [ -n "$SCREENING_RESULTS" ]; then
    echo "Screening documentation:"
    echo "$SCREENING_RESULTS"
fi

echo "=========================================="
echo "✅ GATE PASSED: $GATE_NAME"
echo "=========================================="
exit 0