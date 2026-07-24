#!/bin/bash

# Gate 1: Plan Structure Validation
# Validates plan format against specification and checks required sections

PLAN_FILE="$1"
GATE_NAME="Plan Structure Validation"

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
echo "Gate 1: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Run the plan parser validation
PYTHON_SCRIPT="$(dirname "$0")/gate-core/plan-parser.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ GATE FAILED: Plan parser not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check for python availability
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ GATE FAILED: Python not found"
    echo "Install Python 3 to run plan structure validation"
    exit 1
fi

# Create a temporary validation script (inlining Python code directly)
TEMP_SCRIPT_DIR="$(mktemp -d")
GATE_CORE_DIR="$(dirname "$PYTHON_SCRIPT")"

cat > "$TEMP_SCRIPT_DIR/validate_plan_structure.py" << 'EOF'
import sys
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class PlanSection:
    name: str
    content: str
    line_start: int
    line_end: int

@dataclass
class PlanStep:
    number: int
    content: str
    dependencies: List[str]
    line_number: int

@dataclass
class ExecutorManifest:
    identity: Optional[str] = None
    capabilities: Optional[List[str]] = None
    input_schemas: Optional[Dict] = None
    output_schemas: Optional[Dict] = None
    token_budget: Optional[str] = None
    complete: bool = False

@dataclass
class ParsedPlan:
    file_path: str
    revision: str
    date: str
    goal: str
    sections: Dict[str, PlanSection]
    steps: List[PlanStep]
    dependencies: Dict[str, List[str]]
    executor_manifest: ExecutorManifest
    errors: List[str]
    warnings: List[str]

