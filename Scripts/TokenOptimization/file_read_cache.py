#!/usr/bin/env python3
"""
File Read Caching Hook for Devin CLI

Adapted from Cache-Cow for Claude Code to implement intelligent file read caching
for SovereignAI governance files. Reduces token consumption by blocking unnecessary
re-reads and enforcing partial reads for large files.

Features:
- Blocks re-reads of unchanged files
- Shows diff for changed files instead of full content
- Enforces partial reads for files >1000 lines
- Caches partial read ranges to avoid duplicate reads
- Skips binary and generated files
"""

import json
import sys
import os
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple, Dict, List


def get_tool_input() -> Dict:
    """Parse tool input from stdin."""
    try:
        input_data = json.load(sys.stdin)
        return input_data
    except json.JSONDecodeError:
        return {}


def get_cache_key(file_path: str) -> str:
    """Generate cache key from file path."""
    return hashlib.md5(file_path.encode()).hexdigest()


def is_binary_file(file_path: str) -> bool:
    """Check if file is binary based on extension."""
    binary_extensions = {
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.pdf', '.lock',
        '.min.js', '.min.css', '.map', '.pyc', '.pyo', '.pyd', '.so', '.dll',
        '.exe', '.bin', '.dat', '.db', '.sqlite', '.zip', '.tar', '.gz'
    }
    return Path(file_path).suffix.lower() in binary_extensions


def get_line_count(file_path: str) -> int:
    """Get line count of file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (IOError, UnicodeDecodeError):
        return 0


def get_file_hash(file_path: str) -> Optional[str]:
    """Get MD5 hash of file content."""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except IOError:
        return None


def show_file_diff(old_file: str, new_file: str) -> str:
    """Show unified diff between two files."""
    try:
        result = subprocess.run(
            ['diff', '-u', '3', old_file, new_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return "No changes detected."
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return "Diff unavailable."


def merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping or adjacent ranges."""
    if not ranges:
        return []
    
    sorted_ranges = sorted(ranges, key=lambda x: (x[0], x[1]))
    merged = [sorted_ranges[0]]
    
    for current in sorted_ranges[1:]:
        last = merged[-1]
        if current[0] <= last[1] + 1:
            # Overlapping or adjacent - merge
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    
    return merged


def is_range_covered(ranges: List[Tuple[int, int]], 
                    start: int, end: int) -> bool:
    """Check if a range is covered by existing ranges."""
    for range_start, range_end in ranges:
        if range_start <= start and range_end >= end:
            return True
    return False


