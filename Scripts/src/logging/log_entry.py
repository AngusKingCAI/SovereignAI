"""
Log entry dataclass for structured logging system.
"""
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime, timezone


@dataclass
class LogEntry:
    """Structured log entry with standard schema."""
    timestamp: str  # ISO 8601 UTC
    level: str     # LogLevel value
    service: str   # Service name
    event: str     # Event name
    trace_id: str  # Correlation ID
    component: str # Logging area
    message: str   # Human-readable message
    context: Dict[str, Any]  # Additional context

    @classmethod
    def create(
        cls,
        level: str,
        service: str,
        event: str,
        trace_id: str,
        component: str,
        message: str,
        context: Dict[str, Any]
    ) -> 'LogEntry':
        """Create a new log entry with current timestamp."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return cls(
            timestamp=timestamp,
            level=level,
            service=service,
            event=event,
            trace_id=trace_id,
            component=component,
            message=message,
            context=context
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "service": self.service,
            "event": self.event,
            "trace_id": self.trace_id,
            "component": self.component,
            "message": self.message,
            "context": self.context
        }

    def to_json(self) -> str:
        """Convert log entry to JSON string."""
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)