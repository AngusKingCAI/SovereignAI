"""
Cross-platform path normalization for Governor.py v1.5

This module provides path handling utilities that work correctly across
Windows, Linux, and macOS. It implements the path normalization abstraction
specified in v1.5 spec §2.5.

Key Functions:
- safe_join(): Prevents path traversal attacks
- matches_glob(): Pattern matching with case-insensitive support on Windows
- to_posix(): Converts paths to POSIX format for audit logs
- to_native(): Converts paths to native platform format

Platform-Specific Behaviors:
- Windows: Backslash handling, case-insensitive matching
- Unix/Linux/macOS: Forward slash handling, case-sensitive matching
- Cross-platform: Consistent path normalization for audit logs

Example:
    safe_join("Governor/rules", "../../../etc/passwd")  # Raises SecurityError
    matches_glob("Governor/rules/*.yaml", "Governor/rules/test.yaml")  # True
    to_posix("Governor\\rules\\test.yaml")  # "Governor/rules/test.yaml"
"""

import os
import sys
import re
from pathlib import Path
from typing import Union


class PathTraversalError(Exception):
    """Raised when a path traversal attempt is detected."""
    pass


def safe_join(base: Union[str, Path], *paths: Union[str, Path]) -> str:
    """
    Safely join paths, preventing directory traversal attacks.
    
    This function ensures that the resulting path is within the base directory,
    preventing attacks like "../../../etc/passwd".
    
    Args:
        base: Base directory path
        *paths: Path components to join
        
    Returns:
        Absolute, normalized path string
        
    Raises:
        PathTraversalError: If the resulting path escapes the base directory
        
    Example:
        >>> safe_join("Governor/rules", "test.yaml")
        'Governor/rules/test.yaml'
        >>> safe_join("Governor/rules", "../../../etc/passwd")
        PathTraversalError: Path traversal detected
    """
    base_path = Path(base).resolve()
    result_path = base_path
    
    for path in paths:
        result_path = result_path / path
    
    # Resolve to get absolute path (resolves .. and symlinks)
    result_path = result_path.resolve()
    
    # Check if the result is within the base directory
    try:
        result_path.relative_to(base_path)
    except ValueError:
        raise PathTraversalError(
            f"Path traversal detected: {result_path} is outside base directory {base_path}"
        )
    
    return str(result_path)


def matches_glob(pattern: str, path: str, case_sensitive: bool = None) -> bool:
    """
    Check if a path matches a glob pattern.
    
    Supports glob patterns like "*.yaml", "**/*.py", "test_*.py".
    On Windows, matching is case-insensitive by default unless explicitly specified.
    
    Args:
        pattern: Glob pattern to match against
        path: Path to test
        case_sensitive: Force case sensitivity (None = auto-detect by platform)
        
    Returns:
        True if path matches pattern, False otherwise
        
    Example:
        >>> matches_glob("*.yaml", "test.yaml")
        True
        >>> matches_glob("**/*.py", "Governor/engine.py")
        True
    """
    # Auto-detect case sensitivity based on platform
    if case_sensitive is None:
        case_sensitive = sys.platform != "win32"
    
    # Normalize paths for comparison
    if not case_sensitive:
        pattern = pattern.lower()
        path = path.lower()
    
    # Convert glob pattern to regex
    regex_pattern = glob_to_regex(pattern)
    
    return bool(re.match(regex_pattern, path))


def glob_to_regex(pattern: str) -> str:
    """
    Convert a glob pattern to a regex pattern.
    
    Args:
        pattern: Glob pattern
        
    Returns:
        Regex pattern string
    """
    # Escape special regex characters except glob wildcards
    special_chars = '.^$+{}[]|()'
    regex = []
    i = 0
    
    while i < len(pattern):
        char = pattern[i]
        
        if char == '*':
            if i + 1 < len(pattern) and pattern[i + 1] == '*':
                # ** matches any number of directories
                regex.append('.*')
                i += 2
            else:
                # * matches any filename or directory name
                regex.append('[^/]*')
                i += 1
        elif char == '?':
            # ? matches any single character
            regex.append('[^/]')
            i += 1
        elif char in special_chars:
            # Escape special regex characters
            regex.append(f'\\{char}')
            i += 1
        else:
            regex.append(char)
            i += 1
    
    return '^' + ''.join(regex) + '$'


def to_posix(path: Union[str, Path]) -> str:
    """
    Convert a path to POSIX format (forward slashes).
    
    This is used for audit logs to ensure consistent path representation
    across platforms.
    
    Args:
        path: Path to convert
        
    Returns:
        POSIX-formatted path string
        
    Example:
        >>> to_posix("Governor\\rules\\test.yaml")
        'Governor/rules/test.yaml'
    """
    path_str = str(path)
    return path_str.replace('\\', '/')


def to_native(path: Union[str, Path]) -> str:
    """
    Convert a path to native platform format.
    
    Args:
        path: Path to convert
        
    Returns:
        Native-formatted path string
        
    Example:
        >>> to_native("Governor/rules/test.yaml")  # On Windows
        'Governor\\rules\\test.yaml'
    """
    path_str = str(path)
    if sys.platform == "win32":
        return path_str.replace('/', '\\')
    return path_str


def normalize_path(path: Union[str, Path]) -> str:
    """
    Normalize a path for consistent comparison.
    
    This function:
    - Converts to absolute path
    - Resolves symlinks
    - Normalizes separators
    - Handles case-insensitivity on Windows
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path string
    """
    path_obj = Path(path).resolve()
    path_str = str(path_obj)
    
    # Normalize separators to forward slashes for consistency
    path_str = path_str.replace('\\', '/')
    
    # On Windows, convert to lowercase for case-insensitive comparison
    if sys.platform == "win32":
        path_str = path_str.lower()
    
    return path_str


def paths_equal(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """
    Check if two paths are equal, accounting for platform differences.
    
    This handles:
    - Different path separators (Windows vs Unix)
    - Case-insensitivity on Windows
    - Symlink resolution
    
    Args:
        path1: First path
        path2: Second path
        
    Returns:
        True if paths are equal, False otherwise
    """
    return normalize_path(path1) == normalize_path(path2)


def is_within_directory(path: Union[str, Path], directory: Union[str, Path]) -> bool:
    """
    Check if a path is within a directory.
    
    Args:
        path: Path to check
        directory: Directory to check against
        
    Returns:
        True if path is within directory, False otherwise
    """
    try:
        Path(path).resolve().relative_to(Path(directory).resolve())
        return True
    except ValueError:
        return False
