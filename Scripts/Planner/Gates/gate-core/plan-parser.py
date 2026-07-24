#!/usr/bin/env python3
"""
Plan parser for validating plan structure and content.
Parses plan files and extracts structured data for gate validation.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PlanSection:
    """Represents a section in a plan file."""
    name: str
    content: str
    line_start: int
    line_end: int


@dataclass
class PlanStep:
    """Represents a step in a plan."""
    number: int
    content: str
    dependencies: List[str]
    line_number: int


@dataclass
class ExecutorManifest:
    """Represents the Executor Manifest from a plan."""
    identity: Optional[str] = None
    capabilities: Optional[List[str]] = None
    input_schemas: Optional[Dict] = None
    output_schemas: Optional[Dict] = None
    token_budget: Optional[str] = None
    complete: bool = False


@dataclass
class ParsedPlan:
    """Represents a fully parsed plan file."""
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
    """Parser for plan files following the specification format."""
    
    def __init__(self):
        self.required_sections = ["Context", "Steps", "Dependencies", "Executor Manifest"]
        self.implementation_patterns = [
            r'\bdef\s+\w+\s*\(',  # Function definitions
            r'\bclass\s+\w+\s*:',  # Class definitions
            r'\bimport\s+\w+',  # Import statements
            r'\bfrom\s+\w+\s+import',  # From imports
            r'\w+\s*=\s*\w+\(.*\)',  # Function calls
            r'```python',  # Python code blocks
            r'```javascript',  # JavaScript code blocks
            r'```bash',  # Bash code blocks
            r'\bwrite\s+file',  # File write operations
            r'\bcreate\s+file',  # File creation operations
            r'\bimplement\s+',  # Implementation language
            r'\bcode\s+implementation',  # Code implementation
        ]
    
    def parse_file(self, file_path: str) -> ParsedPlan:
        """Parse a plan file and return structured data."""
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
                    plan.errors.append(f"Missing required section: {section}")
            
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
            
            # Check for implementation details
            scope_violations = self._check_scope_compliance(content)
            if scope_violations:
                plan.errors.extend(scope_violations)
            
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
                errors=[f"Parse error: {str(e)}"],
                warnings=[]
            )
    
    def _extract_field(self, content: str, pattern: str) -> str:
        """Extract a field from content using regex pattern."""
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""
    
    def _extract_sections(self, content: str) -> Dict[str, PlanSection]:
        """Extract all sections from plan content."""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        current_line_start = 0
        
        for i, line in enumerate(lines):
            # Check for section headers (## Level 2 headers)
            section_match = re.match(r'^##\s+(.+)$', line)
            if section_match:
                # Save previous section if exists
                if current_section:
                    sections[current_section] = PlanSection(
                        name=current_section,
                        content='\n'.join(current_content).strip(),
                        line_start=current_line_start,
                        line_end=i - 1
                    )
                
                # Start new section
                current_section = section_match.group(1).strip()
                current_content = []
                current_line_start = i + 1
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = PlanSection(
                name=current_section,
                content='\n'.join(current_content).strip(),
                line_start=current_line_start,
                line_end=len(lines) - 1
            )
        
        return sections
    
    def _parse_steps(self, steps_content: str) -> List[PlanStep]:
        """Parse steps from the Steps section."""
        steps = []
        lines = steps_content.split('\n')
        
        for line in lines:
            # Match numbered steps (1., 2., etc.)
            step_match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
            if step_match:
                step_num = int(step_match.group(1))
                step_content = step_match.group(2)
                
                # Extract dependencies (look for "depends on" or similar)
                dependencies = self._extract_dependencies(step_content)
                
                steps.append(PlanStep(
                    number=step_num,
                    content=step_content,
                    dependencies=dependencies,
                    line_number=lines.index(line) + 1
                ))
        
        return steps
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependency references from step content."""
        dependencies = []
        # Look for patterns like "depends on step 1", "after step 2", etc.
        dep_patterns = [
            r'depends?\s+on\s+step\s+(\d+)',
            r'after\s+step\s+(\d+)',
            r'requires?\s+step\s+(\d+)',
            r'following\s+step\s+(\d+)',
        ]
        
        for pattern in dep_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dependencies.extend([f"step_{match}" for match in matches])
        
        return dependencies
    
    def _parse_dependencies(self, deps_content: str) -> Dict[str, List[str]]:
        """Parse the Dependencies section."""
        dependencies = {}
        lines = deps_content.split('\n')
        
        for line in lines:
            # Look for "step N: depends on X, Y, Z" patterns
            dep_match = re.match(r'^step\s+(\d+):\s*(.+)$', line.strip(), re.IGNORECASE)
            if dep_match:
                step_num = f"step_{dep_match.group(1)}"
                dep_list = [d.strip() for d in dep_match.group(2).split(',')]
                dependencies[step_num] = dep_list
        
        return dependencies
    
    def _parse_executor_manifest(self, manifest_content: str) -> ExecutorManifest:
        """Parse the Executor Manifest section."""
        manifest = ExecutorManifest()
        lines = manifest_content.split('\n')
        
        for line in lines:
            # Parse identity
            if 'identity' in line.lower():
                identity_match = re.search(r'identity\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if identity_match:
                    manifest.identity = identity_match.group(1).strip()
            
            # Parse capabilities
            if 'capabilities' in line.lower():
                caps_match = re.search(r'capabilities\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if caps_match:
                    caps_str = caps_match.group(1).strip()
                    manifest.capabilities = [c.strip() for c in caps_str.split(',')]
            
            # Parse token budget
            if 'token' in line.lower() and 'budget' in line.lower():
                token_match = re.search(r'token\s+budget\s*[:=]\s*(.+)', line, re.IGNORECASE)
                if token_match:
                    manifest.token_budget = token_match.group(1).strip()
            
            # Parse I/O schemas (simplified)
            if 'input' in line.lower() or 'output' in line.lower():
                # Mark that schemas are mentioned (detailed parsing would be more complex)
                if not manifest.input_schemas:
                    manifest.input_schemas = {}
                if not manifest.output_schemas:
                    manifest.output_schemas = {}
        
        # Check completeness
        manifest.complete = bool(
            manifest.identity and 
            manifest.capabilities and 
            manifest.token_budget
        )
        
        return manifest
    
    def _check_scope_compliance(self, content: str) -> List[str]:
        """Check for implementation details that violate planning scope."""
        violations = []
        
        for pattern in self.implementation_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                violations.append(f"Implementation pattern detected: {pattern} (found {len(matches)} times)")
        
        return violations
    
    def validate_structure(self, plan: ParsedPlan) -> Tuple[bool, List[str]]:
        """Validate plan structure against requirements."""
        errors = []
        
        # Check required sections
        for section in self.required_sections:
            if section not in plan.sections:
                errors.append(f"Missing required section: {section}")
        
        # Check metadata
        if not plan.revision:
            errors.append("Missing revision information")
        if not plan.date:
            errors.append("Missing date information")
        if not plan.goal:
            errors.append("Missing goal information")
        
        # Check steps
        if not plan.steps:
            errors.append("No steps defined in plan")
        
        # Check Executor Manifest
        if not plan.executor_manifest.complete:
            errors.append("Executor Manifest is incomplete")
        
        return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test the parser
    parser = PlanParser()
    
    # Create a test plan file
    test_plan = """# Plan 1 — Test Plan

**Revision**: 1.0  
**Date**: 2026-07-24  
**Goal**: Test the plan parser

## Context
This is a test context for the plan parser.

## Steps
1. Create test file
2. Parse test file depends on step 1
3. Validate results depends on step 2

## Dependencies
step_1: []
step_2: [step_1]
step_3: [step_2]

## Executor Manifest
Identity: test-executor
Capabilities: read, write, parse
Token Budget: 1000
"""
    
    # Write test plan (Windows-compatible)
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        test_path = f.name
        f.write(test_plan)
    
    try:
        # Parse the test plan
        parsed = parser.parse_file(test_path)
        
        # Print results
        print(f"Plan: {parsed.file_path}")
        print(f"Revision: {parsed.revision}")
        print(f"Date: {parsed.date}")
        print(f"Goal: {parsed.goal}")
        print(f"Sections: {list(parsed.sections.keys())}")
        print(f"Steps: {len(parsed.steps)}")
        print(f"Dependencies: {parsed.dependencies}")
        print(f"Executor Manifest Complete: {parsed.executor_manifest.complete}")
        print(f"Errors: {parsed.errors}")
        print(f"Warnings: {parsed.warnings}")
        
        # Validate structure
        is_valid, structure_errors = parser.validate_structure(parsed)
        print(f"\nStructure Valid: {is_valid}")
        print(f"Structure Errors: {structure_errors}")
    finally:
        # Clean up
        os.unlink(test_path)