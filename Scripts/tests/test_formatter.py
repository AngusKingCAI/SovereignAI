"""
Unit tests for JSON formatter.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging.formatter import JSONFormatter, OpenTelemetryFormatter
from datetime import datetime, timezone


class TestJSONFormatter(unittest.TestCase):
    """Test cases for JSONFormatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = JSONFormatter()
    
    def test_format_basic_log_entry(self):
        """Test formatting a basic log entry."""
        log_entry = {
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "INFO",
            "service": "test-service",
            "event": "test-event",
            "trace_id": "test-trace-123",
            "component": "test-component",
            "message": "Test message",
            "context": {"key": "value"}
        }
        
        result = self.formatter.format(log_entry)
        
        self.assertIsInstance(result, str)
        self.assertIn("test-service", result)
        self.assertIn("Test message", result)
        self.assertIn("test-trace-123", result)
    
    def test_format_empty_log_entry(self):
        """Test formatting an empty log entry."""
        log_entry = {}
        result = self.formatter.format(log_entry)
        self.assertIsInstance(result, str)
    
    def test_format_batch(self):
        """Test formatting multiple log entries."""
        log_entries = [
            {"level": "INFO", "message": "First message"},
            {"level": "DEBUG", "message": "Second message"}
        ]
        
        result = self.formatter.format_batch(log_entries)
        
        self.assertIsInstance(result, str)
        self.assertIn("First message", result)
        self.assertIn("Second message", result)
    
    def test_format_with_indent(self):
        """Test formatting with indentation."""
        formatter = JSONFormatter(indent=2)
        log_entry = {"level": "INFO", "message": "Test"}
        
        result = formatter.format(log_entry)
        
        self.assertIn("\n", result)  # Should have newlines for indentation
    
    def test_format_with_datetime(self):
        """Test formatting with datetime object."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "level": "INFO",
            "message": "Test"
        }
        
        result = self.formatter.format(log_entry)
        self.assertIsInstance(result, str)


class TestOpenTelemetryFormatter(unittest.TestCase):
    """Test cases for OpenTelemetryFormatter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.formatter = OpenTelemetryFormatter()
    
    def test_ensure_otel_fields(self):
        """Test that OpenTelemetry fields are added."""
        log_entry = {
            "level": "INFO",
            "message": "Test message",
            "service": "test-service"
        }
        
        result = self.formatter.format(log_entry)
        
        self.assertIsInstance(result, str)
        self.assertIn("severityNumber", result)
        self.assertIn("severityText", result)
        self.assertIn("body", result)
        self.assertIn("resource", result)
        self.assertIn("attributes", result)
    
    def test_severity_number_mapping(self):
        """Test log level to severity number mapping."""
        self.assertEqual(self.formatter._map_severity_number("DEBUG"), 1)
        self.assertEqual(self.formatter._map_severity_number("INFO"), 9)
        self.assertEqual(self.formatter._map_severity_number("WARN"), 13)
        self.assertEqual(self.formatter._map_severity_number("ERROR"), 17)
        self.assertEqual(self.formatter._map_severity_number("FATAL"), 21)
    
    def test_case_insensitive_severity_mapping(self):
        """Test case-insensitive severity mapping."""
        self.assertEqual(self.formatter._map_severity_number("debug"), 1)
        self.assertEqual(self.formatter._map_severity_number("InFo"), 9)
    
    def test_invalid_severity_mapping(self):
        """Test default severity for invalid level."""
        result = self.formatter._map_severity_number("INVALID")
        self.assertEqual(result, 9)  # Default to INFO


if __name__ == '__main__':
    unittest.main()