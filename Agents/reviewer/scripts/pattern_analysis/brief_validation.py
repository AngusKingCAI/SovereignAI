#!/usr/bin/env python3
"""
Brief Validation Script

Validates brief quality before Round Table review.
Ensures briefs meet quality standards for panelist evaluation.
"""

import sys
import os
import json
import argparse
from pathlib import Path
import re

# UTF-8 print helper for Windows console compatibility
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

class BriefValidator:
    """Validates brief quality for Round Table review."""
    
    def __init__(self, brief_file=None):
        """Initialize brief validator."""
        self.brief_file = brief_file
        self.brief_content = ""
        self.validation_results = []
        
    def load_brief(self):
        """Load brief content from file."""
        if not self.brief_file:
            safe_print("No brief file provided")
            return False
        
        try:
            with open(self.brief_file, 'r', encoding='utf-8') as f:
                self.brief_content = f.read()
            
            safe_print(f"Loaded brief from {self.brief_file}")
            return True
            
        except Exception as e:
            safe_print(f"Error loading brief: {e}")
            return False
    
    def validate_structure(self):
        """Validate brief structure."""
        required_sections = [
            '## Brief',
            '## Plan Number',
            '## Title',
            '## Context',
            '## Requirements',
            '## Constraints'
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in self.brief_content:
                missing_sections.append(section)
        
        if missing_sections:
            self.validation_results.append({
                'category': 'structure',
                'status': 'fail',
                'message': f"Missing required sections: {', '.join(missing_sections)}"
            })
            return False
        else:
            self.validation_results.append({
                'category': 'structure',
                'status': 'pass',
                'message': 'All required sections present'
            })
            return True
    
    def validate_content(self):
        """Validate brief content quality."""
        issues = []
        
        # Check for minimum content length
        if len(self.brief_content) < 500:
            issues.append("Brief content too short (< 500 characters)")
        
        # Check for vague terms
        vague_terms = [' TBD ', ' TODO ', ' tbd ', ' todo ', ' pending ', ' TBD:', ' TODO:']
        for term in vague_terms:
            if term in self.brief_content:
                issues.append(f"Found vague term: {term.strip()}")
        
        # Check for missing requirements
        if '## Requirements' in self.brief_content:
            requirements_section = self.brief_content.split('## Requirements')[1].split('##')[0]
            if len(requirements_section.strip()) < 100:
                issues.append("Requirements section too brief")
        
        if issues:
            self.validation_results.append({
                'category': 'content',
                'status': 'fail',
                'message': f"Content quality issues: {', '.join(issues)}"
            })
            return False
        else:
            self.validation_results.append({
                'category': 'content',
                'status': 'pass',
                'message': 'Content quality acceptable'
            })
            return True
    
    def validate_formatting(self):
        """Validate brief formatting."""
        issues = []
        
        # Check for proper heading hierarchy
        lines = self.brief_content.split('\n')
        heading_levels = []
        for line in lines:
            match = re.match(r'^(#+)\s+', line)
            if match:
                level = len(match.group(1))
                heading_levels.append(level)
        
        # Check for invalid heading jumps
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                issues.append(f"Invalid heading level jump at line {i+1}")
        
        # Check for proper markdown formatting
        if not re.search(r'^# ', self.brief_content):
            issues.append("Brief must start with main title (#)")
        
        if issues:
            self.validation_results.append({
                'category': 'formatting',
                'status': 'fail',
                'message': f"Formatting issues: {', '.join(issues)}"
            })
            return False
        else:
            self.validation_results.append({
                'category': 'formatting',
                'status': 'pass',
                'message': 'Formatting acceptable'
            })
            return True
    
    def validate_completeness(self):
        """Validate brief completeness."""
        required_fields = [
            'Plan Number:',
            'Title:',
            'Context:',
            'Requirements:',
            'Constraints:'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in self.brief_content:
                missing_fields.append(field)
        
        if missing_fields:
            self.validation_results.append({
                'category': 'completeness',
                'status': 'fail',
                'message': f"Missing required fields: {', '.join(missing_fields)}"
            })
            return False
        else:
            self.validation_results.append({
                'category': 'completeness',
                'status': 'pass',
                'message': 'All required fields present'
            })
            return True
    
    def run_validation(self):
        """Run complete brief validation."""
        if not self.load_brief():
            return False
        
        # Run all validation checks
        structure_pass = self.validate_structure()
        content_pass = self.validate_content()
        formatting_pass = self.validate_formatting()
        completeness_pass = self.validate_completeness()
        
        # Overall pass if all checks pass
        overall_pass = all([structure_pass, content_pass, formatting_pass, completeness_pass])
        
        return overall_pass
    
    def export_results(self, output_file=None):
        """Export validation results to JSON."""
        results = {
            'validation_timestamp': Path().cwd().name,
            'brief_file': self.brief_file,
            'overall_status': 'pass' if all(r['status'] == 'pass' for r in self.validation_results) else 'fail',
            'validation_results': self.validation_results
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            safe_print(f"✅ Results exported to {output_file}")
        else:
            safe_print(json.dumps(results, indent=2))
        
        return results

def main():
    """Main brief validation pipeline."""
    parser = argparse.ArgumentParser(description='Brief Validation Script')
    parser.add_argument('--brief-file', type=str, required=True, help='Path to brief file')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    
    args = parser.parse_args()
    
    safe_print("Starting Brief Validation...")
    
    # Initialize validator
    validator = BriefValidator(brief_file=args.brief_file)
    
    # Run validation
    if validator.run_validation():
        safe_print("✅ Brief validation passed")
        result = 0
    else:
        safe_print("❌ Brief validation failed")
        result = 1
    
    # Export results
    validator.export_results(args.output)
    
    return result

if __name__ == "__main__":
    sys.exit(main())