"""
Unit tests for LogLevel enumeration.
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging.log_level import LogLevel


class TestLogLevel(unittest.TestCase):
    """Test cases for LogLevel enum."""
    
    def test_log_level_values(self):
        """Test that log levels have correct string values."""
        self.assertEqual(LogLevel.DEBUG.value, "DEBUG")
        self.assertEqual(LogLevel.INFO.value, "INFO")
        self.assertEqual(LogLevel.WARN.value, "WARN")
        self.assertEqual(LogLevel.ERROR.value, "ERROR")
        self.assertEqual(LogLevel.FATAL.value, "FATAL")
    
    def test_log_level_comparison(self):
        """Test log level comparison operators."""
        self.assertTrue(LogLevel.DEBUG < LogLevel.INFO)
        self.assertTrue(LogLevel.INFO < LogLevel.WARN)
        self.assertTrue(LogLevel.WARN < LogLevel.ERROR)
        self.assertTrue(LogLevel.ERROR < LogLevel.FATAL)
        
        self.assertTrue(LogLevel.DEBUG <= LogLevel.INFO)
        self.assertTrue(LogLevel.INFO <= LogLevel.WARN)
        
        self.assertTrue(LogLevel.WARN > LogLevel.INFO)
        self.assertTrue(LogLevel.ERROR > LogLevel.WARN)
        
        self.assertTrue(LogLevel.FATAL >= LogLevel.ERROR)
        self.assertTrue(LogLevel.ERROR >= LogLevel.WARN)
    
    def test_from_string(self):
        """Test parsing log levels from strings."""
        self.assertEqual(LogLevel.from_string("DEBUG"), LogLevel.DEBUG)
        self.assertEqual(LogLevel.from_string("INFO"), LogLevel.INFO)
        self.assertEqual(LogLevel.from_string("WARN"), LogLevel.WARN)
        self.assertEqual(LogLevel.from_string("ERROR"), LogLevel.ERROR)
        self.assertEqual(LogLevel.from_string("FATAL"), LogLevel.FATAL)
        
        # Test case insensitivity
        self.assertEqual(LogLevel.from_string("debug"), LogLevel.DEBUG)
        self.assertEqual(LogLevel.from_string("InFo"), LogLevel.INFO)
    
    def test_from_string_invalid(self):
        """Test that invalid log level strings raise ValueError."""
        with self.assertRaises(ValueError):
            LogLevel.from_string("INVALID")
        with self.assertRaises(ValueError):
            LogLevel.from_string("TRACE")


if __name__ == '__main__':
    unittest.main()