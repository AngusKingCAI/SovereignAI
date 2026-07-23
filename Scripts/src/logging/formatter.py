"""
JSON formatter for structured logging following OpenTelemetry standards.
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class JSONFormatter:
    """Formats log entries as JSON following OpenTelemetry standards."""
    
    def __init__(self, ensure_ascii: bool = False, indent: Optional[int] = None):
        """
        Initialize JSON formatter.
        
        Args:
            ensure_ascii: Whether to escape non-ASCII characters
            indent: JSON indentation (None for compact output)
        """
        self.ensure_ascii = ensure_ascii
        self.indent = indent
    
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format a log entry as JSON string.
        
        Args:
            log_entry: Dictionary containing log entry data
            
        Returns:
            JSON string representation of the log entry
        """
        return json.dumps(
            log_entry,
            ensure_ascii=self.ensure_ascii,
            indent=self.indent,
            default=self._json_serializer
        )
    
    def _json_serializer(self, obj: Any) -> str:
        """
        Custom JSON serializer for non-serializable objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            String representation of the object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return str(obj.__dict__)
        else:
            return str(obj)
    
    def format_batch(self, log_entries: List[Dict[str, Any]]) -> str:
        """
        Format multiple log entries as a JSON array.
        
        Args:
            log_entries: List of log entry dictionaries
            
        Returns:
            JSON array string of log entries
        """
        return json.dumps(
            log_entries,
            ensure_ascii=self.ensure_ascii,
            indent=self.indent,
            default=self._json_serializer
        )


class OpenTelemetryFormatter(JSONFormatter):
    """
    JSON formatter specifically for OpenTelemetry log format.
    Follows OpenTelemetry Log Data Model specification.
    """
    
    def format(self, log_entry: Dict[str, Any]) -> str:
        """
        Format log entry following OpenTelemetry log data model.
        
        Args:
            log_entry: Dictionary containing log entry data
            
        Returns:
            OpenTelemetry-compliant JSON string
        """
        # Ensure required OpenTelemetry fields are present
        otel_entry = self._ensure_otel_fields(log_entry)
        
        return super().format(otel_entry)
    
    def _ensure_otel_fields(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure log entry has required OpenTelemetry fields.
        
        Args:
            log_entry: Original log entry
            
        Returns:
            Log entry with OpenTelemetry fields
        """
        # OpenTelemetry required fields
        required_fields = {
            "timestamp": log_entry.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "severityNumber": self._map_severity_number(log_entry.get("level", "INFO")),
            "severityText": log_entry.get("level", "INFO"),
            "body": log_entry.get("message", ""),
            "resource": {
                "service.name": log_entry.get("service", "unknown"),
                "service.version": "1.0.0"
            },
            "attributes": {
                "trace_id": log_entry.get("trace_id", ""),
                "component": log_entry.get("component", "unknown"),
                "event": log_entry.get("event", "unknown")
            }
        }
        
        # Add any additional context to attributes
        if "context" in log_entry:
            required_fields["attributes"].update(log_entry["context"])
        
        return required_fields
    
    def _map_severity_number(self, level: str) -> int:
        """
        Map log level string to OpenTelemetry severity number.
        
        Args:
            level: Log level string
            
        Returns:
            OpenTelemetry severity number
        """
        severity_map = {
            "DEBUG": 1,   # TRACE
            "INFO": 9,    # INFO
            "WARN": 13,   # WARN
            "ERROR": 17,  # ERROR
            "FATAL": 21   # FATAL
        }
        return severity_map.get(level.upper(), 9)