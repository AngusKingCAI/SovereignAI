# Compliance Criteria Reference for Reviewer Agent

## Purpose
Single source of truth (SSOT) for detailed compliance criteria used in review workflows. This document contains the specific standards and requirements that workflows reference.

## File Type Compliance Criteria

### Code Files (.py, .js, .ts, etc.)

#### Modularity Requirements
- **Single Responsibility Principle**: Each function should do one thing well
- **Clear Interfaces**: Functions should have explicit inputs and outputs
- **Independent Testability**: Functions should be testable in isolation
- **Dependency Injection**: Dependencies should be passed as parameters, not hardcoded
- **Separation of Concerns**: Business logic should be separated from I/O operations

#### Testing Requirements
- **Test Location**: Tests must be in Scripts/Tests/ (never in App/ directory)
- **Test Coverage**: Minimum 90% coverage for all functions
- **Dependency Injection**: Tests should use dependency injection for isolation
- **Mocking**: External dependencies (I/O, databases, APIs) must be mocked
- **Test Paths**: Both success and error paths must be tested
- **Test Quality**: Tests should be deterministic and not implementation-dependent

#### Code Quality Standards
- **Error Handling**: Appropriate error handling and validation
- **Readability**: Code should be clear and maintainable
- **Security Practices**: Follow security best practices (no hardcoded secrets, proper input validation)
- **Documentation**: Meaningful docstrings for classes and functions
- **Code Style**: Follow project coding standards and conventions

#### Best Practices Adherence
- **SOLID Principles**: Single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion
- **Design Patterns**: Use appropriate design patterns for common problems
- **Separation of Concerns**: Clear boundaries between different concerns
- **Industry Standards**: Follow current industry best practices for the language/framework

### Configuration Files (.json, .yaml, .toml, .ini, etc.)

#### Structure Requirements
- **Schema Compliance**: Must follow defined schema if one exists
- **Valid Syntax**: Must be syntactically valid for the file type
- **Proper Structure**: Logical organization and grouping of related settings
- **Documentation**: Include comments explaining configuration purpose

#### Security Requirements
- **No Hardcoded Secrets**: API keys, passwords, tokens must not be in config files
- **Environment Separation**: Different configurations for different environments
- **Access Control**: Proper file permissions if applicable
- **Secrets Management**: Use environment variables or secret management systems

#### Best Practices
- **Validation**: Configuration should be validated at startup
- **Defaults**: Provide sensible defaults for all settings
- **Documentation**: Document all configuration options and their effects
- **Version Control**: Exclude sensitive configs from version control

### Documentation Files (.md, .txt, .rst, etc.)

#### Structure Requirements
- **Clear Organization**: Logical flow and structure
- **Proper Formatting**: Correct use of markup syntax
- **Headings**: Appropriate heading hierarchy
- **Sections**: Clear section divisions for different topics

#### Content Requirements
- **Accuracy**: Information must be accurate and up-to-date
- **Completeness**: Cover all necessary topics
- **Clarity**: Writing should be clear and understandable
- **Relevance**: Content should be relevant to the document's purpose

#### Link and Reference Requirements
- **Link Validity**: All links must be valid and working
- **Cross-References**: Proper cross-referencing within documentation
- **External References**: Cite external sources appropriately
- **Version Specific**: Document should specify version/service it applies to

#### Maintainability
- **Update Process**: Clear process for keeping documentation current
- **Review Schedule**: Regular review and update cycle
- **Ownership**: Clear ownership of different documentation sections
- **Accessibility**: Documentation should be easily findable and accessible

### Data Files (.csv, .json, .xml, etc.)

#### Format Requirements
- **Valid Format**: Must conform to the specified file format
- **Proper Structure**: Appropriate structure for the data type
- **Encoding**: Proper character encoding (typically UTF-8)
- **Consistency**: Consistent formatting throughout the file

#### Data Integrity
- **Data Validation**: Data should be validated against schema
- **Completeness**: All required fields should be present
- **Accuracy**: Data should be accurate and consistent
- **Backup**: Appropriate backup and versioning strategy

#### Usage Patterns
- **Purpose Clarity**: Clear purpose for the data file
- **Access Patterns**: Appropriate read/write patterns
- **Performance**: Consider performance implications for large files
- **Security**: Sensitive data should be appropriately protected

### Build/Deployment Files (Dockerfile, docker-compose.yml, etc.)

#### Security Best Practices
- **Base Images**: Use trusted, minimal base images
- **No Secrets**: No secrets in build files
- **User Permissions**: Run as non-root user when possible
- **Scanning**: Regular security scanning of images

#### Configuration Best Practices
- **Environment Variables**: Use environment variables for configuration
- **Resource Limits**: Set appropriate resource limits
- **Health Checks**: Implement health checks
- **Logging**: Proper logging configuration

#### Maintainability
- **Documentation**: Document build and deployment processes
- **Versioning**: Tag and version Docker images appropriately
- **Reproducibility**: Builds should be reproducible
- **Testing**: Test deployment configurations

## Severity Classifications

### CRITICAL Issues
- **Definition**: Violations that must be fixed immediately
- **Examples**: Missing tests, hardcoded dependencies, mixed concerns, security vulnerabilities
- **Action Required**: Must be fixed before proceeding with other work
- **Timeline**: Immediate

### HIGH Issues
- **Definition**: Major quality issues that should be fixed soon
- **Examples**: Monolithic functions, poor modularity, missing error handling
- **Action Required**: Should be fixed in next iteration
- **Timeline**: 1-2 iterations

### MEDIUM Issues
- **Definition**: Best practices improvements for code quality
- **Examples**: Code readability, maintainability improvements, documentation gaps
- **Action Required**: Should be addressed when time permits
- **Timeline**: 2-3 iterations

### LOW Issues
- **Definition**: Minor suggestions and optimizations
- **Examples**: Comments, formatting, minor style improvements
- **Action Required**: Optional improvements
- **Timeline**: When convenient

## Systematic Pattern Recognition

### Common Anti-Patterns
- **Duplicate Code**: Same logic repeated in multiple places
- **God Objects**: Classes/functions that do too much
- **Magic Numbers**: Unexplained numeric constants
- **Dead Code: Unused code that should be removed
- **TODO Comments**: Unresolved TODOs in production code

### Common Compliance Patterns
- **Empty Configuration Files**: Placeholder files without purpose
- **Placeholder Values**: Hashes, IDs, or other placeholder values
- **Stub Implementations**: Functions that always return fixed values
- **Missing Documentation**: Lack of docstrings or comments
- **Inconsistent Naming**: Different naming conventions in similar contexts

## Best Practices Research Sources

### Research Strategy
1. **Check Local Knowledge First**: Docs/index.md, Docs/Research/index.md, Docs/Code/index.md
2. **Web Search for Current Standards**: Use **{BP}** web search for latest best practices
3. **Industry Standards**: Follow established industry standards for language/framework
4. **Security Guidelines**: Consult current security best practices
5. **Performance Considerations**: Consider performance implications of design decisions

### Search Query Patterns
- **Language-Specific**: "[Language] best practices 2024"
- **Pattern-Specific**: "[Design pattern] best practices [language]"
- **File Type-Specific**: "[File type] configuration best practices"
- **Security-Specific**: "[Language] security best practices 2024"
- **Testing-Specific**: "[Language] testing best practices"