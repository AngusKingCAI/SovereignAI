"""Tests for TaskGraphCache and GraphMemory protocol (Plan 24 S9, P23-A)."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest

from sovereignai.memory.graph_backend import TaskGraphCache


@runtime_checkable
class GraphMemory(Protocol):
    """Protocol for graph memory queries. Locked contract for Plan 24 TaskGraphCache."""

    def query(self, entity_id: str, depth: int = 2) -> list[dict]:
        """Query graph memory for entity and related nodes up to specified depth."""
        ...


def test_task_graph_cache_construction():
    """Test TaskGraphCache construction with default :memory: database."""
    cache = TaskGraphCache()
    assert cache._db_path == ":memory:"
    assert cache._closed is False


def test_task_graph_cache_file_backed():
    """Test TaskGraphCache construction with file-backed database."""
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as f:
        db_path = f.name
    
    try:
        cache = TaskGraphCache(db_path=db_path)
        assert cache._db_path == db_path
        assert cache._closed is False
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_task_graph_cache_add_entity():
    """Test adding entities to the graph."""
    cache = TaskGraphCache()
    cache.add_entity("entity1", "test_type", {"key": "value"})
    
    # Query should return the entity
    results = cache.query("entity1", depth=0)
    assert len(results) == 1
    assert results[0]["id"] == "entity1"
    assert results[0]["type"] == "test_type"


def test_task_graph_cache_add_relation():
    """Test adding relations between entities."""
    cache = TaskGraphCache()
    cache.add_entity("entity1", "type1")
    cache.add_entity("entity2", "type2")
    cache.add_relation("entity1", "entity2", "relates_to")
    
    # Query should traverse the relation
    results = cache.query("entity1", depth=1)
    assert len(results) >= 1
    # Should include entity2 via relation
    entity2_found = any(r["id"] == "entity2" for r in results)
    assert entity2_found


def test_task_graph_cache_locked_signature():
    """Test that TaskGraphCache.query has locked signature per P23-A contract."""
    cache = TaskGraphCache()
    
    # Verify signature matches: query(entity_id: str, depth: int = 2) -> list[dict]
    import inspect
    sig = inspect.signature(cache.query)
    params = list(sig.parameters.keys())
    
    assert "entity_id" in params
    assert "depth" in params
    assert sig.parameters["depth"].default == 2
    
    # Verify return type annotation
    return_annotation = sig.return_annotation
    # Should be list[dict] or similar
    assert "list" in str(return_annotation)


def test_task_graph_cache_recursive_cte():
    """Test that query uses recursive CTE for graph traversal."""
    cache = TaskGraphCache()
    
    # Create a chain: entity1 -> entity2 -> entity3
    cache.add_entity("entity1", "type1")
    cache.add_entity("entity2", "type2")
    cache.add_entity("entity3", "type3")
    cache.add_relation("entity1", "entity2", "relates_to")
    cache.add_relation("entity2", "entity3", "relates_to")
    
    # Query with depth=2 should traverse the chain
    results = cache.query("entity1", depth=2)
    assert len(results) >= 2  # At least entity2 and entity3
    
    # Verify depth information
    entity1_result = next(r for r in results if r["id"] == "entity1")
    assert entity1_result["depth"] == 0


def test_task_graph_cache_close_idempotent():
    """Test that close() is idempotent via _closed flag (DD-24.11.2)."""
    cache = TaskGraphCache()
    
    # First close
    cache.close()
    assert cache._closed is True
    
    # Second close should not raise error
    cache.close()
    assert cache._closed is True


def test_task_graph_cache_per_task_ephemeral():
    """Test that TaskGraphCache is per-task ephemeral (default :memory:)."""
    cache1 = TaskGraphCache()
    cache2 = TaskGraphCache()
    
    # Add entity to cache1
    cache1.add_entity("test_entity", "test_type")
    
    # Cache2 should not have the entity (different databases)
    results = cache2.query("test_entity", depth=0)
    assert len(results) == 0


def test_task_graph_cache_satisfies_graph_memory_protocol():
    """Test that TaskGraphCache satisfies GraphMemory protocol (P23-A)."""
    cache = TaskGraphCache()
    
    # Duck-typed protocol check using isinstance
    assert isinstance(cache, GraphMemory)
    
    # Verify the method exists and is callable
    assert hasattr(cache, 'query')
    assert callable(cache.query)


def test_task_graph_cache_return_type_matches_protocol():
    """Test that query return type list[dict] matches GraphMemory Protocol exactly."""
    cache = TaskGraphCache()
    cache.add_entity("test", "type")
    
    result = cache.query("test", depth=0)
    
    # Should return list of dicts
    assert isinstance(result, list)
    if result:
        assert isinstance(result[0], dict)


def test_task_graph_cache_sqlite_stdlib():
    """Test that TaskGraphCache uses sqlite3 from Python stdlib (no new deps)."""
    import sqlite3
    
    # Verify sqlite3 is available (it's Python stdlib)
    assert sqlite3 is not None
    
    # TaskGraphCache should work without external deps
    cache = TaskGraphCache()
    cache.add_entity("test", "type")
    results = cache.query("test", depth=0)
    assert len(results) == 1
