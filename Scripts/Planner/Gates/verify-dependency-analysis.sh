#!/bin/bash

# Gate 4: Dependency Analysis Validation
# Validates dependency graph integrity and execution order

PLAN_FILE="$1"
GATE_NAME="Dependency Analysis Validation"

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
echo "Gate 4: $GATE_NAME"
echo "=========================================="
echo "Plan File: $PLAN_FILE"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "=========================================="

# Extract Dependencies section
DEPS_SECTION=$(sed -n '/^## Dependencies/,/^##/p' "$PLAN_FILE" | sed '$d')

if [ -z "$DEPS_SECTION" ]; then
    echo "❌ GATE FAILED: Dependencies section not found"
    echo "Action: Add Dependencies section to plan"
    echo "Reference: Workflow/Planner/Planner_Plan_Workflow.md - Dependencies section"
    exit 1
fi

# Extract Steps section for step validation
STEPS_SECTION=$(sed -n '/^## Steps/,/^##/p' "$PLAN_FILE" | sed '$d')

# Run the dependency analyzer
PYTHON_SCRIPT="$(dirname "$0")/gate-core/dependency-analyzer.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ GATE FAILED: Dependency analyzer not found: $PYTHON_SCRIPT"
    exit 1
fi

# Check for python availability
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ GATE FAILED: Python not found"
    echo "Install Python 3 to run dependency analysis"
    exit 1
fi

# Create a temporary validation script (inlining Python code directly)
TEMP_SCRIPT_DIR="$(mktemp -d)"

cat > "$TEMP_SCRIPT_DIR/validate_dependencies.py" << 'EOF'
import sys
import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass

@dataclass
class DependencyIssue:
    issue_type: str
    description: str
    steps_involved: List[str]
    severity: str

@dataclass
class DependencyAnalysisResult:
    is_valid: bool
    issues: List[DependencyIssue]
    dependency_graph: Dict[str, List[str]]
    execution_order: List[str]
    warnings: List[str]

