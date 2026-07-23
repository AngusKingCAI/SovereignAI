# Phase 0 Logging Foundation - Usage Guide

## Overview

The Phase 0 Logging Foundation provides a structured, deterministic logging system for the SovereignAI Harness. It follows OpenTelemetry standards and provides three distinct logging areas for comprehensive observability.

## Features

- **Structured JSON Logging**: All logs are formatted as JSON for machine processing
- **Correlation IDs**: Automatic trace ID generation for distributed tracing
- **Three Logging Areas**: Harness infrastructure, Phase 0 operations, and constitutional audit
- **Conversation Logging**: Automatic capture of AI conversations for audit trails
- **OpenTelemetry Compliance**: Follows OpenTelemetry log data model
- **Multiple Output Handlers**: Stdout, stderr, and file output support
- **Configurable Log Levels**: DEBUG, INFO, WARN, ERROR, FATAL

## Quick Start

### Basic Usage

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging import get_logger

# Get a logger instance
logger = get_logger(service="my-service", component="test-component")

# Log messages at different levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warn("This is a warning message")
logger.error("This is an error message")
logger.fatal("This is a fatal message")
```

### With Context

```python
# Add context to log entries
context_logger = logger.with_context({"user_id": "user-123", "session": "session-456"})
context_logger.info("User performed an action")
```

### With Custom Configuration

```python
from src.logging import DEFAULT_CONFIG

# Create custom configuration
config = DEFAULT_CONFIG.copy()
config["level"] = "DEBUG"
config["outputs"] = ["stdout", "file"]
config["log_directory"] = "Logs"
config["use_otel_format"] = False

# Use custom configuration
logger = get_logger(service="my-service", config=config)
```

## Logging Areas

### Harness Infrastructure Logger

```python
from src.logging import get_harness_logger

# Logger for harness infrastructure events
harness_logger = get_harness_logger()
harness_logger.info("Kernel initialization started")
harness_logger.error("Kernel initialization failed", {"error_code": 500})
```

### Phase 0 Operations Logger

```python
from src.logging import get_phase_logger

# Logger for Phase 0 operations
phase_logger = get_phase_logger()
phase_logger.info("Repository foundation initiated")
phase_logger.warn("Phase 0 specification review pending")
```

### Constitutional Audit Logger

```python
from src.logging import get_audit_logger

# Logger for constitutional compliance events
audit_logger = get_audit_logger()
audit_logger.info("Gate verification passed", {"phase": 0})
audit_logger.error("Constitutional violation detected", {"violation": "First Rule"})
```

## Conversation Logging

### Starting a Conversation Session

```python
from src.logging import get_conversation_logger

# Get conversation logger
conv_logger = get_conversation_logger()

# Start a new session
session = conv_logger.start_session(
    session_id="session-123",
    trace_id="trace-456",
    context={"user": "test-user", "task": "phase-0-implementation"}
)

# Log messages
conv_logger.log_user_message("Please implement the logging system")
conv_logger.log_assistant_message("I'll implement the logging foundation system")
conv_logger.log_system_message("Implementation started")

# End session
conv_logger.end_session("Logging system implementation completed")
```

## Configuration

### Default Configuration

```python
DEFAULT_CONFIG = {
    "level": "INFO",
    "format": "json",
    "outputs": ["stdout"],
    "default_component": "harness_infrastructure",
    "correlation_id_enabled": True,
    "log_directory": "Logs",
    "use_otel_format": True,
    "service_name": "SovereignAI_Harness",
    "service_version": "0.1.0",
    "ensure_ascii": False,
    "json_indent": None,
    "conversation_logging_enabled": True,
    "conversation_storage_path": "Logs/Conversations"
}
```

### Development Configuration

```python
from src.logging import DEFAULT_CONFIG

dev_config = DEFAULT_CONFIG.copy()
dev_config["level"] = "DEBUG"
dev_config["outputs"] = ["stdout", "file"]
dev_config["json_indent"] = 2
dev_config["use_otel_format"] = False
```

### Production Configuration

```python
from src.logging import DEFAULT_CONFIG

prod_config = DEFAULT_CONFIG.copy()
prod_config["level"] = "INFO"
prod_config["outputs"] = ["file"]
prod_config["use_otel_format"] = True
```

## Log Entry Schema

### Standard JSON Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "level": "INFO",
  "service": "SovereignAI_Harness",
  "event": "harness_infrastructure",
  "trace_id": "trace-123",
  "component": "harness_infrastructure",
  "message": "Message content",
  "context": {
    "key": "value"
  }
}
```

### OpenTelemetry Format

```json
{
  "timestamp": "2024-01-01T00:00:00Z",
  "severityNumber": 9,
  "severityText": "INFO",
  "body": "Message content",
  "resource": {
    "service.name": "SovereignAI_Harness",
    "service.version": "1.0.0"
  },
  "attributes": {
    "trace_id": "trace-123",
    "component": "harness_infrastructure",
    "event": "harness_infrastructure"
  }
}
```

## Testing

### Running Tests

```bash
# Run all tests
python tests/test_log_level.py
python tests/test_correlation.py
python tests/test_formatter.py
python tests/test_integration.py

# Run specific test
python -m unittest tests.test_integration.TestLoggingIntegration.test_logger_complete_workflow
```

## Best Practices

1. **Use Appropriate Log Levels**: DEBUG for development, INFO for normal operations, WARN for potential issues, ERROR for failures, FATAL for critical failures
2. **Include Context**: Add relevant context to log entries for better debugging
3. **Use Correlation IDs**: Leverage automatic trace ID generation for distributed tracing
4. **Choose Correct Logging Area**: Use the appropriate logging area for different types of events
5. **Conversation Logging**: Enable conversation logging for audit trails and debugging
6. **Configuration**: Use appropriate configuration for development vs production environments

## Integration with Gate System

The logging system integrates with the hash-based gate system:

```python
from src.logging import get_audit_logger
from Scripts.Architect.Gates import verify_phase_complete

# Get audit logger with trace ID
audit_logger = get_audit_logger(trace_id="phase-0-verification")

# Log gate verification
audit_logger.info("Phase verification started", {"phase": 0})

# Run gate verification
result = verify_phase_complete(0)

# Log result
if result.success:
    audit_logger.info("Phase verification passed", {"phase": 0})
else:
    audit_logger.error("Phase verification failed", {"phase": 0, "reason": result.error})
```

## Troubleshooting

### Logs Not Appearing

1. Check log level configuration (DEBUG shows all logs, INFO filters DEBUG)
2. Verify output handlers are configured correctly
3. Check file permissions for log directory

### Conversation Logs Not Saving

1. Verify conversation logging is enabled in configuration
2. Check conversation storage path exists and is writable
3. Ensure session is properly ended with `end_session()`

### Correlation IDs Not Consistent

1. Use `with_trace_id()` to set specific trace ID
2. Use `get_correlation_manager()` to manage trace ID lifecycle
3. Ensure trace ID is propagated through context chaining

## Architecture

The logging system follows the SovereignAI constitutional principles:

- **Deterministic**: No external dependencies, reproducible behavior
- **Observable**: All system state changes logged with correlation IDs
- **Minimal Coupling**: Independent logging system, replaceable implementation
- **Testability**: Comprehensive test coverage for all components
- **Architecture First**: Interfaces precede implementation, tests precede integration