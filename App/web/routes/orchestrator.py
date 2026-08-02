"""Orchestrator API routes for Plan 31.

Provides REST and SSE endpoints for orchestrator interaction.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.web.schemas import (
    MemoryNotReadyResponse,
    MessageRequest,
    OrchestratorResponse,
    OrchestratorStatus,
    TaskEventDTO,
    TaskListResponse,
)


router = APIRouter(prefix="/api/orchestrator", tags=["orchestrator"])


# Placeholder for dependencies - will be injected via DI
orchestrator_facade = None
memory_gateway = None
idempotency_cache = None
sse_broker = None


def set_dependencies(
    orchestrator_facade_dep=None,
    memory_gateway_dep=None,
    idempotency_cache_dep=None,
    sse_broker_dep=None,
):
    """Set injected dependencies for orchestrator routes."""
    global orchestrator_facade, memory_gateway, idempotency_cache, sse_broker
    orchestrator_facade = orchestrator_facade_dep
    memory_gateway = memory_gateway_dep
    idempotency_cache = idempotency_cache_dep
    sse_broker = sse_broker_dep


@router.post("/message", response_model=OrchestratorResponse)
async def post_message(request: Request, message: MessageRequest) -> OrchestratorResponse:
    """Submit a message to the orchestrator.

    Supports idempotency via Idempotency-Key header.
    """
    # Check memory gateway readiness
    if memory_gateway is None or not memory_gateway.is_ready():
        error_response = MemoryNotReadyResponse()
        raise HTTPException(
            status_code=503,
            headers={"Retry-After": "5"},
            detail=error_response.model_dump(),
        )

    # Extract idempotency key
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        # Validate idempotency key format (should be UUID4)
        try:
            # Simple validation - check if it looks like a UUID
            import uuid
            uuid.UUID(idempotency_key)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Idempotency-Key format")

        # Get session from cookie
        session_id = request.cookies.get("session_id")
        if not session_id:
            raise HTTPException(status_code=401, detail="Session required")

        # Check cache for existing response
        payload_hash = hashlib.sha256(
            json.dumps(message.model_dump(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        cached = await idempotency_cache.get(
            session_id=session_id,
            idempotency_key=idempotency_key,
            endpoint_path="/api/orchestrator/message",
        )
        if cached:
            if cached["payload_hash"] == payload_hash:
                # Return cached response
                return OrchestratorResponse(**cached["response_body"])
            else:
                # Payload mismatch - conflict
                raise HTTPException(status_code=409, detail="Idempotency key conflict")

    # Call orchestrator facade
    try:
        response = await orchestrator_facade.process_message(
            content=message.content,
            session_id=message.session_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Cache response if idempotency key provided
    if idempotency_key and idempotency_cache:
        await idempotency_cache.set(
            session_id=session_id,
            idempotency_key=idempotency_key,
            endpoint_path="/api/orchestrator/message",
            payload_hash=payload_hash,
            status_code=200,
            response_body=response.model_dump(),
            content_type="application/json",
        )

    return response


@router.get("/status", response_model=OrchestratorStatus)
async def get_status() -> OrchestratorStatus:
    """Get orchestrator status."""
    if orchestrator_facade is None:
        raise HTTPException(status_code=503, detail="Orchestrator not available")

    status = await orchestrator_facade.get_status()
    return OrchestratorStatus(
        state=status["state"],
        uptime_seconds=status["uptime_seconds"],
        tasks_completed=status["tasks_completed"],
        tasks_failed=status["tasks_failed"],
    )


@router.get("/stream")
async def orchestrator_stream(request: Request):
    """SSE stream for orchestrator events.

    Emits orchestrator.response.ready and orchestrator.clarification_needed events.
    """
    if sse_broker is None:
        raise HTTPException(status_code=503, detail="SSE broker not available")

    # Auth validation (placeholder)
    async def auth_validator(req):
        # Placeholder for actual auth validation
        return True, "testuser", "session-123"

    # Create SSE connection
    connection, conn_id = await sse_broker.create_connection(
        request,
        "orchestrator_stream",
        auth_validator,
    )

    # Return SSE stream
    return StreamingResponse(
        sse_broker.event_generator(conn_id, request),
        media_type="text/event-stream",
    )


@router.get("/events/tasks")
async def get_task_events(
    request: Request,
    event_type: str | None = None,
    task_id: str | None = None,
    since_event_id: int | None = None,
    page_size: int = 50,
):
    """Get task events.

    Supports both SSE (via Accept: text/event-stream) and REST.
    """
    # Check for SSE request
    accept_header = request.headers.get("Accept", "")
    if "text/event-stream" in accept_header:
        if sse_broker is None:
            raise HTTPException(status_code=503, detail="SSE broker not available")

        # Auth validation (placeholder)
        async def auth_validator(req):
            return True, "testuser", "session-123"

        # Create SSE connection
        connection, conn_id = await sse_broker.create_connection(
            request,
            "tasks_events",
            auth_validator,
        )

        # Return SSE stream
        return StreamingResponse(
            sse_broker.event_generator(conn_id, request),
            media_type="text/event-stream",
        )

    # REST fallback - return paginated events
    if orchestrator_facade is None:
        raise HTTPException(status_code=503, detail="Orchestrator not available")

    # Validate page_size
    page_size = max(1, min(page_size, 500))

    # Get events from orchestrator
    events = await orchestrator_facade.get_task_events(
        event_type=event_type,
        task_id=task_id,
        since_event_id=since_event_id,
        limit=page_size,
    )

    # Convert to DTOs
    task_events = [
        TaskEventDTO(
            event_id=event["event_id"],
            task_id=event["task_id"],
            event_type=event["event_type"],
            timestamp=event["timestamp"],
            details=event.get("details"),
        )
        for event in events["events"]
    ]

    return TaskListResponse(
        events=task_events,
        total_count=events["total_count"],
        next_event_id=events.get("next_event_id"),
        page_size=page_size,
    )


@router.get("/memory/{path:path}")
async def memory_endpoint(path: str, request: Request):
    """Memory endpoints - delegate to orchestrator facade.

    Returns 503 if MemoryGateway not ready.
    """
    if memory_gateway is None or not memory_gateway.is_ready():
        error_response = MemoryNotReadyResponse()
        raise HTTPException(
            status_code=503,
            headers={"Retry-After": "5"},
            detail=error_response.model_dump(),
        )

    if orchestrator_facade is None:
        raise HTTPException(status_code=503, detail="Orchestrator not available")

    # Delegate to orchestrator facade
    try:
        response = await orchestrator_facade.handle_memory_request(
            path=path,
            method=request.method,
            params=dict(request.query_params),
            body=await request.body(),
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
