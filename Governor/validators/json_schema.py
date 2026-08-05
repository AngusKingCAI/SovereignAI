"""
JSON Schema Validator for Governor.py v1.5

This module provides JSON schema validation for Governor rule structures.
It implements a lightweight schema validator for rule validation per v1.5 spec §3.2.

Key Features:
- Rule schema definition per v1.5 spec §3.2
- Type checking for all rule fields
- Clear error reporting
- Lightweight implementation (no external dependencies)
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass


@dataclass
class SchemaValidationError:
    """Represents a schema validation error."""
    field: str
    message: str
    expected: str
    actual: str


# Rule schema per v1.5 spec §3.2
RULE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": ["id", "version", "tier", "agent", "domain", "triggers", "check"],
    "properties": {
        "id": {"type": "string"},
        "version": {"type": "string"},
        "tier": {"type": "string", "enum": ["blocking", "warning", "observational"]},
        "agent": {"type": "string", "enum": ["architect", "planner", "executor", "reviewer", "all"]},
        "domain": {"type": "string", "enum": ["execution", "planning", "communication", "file_access", "all"]},
        "triggers": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse", 
                        "PermissionRequest", "Stop", "SessionEnd", "PostCompaction"]
            }
        },
        "check": {
            "type": "object",
            "properties": {
                "params": {
                    "type": "object",
                    "properties": {
                        "actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "description": {"type": "string"},
        "metadata": {"type": "object"},
        "enabled": {"type": "boolean"},
        "scope": {"type": "string", "enum": ["app", "harness", "all"]},
        "aliases": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}


def validate_type(value: Any, expected_type: str) -> bool:
    """
    Check if a value matches the expected type.
    
    Args:
        value: Value to check
        expected_type: Expected type string ("string", "number", "boolean", "array", "object")
        
    Returns:
        True if type matches
    """
    type_map = {
        "string": str,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict
    }
    
    python_type = type_map.get(expected_type)
    if python_type is None:
        return False
    
    return isinstance(value, python_type)


def validate_enum(value: Any, enum_values: List[Any]) -> bool:
    """
    Check if a value is in the allowed enum values.
    
    Args:
        value: Value to check
        enum_values: List of allowed values
        
    Returns:
        True if value is in enum
    """
    return value in enum_values


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any], 
                   field_path: str = "") -> List[SchemaValidationError]:
    """
    Validate data against a JSON schema.
    
    Args:
        data: Data to validate
        schema: Schema definition
        field_path: Current field path (for error reporting)
        
    Returns:
        List of validation errors
    """
    errors: List[SchemaValidationError] = []
    
    # Check type
    if "type" in schema:
        if not validate_type(data, schema["type"]):
            errors.append(SchemaValidationError(
                field=field_path or "root",
                message=f"Expected type '{schema['type']}'",
                expected=schema["type"],
                actual=type(data).__name__
            ))
            return errors  # Type mismatch, don't continue
    
    # Check required fields
    if schema.get("type") == "object" and "required" in schema:
        for required_field in schema["required"]:
            if required_field not in data:
                errors.append(SchemaValidationError(
                    field=field_path or "root",
                    message=f"Required field '{required_field}' is missing",
                    expected="field present",
                    actual="field missing"
                ))
    
    # Check properties
    if schema.get("type") == "object" and "properties" in schema:
        for prop_name, prop_schema in schema["properties"].items():
            if prop_name in data:
                prop_path = f"{field_path}.{prop_name}" if field_path else prop_name
                errors.extend(validate_schema(data[prop_name], prop_schema, prop_path))
    
    # Check array items
    if schema.get("type") == "array" and "items" in schema:
        if isinstance(data, list):
            for i, item in enumerate(data):
                item_path = f"{field_path}[{i}]" if field_path else f"[{i}]"
                errors.extend(validate_schema(item, schema["items"], item_path))
    
    # Check enum
    if "enum" in schema:
        if not validate_enum(data, schema["enum"]):
            errors.append(SchemaValidationError(
                field=field_path or "root",
                message=f"Value must be one of {schema['enum']}",
                expected=f"one of {schema['enum']}",
                actual=str(data)
            ))
    
    return errors


def validate_rule_schema(rule_data: Dict[str, Any]) -> List[SchemaValidationError]:
    """
    Validate a rule dictionary against the rule schema.
    
    Args:
        rule_data: Rule dictionary to validate
        
    Returns:
        List of validation errors (empty if valid)
    """
    return validate_schema(rule_data, RULE_SCHEMA)


def validate_and_normalize_rule(rule_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize a rule dictionary.
    
    This function:
    1. Validates the rule against the schema
    2. Sets default values for optional fields
    3. Returns a normalized rule dictionary
    
    Args:
        rule_data: Rule dictionary to validate
        
    Returns:
        Normalized rule dictionary
        
    Raises:
        ValueError: If validation fails
    """
    errors = validate_rule_schema(rule_data)
    if errors:
        error_messages = [f"{e.field}: {e.message} (expected {e.expected}, got {e.actual})" 
                          for e in errors]
        raise ValueError(f"Rule schema validation failed:\n" + "\n".join(error_messages))
    
    # Normalize: set defaults for optional fields
    normalized = rule_data.copy()
    
    if "enabled" not in normalized:
        normalized["enabled"] = True
    
    if "description" not in normalized:
        normalized["description"] = ""
    
    if "aliases" not in normalized:
        normalized["aliases"] = []
    
    if "metadata" not in normalized:
        normalized["metadata"] = {}
    
    return normalized
