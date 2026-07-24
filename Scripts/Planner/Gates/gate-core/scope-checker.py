#!/usr/bin/env python3
"""
Scope checker for validating planning scope compliance.
Detects implementation details that violate planning-only scope.
"""

import re
from pathlib import Path
from typing import List, Tuple


class ScopeChecker:
    """Checker for ensuring plans contain only planning content, not implementation details."""
    
    def __init__(self):
        # Patterns that indicate implementation work
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
            'script_execution': r'\brun\s+script',
            'execute_command': r'\bexecute\s+\w+',
            'api_call': r'\bapi\s+call',
            'database_query': r'\b(query|execute)\s+(sql|database)',
        }
        
        # Planning-specific keywords that are allowed
        self.planning_keywords = [
            'plan', 'design', 'specify', 'define', 'outline', 'structure',
            'document', 'describe', 'propose', 'suggest', 'recommend',
            'analyze', 'evaluate', 'assess', 'consider', 'review'
        ]
    
    def check_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Check a plan file for scope compliance."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.check_content(content)
            
        except Exception as e:
            return False, [f"Scope check error: {str(e)}"]
    
    def check_content(self, content: str) -> Tuple[bool, List[str]]:
        """Check content for scope compliance."""
        violations = []
        
        for pattern_name, pattern in self.implementation_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Get context for the violation
                violation_context = self._get_violation_context(content, pattern, matches[0])
                violations.append(
                    f"Implementation pattern '{pattern_name}' detected: {violation_context}"
                )
        
        # Check for allowed planning keywords to reduce false positives
        if violations:
            planning_content = self._check_planning_content(content)
            if planning_content:
                violations.append(
                    f"Note: Plan contains planning keywords: {', '.join(planning_content[:3])}"
                )
        
        return (len(violations) == 0, violations)
    
    def _get_violation_context(self, content: str, pattern: str, match: str) -> str:
        """Get context around a violation for better error messages."""
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                # Get surrounding lines for context
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = '\n'.join(lines[start:end])
                return f"Line {i + 1}: {context.strip()}"
        return f"Pattern match: {match}"
    
    def _check_planning_content(self, content: str) -> List[str]:
        """Check if content contains planning keywords to reduce false positives."""
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in self.planning_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def get_scope_compliance_report(self, file_path: str) -> dict:
        """Generate a detailed scope compliance report."""
        is_compliant, violations = self.check_file(file_path)
        
        return {
            'file_path': file_path,
            'is_compliant': is_compliant,
            'violations': violations,
            'violation_count': len(violations),
            'compliance_score': max(0, 100 - (len(violations) * 10))
        }


if __name__ == "__main__":
    # Test the scope checker
    checker = ScopeChecker()
    
    # Test with planning content (should pass)
    planning_content = """
# Plan 1 — Test Plan

**Goal**: Plan the test infrastructure

## Steps
1. Design the test framework structure
2. Define test requirements and specifications
3. Plan test implementation approach
4. Document test strategy
"""
    
    is_valid, violations = checker.check_content(planning_content)
    print(f"Planning content valid: {is_valid}")
    print(f"Violations: {violations}")
    
    # Test with implementation content (should fail)
    implementation_content = """
# Plan 1 — Test Plan

**Goal**: Implement the test framework

## Steps
1. Write test_function() to validate inputs
2. Create class TestRunner for execution
3. Import pytest for testing
4. Execute the test script
"""
    
    is_valid, violations = checker.check_content(implementation_content)
    print(f"\nImplementation content valid: {is_valid}")
    print(f"Violations: {violations}")