"""
Stdout output handler for structured logging.
"""
import sys
from typing import Dict, Any


class StdoutOutputHandler:
    """Output handler that writes formatted log entries to stdout."""
    
    def __init__(self, flush: bool = True):
        """
        Initialize stdout output handler.
        
        Args:
            flush: Whether to flush output after each write
        """
        self.flush = flush
    
    def write(self, formatted_entry: str) -> None:
        """
        Write a formatted log entry to stdout.
        
        Args:
            formatted_entry: JSON-formatted log entry string
        """
        print(formatted_entry, file=sys.stdout)
        if self.flush:
            sys.stdout.flush()
    
    def write_batch(self, formatted_entries: str) -> None:
        """
        Write multiple formatted log entries to stdout.
        
        Args:
            formatted_entries: JSON array of formatted log entries
        """
        print(formatted_entries, file=sys.stdout)
        if self.flush:
            sys.stdout.flush()


class StderrOutputHandler:
    """Output handler that writes formatted log entries to stderr."""
    
    def __init__(self, flush: bool = True):
        """
        Initialize stderr output handler.
        
        Args:
            flush: Whether to flush output after each write
        """
        self.flush = flush
    
    def write(self, formatted_entry: str) -> None:
        """
        Write a formatted log entry to stderr.
        
        Args:
            formatted_entry: JSON-formatted log entry string
        """
        print(formatted_entry, file=sys.stderr)
        if self.flush:
            sys.stderr.flush()
    
    def write_batch(self, formatted_entries: str) -> None:
        """
        Write multiple formatted log entries to stderr.
        
        Args:
            formatted_entries: JSON array of formatted log entries
        """
        print(formatted_entries, file=sys.stderr)
        if self.flush:
            sys.stderr.flush()