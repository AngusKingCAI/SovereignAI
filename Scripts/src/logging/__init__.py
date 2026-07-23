"""
Structured logging system for SovereignAI Harness.
Phase 0 Logging Foundation implementation.
"""
from .logger import (
    Logger, 
    get_logger, 
    get_harness_logger, 
    get_phase_logger, 
    get_audit_logger,
    LoggingArea,
    DEFAULT_CONFIG
)
from .log_level import LogLevel
from .log_entry import LogEntry
from .log_context import LogContext
from .correlation import CorrelationManager, get_correlation_manager
from .formatter import JSONFormatter, OpenTelemetryFormatter
from .conversation_logger import ConversationLogger, ConversationSession, get_conversation_logger

__all__ = [
    'Logger',
    'get_logger',
    'get_harness_logger',
    'get_phase_logger',
    'get_audit_logger',
    'LoggingArea',
    'DEFAULT_CONFIG',
    'LogLevel',
    'LogEntry',
    'LogContext',
    'CorrelationManager',
    'get_correlation_manager',
    'JSONFormatter',
    'OpenTelemetryFormatter',
    'ConversationLogger',
    'ConversationSession',
    'get_conversation_logger'
]