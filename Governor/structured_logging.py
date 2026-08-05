"""
Structured Logging for Governor.py v1.5

This module provides structured logging with optional structlog integration
and stdlib fallback. It supports JSON-formatted log output with context fields.

Key Features:
- Optional structlog integration with stdlib fallback
- JSON-formatted log output
- Context fields: trace_id, rule_id, hook_name, duration_ms
- Per-layer logging (engine, state_machine, hook_handlers, actions, audit)
- Performance-aware logging

This implements the structured logging specified in v1.5 spec §4.6.
"""

import sys
import json
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Try to import structlog
USE_STRUCTLOG = False
try:
    import structlog
    USE_STRUCTLOG = True
except ImportError:
    USE_STRUCTLOG = False

# Import trace ID management
try:
    from .trace_id import get_trace_id
except ImportError:
    from trace_id import get_trace_id


# Logger instances per layer
_loggers: Dict[str, Any] = {}


def get_logger(layer: str) -> Any:
    """
    Get a structured logger for a specific layer.
    
    Args:
        layer: Layer name (engine, state_machine, hook_handlers, actions, audit)
        
    Returns:
        Logger instance (structlog or stdlib fallback)
    """
    global _loggers
    
    if layer not in _loggers:
        if USE_STRUCTLOG:
            _loggers[layer] = _create_structlog_logger(layer)
        else:
            _loggers[layer] = _create_stdlib_logger(layer)
    
    return _loggers[layer]


def _create_structlog_logger(layer: str) -> Any:
    """
    Create a structlog logger for a layer.
    
    Args:
        layer: Layer name
        
    Returns:
        Configured structlog logger
    """
    # Configure structlog with JSON processor
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger(layer)


def _create_stdlib_logger(layer: str) -> Any:
    """
    Create a stdlib logger fallback for a layer.
    
    Args:
        layer: Layer name
        
    Returns:
        Configured stdlib logger with JSON formatting
    """
    import logging
    
    logger = logging.getLogger(f"governor.{layer}")
    logger.setLevel(logging.DEBUG)
    
    # Create handler with JSON formatter
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    
    return logger


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for stdlib logging fallback.
    
    Formats log records as JSON with standard fields.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log entry
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "layer": record.name.split('.')[-1],
            "message": record.getMessage(),
            "trace_id": get_trace_id(),
        }
        
        # Add optional fields if present
        if hasattr(record, 'rule_id') and record.rule_id:
            log_entry['rule_id'] = record.rule_id
        if hasattr(record, 'hook_name') and record.hook_name:
            log_entry['hook_name'] = record.hook_name
        if hasattr(record, 'duration_ms') and record.duration_ms:
            log_entry['duration_ms'] = record.duration_ms
        
        # Add extra fields from record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 'msecs',
                          'relativeCreated', 'thread', 'threadName', 'processName', 'process',
                          'message', 'exc_info', 'exc_text', 'stack_info']:
                if not key.startswith('_'):
                    log_entry[key] = value
        
        return json.dumps(log_entry)


def log_structured(layer: str, level: str, message: str, **kwargs) -> None:
    """
    Log a structured message with context fields.
    
    Args:
        layer: Layer name (engine, state_machine, hook_handlers, actions, audit)
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **kwargs: Additional context fields (rule_id, hook_name, duration_ms, etc.)
    """
    logger = get_logger(layer)
    
    # Add trace_id to context
    context = {
        "trace_id": get_trace_id(),
        **kwargs
    }
    
    if USE_STRUCTLOG:
        # Use structlog
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(message, **context)
    else:
        # Use stdlib fallback
        import logging
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create log record with context
        record = logging.LogRecord(
            name=f"governor.{layer}",
            level=log_level,
            pathname="",
            lineno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        
        # Add context fields to record
        for key, value in context.items():
            setattr(record, key, value)
        
        logger.handle(record)


def log_timing(layer: str, operation: str, duration_ms: float, **kwargs) -> None:
    """
    Log timing information with duration.
    
    Args:
        layer: Layer name
        operation: Operation name
        duration_ms: Duration in milliseconds
        **kwargs: Additional context fields
    """
    log_structured(
        layer,
        "debug",
        f"Operation completed: {operation}",
        duration_ms=duration_ms,
        **kwargs
    )


class TimingContext:
    """
    Context manager for timing operations.
    
    Usage:
        with TimingContext("engine", "rule_evaluation"):
            # Operation to time
            pass
    """
    
    def __init__(self, layer: str, operation: str, **kwargs):
        self.layer = layer
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.time() - self.start_time) * 1000
            log_timing(self.layer, self.operation, duration_ms, **self.kwargs)
        return False  # Don't suppress exceptions


def is_structlog_enabled() -> bool:
    """
    Check if structlog is enabled.
    
    Returns:
        True if structlog is available and enabled
    """
    return USE_STRUCTLOG
