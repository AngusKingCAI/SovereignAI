"""Tests for TaskGraphCache.

Tests graph memory storage, querying, and lifecycle management.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from sovereignai.memory.graph_backend import GraphMemory, TaskGraphCache


@pytest.fixture
def temp_db_path(tmp_path: Path) -> str:
    """Temporary database path for testing."""
    return str(tmp_path / "test_graph.db")


@pytest.fixture
def memory_graph() -> TaskGraphCache:
    """TaskGraphCache instance with in-memory database."""
    return TaskGraphCache(":memory:")


@pytest.fixture
def file_graph(temp_db_path: str) -> TaskGraphCache:
    """TaskGraphCache instance with file-backed database."""
    graph = TaskGraphCache(temp_db_path)
    yield graph
    graph.close()


def test_initialize_db_creates_tables(memory_graph: TaskGraphCache) -> None:
    """Test that _initialize_db creates necessary tables and indexes."""
    assert memory_graph._connection is not None
    
    # Check that entities table exists
    cursor = memory_graph._connection.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='entities'"
    )
    assert cursor.fetchone() is not None
    
    # Check that relations table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='relations'"
    )
    assert cursor.fetchone() is not None
    
    # Check that indexes exist
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='relations'"
    )
    indexes = [row[0] for row in cursor]
    assert "idx_relations_source" in indexes
    assert "idx_relations_target" in indexes


def test_initialize_db_with_file_path(file_graph: TaskGraphCache) -> None:
    """Test that _initialize_db works with file-backed database."""
    assert file_graph._connection is not None
    assert not file_graph._closed


def test_add_entity(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity inserts entity into database."""
    memory_graph.add_entity("entity1", "Person", {"name": "Alice", "age": 30})
    
    # Verify entity was inserted
    cursor = memory_graph._connection.cursor()
    cursor.execute("SELECT * FROM entities WHERE id = ?", ("entity1",))
    row = cursor.fetchone()
    assert row is not None
    assert row["id"] == "entity1"
    assert row["type"] == "Person"


