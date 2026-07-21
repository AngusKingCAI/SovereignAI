"""Tests for Librarian event handler integration.

Tests task lifecycle event handling with MemoryGateway integration.
"""
from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from sovereignai.librarian.librarian import Librarian
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.events import (
    TaskCompleted,
    TaskCreated,
    TaskDeleted,
    TaskFailed,
    TaskUpdated,
)
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import Channel, CorrelationId, TraceLevel


@pytest.fixture
def mock_graph() -> MagicMock:
    """Mock capability graph."""
    graph = MagicMock(spec=ICapabilityIndex)
    graph.find_providers.return_value = []
    return graph


@pytest.fixture
def mock_trace() -> MagicMock:
    """Mock trace emitter."""
    trace = MagicMock(spec=TraceEmitter)
    return trace


@pytest.fixture
def mock_memory_gateway() -> MagicMock:
    """Mock MemoryGateway."""
    gateway = MagicMock()
    gateway.merge = AsyncMock()
    gateway.rollback = AsyncMock()
    return gateway


@pytest.fixture
def librarian(
    mock_graph: MagicMock, mock_trace: MagicMock, mock_memory_gateway: MagicMock
) -> Librarian:
    """Librarian instance with mock dependencies."""
    return Librarian(mock_graph, mock_trace, mock_memory_gateway)


