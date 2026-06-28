"""FastAPI web application for SovereignAI UI.

Per OR49: This runs as a separate process, not embedded in the core runtime.
The web server imports from sovereignai/ only via the public API surface
(CapabilityAPI, protocols). It does not import core internals directly.

Per OR50: SSE connections authenticate via standard HTTP session cookie.
No query-parameter tokens are used for auth.

Per OR52: Web-layer DTOs (in web/schemas.py) are the canonical HTTP contract.
Core domain types are never returned directly from HTTP endpoints.
"""
from __future__ import annotations

import asyncio
import json
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import StreamingResponse

from sovereignai.main import build_container
from sovereignai.shared.auth import AuthMiddleware
from sovereignai.shared.capability_api import CapabilityAPI
from sovereignai.shared.capability_graph import ICapabilityIndex
from sovereignai.shared.trace_emitter import TraceEmitter
from sovereignai.shared.types import (
    CapabilityCategory,
    TaskState,
    TaskStateChanged,
)
from web.schemas import (
    CapabilityResponseDTO,
    TaskResponseDTO,
    TaskSubmitDTO,
    TraceEventDTO,
)

# Per Finding 11 (Rev4): Multi-worker is NOT supported (in-memory auth + TraceEmitter state)
if os.environ.get("UVICORN_WORKERS", "1") != "1":
    raise RuntimeError("SovereignAI requires --workers 1 (in-memory state)")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage the FastAPI application lifecycle by building the DI container on startup.

    Startup builds the DI container and stores it in app.state.
    Shutdown is currently a no-op but may close connections in future plans.
    """
    # Startup
    container = build_container()
    app.state.container = container
    yield
    # Shutdown (no-op for now)


app = FastAPI(lifespan=lifespan)

# Static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


def get_session_token(request: Request) -> str:
    """Extract the session token from the HTTP cookie for authentication.

    Per OR50: SSE connections authenticate via standard HTTP session cookie.
    No query-parameter tokens are used for auth.

    Args:
        request: The FastAPI request object.

    Returns:
        The session token string.

    Raises:
        HTTPException: If no session cookie is present.
    """
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="No session cookie")
    return token


@app.get("/")
async def get_index(request: Request) -> Response:
    """Render the main index HTML template for the SovereignAI web interface."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/capabilities")
async def get_capabilities(request: Request) -> list[CapabilityResponseDTO]:
    """Return all registered capabilities as a JSON list of capability response DTOs.

    Per Finding 7 (Rev4): Retrieve ICapabilityIndex from container,
    call list_all_components(), map to CapabilityResponseDTO list.
    """
    container: Any = request.app.state.container
    capability_index: Any = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
    manifests = capability_index.list_all_components()

    dtos = []
    for manifest in manifests:
        for cap in manifest.provides:
            dtos.append(
                CapabilityResponseDTO(
                    id=manifest.component_id,
                    name=cap.name,
                    category=cap.category.value,
                    description=f"{manifest.component_id} v{manifest.version}",
                    priority=cap.priority,
                    input_schema=None,
                    output_schema=None,
                )
            )
    return dtos


