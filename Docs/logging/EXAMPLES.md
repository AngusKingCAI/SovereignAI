# Phase 0 Logging Foundation - Usage Examples

## Example 1: Basic Logging

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging import get_logger, DEFAULT_CONFIG

# Basic logger with default configuration
logger = get_logger(service="example-service", component="demo")

# Log messages at different levels
logger.debug("Starting initialization process")
logger.info("Service started successfully")
logger.warn("Memory usage above threshold", {"usage_percent": 85})
logger.error("Database connection failed", {"error_code": "DB001"})
logger.fatal("System crash imminent", {"memory": "critical"})
```

## Example 2: Contextual Logging

```python
# Create logger with user context
logger = get_logger(service="user-service", component="authentication")

# Add context and log
auth_logger = logger.with_context({
    "user_id": "user-123",
    "session_id": "session-456",
    "ip_address": "192.168.1.1"
})

auth_logger.info("User login attempt")
auth_logger.warn("Multiple failed login attempts", {"attempts": 5})
auth_logger.error("Account locked", {"reason": "too_many_attempts"})
```

## Example 3: Phase-Specific Logging

```python
from src.logging import get_harness_logger, get_phase_logger, get_audit_logger

# Harness infrastructure logging
harness_logger = get_harness_logger()
harness_logger.info("Kernel initialization")
harness_logger.debug("Memory allocation", {"size": "1024MB"})
harness_logger.error("Kernel panic", {"error": "0xDEADBEEF"})

# Phase 0 operations logging
phase_logger = get_phase_logger()
phase_logger.info("Repository foundation started")
phase_logger.debug("Creating directory structure")
phase_logger.warn("Specification review pending")

# Constitutional audit logging
audit_logger = get_audit_logger()
audit_logger.info("Gate verification passed", {"phase": 0})
audit_logger.error("Constitutional violation", {"rule": "First Rule"})
```

## Example 4: Conversation Logging

```python
from src.logging import get_conversation_logger

# Get conversation logger
conv_logger = get_conversation_logger()

# Start development session
session = conv_logger.start_session(
    session_id="dev-session-001",
    trace_id="trace-001",
    context={
        "developer": "AI-Architect",
        "task": "Implement Phase 0 logging",
        "phase": 0
    }
)

# Log development conversation
conv_logger.log_user_message("Implement the logging foundation system")
conv_logger.log_assistant_message("I'll implement a structured JSON logging system")
conv_logger.log_system_message("Implementation started")
conv_logger.log_user_message("Add conversation logging for audit trails")
conv_logger.log_assistant_message("Adding conversation logger with JSON storage")
conv_logger.log_system_message("Conversation logger implementation completed")

# End session with summary
conv_logger.end_session("Phase 0 logging foundation implementation completed successfully")
```

## Example 5: Custom Configuration

```python
from src.logging import get_logger, DEFAULT_CONFIG

# Development configuration
dev_config = DEFAULT_CONFIG.copy()
dev_config["level"] = "DEBUG"
dev_config["outputs"] = ["stdout", "file"]
dev_config["json_indent"] = 2
dev_config["use_otel_format"] = False

dev_logger = get_logger(service="dev-service", config=dev_config)
dev_logger.debug("Development mode enabled")

# Production configuration
prod_config = DEFAULT_CONFIG.copy()
prod_config["level"] = "INFO"
prod_config["outputs"] = ["file"]
prod_config["use_otel_format"] = True

prod_logger = get_logger(service="prod-service", config=prod_config)
prod_logger.info("Production service started")
```

## Example 6: Component Switching

```python
from src.logging import get_logger, LoggingArea

# Create base logger
base_logger = get_logger(service="harness-service")

# Switch to different components
harness_logger = base_logger.with_component(LoggingArea.HARNESS_INFRASTRUCTURE)
harness_logger.info("Kernel initialization")

phase_logger = base_logger.with_component(LoggingArea.PHASE_0_OPERATIONS)
phase_logger.info("Phase 0 operations started")

audit_logger = base_logger.with_component(LoggingArea.CONSTITUTIONAL_AUDIT)
audit_logger.info("Constitutional compliance check")
```

## Example 7: Correlation ID Management

```python
from src.logging import get_logger, get_correlation_manager

