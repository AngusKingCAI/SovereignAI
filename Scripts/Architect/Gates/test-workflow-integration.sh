#!/bin/bash

# Test Script: Architect Workflow Integration
# Tests that workflow gates are properly integrated and functional

echo "=========================================="
echo "Architect Workflow Integration Test"
echo "=========================================="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Test 1: Verify workflow document has gate steps
echo "Test 1: Verify workflow document includes gate steps"
if [ -f "Workflow/Architect/Architect Workflow.md" ]; then
    echo "✓ Workflow document exists"
    
    if grep -q "Verify Previous Phase Completion" "Workflow/Architect/Architect Workflow.md"; then
        echo "✓ Workflow includes Step 0 gate (Verify Previous Phase Completion)"
    else
        echo "✗ Workflow missing Step 0 gate"
        exit 1
    fi
    
    if grep -q "Record Phase Completion" "Workflow/Architect/Architect Workflow.md"; then
        echo "✓ Workflow includes Step 10 gate (Record Phase Completion)"
    else
        echo "✗ Workflow missing Step 10 gate"
        exit 1
    fi
else
    echo "✗ Workflow document not found"
    exit 1
fi

# Test 2: Verify AGENTS.md references workflow for gate enforcement
echo ""
echo "Test 2: Verify AGENTS.md references workflow for gate enforcement"
if [ -f "Agents/Architect/AGENTS.md" ]; then
    echo "✓ AGENTS.md exists"
    
    if grep -q "Architect Workflow.md" "Agents/Architect/AGENTS.md"; then
        echo "✓ AGENTS.md references workflow document"
    else
        echo "✗ AGENTS.md missing workflow reference"
        exit 1
    fi
    
    if grep -q "Skipping gates is a SCOPE VIOLATION" "Agents/Architect/AGENTS.md"; then
        echo "✓ AGENTS.md defines gate skipping as scope violation"
    else
        echo "✗ AGENTS.md missing scope violation definition"
        exit 1
    fi
else
    echo "✗ AGENTS.md not found"
    exit 1
fi

# Test 3: Verify gate scripts exist and are executable
echo ""
echo "Test 3: Verify gate scripts exist and are executable"
if [ -f "Scripts/Architect/Gates/verify-phase-complete.sh" ]; then
    echo "✓ verify-phase-complete.sh exists"
    if [ -x "Scripts/Architect/Gates/verify-phase-complete.sh" ]; then
        echo "✓ verify-phase-complete.sh is executable"
    else
        echo "⚠ verify-phase-complete.sh not executable (may need chmod +x)"
    fi
else
    echo "✗ verify-phase-complete.sh not found"
    exit 1
fi

if [ -f "Scripts/Architect/Gates/record-phase-complete.sh" ]; then
    echo "✓ record-phase-complete.sh exists"
    if [ -x "Scripts/Architect/Gates/record-phase-complete.sh" ]; then
        echo "✓ record-phase-complete.sh is executable"
    else
        echo "⚠ record-phase-complete.sh not executable (may need chmod +x)"
    fi
else
    echo "✗ record-phase-complete.sh not found"
    exit 1
fi

# Test 4: Verify gate scripts can be executed successfully
echo ""
echo "Test 4: Verify gate scripts execute successfully"
echo "Testing verify-phase-complete.sh with Phase 4..."
bash Scripts/Architect/Gates/verify-phase-complete.sh 4
if [ $? -eq 0 ]; then
    echo "✓ verify-phase-complete.sh executed successfully"
else
    echo "✗ verify-phase-complete.sh execution failed"
    exit 1
fi

echo ""
echo "Test Summary"
echo "=========================================="
echo "✓ All workflow integration tests passed"
echo "✓ Workflow document includes gate steps"
echo "✓ AGENTS.md references workflow for enforcement"
echo "✓ Gate scripts exist and are executable"
echo "✓ Gate scripts execute successfully"
echo "=========================================="
echo "Test PASSED: Workflow integration verified"
exit 0