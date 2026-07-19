"""Tests for SymbolMap latency budget (Plan 24 S9, DD-24.11.4)."""
from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock

from sovereignai.indexing.symbol_map import SymbolMap


def test_symbol_map_latency_budget() -> None:
    """Test SymbolMap indexing latency budget: warmup + 5-run median ≤2000ms (DD-24.11.4)."""
    # Performance test - always run with reduced data set for CI

    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)

    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)

        # Create a moderately-sized Python file
        test_file = project_root / "test.py"
        test_file.write_text("""
def function1():
    pass

def function2():
    pass

class Class1:
    def method1(self):
        pass

    def method2(self):
        pass

class Class2:
    def method3(self):
        pass
""")

        # Warmup run
        symbol_map.index(project_root)

        # 5 timed runs
        timings = []
        for i in range(5):
            start = time.time()
            symbol_map.index(project_root)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            timings.append(elapsed)

            # Output all timings in failure (DD-24.11.4)
            print(f"Run {i+1}: {elapsed:.2f}ms")

        # Calculate median
        median = sorted(timings)[2]
        print(f"Median: {median:.2f}ms")

        # Assert median ≤ 2000ms
        assert median <= 2000, (
            f"Median latency {median:.2f}ms exceeds 2000ms budget. Timings: {timings}"
        )


def test_symbol_map_query_latency() -> None:
    """Test SymbolMap query latency budget."""
    # Performance test - always run with reduced data set for CI

    trace = MagicMock()
    symbol_map = SymbolMap(trace=trace)

    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        project_root = Path(temp_dir)
        test_file = project_root / "test.py"
        test_file.write_text("""
def test_function():
    pass

class TestClass:
    def method(self):
        pass
""")

        symbol_map.index(project_root)

        # Query timing
        start = time.time()
        symbol_map.query("test_function", budget=1024)
        elapsed = (time.time() - start) * 1000

        print(f"Query latency: {elapsed:.2f}ms")

        # Query should be fast (< 100ms)
        assert elapsed < 100, f"Query latency {elapsed:.2f}ms exceeds 100ms threshold"