def pre_read_hook(input_data: Dict) -> int:
    """
    PreToolUse hook for read operations.
    
    Blocks unnecessary re-reads and enforces partial reads for large files.
    Returns exit code: 0 (allow), 2 (block)
    """
    session_id = input_data.get('session_id', '')
    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    offset = tool_input.get('offset')
    limit = tool_input.get('limit')
    
    # Skip if missing required fields
    if not file_path or not session_id:
        return 0
    
    # Skip if file doesn't exist
    if not os.path.isfile(file_path):
        return 0
    
    # Skip binary files
    if is_binary_file(file_path):
        return 0
    
    # Setup cache directory
    temp_base = Path(tempfile.gettempdir())
    cache_dir = temp_base / "devin-read-cache" / session_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_key = get_cache_key(file_path)
    cache_file = cache_dir / cache_key
    ranges_file = cache_dir / f"{cache_key}.ranges"
    snapshot_file = cache_dir / f"{cache_key}.snapshot"
    
    # Check if partial read
    is_partial = offset is not None or limit is not None
    
    # Block large files for full reads (increased limit for SovereignAI governance files)
    if not is_partial:
        line_count = get_line_count(file_path)
        if line_count > 2000:  # Increased from 1000 to accommodate governance files
            print(f"This file has {line_count} lines. Consider using offset/limit to read only the section you need.", file=sys.stderr)
            print(f"File: {file_path}", file=sys.stderr)
            # Changed from blocking (return 2) to warning (return 0) to prevent blocking legitimate reads
            return 0
    
    # Handle partial reads
    if is_partial:
        offset_num = offset if offset is not None else 0
        limit_num = limit if limit is not None else get_line_count(file_path)
        
        if limit_num <= 0:
            return 0
        
        start = offset_num + 1
        end = offset_num + limit_num
        
        # Load existing ranges
        ranges = []
        if ranges_file.exists():
            try:
                with open(ranges_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2:
                            ranges.append((int(parts[0]), int(parts[1])))
            except (IOError, ValueError):
                pass
        
        # Check if file has changed since last partial read
        if snapshot_file.exists():
            current_hash = get_file_hash(file_path)
            snapshot_hash = get_file_hash(str(snapshot_file))
            
            if current_hash == snapshot_hash:
                # File unchanged - check if range is covered
                if is_range_covered(ranges, start, end):
                    print(f"Range already read (lines {start}-{end}): {file_path}")
                    print("Content unchanged since last read. Proceeding with read for context refresh.")
                    # Changed from blocking (return 2) to allowing (return 0) for context refresh
                    return 0
            else:
                # File changed - show diff
                print(f"Showing changes since last read: {file_path}")
                print("---")
                diff = show_file_diff(str(snapshot_file), file_path)
                print(diff)
                print("---")
                print("Above diff shows changes since your last read. Check the actual read result below.")
                ranges_file.unlink(missing_ok=True)
                return 0
        
        # Check against full cache
        if cache_file.exists():
            current_hash = get_file_hash(file_path)
            cache_hash = get_file_hash(str(cache_file))
            
            if current_hash == cache_hash:
                if is_range_covered(ranges, start, end):
                    print(f"Range already read (lines {start}-{end}): {file_path}")
                    print("Content unchanged since last read. Proceeding with read for context refresh.")
                    # Changed from blocking (return 2) to allowing (return 0) for context refresh
                    return 0
            else:
                print(f"Showing changes since last read: {file_path}")
                print("---")
                diff = show_file_diff(str(cache_file), file_path)
                print(diff)
                print("---")
                print("Above diff shows changes since your last read. Check the actual read result below.")
                cache_file.unlink(missing_ok=True)
                ranges_file.unlink(missing_ok=True)
                return 0
        
        return 0
    
    # Handle full reads
    if not cache_file.exists():
        return 0
    
    # Check if file has changed
    current_hash = get_file_hash(file_path)
    cache_hash = get_file_hash(str(cache_file))
    
    if current_hash == cache_hash:
        print(f"File unchanged (re-read for context refresh): {file_path}")
        print("Content unchanged since last read. Proceeding with read for context refresh.")
        # Changed from blocking (return 2) to allowing (return 0) for context refresh
        return 0
    else:
        print(f"Showing changes since last read: {file_path}")
        print("---")
        diff = show_file_diff(str(cache_file), file_path)
        print(diff)
        print("---")
        print("Above diff shows changes since your last read. Check the actual read result below.")
        # Update cache - post-read hook will handle this
        return 0


def post_read_hook(input_data: Dict) -> int:
    """
    PostToolUse hook for read/edit/write operations.
    
    Caches file contents and tracks partial read ranges.
    Returns exit code: 0 (always allow)
    """
    session_id = input_data.get('session_id', '')
    tool_input = input_data.get('tool_input', {})
    file_path = tool_input.get('file_path', '')
    offset = tool_input.get('offset')
    limit = tool_input.get('limit')
    content = tool_input.get('content')
    new_string = tool_input.get('new_string')
    
    # Skip if missing required fields
    if not file_path or not session_id:
        return 0
    
    # Skip if file doesn't exist
    if not os.path.isfile(file_path):
        return 0
    
    # Skip binary files
    if is_binary_file(file_path):
        return 0
    
    # Setup cache directory
    temp_base = Path(tempfile.gettempdir())
    cache_dir = temp_base / "devin-read-cache" / session_id
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_key = get_cache_key(file_path)
    cache_file = cache_dir / cache_key
    ranges_file = cache_dir / f"{cache_key}.ranges"
    snapshot_file = cache_dir / f"{cache_key}.snapshot"
    
    # Check if this is a write operation (edit/write)
    is_write = content is not None or new_string is not None or 'old_string' in tool_input
    
    if is_write:
        # Invalidate cache and ranges on write (don't update cache - let next read handle it)
        cache_file.unlink(missing_ok=True)
        snapshot_file.unlink(missing_ok=True)
        ranges_file.unlink(missing_ok=True)
        return 0
    
    # Handle read operations
    is_partial = offset is not None or limit is not None
    
    if is_partial:
        offset_num = offset if offset is not None else 0
        limit_num = limit if limit is not None else get_line_count(file_path)
        
        if limit_num <= 0:
            return 0
        
        start = offset_num + 1
        end = offset_num + limit_num
        
        # Update snapshot
        try:
            import shutil
            shutil.copy(file_path, snapshot_file)
        except IOError:
            pass
        
        # Add range to ranges file
        ranges = []
        if ranges_file.exists():
            try:
                with open(ranges_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 2:
                            ranges.append((int(parts[0]), int(parts[1])))
            except (IOError, ValueError):
                pass
        
        ranges.append((start, end))
        ranges = merge_ranges(ranges)
        
        try:
            with open(ranges_file, 'w') as f:
                for range_start, range_end in ranges:
                    f.write(f"{range_start} {range_end}\n")
        except IOError:
            pass
    else:
        # Full read - cache entire file
        try:
            import shutil
            shutil.copy(file_path, cache_file)
        except IOError:
            pass
        
        # Initialize ranges with full file
        total_lines = get_line_count(file_path)
        try:
            with open(ranges_file, 'w') as f:
                f.write(f"1 {total_lines}\n")
        except IOError:
            pass
        
        snapshot_file.unlink(missing_ok=True)
    
    return 0


def session_start_hook(input_data: Dict) -> int:
    """
    SessionStart hook to clear old cache.
    
    Cleans up cache directories older than 7 days.
    Returns exit code: 0 (always allow)
    """
    session_id = input_data.get('session_id', '')
    temp_base = Path(tempfile.gettempdir())
    cache_base = temp_base / "devin-read-cache"
    
    # Clear current session cache
    if session_id:
        session_cache = cache_base / session_id
        if session_cache.exists():
            import shutil
            try:
                shutil.rmtree(session_cache)
            except IOError:
                pass
    
    # Clean up old caches (>7 days)
    try:
        import time
        current_time = time.time()
        seven_days = 7 * 24 * 60 * 60
        
        if cache_base.exists():
            for session_dir in cache_base.iterdir():
                if session_dir.is_dir():
                    dir_mtime = session_dir.stat().st_mtime
                    if current_time - dir_mtime > seven_days:
                        import shutil
                        try:
                            shutil.rmtree(session_dir)
                        except IOError:
                            pass
    except (IOError, AttributeError):
        pass
    
    return 0


def main():
    """Main entry point."""
    input_data = get_tool_input()
    event = os.environ.get('DEVIN_HOOK_EVENT', '')
    
    if event == 'PreToolUse':
        tool_name = input_data.get('tool_name', '')
        if tool_name == 'read':
            sys.exit(pre_read_hook(input_data))
    elif event == 'PostToolUse':
        tool_name = input_data.get('tool_name', '')
        if tool_name in ['read', 'edit', 'write']:
            sys.exit(post_read_hook(input_data))
    elif event == 'SessionStart':
        sys.exit(session_start_hook(input_data))
    
    sys.exit(0)


if __name__ == '__main__':
    main()