class PlanParser:
    def __init__(self):
        self.required_sections = ["Context", "Steps", "Dependencies", "Executor Manifest"]
    
    def parse_file(self, file_path: str) -> ParsedPlan:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            plan = ParsedPlan(
                file_path=file_path,
                revision="",
                date="",
                goal="",
                sections={},
                steps=[],
                dependencies={},
                executor_manifest=ExecutorManifest(),
                errors=[],
                warnings=[]
            )
            
            # Extract metadata
            plan.revision = self._extract_field(content, r'Revision:\s*(.+)')
            plan.date = self._extract_field(content, r'Date:\s*(.+)')
            plan.goal = self._extract_field(content, r'Goal:\s*(.+)')
            
            # Validate metadata
            if not plan.revision:
                plan.errors.append("Missing revision information")
            if not plan.date:
                plan.errors.append("Missing date information")
            if not plan.goal:
                plan.errors.append("Missing goal information")
            
            # Extract sections
            plan.sections = self._extract_sections(content)
            
            # Validate required sections
            for section in self.required_sections:
                if section not in plan.sections:
                    plan.errors.append("Missing required section: " + section)
            
            # Parse steps if present
            if "Steps" in plan.sections:
                plan.steps = self._parse_steps(plan.sections["Steps"].content)
            
            # Parse dependencies if present
            if "Dependencies" in plan.sections:
                plan.dependencies = self._parse_dependencies(plan.sections["Dependencies"].content)
            
            # Parse Executor Manifest if present
            if "Executor Manifest" in plan.sections:
                plan.executor_manifest = self._parse_executor_manifest(plan.sections["Executor Manifest"].content)
            else:
                plan.errors.append("Missing Executor Manifest section")
            
            return plan
            
        except Exception as e:
            return ParsedPlan(
                file_path=file_path,
                revision="",
                date="",
                goal="",
                sections={},
                steps=[],
                dependencies={},
                executor_manifest=ExecutorManifest(),
                errors=["Parse error: " + str(e)],
                warnings=[]
            )
    
    def _extract_field(self, content: str, pattern: str) -> str:
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def _extract_sections(self, content: str) -> Dict[str, PlanSection]:
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        current_line_start = 0
        
        for i, line in enumerate(lines):
            section_match = re.match(r'^##\s+(.+)$', line)
            if section_match:
                if current_section:
                    sections[current_section] = PlanSection(
                        name=current_section,
                        content='\n'.join(current_content).strip(),
                        line_start=current_line_start,
                        line_end=i - 1
                    )
                
                current_section = section_match.group(1).strip()
                current_content = []
                current_line_start = i + 1
            else:
                if current_section:
                    current_content.append(line)
        
        if current_section:
            sections[current_section] = PlanSection(
                name=current_section,
                content='\n'.join(current_content).strip(),
                line_start=current_line_start,
                line_end=len(lines) - 1
            )
        
        return sections
    
    def _parse_steps(self, steps_content: str) -> List[PlanStep]:
        steps = []
        lines = steps_content.split('\n')
        
        for line in lines:
            step_match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
            if step_match:
                step_num = int(step_match.group(1))
                step_content = step_match.group(2)
                dependencies = self._extract_dependencies(step_content)
                
                steps.append(PlanStep(
                    number=step_num,
                    content=step_content,
                    dependencies=dependencies,
                    line_number=lines.index(line) + 1
                ))
        
        return steps
    
    def _extract_dependencies(self, content: str) -> List[str]:
        dependencies = []
        dep_patterns = [
            r'depends?\s+on\s+step\s+(\d+)',
            r'after\s+step\s+(\d+)',
            r'requires?\s+step\s+(\d+)',
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend(["step_" + str(match) for match in matches])
        
        return dependencies
    
    def _parse_dependencies(self, deps_content: str) -> Dict[str, List[str]]:
        dependencies = {}
        lines = deps_content.split('\n')
        
        for line in lines:
            dep_match = re.match(r'^step\s*(\d+)\s*[:=]\s*(.+)$', line.strip(), re.IGNORECASE)
            if dep_match:
                step_num = "step_" + str(dep_match.group(1))
                dep_list = [d.strip() for d in dep_match.group(2).split(',')]
                dependencies[step_num] = dep_list
        
        return dependencies
    
    def _parse_executor_manifest(self, manifest_content: str) -> ExecutorManifest:
        manifest = ExecutorManifest()
        lines = manifest_content.split('\n')
        
        for line in lines:
            if 'identity' in line.lower():
                identity_match = re.search(r'identity\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if identity_match:
                    manifest.identity = identity_match.group(1).strip()
            
            if 'capabilities' in line.lower():
                caps_match = re.search(r'capabilities\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if caps_match:
                    caps_str = caps_match.group(1).strip()
                    manifest.capabilities = [c.strip() for c in caps_str.split(',')]
            
            if 'token' in line.lower() and 'budget' in line.lower():
                token_match = re.search(r'token\s+budget\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if token_match:
                    manifest.token_budget = token_match.group(1).strip()
        
        manifest.complete = bool(
            manifest.identity and 
            manifest.capabilities and 
            manifest.token_budget
        )
        
        return manifest
    
    def validate_structure(self, plan: ParsedPlan) -> tuple:
        errors = []
        
        for section in self.required_sections:
            if section not in plan.sections:
                errors.append("Missing required section: " + section)
        
        if not plan.revision:
            errors.append("Missing revision information")
        if not plan.date:
            errors.append("Missing date information")
        if not plan.goal:
            errors.append("Missing goal information")
        
        if not plan.steps:
            errors.append("No steps defined in plan")
        
        if not plan.executor_manifest.complete:
            errors.append("Executor Manifest is incomplete")
        
        return (len(errors) == 0, errors)

plan_file = sys.argv[1]
parser = PlanParser()
parsed = parser.parse_file(plan_file)
is_valid, errors = parser.validate_structure(parsed)

if is_valid:
    print("PASS: Plan structure validated")
    print("Sections found: " + str(list(parsed.sections.keys())))
    print("Steps defined: " + str(len(parsed.steps)))
    print("Executor Manifest complete: " + str(parsed.executor_manifest.complete))
    sys.exit(0)
else:
    print("FAIL: Plan structure validation failed")
    for error in errors:
        print("  - " + str(error))
    sys.exit(1)
EOF

# Run validation
$PYTHON_CMD "$TEMP_SCRIPT_DIR/validate_plan_structure.py" "$PLAN_FILE"
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
    echo "Action: Fix plan structure before proceeding"
    echo "Reference: Workflow/Planner/Plan.md - Plan Format section"
    exit 1
fi