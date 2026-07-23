"""
Integration tests for the complete logging system.
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.logging.logger import Logger, LoggingArea, DEFAULT_CONFIG
from src.logging.conversation_logger import ConversationLogger


class TestLoggingIntegration(unittest.TestCase):
    """Integration tests for the complete logging system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = DEFAULT_CONFIG.copy()
        self.config["outputs"] = ["file"]
        self.config["log_directory"] = self.temp_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_complete_workflow(self):
        """Test complete logging workflow from creation to output."""
        # Use non-OTEL format for simpler testing and DEBUG level to see all messages
        test_config = self.config.copy()
        test_config["use_otel_format"] = False
        test_config["level"] = "DEBUG"
        
        logger = Logger(
            service="test-service",
            component="test-component",
            config=test_config
        )
        
        # Log messages at different levels
        logger.debug("Debug message", {"debug_key": "debug_value"})
        logger.info("Info message", {"info_key": "info_value"})
        logger.warn("Warning message", {"warn_key": "warn_value"})
        logger.error("Error message", {"error_key": "error_value"})
        
        # Check that log file was created
        log_files = os.listdir(os.path.join(self.temp_dir, "test-component"))
        self.assertTrue(len(log_files) > 0)
        
        # Read and verify log file content
        log_file = os.path.join(self.temp_dir, "test-component", log_files[0])
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        self.assertTrue(len(lines) >= 4)  # At least 4 log entries
        
        # Verify log entry structure
        for line in lines:
            log_entry = json.loads(line)
            self.assertIn("timestamp", log_entry)
            self.assertIn("level", log_entry)
            self.assertIn("service", log_entry)
            self.assertIn("message", log_entry)
            self.assertIn("trace_id", log_entry)
    
    def test_logger_with_context(self):
        """Test logger with context chaining."""
        # Use non-OTEL format for simpler testing
        test_config = self.config.copy()
        test_config["use_otel_format"] = False
        test_config["level"] = "DEBUG"
        
        logger = Logger(
            service="test-service",
            component="test-component",
            config=test_config
        )
        
        # Add context
        context_logger = logger.with_context({"user_id": "user-123", "session": "session-456"})
        context_logger.info("Message with context")
        
        # Verify context in log
        log_files = os.listdir(os.path.join(self.temp_dir, "test-component"))
        log_file = os.path.join(self.temp_dir, "test-component", log_files[0])
        
        with open(log_file, 'r') as f:
            log_entry = json.loads(f.readline())
        
        self.assertEqual(log_entry["context"]["user_id"], "user-123")
        self.assertEqual(log_entry["context"]["session"], "session-456")
    
    def test_logger_component_switching(self):
        """Test switching between different logging components."""
        # Use non-OTEL format for simpler testing
        test_config = self.config.copy()
        test_config["use_otel_format"] = False
        test_config["level"] = "DEBUG"
        
        logger = Logger(service="test-service", config=test_config)
        
        # Log to default component
        logger.info("Default component message")
        
        # Switch to different component
        harness_logger = logger.with_component(LoggingArea.HARNESS_INFRASTRUCTURE)
        harness_logger.info("Harness infrastructure message")
        
        # Verify logs in different components
        harness_dir = os.path.join(self.temp_dir, LoggingArea.HARNESS_INFRASTRUCTURE)
        self.assertTrue(os.path.exists(harness_dir))
    
    def test_correlation_id_propagation(self):
        """Test correlation ID propagation across log entries."""
        # Use non-OTEL format for simpler testing
        test_config = self.config.copy()
        test_config["use_otel_format"] = False
        test_config["level"] = "DEBUG"
        
        logger = Logger(
            service="test-service",
            component="test-component",
            trace_id="test-trace-123",
            config=test_config
        )
        
        logger.info("First message")
        logger.info("Second message")
        
        # Verify same trace ID in both messages
        log_files = os.listdir(os.path.join(self.temp_dir, "test-component"))
        log_file = os.path.join(self.temp_dir, "test-component", log_files[0])
        
        with open(log_file, 'r') as f:
            first_entry = json.loads(f.readline())
            second_entry = json.loads(f.readline())
        
        self.assertEqual(first_entry["trace_id"], "test-trace-123")
        self.assertEqual(second_entry["trace_id"], "test-trace-123")
    
    def test_conversation_logger_integration(self):
        """Test conversation logger integration."""
        conv_logger = ConversationLogger(storage_path=self.temp_dir)
        
        # Start a session
        session = conv_logger.start_session(
            session_id="test-session-123",
            trace_id="test-trace-456",
            context={"user": "test-user"}
        )
        
        # Add messages
        conv_logger.log_user_message("Hello, can you help me?")
        conv_logger.log_assistant_message("I'd be happy to help you with your task.")
        conv_logger.log_system_message("Conversation started successfully")
        
        # End session
        conv_logger.end_session("Test conversation completed")
        
        # Verify session was saved
        session_file = os.path.join(self.temp_dir, "test-session-123.json")
        self.assertTrue(os.path.exists(session_file))
        
        # Verify session content
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        self.assertEqual(session_data["session_id"], "test-session-123")
        self.assertEqual(session_data["trace_id"], "test-trace-456")
        self.assertEqual(len(session_data["messages"]), 3)
        self.assertEqual(session_data["messages"][0]["role"], "user")
        self.assertEqual(session_data["messages"][1]["role"], "assistant")
        self.assertEqual(session_data["messages"][2]["role"], "system")
        self.assertEqual(session_data["summary"], "Test conversation completed")


class TestLoggingAreas(unittest.TestCase):
    """Test the three logging areas as specified in Phase 0."""
    
    def test_logging_areas_exist(self):
        """Test that all three logging areas are defined."""
        self.assertEqual(LoggingArea.HARNESS_INFRASTRUCTURE, "harness_infrastructure")
        self.assertEqual(LoggingArea.PHASE_0_OPERATIONS, "phase_0_operations")
        self.assertEqual(LoggingArea.CONSTITUTIONAL_AUDIT, "constitutional_audit")
    
    def test_logging_areas_unique(self):
        """Test that logging areas are unique."""
        areas = [
            LoggingArea.HARNESS_INFRASTRUCTURE,
            LoggingArea.PHASE_0_OPERATIONS,
            LoggingArea.CONSTITUTIONAL_AUDIT
        ]
        self.assertEqual(len(areas), len(set(areas)))


if __name__ == '__main__':
    unittest.main()