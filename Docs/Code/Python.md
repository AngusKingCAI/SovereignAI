# Python Code Style Guide

**Purpose:** Python script examples and style standards for Architect agent implementations

## PEP 8 Basics

### Naming Conventions
- **Functions/variables:** snake_case (`python_function`, `my_variable`)
- **Classes:** PascalCase (`PythonClass`, `MyClass`)
- **Constants:** UPPER_SNAKE_CASE (`CONSTANT_VALUE`, `MAX_RETRIES`)

### Code Layout
- **Maximum line length:** 79 characters (standard)
- **Indentation:** 4 spaces per level
- **Import order:** Standard library, third-party, local imports
- **Blank lines:** 2 blank lines between top-level functions, 1 blank line between methods

## Function Modularity Principles

### Single Responsibility
- Each function must have one clear purpose
- Complex logic should be split into smaller functions
- Functions should be testable in isolation

### Clear Interfaces
- Well-defined inputs and outputs
- Every function must have a docstring explaining purpose, parameters, and return values
- Type hints should be used for function signatures

### No Side Effects
- Functions should not modify external state unless explicitly required
- Avoid global variable modifications
- Return new values rather than modifying existing ones

### Independence
- Functions should be testable without dependencies on external state
- Mock external dependencies in tests
- Avoid tight coupling between functions

## Safe Function Addition Patterns

### Backward Compatibility
- New functions must not break existing functionality
- Use default parameters for new optional arguments to maintain compatibility
- Keep old function implementations as wrappers that call new implementations if needed

### Add-Only Policy
- Extend functionality by adding new functions rather than modifying existing ones
- New functions must be additive, not destructive to existing code
- Provide fallback behavior when new features are not available

### Graceful Degradation
- New functions must handle errors gracefully without affecting existing functionality
- Use try-catch blocks appropriately
- Provide meaningful error messages

### Deprecation Process
- When modifying existing functions, use deprecation warnings
- Provide clear migration path for breaking changes
- Tag breaking changes with version numbers

## Code Structure Requirements

### Function Design
- **Function length:** Maximum 50 lines (complex logic should be split)
- **Parameter count:** Maximum 5 parameters (use dataclasses for complex data)
- **Nesting depth:** Maximum 4 levels
- **Cyclomatic complexity:** Functions should have complexity scores under 10
- **Return values:** Functions should return consistent types; use tuples/objects for multiple return values

### File Organization
- **No monolithic files:** Avoid files >300 lines - split into focused modules
- **Clear naming:** Module names must clearly indicate their purpose and domain
- **Cohesion:** Group related functions in the same module
- **Separation of concerns:** Separate business logic from data access, presentation, and infrastructure

## Module Organization Standards

### Import Structure
- Follow PEP 8 import order: standard library, third-party, local imports
- Group imports with blank lines between each group
- Use absolute imports rather than relative imports

### Module Design
- **Cohesion:** Group related functions in the same module
- **Separation of concerns:** Separate business logic from data access, presentation, and infrastructure
- **No monolithic files:** Avoid large files (>300 lines) - split into focused modules
- **Clear naming:** Module names must clearly indicate their purpose and domain

## Example Code

### Good Function Example
```python
def validate_json_file(file_path: str) -> bool:
    """
    Validate JSON file syntax and structure.
    
    Args:
        file_path: Path to the JSON file to validate
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
        print(f"Validation error: {e}")
        return False
```

### Bad Function Example
```python
def doStuff(x):  # Bad: vague name, no docstring, no type hints
    a = []
    for i in x:
        if i > 0:
            a.append(i * 2)
    return a
```

## Testing Requirements
- New functions must have corresponding tests
- Tests should verify both success and error cases
- Use mock objects for external dependencies
- Maintain test coverage above 80% for new code
