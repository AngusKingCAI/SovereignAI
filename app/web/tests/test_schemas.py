"""Tests for app/web/schemas.py DTOs."""

import pytest
from pydantic import ValidationError

from app.web.schemas import (
    AuditPage,
    CircuitState,
    CircuitStateList,
    CrossDepartmentMessage,
    EpisodicEventDTO,
    EpisodicQueryRequest,
    EpisodicQueryResponse,
    GraphEdgeDTO,
    GraphNodeDTO,
    GraphQueryRequest,
    GraphQueryResponse,
    HealthSnapshot,
    LifecycleEventDTO,
    LifecycleReadyResponse,
    LoginRequest,
    LoginResponse,
    MemoryNotReadyResponse,
    MergeConflictDTO,
    MergeConflictPage,
    MessageRequest,
    MessagingAuditEntryDTO,
    ModelListResponse,
    ModelQuery,
    ModelSummary,
    OrchestratorResponse,
    OrchestratorStatus,
    OptionsUpdate,
    SubsystemHealth,
    SyncTrigger,
    TaskEventDTO,
    TaskListResponse,
    TraceEvent,
    TraceLogRequest,
    TraceLogResponse,
)


def test_dto_inventory_complete():
    """Verify all required DTOs from plan S1.2 are defined."""
    required_dtos = [
        "OrchestratorResponse",
        "MessageRequest",
        "OrchestratorStatus",
        "CrossDepartmentMessage",
        "AuditPage",
        "AuditEntry",
        "CircuitStateList",
        "HealthSnapshot",
        "LoginRequest",
        "LoginResponse",
        "OptionsUpdate",
        "ModelQuery",
        "SyncTrigger",
        "TraceEvent",
        "GraphNodeDTO",
        "GraphEdgeDTO",
        "GraphQueryRequest",
        "GraphQueryResponse",
        "EpisodicQueryRequest",
        "EpisodicQueryResponse",
        "EpisodicEventDTO",
        "TaskEventDTO",
        "TaskListResponse",
        "LifecycleEventDTO",
        "TraceLogRequest",
        "TraceLogResponse",
        "LifecycleReadyResponse",
        "MemoryNotReadyResponse",
        "MergeConflictDTO",
        "MergeConflictPage",
        "ModelSummary",
        "ModelListResponse",
        "MessagingAuditEntryDTO",
    ]
    
    import app.web.schemas as schemas_module
    
    for dto_name in required_dtos:
        assert hasattr(schemas_module, dto_name), f"Missing DTO: {dto_name}"


def test_no_core_types_in_schemas():
    """Verify no core types are imported in schemas.py."""
    import app.web.schemas as schemas_module
    import inspect
    
    source = inspect.getsource(schemas_module)
    
    # Check for forbidden imports from core
    forbidden_imports = [
        "from app.sovereignai",
        "from app.core",
        "from app.models",
    ]
    
    for forbidden in forbidden_imports:
        assert forbidden not in source, f"Found forbidden import: {forbidden}"


def test_merge_conflict_dto_fields_valid():
    """Verify MergeConflictDTO has correct fields and validation."""
    dto = MergeConflictDTO(
        conflict_id="test-conflict-1",
        entity_name="test-entity",
        entity_type="person",
        canonical_uuid="uuid-1",
        candidate_uuids=["uuid-2", "uuid-3"],
        first_observed_at="2026-07-21T00:00:00Z",
        resolution_status="unresolved",
    )
    
    assert dto.conflict_id == "test-conflict-1"
    assert dto.resolution_status == "unresolved"
    
    # Test valid resolution_status values
    for status in ["unresolved", "suppressed_by_dedup"]:
        MergeConflictDTO(
            conflict_id="test",
            entity_name="test",
            entity_type="test",
            canonical_uuid="test",
            candidate_uuids=["test"],
            first_observed_at="2026-07-21T00:00:00Z",
            resolution_status=status,
        )
    
    # Test invalid resolution_status
    with pytest.raises(ValidationError):
        MergeConflictDTO(
            conflict_id="test",
            entity_name="test",
            entity_type="test",
            canonical_uuid="test",
            candidate_uuids=["test"],
            first_observed_at="2026-07-21T00:00:00Z",
            resolution_status="invalid",
        )


