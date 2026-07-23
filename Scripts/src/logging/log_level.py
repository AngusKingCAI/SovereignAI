"""
Log level enumeration for structured logging system.
"""
from enum import Enum
from typing import Dict


class LogLevel(Enum):
    """Standard log levels for structured logging."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

    def __str__(self) -> str:
        return self.value

    def __lt__(self, other: 'LogLevel') -> bool:
        """Enable log level comparison for filtering."""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
        return level_order[self] < level_order[other]

    def __le__(self, other: 'LogLevel') -> bool:
        """Enable log level comparison for filtering."""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
        return level_order[self] <= level_order[other]

    def __gt__(self, other: 'LogLevel') -> bool:
        """Enable log level comparison for filtering."""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
        return level_order[self] > level_order[other]

    def __ge__(self, other: 'LogLevel') -> bool:
        """Enable log level comparison for filtering."""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARN: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4
        }
        return level_order[self] >= level_order[other]

    @classmethod
    def from_string(cls, level_str: str) -> 'LogLevel':
        """Parse log level from string."""
        level_map = {
            "DEBUG": cls.DEBUG,
            "INFO": cls.INFO,
            "WARN": cls.WARN,
            "ERROR": cls.ERROR,
            "FATAL": cls.FATAL
        }
        upper_str = level_str.upper()
        if upper_str not in level_map:
            raise ValueError(f"Invalid log level: {level_str}")
        return level_map[upper_str]