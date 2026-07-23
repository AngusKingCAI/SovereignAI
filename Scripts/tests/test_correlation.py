"""
Unit tests for correlation ID management.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging.correlation import CorrelationManager, get_correlation_manager


class TestCorrelationManager(unittest.TestCase):
    """Test cases for CorrelationManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CorrelationManager()
    
    def test_generate_trace_id(self):
        """Test trace ID generation."""
        trace_id = self.manager.generate_trace_id()
        self.assertIsInstance(trace_id, str)
        self.assertTrue(len(trace_id) > 0)
        
        # Generate another ID and ensure they're different
        another_id = self.manager.generate_trace_id()
        self.assertNotEqual(trace_id, another_id)
    
    def test_generate_span_id(self):
        """Test span ID generation."""
        span_id = self.manager.generate_span_id()
        self.assertIsInstance(span_id, str)
        self.assertTrue(len(span_id) > 0)
        
        # Generate another ID and ensure they're different
        another_id = self.manager.generate_span_id()
        self.assertNotEqual(span_id, another_id)
    
    def test_set_get_trace_id(self):
        """Test setting and getting trace ID."""
        custom_id = "custom-trace-id-123"
        self.manager.set_trace_id(custom_id)
        self.assertEqual(self.manager.get_trace_id(), custom_id)
    
    def test_set_get_span_id(self):
        """Test setting and getting span ID."""
        custom_id = "custom-span-id-456"
        self.manager.set_span_id(custom_id)
        self.assertEqual(self.manager.get_span_id(), custom_id)
    
    def test_get_trace_id_auto_generate(self):
        """Test automatic trace ID generation."""
        trace_id = self.manager.get_trace_id()
        self.assertIsInstance(trace_id, str)
        self.assertTrue(len(trace_id) > 0)
        
        # Call again should return same ID
        same_id = self.manager.get_trace_id()
        self.assertEqual(trace_id, same_id)
    
    def test_get_span_id_auto_generate(self):
        """Test automatic span ID generation."""
        span_id = self.manager.get_span_id()
        self.assertIsInstance(span_id, str)
        self.assertTrue(len(span_id) > 0)
        
        # Call again should return same ID
        same_id = self.manager.get_span_id()
        self.assertEqual(span_id, same_id)
    
    def test_new_span(self):
        """Test creating a new span within current trace."""
        first_span = self.manager.get_span_id()
        new_span = self.manager.new_span()
        
        self.assertNotEqual(first_span, new_span)
        self.assertEqual(self.manager.get_span_id(), new_span)
    
    def test_new_trace(self):
        """Test creating a new trace."""
        first_trace = self.manager.get_trace_id()
        new_trace = self.manager.new_trace()
        
        self.assertNotEqual(first_trace, new_trace)
        self.assertEqual(self.manager.get_trace_id(), new_trace)
        
        # Span should also be new
        new_span = self.manager.get_span_id()
        self.assertIsInstance(new_span, str)
    
    def test_reset(self):
        """Test resetting correlation IDs."""
        self.manager.set_trace_id("test-trace")
        self.manager.set_span_id("test-span")
        
        self.manager.reset()
        
        # After reset, should generate new IDs
        new_trace = self.manager.get_trace_id()
        new_span = self.manager.get_span_id()
        
        self.assertNotEqual(new_trace, "test-trace")
        self.assertNotEqual(new_span, "test-span")
    
    def test_global_correlation_manager(self):
        """Test global correlation manager instance."""
        global_manager = get_correlation_manager()
        self.assertIsInstance(global_manager, CorrelationManager)
        
        # Should return same instance
        same_manager = get_correlation_manager()
        self.assertIs(global_manager, same_manager)


if __name__ == '__main__':
    unittest.main()