"""
Logging configuration for structured logging system.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class LoggingArea(Enum):
    """The three logging areas as specified in Phase 0 foundation."""
    HARNESS_INFRASTRUCTURE = "harness_infrastructure"
    PHASE_0_OPERATIONS = "phase_0_operations"
    CONSTITUTIONAL_AUDIT = "constitutional_audit"


@dataclass
class LoggingConfig:
    """Configuration for the structured logging system."""
    
    # Log level filtering
    level: str = "INFO"
    
    # Output format
    format: str = "json"  # Only JSON format supported in Phase 0
    
    # Output destinations
    outputs: List[str] = field(default_factory=lambda: ["stdout"])
    
    # Default component
    default_component: str = "harness_infrastructure"
    
    # Correlation ID management
    correlation_id_enabled: bool = True
    
    # File output configuration
    log_directory: str = "Logs/Architect"
    
    # OpenTelemetry compliance
    use_otel_format: bool = True
    
    # Service identification
    service_name: str = "SovereignAI_Harness"
    service_version: str = "0.1.0"
    
    # Performance options
    ensure_ascii: bool = False  # Allow UTF-8 characters
    json_indent: Optional[int] = None  # Compact JSON by default
    
    # Conversation logging
    conversation_logging_enabled: bool = True
    conversation_storage_path: str = "Logs/Architect/Conversations"
    
    @classmethod
    def default(cls) -> 'LoggingConfig':
        """Create default logging configuration."""
        return cls()
    
    @classmethod
    def development(cls) -> 'LoggingConfig':
        """Create development-friendly configuration with verbose output."""
        return cls(
            level="DEBUG",
            outputs=["stdout", "file"],
            json_indent=2,
            use_otel_format=False
        )
    
    @classmethod
    def production(cls) -> 'LoggingConfig':
        """Create production-optimized configuration."""
        return cls(
            level="INFO",
            outputs=["file"],
            ensure_ascii=False,
            json_indent=None,
            use_otel_format=True
        )
    
    @classmethod
    def for_component(cls, component: LoggingArea) -> 'LoggingConfig':
        """Create configuration for a specific logging area."""
        return cls(
            default_component=component.value,
            log_directory=f"Logs/{component.value}"
        )


# Global configuration instance
_global_config: Optional[LoggingConfig] = None


def get_config() -> LoggingConfig:
    """Get the global logging configuration."""
    global _global_config
    if _global_config is None:
        _global_config = LoggingConfig.default()
    return _global_config


def set_config(config: LoggingConfig) -> None:
    """Set the global logging configuration."""
    global _global_config
    _global_config = config