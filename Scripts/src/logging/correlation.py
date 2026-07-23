"""
Correlation ID generation and management for distributed tracing.
"""
import uuid
from typing import Optional


class CorrelationManager:
    """Manages correlation IDs for distributed tracing and conversation logging."""
    
    def __init__(self):
        self._current_trace_id: Optional[str] = None
        self._current_span_id: Optional[str] = None
    
    def generate_trace_id(self) -> str:
        """Generate a new trace ID for a conversation or workflow."""
        return str(uuid.uuid4())
    
    def generate_span_id(self) -> str:
        """Generate a new span ID for an operation within a trace."""
        return str(uuid.uuid4())
    
    def set_trace_id(self, trace_id: str) -> None:
        """Set the current trace ID manually."""
        self._current_trace_id = trace_id
    
    def set_span_id(self, span_id: str) -> None:
        """Set the current span ID manually."""
        self._current_span_id = span_id
    
    def get_trace_id(self) -> str:
        """Get the current trace ID, generating one if needed."""
        if self._current_trace_id is None:
            self._current_trace_id = self.generate_trace_id()
        return self._current_trace_id
    
    def get_span_id(self) -> str:
        """Get the current span ID, generating one if needed."""
        if self._current_span_id is None:
            self._current_span_id = self.generate_span_id()
        return self._current_span_id
    
    def new_span(self) -> str:
        """Start a new span within the current trace."""
        self._current_span_id = self.generate_span_id()
        return self._current_span_id
    
    def new_trace(self) -> str:
        """Start a new trace (new conversation/workflow)."""
        self._current_trace_id = self.generate_trace_id()
        self._current_span_id = self.generate_span_id()
        return self._current_trace_id
    
    def reset(self) -> None:
        """Reset all correlation IDs."""
        self._current_trace_id = None
        self._current_span_id = None


# Global correlation manager instance
_global_correlation_manager = CorrelationManager()


def get_correlation_manager() -> CorrelationManager:
    """Get the global correlation manager instance."""
    return _global_correlation_manager