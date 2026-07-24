#!/usr/bin/env python3
"""
Dependency analyzer for validating plan dependency structure and integrity.
"""

import re
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass


@dataclass
class DependencyIssue:
    """Represents a dependency issue found during analysis."""
    issue_type: str  # 'circular', 'missing', 'invalid_format', 'orphan'
    description: str
    steps_involved: List[str]
    severity: str  # 'critical', 'high', 'medium', 'low'


@dataclass
class DependencyAnalysisResult:
    """Result of dependency analysis."""
    is_valid: bool
    issues: List[DependencyIssue]
    dependency_graph: Dict[str, List[str]]
    execution_order: List[str]
    warnings: List[str]


class DependencyAnalyzer:
    """Analyzer for plan dependency structure and integrity."""
    
    def __init__(self):
        self.step_pattern = r'step\s*(\d+)'
        self.dependency_pattern = r'step\s*(\d+)'
    
    def analyze_dependencies(self, steps: List, dependency_section: str) -> DependencyAnalysisResult:
        """Analyze the dependency structure of a plan."""
        issues = []
        warnings = []
        
        # Parse dependency section
        dependency_graph = self._parse_dependency_section(dependency_section)
        
        # Validate step references
        step_numbers = {step.number for step in steps}
        dependency_numbers = set()
        
        for step_key, dependencies in dependency_graph.items():
            step_num = self._extract_step_number(step_key)
            if step_num:
                dependency_numbers.add(step_num)
                
                # Check if step exists
                if step_num not in step_numbers:
                    issues.append(DependencyIssue(
                        issue_type='missing',
                        description=f"Dependency references non-existent step {step_num}",
                        steps_involved=[step_key],
                        severity='high'
                    ))
            
            # Validate dependency references
            for dep in dependencies:
                dep_num = self._extract_step_number(dep)
                if dep_num:
                    if dep_num not in step_numbers:
                        issues.append(DependencyIssue(
                            issue_type='missing',
                            description=f"Step {step_num} depends on non-existent step {dep_num}",
                            steps_involved=[step_key, dep],
                            severity='high'
                        ))
        
        # Check for circular dependencies
        circular_issues = self._detect_circular_dependencies(dependency_graph)
        issues.extend(circular_issues)
        
        # Check for orphan steps (no dependencies and not depended upon)
        orphan_issues = self._detect_orphan_steps(step_numbers, dependency_graph)
        issues.extend(orphan_issues)
        
        # Generate execution order
        try:
            execution_order = self._generate_execution_order(dependency_graph)
        except Exception as e:
            issues.append(DependencyIssue(
                issue_type='invalid_format',
                description=f"Cannot generate execution order: {str(e)}",
                steps_involved=list(dependency_graph.keys()),
                severity='critical'
            ))
            execution_order = []
        
        # Check for potential parallelization opportunities
        if len(execution_order) > 1:
            parallelizable = self._find_parallelizable_steps(dependency_graph, execution_order)
            if parallelizable:
                warnings.append(f"Steps that could potentially run in parallel: {parallelizable}")
        
        is_valid = all(issue.severity != 'critical' for issue in issues)
        
        return DependencyAnalysisResult(
            is_valid=is_valid,
            issues=issues,
            dependency_graph=dependency_graph,
            execution_order=execution_order,
            warnings=warnings
        )
    
    def _parse_dependency_section(self, content: str) -> Dict[str, List[str]]:
        """Parse the dependency section content."""
        dependencies = {}
        lines = content.split('\n')
        
        for line in lines:
            # Look for "step N: depends on X, Y, Z" patterns
            dep_match = re.match(r'^step\s*(\d+)\s*[:=]\s*(.+)$', line.strip(), re.IGNORECASE)
            if dep_match:
                step_num = f"step_{dep_match.group(1)}"
                dep_content = dep_match.group(2)
                
                # Extract dependencies
                deps = []
                dep_matches = re.findall(r'step\s*(\d+)', dep_content, re.IGNORECASE)
                deps.extend([f"step_{match}" for match in dep_matches])
                
                dependencies[step_num] = deps
        
        return dependencies
    
    def _extract_step_number(self, step_reference: str) -> int:
        """Extract step number from a step reference."""
        match = re.search(r'step\s*(\d+)', step_reference, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def _detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        """Detect circular dependencies in the dependency graph."""
        issues = []
        visited = set()
        recursion_stack = set()
        
        def detect_cycle(node, path):
            if node in recursion_stack:
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                issues.append(DependencyIssue(
                    issue_type='circular',
                    description=f"Circular dependency detected: {' -> '.join(cycle)} -> {node}",
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
        """Detect steps that have no dependencies and are not depended upon."""
        issues = []
        
        # Get all steps that are depended upon
        depended_upon = set()
        for deps in dependency_graph.values():
            depended_upon.update(deps)
        
        # Find steps that have no dependencies and are not depended upon
        for step_num in step_numbers:
            step_key = f"step_{step_num}"
            if step_key not in dependency_graph or not dependency_graph[step_key]:
                if step_key not in depended_upon and len(step_numbers) > 1:
                    issues.append(DependencyIssue(
                        issue_type='orphan',
                        description=f"Step {step_num} has no dependencies and is not depended upon",
                        steps_involved=[step_key],
                        severity='low'
                    ))
        
        return issues
    
    def _generate_execution_order(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """Generate a valid execution order using topological sort."""
        # Build in-degree count
        in_degree = {node: 0 for node in dependency_graph}
        for node in dependency_graph:
            for neighbor in dependency_graph[node]:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1
        
        # Initialize queue with nodes having in-degree 0
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
        
        # Check if topological sort was successful (no cycles)
        if len(execution_order) != len(dependency_graph):
            raise ValueError("Cannot generate execution order due to circular dependencies")
        
        return execution_order
    
    def _find_parallelizable_steps(self, dependency_graph: Dict[str, List[str]], execution_order: List[str]) -> List[str]:
        """Find steps that could potentially run in parallel."""
        parallelizable = []
        
        # Build reverse dependency graph (what depends on what)
        reverse_graph = {node: [] for node in dependency_graph}
        for node, deps in dependency_graph.items():
            for dep in deps:
                if dep in reverse_graph:
                    reverse_graph[dep].append(node)
        
        # Find steps that have no dependencies between them
        for i, step1 in enumerate(execution_order):
            for step2 in execution_order[i+1:]:
                # Check if step1 and step2 have any dependency relationship
                has_dependency = (
                    step2 in dependency_graph.get(step1, []) or
                    step1 in dependency_graph.get(step2, []) or
                    step1 in reverse_graph.get(step2, []) or
                    step2 in reverse_graph.get(step1, [])
                )
                
                if not has_dependency:
                    parallelizable.append(f"{step1} and {step2}")
        
        return parallelizable[:5]  # Limit to first 5 examples


if __name__ == "__main__":
    # Test the dependency analyzer
    analyzer = DependencyAnalyzer()
    
    # Test with valid dependencies
    valid_deps = """
step_1: []
step_2: [step_1]
step_3: [step_1]
step_4: [step_2, step_3]
"""
    
    result = analyzer.analyze_dependencies([], valid_deps)
    print(f"Valid dependencies: {result.is_valid}")
    print(f"Execution order: {result.execution_order}")
    print(f"Issues: {[(i.issue_type, i.description) for i in result.issues]}")
    
    # Test with circular dependencies
    circular_deps = """
step_1: [step_2]
step_2: [step_3]
step_3: [step_1]
"""
    
    result = analyzer.analyze_dependencies([], circular_deps)
    print(f"\nCircular dependencies: {result.is_valid}")
    print(f"Issues: {[(i.issue_type, i.description) for i in result.issues]}")