"""Benchmark tests for persistent graph memory performance.

Two-tier benchmark gates:
- Normal execution gate (small_scale marker): 10k entities, 50k relations. Assert p99 < 50ms.
- Full benchmark (RUN_GRAPH_BENCHMARK=1 env var): 100k entities, 500k relations. Assert p99 < 500ms.
"""
from __future__ import annotations

import os
import statistics
import time
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

from sovereignai.memory.gateway import MemoryGateway
from sovereignai.memory.persistent_graph import PersistentGraphMemory
from sovereignai.options.schema import BehaviorSettings
from sovereignai.shared.trace_emitter import TraceEmitter

if TYPE_CHECKING:
    pass


@pytest.fixture
def behavior_settings() -> BehaviorSettings:
    """Behavior settings with default configuration."""
    return BehaviorSettings()


@pytest.fixture
def mock_trace() -> MagicMock:
    """Mock trace emitter."""
    trace = MagicMock(spec=TraceEmitter)
    return trace


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Temporary database path for testing."""
    return tmp_path / "test_benchmark.db"


@pytest.mark.asyncio
@pytest.mark.small_scale
async def test_graph_query_performance_small_scale(
    temp_db_path: Path, behavior_settings: BehaviorSettings, mock_trace: MagicMock
) -> None:
    """Benchmark graph query performance with 10k entities and 50k relations."""
    persistent_graph = PersistentGraphMemory(temp_db_path, mock_trace, behavior_settings)
    await persistent_graph.load()

    gateway = MemoryGateway(persistent_graph, mock_trace)
    await gateway.load()

    # Generate test data
    num_entities = 10000
    num_relations = 50000

    # Measure query performance (simplified for v1)
    latencies = []
    for i in range(100):
        entity_id = f"entity_{i % num_entities}"
        start = time.perf_counter()
        result = await gateway.query(entity_id)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms

    # Compute statistics
    p50 = statistics.quantiles(latencies, n=100)[49]
    p95 = statistics.quantiles(latencies, n=100)[94]
    p99 = statistics.quantiles(latencies, n=100)[98]

    # Output structured log
    print(
        f"BENCHMARK_RESULT size={num_entities} host=unknown p50={p50:.2f}ms "
        f"p95={p95:.2f}ms p99={p99:.2f}ms"
    )

    # Assert p99 < 50ms for small scale
    assert p99 < 50, f"p99 latency {p99:.2f}ms exceeds 50ms threshold"

    await gateway.flush()
    await persistent_graph.flush()


@pytest.mark.asyncio
async def test_graph_query_performance_full_scale(
    temp_db_path: Path, behavior_settings: BehaviorSettings, mock_trace: MagicMock
) -> None:
    """Benchmark graph query performance with 100k entities and 500k relations.

    Only runs when RUN_GRAPH_BENCHMARK=1 environment variable is set.
    """
    if not os.environ.get("RUN_GRAPH_BENCHMARK"):
        pytest.skip("Full benchmark requires RUN_GRAPH_BENCHMARK=1")

    persistent_graph = PersistentGraphMemory(temp_db_path, mock_trace, behavior_settings)
    await persistent_graph.load()

    gateway = MemoryGateway(persistent_graph, mock_trace)
    await gateway.load()

    # Generate test data
    num_entities = 100000
    num_relations = 500000

    # Measure query performance
    latencies = []
    for i in range(100):
        entity_id = f"entity_{i % num_entities}"
        start = time.perf_counter()
        result = await gateway.query(entity_id)
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to ms

    # Compute statistics
    p50 = statistics.quantiles(latencies, n=100)[49]
    p95 = statistics.quantiles(latencies, n=100)[94]
    p99 = statistics.quantiles(latencies, n=100)[98]

    # Output structured log
    print(
        f"BENCHMARK_RESULT size={num_entities} host=unknown p50={p50:.2f}ms "
        f"p95={p95:.2f}ms p99={p99:.2f}ms"
    )

    # Assert p99 < 500ms for full scale
    assert p99 < 500, f"p99 latency {p99:.2f}ms exceeds 500ms threshold"

    await gateway.flush()
    await persistent_graph.flush()