def test_memory_not_ready_response_fields_valid():
    """Verify MemoryNotReadyResponse has correct fields."""
    response = MemoryNotReadyResponse()
    
    assert response.error_code == "memory_not_ready"
    assert response.message == "Memory subsystem still loading"
    assert response.retry_after_seconds == 5
    
    # Test with custom values
    custom = MemoryNotReadyResponse(retry_after_seconds=10)
    assert custom.retry_after_seconds == 10
    
    # Test invalid error_code
    with pytest.raises(ValidationError):
        MemoryNotReadyResponse(error_code="invalid_error")


def test_task_list_response_fields_valid():
    """Verify TaskListResponse has correct fields."""
    response = TaskListResponse(
        events=[
            TaskEventDTO(
                event_id=1,
                task_id="task-1",
                event_type="created",
                timestamp="2026-07-21T00:00:00Z",
            )
        ],
        total_count=1,
        page_size=500,
    )
    
    assert response.total_count == 1
    assert response.page_size == 500
    assert response.next_event_id is None
    
    # Test with next_event_id
    response_with_next = TaskListResponse(
        events=[],
        total_count=100,
        page_size=50,
        next_event_id=51,
    )
    assert response_with_next.next_event_id == 51


def test_dto_round_trip_all_schemas():
    """Verify all DTOs can serialize and deserialize correctly."""
    dtos_to_test = [
        (
            OrchestratorResponse,
            {
                "task_id": "task-1",
                "status": "completed",
                "response_text": "Done",
                "error": None,
                "created_at": "2026-07-21T00:00:00Z",
            },
        ),
        (
            MessageRequest,
            {"content": "Test message", "session_id": None},
        ),
        (
            LoginRequest,
            {"username": "testuser", "password": "password123", "setup_token": None},
        ),
        (
            HealthSnapshot,
            {
                "status": "READY",
                "subsystems": [
                    {
                        "name": "worker-1",
                        "kind": "worker",
                        "status": "HEALTHY",
                        "details": None,
                    }
                ],
                "cache_age_ms": 1000,
            },
        ),
        (
            LoginResponse,
            {"expires_at": "2026-07-22T00:00:00Z", "username": "testuser"},
        ),
        (
            OptionsUpdate,
            {"key": "test_option", "value": "test_value"},
        ),
        (
            ModelQuery,
            {"model_id": "model-1", "provider": "openai"},
        ),
        (
            SyncTrigger,
            {"model_id": "model-1"},
        ),
        (
            TraceEvent,
            {
                "timestamp": "2026-07-21T00:00:00Z",
                "level": "INFO",
                "source": "test",
                "message": "Test message",
                "event_type": "test_event",
            },
        ),
        (
            GraphNodeDTO,
            {
                "uuid": "uuid-1",
                "name": "node-1",
                "type": "person",
                "attributes": {"key": "value"},
            },
        ),
        (
            GraphEdgeDTO,
            {
                "src_id": "uuid-1",
                "dst_id": "uuid-2",
                "type": "knows",
                "attributes": {"weight": 1.0},
            },
        ),
        (
            GraphQueryRequest,
            {
                "query_type": "entity_search",
                "entity_name": "John",
                "entity_type": "person",
                "relation_type": None,
                "max_depth": 1,
            },
        ),
        (
            GraphQueryResponse,
            {
                "nodes": [
                    {
                        "uuid": "uuid-1",
                        "name": "node-1",
                        "type": "person",
                        "attributes": {},
                    }
                ],
                "edges": [],
            },
        ),
        (
            EpisodicEventDTO,
            {
                "id": 1,
                "event_type": "memory_created",
                "timestamp": "2026-07-21T00:00:00Z",
                "correlation_id": "corr-1",
                "summary": "Test summary",
            },
        ),
        (
            EpisodicQueryRequest,
            {
                "event_type": "memory_created",
                "since": "2026-07-20T00:00:00Z",
                "until": "2026-07-21T00:00:00Z",
                "offset": 0,
                "limit": 100,
            },
        ),
        (
            EpisodicQueryResponse,
            {
                "events": [],
                "total_count": 0,
                "offset": 0,
                "limit": 100,
            },
        ),
        (
            TaskEventDTO,
            {
                "event_id": 1,
                "task_id": "task-1",
                "event_type": "created",
                "timestamp": "2026-07-21T00:00:00Z",
                "details": {"key": "value"},
            },
        ),
        (
            TaskListResponse,
            {
                "events": [],
                "total_count": 0,
                "page_size": 500,
                "next_event_id": None,
            },
        ),
        (
            LifecycleEventDTO,
            {
                "event_type": "ready",
                "timestamp": "2026-07-21T00:00:00Z",
                "server_pid": 12345,
                "instance_uuid": "uuid-1",
                "drain_timeout_seconds": 60,
            },
        ),
        (
            TraceLogRequest,
            {
                "event_type": "INFO",
                "since": "2026-07-20T00:00:00Z",
                "until": "2026-07-21T00:00:00Z",
                "offset": 0,
                "limit": 500,
            },
        ),
        (
            TraceLogResponse,
            {
                "events": [],
                "total_count": 0,
                "offset": 0,
                "limit": 500,
            },
        ),
        (
            LifecycleReadyResponse,
            {
                "ready": True,
                "server_pid": 12345,
                "instance_uuid": "uuid-1",
            },
        ),
        (
            MemoryNotReadyResponse,
            {
                "error_code": "memory_not_ready",
                "message": "Memory subsystem still loading",
                "retry_after_seconds": 5,
            },
        ),
        (
            MergeConflictDTO,
            {
                "conflict_id": "conflict-1",
                "entity_name": "entity-1",
                "entity_type": "person",
                "canonical_uuid": "uuid-1",
                "candidate_uuids": ["uuid-2"],
                "first_observed_at": "2026-07-21T00:00:00Z",
                "resolution_status": "unresolved",
            },
        ),
        (
            MergeConflictPage,
            {
                "items": [],
                "total_count": 0,
                "offset": 0,
                "limit": 100,
            },
        ),
        (
            ModelSummary,
            {
                "model_id": "model-1",
                "provider": "openai",
                "sync_status": "synced",
            },
        ),
        (
            ModelListResponse,
            {
                "models": [],
                "total_count": 0,
            },
        ),
        (
            MessagingAuditEntryDTO,
            {
                "id": "entry-1",
                "source_department": "dept-1",
                "target_department": "dept-2",
                "content_preview": "Test content",
                "timestamp": "2026-07-21T00:00:00Z",
            },
        ),
        (
            OrchestratorStatus,
            {
                "state": "running",
                "uptime_seconds": 3600.0,
                "tasks_completed": 10,
                "tasks_failed": 1,
            },
        ),
        (
            CrossDepartmentMessage,
            {
                "source_department": "dept-1",
                "target_department": "dept-2",
                "content": "Test message",
                "correlation_id": "corr-1",
            },
        ),
    ]
    
    for dto_class, test_data in dtos_to_test:
        # Test deserialization
        dto = dto_class(**test_data)
        
        # Test serialization
        serialized = dto.model_dump()
        
        # Test round-trip
        dto2 = dto_class(**serialized)
        assert dto == dto2