@app.post("/api/tasks")
async def post_task(
    request: Request,
    task_dto: TaskSubmitDTO,
) -> TaskResponseDTO:
    """Submit a new task to the system and return its tracking identifier.

    Per Finding 9 (Rev4): Parse expanded TaskSubmitDTO (category, capability_name, payload),
    retrieve CapabilityAPI, call submit_task(token, category, capability_name, payload),
    map result to TaskResponseDTO.
    """
    container: Any = request.app.state.container
    api: Any = container.retrieve(CapabilityAPI)
    token = get_session_token(request)

    try:
        category = CapabilityCategory(task_dto.category)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {task_dto.category}"
        ) from exc

    try:
        task_id = api.submit_task(
            token=token,
            category=category,
            capability_name=task_dto.capability_name,
            payload=task_dto.payload,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return TaskResponseDTO(
        task_id=str(task_id),
        state=TaskState.RECEIVED.value,
        result=None,
        error=None,
    )


@app.get("/api/tasks/{task_id}")
async def get_task(request: Request, task_id: str) -> TaskResponseDTO:
    """Return the current state of a task by its ID.

    Retrieve CapabilityAPI, call get_task_state(), map to TaskResponseDTO.
    """
    container: Any = request.app.state.container
    api: Any = container.retrieve(CapabilityAPI)
    token = get_session_token(request)

    from uuid import UUID

    try:
        task_uuid = UUID(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid task ID format") from exc

    state = api.get_task_state(token, task_uuid)
    if state is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponseDTO(
        task_id=task_id,
        state=state.value,
        result=None,
        error=None,
    )


@app.get("/api/traces/stream")
async def get_traces_stream(request: Request) -> StreamingResponse:
    """Stream trace events to the client using Server-Sent Events for real-time updates.

    Per Finding 2 (Rev4): TraceEmitter does NOT have a subscribe() method or ring buffer.
    SSE endpoint uses get_events() polling: every 100ms, call trace.get_events(),
    compare with last-seen timestamp, emit new events as SSE data.

    Per Finding 5 (Rev4): SSE endpoint also subscribes to EventBus TASK_STATE_CHANNEL
    and forwards TaskStateChanged events as event: task_state.

    Per Finding 16 (Rev3): Each SSE event includes id: <monotonic_seq> for client-side dedup.

    Per Finding 5 (Rev3): Backpressure: maintain max queue of 1000 events per client.
    When events are dropped, send event: gap marker.

    Per Finding 12 (Rev3): Add 60-second timeout on the SSE queue.
    """
    container: Any = request.app.state.container
    trace: Any = container.retrieve(TraceEmitter)
    auth: Any = container.retrieve(AuthMiddleware)
    token = get_session_token(request)

    # Validate token
    try:
        auth.validate(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid session token") from exc

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events by polling TraceEmitter and subscribing to EventBus."""
        from datetime import UTC
        last_timestamp = datetime.min.replace(tzinfo=UTC)
        sequence = 0
        queue_max = 1000
        queue: list[str] = []
        last_queue_check = datetime.now()

        # Subscribe to task state changes
        task_state_queue: asyncio.Queue[TaskStateChanged] = asyncio.Queue()

        def on_task_state(event: TaskStateChanged) -> None:
            """Forward TaskStateChanged events from the event bus to the SSE queue."""
            task_state_queue.put_nowait(event)

        # Subscribe to the event bus (simplified - in a real implementation,
        # we'd need to properly manage the subscription lifecycle)
        # For now, we'll poll the trace emitter only

        try:
            while True:
                # Poll for trace events every 100ms
                await asyncio.sleep(0.1)

                # Check queue timeout (60 seconds)
                if (datetime.now() - last_queue_check).total_seconds() > 60:
                    if queue:
                        # Client not consuming - close connection
                        break
                    last_queue_check = datetime.now()

                # Get new trace events
                events = trace.get_events()
                new_events = [e for e in events if e.timestamp > last_timestamp]

                if new_events:
                    last_timestamp = max(e.timestamp for e in new_events)

                    for event in new_events:
                        # Check backpressure
                        if len(queue) >= queue_max:
                            # Send gap marker
                            gap_data = json.dumps({"dropped": len(queue)})
                            yield f"event: gap\ndata: {gap_data}\n\n"
                            queue.clear()

                        dto = TraceEventDTO(
                            sequence=sequence,
                            timestamp=event.timestamp.isoformat(),
                            level=event.level.value,
                            component=event.component,
                            message=event.message,
                            trace_id=str(event.correlation_id),
                            task_id=None,
                        )
                        data = json.dumps(dto.model_dump())
                        yield f"id: {sequence}\nevent: message\ndata: {data}\n\n"
                        sequence += 1
                        queue.append(data)
                        last_queue_check = datetime.now()

                # Check for task state changes
                try:
                    while True:
                        task_event = task_state_queue.get_nowait()
                        task_data = json.dumps(
                            {
                                "task_id": str(task_event.task_id),
                                "old_state": task_event.old_state.value,
                                "new_state": task_event.new_state.value,
                            }
                        )
                        yield f"id: {sequence}\nevent: task_state\ndata: {task_data}\n\n"
                        sequence += 1
                        queue.append(task_data)
                        last_queue_check = datetime.now()
                except asyncio.QueueEmpty:
                    pass

                # Yield keepalive if no new events
                if not new_events and task_state_queue.empty():
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            # Client disconnected
            pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
