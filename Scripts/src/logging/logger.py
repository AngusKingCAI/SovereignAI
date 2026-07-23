"""
Main Logger interface for structured logging system.
"""
from typing import Dict, Any, Optional, List
from .log_level import LogLevel
from .log_entry import LogEntry
from .log_context import LogContext
from .correlation import get_correlation_manager
from .formatter import JSONFormatter, OpenTelemetryFormatter
from .output import StdoutOutputHandler, FileOutputHandler

# Default configuration values
DEFAULT_CONFIG = {
    "level": "INFO",
    "format": "json",
    "outputs": ["stdout"],
    "default_component": "harness_infrastructure",
    "correlation_id_enabled": True,
    "log_directory": "Logs/Architect",
    "use_otel_format": True,
    "service_name": "SovereignAI_Harness",
    "service_version": "0.1.0",
    "ensure_ascii": False,
    "json_indent": None,
    "conversation_logging_enabled": True,
    "conversation_storage_path": "Logs/Architect/Conversations"
}

class LoggingArea:
    """The three logging areas as specified in Phase 0 foundation."""
    HARNESS_INFRASTRUCTURE = "harness_infrastructure"
    PHASE_0_OPERATIONS = "phase_0_operations"
    CONSTITUTIONAL_AUDIT = "constitutional_audit"


class Logger:
    """Main logging interface for structured logging."""
    
    def __init__(
        self,
        service: Optional[str] = None,
        component: Optional[str] = None,
        trace_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize logger.
        
        Args:
            service: Service name (defaults to config)
            component: Component/logging area name
            trace_id: Optional correlation ID for distributed tracing
            config: Optional configuration dictionary
        """
        self.config = config or DEFAULT_CONFIG
        self.service = service or self.config.get("service_name", "SovereignAI_Harness")
        self.component = component or self.config.get("default_component", "harness_infrastructure")
        self._trace_id = trace_id
        self._context: Dict[str, Any] = {}
        
        # Initialize correlation manager
        self.correlation_manager = get_correlation_manager()
        if self._trace_id:
            self.correlation_manager.set_trace_id(self._trace_id)
        
        # Initialize formatter
        if self.config.get("use_otel_format", True):
            self.formatter = OpenTelemetryFormatter(
                ensure_ascii=self.config.get("ensure_ascii", False),
                indent=self.config.get("json_indent", None)
            )
        else:
            self.formatter = JSONFormatter(
                ensure_ascii=self.config.get("ensure_ascii", False),
                indent=self.config.get("json_indent", None)
            )
        
        # Initialize output handlers
        self.output_handlers = self._initialize_output_handlers()
    
    def _initialize_output_handlers(self) -> List:
        """Initialize output handlers based on configuration."""
        handlers = []
        
        for output in self.config.get("outputs", ["stdout"]):
            if output == "stdout":
                handlers.append(StdoutOutputHandler())
            elif output == "file":
                handlers.append(FileOutputHandler(
                    log_dir=self.config.get("log_directory", "Logs"),
                    component=self.component
                ))
        
        return handlers
    
    def _get_trace_id(self) -> str:
        """Get current trace ID from correlation manager."""
        if self._trace_id:
            return self._trace_id
        return self.correlation_manager.get_trace_id()
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on level filtering."""
        config_level = LogLevel.from_string(self.config.get("level", "INFO"))
        return level >= config_level
    
    def _log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal logging method.
        
        Args:
            level: Log level
            message: Log message
            context: Additional context information
        """
        if not self._should_log(level):
            return
        
        # Merge current context with provided context
        merged_context = self._context.copy()
        if context:
            merged_context.update(context)
        
        # Create log entry
        log_entry = LogEntry.create(
            level=level.value,
            service=self.service,
            event=self.component,
            trace_id=self._get_trace_id(),
            component=self.component,
            message=message,
            context=merged_context
        )
        
        # Format and output
        formatted_entry = self.formatter.format(log_entry.to_dict())
        for handler in self.output_handlers:
            handler.write(formatted_entry)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, context)
    
    def warn(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._log(LogLevel.WARN, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, context)
    
    def fatal(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log fatal message."""
        self._log(LogLevel.FATAL, message, context)
    
    def with_context(self, context: Dict[str, Any]) -> 'Logger':
        """
        Create a new logger with additional context.
        
        Args:
            context: Additional context to add
            
        Returns:
            New logger instance with merged context
        """
        new_logger = Logger(self.service, self.component, self._trace_id, self.config)
        new_logger._context = self._context.copy()
        new_logger._context.update(context)
        return new_logger
    
    def with_component(self, component: str) -> 'Logger':
        """
        Create a new logger for a different component.
        
        Args:
            component: New component name
            
        Returns:
            New logger instance for the specified component
        """
        return Logger(self.service, component, self._trace_id, self.config)
    
    def with_trace_id(self, trace_id: str) -> 'Logger':
        """
        Create a new logger with a specific trace ID.
        
        Args:
            trace_id: Correlation ID for distributed tracing
            
        Returns:
            New logger instance with the specified trace ID
        """
        return Logger(self.service, self.component, trace_id, self.config)


def get_logger(
    service: Optional[str] = None,
    component: Optional[str] = None,
    trace_id: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> Logger:
    """
    Get a logger instance.
    
    Args:
        service: Service name
        component: Component/logging area name
        trace_id: Optional correlation ID
        config: Optional configuration dictionary
        
    Returns:
        Logger instance
    """
    return Logger(service, component, trace_id, config)


def get_harness_logger(trace_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Logger:
    """Get logger for harness infrastructure area."""
    return get_logger(
        component=LoggingArea.HARNESS_INFRASTRUCTURE.value,
        trace_id=trace_id,
        config=config
    )


def get_phase_logger(trace_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Logger:
    """Get logger for Phase 0 operations area."""
    return get_logger(
        component=LoggingArea.PHASE_0_OPERATIONS.value,
        trace_id=trace_id,
        config=config
    )


def get_audit_logger(trace_id: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Logger:
    """Get logger for constitutional audit area."""
    return get_logger(
        component=LoggingArea.CONSTITUTIONAL_AUDIT.value,
        trace_id=trace_id,
        config=config
    )