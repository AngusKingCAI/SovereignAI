"""
YAML Rule Validator for Governor.py v1.5

This module provides safe YAML parsing and validation for Governor rule files.
It implements dangerous feature disabling, schema validation, and type safety
checks per the v1.5 specification.

Key Features:
- Safe YAML loading with dangerous features disabled
- Rule schema validation per v1.5 spec §3.2
- Type safety checks for all rule fields
- Error reporting with clear messages
"""

import yaml
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass


@dataclass
class RuleValidationError:
    """Represents a validation error in a rule YAML file."""
    file_path: str
    field: str
    message: str
    line: Optional[int] = None


class SafeYAMLLoader(yaml.SafeLoader):
    """
    Custom YAML loader with additional safety restrictions.
    
    Disables dangerous YAML features:
    - No object construction ( !!python/object )
    - No arbitrary code execution
    - No file access
    """
    
    def construct_python_object(self, node):
        """Prevent construction of arbitrary Python objects."""
        raise yaml.constructor.ConstructorError(
            None, None,
            f"Python object construction is not allowed for security reasons",
            node.start_mark
        )


# Register the dangerous object constructor prevention
SafeYAMLLoader.add_constructor(
    'tag:yaml.org,2002:python/object',
    SafeYAMLLoader.construct_python_object
)
SafeYAMLLoader.add_constructor(
    'tag:yaml.org,2002:python/object/new',
    SafeYAMLLoader.construct_python_object
)
SafeYAMLLoader.add_constructor(
    'tag:yaml.org,2002:python/object/apply',
    SafeYAMLLoader.construct_python_object
)


# Rule schema per v1.5 spec §3.2
REQUIRED_FIELDS: Set[str] = {
    "id",
    "version",
    "tier",
    "agent",
    "domain",
    "triggers",
    "check"
}

OPTIONAL_FIELDS: Set[str] = {
    "description",
    "metadata",
    "enabled",
    "aliases",
    "name"
}

VALID_TIERS: Set[str] = {"blocking", "warning", "observational"}
VALID_AGENTS: Set[str] = {"architect", "planner", "executor", "reviewer", "all"}
VALID_DOMAINS: Set[str] = {"execution", "planning", "communication", "file_access", "all"}
VALID_TRIGGERS: Set[str] = {
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "Stop",
    "SessionEnd",
    "PostCompaction"
}