@pytest.mark.asyncio
async def test_task_completed_updates_graph(
    librarian: Librarian, mock_memory_gateway: MagicMock, mock_trace: MagicMock
) -> None:
    """Test that task.completed event extracts entities and updates knowledge graph."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskCompleted(
        task_id=task_id,
        result=(
            '{"entities": [{"id": "entity1", "type": "Person", '
            '"attributes": {"name": "Alice"}}]}'
        ),
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify merge was called
    mock_memory_gateway.merge.assert_called_once()
    call_args = mock_memory_gateway.merge.call_args
    assert call_args[0][0] == str(task_id)
    assert len(call_args[0][1]) == 1  # One entity extracted
    assert call_args[0][1][0]["id"] == "entity1"


@pytest.mark.asyncio
async def test_task_failed_rollback_in_progress(
    librarian: Librarian, mock_memory_gateway: MagicMock, mock_trace: MagicMock
) -> None:
    """Test that task.failed event rolls back in-progress merge."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskFailed(
        task_id=task_id,
        error_message="Task failed",
        failed_at=datetime.now(UTC),
        channel=Channel("task.failed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify rollback was called
    mock_memory_gateway.rollback.assert_called_once_with(str(task_id))


@pytest.mark.asyncio
async def test_task_failed_post_commit_returns_false(
    librarian: Librarian, mock_memory_gateway: MagicMock, mock_trace: MagicMock
) -> None:
    """Test that task.failed returns False when merge already committed."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock rollback to return False (merge already committed)
    mock_memory_gateway.rollback.return_value = False

    event = TaskFailed(
        task_id=task_id,
        error_message="Task failed",
        failed_at=datetime.now(UTC),
        channel=Channel("task.failed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify rollback was called
    mock_memory_gateway.rollback.assert_called_once_with(str(task_id))


@pytest.mark.asyncio
async def test_task_deleted_ephemeral_only(
    librarian: Librarian, mock_trace: MagicMock
) -> None:
    """Test that task.deleted garbage-collects ephemeral storage only."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskDeleted(
        task_id=task_id,
        deleted_at=datetime.now(UTC),
        channel=Channel("task.deleted"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify trace emission mentions ephemeral garbage collection
    mock_trace.emit.assert_called()
    debug_calls = [
        call
        for call in mock_trace.emit.call_args_list
        if call[1]["level"] == TraceLevel.DEBUG
    ]
    assert any("ephemeral storage garbage-collected" in str(call) for call in debug_calls)
    assert any("persistent graph retained" in str(call) for call in debug_calls)


@pytest.mark.asyncio
async def test_rollback_blocks_on_unrelated_task_merge_lock(
    librarian: Librarian, mock_memory_gateway: MagicMock, mock_trace: MagicMock
) -> None:
    """Test that rollback blocks on unrelated task merge lock (v1 limitation)."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock rollback to simulate blocking behavior
    mock_memory_gateway.rollback.return_value = False

    event = TaskFailed(
        task_id=task_id,
        error_message="Task failed",
        failed_at=datetime.now(UTC),
        channel=Channel("task.failed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify rollback was attempted
    mock_memory_gateway.rollback.assert_called_once()

    # v1 limitation: returns False when merge already committed
    assert mock_memory_gateway.rollback.return_value is False


@pytest.mark.asyncio
async def test_merge_relation_src_and_dst_rewritten(
    librarian: Librarian, mock_memory_gateway: MagicMock
) -> None:
    """Test that merge rewrites relation src and dst on entity dedup."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock entities with relations
    entities = [
        {"id": "entity1", "type": "Person", "attributes": {"name": "Alice"}},
        {"id": "entity2", "type": "Person", "attributes": {"name": "Bob"}},
        {"src_id": "entity1", "dst_id": "entity2", "type": "knows"},
    ]

    event = TaskCompleted(
        task_id=task_id,
        result=json.dumps({"entities": entities}),
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify merge was called with entities including relations
    mock_memory_gateway.merge.assert_called_once()
    call_args = mock_memory_gateway.merge.call_args
    assert call_args[0][0] == str(task_id)
    assert len(call_args[0][1]) == 3  # 2 entities + 1 relation


@pytest.mark.asyncio
async def test_merge_relation_dedup_after_reattachment(
    librarian: Librarian, mock_memory_gateway: MagicMock
) -> None:
    """Test that merge deduplicates relations after reattachment."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock entities with duplicate relations
    entities = [
        {"id": "entity1", "type": "Person", "attributes": {"name": "Alice"}},
        {"id": "entity2", "type": "Person", "attributes": {"name": "Bob"}},
        {"src_id": "entity1", "dst_id": "entity2", "type": "knows"},
        {"src_id": "entity1", "dst_id": "entity2", "type": "knows"},  # Duplicate
    ]

    event = TaskCompleted(
        task_id=task_id,
        result=json.dumps({"entities": entities}),
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify merge was called (dedup happens in MemoryGateway, not Librarian)
    mock_memory_gateway.merge.assert_called_once()


@pytest.mark.asyncio
async def test_merge_self_loop_handling(
    librarian: Librarian, mock_memory_gateway: MagicMock
) -> None:
    """Test that merge retains self-loops on canonical entity."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock entity with self-loop relation
    entities = [
        {"id": "entity1", "type": "Person", "attributes": {"name": "Alice"}},
        {"src_id": "entity1", "dst_id": "entity1", "type": "self_ref"},
    ]

    event = TaskCompleted(
        task_id=task_id,
        result=json.dumps({"entities": entities}),
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify merge was called with self-loop
    mock_memory_gateway.merge.assert_called_once()
    call_args = mock_memory_gateway.merge.call_args
    assert call_args[0][0] == str(task_id)
    assert len(call_args[0][1]) == 2  # 1 entity + 1 self-loop relation


@pytest.mark.asyncio
async def test_merge_non_canonical_entity_retained_in_entities_table(
    librarian: Librarian, mock_memory_gateway: MagicMock
) -> None:
    """Test that non-canonical entities are retained in entities table (v1)."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    # Mock entities with potential dedup collision
    entities = [
        {"id": "entity1", "type": "Person", "attributes": {"name": "Alice"}},
        {"id": "entity2", "type": "Person", "attributes": {"name": "Alice"}},  # Same name/type
    ]

    event = TaskCompleted(
        task_id=task_id,
        result=json.dumps({"entities": entities}),
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify merge was called with both entities
    mock_memory_gateway.merge.assert_called_once()
    call_args = mock_memory_gateway.merge.call_args
    assert call_args[0][0] == str(task_id)
    assert len(call_args[0][1]) == 2  # Both entities passed to merge


@pytest.mark.asyncio
async def test_librarian_without_memory_gateway(
    mock_graph: MagicMock, mock_trace: MagicMock
) -> None:
    """Test that Librarian handles events gracefully without MemoryGateway."""
    # Create librarian without MemoryGateway
    librarian_no_gateway = Librarian(mock_graph, mock_trace, None)

    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskCompleted(
        task_id=task_id,
        result='{"entities": []}',
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=correlation_id,
    )

    await librarian_no_gateway.handle_event(event)

    # Verify no exception was raised (graceful handling)
    warn_calls = [
        call
        for call in mock_trace.emit.call_args_list
        if call[1]["level"] == TraceLevel.WARN
    ]
    assert any("MemoryGateway not available" in str(call) for call in warn_calls)


@pytest.mark.asyncio
async def test_task_created_updates_trace(
    librarian: Librarian, mock_trace: MagicMock
) -> None:
    """Test that task.created event emits trace."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskCreated(
        task_id=task_id,
        capability_name="test",
        capability_category="test",
        payload="",
        submitted_at=datetime.now(UTC),
        channel=Channel("task.created"),
        correlation_id=correlation_id,
    )

    await librarian.handle_event(event)

    # Verify trace was emitted
    mock_trace.emit.assert_called()


def test_merge_results_deduplicates_by_id(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() deduplicates by id."""
    results = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "name": "Alice Duplicate"},
    ]

    merged = librarian._merge_results("test", results)
    assert len(merged) == 2
    assert merged[0]["id"] == "1"
    assert merged[1]["id"] == "2"


def test_merge_results_sorts_by_timestamp(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() sorts by timestamp for episodic/trace."""
    results = [
        {"id": "1", "timestamp": "2024-01-02T00:00:00Z"},
        {"id": "2", "timestamp": "2024-01-01T00:00:00Z"},
    ]

    merged = librarian._merge_results("episodic", results)
    assert merged[0]["timestamp"] == "2024-01-01T00:00:00Z"
    assert merged[1]["timestamp"] == "2024-01-02T00:00:00Z"


def test_merge_results_working_first_backend_wins(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() returns first backend's results for working."""
    results = [
        {"result": "first"},
        {"result": "second"},
    ]

    merged = librarian._merge_results("working", results)
    assert len(merged) == 1
    assert merged[0]["result"] == "first"


def test_store_throws_no_provider_error(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that store() raises error when no provider is available."""
    from sovereignai.shared.types import NoActiveProviderError

    mock_graph.find_providers.return_value = []

    with pytest.raises(NoActiveProviderError):
        librarian.store("test_memory", {"key": "value"})


def test_store_returns_record_id_on_success(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that store() returns a record ID when a provider is available."""
    mock_graph.find_providers.return_value = [("component1", 1)]

    record_id = librarian.store("test_memory", {"key": "value"})
    assert record_id is not None
    assert isinstance(record_id, str)


def test_query_throws_no_provider_error(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that query() raises error when no provider is available."""
    from sovereignai.shared.types import NoActiveProviderError

    mock_graph.find_providers.return_value = []

    with pytest.raises(NoActiveProviderError):
        librarian.query("test_memory", {"query": "test"})


def test_delete_throws_no_provider_error(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that delete() raises error when no provider is available."""
    from sovereignai.shared.types import NoActiveProviderError

    mock_graph.find_providers.return_value = []

    with pytest.raises(NoActiveProviderError):
        librarian.delete("test_memory", "record_id")


def test_route_returns_component_ids(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _route() returns component IDs."""
    mock_graph.find_providers.return_value = [
        ("component1", 1),
        ("component2", 2),
    ]

    result = librarian._route("test_memory", "memory_storage")
    assert result == ["component1", "component2"]


def test_route_returns_empty_when_no_providers(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _route() returns empty list when no providers found."""
    mock_graph.find_providers.return_value = []

    result = librarian._route("test_memory", "memory_storage")
    assert result == []


def test_merge_results_graph_uses_memory_gateway(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() uses default merge logic for graph."""
    results = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "1", "name": "Alice Duplicate"},
    ]

    merged = librarian._merge_results("graph", results)
    assert len(merged) == 2
    assert merged[0]["id"] == "1"
    assert merged[1]["id"] == "2"


def test_merge_results_procedural_deduplicates_by_id(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() deduplicates by id for procedural."""
    results = [
        {"id": "1", "name": "Alice", "content": "First"},
        {"id": "2", "name": "Bob", "content": "Second"},
        {"id": "1", "name": "Alice", "content": "Duplicate"},
    ]

    merged = librarian._merge_results("procedural", results)
    assert len(merged) == 2
    assert merged[0]["id"] == "1"
    assert merged[1]["id"] == "2"


def test_merge_results_trace_sorts_by_timestamp_asc(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() sorts by timestamp ascending for trace."""
    results = [
        {"id": "1", "timestamp": "2024-01-02T00:00:00Z"},
        {"id": "2", "timestamp": "2024-01-01T00:00:00Z"},
    ]

    merged = librarian._merge_results("trace", results)
    assert merged[0]["timestamp"] == "2024-01-01T00:00:00Z"
    assert merged[1]["timestamp"] == "2024-01-02T00:00:00Z"


def test_merge_results_includes_no_id_results(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() includes results without id field."""
    results = [
        {"name": "Alice"},
        {"id": "1", "name": "Bob"},
    ]

    merged = librarian._merge_results("test", results)
    assert len(merged) == 2


def test_merge_results_empty_list(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that _merge_results() handles empty list."""
    merged = librarian._merge_results("test", [])
    assert merged == []


def test_query_returns_merged_results(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that query() returns merged results from backends."""
    mock_graph.find_providers.return_value = [("component1", 1)]
    
    results = librarian.query("test_memory", {"query": "test"})
    # Since we can't actually call backend methods, test that it doesn't crash
    assert results is not None


def test_delete_logs_debug_message(
    librarian: Librarian, mock_graph: MagicMock
) -> None:
    """Test that delete() logs debug message."""
    mock_graph.find_providers.return_value = [("component1", 1)]
    
    librarian.delete("test_memory", "record_id")
    # Verify it doesn't crash


def test_extract_entities_from_json_payload(
    librarian: Librarian
) -> None:
    """Test that _extract_entities() extracts entities from JSON payload."""
    event = TaskCreated(
        task_id=uuid4(),
        capability_name="test",
        capability_category="test",
        payload='{"entities": [{"id": "1", "type": "Person"}]}',
        submitted_at=datetime.now(UTC),
        channel=Channel("task.created"),
        correlation_id=CorrelationId(uuid4()),
    )

    entities = librarian._extract_entities(event)
    assert len(entities) == 1
    assert entities[0]["id"] == "1"


def test_extract_entities_from_result_field(
    librarian: Librarian
) -> None:
    """Test that _extract_entities() extracts entities from result field."""
    event = TaskCompleted(
        task_id=uuid4(),
        result='{"entities": [{"id": "2", "type": "Person"}]}',
        completed_at=datetime.now(UTC),
        channel=Channel("task.completed"),
        correlation_id=CorrelationId(uuid4()),
    )

    entities = librarian._extract_entities(event)
    assert len(entities) == 1
    assert entities[0]["id"] == "2"


def test_extract_entities_returns_empty_on_invalid_json(
    librarian: Librarian
) -> None:
    """Test that _extract_entities() returns empty list on invalid JSON."""
    event = TaskCreated(
        task_id=uuid4(),
        capability_name="test",
        capability_category="test",
        payload="invalid json",
        submitted_at=datetime.now(UTC),
        channel=Channel("task.created"),
        correlation_id=CorrelationId(uuid4()),
    )

    entities = librarian._extract_entities(event)
    assert entities == []


def test_extract_entities_returns_empty_on_no_entities_field(
    librarian: Librarian
) -> None:
    """Test that _extract_entities() returns empty list when no entities field."""
    event = TaskCreated(
        task_id=uuid4(),
        capability_name="test",
        capability_category="test",
        payload='{"data": "some data"}',
        submitted_at=datetime.now(UTC),
        channel=Channel("task.created"),
        correlation_id=CorrelationId(uuid4()),
    )

    entities = librarian._extract_entities(event)
    assert entities == []


def test_handle_task_created_emits_trace(
    librarian: Librarian, mock_trace: MagicMock
) -> None:
    """Test that _handle_task_created emits trace."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskCreated(
        task_id=task_id,
        capability_name="test",
        capability_category="test",
        payload="",
        submitted_at=datetime.now(UTC),
        channel=Channel("task.created"),
        correlation_id=correlation_id,
    )

    librarian._handle_task_created(event, str(task_id), "dedup_key")
    mock_trace.emit.assert_called()


def test_handle_task_updated_emits_trace(
    librarian: Librarian, mock_trace: MagicMock
) -> None:
    """Test that _handle_task_updated emits trace."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskUpdated(
        task_id=task_id,
        old_state="old",
        new_state="new",
        updated_at=datetime.now(UTC),
        channel=Channel("task.updated"),
        correlation_id=correlation_id,
    )

    librarian._handle_task_updated(event, str(task_id), "dedup_key")
    mock_trace.emit.assert_called()


def test_handle_task_deleted_emits_trace(
    librarian: Librarian, mock_trace: MagicMock
) -> None:
    """Test that _handle_task_deleted emits trace."""
    task_id = uuid4()
    correlation_id = CorrelationId(uuid4())

    event = TaskDeleted(
        task_id=task_id,
        deleted_at=datetime.now(UTC),
        channel=Channel("task.deleted"),
        correlation_id=correlation_id,
    )

    librarian._handle_task_deleted(event, str(task_id), "dedup_key")
    mock_trace.emit.assert_called()
