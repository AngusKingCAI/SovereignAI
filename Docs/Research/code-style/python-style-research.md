# Python Code Style Best Practices Research

**Source:** PEP 8, Real Python, Google Style Guide  
**Date:** 2026-07-25  
**Purpose:** Python code style guide for Architect agent

## Key Best Practices from Research

### PEP 8 Fundamentals
- **Consistency** is most important - within project, module, and function
- **Naming conventions:**
  - Functions/variables: snake_case (`python_function`)
  - Classes: PascalCase (`PythonClass`)
  - Constants: UPPER_SNAKE_CASE (`CONSTANT_VALUE`)
- **Code layout:** Maximum line length, proper indentation, blank lines
- **Import structure:** Standard library, third-party, local imports

### Modular Design Principles
- **Functions should do one thing only**
- **Break code into logical chunks using functions**
- **Avoid nested control flows** - use functions to encapsulate logic
- **Module organization:** Group related functions together
- **Separation of concerns:** Business logic vs data access vs infrastructure

### Function Design Standards
- **Single responsibility:** Each function has one clear purpose
- **Clear interfaces:** Well-defined inputs and outputs
- **No side effects:** Functions shouldn't modify external state unless required
- **Independence:** Testable in isolation without external dependencies
- **Documentation:** Every function must have docstring

### Safe Addition Patterns
- **Backward compatibility:** New functions must not break existing functionality
- **Default parameters:** Use defaults for new optional arguments
- **Function extension:** Add new functions rather than modify existing ones
- **Graceful degradation:** Handle errors without affecting existing functionality
- **Add-only policy:** New functions are additive, not destructive

### Code Structure Requirements
- **Function length:** Should not exceed 50 lines
- **Parameter count:** Maximum 5 parameters (use dataclasses for complex data)
- **Nesting depth:** Maximum 4 levels
- **Cyclomatic complexity:** Under 10
- **Return values:** Consistent types; use tuples/objects for multiple returns

### File Organization
- **No monolithic files:** Avoid files >300 lines - split into focused modules
- **Clear naming:** Module names must indicate purpose and domain
- **Cohesion:** Group related functions in same module
- **Import order:** Standard library, third-party, local imports
