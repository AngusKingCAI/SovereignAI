"""
Log context dataclass for structured logging system.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class LogContext:
    """Additional context information for log entries."""
    component: str
    event: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert log context to dictionary for JSON serialization."""
        result = {
            "component": self.component,
            "event": self.event
        }
        
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.request_id:
            result["request_id"] = self.request_id
        if self.session_id:
            result["session_id"] = self.session_id
        
        result.update(self.additional_context)
        return result

    def merge(self, other: 'LogContext') -> 'LogContext':
        """Merge another log context into this one."""
        merged_context = self.additional_context.copy()
        merged_context.update(other.additional_context)
        
        return LogContext(
            component=other.component or self.component,
            event=other.event or self.event,
            trace_id=other.trace_id or self.trace_id,
            span_id=other.span_id or self.span_id,
            user_id=other.user_id or self.user_id,
            request_id=other.request_id or self.request_id,
            session_id=other.session_id or self.session_id,
            additional_context=merged_context
        )