# Get correlation manager
correlation_manager = get_correlation_manager()

# Start new trace
trace_id = correlation_manager.new_trace()
logger = get_logger(service="distributed-service", trace_id=trace_id)

# All logs share the same trace ID
logger.info("First operation")
logger.info("Second operation")
logger.info("Third operation")

# Start new span for specific operation
span_id = correlation_manager.new_span()
logger.info("Operation in new span")

# Manual trace ID setting
logger_with_trace = logger.with_trace_id("manual-trace-123")
logger_with_trace.info("Operation with manual trace ID")
```

## Example 8: Integration with Gate System

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging import get_audit_logger

# Get audit logger for gate operations
audit_logger = get_audit_logger(trace_id="gate-verification-001")

# Log gate verification start
audit_logger.info("Phase gate verification started", {
    "phase": 0,
    "operation": "verify_phase_complete"
})

# Simulate gate verification
try:
    # This would call the actual gate system
    result = {"success": True, "phase": 0}
    
    if result["success"]:
        audit_logger.info("Phase gate verification passed", {
            "phase": result["phase"],
            "verification_time": "2024-01-01T00:00:00Z"
        })
    else:
        audit_logger.error("Phase gate verification failed", {
            "phase": result["phase"],
            "reason": "previous_phase_incomplete"
        })
except Exception as e:
    audit_logger.fatal("Gate verification system error", {
        "error": str(e),
        "error_type": type(e).__name__
    })
```

## Example 9: Error Handling and Context

```python
from src.logging import get_logger

logger = get_logger(service="error-service", component="error-handling")

# Log error with full context
try:
    # Simulate an error
    result = 1 / 0
except ZeroDivisionError as e:
    logger.error("Division by zero error", {
        "error_type": "ZeroDivisionError",
        "error_message": str(e),
        "operation": "calculation",
        "input_values": {"numerator": 1, "denominator": 0},
        "stack_trace": "simulated_trace"
    })

# Log with additional context
error_context = {
    "user_id": "user-123",
    "request_id": "req-456",
    "operation": "data_processing",
    "retry_count": 3
}

logger.error("Operation failed after retries", error_context)
```

## Example 10: Batch Operations

```python
from src.logging import get_logger

logger = get_logger(service="batch-service", component="batch-operations")

# Log batch operation start
logger.info("Batch operation started", {
    "batch_id": "batch-001",
    "total_items": 1000,
    "operation_type": "data_migration"
})

# Simulate batch processing
for i in range(10):
    logger.debug(f"Processing item {i}", {
        "batch_id": "batch-001",
        "item_number": i,
        "status": "processing"
    })

# Log batch operation completion
logger.info("Batch operation completed", {
    "batch_id": "batch-001",
    "items_processed": 10,
    "success_count": 10,
    "failure_count": 0,
    "duration_seconds": 5.2
})
```

## Example 11: Multi-Service Logging

```python
from src.logging import get_logger

# Create loggers for different services
auth_logger = get_logger(service="auth-service", component="authentication")
db_logger = get_logger(service="database-service", component="data_access")
api_logger = get_logger(service="api-service", component="api_endpoint")

# Log across services
auth_logger.info("User authentication", {"user_id": "user-123"})
db_logger.info("Database query", {"query": "SELECT * FROM users"})
api_logger.info("API request received", {"endpoint": "/api/users", "method": "GET"})
```

## Example 12: Testing Integration

```python
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging import get_logger, DEFAULT_CONFIG

# Create temporary directory for test logs
temp_dir = tempfile.mkdtemp()

# Configure test logger
test_config = DEFAULT_CONFIG.copy()
test_config["outputs"] = ["file"]
test_config["log_directory"] = temp_dir
test_config["level"] = "DEBUG"
test_config["use_otel_format"] = False

# Create test logger
test_logger = get_logger(service="test-service", config=test_config)

# Run test operations
test_logger.info("Test started")
test_logger.debug("Processing test data")
test_logger.info("Test completed successfully")

# Verify log file exists
import os
log_files = os.listdir(os.path.join(temp_dir, "harness_infrastructure"))
print(f"Log files created: {log_files}")

# Clean up
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)
```

These examples demonstrate the comprehensive capabilities of the Phase 0 Logging Foundation system for the SovereignAI Harness infrastructure.