"""
File output handler for structured logging.
"""
import os
from datetime import datetime, timezone


class FileOutputHandler:
    """Output handler that writes formatted log entries to files."""
    
    def __init__(self, log_dir: str = "Logs/Architect", component: str = "harness"):
        """
        Initialize file output handler.
        
        Args:
            log_dir: Base directory for log files
            component: Component name for file naming
        """
        self.log_dir = log_dir
        self.component = component
        self._current_file = None
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Ensure the log directory exists."""
        component_dir = os.path.join(self.log_dir, self.component)
        os.makedirs(component_dir, exist_ok=True)
    
    def _get_log_filename(self) -> str:
        """Generate log filename based on current date."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return f"{self.component}-{today}.jsonl"
    
    def _get_log_filepath(self) -> str:
        """Get full path to the current log file."""
        component_dir = os.path.join(self.log_dir, self.component)
        filename = self._get_log_filename()
        return os.path.join(component_dir, filename)
    
    def write(self, formatted_entry: str) -> None:
        """
        Write a formatted log entry to the log file.
        
        Args:
            formatted_entry: JSON-formatted log entry string
        """
        filepath = self._get_log_filepath()
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(formatted_entry + '\n')
    
    def write_batch(self, formatted_entries: str) -> None:
        """
        Write multiple formatted log entries to the log file.
        
        Args:
            formatted_entries: JSON array of formatted log entries
        """
        filepath = self._get_log_filepath()
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(formatted_entries + '\n')
    
    def rotate_log(self) -> None:
        """Force log rotation (create new file)."""
        # This is a simple implementation - could be enhanced with size-based rotation
        self._current_file = None