def test_subsystem_health_kind_discriminator_valid():
    """Verify SubsystemHealth kind discriminator accepts valid values."""
    valid_kinds = ["worker", "adapter", "hardware", "core"]
    
    for kind in valid_kinds:
        health = SubsystemHealth(
            name="test-component",
            kind=kind,
            status="HEALTHY",
            details=None,
        )
        assert health.kind == kind
    
    # Test invalid kind
    with pytest.raises(ValidationError):
        SubsystemHealth(
            name="test-component",
            kind="invalid_kind",
            status="HEALTHY",
            details=None,
        )


def test_subsystem_health_kind_required():
    """Verify SubsystemHealth kind field is required."""
    with pytest.raises(ValidationError):
        SubsystemHealth(
            name="test-component",
            kind=None,  # type: ignore
            status="HEALTHY",
            details=None,
        )


def test_login_response_body_does_not_contain_session_id():
    """Verify LoginResponse does not contain session_id field (session via cookie only)."""
    response = LoginResponse(
        expires_at="2026-07-22T00:00:00Z",
        username="testuser",
    )
    
    # Verify no session_id field exists
    assert not hasattr(response, "session_id") or "session_id" not in response.model_fields
    
    # Verify only expected fields exist
    expected_fields = {"expires_at", "username"}
    actual_fields = set(response.model_fields.keys())
    assert actual_fields == expected_fields
