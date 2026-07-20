#!/usr/bin/env python3
"""Performance monitoring system for executor workflow steps.

Tracks execution time, resource usage, and git operation performance
to identify bottlenecks and optimization opportunities.

Usage:
    from performance_monitor import PerformanceMonitor
    
    monitor = PerformanceMonitor("plan-123")
    
    with monitor.track_step("test_execution"):
        run_tests()
    
    monitor.generate_report()
"""

import json
import time
import tracemalloc
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


class PerformanceMonitor:
    """Monitor performance of executor workflow steps."""
    
    def __init__(self, plan_id, output_dir=None):
        """Initialize performance monitor for a plan execution.
        
        Args:
            plan_id: Plan identifier (e.g., "plan-123")
            output_dir: Directory to store performance reports (default: logs/performance)
        """
        self.plan_id = plan_id
        self.output_dir = output_dir or Path("logs/performance")
        self.plan_id = plan_id
        self.output_dir = output_dir or Path("logs/performance")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = time.time()
        self.steps = {}
        self.current_step = None
        self.step_start_time = None
        
    @contextmanager
    def track_step(self, step_name):
        """Context manager to track performance of a workflow step.
        
        Args:
            step_name: Name of the step being tracked
            
        Example:
            with monitor.track_step("test_execution"):
                run_tests()
        """
        self.current_step = step_name
        self.step_start_time = time.time()
        
        # Start memory tracking
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()[0]
        
        try:
            yield
        finally:
            # Calculate metrics
            end_time = time.time()
            duration = end_time - self.step_start_time
            
            # Get memory usage
            current_memory, peak_memory = tracemalloc.get_traced_memory()
            memory_delta = current_memory - start_memory
            
            tracemalloc.stop()
            
            # Store step metrics
            self.steps[step_name] = {
                "duration_seconds": round(duration, 3),
                "start_time": datetime.fromtimestamp(self.step_start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "memory_used_mb": round(memory_delta / (1024 * 1024), 2),
                "peak_memory_mb": round(peak_memory / (1024 * 1024), 2),
                "status": "completed"
            }
            
            self.current_step = None
            self.step_start_time = None
    
    def record_git_operation(self, operation, duration):
        """Record a git operation performance metric.
        
        Args:
            operation: Git operation name (e.g., "git status", "git diff")
            duration: Operation duration in seconds
        """
        if "git_operations" not in self.steps:
            self.steps["git_operations"] = {
                "operations": [],
                "total_duration": 0.0
            }
        
        self.steps["git_operations"]["operations"].append({
            "operation": operation,
            "duration_seconds": round(duration, 3)
        })
        self.steps["git_operations"]["total_duration"] += duration
    
    def record_step_failure(self, step_name, error):
        """Record a step failure for performance analysis.
        
        Args:
            step_name: Name of the failed step
            error: Error message
        """
        if step_name in self.steps:
            self.steps[step_name]["status"] = "failed"
            self.steps[step_name]["error"] = error
        else:
            self.steps[step_name] = {
                "status": "failed",
                "error": error,
                "duration_seconds": 0.0
            }
    
    def get_total_duration(self) -> float:
        """Get total execution duration in seconds."""
        return round(time.time() - self.start_time, 3)
    
    def get_slowest_steps(self, top_n=5):
        """Get the slowest steps by duration.
        
        Args:
            top_n: Number of slowest steps to return
            
        Returns:
            List of (step_name, duration) tuples sorted by duration
        """
        completed_steps = [
            (name, data["duration_seconds"])
            for name, data in self.steps.items()
            if isinstance(data, dict) and "duration_seconds" in data
        ]
        return sorted(completed_steps, key=lambda x: x[1], reverse=True)[:top_n]
    
    def generate_report(self) -> dict:
        """Generate performance report for the execution.
        
        Returns:
            Dictionary containing performance metrics
        """
        total_duration = self.get_total_duration()
        slowest_steps = self.get_slowest_steps()
        
        # Calculate git operation overhead
        git_overhead = 0.0
        if "git_operations" in self.steps:
            git_overhead = self.steps["git_operations"]["total_duration"]
        
        report = {
            "plan_id": self.plan_id,
            "total_duration_seconds": total_duration,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "steps": self.steps,
            "slowest_steps": slowest_steps,
            "git_overhead_seconds": round(git_overhead, 3),
            "git_overhead_percentage": round((git_overhead / total_duration) * 100, 2) if total_duration > 0 else 0,
            "total_steps": len(self.steps),
            "completed_steps": sum(1 for s in self.steps.values() if isinstance(s, dict) and s.get("status") == "completed"),
            "failed_steps": sum(1 for s in self.steps.values() if isinstance(s, dict) and s.get("status") == "failed")
        }
        
        return report
    
    def save_report(self) -> Path:
        """Save performance report to disk.
        
        Returns:
            Path to the saved report file
        """
        report = self.generate_report()
        report_file = self.output_dir / f"performance-{self.plan_id}.json"
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
    def print_summary(self):
        """Print a human-readable performance summary."""
        report = self.generate_report()
        
        print(f"\n{'='*60}")
        print(f"Performance Report: {self.plan_id}")
        print(f"{'='*60}")
        print(f"Total Duration: {report['total_duration_seconds']:.2f}s")
        print(f"Git Overhead: {report['git_overhead_seconds']:.2f}s ({report['git_overhead_percentage']:.1f}%)")
        print(f"Steps Completed: {report['completed_steps']}/{report['total_steps']}")
        
        if report['failed_steps'] > 0:
            print(f"Steps Failed: {report['failed_steps']}")
        
        print(f"\nTop 5 Slowest Steps:")
        for step_name, duration in report['slowest_steps']:
            print(f"  {step_name}: {duration:.2f}s")
        
        print(f"{'='*60}\n")


def git_operation_timer(operation: str):
    """Decorator to time git operations.
    
    Args:
        operation: Name of the git operation
        
    Example:
        @git_operation_timer("git status")
        def run_git_status():
            subprocess.run(["git", "status"])
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            # Try to get monitor from kwargs
            monitor = kwargs.get('performance_monitor')
            if monitor and isinstance(monitor, PerformanceMonitor):
                monitor.record_git_operation(operation, duration)
            
            return result
        return wrapper
    return decorator