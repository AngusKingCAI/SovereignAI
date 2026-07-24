#!/bin/bash

# Gate 4: Quality Assessment Validation
# Validates plan quality against Quality_Rubric.md criteria

PLAN_FILE="$1"
GATE_NAME="Quality Assessment Validation"

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
echo "Gate 4: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Check for quality rubric
RUBRIC_FILE="Workflow/Planner/Quality_Rubric.md"
if [ ! -f "$RUBRIC_FILE" ]; then
    echo "WARNING: Quality_Rubric.md not found at $RUBRIC_FILE"
    echo "Proceeding with basic quality checks"
    RUBRIC_FILE=""
fi

# Create temporary directory for Python script
TEMP_SCRIPT_DIR=$(mktemp -d)
trap "rm -rf '$TEMP_SCRIPT_DIR'" EXIT

# Check for Python command (Windows compatibility)
PYTHON_CMD=""
if [ -f "C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe" ]; then
    PYTHON_CMD="C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
elif command -v python.exe &> /dev/null; then
    PYTHON_CMD="python.exe"
else
    echo "ERROR: Python not found. Please install Python 3."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Test Python availability
if ! $PYTHON_CMD --version &> /dev/null; then
    echo "ERROR: Python command '$PYTHON_CMD' not working"
    echo "Attempting direct Python call..."
    if [ -f "C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe" ]; then
        PYTHON_CMD="C:/Users/King/AppData/Local/Programs/Python/Python311/python.exe"
        echo "Found Python at: $PYTHON_CMD"
        if ! $PYTHON_CMD --version &> /dev/null; then
            echo "ERROR: Python executable found but not working"
            exit 1
        fi
    else
        exit 1
    fi
fi

# Copy gate-core if it exists
if [ -d "gate-core" ]; then
    cp -r gate-core "$TEMP_SCRIPT_DIR/"
fi

# Create Python validation script
cat > "$TEMP_SCRIPT_DIR/validate_quality.py" << 'EOF'
import sys
import re
from typing import List, Dict, Tuple