def validate_rule_yaml(file_path: str, yaml_content: str) -> List[RuleValidationError]:
    """
    Validate a Governor rule YAML file.
    
    Args:
        file_path: Path to the YAML file (for error reporting)
        yaml_content: String content of the YAML file
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors: List[RuleValidationError] = []
    
    # Parse YAML safely
    try:
        rule_data = yaml.load(yaml_content, Loader=SafeYAMLLoader)
    except yaml.YAMLError as e:
        errors.append(RuleValidationError(
            file_path=file_path,
            field="parse",
            message=f"YAML parsing error: {e}",
            line=e.problem_mark.line if hasattr(e, 'problem_mark') else None
        ))
        return errors
    
    if not isinstance(rule_data, dict):
        errors.append(RuleValidationError(
            file_path=file_path,
            field="root",
            message="Rule must be a dictionary/object"
        ))
        return errors
    
    # Validate required fields
    for field in REQUIRED_FIELDS:
        if field not in rule_data:
            errors.append(RuleValidationError(
                file_path=file_path,
                field=field,
                message=f"Required field '{field}' is missing"
            ))
    
    # Validate field types
    if "id" in rule_data and not isinstance(rule_data["id"], str):
        errors.append(RuleValidationError(
            file_path=file_path,
            field="id",
            message="Field 'id' must be a string"
        ))
    
    if "version" in rule_data and not isinstance(rule_data["version"], str):
        errors.append(RuleValidationError(
            file_path=file_path,
            field="version",
            message="Field 'version' must be a string (semantic version)"
        ))
    
    if "tier" in rule_data:
        if not isinstance(rule_data["tier"], str):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="tier",
                message="Field 'tier' must be a string"
            ))
        elif rule_data["tier"] not in VALID_TIERS:
            errors.append(RuleValidationError(
                file_path=file_path,
                field="tier",
                message=f"Invalid tier '{rule_data['tier']}'. Valid tiers: {VALID_TIERS}"
            ))
    
    if "agent" in rule_data:
        if not isinstance(rule_data["agent"], str):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="agent",
                message="Field 'agent' must be a string"
            ))
        elif rule_data["agent"] not in VALID_AGENTS:
            errors.append(RuleValidationError(
                file_path=file_path,
                field="agent",
                message=f"Invalid agent '{rule_data['agent']}'. Valid agents: {VALID_AGENTS}"
            ))
    
    if "domain" in rule_data:
        if not isinstance(rule_data["domain"], str):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="domain",
                message="Field 'domain' must be a string"
            ))
        elif rule_data["domain"] not in VALID_DOMAINS:
            errors.append(RuleValidationError(
                file_path=file_path,
                field="domain",
                message=f"Invalid domain '{rule_data['domain']}'. Valid domains: {VALID_DOMAINS}"
            ))
    
    if "triggers" in rule_data:
        if not isinstance(rule_data["triggers"], list):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="triggers",
                message="Field 'triggers' must be a list"
            ))
        else:
            for i, trigger in enumerate(rule_data["triggers"]):
                if not isinstance(trigger, str):
                    errors.append(RuleValidationError(
                        file_path=file_path,
                        field=f"triggers[{i}]",
                        message=f"Trigger at index {i} must be a string"
                    ))
                elif trigger not in VALID_TRIGGERS:
                    errors.append(RuleValidationError(
                        file_path=file_path,
                        field=f"triggers[{i}]",
                        message=f"Invalid trigger '{trigger}' at index {i}. Valid triggers: {VALID_TRIGGERS}"
                    ))
    
    if "check" in rule_data:
        if not isinstance(rule_data["check"], dict):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="check",
                message="Field 'check' must be a dictionary"
            ))
        else:
            # Validate check structure per spec §3.2
            if "params" in rule_data["check"]:
                if not isinstance(rule_data["check"]["params"], dict):
                    errors.append(RuleValidationError(
                        file_path=file_path,
                        field="check.params",
                        message="Field 'check.params' must be a dictionary"
                    ))
                else:
                    # Validate actions if present
                    if "actions" in rule_data["check"]["params"]:
                        if not isinstance(rule_data["check"]["params"]["actions"], list):
                            errors.append(RuleValidationError(
                                file_path=file_path,
                                field="check.params.actions",
                                message="Field 'check.params.actions' must be a list"
                            ))
                        else:
                            for i, action in enumerate(rule_data["check"]["params"]["actions"]):
                                if not isinstance(action, dict):
                                    errors.append(RuleValidationError(
                                        file_path=file_path,
                                        field=f"check.params.actions[{i}]",
                                        message=f"Action at index {i} must be a dictionary"
                                    ))
                                elif "name" not in action:
                                    errors.append(RuleValidationError(
                                        file_path=file_path,
                                        field=f"check.params.actions[{i}]",
                                        message=f"Action at index {i} must have a 'name' field"
                                    ))
    
    # Validate optional fields if present
    if "enabled" in rule_data and not isinstance(rule_data["enabled"], bool):
        errors.append(RuleValidationError(
            file_path=file_path,
            field="enabled",
            message="Field 'enabled' must be a boolean"
        ))
    
    if "aliases" in rule_data:
        if not isinstance(rule_data["aliases"], list):
            errors.append(RuleValidationError(
                file_path=file_path,
                field="aliases",
                message="Field 'aliases' must be a list"
            ))
        else:
            for i, alias in enumerate(rule_data["aliases"]):
                if not isinstance(alias, str):
                    errors.append(RuleValidationError(
                        file_path=file_path,
                        field=f"aliases[{i}]",
                        message=f"Alias at index {i} must be a string"
                    ))
    
    # Check for unknown fields
    known_fields = REQUIRED_FIELDS | OPTIONAL_FIELDS
    for field in rule_data.keys():
        if field not in known_fields:
            errors.append(RuleValidationError(
                file_path=file_path,
                field=field,
                message=f"Unknown field '{field}'. Valid fields: {sorted(known_fields)}"
            ))
    
    return errors


def load_rule_yaml(file_path: str) -> Dict[str, Any]:
    """
    Load and validate a rule YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Parsed rule dictionary
        
    Raises:
        ValueError: If validation fails
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        yaml_content = f.read()
    
    errors = validate_rule_yaml(file_path, yaml_content)
    if errors:
        error_messages = [f"{e.field}: {e.message}" for e in errors]
        raise ValueError(f"Rule validation failed for {file_path}:\n" + "\n".join(error_messages))
    
    return yaml.load(yaml_content, Loader=SafeYAMLLoader)
