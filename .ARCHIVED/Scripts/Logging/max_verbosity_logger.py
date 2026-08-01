"""Maximum verbosity logger capturing every detail.

Captures complete system state, environment, timing, I/O, and execution details.
"""

from __future__ import annotations

import json
import os
import sys
import psutil
import platform
import subprocess
from datetime import datetime
from pathlib import Path


def get_complete_system_state() -> dict:
    """Capture complete system state."""
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "working_directory": os.getcwd(),
        "current_user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "current_pid": os.getpid(),
        "parent_pid": os.getppid(),
        "executable": sys.executable,
        "python_path": sys.path,
    }


def get_complete_environment() -> dict:
    """Capture all environment variables."""
    return dict(os.environ)


def get_process_details() -> dict:
    """Capture detailed process information."""
    try:
        process = psutil.Process(os.getpid())
        return {
            "pid": process.pid,
            "ppid": process.ppid(),
            "name": process.name(),
            "exe": process.exe(),
            "cwd": process.cwd(),
            "cmdline": process.cmdline(),
            "status": process.status(),
            "create_time": process.create_time(),
            "cpu_percent": process.cpu_percent(),
            "memory_info": dict(process.memory_info()._asdict()),
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "num_handles": process.num_handles(),
            "environ": dict(process.environ()),
        }
    except Exception as e:
        return {"error": f"Failed to get process details: {e}"}


def get_filesystem_state() -> dict:
    """Capture filesystem state."""
    try:
        disk_usage = psutil.disk_usage(os.getcwd())
        return {
            "current_directory": os.getcwd(),
            "disk_total": disk_usage.total,
            "disk_used": disk_usage.used,
            "disk_free": disk_usage.free,
            "disk_percent": disk_usage.percent,
        }
    except Exception as e:
        return {"error": f"Failed to get filesystem state: {e}"}


def get_network_state() -> dict:
    """Capture network state."""
    try:
        network_io = psutil.net_io_counters()
        return {
            "bytes_sent": network_io.bytes_sent,
            "bytes_recv": network_io.bytes_recv,
            "packets_sent": network_io.packets_sent,
            "packets_recv": network_io.packets_recv,
        }
    except Exception as e:
        return {"error": f"Failed to get network state: {e}"}


def get_complete_timing() -> dict:
    """Capture complete timing information."""
    now = datetime.now()
    return {
        "timestamp_iso": now.isoformat(),
        "timestamp_unix": now.timestamp(),
        "timestamp_utc": now.utcnow().isoformat(),
        "timezone": str(now.tzinfo),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "microsecond": now.microsecond,
    }


def get_stdin_raw() -> str:
    """Capture raw stdin."""
    try:
        return sys.stdin.read()
    except (IOError, OSError):
        return ""


def get_hook_context(data: dict) -> dict:
    """Capture complete hook context."""
    return {
        "hook_event_name": data.get("hook_event_name", "unknown"),
        "session_id": data.get("session_id", "unknown"),
        "prompt_id": data.get("prompt_id", "unknown"),
        "tool_name": data.get("tool_name", "unknown"),
        "tool_use_id": data.get("tool_use_id", "unknown"),
        "tool_input": data.get("tool_input", {}),
        "tool_response": data.get("tool_response", {}),
        "working_directory": data.get("working_directory", "unknown"),
        "project_root": data.get("project_root", "unknown"),
        "all_hook_data": data,
    }


def create_max_verbosity_entry(event_type: str, data: dict) -> dict:
    """Create a maximum verbosity log entry."""
    return {
        "event": event_type,
        "timing": get_complete_timing(),
        "system_state": get_complete_system_state(),
        "environment": get_complete_environment(),
        "process_details": get_process_details(),
        "filesystem_state": get_filesystem_state(),
        "network_state": get_network_state(),
        "hook_context": get_hook_context(data),
        "stack_trace": traceback.format_stack() if 'traceback' in globals() else [],
    }


def log_max_verbosity() -> None:
    """Log with maximum verbosity."""
    try:
        # Read stdin
        try:
            data = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            data = {}
        
        # Determine event type
        event_type = data.get("hook_event_name", "unknown")
        
        # Create maximum verbosity entry
        entry = create_max_verbosity_entry(event_type, data)
        
        # Write to log file
        log_dir = Path("Logs/Architect")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"max_verbosity_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
        
        print(f"✅ Max verbosity logged: {log_file}", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Max verbosity logger error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


if __name__ == "__main__":
    import traceback
    log_max_verbosity()