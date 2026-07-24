#!/bin/bash

# Gate 2: Scope Compliance Validation
# Validates that plans contain only planning content, no implementation details

PLAN_FILE="$1"
GATE_NAME="Scope Compliance Validation"

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
echo "Gate 2: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Run the scope checker
PYTHON_SCRIPT="$(dirname "$0")/gate-core/scope-checker.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ GATE FAILED: Scope checker not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check for python availability
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ GATE FAILED: Python not found"
    echo "Install Python 3 to run scope compliance validation"
    exit 1
fi

# Create a temporary validation script (inlining Python code directly)
TEMP_SCRIPT_DIR="$(mktemp -d)"

cat > "$TEMP_SCRIPT_DIR/validate_scope_compliance.py" << 'EOF'
import sys
import re
from typing import List, Tuple

class ScopeChecker:
    def __init__(self):
        self.implementation_patterns = {
            'function_definition': r'\bdef\s+\w+\s*\(',
            'class_definition': r'\bclass\s+\w+\s*:',
            'import_statement': r'\bimport\s+\w+',
            'from_import': r'\bfrom\s+\w+\s+import',
            'function_call': r'\w+\s*=\s*\w+\(.*\)',
            'python_code_block': r'```python',
            'javascript_code_block': r'```javascript',
            'bash_code_block': r'```bash',
            'file_write': r'\bwrite\s+file',
            'file_create': r'\bcreate\s+file',
            'implement_keyword': r'\bimplement\s+',
            'code_implementation': r'\bcode\s+implementation',
        }
        
        self.planning_keywords = [
            'plan', 'design', 'specify', 'define', 'outline', 'structure',
            'document', 'describe', 'propose', 'suggest', 'recommend',
            'analyze', 'evaluate', 'assess', 'consider', 'review'
        ]
    
    def check_file(self, file_path: str) -> Tuple[bool, List[str]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.check_content(content)
        except Exception as e:
            return False, ["Scope check error: " + str(e)]
    
    def check_content(self, content: str) -> Tuple[bool, List[str]]:
        violations = []
        
        for pattern_name, pattern in self.implementation_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violation_context = self._get_violation_context(content, pattern, matches[0])
                violations.append(
                    "Implementation pattern '" + pattern_name + "' detected: " + violation_context
                )
        
        if violations:
            planning_content = self._check_planning_content(content)
            if planning_content:
                violations.append(
                    "Note: Plan contains planning keywords: " + ", ".join(planning_content[:3])
                )
        
        return (len(violations) == 0, violations)
    
    def _get_violation_context(self, content: str, pattern: str, match: str) -> str:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = '\n'.join(lines[start:end])
                return "Line " + str(i + 1) + ": " + context.strip()
        return "Pattern match: " + match
    
    def _check_planning_content(self, content: str) -> List[str]:
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in self.planning_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords

plan_file = sys.argv[1]
checker = ScopeChecker()
is_compliant, violations = checker.check_file(plan_file)

if is_compliant:
    print("PASS: Scope compliance validated")
    print("Plan contains planning content only (no implementation details)")
    sys.exit(0)
else:
    print("FAIL: Scope compliance validation failed")
    print("Violations found: " + str(len(violations)))
    for violation in violations:
        print("  - " + violation)
    sys.exit(1)
EOF

# Run validation
$PYTHON_CMD "$TEMP_SCRIPT_DIR/validate_scope_compliance.py" "$PLAN_FILE"
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
    echo "Action: Remove implementation details, planning only"
    echo "Reference: .devin/skills/planner-scope/SKILL.md - Scope Boundaries"
    exit 1
fi