class QualityAssessment:
    def __init__(self):
        self.dimensions = {
            'accuracy': {'weight': 0.30, 'score': 0, 'notes': []},
            'completeness': {'weight': 0.25, 'score': 0, 'notes': []},
            'clarity': {'weight': 0.20, 'score': 0, 'notes': []},
            'structure': {'weight': 0.15, 'score': 0, 'notes': []},
            'context': {'weight': 0.10, 'score': 0, 'notes': []}
        }
        self.hard_fails = []
    
    def assess_accuracy(self, content: str) -> int:
        """Assess accuracy: factual correctness and alignment with requirements"""
        score = 5
        notes = []
        
        # Check for goal statement
        if not re.search(r'\*\*Goal\*\*:', content, re.IGNORECASE):
            score = min(score - 2, 1)
            notes.append("Missing goal statement")
        
        # Check for technical accuracy indicators
        if re.search(r'implement|code|script|execute', content, re.IGNORECASE):
            score = min(score - 1, 1)
            notes.append("Contains implementation language (may affect accuracy)")
        
        self.dimensions['accuracy']['score'] = score
        self.dimensions['accuracy']['notes'] = notes
        return score
    
    def assess_completeness(self, content: str) -> int:
        """Assess completeness: inclusion of all necessary elements"""
        score = 5
        notes = []
        
        # Check for required sections
        required_sections = ['Context', 'Steps', 'Dependencies']
        for section in required_sections:
            if not re.search(r'## ' + section, content, re.IGNORECASE):
                score = min(score - 1, 1)
                notes.append(f"Missing required section: {section}")
        
        # Check for metadata
        if not re.search(r'\*\*Revision\*\*:', content, re.IGNORECASE):
            score = min(score - 1, 1)
            notes.append("Missing revision metadata")
        
        if not re.search(r'\*\*Date\*\*:', content, re.IGNORECASE):
            score = min(score - 1, 1)
            notes.append("Missing date metadata")
        
        self.dimensions['completeness']['score'] = score
        self.dimensions['completeness']['notes'] = notes
        return score
    
    def assess_clarity(self, content: str) -> int:
        """Assess clarity: readability and understandability"""
        score = 5
        notes = []
        
        # Check goal statement clarity
        goal_match = re.search(r'\*\*Goal\*\*:\s*(.+)', content, re.IGNORECASE)
        if goal_match:
            goal = goal_match.group(1).strip()
            if len(goal) < 10:
                score = min(score - 1, 1)
                notes.append("Goal statement too short/unclear")
        else:
            score = min(score - 2, 1)
            notes.append("No clear goal statement found")
        
        # Check for vague language
        vague_terms = ['somehow', 'maybe', 'possibly', 'kind of', 'sort of']
        for term in vague_terms:
            if re.search(term, content, re.IGNORECASE):
                score = min(score - 1, 4)
                notes.append(f"Contains vague language: {term}")
                break
        
        self.dimensions['clarity']['score'] = score
        self.dimensions['clarity']['notes'] = notes
        return score
    
    def assess_structure(self, content: str) -> int:
        """Assess structure: organization and logical flow"""
        score = 5
        notes = []
        
        # Check for proper section structure
        section_pattern = r'^##\s+\w+'
        sections = re.findall(section_pattern, content, re.MULTILINE)
        if len(sections) < 3:
            score = min(score - 1, 1)
            notes.append("Insufficient section structure")
        
        # Check for circular dependencies
        if 'circular' in content.lower():
            score = 1
            notes.append("Circular dependencies detected")
            self.hard_fails.append("Circular dependencies")
        
        # Check line count (≤120 lines guideline)
        line_count = len(content.split('\n'))
        if line_count > 120:
            score = min(score - 1, 4)
            notes.append(f"Plan exceeds 120 lines ({line_count} lines)")
        
        self.dimensions['structure']['score'] = score
        self.dimensions['structure']['notes'] = notes
        return score
    
    def assess_context(self, content: str) -> int:
        """Assess context: background information and rationale"""
        score = 5
        notes = []
        
        # Check for context section
        context_match = re.search(r'## Context\s*\n(.*?)(?=##|\Z)', content, re.DOTALL | re.IGNORECASE)
        if context_match:
            context_text = context_match.group(1).strip()
            if len(context_text) < 50:
                score = min(score - 1, 1)
                notes.append("Context section too brief")
        else:
            score = min(score - 2, 1)
            notes.append("Missing or empty context section")
        
        self.dimensions['context']['score'] = score
        self.dimensions['context']['notes'] = notes
        return score
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall quality score"""
        total_score = 0
        for dim_name, dim_data in self.dimensions.items():
            total_score += dim_data['score'] * dim_data['weight']
        return round(total_score, 2)
    
    def assess_plan(self, content: str) -> Tuple[bool, float, List[str]]:
        """Perform complete quality assessment"""
        self.assess_accuracy(content)
        self.assess_completeness(content)
        self.assess_clarity(content)
        self.assess_structure(content)
        self.assess_context(content)
        
        overall_score = self.calculate_overall_score()
        
        # Collect all notes
        all_notes = []
        for dim_name, dim_data in self.dimensions.items():
            if dim_data['notes']:
                all_notes.append(f"{dim_name}: {', '.join(dim_data['notes'])}")
        
        # Check for hard fails
        is_valid = len(self.hard_fails) == 0 and overall_score >= 2.5
        
        return is_valid, overall_score, all_notes

# Read plan file
plan_file = sys.argv[1]
with open(plan_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Perform quality assessment
assessor = QualityAssessment()
is_valid, overall_score, notes = assessor.assess_plan(content)

print("Quality Assessment Results")
print("==========================================")
print("Overall Quality Score: " + str(overall_score) + "/5.0")
print("")
print("Dimension Scores:")
for dim_name, dim_data in assessor.dimensions.items():
    print("  " + dim_name.capitalize() + ": " + str(dim_data['score']) + "/5 (weight: " + str(dim_data['weight']) + ")")

if notes:
    print("")
    print("Notes:")
    for note in notes:
        print("  - " + note)

if assessor.hard_fails:
    print("")
    print("Hard Fails:")
    for fail in assessor.hard_fails:
        print("  - " + fail)

print("")
print("Quality Thresholds:")
print("  5.0 - 4.5: Excellent - Clean pass")
print("  4.4 - 3.5: Good - Clean pass")
print("  3.4 - 2.5: Fair - Proceed with rationale")
print("  2.4 - 1.5: Poor - Requires revisions")
print("  1.4 - 0.0: Critical - Block review")

if is_valid:
    print("")
    print("PASS: Quality assessment validated")
    sys.exit(0)
else:
    print("")
    print("FAIL: Quality assessment validation failed")
    sys.exit(1)
EOF

# Run validation
$PYTHON_CMD "$TEMP_SCRIPT_DIR/validate_quality.py" "$PLAN_FILE"
VALIDATION_RESULT=$?

# Cleanup
rm -rf "$TEMP_SCRIPT_DIR"

if [ $VALIDATION_RESULT -eq 0 ]; then
    echo "=========================================="
    echo "GATE PASSED: $GATE_NAME"
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "GATE FAILED: $GATE_NAME"
    echo "=========================================="
    echo "Action: Improve plan quality before proceeding"
    echo "Reference: Plans/Quality_Rubric.md - Scoring Dimensions"
    exit 1
fi