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

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse

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


@app.middleware("http")
async def first_run_redirect(request: Request, call_next: Any) -> Response:
    """Redirect to registration page on first run when no users exist.

    API paths return 401 instead of redirect to avoid JSON parsing errors.
    Static files, auth endpoints, and login/register pages are always allowed.
    """
    path = request.url.path
    if (
        path.startswith("/static/")
        or path in ("/login", "/register")
        or path.startswith("/api/auth/")
    ):
        return await call_next(request)  # type: ignore[no-any-return]

    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) == 0:
        if path.startswith("/api/"):
            # Return JSONResponse directly — raising HTTPException inside BaseHTTPMiddleware
            # gets swallowed by Starlette and turned into a 500. The frontend's auth check
            # (app.js) expects a clean 401 JSON response.
            return JSONResponse(
                status_code=401,
                content={"detail": "No user registered — complete first-run setup"},
            )
        return RedirectResponse(url="/register")  # type: ignore[no-any-return]

    return await call_next(request)  # type: ignore[no-any-return]


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
    token = request.cookies.get("session_id")
    if not token:
        raise HTTPException(status_code=401, detail="No session cookie")
    return token


async def get_current_user(request: Request) -> Any:
    """Validate the session cookie and return the authenticated user.

    Args:
        request: The FastAPI request object.

    Returns:
        The authenticated user object.

    Raises:
        HTTPException: If session is invalid or expired.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        user = auth.validate(session_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired session") from exc
    return user


@app.get("/")
async def get_index(request: Request) -> Response:
    """Render the main index HTML template for the SovereignAI web interface."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/auth/login")
async def login(request: Request, response: Response) -> dict:
    """Validate credentials and set session cookie."""
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        session = auth.login(data["username"], data["password"])
        response.set_cookie(
            key="session_id",
            value=session.token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=86400,
        )
        return {"status": "authenticated"}
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid credentials") from exc


@app.post("/api/auth/logout")
async def logout(response: Response) -> dict:
    """Clear session cookie."""
    response.delete_cookie(key="session_id")
    return {"status": "logged_out"}


@app.post("/api/auth/register")
async def register(request: Request) -> dict:
    """First-run registration. Only allowed when no users exist."""
    data = await request.json()
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        raise HTTPException(status_code=403, detail="Registration closed — user already exists")
    try:
        auth.register_user(data["username"], data["password"])
    except ValueError as exc:
        raise HTTPException(
            status_code=403, detail="Registration closed — user already exists"
        ) from exc
    return {"status": "created"}


@app.get("/login")
async def login_page(request: Request) -> Response:
    """Render the login page."""
    return templates.TemplateResponse(request, "login.html")


@app.get("/register")
async def register_page(request: Request) -> Response:
    """Render the registration page. Only accessible when no users exist."""
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    if len(auth._password_hashes) > 0:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "register.html")


@app.get("/api/auth/status")
async def auth_status(request: Request) -> dict:
    """Check if session is valid. Used by SSE 401 handler in app.js."""
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    container: Any = request.app.state.container
    auth: Any = container.retrieve(AuthMiddleware)
    try:
        user = auth.validate(session_id)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired session") from exc
    return {"username": user.username}


@app.get("/api/capabilities", dependencies=[Depends(get_current_user)])
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


@app.get("/api/workers", dependencies=[Depends(get_current_user)])
async def get_workers(request: Request) -> list[dict]:
    """Return all registered components from the capability graph.

    Per Finding 8 (Rev4): CapabilityCategory.WORKER does not exist.
    Use list_all_components() and return all — UI filters client-side.
    """
    container: Any = request.app.state.container
    capability_index: Any = container.retrieve(ICapabilityIndex)  # type: ignore[type-abstract]
    components = capability_index.list_all_components()

    return [
        {
            "id": str(c.component_id),
            "name": c.version,
            "category": c.provides[0].category.value if c.provides else "unknown",
        }
        for c in components
    ]


@app.get("/api/tasks", dependencies=[Depends(get_current_user)])
async def get_tasks(request: Request) -> list[TaskResponseDTO]:
    """Return all tasks from the task state machine.

    The Task dataclass holds task_id, capability, payload, submitted_at —
    NOT state/result/error. State is tracked separately by the state machine
    (get_state). result/error are not stored in v1 (no result-storage layer);
    return null until a future plan adds task result persistence.
    """
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    tasks = task_state_query.list_tasks()

    dtos: list[TaskResponseDTO] = []
    for t in tasks:
        state = task_state_query.get_state(t.task_id)
        state_str = state.value if state is not None else "unknown"
        dtos.append(
            TaskResponseDTO(
                task_id=str(t.task_id),
                state=state_str,
                result=None,   # v1: no result storage yet
                error=None,    # v1: no error storage yet
            )
        )
    return dtos


@app.post("/api/tasks", dependencies=[Depends(get_current_user)])
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


@app.get("/api/tasks/{task_id}", dependencies=[Depends(get_current_user)])
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


@app.post("/api/dispatch", dependencies=[Depends(get_current_user)])
async def dispatch(request: Request) -> TaskResponseDTO:
    """Submit a natural language message to the Capability API.

    Per Finding 2 (Rev5): Extract session cookie as token for CapabilityAPI.submit_task().
    Retrieve CapabilityAPI from container, call submit_task() with the message,
    return TaskResponseDTO with the submitted task.
    """
    from sovereignai.shared.capability_api import CapabilityAPI
    from sovereignai.shared.task_state_machine import ITaskStateQuery

    container: Any = request.app.state.container
    capability_api: Any = container.retrieve(CapabilityAPI)
    task_state_query: Any = container.retrieve(ITaskStateQuery)  # type: ignore[type-abstract]
    token = get_session_token(request)

    data = await request.json()
    message = data.get("message", "")

    try:
        task_id = capability_api.submit_task(
            token=token,
            category=CapabilityCategory.TOOL,
            capability_name="web_search",
            payload=message,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Retrieve the task state from the state machine
    state = task_state_query.get_state(task_id)
    if state is None:
        state = TaskState.RECEIVED

    return TaskResponseDTO(
        task_id=str(task_id),
        state=state.value,
        result=None,
        error=None,
    )


@app.get("/api/hardware", dependencies=[Depends(get_current_user)])
async def get_hardware(request: Request) -> dict:
    """Return current hardware probe results.

    Retrieve HardwareProbe, call probe_async(), return hardware info dict.
    """
    from web.hardware_probe import HardwareProbe

    probe = HardwareProbe()
    info = await probe.probe_async()

    return {
        "cpu_count": info.cpu_count,
        "cpu_freq_mhz": info.cpu_freq_mhz,
        "ram_total_mb": info.ram_total_mb,
        "ram_available_mb": info.ram_available_mb,
        "gpu_name": info.gpu_name,
        "gpu_vram_mb": info.gpu_vram_mb,
    }


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
