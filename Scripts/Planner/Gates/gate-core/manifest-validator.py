#!/usr/bin/env python3
"""
Executor Manifest validator for validating Executor Manifest completeness and format.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ManifestField:
    """Represents a field in the Executor Manifest."""
    name: str
    required: bool
    found: bool
    value: Optional[str]
    errors: List[str]


@dataclass
class ManifestValidationResult:
    """Result of Executor Manifest validation."""
    is_valid: bool
    completeness_score: float
    fields: Dict[str, ManifestField]
    errors: List[str]
    warnings: List[str]


class ManifestValidator:
    """Validator for Executor Manifest sections in plans."""
    
    def __init__(self):
        self.required_fields = {
            'identity': {'required': True, 'patterns': [r'identity\s*[:=]\s*(.+)']},
            'capabilities': {'required': True, 'patterns': [r'capabilities\s*[:=]\s*(.+)']},
            'token_budget': {'required': True, 'patterns': [r'token\s+budget\s*[:=]\s*(.+)']},
        }
        
        self.optional_fields = {
            'input_schemas': {'required': False, 'patterns': [r'input\s+schema[s]?\s*[:=]\s*(.+)']},
            'output_schemas': {'required': False, 'patterns': [r'output\s+schema[s]?\s*[:=]\s*(.+)']},
            'timeout': {'required': False, 'patterns': [r'timeout\s*[:=]\s*(.+)']},
            'memory_limit': {'required': False, 'patterns': [r'memory\s+limit\s*[:=]\s*(.+)']},
        }
    
    def validate_manifest_section(self, manifest_content: str) -> ManifestValidationResult:
        """Validate the Executor Manifest section content."""
        fields = {}
        errors = []
        warnings = []
        
        # Check required fields
        for field_name, field_config in self.required_fields.items():
            field_result = self._check_field(manifest_content, field_name, field_config)
            fields[field_name] = field_result
            
            if field_config['required'] and not field_result.found:
                errors.append(f"Missing required field: {field_name}")
            elif field_result.errors:
                errors.extend(field_result.errors)
        
        # Check optional fields
        for field_name, field_config in self.optional_fields.items():
            field_result = self._check_field(manifest_content, field_name, field_config)
            fields[field_name] = field_result
            
            if not field_result.found:
                warnings.append(f"Optional field not found: {field_name}")
        
        # Calculate completeness score
        required_count = len(self.required_fields)
        found_required = sum(1 for f in fields.values() if f.found and f.name in self.required_fields)
        completeness_score = (found_required / required_count) * 100 if required_count > 0 else 0
        
        # Additional validation checks
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
        """Check if a field exists in the content and extract its value."""
        found = False
        value = None
        errors = []
        
        for pattern in field_config['patterns']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                found = True
                value = match.group(1).strip()
                break
        
        # Validate field value if found
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
        """Validate the value of a specific field."""
        errors = []
        
        if field_name == 'identity':
            if not value or len(value) < 3:
                errors.append("Identity must be at least 3 characters")
        
        elif field_name == 'capabilities':
            if not value:
                errors.append("Capabilities cannot be empty")
            else:
                # Check if it's a list-like format
                if ',' not in value and not value.startswith('['):
                    errors.append("Capabilities should be a comma-separated list")
        
        elif field_name == 'token_budget':
            # Check if it's a valid number or range
            if not re.match(r'^\d+$|^\d+-\d+$', value.strip()):
                errors.append("Token budget should be a number or range (e.g., '1000' or '500-2000')")
        
        return errors
    
    def _validate_field_values(self, fields: Dict[str, ManifestField], errors: List[str], warnings: List[str]):
        """Cross-validate field values for consistency."""
        # Check if capabilities include identity
        if 'identity' in fields and 'capabilities' in fields:
            if fields['identity'].found and fields['capabilities'].found:
                identity = fields['identity'].value
                capabilities = fields['capabilities'].value
                
                if identity and identity.lower() in capabilities.lower():
                    warnings.append(f"Identity '{identity}' should not be listed in capabilities")
        
        # Check token budget reasonableness
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
                # Already caught in individual field validation
                pass


if __name__ == "__main__":
    # Test the manifest validator
    validator = ManifestValidator()
    
    # Test with complete manifest
    complete_manifest = """
Identity: test-executor
Capabilities: read, write, parse, validate
Token Budget: 1000-5000
Input Schema: json
Output Schema: json
"""
    
    result = validator.validate_manifest_section(complete_manifest)
    print(f"Complete manifest valid: {result.is_valid}")
    print(f"Completeness score: {result.completeness_score}%")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    # Test with incomplete manifest
    incomplete_manifest = """
Identity: test-executor
Token Budget: 1000
"""
    
    result = validator.validate_manifest_section(incomplete_manifest)
    print(f"\nIncomplete manifest valid: {result.is_valid}")
    print(f"Completeness score: {result.completeness_score}%")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")