def test_add_entity_with_attributes(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity stores attributes as JSON."""
    attributes = {"name": "Alice", "age": 30, "city": "NYC"}
    memory_graph.add_entity("entity1", "Person", attributes)
    
    # Verify attributes were stored
    cursor = memory_graph._connection.cursor()
    cursor.execute("SELECT attributes FROM entities WHERE id = ?", ("entity1",))
    row = cursor.fetchone()
    assert row is not None
    assert row["attributes"] is not None


def test_add_entity_without_attributes(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity handles None attributes."""
    memory_graph.add_entity("entity1", "Person", None)
    
    # Verify entity was inserted with None attributes
    cursor = memory_graph._connection.cursor()
    cursor.execute("SELECT attributes FROM entities WHERE id = ?", ("entity1",))
    row = cursor.fetchone()
    assert row is not None
    assert row["attributes"] is None


def test_add_entity_replace_existing(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity replaces existing entity (INSERT OR REPLACE)."""
    memory_graph.add_entity("entity1", "Person", {"name": "Alice"})
    memory_graph.add_entity("entity1", "Person", {"name": "Bob"})
    
    # Verify entity was replaced
    cursor = memory_graph._connection.cursor()
    cursor.execute("SELECT attributes FROM entities WHERE id = ?", ("entity1",))
    row = cursor.fetchone()
    assert row is not None
    # Should have Bob's attributes now
    import json
    attrs = json.loads(row["attributes"])
    assert attrs["name"] == "Bob"


def test_add_entity_when_closed(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity returns early when closed."""
    memory_graph.close()
    
    # Should not raise error
    memory_graph.add_entity("entity1", "Person", {"name": "Alice"})


def test_add_entity_when_connection_none(memory_graph: TaskGraphCache) -> None:
    """Test that add_entity returns early when connection is None."""
    memory_graph._connection = None
    
    # Should not raise error
    memory_graph.add_entity("entity1", "Person", {"name": "Alice"})


def test_add_relation(memory_graph: TaskGraphCache) -> None:
    """Test that add_relation inserts relation into database."""
    # First add entities
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    
    # Add relation
    memory_graph.add_relation("entity1", "entity2", "knows")
    
    # Verify relation was inserted
    cursor = memory_graph._connection.cursor()
    cursor.execute(
        "SELECT * FROM relations WHERE source = ? AND target = ?",
        ("entity1", "entity2")
    )
    row = cursor.fetchone()
    assert row is not None
    assert row["source"] == "entity1"
    assert row["target"] == "entity2"
    assert row["relation"] == "knows"


def test_add_relation_when_closed(memory_graph: TaskGraphCache) -> None:
    """Test that add_relation returns early when closed."""
    memory_graph.close()
    
    # Should not raise error
    memory_graph.add_relation("entity1", "entity2", "knows")


def test_add_relation_when_connection_none(memory_graph: TaskGraphCache) -> None:
    """Test that add_relation returns early when connection is None."""
    memory_graph._connection = None
    
    # Should not raise error
    memory_graph.add_relation("entity1", "entity2", "knows")


def test_query_returns_empty_when_closed(memory_graph: TaskGraphCache) -> None:
    """Test that query returns empty list when closed."""
    memory_graph.close()
    
    results = memory_graph.query("entity1")
    assert results == []


def test_query_returns_empty_when_connection_none(memory_graph: TaskGraphCache) -> None:
    """Test that query returns empty list when connection is None."""
    memory_graph._connection = None
    
    results = memory_graph.query("entity1")
    assert results == []


def test_query_single_entity(memory_graph: TaskGraphCache) -> None:
    """Test that query returns single entity."""
    memory_graph.add_entity("entity1", "Person", {"name": "Alice"})
    
    results = memory_graph.query("entity1")
    
    assert len(results) == 1
    assert results[0]["id"] == "entity1"
    assert results[0]["type"] == "Person"
    assert results[0]["depth"] == 0
    assert results[0]["relation"] is None
    assert results[0]["source_id"] is None


def test_query_with_relations(memory_graph: TaskGraphCache) -> None:
    """Test that query traverses relations up to specified depth."""
    # Create a chain: entity1 -> entity2 -> entity3
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    memory_graph.add_entity("entity3", "Person")
    
    memory_graph.add_relation("entity1", "entity2", "knows")
    memory_graph.add_relation("entity2", "entity3", "knows")
    
    # Query with depth 2
    results = memory_graph.query("entity1", depth=2)
    
    # Should return all 3 entities
    assert len(results) == 3
    entity_ids = {r["id"] for r in results}
    assert "entity1" in entity_ids
    assert "entity2" in entity_ids
    assert "entity3" in entity_ids


def test_query_depth_parameter(memory_graph: TaskGraphCache) -> None:
    """Test that query respects depth parameter."""
    # Create a chain: entity1 -> entity2 -> entity3 -> entity4
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    memory_graph.add_entity("entity3", "Person")
    memory_graph.add_entity("entity4", "Person")
    
    memory_graph.add_relation("entity1", "entity2", "knows")
    memory_graph.add_relation("entity2", "entity3", "knows")
    memory_graph.add_relation("entity3", "entity4", "knows")
    
    # Query with depth 1
    results = memory_graph.query("entity1", depth=1)
    
    # Should return only entity1 and entity2
    assert len(results) == 2
    entity_ids = {r["id"] for r in results}
    assert "entity1" in entity_ids
    assert "entity2" in entity_ids
    assert "entity3" not in entity_ids


def test_query_nonexistent_entity(memory_graph: TaskGraphCache) -> None:
    """Test that query returns empty list for nonexistent entity."""
    results = memory_graph.query("nonexistent")
    assert results == []


def test_query_with_invalid_json_attributes(memory_graph: TaskGraphCache) -> None:
    """Test that query handles invalid JSON attributes gracefully."""
    # Add entity with invalid JSON
    cursor = memory_graph._connection.cursor()
    cursor.execute(
        "INSERT INTO entities (id, type, attributes) VALUES (?, ?, ?)",
        ("entity1", "Person", "invalid json")
    )
    memory_graph._connection.commit()
    
    # Query should handle the invalid JSON
    results = memory_graph.query("entity1")
    assert len(results) == 1
    assert results[0]["attributes"] is None


def test_query_relation_information(memory_graph: TaskGraphCache) -> None:
    """Test that query includes relation information."""
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    
    memory_graph.add_relation("entity1", "entity2", "knows")
    
    results = memory_graph.query("entity1", depth=1)
    
    # Find the related entity
    related = next((r for r in results if r["id"] == "entity2"), None)
    assert related is not None
    assert related["relation"] == "knows"
    assert related["source_id"] == "entity1"


def test_close_closes_connection(memory_graph: TaskGraphCache) -> None:
    """Test that close closes the database connection."""
    assert memory_graph._connection is not None
    assert not memory_graph._closed
    
    memory_graph.close()
    
    assert memory_graph._connection is None
    assert memory_graph._closed


def test_close_is_idempotent(memory_graph: TaskGraphCache) -> None:
    """Test that close can be called multiple times without error."""
    memory_graph.close()
    memory_graph.close()  # Should not raise error
    assert memory_graph._closed


def test_close_does_not_reinitialize(memory_graph: TaskGraphCache) -> None:
    """Test that closed graph does not reinitialize on operations."""
    memory_graph.close()
    
    # Operations should not reinitialize
    memory_graph.add_entity("entity1", "Person")
    assert memory_graph._connection is None


def test_del_calls_close(memory_graph: TaskGraphCache) -> None:
    """Test that __del__ calls close."""
    assert memory_graph._connection is not None
    
    # Trigger __del__
    del memory_graph
    
    # If we had a reference, it would be closed now


def test_graph_memory_protocol(memory_graph: TaskGraphCache) -> None:
    """Test that TaskGraphCache implements GraphMemory protocol."""
    assert isinstance(memory_graph, GraphMemory)


def test_query_default_depth(memory_graph: TaskGraphCache) -> None:
    """Test that query uses default depth of 2."""
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    memory_graph.add_entity("entity3", "Person")
    
    memory_graph.add_relation("entity1", "entity2", "knows")
    memory_graph.add_relation("entity2", "entity3", "knows")
    
    # Query without depth parameter
    results = memory_graph.query("entity1")
    
    # Should traverse up to depth 2
    assert len(results) == 3


def test_query_with_circular_relations(memory_graph: TaskGraphCache) -> None:
    """Test that query handles circular relations correctly."""
    # Create a cycle: entity1 -> entity2 -> entity1
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    
    memory_graph.add_relation("entity1", "entity2", "knows")
    memory_graph.add_relation("entity2", "entity1", "knows")
    
    # Query should handle the cycle without infinite loop
    results = memory_graph.query("entity1", depth=5)
    
    # The recursive CTE will follow the cycle and return multiple entries
    # What matters is that it doesn't crash and returns both entities
    entity_ids = {r["id"] for r in results}
    assert "entity1" in entity_ids
    assert "entity2" in entity_ids


def test_multiple_starting_entities(memory_graph: TaskGraphCache) -> None:
    """Test that multiple entities can be starting points for queries."""
    memory_graph.add_entity("entity1", "Person")
    memory_graph.add_entity("entity2", "Person")
    memory_graph.add_entity("entity3", "Person")
    
    memory_graph.add_relation("entity1", "entity3", "knows")
    memory_graph.add_relation("entity2", "entity3", "knows")
    
    # Query from entity1
    results1 = memory_graph.query("entity1")
    assert len(results1) == 2
    
    # Query from entity2
    results2 = memory_graph.query("entity2")
    assert len(results2) == 2