class DependencyAnalyzer:
    def __init__(self):
        self.step_pattern = r'step\s*(\d+)'
        self.dependency_pattern = r'step\s*(\d+)'
    
    def analyze_dependencies(self, steps: List, dependency_section: str) -> DependencyAnalysisResult:
        issues = []
        warnings = []
        
        dependency_graph = self._parse_dependency_section(dependency_section)
        
        step_numbers = {step.number for step in steps}
        dependency_numbers = set()
        
        for step_key, dependencies in dependency_graph.items():
            step_num = self._extract_step_number(step_key)
            if step_num:
                dependency_numbers.add(step_num)
                
                if step_num not in step_numbers:
                    issues.append(DependencyIssue(
                        issue_type='missing',
                        description="Dependency references non-existent step " + str(step_num),
                        steps_involved=[step_key],
                        severity='high'
                    ))
            
            for dep in dependencies:
                dep_num = self._extract_step_number(dep)
                if dep_num:
                    if dep_num not in step_numbers:
                        issues.append(DependencyIssue(
                            issue_type='missing',
                            description="Step " + str(step_num) + " depends on non-existent step " + str(dep_num),
                            steps_involved=[step_key, dep],
                            severity='high'
                        ))
        
        circular_issues = self._detect_circular_dependencies(dependency_graph)
        issues.extend(circular_issues)
        
        orphan_issues = self._detect_orphan_steps(step_numbers, dependency_graph)
        issues.extend(orphan_issues)
        
        try:
            execution_order = self._generate_execution_order(dependency_graph)
        except Exception as e:
            issues.append(DependencyIssue(
                issue_type='invalid_format',
                description="Cannot generate execution order: " + str(e),
                steps_involved=list(dependency_graph.keys()),
                severity='critical'
            ))
            execution_order = []
        
        if len(execution_order) > 1:
            parallelizable = self._find_parallelizable_steps(dependency_graph, execution_order)
            if parallelizable:
                warnings.append("Steps that could potentially run in parallel: " + str(parallelizable))
        
        is_valid = all(issue.severity != 'critical' for issue in issues)
        
        return DependencyAnalysisResult(
            is_valid=is_valid,
            issues=issues,
            dependency_graph=dependency_graph,
            execution_order=execution_order,
            warnings=warnings
        )
    
    def _parse_dependency_section(self, content: str) -> Dict[str, List[str]]:
        dependencies = {}
        lines = content.split('\n')
        
        for line in lines:
            dep_match = re.match(r'^step\s*(\d+)\s*[:=]\s*(.+)$', line.strip(), re.IGNORECASE)
            if dep_match:
                step_num = "step_" + str(dep_match.group(1))
                dep_content = dep_match.group(2)
                
                deps = []
                dep_matches = re.findall(r'step\s*(\d+)', dep_content, re.IGNORECASE)
                deps.extend(["step_" + str(match) for match in dep_matches])
                
                dependencies[step_num] = deps
        
        return dependencies
    
    def _extract_step_number(self, step_reference: str) -> int:
        match = re.search(r'step\s*(\d+)', step_reference, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        issues = []
        visited = set()
        recursion_stack = set()
        
        def detect_cycle(node, path):
            if node in recursion_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                issues.append(DependencyIssue(
                    issue_type='circular',
                    description="Circular dependency detected: " + " -> ".join(cycle) + " -> " + node,
                    steps_involved=cycle + [node],
                    severity='critical'
                ))
                return True
            
            if node in visited:
                return False
            
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if detect_cycle(neighbor, path):
                    return True
            
            recursion_stack.remove(node)
            path.pop()
            return False
        
        for node in dependency_graph:
            if node not in visited:
                detect_cycle(node, [])
        
        return issues
    
    def _detect_orphan_steps(self, step_numbers: Set[int], dependency_graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        issues = []
        
        depended_upon = set()
        for deps in dependency_graph.values():
            depended_upon.update(deps)
        
        for step_num in step_numbers:
            step_key = "step_" + str(step_num)
            if step_key not in dependency_graph or not dependency_graph[step_key]:
                if step_key not in depended_upon and len(step_numbers) > 1:
                    issues.append(DependencyIssue(
                        issue_type='orphan',
                        description="Step " + str(step_num) + " has no dependencies and is not depended upon",
                        steps_involved=[step_key],
                        severity='low'
                    ))
        
        return issues
    
    def _generate_execution_order(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        in_degree = {node: 0 for node in dependency_graph}
        for node in dependency_graph:
            for neighbor in dependency_graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        from collections import deque
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        execution_order = []
        
        while queue:
            node = queue.popleft()
            execution_order.append(node)
            
            for neighbor in dependency_graph.get(node, []):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        if len(execution_order) != len(dependency_graph):
            raise ValueError("Cannot generate execution order due to circular dependencies")
        
        return execution_order
    
    def _find_parallelizable_steps(self, dependency_graph: Dict[str, List[str]], execution_order: List[str]) -> List[str]:
        parallelizable = []
        
        reverse_graph = {node: [] for node in dependency_graph}
        for node, deps in dependency_graph.items():
            for dep in deps:
                if dep in reverse_graph:
                    reverse_graph[dep].append(node)
        
        for i, step1 in enumerate(execution_order):
            for step2 in execution_order[i+1:]:
                has_dependency = (
                    step2 in dependency_graph.get(step1, []) or
                    step1 in dependency_graph.get(step2, []) or
                    step1 in reverse_graph.get(step2, []) or
                    step2 in reverse_graph.get(step1, [])
                )
                
                if not has_dependency:
                    parallelizable.append(step1 + " and " + step2)
        
        return parallelizable[:5]

deps_content = sys.argv[1]
steps_content = sys.argv[2] if len(sys.argv) > 2 else ""

analyzer = DependencyAnalyzer()

steps = []
if steps_content:
    for line in steps_content.split('\n'):
        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if match:
            from types import SimpleNamespace
            steps.append(SimpleNamespace(number=int(match.group(1))))

result = analyzer.analyze_dependencies(steps, deps_content)

print("Dependency Graph: " + str(len(result.dependency_graph)) + " steps")
print("Execution Order: " + " -> ".join(result.execution_order))

if result.is_valid:
    print("PASS: Dependency analysis validated")
    print("Issues found: " + str(len(result.issues)))
    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print("  - " + warning)
    sys.exit(0)
else:
    print("FAIL: Dependency analysis validation failed")
    for issue in result.issues:
        print("  - [" + issue.severity.upper() + "] " + issue.description)
    sys.exit(1)
EOF

# Run validation
$PYTHON_CMD "$TEMP_SCRIPT_DIR/validate_dependencies.py" "$DEPS_SECTION" "$STEPS_SECTION"
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
    echo "Action: Fix dependency structure before proceeding"
    echo "Reference: Workflow/Planner/Planner_Plan_Workflow.md - Dependencies section"
    exit 1
fi