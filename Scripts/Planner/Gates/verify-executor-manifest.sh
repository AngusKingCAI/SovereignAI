#!/bin/bash

# Gate 3: Executor Manifest Validation
# Validates Executor Manifest completeness and format

PLAN_FILE="$1"
GATE_NAME="Executor Manifest Validation"

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
echo "Gate 3: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Extract Executor Manifest section
MANIFEST_SECTION=$(sed -n '/^## Executor Manifest/,/^##/p' "$PLAN_FILE" | sed '$d')

if [ -z "$MANIFEST_SECTION" ]; then
    echo "❌ GATE FAILED: Executor Manifest section not found"
    echo "Action: Add Executor Manifest section to plan"
    echo "Reference: Workflow/Planner/Planner_Plan_Workflow.md - Executor Manifest section"
    exit 1
fi

# Run the manifest validator
PYTHON_SCRIPT="$(dirname "$0")/gate-core/manifest-validator.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ GATE FAILED: Manifest validator not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check for python availability
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ GATE FAILED: Python not found"
    echo "Install Python 3 to run manifest validation"
    exit 1
fi

# Create a temporary validation script (inlining Python code directly)
TEMP_SCRIPT_DIR="$(mktemp -d)"

cat > "$TEMP_SCRIPT_DIR/validate_manifest.py" << 'EOF'
import sys
import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ManifestField:
    name: str
    required: bool
    found: bool
    value: Optional[str]
    errors: List[str]

@dataclass
class ManifestValidationResult:
    is_valid: bool
    completeness_score: float
    fields: Dict[str, ManifestField]
    errors: List[str]
    warnings: List[str]

class ManifestValidator:
    def __init__(self):
        self.required_fields = {
            'identity': {'required': True, 'patterns': [r'identity\s*[:=]\s*(.+)']},
            'capabilities': {'required': True, 'patterns': [r'capabilities\s*[:=]\s*(.+)']},
        }
        
        self.optional_fields = {
            'input_schemas': {'required': False, 'patterns': [r'input\s+schema[s]?\s*[:=]\s*(.+)']},
            'output_schemas': {'required': False, 'patterns': [r'output\s+schema[s]?\s*[:=]\s*(.+)']},
        }
    
    def validate_manifest_section(self, manifest_content: str) -> ManifestValidationResult:
        fields = {}
        errors = []
        warnings = []
        
        for field_name, field_config in self.required_fields.items():
            field_result = self._check_field(manifest_content, field_name, field_config)
            fields[field_name] = field_result
            
            if field_config['required'] and not field_result.found:
                errors.append("Missing required field: " + field_name)
            elif field_result.errors:
                errors.extend(field_result.errors)
        
        for field_name, field_config in self.optional_fields.items():
            field_result = self._check_field(manifest_content, field_name, field_config)
            fields[field_name] = field_result
            
            if not field_result.found:
                warnings.append("Optional field not found: " + field_name)
        
        required_count = len([f for f in self.required_fields.values() if f['required']])
        found_required = sum(1 for f_name, f_config in self.required_fields.items() if f_config['required'] and fields[f_name].found)
        completeness_score = (found_required / required_count) * 100 if required_count > 0 else 0
        
        self._validate_field_values(fields, errors, warnings)
        
        is_valid = (len(errors) == 0) and (completeness_score == 100)
        
        return ManifestValidationResult(
            is_valid=is_valid,
            completeness_score=completeness_score,
            fields=fields,
            errors=errors,
            warnings=warnings
        )
    
    def _check_field(self, content: str, field_name: str, field_config: dict) -> ManifestField:
        found = False
        value = None
        errors = []
        
        for pattern in field_config['patterns']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                found = True
                value = match.group(1).strip()
                break
        
        if found and value:
            field_errors = self._validate_field_value(field_name, value)
            errors.extend(field_errors)
        
        return ManifestField(
            name=field_name,
            required=field_config['required'],
            found=found,
            value=value,
            errors=errors
        )
    
    def _validate_field_value(self, field_name: str, value: str) -> List[str]:
        errors = []
        
        if field_name == 'identity':
            if not value or len(value) < 3:
                errors.append("Identity must be at least 3 characters")
        
        elif field_name == 'capabilities':
            if not value:
                errors.append("Capabilities cannot be empty")
            else:
                if ',' not in value and not value.startswith('['):
                    errors.append("Capabilities should be a comma-separated list")
        
        elif field_name == 'token_budget':
            if not re.match(r'^\d+$|^\d+-\d+$', value.strip()):
                errors.append("Token budget should be a number or range (e.g., '1000' or '500-2000')")
        
        return errors
    
    def _validate_field_values(self, fields: Dict[str, ManifestField], errors: List[str], warnings: List[str]):
        if 'identity' in fields and 'capabilities' in fields:
            if fields['identity'].found and fields['capabilities'].found:
                identity = fields['identity'].value
                capabilities = fields['capabilities'].value
                
                if identity and identity.lower() in capabilities.lower():
                    warnings.append("Identity '" + identity + "' should not be listed in capabilities")
        
        if 'token_budget' in fields and fields['token_budget'].found:
            try:
                budget_str = fields['token_budget'].value
                if '-' in budget_str:
                    min_bud, max_bud = map(int, budget_str.split('-'))
                    if min_bud >= max_bud:
                        errors.append("Token budget range must have minimum less than maximum")
                else:
                    budget = int(budget_str)
                    if budget < 100:
                        warnings.append("Token budget seems very low (< 100 tokens)")
                    elif budget > 100000:
                        warnings.append("Token budget seems very high (> 100,000 tokens)")
            except ValueError:
                pass

manifest_content = sys.argv[1]
validator = ManifestValidator()
result = validator.validate_manifest_section(manifest_content)

print("Completeness Score: " + str(round(result.completeness_score, 1)) + "%")

if result.is_valid:
    print("PASS: Executor Manifest validated")
    print("Fields validated: " + str(len(result.fields)))
    for field_name, field in result.fields.items():
        status = "OK" if field.found else "MISSING"
        req = "(required)" if field.required else "(optional)"
        print("  " + status + " " + field_name + ": " + req)
    sys.exit(0)
else:
    print("FAIL: Executor Manifest validation failed")
    for error in result.errors:
        print("  - " + error)
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print("  - " + warning)
    sys.exit(1)
EOF

# Run validation
$PYTHON_CMD "$TEMP_SCRIPT_DIR/validate_manifest.py" "$MANIFEST_SECTION"
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
    echo "Action: Complete Executor Manifest per specification"
    echo "Reference: Workflow/Planner/Planner_Plan_Workflow.md - Executor Manifest section"
    exit 1
fi