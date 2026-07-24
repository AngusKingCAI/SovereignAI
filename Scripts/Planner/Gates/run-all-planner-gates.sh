#!/bin/bash

# Master gate runner for Planner agent
# Runs all 6 gates sequentially and blocks plan delivery if any gate fails

PLAN_FILE="$1"
SESSION_ID="$2"

if [ -z "$PLAN_FILE" ]; then
    echo "❌ ERROR: No plan file provided"
    echo "Usage: $0 <plan_file> [session_id]"
    exit 1
fi

# Check for required tools
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ ERROR: Python not found"
    echo "Install Python 3 to run Planner gate system"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  WARNING: jq not found, JSON logging will be limited"
    USE_JQ=false
else
    USE_JQ=true
fi

if [ ! -f "$PLAN_FILE" ]; then
    echo "❌ ERROR: Plan file not found: $PLAN_FILE"
    exit 1
fi

GATE_DIR="$(dirname "$0")"
SESSION_ID="${SESSION_ID:-planner-gate-$(date +%s)}"

echo "=========================================="
echo "Planner Gate System - Master Runner"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Session ID: $SESSION_ID"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Initialize gate results
GATE_RESULTS=()
FAILED_GATES=()

# Gate 1: Plan Structure Validation
echo ""
echo "🔍 Running Gate 1: Plan Structure Validation..."
bash "$GATE_DIR/verify-plan-structure-fixed.sh" "$PLAN_FILE"
GATE1_RESULT=$?
GATE_RESULTS+=("Gate 1 (Structure): $([ $GATE1_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE1_RESULT -ne 0 ]; then
    FAILED_GATES+=("Plan Structure Validation")
fi

# Gate 2: Scope Compliance Validation
echo ""
echo "🔍 Running Gate 2: Scope Compliance Validation..."
bash "$GATE_DIR/verify-scope-compliance.sh" "$PLAN_FILE"
GATE2_RESULT=$?
GATE_RESULTS+=("Gate 2 (Scope): $([ $GATE2_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE2_RESULT -ne 0 ]; then
    FAILED_GATES+=("Scope Compliance Validation")
fi

# Gate 3: Dependency Analysis Validation
echo ""
echo "🔍 Running Gate 3: Dependency Analysis Validation..."
bash "$GATE_DIR/verify-dependency-analysis.sh" "$PLAN_FILE"
GATE3_RESULT=$?
GATE_RESULTS+=("Gate 3 (Dependencies): $([ $GATE3_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE3_RESULT -ne 0 ]; then
    FAILED_GATES+=("Dependency Analysis Validation")
fi

# Gate 4: Quality Assessment Validation
echo ""
echo "🔍 Running Gate 4: Quality Assessment Validation..."
bash "$GATE_DIR/verify-quality-assessment.sh" "$PLAN_FILE"
GATE4_RESULT=$?
GATE_RESULTS+=("Gate 4 (Quality): $([ $GATE4_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE4_RESULT -ne 0 ]; then
    FAILED_GATES+=("Quality Assessment Validation")
fi

# Gate 5: Landmine Screening Verification
echo ""
echo "🔍 Running Gate 5: Landmine Screening Verification..."
bash "$GATE_DIR/verify-landmine-screening.sh" "$PLAN_FILE"
GATE5_RESULT=$?
GATE_RESULTS+=("Gate 5 (Landmines): $([ $GATE5_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE5_RESULT -ne 0 ]; then
    FAILED_GATES+=("Landmine Screening Verification")
fi

# Gate 6: Infrastructure Scope Validation
echo ""
echo "🔍 Running Gate 6: Infrastructure Scope Validation..."
bash "$GATE_DIR/architect-validation-gate.sh" "$PLAN_FILE"
GATE6_RESULT=$?
GATE_RESULTS+=("Gate 6 (Infrastructure): $([ $GATE6_RESULT -eq 0 ] && echo "PASS" || echo "FAIL")")
if [ $GATE6_RESULT -ne 0 ]; then
    FAILED_GATES+=("Infrastructure Scope Validation")
fi

# Generate final results
echo ""
echo "=========================================="
echo "Planner Gate System - Final Results"
echo "=========================================="
echo "Session ID: $SESSION_ID"
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

for result in "${GATE_RESULTS[@]}"; do
    echo "$result"
done

echo "=========================================="

# Check if all gates passed
if [ ${#FAILED_GATES[@]} -eq 0 ]; then
    echo "✅ ALL GATES PASSED"
    echo "=========================================="
    echo "Plan approved for Executor delivery"
    
    # Generate gate completion hash
    GATE_HASH=$(echo "$PLAN_FILE$SESSION_ID$(date -u +"%Y-%m-%dT%H:%M:%SZ")" | sha256sum | cut -d' ' -f1)
    echo "Gate Completion Hash: $GATE_HASH"
    
    # Log gate completion
    LOG_ENTRY="Logs/Planner/gate-completions/${SESSION_ID}.json"
    mkdir -p "$(dirname "$LOG_ENTRY")"
    
    if [ "$USE_JQ" = true ]; then
        cat > "$LOG_ENTRY" << EOF
{
  "session_id": "$SESSION_ID",
  "plan_file": "$PLAN_FILE",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "gate_results": $(printf '%s\n' "${GATE_RESULTS[@]}" | jq -R . | jq -s .),
  "completion_hash": "$GATE_HASH",
  "status": "all_passed"
}
EOF
    else
        cat > "$LOG_ENTRY" << EOF
{
  "session_id": "$SESSION_ID",
  "plan_file": "$PLAN_FILE",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "gate_results": ["$(IFS=$'\n'; echo "${GATE_RESULTS[*]}")"],
  "completion_hash": "$GATE_HASH",
  "status": "all_passed"
}
EOF
    fi
    
    echo "Gate completion logged to: $LOG_ENTRY"
    exit 0
else
    echo "❌ GATE SYSTEM FAILED"
    echo "=========================================="
    echo "Failed Gates:"
    for gate in "${FAILED_GATES[@]}"; do
        echo "  - $gate"
    done
    echo ""
    echo "Action: Address failed gates before plan delivery"
    echo "Plan delivery BLOCKED until all gates pass"
    
    # Log gate failure
    LOG_ENTRY="Logs/Planner/gate-failures/${SESSION_ID}.json"
    mkdir -p "$(dirname "$LOG_ENTRY")"
    
    if [ "$USE_JQ" = true ]; then
        cat > "$LOG_ENTRY" << EOF
{
  "session_id": "$SESSION_ID",
  "plan_file": "$PLAN_FILE",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "gate_results": $(printf '%s\n' "${GATE_RESULTS[@]}" | jq -R . | jq -s .),
  "failed_gates": $(printf '%s\n' "${FAILED_GATES[@]}" | jq -R . | jq -s .),
  "status": "failed"
}
EOF
    else
        cat > "$LOG_ENTRY" << EOF
{
  "session_id": "$SESSION_ID",
  "plan_file": "$PLAN_FILE",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "gate_results": ["$(IFS=$'\n'; echo "${GATE_RESULTS[*]}")"],
  "failed_gates": ["$(IFS=$'\n'; echo "${FAILED_GATES[*]}")"],
  "status": "failed"
}
EOF
    fi
    
    echo "Gate failure logged to: $LOG_ENTRY"
    exit 1
fi